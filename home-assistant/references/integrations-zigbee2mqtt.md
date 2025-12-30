# Home Assistant Zigbee2MQTT Integration Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Zigbee2MQTT Setup](#zigbee2mqtt-setup)
- [Device Pairing](#device-pairing)
- [Entity Naming](#entity-naming)
- [MQTT Topics](#mqtt-topics)
- [Device Triggers](#device-triggers)
- [Groups](#groups)
- [Binding](#binding)
- [Device Configuration](#device-configuration)
- [Availability](#availability)
- [Common Devices](#common-devices)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Zigbee2MQTT bridges Zigbee devices to MQTT, allowing Home Assistant to control them via the MQTT integration.

### Key Terms

| Term | Description |
|------|-------------|
| **Coordinator** | USB Zigbee adapter |
| **Router** | Mains-powered device that extends network |
| **End Device** | Battery device, doesn't route |
| **Binding** | Direct device-to-device communication |
| **Group** | Multiple devices controlled together |
| **OTA** | Over-the-air firmware updates |

### Architecture

```
Zigbee Device → Coordinator → Zigbee2MQTT → MQTT Broker → Home Assistant
```

### Supported Coordinators

| Coordinator | Description |
|-------------|-------------|
| CC2652P | Popular, well-supported |
| ConBee II/III | Deconz compatible |
| SONOFF ZBDongle-P | CC2652P based |
| SONOFF ZBDongle-E | EFR32MG21 based |
| SLZB-06 | Ethernet/PoE option |

---

## Zigbee2MQTT Setup

### Home Assistant Add-on

```yaml
# Install via: Settings > Add-ons > Add-on Store > Zigbee2MQTT

# Configuration (via add-on UI or configuration.yaml)
serial:
  port: /dev/ttyUSB0
  adapter: zstack  # or ezsp, deconz

mqtt:
  server: mqtt://core-mosquitto:1883
  user: !secret mqtt_user
  password: !secret mqtt_password

advanced:
  network_key: GENERATE
  pan_id: GENERATE
```

### Docker Compose

```yaml
version: '3.8'
services:
  zigbee2mqtt:
    image: koenkk/zigbee2mqtt
    volumes:
      - ./data:/app/data
      - /run/udev:/run/udev:ro
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    environment:
      - TZ=Europe/Stockholm
    restart: unless-stopped
```

### configuration.yaml (Z2M)

```yaml
# /config/zigbee2mqtt/configuration.yaml

homeassistant: true  # Enable HA MQTT discovery
permit_join: false

mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://localhost:1883

serial:
  port: /dev/ttyUSB0

advanced:
  log_level: info
  network_key: [1, 3, 5, 7, 9, 11, 13, 15, 0, 2, 4, 6, 8, 10, 12, 13]
  pan_id: 6754
  channel: 11

frontend:
  port: 8080

device_options:
  retain: true
```

---

## Device Pairing

### Enable Pairing

```yaml
# Via HA service
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/permit_join
  payload: '{"value": true}'

# With timeout
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/permit_join
  payload: '{"value": true, "time": 120}'
```

### Via Automation

```yaml
automation:
  - id: z2m_permit_join
    alias: "Z2M Permit Join"
    trigger:
      - platform: state
        entity_id: input_boolean.zigbee_permit_join
        to: "on"
    action:
      - service: mqtt.publish
        data:
          topic: zigbee2mqtt/bridge/request/permit_join
          payload: '{"value": true, "time": 120}'
      - delay: "00:02:00"
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.zigbee_permit_join
```

### Disable Pairing

```yaml
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/permit_join
  payload: '{"value": false}'
```

### Interview Device

```yaml
# Force re-interview
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/interview
  payload: '{"id": "0x00158d0001234567"}'
```

---

## Entity Naming

### Rename Device

```yaml
# Via MQTT
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/rename
  payload: '{"from": "0x00158d0001234567", "to": "living_room_motion"}'

# Via configuration.yaml (Z2M)
devices:
  '0x00158d0001234567':
    friendly_name: living_room_motion
```

### Entity ID Format

```
# Default format
[domain].[friendly_name]_[property]

# Examples
binary_sensor.living_room_motion_occupancy
sensor.living_room_motion_battery
sensor.living_room_motion_temperature
light.living_room_bulb
```

### Customize Entity Names

```yaml
# Z2M configuration.yaml
devices:
  '0x00158d0001234567':
    friendly_name: living_room_motion
    homeassistant:
      occupancy:
        name: "Living Room Motion"
        device_class: motion
      battery:
        name: "Living Room Motion Battery"
```

---

## MQTT Topics

### Topic Structure

```
zigbee2mqtt/
├── bridge/
│   ├── state                 # Bridge online/offline
│   ├── info                  # Bridge info
│   ├── devices               # List of devices
│   ├── groups                # List of groups
│   ├── event                 # Device events
│   └── request/              # Commands
│       ├── permit_join
│       ├── device/rename
│       └── device/remove
├── [device_name]/
│   ├── (state payload)       # Device state
│   ├── set                   # Control device
│   ├── get                   # Request state
│   └── availability          # Online status
└── [group_name]/
    ├── (state payload)
    └── set
```

### Device State Topic

```json
// zigbee2mqtt/living_room_motion
{
  "battery": 100,
  "illuminance": 150,
  "illuminance_lux": 150,
  "linkquality": 120,
  "occupancy": true,
  "temperature": 24.5,
  "voltage": 3005
}
```

### Control Device

```yaml
# Turn on light
service: mqtt.publish
data:
  topic: zigbee2mqtt/living_room_bulb/set
  payload: '{"state": "ON"}'

# Set brightness
service: mqtt.publish
data:
  topic: zigbee2mqtt/living_room_bulb/set
  payload: '{"state": "ON", "brightness": 200}'

# Set color temperature
service: mqtt.publish
data:
  topic: zigbee2mqtt/living_room_bulb/set
  payload: '{"color_temp": 350}'

# Set RGB color
service: mqtt.publish
data:
  topic: zigbee2mqtt/living_room_bulb/set
  payload: '{"color": {"r": 255, "g": 100, "b": 50}}'
```

---

## Device Triggers

### Button Events

```yaml
automation:
  - id: ikea_button_single
    alias: "IKEA Button Single Press"
    trigger:
      - platform: device
        domain: mqtt
        device_id: abc123def456
        type: action
        subtype: "on"
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

### Via MQTT Topic

```yaml
automation:
  - id: aqara_button
    alias: "Aqara Button"
    trigger:
      - platform: mqtt
        topic: "zigbee2mqtt/aqara_button"
    condition:
      - condition: template
        value_template: "{{ trigger.payload_json.action is defined }}"
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.payload_json.action == 'single' }}"
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.living_room
          - conditions:
              - condition: template
                value_template: "{{ trigger.payload_json.action == 'double' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.living_room
                data:
                  brightness_pct: 100
```

### Common Button Actions

| Device | Actions |
|--------|---------|
| IKEA TRADFRI | on, off, brightness_up, brightness_down, arrow_left, arrow_right |
| Aqara Mini Switch | single, double, triple, quadruple, hold, release |
| Hue Dimmer | on_press, off_press, up_press, down_press, *_hold, *_release |
| IKEA STYRBAR | on, off, brightness_move_up, brightness_move_down, arrow_left_click |

### Button Blueprint

```yaml
automation:
  - id: z2m_button_handler
    alias: "Z2M Button Handler"
    trigger:
      - platform: mqtt
        topic: "zigbee2mqtt/+/action"
    variables:
      device_name: "{{ trigger.topic.split('/')[1] }}"
      action: "{{ trigger.payload }}"
    action:
      - service: logbook.log
        data:
          name: "Z2M Button"
          message: "{{ device_name }}: {{ action }}"
```

---

## Groups

### Create Group

```yaml
# Via MQTT
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/group/add
  payload: '{"friendly_name": "living_room_lights", "id": 1}'
```

### Add Device to Group

```yaml
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/group/members/add
  payload: '{"group": "living_room_lights", "device": "bulb_1"}'

# Add specific endpoint
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/group/members/add
  payload: '{"group": "living_room_lights", "device": "bulb_1", "endpoint": 1}'
```

### Z2M Configuration Groups

```yaml
# configuration.yaml (Z2M)
groups:
  '1':
    friendly_name: living_room_lights
    retain: true
    devices:
      - bulb_1
      - bulb_2
      - bulb_3
```

### Control Group

```yaml
# Control all lights in group
service: mqtt.publish
data:
  topic: zigbee2mqtt/living_room_lights/set
  payload: '{"state": "ON", "brightness": 200}'

# Via HA light entity
service: light.turn_on
target:
  entity_id: light.living_room_lights
data:
  brightness: 200
```

### Remove from Group

```yaml
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/group/members/remove
  payload: '{"group": "living_room_lights", "device": "bulb_1"}'
```

---

## Binding

Direct device-to-device control without going through the coordinator.

### Bind Devices

```yaml
# Bind button to light
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/bind
  payload: '{"from": "remote_1", "to": "bulb_1", "clusters": ["genOnOff", "genLevelCtrl"]}'

# Bind to group
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/bind
  payload: '{"from": "remote_1", "to": "living_room_lights", "clusters": ["genOnOff"]}'
```

### Common Clusters

| Cluster | Function |
|---------|----------|
| genOnOff | On/Off control |
| genLevelCtrl | Brightness control |
| lightingColorCtrl | Color control |
| genScenes | Scene control |

### Unbind

```yaml
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/unbind
  payload: '{"from": "remote_1", "to": "bulb_1"}'
```

### Check Bindings

```yaml
# Check bridge/devices topic for bind_cluster list
# Or Z2M frontend > Device > Bind tab
```

---

## Device Configuration

### Configure Device Options

```yaml
# Z2M configuration.yaml
devices:
  '0x00158d0001234567':
    friendly_name: living_room_motion
    retain: true
    qos: 1
    debounce: 1
    debounce_ignore:
      - action
    filtered_attributes:
      - temperature
    filtered_optimistic:
      - state
```

### Runtime Configuration

```yaml
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/configure
  payload: '{"id": "living_room_motion"}'
```

### Set Device Options

```yaml
# Set specific options
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/options
  payload: >
    {
      "id": "living_room_bulb",
      "options": {
        "transition": 2,
        "retain": true
      }
    }
```

### Common Options

| Option | Description |
|--------|-------------|
| `retain` | Retain MQTT messages |
| `qos` | MQTT QoS (0, 1, 2) |
| `debounce` | Debounce interval (seconds) |
| `transition` | Default transition time |
| `filtered_attributes` | Attributes to not publish |

---

## Availability

### Device Availability

```yaml
# Published to: zigbee2mqtt/[device]/availability
# Payload: "online" or "offline"

# Configure in Z2M
advanced:
  availability_timeout: 0  # Disable
  availability_blocklist: []
  availability_passlist: []
```

### Use in Automations

```yaml
automation:
  - id: device_offline_alert
    alias: "Device Offline Alert"
    trigger:
      - platform: mqtt
        topic: "zigbee2mqtt/+/availability"
        payload: "offline"
    action:
      - service: notify.mobile_app
        data:
          title: "Zigbee Device Offline"
          message: >
            {{ trigger.topic.split('/')[1] }} went offline
```

### Check Device Availability

```yaml
# In templates
{{ states('binary_sensor.living_room_motion_availability') }}

# Via MQTT
# zigbee2mqtt/living_room_motion/availability
```

---

## Common Devices

### IKEA TRADFRI Bulb

```yaml
# Control
service: mqtt.publish
data:
  topic: zigbee2mqtt/ikea_bulb/set
  payload: >
    {
      "state": "ON",
      "brightness": 254,
      "color_temp": 350,
      "transition": 2
    }
```

### Aqara Motion Sensor

```yaml
automation:
  - id: aqara_motion
    trigger:
      - platform: state
        entity_id: binary_sensor.aqara_motion_occupancy
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

### Aqara Door Sensor

```yaml
automation:
  - id: door_opened
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_contact
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Front door opened"
```

### Aqara Temperature/Humidity

```yaml
# Entities created:
# sensor.aqara_temp_temperature
# sensor.aqara_temp_humidity
# sensor.aqara_temp_pressure
# sensor.aqara_temp_battery

# Use in automation
automation:
  - id: temp_alert
    trigger:
      - platform: numeric_state
        entity_id: sensor.aqara_temp_temperature
        above: 28
    action:
      - service: notify.mobile_app
        data:
          message: "Temperature is {{ states('sensor.aqara_temp_temperature') }}°C"
```

### Sonoff SNZB Button

```yaml
automation:
  - id: sonoff_button
    trigger:
      - platform: mqtt
        topic: "zigbee2mqtt/sonoff_button"
    condition:
      - condition: template
        value_template: "{{ trigger.payload_json.action in ['single', 'double', 'long'] }}"
    action:
      - choose:
          - conditions: "{{ trigger.payload_json.action == 'single' }}"
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.lamp
```

### Tuya Smart Plug

```yaml
# Entities:
# switch.tuya_plug
# sensor.tuya_plug_power
# sensor.tuya_plug_voltage
# sensor.tuya_plug_current
# sensor.tuya_plug_energy

# Monitor power
automation:
  - id: high_power_alert
    trigger:
      - platform: numeric_state
        entity_id: sensor.tuya_plug_power
        above: 1000
    action:
      - service: notify.mobile_app
        data:
          message: "High power usage: {{ states('sensor.tuya_plug_power') }}W"
```

---

## Common Patterns

### Universal Button Handler

```yaml
automation:
  - id: z2m_button_universal
    alias: "Z2M Universal Button Handler"
    trigger:
      - platform: mqtt
        topic: "zigbee2mqtt/+/action"
    mode: queued
    variables:
      device: "{{ trigger.topic.split('/')[1] }}"
      action: "{{ trigger.payload }}"
    action:
      - choose:
          # Living room remote
          - conditions:
              - condition: template
                value_template: "{{ device == 'living_room_remote' }}"
            sequence:
              - choose:
                  - conditions: "{{ action == 'on' }}"
                    sequence:
                      - service: light.turn_on
                        target:
                          entity_id: light.living_room
                  - conditions: "{{ action == 'off' }}"
                    sequence:
                      - service: light.turn_off
                        target:
                          entity_id: light.living_room
```

### Battery Monitoring

```yaml
template:
  - sensor:
      - name: "Low Battery Devices"
        state: >
          {{ states.sensor
             | selectattr('entity_id', 'search', 'battery')
             | selectattr('state', 'is_number')
             | selectattr('state', 'lt', '20')
             | map(attribute='entity_id')
             | list | count }}
        attributes:
          devices: >
            {{ states.sensor
               | selectattr('entity_id', 'search', 'battery')
               | selectattr('state', 'is_number')
               | selectattr('state', 'lt', '20')
               | map(attribute='name')
               | list }}

automation:
  - id: battery_alert
    trigger:
      - platform: numeric_state
        entity_id: sensor.low_battery_devices
        above: 0
    action:
      - service: notify.mobile_app
        data:
          title: "Low Battery Alert"
          message: >
            Devices with low battery:
            {{ state_attr('sensor.low_battery_devices', 'devices') | join(', ') }}
```

### Link Quality Monitoring

```yaml
template:
  - sensor:
      - name: "Weak Zigbee Devices"
        state: >
          {{ states.sensor
             | selectattr('entity_id', 'search', 'linkquality')
             | selectattr('state', 'is_number')
             | selectattr('state', 'lt', '50')
             | list | count }}
```

---

## Best Practices

### Device Naming

```yaml
# Use consistent, descriptive names
devices:
  '0x00158d0001234567':
    friendly_name: living_room_motion_1  # room_type_number
  '0x00158d0001234568':
    friendly_name: kitchen_temp_sensor
  '0x00158d0001234569':
    friendly_name: bedroom_bulb_ceiling
```

### Network Stability

```yaml
# Z2M configuration
advanced:
  channel: 15  # Avoid WiFi interference (11, 15, 20, 25)
  transmit_power: 20
  network_key: GENERATE  # Use unique network key
```

### Router Placement

- Place mains-powered devices (bulbs, plugs) evenly
- Keep coordinator away from USB 3.0 ports
- Avoid placing near WiFi routers
- Battery devices connect to nearest router

### OTA Updates

```yaml
# Enable OTA in Z2M
ota:
  update_check_interval: 1440  # Check daily
  disable_automatic_update_check: false

# Trigger update
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/ota_update/update
  payload: '{"id": "bulb_1"}'
```

---

## Troubleshooting

### Device Not Pairing

| Issue | Solution |
|-------|----------|
| Not in pairing mode | Enable permit_join |
| Out of range | Move closer to coordinator |
| Already paired | Factory reset device |
| Wrong channel | Check device supports channel |

### Device Dropping

| Issue | Solution |
|-------|----------|
| Weak signal | Add routers between |
| Interference | Change Zigbee channel |
| Too many end devices | Add more routers |
| Power issues | Check coordinator power |

### Debug Logging

```yaml
# Z2M configuration.yaml
advanced:
  log_level: debug
  log_output:
    - console
    - file
```

### Network Map

```yaml
# Request network map
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/networkmap
  payload: '{"type": "raw", "routes": true}'

# View in Z2M frontend > Map tab
```

### Re-Interview Device

```yaml
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/interview
  payload: '{"id": "problematic_device"}'
```

### Remove Device

```yaml
# Remove from network
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/remove
  payload: '{"id": "device_name"}'

# Force remove (if device unresponsive)
service: mqtt.publish
data:
  topic: zigbee2mqtt/bridge/request/device/remove
  payload: '{"id": "device_name", "force": true}'
```

### Check Device State

```bash
# Subscribe to device topic
mosquitto_sub -h localhost -t "zigbee2mqtt/device_name/#" -v

# Check bridge devices
mosquitto_sub -h localhost -t "zigbee2mqtt/bridge/devices" | jq
```
