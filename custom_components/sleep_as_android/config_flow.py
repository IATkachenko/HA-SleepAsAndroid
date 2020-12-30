import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, schema


class SleepAsAndroidFlow(config_entries.ConfigFlow, domain=DOMAIN):

    def __init__(self):
        self._data = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._data = user_input
            return self.async_create_entry(title=self._data['name'], data=self._data)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(schema)
        )


@config_entries.HANDLERS.register(DOMAIN)
class SleepAsAndroidConfigFlow(SleepAsAndroidFlow, config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        super().__init__()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SleepAsAndroidOptionsFlowHandler(config_entry)


class SleepAsAndroidOptionsFlowHandler(SleepAsAndroidFlow, config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self._config_entry = config_entry
        self._entry_id = config_entry.entry_id

    async def async_step_init(self, input=None):
        return await self.async_step_user(input)

