from enum import Enum

from custom_components.sleep_as_android.const import DOMAIN


Input = {
    'device': {
        "name": "SleepAsAndroid device",
        "description": "Device for Sleep as Android ",
        "selector": {
            "device": {
                "integration": f"{DOMAIN}",
            }
        }
    },
    'person': {
        "name": "Person",
        "description": "Person for checking state",
        "selector": {
            "entity": {
                "domain": "person"
            }
        }
    },
    'state': {
        "name": "State",
        "description": "Person must be in this state",
        "default": "home"
    }
}


class InputMapping(Enum):
    full = ["device", "person", "state"]
