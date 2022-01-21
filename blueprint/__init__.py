import ruamel.yaml


yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True


def tagged_empty_scalar(tag, value):
    return yaml.load('!' + tag + " " + value)