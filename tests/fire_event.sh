#!/bin/bash

TOPIC='SleepAsAndroid/test'
send_message() {
  local topic="$1"
  local message="$2"

  docker exec -it mqtt mosquitto_pub -h localhost -i client -m "${message}" -t "${topic}" -u client -d
}

send_message "$TOPIC" '{"event": "sleep_tracking_started"}'
