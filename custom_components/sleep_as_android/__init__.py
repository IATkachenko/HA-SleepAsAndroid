"""Sleep As Android integration"""

import logging
from typing import List

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .sensor import SleepAsAndroidSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry):
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    _LOGGER.info("Setting up %s ", config_entry.entry_id)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][config_entry.entry_id] = SleepAsAndroidInstance(hass, config_entry)
    return True


class SleepAsAndroidInstance:
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self._config_entry = config_entry
        self.sensors: List[SleepAsAndroidSensor] = []

        try:
            self._name: str = self.get_from_config('name')
        except KeyError:
            self._name = 'SleepAsAndroid'

        self.hass.loop.create_task(self.hass.config_entries.async_forward_entry_setup(self._config_entry, 'sensor'))

    def get_from_config(self, name: str) -> str:
        try:
            data = self._config_entry.options[name]
        except KeyError:
            data = self._config_entry.data[name]

        return data

    @property
    def name(self) -> str:
        return self._name

    @property
    def mqtt_topic(self) -> str:
        _topic = None

        try:
            _topic = self.get_from_config('root_topic')
        except KeyError:
            try:
                _topic = self.get_from_config('topic')
                _LOGGER.warning("You are using deprecated configuration with one topic per integration. \n"
                                "Please remove additional integration and set root topic for all devices instead.")
                _topic = '/'.join(_topic.split('/')[:-1])
            except KeyError:
                _topic = 'SleepAsAndroid'
                _LOGGER.critical("Could not find topic or root_topic in configuration. Will use %s instead",
                                 _topic)

        return _topic + '/+'
