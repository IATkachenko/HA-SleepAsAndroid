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

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the sensor entry"""
    async_add_entities([SleepAsAndroidSensor(hass, config_entry)])
    return True


class SleepAsAndroidSensor(Entity):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self._hass: HomeAssistant = hass
        self._entity_id: ConfigEntry.entry_id = config_entry.entry_id
        self._topic: str = config_entry.data['topic']
        self._qos = config_entry.data['qos']
        self._name = config_entry.data['name']
        self._config = config_entry.data

        self._state: str = STATE_UNKNOWN
        self._sub_state = None  # subscription state

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""
        await super().async_added_to_hass()
        await self._subscribe_topics()

    async def async_will_remove_from_hass(self):
        self._sub_state = await subscription.async_unsubscribe_topics(self._hass, self._sub_state)

    async def _subscribe_topics(self):
        """(Re)Subscribe to topics."""
        _LOGGER.debug("Subscribing ... ")

        @callback
        # @log_messages(self.hass, self.entity_id)
        def message_received(msg):
            """Handle new MQTT messages."""
            new_state = STATE_UNKNOWN

            try:
                new_state = json.loads(msg.payload)['event']
            except KeyError:
                _LOGGER.warning("Got unexpected payload: '%s'", msg.payload)

            if self.state != new_state:
                payload = {"event": new_state}
                _LOGGER.debug("Firing '%s' with payload: '%s'", self.name, payload)
                self.hass.bus.fire(self.name, payload)
                self._state = new_state
                self.async_write_ha_state()

        self._sub_state = await subscription.async_subscribe_topics(self._hass, self._sub_state, {
            "state_topic": {"topic": self._topic, "msg_callback": message_received,
                "qos": self._qos, }}, )
        _LOGGER.debug("Subscribing ... done!")

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
        return self.name + "_" + self._topic.replace('/', '_')

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:sleep"

    @property
    def available(self) -> bool:
        return self.state != STATE_UNKNOWN
