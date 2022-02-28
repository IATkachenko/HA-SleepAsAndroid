"""Configuration via UI for the integration."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DEFAULT_NAME, DEFAULT_QOS, DEFAULT_TOPIC_TEMPLATE, DOMAIN


def get_value(config_entry: config_entries | None, param: str, default=None):
    """Get current value for configuration parameter.

    :param config_entry: config_entries|None: config entry from Flow
    :param param: str: parameter name for getting value
    :param default: default value for parameter, defaults to None
    :returns: parameter value, or default value or None
    """
    if config_entry is not None:
        return config_entry.options.get(param, config_entry.data.get(param, default))
    else:
        return default


def create_schema(
    config_entry: config_entries | None, step: str = "user"
) -> vol.Schema:
    """Generate configuration schema.

    :param config_entry: config_entries|None: config entry from Flow
    :param step: stem name
    """
    schema = vol.Schema({})
    if step == "user":
        schema = schema.extend(
            {
                vol.Required(
                    "name",
                    default=get_value(
                        config_entry=config_entry, param="name", default=DEFAULT_NAME
                    ),
                ): str,
            }
        )

    schema = schema.extend(
        {
            vol.Required(
                "topic_template",
                default=get_value(
                    config_entry=config_entry,
                    param="topic_template",
                    default=DEFAULT_TOPIC_TEMPLATE,
                ),
            ): str,
            vol.Optional(
                "qos",
                default=get_value(
                    config_entry=config_entry, param="qos", default=DEFAULT_QOS
                ),
            ): int,
        }
    )
    return schema


class SleepAsAndroidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """First time set up flow."""

    def __init__(self):
        """Initialize entry."""
        self._config_entry: config_entries | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SleepAsAndroidOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=create_schema(None, step="user")
        )


class SleepAsAndroidOptionsFlow(config_entries.OptionsFlow):
    """Changing options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()
        self._config_entry = config_entry
        self._entry_id = config_entry.entry_id

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=create_schema(self._config_entry, step="init"),
            errors=errors,
        )
