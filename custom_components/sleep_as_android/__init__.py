"""Sleep As Android integration"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

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
        hass.loop.create_task(self.hass.config_entries.async_forward_entry_setup(self._config_entry, 'sensor'))
