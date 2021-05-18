"""
Sensor for Sleep as android states
"""

import logging
import json

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.mqtt import subscription
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .device_trigger import TRIGGERS

from .const import DOMAIN
from . import SleepAsAndroidInstance

_LOGGER = logging.getLogger(__name__)


def get_name_from_topic(topic: str) -> str:
    return topic.split('/')[-1]


def generate_id(instance: SleepAsAndroidInstance, name: str) -> str:
    return instance.name + '_' + name


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the sensor entry"""
    instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]

    async def add_configured_entities():
        entity_registry = await er.async_get_registry(hass)

        # todo
        # instance.senor should be a dict. Keys -- topics.
        # if topic not match template -- new key
        # if match just add to list
        for entity in er.async_entries_for_config_entry(entity_registry, config_entry.entry_id):
            instance.sensors.append(SleepAsAndroidSensor(hass, config_entry, "/".join(entity.unique_id.split('_')[1:])))

        async_add_entities(instance.sensors.append)

    async def subscribe_root_topic(root_instance: SleepAsAndroidInstance):
        """(Re)Subscribe to topics."""
        _LOGGER.debug("Subscribing to root topic '%s'", root_instance.mqtt_topic)
        sub_state = None

        @callback
        # @log_messages(self.hass, self.entry_id)
        def message_received(msg):
            """Handle new MQTT messages."""

            # todo
            # create entity if needed
            # call message_received of entity

            entity_registry = await er.async_get_registry(hass)
            _LOGGER.debug("Got message %s", msg)
            entity_id = root_instance.name + '_' + msg.topic.replace('/', '_')
            candidate_entity = entity_registry.async_get_entity_id('sensor', DOMAIN, entity_id)

            if candidate_entity is None:
                _LOGGER.info("New device! Let's create sensor for %s", msg.topic)
                new_entity = SleepAsAndroidSensor(hass, config_entry, msg.topic)
                new_entity.message_received(msg, True)
                async_add_entities([new_entity])

        sub_state = await subscription.async_subscribe_topics(
            hass,
            sub_state,
            {
                "state_topic": {
                    "topic": root_instance.mqtt_topic,
                    "msg_callback": message_received,
                    "qos": config_entry.data['qos']
                }
            }
        )
        if sub_state is not None:
            _LOGGER.debug("Subscribing to root topic is done!")
    # todo
    # instance should subscribe to topics and call message_received of sensor
    await add_configured_entities()
    await subscribe_root_topic(instance)
    return True


class SleepAsAndroidSensor(Entity):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, topic: str):
        self._instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]

        self.hass: HomeAssistant = hass

        self._topic: str = topic
        self._qos = config_entry.data['qos']

        name = get_name_from_topic(topic)
        self._name: str = self._instance.name + '_' + name
        self._state: str = STATE_UNKNOWN
        self._device_id: str = "unknown"
        self._sub_state = None  # subscription state

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        device_registry = await dr.async_get_registry(self.hass)
        device = device_registry.async_get_device(identifiers=self.device_info['identifiers'], connections=set())
        _LOGGER.debug("My device id is %s", device.id)
        self._device_id = device.id
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        self._sub_state = await subscription.async_unsubscribe_topics(self.hass, self._sub_state)

    def message_received(self, msg, first: bool = False):
        """Handle new MQTT messages."""
        new_state = STATE_UNKNOWN

        try:
            new_state = json.loads(msg.payload)['event']
            if self.state != new_state:
                payload = {"event": new_state}
                _LOGGER.debug("Firing '%s' with payload: '%s'", self.name, payload)
                self.hass.bus.fire(self.name, payload)
                if new_state in TRIGGERS:
                    self.hass.bus.async_fire(DOMAIN + "_event", {"device_id": self.device_id, "type": new_state})
                else:
                    _LOGGER.warning("Got %s event, but it is not in TRIGGERS list: will not fire this event for "
                                    "trigger!", new_state)
        except KeyError:
            _LOGGER.warning("Got unexpected payload: '%s'", msg.payload)
        except json.decoder.JSONDecodeError:
            _LOGGER.warning("expected JSON payload. got '%s' instead", msg.payload)
            new_state = msg.payload

        self._state = new_state
        if not first:
            self.async_write_ha_state()

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._instance.name + '_' + self._topic.replace('/', '_')

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:sleep"

    @property
    def available(self) -> bool:
        return self.state != STATE_UNKNOWN

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_info(self):
        _LOGGER.debug("My identifiers is %s", {(DOMAIN, self.unique_id)})
        info = {"identifiers": {(DOMAIN, self.unique_id)}, "name": self.name, "manufacturer": "SleepAsAndroid",
                "type": None}
        return info
