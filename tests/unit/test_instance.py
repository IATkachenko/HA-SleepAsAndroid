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
from sleep_as_android.const import DOMAIN

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
        self.assertEqual(
            SleepAsAndroidInstance.device_name_from_topic_and_position(topic, 2),
            'baz'
        )
        self.assertEqual(
            SleepAsAndroidInstance.device_name_from_topic_and_position(topic, 8),
            'moo'
        )

    def test_device_position_in_topic(self):
        with patch(__name__+'.TestingSleepAsAndroidInstance.configured_topic', new_callable=mock.PropertyMock ) as mock_configured_topic:
            mock_configured_topic.return_value = 'SleepAsAndroid/%%%device%%%'
            instance = TestingSleepAsAndroidInstance(hass=None, config_entry=None, registry=None)
            self.assertEqual(instance.device_position_in_topic, 1)

    def test_topic_template(self):
        name = uuid.uuid4()
        varaints = (
            ['foo/bar', 'foo/bar' ],
            ['baz/%%%device%%%', 'baz/+'],
            ['foo/%%%device%%%/bar', 'foo/+/bar'],
            ['foo/%%%device%%%baz/bar', 'foo/%%%device%%%baz/bar'],
        )
        for template, expect in varaints:
            type(config_entry).options = PropertyMock(
                return_value={
                    'name': name,
                    'topic_template': template,
            })
            with self.subTest(template=template):
                instance = SleepAsAndroidInstance(hass=hass, config_entry=config_entry, registry=None)
                self.assertEqual(instance.topic_template, expect)

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
