
from io import StringIO

from custom_components.sleep_as_android.device_trigger import TRIGGERS, DOMAIN
import ruamel.yaml

yaml = ruamel.yaml.YAML()

yaml.preserve_quotes = True


def tagged_empty_scalar(tag, value):
    return yaml.load('!' + tag + " " + value)


def single_quote_dump(raw_str):
    changed_yaml = ruamel.yaml.YAML()
    changed_yaml.default_style = "'"
    return changed_yaml.load(raw_str)


def main():
    blueprint = {
        "blueprint": {
            "name": "Sleep as Android MQTT actions",
            "description": "Define actions based on Sleep As Android sensor states",
            "domain": "automation",
            "source_url": "",
            "input": {
                "device": {
                    "name": "SleepAsAndroid sensor",
                    "description": "Sensor for Sleep as Android device",
                    "selector": {
                        "entity": {
                            "domain": f"{DOMAIN}"
                        }
                    }
                },
                "person": {
                    "name": "Person",
                    "description": "Person for checking state",
                    "selector": {
                        "entity": {
                            "domain": "person"
                        }
                    }
                },
                "state": {
                    "name": "State",
                    "description": "Person must be in this state",
                    "default": "home"
                },
            },
        },
        "mode": "queued",
        "max_exceeded": "silent",
        "trigger": [
            {
                "platform": "state",
                "entity_id": tagged_empty_scalar("input", "'device'")
            }
        ],
        "condition": [
            {
                "condition": "state",
                "entity_id": tagged_empty_scalar("input", "person"),
                "state": tagged_empty_scalar("input", "state")
            }
        ],
        "action": [
            {
                "variables": {
                    "action": "{{ trigger.to_state.state }}"
                }
            },
            {
                "choose": []
            }
        ]
    }

    for t in TRIGGERS:
        blueprint["blueprint"]["input"][t] = {
            "name": t,
            "description": f"{t} event",
            "default": [],
            "selector": {"action": {} }
        }
        blueprint["action"][1]["choose"].append({
            "conditions": single_quote_dump(f"'{{{{ action == ''''{t}'''' }}}}'"),
            "sequence": tagged_empty_scalar("input", f"'{t}'")
        })

    string_stream = StringIO()

    yaml.dump(blueprint, string_stream)
    output_str = string_stream.getvalue()
    string_stream.close()
    print(output_str.replace('"', "'"))


if __name__ == '__main__':
    main()
