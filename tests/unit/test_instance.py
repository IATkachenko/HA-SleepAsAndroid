import unittest
import unittest.mock as mock
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock
import aiounittest
import sys
import os
import uuid

import sleep_as_android

sys.path.append(os.path.join(sys.path[0], "../../custom_components"))

from sleep_as_android import SleepAsAndroidInstance
from sleep_as_android.const import DOMAIN, DEVICE_MACRO

SleepAsAndroidInstance_cache = SleepAsAndroidInstance
hass = MagicMock()
config_entry = MagicMock()
hass.data = {}


class TestingSleepAsAndroidInstance(SleepAsAndroidInstance):
    def __init__(self, hass=None, config_entry=None, registry=None):
        pass


class SleepAsAndroidInstanceTests(unittest.TestCase):
    def test_device_name_from_topic_and_position(self):
        topic = 'foo/bar/baz/moo'
        variants = (
            ['test', 1, 'test'],
            [topic, 2, 'baz'],
            [topic, 8, 'moo']
        )
        for t, position, expect in variants:
            self.assertEqual(
                SleepAsAndroidInstance.device_name_from_topic_and_position(t, position),
                expect
            )

    def test_device_position_in_topic(self):
        with patch(__name__+'.TestingSleepAsAndroidInstance.configured_topic', new_callable=mock.PropertyMock ) as mock_configured_topic:
            mock_configured_topic.return_value = 'SleepAsAndroid/%%%device%%%'
            instance = TestingSleepAsAndroidInstance(hass=None, config_entry=None, registry=None)
            self.assertEqual(instance.device_position_in_topic, 1)

    @patch(__name__+".SleepAsAndroidInstance.configured_topic", new_callable=PropertyMock)
    @patch(__name__+".SleepAsAndroidInstance.device_position_in_topic", new_callable=PropertyMock)
    def test_topic_template(self, mocked_device_position_in_topic, mocked_configured_topic):
        variants = (
            ['foo/bar', 2, 'foo/bar'],
            ['baz/%%%device%%%', 1, 'baz/+'],
            ['foo/%%%device%%%/bar', 1, 'foo/+/bar'],
            ['foo/%%%device%%%baz/bar', 3, 'foo/%%%device%%%baz/bar'],
        )
        for template, position, expect in variants:
            with self.subTest(template=template, position=position, expect=expect):
                mocked_device_position_in_topic.return_value = position
                mocked_configured_topic.return_value = template
                instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
                self.assertEqual(instance.topic_template, expect)

    def test_name(self):
        name = uuid.uuid4()

        type(config_entry).options = PropertyMock(
            return_value={
                'name': name,
                'topic_template': uuid.uuid4(),
            })
        instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
        self.assertEqual(instance.name, name)

        #  check default name
        type(config_entry).options = PropertyMock(return_value={})
        type(config_entry).data = PropertyMock(return_value={})

        instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
        self.assertEqual(instance.name, 'SleepAsAndroid')

    @patch(__name__+".SleepAsAndroidInstance.device_position_in_topic", new_callable=PropertyMock)
    def test_device_name_from_topic(self, mocked_device_position_in_topic):
        topic = 'foo/bar/baz/moo'
        variants = (
            ['test', 1, 'test'],
            [topic, 2, 'baz'],
            [topic, 8, 'moo']
        )
        instance = TestingSleepAsAndroidInstance(None, None, None)
        for t, position, expect in variants:
            mocked_device_position_in_topic.return_value = position
            self.assertEqual(instance.device_name_from_topic(t), expect)

    @patch(__name__+".SleepAsAndroidInstance.get_from_config")
    def test_configured_topic(self, mocked_get_from_config):
        def side_effect(_arg):
            raise KeyError

        variants = (
            ['foo'],
            ['foo/bar']
        )
        instance = TestingSleepAsAndroidInstance(None, None, None)
        for v in variants:
            with self.subTest(topic=v, expect=v):
                mocked_get_from_config.return_value = v
                self.assertEqual(instance.configured_topic, v)

        mocked_get_from_config.side_effect = side_effect
        self.assertEqual(instance.configured_topic, 'SleepAsAndroid/' + DEVICE_MACRO)

    @patch(__name__+".SleepAsAndroidInstance.name", new_callable=PropertyMock)
    def test_create_entity_id(self, mocked_name):
        variants = (
            [ 'foo', 'bar', 'foo_bar' ],
        )
        instance = TestingSleepAsAndroidInstance(None, None, None)
        for name, device_name, e in variants:
            with self.subTest(name=name, device_name=device_name, expect=e):
                mocked_name.return_value = name
                self.assertEqual(instance.create_entity_id(device_name), e)

    @patch(__name__ + ".SleepAsAndroidInstance.name", new_callable=PropertyMock)
    def test_device_name_from_entity_id(self, mocked_name):
        variants = (
            ['foo', 'foo_bar', 'bar'],
        )
        instance = TestingSleepAsAndroidInstance(None, None, None)
        for name, entity_id, e in variants:
            with self.subTest(name=name, entity_id=entity_id, expect=e):
                mocked_name.return_value = name
                self.assertEqual(instance.device_name_from_entity_id(entity_id), e)

class AsyncSleepAsAndroidInstanceTests(aiounittest.AsyncTestCase):
    async def test_async_setup(self):
        ret = await sleep_as_android.async_setup(None, None)
        self.assertTrue(ret)

    @patch('homeassistant.helpers.entity_registry.async_get_registry')
    @patch(__name__ + '.SleepAsAndroidInstance', spec=SleepAsAndroidInstance)
    async def test_async_setup_entry(self, mocked_SleepAsAndroidInstance, mocked_entity_registry):
        mocked_entry_id = PropertyMock(return_value=uuid.uuid4())
        type(config_entry).entry_id = mocked_entry_id

        ret = await sleep_as_android.async_setup_entry(hass, config_entry)

        self.assertIsInstance(hass.data[DOMAIN][config_entry.entry_id], SleepAsAndroidInstance_cache)
        self.assertTrue(ret)


if __name__ == '__main__':
    unittest.main(verbosity=3)
