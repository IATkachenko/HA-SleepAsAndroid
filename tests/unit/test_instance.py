import pytest
import unittest.mock as mock
from unittest.mock import patch, MagicMock, PropertyMock
from homeassistant.helpers import entity_registry

import uuid

import custom_components.sleep_as_android
from custom_components.sleep_as_android import SleepAsAndroidInstance
from custom_components.sleep_as_android.const import DOMAIN, DEVICE_MACRO

SleepAsAndroidInstance_cache = SleepAsAndroidInstance
hass = MagicMock()
config_entry = MagicMock()
hass.data = {}


@pytest.mark.skip
class TestingSleepAsAndroidInstance(SleepAsAndroidInstance):
    def __init__(self, hass=None, config_entry=None, registry=None):
        pass


class TestSleepAsAndroidInstance:

    @pytest.mark.parametrize(
        "t, position, expect", [
            ('test', 1, 'test'),
            ("foo/bar/baz/moo", 2, 'baz'),
            ("foo/bar/baz/moo", 8, 'moo'),
        ])
    def test_device_name_from_topic_and_position(self, t, position, expect):
        assert SleepAsAndroidInstance.device_name_from_topic_and_position(t, position) == expect

    def test_device_position_in_topic(self):
        with patch(__name__+'.TestingSleepAsAndroidInstance.configured_topic', new_callable=mock.PropertyMock ) as mock_configured_topic:
            mock_configured_topic.return_value = 'SleepAsAndroid/%%%device%%%'
            instance = TestingSleepAsAndroidInstance(hass=None, config_entry=None, registry=None)
            assert instance.device_position_in_topic == 1

    @pytest.mark.parametrize("template, position, expect", [
        ('foo/bar', 2, 'foo/bar'),
        ('baz/%%%device%%%', 1, 'baz/+'),
        ('foo/%%%device%%%/bar', 1, 'foo/+/bar'),
        ('foo/%%%device%%%baz/bar', 3, 'foo/%%%device%%%baz/bar'),
    ])
    @patch(__name__ + ".SleepAsAndroidInstance.configured_topic", new_callable=PropertyMock)
    @patch(__name__ + ".SleepAsAndroidInstance.device_position_in_topic", new_callable=PropertyMock)
    def test_topic_template(self, mocked_device_position_in_topic, mocked_configured_topic, template, position, expect, ):
        mocked_device_position_in_topic.return_value = position
        mocked_configured_topic.return_value = template
        instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
        assert instance.topic_template == expect

    def test_name(self):
        name = uuid.uuid4()

        type(config_entry).options = PropertyMock(
            return_value={
                'name': name,
                'topic_template': uuid.uuid4(),
            })
        instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
        assert instance.name == name

        #  check default name
        type(config_entry).options = PropertyMock(return_value={})
        type(config_entry).data = PropertyMock(return_value={})

        instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
        assert instance.name == 'SleepAsAndroid'

    @pytest.mark.parametrize("t, position, expect", [
        ('test', 1, 'test'),
        ("foo/bar/baz/moo", 2, 'baz'),
        ("foo/bar/baz/moo", 8, 'moo'),
    ])
    @patch(__name__ + ".SleepAsAndroidInstance.device_position_in_topic", new_callable=PropertyMock)
    def test_device_name_from_topic(self, mocked_device_position_in_topic, t, position, expect,):
        instance = TestingSleepAsAndroidInstance(None, None, None)
        mocked_device_position_in_topic.return_value = position
        assert instance.device_name_from_topic(t) == expect

    @pytest.mark.parametrize("v", [
        'foo',
        'foo/bar',
    ])
    @patch(__name__ + ".SleepAsAndroidInstance.get_from_config")
    def test_configured_topic(self, mocked_get_from_config, v):
        instance = TestingSleepAsAndroidInstance(None, None, None)
        mocked_get_from_config.return_value = v
        assert instance.configured_topic == v

    @patch(__name__ + ".SleepAsAndroidInstance.get_from_config")
    def test_with_exception(self, mocked_get_from_config):
        def side_effect(_arg):
            raise KeyError

        instance = TestingSleepAsAndroidInstance(None, None, None)
        mocked_get_from_config.side_effect = side_effect
        assert instance.configured_topic == 'SleepAsAndroid/' + DEVICE_MACRO

    @pytest.mark.parametrize("name, device_name, e", [
        ('foo', 'bar', 'foo_bar'),
    ])
    @patch(__name__+".SleepAsAndroidInstance.name", new_callable=PropertyMock)
    def test_create_entity_id(self, mocked_name, name, device_name, e):
        instance = TestingSleepAsAndroidInstance(None, None, None)
        mocked_name.return_value = name
        assert instance.create_entity_id(device_name) == e

    @pytest.mark.parametrize("name, entity_id, e", [
        ('foo', 'foo_bar', 'bar'),
    ])
    @patch(__name__ + ".SleepAsAndroidInstance.name", new_callable=PropertyMock)
    def test_device_name_from_entity_id(self, mocked_name, name, entity_id, e):
        instance = TestingSleepAsAndroidInstance(None, None, None)
        mocked_name.return_value = name
        assert instance.device_name_from_entity_id(entity_id) == e

    @patch('homeassistant.helpers.entity_registry.async_get_registry', spec=entity_registry.EntityRegistry)
    def test_entity_registry(self, mocked_entity_registry):
        instance = SleepAsAndroidInstance(hass, config_entry, mocked_entity_registry)
        assert isinstance(instance.entity_registry, entity_registry.EntityRegistry) is True


class TestAsyncSleepAsAndroidInstance:
    async def test_async_setup(self):
        assert await custom_components.sleep_as_android.async_setup(None, None) is True

    @patch('homeassistant.helpers.entity_registry.async_get_registry')
    @patch(__name__ + '.SleepAsAndroidInstance', spec=SleepAsAndroidInstance)
    async def test_async_setup_entry(self, mocked_SleepAsAndroidInstance, mocked_entity_registry):
        mocked_entry_id = PropertyMock(return_value=uuid.uuid4())
        type(config_entry).entry_id = mocked_entry_id

        ret = await custom_components.sleep_as_android.async_setup_entry(hass, config_entry)

        assert isinstance(hass.data[DOMAIN][config_entry.entry_id], SleepAsAndroidInstance_cache) is True
        assert ret is True
