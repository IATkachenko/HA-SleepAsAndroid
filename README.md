# Sleep As Android custom integration

This integration will allow you to get events from your [SleepAsAndroid](https://sleep.urbandroid.org) application as sensor state and events in Home assistant.

## Installation & configuration
### Requirements
You will need:  
  * configured MQTT server in `configuration.yaml` like
    ```yaml
    mqtt:
      broker: mqtt.myserver
      port: 1883
      username: ha_husr
      discovery: true 
    ```
 * Sleep As android with MQTT support (currently betta version)
    * go to Settings -> Services -> Acclimatisation
    * enable and configure MQTT

### Installation
 * goto HACS->Integrations->three dot at upper-right conner->Custom repositories;
 * add IATkachenko/HA-SleepAsAndroid to ADD CUSTOM REPOSITORY field and select Integration in CATEGORY;
 * click "add" button;
 * find "Sleep As Andorid" integration;
 * click "Install". Home assistant restart may be required;
 
### Configuration
 * Name: name of sensor and prefix for events
 * Topic: same as topic in Sleep As Android configuration
 * QOS: quality of service for MQTT 
 
## Usage
`<name>` is integration name in lower case without spaces from settings dialog.
List of vents is avaliable at [Sleep As Android documentation page](https://docs.sleep.urbandroid.org/services/automation.html#events)
### on sensor state change
State of sensor `sensor.<name>` will have last event name, that published from application.
### on event
If application publish new event, then integration will fire `<name>` event with payload
```json
{
  "event": "<event_name_from_application>"
}
```

## Troubleshooting
`configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.sleep_as_android: debug
```
