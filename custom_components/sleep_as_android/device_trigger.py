import logging
import voluptuous as vol

from homeassistant.const import (CONF_TYPE, CONF_PLATFORM, CONF_DOMAIN, CONF_DEVICE_ID, )
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.core import HomeAssistant
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA as HA_TRIGGER_BASE_SCHEMA

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

# available at https://docs.sleep.urbandroid.org/services/automation.html#events
TRIGGERS = [
    "sleep_tracking_started",
    "sleep_tracking_stopped",
    "sleep_tracking_paused",
    "sleep_tracking_resumed",
    "alarm_snooze_clicked",
    "alarm_snooze_canceled",
    "time_to_bed_alarm_alert",
    "alarm_alert_start",
    "alarm_alert_dismiss",
    "alarm_skip_next",
    "rem",
    "smart_period",
    "before_smart_period",
    "lullaby_start",
    "lullaby_stop",
    "lullaby_volume_down",
    "deep_sleep",
    "light_sleep",
    "awake",
    "not_awake",
    "apnea_alarm",
    "antisnoring",
    "sound_event_snore",
    "sound_event_talk",
    "sound_event_cough",
    "sound_event_baby",
    "sound_event_laugh"
]

TRIGGER_SCHEMA = HA_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGERS),
    }
)


async def async_get_triggers(hass, device_id):
    """Return a list of triggers."""
    device_registry = await hass.helpers.device_registry.async_get_registry()
    device = device_registry.async_get(device_id)

    triggers = []

    for t in TRIGGERS:
        triggers.append({
            # Required fields of TRIGGER_BASE_SCHEMA
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            # Required fields of TRIGGER_SCHEMA
            CONF_TYPE: t,
        })

    return triggers


async def async_attach_trigger(hass: HomeAssistant, config, action, automation_info):
    """ Attach a trigger. """
    config = TRIGGER_SCHEMA(config)
    _LOGGER.debug("Got subscription to trigger: %s", config)
    event_config = event_trigger.TRIGGER_SCHEMA({
        event_trigger.CONF_PLATFORM: "event",
        event_trigger.CONF_EVENT_TYPE: DOMAIN + "_event",
        event_trigger.CONF_EVENT_DATA: {
            CONF_DEVICE_ID: config[CONF_DEVICE_ID],
            CONF_TYPE: config[CONF_TYPE],
        }
    })

    return await event_trigger.async_attach_trigger(
        hass, event_config, action, automation_info, platform_type="device"
    )
