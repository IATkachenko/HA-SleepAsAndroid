from enum import Enum
from io import StringIO
import os
import sys

from __init__ import tagged_empty_scalar, yaml
from conditions import Condition, ConditionMapping
from inputs import Input, InputMapping
import ruamel.yaml

from custom_components.sleep_as_android.device_trigger import DOMAIN, TRIGGERS


def single_quote_dump(raw_str):
    changed_yaml = ruamel.yaml.YAML()
    changed_yaml.default_style = "'"
    return changed_yaml.load(raw_str)


class OutputMapping(Enum):
    full = "full.yaml"
    labeled = "labeled.yaml"


class Triggers(Enum):
    full = TRIGGERS
    labeled = [
        "alarm_snooze_clicked",
        "alarm_snooze_canceled",
        "alarm_alert_start",
        "alarm_alert_dismiss",
        "alarm_skip_next",
    ]  # Triggers that have label


def main(workdir: str, bp_type: str):
    file_name = OutputMapping[bp_type].value
    file = f"{workdir}/{file_name}"
    blueprint = {
        "blueprint": {
            "name": "Sleep as Android MQTT actions",
            "description": "Define actions based on Sleep As Android sensor states",
            "domain": "automation",
            "source_url": f"https://github.com/IATkachenko/HA-SleepAsAndroid/blob/main/blueprint/{file_name}",
            "input": {},
        },
        "mode": "queued",
        "max_exceeded": "silent",
        "trigger": [],
        "condition": [],
        "action": [{
                "choose": []
        }]
    }
    for c in ConditionMapping[bp_type].value:
        blueprint["condition"].append(Condition.get(c))

    for i in InputMapping[bp_type].value:
        blueprint["blueprint"]["input"][i] = Input.get(i)

    for t in Triggers[bp_type].value:
        blueprint["blueprint"]["input"][t] = {
            "name": t,
            "description": f"{t} event",
            "default": [],
            "selector": {"action": {}},
        }
        blueprint["action"][0]["choose"].append(
            {
                "conditions": {
                    "condition": "trigger",
                    "id": f"{t}",
                },
                "sequence": tagged_empty_scalar("input", f"'{t}'"),
            }
        )
        blueprint["trigger"].append(
            {
                "platform": "device",
                "domain": f"{DOMAIN}",
                "device_id": tagged_empty_scalar("input", "'device'"),
                "type": f"{t}",
                "id": f"{t}",
            }
        )

    string_stream = StringIO()

    yaml.dump(blueprint, string_stream)
    output_str = string_stream.getvalue()
    string_stream.close()
    print(output_str.replace('"', "'"))

    with open(file, "w") as outfile:
        yaml.dump(blueprint, outfile)


if __name__ == "__main__":
    for t in Triggers:
        main(workdir=os.path.dirname(sys.argv[0]), bp_type=t.name)
