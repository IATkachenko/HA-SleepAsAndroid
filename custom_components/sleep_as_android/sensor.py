"""
Sensor for Sleep as android states
"""

import logging
import json

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_entries_for_config_entry


from .device_trigger import TRIGGERS
from .const import DOMAIN

from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from . import SleepAsAndroidInstance

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the sensor entry"""

    async def add_configured_entities():
        """Scan entity registry and add previously created entities to Home Assistant"""

        entities = async_entries_for_config_entry(instance.entity_registry, config_entry.entry_id)
        sensors: List[SleepAsAndroidSensor] = []
        for entity in entities:

            device_name = instance.device_name_from_entity_id(entity.unique_id)
            _LOGGER.debug(f"add_configured_entities: creating sensor with name {device_name}")
            (sensor, _) = instance.get_sensor(device_name)
            sensors.append(sensor)

        async_add_entities(sensors)

    instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]
    await add_configured_entities()
    _LOGGER.debug("async_setup_entry: adding configured entities is finished.")
    _LOGGER.debug("Going to subscribe to root topic.")
    await instance.subscribe_root_topic(async_add_entities)
    _LOGGER.debug("async_setup_entry is finished")
    return True


class SleepAsAndroidSensor(Entity):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, name: str):
        self._instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]

        self.hass: HomeAssistant = hass

        self._name: str = name
        self._state: str = STATE_UNKNOWN
        self._device_id: str = "unknown"
        _LOGGER.debug(f"Creating sensor with name {name}")

    async def async_added_to_hass(self):
        """
        Calls when sensor added to Home Assistant.
        Should create device for sensor here
        """
        await super().async_added_to_hass()
        device_registry = await dr.async_get_registry(self.hass)
        device = device_registry.async_get_device(identifiers=self.device_info['identifiers'], connections=set())
        _LOGGER.debug("My device id is %s", device.id)
        self._device_id = device.id
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        """
        Calls when sensor is removed from Home Assistant
        Should remove device here
        """
        # ToDo: should we remove device?
        pass

    def process_message(self, msg):
        """
        Process new MQTT messages.
        Set sensor state and fire events.

        :param msg: MQTT message
        """
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
        self.async_write_ha_state()

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._instance.create_entity_id(self._name)

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._instance.create_entity_id(self._name)

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
                "type": None, "model": "MQTT"}
        return info
