# Home Assistant MQTT Integration Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [MQTT Configuration](#mqtt-configuration)
- [MQTT Discovery](#mqtt-discovery)
- [MQTT Entities](#mqtt-entities)
- [MQTT Triggers](#mqtt-triggers)
- [MQTT Actions](#mqtt-actions)
- [JSON Payloads](#json-payloads)
- [Availability](#availability)
- [Wildcards](#wildcards)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol ideal for IoT devices. Home Assistant can both subscribe to and publish MQTT messages.

### Key Terms

| Term | Description |
|------|-------------|
| **Broker** | MQTT server that routes messages |
| **Topic** | Message address/channel |
| **Payload** | Message content |
| **QoS** | Quality of Service (0, 1, 2) |
| **Retain** | Keep last message for new subscribers |
| **Discovery** | Auto-configure devices via MQTT |

### MQTT Message Flow

```
Device → Publishes to topic → Broker → Subscribes → Home Assistant
Home Assistant → Publishes to topic → Broker → Subscribes → Device
```

### Common Brokers

| Broker | Description |
|--------|-------------|
| Mosquitto | Popular, lightweight, HA add-on available |
| EMQX | Enterprise features, clustering |
| HiveMQ | Cloud and self-hosted options |

---

## MQTT Configuration

### Via UI (Recommended)

1. Settings > Devices & Services > Add Integration
2. Search for "MQTT"
3. Enter broker details

### Via YAML (Legacy)

```yaml
# configuration.yaml
mqtt:
  broker: 192.168.1.100
  port: 1883
  username: !secret mqtt_user
  password: !secret mqtt_password
```

### Full Configuration Options

```yaml
mqtt:
  broker: 192.168.1.100
  port: 1883
  username: !secret mqtt_user
  password: !secret mqtt_password
  client_id: homeassistant
  keepalive: 60

  # TLS/SSL
  certificate: /ssl/ca.crt
  client_cert: /ssl/client.crt
  client_key: /ssl/client.key
  tls_insecure: false

  # Protocol
  protocol: 3.1.1  # or 5

  # Birth and Last Will
  birth_message:
    topic: homeassistant/status
    payload: online
    qos: 1
    retain: true
  will_message:
    topic: homeassistant/status
    payload: offline
    qos: 1
    retain: true
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `broker` | required | Broker hostname/IP |
| `port` | 1883 | Broker port |
| `username` | none | Authentication username |
| `password` | none | Authentication password |
| `client_id` | random | MQTT client identifier |
| `keepalive` | 60 | Keepalive interval (seconds) |
| `certificate` | none | CA certificate path |
| `protocol` | 3.1.1 | MQTT protocol version |

---

## MQTT Discovery

Discovery allows devices to auto-register with Home Assistant.

### Discovery Topic Format

```
<discovery_prefix>/<component>/<node_id>/<object_id>/config
```

Default prefix: `homeassistant`

### Discovery Message Example

```json
{
  "name": "Temperature",
  "device_class": "temperature",
  "state_topic": "sensors/living_room/temperature",
  "unit_of_measurement": "°C",
  "unique_id": "living_room_temp_001",
  "device": {
    "identifiers": ["living_room_sensor"],
    "name": "Living Room Sensor",
    "manufacturer": "DIY",
    "model": "ESP32 Sensor"
  }
}
```

### Publish Discovery Config

```bash
# Publish via mosquitto_pub
mosquitto_pub -h localhost -t "homeassistant/sensor/living_room/temperature/config" \
  -m '{"name":"Temperature","state_topic":"sensors/living_room/temp","unit_of_measurement":"°C","device_class":"temperature"}'
```

### Discovery Components

| Component | Entity Type |
|-----------|-------------|
| `binary_sensor` | Binary sensor |
| `sensor` | Sensor |
| `switch` | Switch |
| `light` | Light |
| `cover` | Cover |
| `fan` | Fan |
| `climate` | Climate/HVAC |
| `lock` | Lock |
| `alarm_control_panel` | Alarm |
| `number` | Number input |
| `select` | Select input |
| `button` | Button |
| `text` | Text input |

### Device Grouping

```json
{
  "name": "Temperature",
  "state_topic": "device/temp",
  "unique_id": "device_temp",
  "device": {
    "identifiers": ["my_device_001"],
    "name": "My Device",
    "manufacturer": "Acme",
    "model": "Sensor v2",
    "sw_version": "1.2.3",
    "configuration_url": "http://192.168.1.50"
  }
}
```

---

## MQTT Entities

### Sensor

```yaml
mqtt:
  sensor:
    - name: "Temperature"
      state_topic: "sensors/temperature"
      unit_of_measurement: "°C"
      device_class: temperature
      value_template: "{{ value_json.temperature }}"

    - name: "Humidity"
      state_topic: "sensors/humidity"
      unit_of_measurement: "%"
      device_class: humidity
```

### Binary Sensor

```yaml
mqtt:
  binary_sensor:
    - name: "Motion"
      state_topic: "sensors/motion"
      payload_on: "ON"
      payload_off: "OFF"
      device_class: motion

    - name: "Door"
      state_topic: "sensors/door"
      payload_on: "open"
      payload_off: "closed"
      device_class: door
      value_template: "{{ value_json.state }}"
```

### Switch

```yaml
mqtt:
  switch:
    - name: "Pump"
      state_topic: "device/pump/state"
      command_topic: "device/pump/set"
      payload_on: "ON"
      payload_off: "OFF"
      state_on: "ON"
      state_off: "OFF"

    - name: "Relay"
      command_topic: "device/relay/set"
      state_topic: "device/relay/state"
      optimistic: false
```

### Light

```yaml
mqtt:
  light:
    # Simple on/off light
    - name: "Lamp"
      command_topic: "light/lamp/set"
      state_topic: "light/lamp/state"

    # Dimmable light
    - name: "Ceiling Light"
      command_topic: "light/ceiling/set"
      state_topic: "light/ceiling/state"
      brightness_command_topic: "light/ceiling/brightness/set"
      brightness_state_topic: "light/ceiling/brightness/state"
      brightness_scale: 100

    # RGB light
    - name: "LED Strip"
      command_topic: "light/led/set"
      state_topic: "light/led/state"
      rgb_command_topic: "light/led/rgb/set"
      rgb_state_topic: "light/led/rgb/state"
      brightness_command_topic: "light/led/brightness/set"
      brightness_state_topic: "light/led/brightness/state"

    # JSON light (recommended)
    - name: "Smart Bulb"
      schema: json
      command_topic: "light/bulb/set"
      state_topic: "light/bulb/state"
      brightness: true
      color_mode: true
      supported_color_modes:
        - rgb
        - color_temp
```

### Cover

```yaml
mqtt:
  cover:
    - name: "Garage Door"
      command_topic: "cover/garage/set"
      state_topic: "cover/garage/state"
      payload_open: "OPEN"
      payload_close: "CLOSE"
      payload_stop: "STOP"
      state_open: "open"
      state_closed: "closed"
      device_class: garage

    - name: "Blinds"
      command_topic: "cover/blinds/set"
      state_topic: "cover/blinds/state"
      position_topic: "cover/blinds/position"
      set_position_topic: "cover/blinds/position/set"
      position_open: 100
      position_closed: 0
      device_class: blind
```

### Climate

```yaml
mqtt:
  climate:
    - name: "Thermostat"
      mode_command_topic: "hvac/mode/set"
      mode_state_topic: "hvac/mode/state"
      temperature_command_topic: "hvac/temp/set"
      temperature_state_topic: "hvac/temp/state"
      current_temperature_topic: "hvac/current_temp"
      modes:
        - "off"
        - "heat"
        - "cool"
        - "auto"
      min_temp: 15
      max_temp: 30
      temp_step: 0.5
```

### Lock

```yaml
mqtt:
  lock:
    - name: "Front Door"
      command_topic: "lock/front/set"
      state_topic: "lock/front/state"
      payload_lock: "LOCK"
      payload_unlock: "UNLOCK"
      state_locked: "LOCKED"
      state_unlocked: "UNLOCKED"
```

### Number

```yaml
mqtt:
  number:
    - name: "Fan Speed"
      command_topic: "fan/speed/set"
      state_topic: "fan/speed/state"
      min: 0
      max: 100
      step: 10
      unit_of_measurement: "%"
```

### Select

```yaml
mqtt:
  select:
    - name: "Mode"
      command_topic: "device/mode/set"
      state_topic: "device/mode/state"
      options:
        - "Auto"
        - "Manual"
        - "Away"
```

### Button

```yaml
mqtt:
  button:
    - name: "Restart"
      command_topic: "device/restart"
      payload_press: "RESTART"
```

---

## MQTT Triggers

### Basic MQTT Trigger

```yaml
automation:
  - id: mqtt_motion
    trigger:
      - platform: mqtt
        topic: "sensors/motion"
        payload: "ON"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

### JSON Payload Trigger

```yaml
automation:
  - id: mqtt_temperature_alert
    trigger:
      - platform: mqtt
        topic: "sensors/data"
        value_template: "{{ value_json.temperature }}"
        payload: "25"
    action:
      - service: notify.mobile_app
        data:
          message: "Temperature reached 25°C"
```

### Wildcard Topics

```yaml
automation:
  - id: mqtt_any_sensor
    trigger:
      - platform: mqtt
        topic: "sensors/+/state"  # Single-level wildcard
    action:
      - service: system_log.write
        data:
          message: "Received: {{ trigger.topic }} = {{ trigger.payload }}"
```

### Trigger Variables

```yaml
automation:
  - id: mqtt_with_variables
    trigger:
      - platform: mqtt
        topic: "device/status"
    action:
      - service: notify.mobile_app
        data:
          message: >
            Topic: {{ trigger.topic }}
            Payload: {{ trigger.payload }}
            QoS: {{ trigger.qos }}
```

---

## MQTT Actions

### Publish Message

```yaml
action:
  - service: mqtt.publish
    data:
      topic: "device/command"
      payload: "ON"
```

### With QoS and Retain

```yaml
action:
  - service: mqtt.publish
    data:
      topic: "device/command"
      payload: "ON"
      qos: 1
      retain: true
```

### JSON Payload

```yaml
action:
  - service: mqtt.publish
    data:
      topic: "device/settings"
      payload: >
        {"brightness": 80, "color": "warm"}
```

### Template Payload

```yaml
action:
  - service: mqtt.publish
    data:
      topic: "device/brightness"
      payload: "{{ states('input_number.brightness') | int }}"
```

### Complex JSON Template

```yaml
action:
  - service: mqtt.publish
    data:
      topic: "device/config"
      payload: >
        {
          "state": "{{ states('light.lamp') }}",
          "brightness": {{ state_attr('light.lamp', 'brightness') | default(0) }},
          "timestamp": "{{ now().isoformat() }}"
        }
```

---

## JSON Payloads

### Parsing JSON in Sensors

```yaml
mqtt:
  sensor:
    - name: "Temperature"
      state_topic: "sensors/data"
      value_template: "{{ value_json.temperature }}"
      unit_of_measurement: "°C"

    - name: "Humidity"
      state_topic: "sensors/data"
      value_template: "{{ value_json.humidity }}"
      unit_of_measurement: "%"
```

### Nested JSON

```yaml
# Payload: {"sensor": {"temp": 22.5, "hum": 55}}
mqtt:
  sensor:
    - name: "Nested Temp"
      state_topic: "device/data"
      value_template: "{{ value_json.sensor.temp }}"
```

### Array Access

```yaml
# Payload: {"values": [22.5, 23.1, 21.8]}
mqtt:
  sensor:
    - name: "First Value"
      state_topic: "device/data"
      value_template: "{{ value_json.values[0] }}"
```

### JSON Attributes

```yaml
mqtt:
  sensor:
    - name: "Device"
      state_topic: "device/state"
      value_template: "{{ value_json.status }}"
      json_attributes_topic: "device/state"
      json_attributes_template: >
        {
          "battery": {{ value_json.battery }},
          "rssi": {{ value_json.rssi }},
          "uptime": {{ value_json.uptime }}
        }
```

---

## Availability

### Simple Availability

```yaml
mqtt:
  sensor:
    - name: "Temperature"
      state_topic: "device/temp"
      availability_topic: "device/status"
      payload_available: "online"
      payload_not_available: "offline"
```

### Multiple Availability Topics

```yaml
mqtt:
  sensor:
    - name: "Temperature"
      state_topic: "device/temp"
      availability:
        - topic: "device/status"
          payload_available: "online"
          payload_not_available: "offline"
        - topic: "homeassistant/status"
          payload_available: "online"
          payload_not_available: "offline"
      availability_mode: all  # all, any, latest
```

### JSON Availability

```yaml
mqtt:
  sensor:
    - name: "Temperature"
      state_topic: "device/data"
      value_template: "{{ value_json.temp }}"
      availability_topic: "device/data"
      availability_template: >
        {{ 'online' if value_json.status == 'ok' else 'offline' }}
```

---

## Wildcards

### Single-Level Wildcard (+)

```yaml
# Matches: sensors/living/temp, sensors/bedroom/temp
# Not: sensors/living/room/temp

mqtt:
  sensor:
    - name: "Any Room Temp"
      state_topic: "sensors/+/temp"
```

### Multi-Level Wildcard (#)

```yaml
# Matches: sensors/a, sensors/a/b, sensors/a/b/c

automation:
  - trigger:
      - platform: mqtt
        topic: "sensors/#"
    action:
      - service: system_log.write
        data:
          message: "{{ trigger.topic }}: {{ trigger.payload }}"
```

### Wildcard in Automation

```yaml
automation:
  - id: log_all_tasmota
    trigger:
      - platform: mqtt
        topic: "tele/+/STATE"
    action:
      - service: system_log.write
        data:
          message: >
            Device: {{ trigger.topic.split('/')[1] }}
            State: {{ trigger.payload_json.POWER | default('unknown') }}
```

---

## Common Patterns

### Tasmota Device

```yaml
mqtt:
  switch:
    - name: "Tasmota Switch"
      command_topic: "cmnd/tasmota_device/POWER"
      state_topic: "stat/tasmota_device/POWER"
      availability_topic: "tele/tasmota_device/LWT"
      payload_on: "ON"
      payload_off: "OFF"
      payload_available: "Online"
      payload_not_available: "Offline"
```

### Shelly Device

```yaml
mqtt:
  switch:
    - name: "Shelly Switch"
      command_topic: "shellies/shelly1-ABC123/relay/0/command"
      state_topic: "shellies/shelly1-ABC123/relay/0"
      payload_on: "on"
      payload_off: "off"
      availability_topic: "shellies/shelly1-ABC123/online"
      payload_available: "true"
      payload_not_available: "false"
```

### ESP Device (ESPHome style)

```yaml
mqtt:
  binary_sensor:
    - name: "ESP Motion"
      state_topic: "esp_device/binary_sensor/motion/state"
      payload_on: "ON"
      payload_off: "OFF"
      device_class: motion
      availability_topic: "esp_device/status"
      payload_available: "online"
      payload_not_available: "offline"
```

### Sonoff RF Bridge

```yaml
automation:
  - id: rf_motion
    trigger:
      - platform: mqtt
        topic: "tele/rf_bridge/RESULT"
        value_template: "{{ value_json.RfReceived.Data }}"
        payload: "ABC123"  # RF code
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

---

## Best Practices

### Use Unique IDs

```yaml
mqtt:
  sensor:
    - name: "Temperature"
      unique_id: mqtt_living_room_temp
      state_topic: "sensors/living/temp"
```

### Consistent Topic Structure

```
# Recommended structure
<location>/<device>/<entity_type>/<function>

# Examples
home/living_room/sensor/temperature
home/bedroom/light/ceiling/state
home/garage/cover/door/position
```

### Use JSON for Complex Data

```yaml
# Instead of multiple topics
sensors/temp
sensors/humidity
sensors/battery

# Use single JSON topic
sensors/data
# {"temp": 22.5, "humidity": 55, "battery": 85}
```

### Set Appropriate QoS

```yaml
# QoS 0: Fire and forget (fast, may lose messages)
# QoS 1: At least once (recommended for most)
# QoS 2: Exactly once (slower, guaranteed)

mqtt:
  sensor:
    - name: "Critical Sensor"
      state_topic: "sensors/critical"
      qos: 2  # Important data
```

### Use Retain Wisely

```yaml
# Retain for state topics (so HA gets last state on restart)
mqtt:
  switch:
    - name: "Switch"
      state_topic: "device/state"  # Should be retained by device
      command_topic: "device/set"   # Don't need retain
```

---

## Troubleshooting

### Message Not Received

| Problem | Cause | Solution |
|---------|-------|----------|
| No updates | Wrong topic | Check topic spelling |
| Always unavailable | Wrong availability topic | Verify availability payload |
| Payload wrong | JSON parsing error | Check value_template |

### Debug with MQTT Explorer

```bash
# Install MQTT Explorer or use mosquitto_sub
mosquitto_sub -h localhost -t "#" -v
```

### Debug in Home Assistant

```yaml
# Enable MQTT debug logging
logger:
  default: info
  logs:
    homeassistant.components.mqtt: debug
```

### Test Publishing

```bash
# Test with mosquitto_pub
mosquitto_pub -h localhost -t "test/topic" -m "test message"

# With username/password
mosquitto_pub -h localhost -u user -P password -t "test/topic" -m "test"
```

### Common Issues

```yaml
# Issue: State shows payload instead of parsed value
# Fix: Add value_template
mqtt:
  sensor:
    - name: "Temp"
      state_topic: "sensors/data"
      value_template: "{{ value_json.temperature }}"  # Add this

# Issue: Entity always unavailable
# Fix: Check availability topic and payload
mqtt:
  sensor:
    - name: "Sensor"
      availability_topic: "device/status"
      payload_available: "online"      # Must match exactly
      payload_not_available: "offline"

# Issue: Commands not working
# Fix: Verify command topic format
mqtt:
  switch:
    - name: "Switch"
      command_topic: "cmnd/device/POWER"  # Check device expects this
      payload_on: "ON"                     # Check device expects this
```

### Verify Connection

```yaml
# Developer Tools > Services
service: mqtt.publish
data:
  topic: "test/homeassistant"
  payload: "Hello from HA"

# Check broker received message
# Then test subscription
service: mqtt.dump
data:
  topic: "test/#"
  duration: 10
```
