import voluptuous as vol

DOMAIN = "sleep_as_android"
DEVICE_MACRO: str = "%%%device%%%"

schema = {
    vol.Required("name", default="SleepAsAndroid"): str,
    vol.Required("topic_template", default="SleepAsAndroid/%s" % DEVICE_MACRO): str,
    vol.Optional("qos", default=0): int
}