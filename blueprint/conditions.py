from enum import Enum
from __init__ import tagged_empty_scalar


Condition = {
    "person_in_state": {
        "condition": "state",
        "entity_id": tagged_empty_scalar("input", "person"),
        "state": tagged_empty_scalar("input", "state")
    },
    "label": {
        "condition": "state",
        "entity_id": tagged_empty_scalar("input", "sensor"),
        "attribute": "label",
        "state": tagged_empty_scalar("input", "label"),
    }
}


class ConditionMapping(Enum):
    full = ["person_in_state"]
    labeled = ["person_in_state", "label"]
