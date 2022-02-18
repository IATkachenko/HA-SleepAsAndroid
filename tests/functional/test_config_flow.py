"""Test integration_blueprint config flow."""

import json
from unittest.mock import MagicMock, patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_NAME
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sleep_as_android.const import DOMAIN

USER_INPUT = {
    "name": "SleepAsAndroid_test",
    "topic_template": "SleepAsAndroid_test/%%%device%%%",
    "qos": 10,
}


@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        "custom_components.sleep_as_android.async_setup_entry",
        return_value=True,
    ):
        yield


async def _flow_init(hass, advanced_options=True):
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_USER,
            "show_advanced_options": advanced_options,
        },
    )


async def _flow_configure(hass, r, _input=USER_INPUT):
    with patch(
        "homeassistant.helpers.entity_registry.EntityRegistry.async_get",
        return_value=MagicMock(unique_id="foo"),
    ):
        return await hass.config_entries.flow.async_configure(
            r["flow_id"], user_input=_input
        )


async def test_successful_config_flow(hass, mqtt_mock):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await _flow_init(hass)

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await _flow_configure(hass, result)

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY

    assert result["title"] == USER_INPUT[CONF_NAME]
    assert result["data"] == USER_INPUT
    assert result["result"]


async def test_options_flow(hass, mqtt_mock):
    """Test flow for options changes."""
    # setup entry
    entry = MockConfigEntry(domain=DOMAIN, data=USER_INPUT, entry_id="test")
    entry.add_to_hass(hass)

    # Initialize an options flow for entry
    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"show_advanced_options": True}
    )

    # Verify that the first options step is a user form
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # Enter some data into the form
    new_input = dict(USER_INPUT)
    del new_input["name"]
    new_input["topic_template"] = "new_topic/%%%device%%%"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=new_input,
    )

    # Verify that the flow finishes
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == ""

    # Verify that the options were updated

    assert entry.options == new_input


async def test_config_flow_enabled():
    """Test is manifest.json have 'config_flow': true."""
    with open("custom_components/sleep_as_android/manifest.json") as f:
        manifest = json.load(f)
        assert manifest.get("config_flow") is True