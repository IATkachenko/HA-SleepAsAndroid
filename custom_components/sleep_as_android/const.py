"""Consts for the integration."""

DOMAIN = "sleep_as_android"
DEVICE_MACRO: str = "%%%device%%%"

DEFAULT_NAME = "SleepAsAndroid"
DEFAULT_TOPIC_TEMPLATE = "SleepAsAndroid/%s" % DEVICE_MACRO
DEFAULT_QOS = 0

# available at https://docs.sleep.urbandroid.org/services/automation.html#events
sleep_tracking_states = [
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
    "show_skip_next_alarm",
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
    "sound_event_laugh",
    "before_alarm",
    "alarm_rescheduled",
]
