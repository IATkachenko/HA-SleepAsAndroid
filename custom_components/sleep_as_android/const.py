import voluptuous as vol

DOMAIN = "sleep_as_android"
DEVICE_MACRO: str = "%%%device%%%"

DEFAULT_NAME = "SleepAsAndroid"
DEFAULT_TOPIC_TEMPLATE = "SleepAsAndroid/%s" % DEVICE_MACRO
DEFAULT_QOS = 0
