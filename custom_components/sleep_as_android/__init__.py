"""Sleep As Android integration."""
from __future__ import annotations

from functools import cache, cached_property
import logging
import re
from typing import Callable

from awesomeversion import AwesomeVersion
from homeassistant.components.mqtt import subscription
from homeassistant.components.mqtt.subscription import EntitySubscription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import NoEntitySpecifiedError
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from pyhaversion import HaVersion

from .const import DEVICE_MACRO, DOMAIN
from .sensor import SleepAsAndroidSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup(_hass: HomeAssistant, _config_entry: ConfigEntry):
    """Set up the integration based on configuration.yaml."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up the integration based on config_flow."""
    _LOGGER.info("Setting up %s ", config_entry.entry_id)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    registry = er.async_get(hass)
    hass.data[DOMAIN][config_entry.entry_id] = SleepAsAndroidInstance(
        hass, config_entry, registry
    )

    await hass.config_entries.async_forward_entry_setups(
        config_entry, [Platform.SENSOR]
    )
    config_entry.async_on_unload(config_entry.add_update_listener(async_update_options))
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options for entry that was configured via user interface."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove entry configured via user interface."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(
        entry, Platform.SENSOR
    )
    if unload_ok:
        instance: SleepAsAndroidInstance = hass.data[DOMAIN].pop(entry.entry_id)
        await instance.unsubscribe()
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    _LOGGER.debug(
        f"Removing device {device_entry.name} ({device_entry.id=}) by user request"
    )

    dr.async_get(hass).async_remove_device(device_id=device_entry.id)
    instance: SleepAsAndroidInstance = hass.data[DOMAIN][config_entry.entry_id]
    instance.remove_sensor(device_entry.name)

    return True


class SleepAsAndroidInstance:
    """Instance for MQTT communication."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, registry: er):
        """Initialize entry."""
        self.hass = hass
        self._config_entry = config_entry
        self.__sensors: dict[str, SleepAsAndroidSensor] = {}
        self._entity_registry: er = registry
        self._subscription_state = None
        self._ha_version: AwesomeVersion | None = None

        try:
            self._name: str = self.get_from_config("name")
        except KeyError:
            self._name = "SleepAsAndroid"

        # ToDo prepare topic_template and other variables that should be defined one time.

    async def unsubscribe(self):
        """Unsubscribe from topics."""
        _LOGGER.debug(f"subscription state is {self._subscription_state}")
        if self._subscription_state is not None:
            _LOGGER.debug("Unsubscribing")
            if self._ha_version is None:
                await self._get_version()
            if self._ha_version >= AwesomeVersion("2022.3.0"):
                self._subscription_state = subscription.async_unsubscribe_topics(
                    hass=self.hass,
                    sub_state=self._subscription_state,
                )
            else:
                self._subscription_state = await subscription.async_unsubscribe_topics(
                    hass=self.hass,
                    sub_state=self._subscription_state,
                )

    @cached_property
    def device_position_in_topic(self) -> int:
        """Position of DEVICE_MACRO in configured MQTT topic."""
        result: int = 0

        for p in self.configured_topic.split("/"):
            if p == DEVICE_MACRO:
                break
            else:
                result += 1

        return result

    @staticmethod
    def device_name_from_topic_and_position(topic: str, position: int) -> str:
        """Get device name from full topic.

        :param topic: full topic from MQTT message
        :param position: position of device template
        :returns: device name
        """
        s = topic.split("/")
        if position >= len(s):
            # If we have no DEVICE_MACRO in configured_topic,
            # then device_position_in_topic is greater than topic length and we should use
            # last segment of topic as device name
            position = len(s) - 1

        return s[position]

    @cache
    def device_name_from_topic(self, topic: str) -> str:
        """Get device name from topic.

        :param topic: topic string from MQTT message
        :returns: device name
        """
        return self.device_name_from_topic_and_position(
            topic, self.device_position_in_topic
        )

    @cached_property
    def topic_template(self) -> str:
        """Convert topic with {device} to MQTT topic for subscribing."""
        splitted_topic = self.configured_topic.split("/")
        try:
            splitted_topic[self.device_position_in_topic] = "+"
        except IndexError:
            # If we have no DEVICE_MACRO in configured_topic,
            # then device_position_in_topic is greater than topic length
            pass
        return "/".join(splitted_topic)

    @cache
    def get_from_config(self, name: str) -> str:
        """Get current configuration."""
        try:
            data = self._config_entry.options[name]
        except KeyError:
            data = self._config_entry.data[name]

        return data

    @property
    def name(self) -> str:
        """Name of the integration in Home Assistant."""
        return self._name

    @cached_property
    def configured_topic(self) -> str:
        """MQTT topic from integration configuration."""
        _topic = None

        try:
            _topic = self.get_from_config("topic_template")
        except KeyError:
            _topic = "SleepAsAndroid/" + DEVICE_MACRO
            _LOGGER.warning(
                "Could not find topic_template in configuration. Will use %s instead",
                _topic,
            )

        return _topic

    @cache
    def create_entity_id(self, device_name: str) -> str:
        """Generate entity_id based on instance name and device name.

        Used to identify individual sensors.

        :param device_name: name of device
        :returns: id that may be used for searching sensor by entity_id in entity_registry
        """
        _LOGGER.debug(
            f"create_entity_id: my name is {self.name}, device name is {device_name}"
        )
        return self.name + "_" + device_name

    @cache
    def device_name_from_entity_id(self, entity_id: str) -> str:
        """Extract device name from entity_id.

        :param entity_id: entity id that was generated by self.create_entity_id
        :returns: pure device name
        """
        _LOGGER.debug(f"device_name_from_entity_id: entity_id='{entity_id}'")
        return entity_id.replace(self.name + "_", "", 1)

    @property
    def entity_registry(self) -> er:
        """Return the entity registry."""
        return self._entity_registry

    async def subscribe_root_topic(self, async_add_entities: Callable):
        """(Re)Subscribe to topics."""
        _LOGGER.debug(
            "Subscribing to '%s' (generated from '%s')",
            self.topic_template,
            self.configured_topic,
        )
        self._subscription_state = None

        @callback
        def message_received(msg):
            """Handle new MQTT messages."""

            _LOGGER.debug("Got message %s", msg)
            device_name = self.device_name_from_topic(msg.topic)
            entity_id = self.create_entity_id(device_name)
            _LOGGER.debug(f"sensor entity_id is {entity_id}")

            (target_sensor, is_new) = self.get_sensor(device_name)
            if is_new:
                async_add_entities([target_sensor], True)
            try:
                target_sensor.process_message(msg)
            except NoEntitySpecifiedError:
                # ToDo:  async_write_ha_state() runs before async_add_entities, so entity have no entity_id yet
                pass

        async def subscribe_2024_12(
            _hass: HomeAssistant, _state, _topic: dict
        ) -> dict[str, EntitySubscription]:

            result = subscription.async_prepare_subscribe_topics(
                hass=_hass,
                sub_state=_state,
                topics=_topic,
            )
            if result is not None:
                await subscription.async_subscribe_topics(
                    hass=self.hass,
                    sub_state=result,
                )
            return result

        async def subscribe_2022_03(
            _hass: HomeAssistant, _state, _topic: dict
        ) -> dict[str, EntitySubscription]:

            result = subscription.async_prepare_subscribe_topics(
                hass=_hass,
                new_state=_state,
                topics=_topic,
            )
            if result is not None:
                await subscription.async_subscribe_topics(
                    hass=self.hass,
                    sub_state=result,
                )
            return result

        async def subscribe_2021_07(
            _hass: HomeAssistant, _state, _topic: dict
        ) -> dict[str, EntitySubscription]:
            return await subscription.async_subscribe_topics(
                hass=_hass, new_state=_state, topics=_topic
            )

        topic = {
            "state_topic": {
                "topic": self.topic_template,
                "msg_callback": message_received,
                "qos": self._config_entry.data["qos"],
            }
        }

        if self._ha_version is None:
            await self._get_version()
        if self._ha_version >= AwesomeVersion("2024.12.0"):
            self._subscription_state = await subscribe_2024_12(
                self.hass,
                self._subscription_state,
                topic,
            )
        if self._ha_version >= AwesomeVersion("2022.3.0"):
            self._subscription_state = await subscribe_2022_03(
                self.hass,
                self._subscription_state,
                topic,
            )
        else:
            self._subscription_state = await subscribe_2021_07(
                self.hass,
                self._subscription_state,
                topic,
            )

        if self._subscription_state is not None:
            _LOGGER.debug("Subscribing to root topic is done!")
        else:
            _LOGGER.critical(f"Could not subscribe to topic {self.topic_template}")

    def get_sensor(self, sensor_name: str) -> (SleepAsAndroidSensor, bool):
        """Get sensor by it's name.

        If we have no such key in __sensors -- create new sensor

        :param sensor_name: name of sensor
        :return: (sensor with name "sensor_name", it it a new sensor)

        """
        try:
            return self.__sensors[sensor_name], False
        except KeyError:
            _LOGGER.info("New device! Let's create sensor for %s", sensor_name)
            new_sensor = SleepAsAndroidSensor(
                self.hass, self._config_entry, sensor_name
            )
            self.__sensors[sensor_name] = new_sensor
            return new_sensor, True

    async def _get_version(self) -> None:
        ha_version = HaVersion()
        await ha_version.get_version()
        ha_version_cleaned = re.sub(r"[ab][0-9]+$", "", ha_version.version)
        self._ha_version = AwesomeVersion(ha_version_cleaned)

    def remove_sensor(self, sensor_name: str) -> SleepAsAndroidSensor | None:
        """Remove sensor from internal list."""
        # cut prefix to convert device name to sensor name. create_entity_id have created it for us
        sensor_name = (
            sensor_name[len(self.name) + 1 :]
            if sensor_name.startswith(self.name)
            else sensor_name
        )

        _LOGGER.debug(
            f"Removing sensor {sensor_name} from internal list {self.__sensors}"
        )
        return self.__sensors.pop(sensor_name, None)
