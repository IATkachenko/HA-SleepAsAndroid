![version_badge](https://img.shields.io/badge/minimum%20HA%20version-2023.4-red)
![Validate with hassfest](https://github.com/IATkachenko/HA-SleepAsAndroid/workflows/Validate%20with%20hassfest/badge.svg) 
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) 
[![Custom badge](https://img.shields.io/endpoint?color=orange&label=patreon&url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%2F%3Fusername%3DIATkachenko%26type%3Dpatrons)](https://www.patreon.com/IATkachenko)

# Sleep As Android custom integration

This integration will allow you to get events from your [SleepAsAndroid](https://sleep.urbandroid.org) application in a form of the sensor states and events in Home assistant.

## Installation & configuration
### Requirements
You will need:  
  * [Home Assistant with configured MQTT integration](https://www.home-assistant.io/integrations/mqtt/)
    <br/>example of configuration.yaml:
    ```yaml
    mqtt:
      broker: mqtt.myserver
      port: 1883
      username: ha_user
      discovery: true 
    ```
  * [Sleep As android application](https://play.google.com/store/apps/details?id=com.urbandroid.sleep) 
     * go to Settings -> Services -> Automatization -> MQTT
     * enable and configure MQTT

### Installation
 * go to [HACS](https://hacs.xyz/docs/installation/installation) -> `Integrations`
 * press `+ Explore & Add repositories` button
 * type `Sleep As Android` in search field and click at integration name
 * press `Install this repository to HACS` button
 * press `Install` button _(if you have outdated version of Home Assistant -- [check integration version in Wiki](https://github.com/IATkachenko/HA-SleepAsAndroid/wiki/Versions-and-Updates) )_
 * restart **Home Assistant** 
 * go to **Home Assistant** `Settings` -> `Integrations` -> `Add Integration` (right bottom conner)
 * type `Sleep As Android` in search field and click at integration name. [Clean browser cache if nothing found](https://github.com/IATkachenko/HA-SleepAsAndroid/issues/29).

### Configuration 
#### Component configuration
 * `Name`: name of the device/sensor and a prefix for the events. Will be used as a default prefix for devices and events.
 * `Topic template`: template for MQTT topic where `Sleep as Android` will publish event. `%%%device%%%` may be used in template to point to device name position. Examples:
   * **SleepAsAndroid/igor** - no `%%%device%%%` in template just one device will be tracked and one device will be created for `HomeAssistant`
   * **SleepAsAndroid/%%%device%%%** - all sub topics in `SleepAsAndroid/` will be recognized as devices
   * **devices/%%%device%%%/SleepAsAndroidData** - all subtopic in `devices/` will be used as devices, data will be taken from `/SleepAsAndroidData` for every device, ie `devices/igor/SleepAsAndroidData` for device _igor_
 * `QOS`: quality of service for MQTT 

#### Application configuration
To configure `Sleep As Android` for working with this integration:
 1. Go to application settings
 1. Find **Services** in integration section
 1. Go to **Automation**
 1. Find **MQTT** section
 
 Then:
 * Enable it
 * `URL` is a URL for your MQTT server. It should look like `tcp://mqtt_user:mqtt_password@mqtt_host:mqtt_port`
 * `Topic` is a topic name where the application will publish events. See `Topic template` section of component configuration for details. Application settings **MUST NOT** have `%%%device%%%` macro. Use desired device name at position of `%%%device%%%` of integration configuration. Examples related to integration configuration above: **SleepAsAndroid/igor** or **devices/igor/SleepAsAndroidData**. Device name will be "igor" in both cases.
 * `Client ID` is any ID. It is not used by integration and is not published to MQTT (now).

![SleepAsAndroid configuration](./docs/images/SleepAsAndroidSetup.png)
 
More details in [Wiki](https://github.com/IATkachenko/HA-SleepAsAndroid/wiki/application-configuration).
 
## Usage
### blueprint (recommended)
 1. import [blueprint](blueprint/full.yaml):
    1. Got to Home Assistant `settings` 
    1. `blueprints` 
    1. `import blueprint` button
    1. put blueprint URL
    1. press `preview` button
    1. press `import` button
 1. create automatization based on blueprint:
    * `person` and `state` is using to run actions only if **person** in **state** (to avoid run home automatization related to sleep tracking while vacation in Siberia, for example)
    * add actions for [evens]((https://docs.sleep.urbandroid.org/services/automation.html#events))
    
### on device event
 1. select `Device` in automatization trigger and use `SleepAsAndroid` device;
 1. select trigger from a list.

![added_in_version_badge](https://img.shields.io/badge/Since-v1.7.0-red) events will be fired up for every MQTT message  
 
### on sensor state change
`<name>` is an integration name in lower case without spaces from the `Settings` dialog.
`<device>` is a device name
List of events is available at [Sleep As Android documentation page](https://docs.sleep.urbandroid.org/services/automation.html#events)

State of sensor `sensor.<name>_<device>` will contain the recent event name, that got published by the application.
### on event
`<name>` is an integration name in lower case without spaces from the `Settings` dialog.
If application publishes a new event, then integration fires `<name>` event with payload:
```json
{
  "event": "<event_name_from_application>"
}
```
![added_in_version_badge](https://img.shields.io/badge/Since-v1.7.0-red) events will be fired up for every MQTT message
## Attributes
![added_in_version_badge](https://img.shields.io/badge/Since-v1.7.0-red)

Sensor have additional attributes:
  * `timestamp` -- value1 from application event. It is usually timestamp of something. Meaning is depended on event. Please check [Sleep As Android events documentation](https://docs.sleep.urbandroid.org/services/automation.html#events) for more details;
  * `label` -- value2 from application event. It is usually alarm label. You can use this attribute to tell one alarm from another.

If event have no `value<N>` field, then attribute will be set to `unknown`.
## Troubleshooting
`configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.sleep_as_android: debug
```
