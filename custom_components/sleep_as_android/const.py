import voluptuous as vol

DOMAIN = "sleep_as_android"

schema = {
    vol.Required("name", default="SleepAsAndroid"): str,
    vol.Required("topic", ): str,
    vol.Optional("qos", default=0): int
}