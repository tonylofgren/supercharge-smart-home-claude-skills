# ZHA (Zigbee Home Automation) Integration

Complete guide for the native Zigbee Home Automation integration in Home Assistant.

---

## Overview

ZHA (Zigbee Home Automation) is Home Assistant's **native Zigbee integration** - no external software required. It runs entirely within Home Assistant, providing direct control over Zigbee devices.

### ZHA vs Zigbee2MQTT Comparison

| Feature | ZHA | Zigbee2MQTT |
|---------|-----|-------------|
| **Setup** | Native, built-in | Requires separate addon |
| **Device Support** | 2,700+ devices | 3,500+ devices |
| **UI Integration** | Deep HA integration | Via MQTT |
| **Configuration** | UI-based | YAML + UI |
| **Updates** | With HA Core | Independent |
| **Resource Usage** | Lower | Higher (separate process) |
| **Quirks/Fixes** | Community quirks | External converters |
| **Best For** | Simplicity, HA-native | Power users, more devices |

**Choose ZHA if:** You want simplicity, native HA integration, and your devices are supported.

**Choose Z2M if:** You need maximum device support or prefer YAML configuration.

---

## Hardware Setup

### Supported Coordinators

| Coordinator | Chip | Recommended |
|-------------|------|-------------|
| **Home Assistant SkyConnect** | EFR32MG21 | Yes - Official |
| **Home Assistant Yellow** | EFR32MG21 | Yes - Built-in |
| **Sonoff ZBDongle-E** | EFR32MG21 | Yes |
| **Sonoff ZBDongle-P** | CC2652P | Yes |
| **ConBee II** | deCONZ | Yes |
| **ConBee III** | deCONZ | Yes |
| **SLZB-06** | CC2652P | Yes |
| **Tube's Zigbee Coordinator** | CC2652 | Yes |
| **ITead CC2531** | CC2531 | No - Limited |

### Initial Setup

```yaml
# Auto-discovered in most cases
# Manual configuration in configuration.yaml (rarely needed):
zha:
  database_path: /config/zigbee.db
```

### USB Device Path

```yaml
# Common paths
/dev/ttyUSB0          # Generic USB
/dev/ttyACM0          # CDC ACM devices
/dev/serial/by-id/... # Persistent path (recommended)
```

### Firmware Updates

For SkyConnect and Sonoff dongles:
1. Go to **Settings > System > Hardware**
2. Click the three-dot menu on your adapter
3. Select **Update Firmware** if available

For ConBee:
1. Use the deCONZ application
2. Follow Phoscon firmware update guide

---

## Device Pairing

### Basic Pairing Process

1. **Enable Pairing Mode**
   - Go to **Settings > Devices & Services > ZHA**
   - Click **Add Device**
   - ZHA enters pairing mode for 60 seconds

2. **Put Device in Pairing Mode**
   - New devices: Usually automatic when powered on
   - Existing devices: Factory reset (varies by manufacturer)

3. **Interview Process**
   - ZHA queries device capabilities
   - Assigns endpoints and clusters
   - Creates entities automatically

### Common Pairing Methods by Manufacturer

```yaml
# Aqara/Xiaomi
# Hold button 5+ seconds until LED blinks

# IKEA Tradfri
# Press pairing button 4 times quickly

# Hue (bulbs)
# Power cycle 5 times (on for 8s, off for 2s)

# Sonoff
# Hold button 5 seconds

# Tuya
# Hold button 10+ seconds or power cycle 3x
```

### Troubleshooting Failed Pairing

1. **Device Too Far from Coordinator**
   - Move closer or pair near router device
   - Add Zigbee routers for mesh coverage

2. **Device Already Paired**
   - Factory reset the device first
   - Check if it's in another Zigbee network

3. **Interview Incomplete**
   - Reconfigure device in ZHA
   - Check device quirks needed

4. **Interference**
   - Keep USB coordinator away from USB 3.0 ports
   - Use USB extension cable
   - Change Zigbee channel

### Change Zigbee Channel

```yaml
# In ZHA integration settings
# Recommended channels: 11, 15, 20, 25
# Avoid WiFi channel overlap
```

---

## Device Management

### Device Information

Navigate to **Settings > Devices & Services > ZHA > [Device]**

- **Device Info**: Model, manufacturer, firmware
- **Entities**: All exposed entities
- **Clusters**: Raw Zigbee cluster access
- **Signature**: Device identification data

### Reconfigure Device

If a device isn't working correctly:
1. Click device in ZHA
2. Select **Reconfigure Device**
3. ZHA re-interviews the device

### Remove Device

1. Click device in ZHA
2. Select **Remove Device**
3. Choose **Force Remove** if device is offline

---

## Groups & Scenes

### ZHA Groups vs HA Groups

| Type | ZHA Group | HA Group |
|------|-----------|----------|
| **Communication** | Direct Zigbee | Via HA |
| **Speed** | Instant (1 command) | Sequential |
| **State Sync** | Native | Polling |
| **Best For** | Same room lights | Mixed devices |

### Creating ZHA Groups

1. Go to **Settings > Devices & Services > ZHA**
2. Click **Groups**
3. Click **Create Group**
4. Select devices to include
5. Name the group

### Light Groups Example

```yaml
# ZHA creates a light entity for the group
# light.living_room_lights

# Automations work like single light:
service: light.turn_on
target:
  entity_id: light.living_room_lights
data:
  brightness_pct: 75
  transition: 2
```

### Scene Creation

Scenes in ZHA are stored on the coordinator:

1. Set up your lights to desired state
2. In ZHA, create a scene
3. Recall scene via automation:

```yaml
automation:
  - alias: "Evening Scene"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: zha.recall_scene
        data:
          scene_id: 1
          group_id: 1
```

---

## Bindings

Bindings create **direct device-to-device communication** without Home Assistant.

### Benefits of Bindings

- **Instant response** - No HA latency
- **Works offline** - HA can be down
- **Battery efficient** - Direct communication

### Common Binding Scenarios

1. **Switch → Light**: Physical switch controls bulb directly
2. **Remote → Group**: Remote controls multiple lights
3. **Motion Sensor → Light**: Motion triggers light

### Creating Bindings

1. Go to device page in ZHA
2. Click **Manage Clusters**
3. Select cluster to bind (e.g., `OnOff`)
4. Click **Bind** and select target device/group

### Binding Example: IKEA Remote to Light Group

```yaml
# 1. Create ZHA group with lights
# 2. Go to IKEA Remote in ZHA
# 3. Clusters > OnOff > Bind to group
# 4. Clusters > LevelControl > Bind to group

# Remote now controls lights directly!
```

### Unbinding

Follow same process, click **Unbind** instead.

---

## Automations

### Device Triggers

ZHA exposes device-specific triggers:

```yaml
automation:
  - alias: "Button Press Action"
    trigger:
      - platform: device
        domain: zha
        device_id: abc123...
        type: remote_button_short_press
        subtype: button_1
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

### Common Trigger Types

| Trigger | Description |
|---------|-------------|
| `remote_button_short_press` | Quick button press |
| `remote_button_long_press` | Hold button |
| `remote_button_double_press` | Double-click |
| `remote_button_short_release` | Release after short |
| `remote_button_long_release` | Release after hold |

### ZHA Events

For advanced scenarios, listen to ZHA events:

```yaml
automation:
  - alias: "ZHA Event Handler"
    trigger:
      - platform: event
        event_type: zha_event
        event_data:
          device_ieee: "00:11:22:33:44:55:66:77"
          command: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.kitchen
```

### Event Data Structure

```yaml
event_type: zha_event
data:
  device_ieee: "00:11:22:33:44:55:66:77"
  unique_id: "00:11:22:33:44:55:66:77:1:0x0006"
  device_id: "abc123def456"
  endpoint_id: 1
  cluster_id: 6
  command: "on"
  args: []
```

### Button Remote Example (Complete)

```yaml
automation:
  - alias: "IKEA Remote - All Actions"
    mode: single
    trigger:
      - platform: device
        domain: zha
        device_id: abc123...
        type: remote_button_short_press
        subtype: turn_on
        id: "on"
      - platform: device
        domain: zha
        device_id: abc123...
        type: remote_button_short_press
        subtype: turn_off
        id: "off"
      - platform: device
        domain: zha
        device_id: abc123...
        type: remote_button_short_press
        subtype: dim_up
        id: "bright"
      - platform: device
        domain: zha
        device_id: abc123...
        type: remote_button_short_press
        subtype: dim_down
        id: "dim"
    action:
      - choose:
          - conditions:
              - condition: trigger
                id: "on"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.living_room
                data:
                  brightness_pct: 100
          - conditions:
              - condition: trigger
                id: "off"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: light.living_room
          - conditions:
              - condition: trigger
                id: "bright"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.living_room
                data:
                  brightness_step_pct: 20
          - conditions:
              - condition: trigger
                id: "dim"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.living_room
                data:
                  brightness_step_pct: -20
```

---

## Services

### ZHA-Specific Services

```yaml
# Issue Zigbee cluster command
service: zha.issue_zigbee_cluster_command
data:
  ieee: "00:11:22:33:44:55:66:77"
  endpoint_id: 1
  cluster_id: 6
  cluster_type: in
  command: 0
  command_type: server

# Set attribute
service: zha.set_zigbee_cluster_attribute
data:
  ieee: "00:11:22:33:44:55:66:77"
  endpoint_id: 1
  cluster_id: 8
  cluster_type: in
  attribute: 16
  value: 1

# Permit joining
service: zha.permit
data:
  duration: 60
  ieee: "00:11:22:33:44:55:66:77"  # Optional: specific router

# Remove device
service: zha.remove
data:
  ieee: "00:11:22:33:44:55:66:77"
```

---

## Advanced Configuration

### Device Quirks

Quirks fix device-specific issues. ZHA includes many built-in.

**Check if quirk is applied:**
1. Go to device in ZHA
2. Look at **Signature** tab
3. **Quirk** field shows applied quirk

**Custom Quirks (Advanced):**

```python
# custom_components/zha_quirks/my_device.py
from zigpy.quirks import CustomDevice
from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

class MyCustomDevice(CustomDevice):
    signature = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: 0x0104,
                DEVICE_TYPE: 0x0100,
                INPUT_CLUSTERS: [0, 3, 4, 5, 6, 8],
                OUTPUT_CLUSTERS: [25],
            }
        }
    }

    replacement = {
        ENDPOINTS: {
            1: {
                # Modified endpoint definition
            }
        }
    }
```

### Network Optimization

**USB Extension Cable:**
- Always use 1-2m USB extension
- Keeps coordinator away from interference

**Channel Selection:**
- Avoid WiFi overlap
- Check with WiFi Analyzer app
- Channels 15, 20, 25 usually best

**Router Placement:**
- Add mains-powered devices as routers
- Position routers between coordinator and end devices
- Avoid routing through walls with metal/concrete

### Reporting Configuration

Adjust how often devices report:

```yaml
# Via Clusters > Reporting Configuration
# Set min/max report intervals
# Battery devices: longer intervals save battery
```

---

## Migration

### From Zigbee2MQTT to ZHA

1. **Backup Z2M configuration**
2. **Stop Z2M addon**
3. **Factory reset all devices** (required!)
4. **Set up ZHA**
5. **Pair devices one by one**
6. **Update automations** (entity IDs change)

Note: No migration tool exists - devices must be re-paired.

### From ZHA to Zigbee2MQTT

Same process in reverse:
1. Remove devices from ZHA
2. Stop ZHA integration
3. Set up Z2M
4. Pair devices to Z2M

### Backup ZHA Database

```yaml
# ZHA database location
/config/zigbee.db

# Backup before major changes
# Can restore if needed (same coordinator required)
```

---

## Troubleshooting

### Device Not Responding

1. **Check device status** in ZHA
2. **Check last_seen** attribute
3. **Try reconfigure** device
4. **Check mesh routing** - add routers if needed

### Devices Going Unavailable

```yaml
# Common causes:
# - Weak mesh network (add routers)
# - Coordinator too far
# - Interference (USB 3.0, WiFi)
# - Battery depleted

# Solutions:
# - Add mains-powered Zigbee devices as routers
# - Use USB extension cable
# - Change Zigbee channel
```

### Slow Response

```yaml
# Possible issues:
# - Too many hops in mesh
# - Overloaded router
# - Polling entities

# Solutions:
# - Add routers for better paths
# - Use bindings for instant response
# - Reduce report intervals
```

### Debug Logging

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    zigpy: debug
    bellows: debug
    zhaquirks: debug
    homeassistant.components.zha: debug
```

### Network Visualization

1. Go to **Settings > Devices & Services > ZHA**
2. Click **Visualize Zigbee Network**
3. See device connections and LQI values

---

## Best Practices

### Network Design

```yaml
# Good mesh network:
# - Coordinator in central location
# - Routers (mains-powered) every 10-15m
# - No more than 3-4 hops to any device
# - Avoid single points of failure
```

### Device Limits

| Coordinator | Direct Children | Total Network |
|-------------|-----------------|---------------|
| CC2531 | 20 | ~100 |
| CC2652 | 50 | ~200 |
| EFR32 | 50 | ~200 |

### Battery Life

```yaml
# Extend battery device life:
# - Use bindings instead of polling
# - Increase report intervals
# - Keep firmware updated
# - Use quality batteries
```

### Entity Naming

```yaml
# ZHA creates entities with device names
# Rename in HA for clarity:
# - light.0x123456_light → light.kitchen_ceiling
# - sensor.0x789abc_temperature → sensor.bedroom_temp
```

---

## Common Device Examples

### Aqara Motion Sensor

```yaml
# Entities created:
# - binary_sensor.motion_sensor_motion
# - sensor.motion_sensor_illuminance
# - sensor.motion_sensor_battery

automation:
  - alias: "Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.aqara_motion_occupancy
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

### Aqara Temperature Sensor

```yaml
# Entities created:
# - sensor.temp_sensor_temperature
# - sensor.temp_sensor_humidity
# - sensor.temp_sensor_pressure
# - sensor.temp_sensor_battery

automation:
  - alias: "Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aqara_temp_temperature
        above: 30
    action:
      - service: notify.mobile_app
        data:
          message: "Temperature is {{ states('sensor.aqara_temp_temperature') }}C"
```

### IKEA Tradfri Remote

```yaml
# Uses device triggers (see Automations section)
# Or ZHA events for full control

# Event data example:
# command: "on", "off", "move_with_on_off", "stop"
# args: [direction, speed] for dimming
```

### Smart Plug with Power Monitoring

```yaml
# Entities created:
# - switch.smart_plug
# - sensor.smart_plug_power
# - sensor.smart_plug_energy

# Use for appliance monitoring:
automation:
  - alias: "Washing Machine Done"
    trigger:
      - platform: numeric_state
        entity_id: sensor.washer_plug_power
        below: 5
        for: "00:02:00"
    condition:
      - condition: state
        entity_id: input_boolean.washer_running
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Washing machine finished!"
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.washer_running
```

---

## Reference

### Useful Links

- [ZHA Documentation](https://www.home-assistant.io/integrations/zha/)
- [Supported Devices](https://zigbee.blakadder.com/)
- [ZHA Device Handlers (Quirks)](https://github.com/zigpy/zha-device-handlers)
- [Zigbee Alliance](https://csa-iot.org/all-solutions/zigbee/)

### Cluster Reference

| Cluster | ID | Description |
|---------|-------|-------------|
| Basic | 0x0000 | Device info |
| Power Config | 0x0001 | Battery |
| On/Off | 0x0006 | Switch |
| Level Control | 0x0008 | Dimming |
| Color Control | 0x0300 | Color/temp |
| Temperature | 0x0402 | Temperature |
| Humidity | 0x0405 | Humidity |
| Occupancy | 0x0406 | Motion |
| IAS Zone | 0x0500 | Security |
| Electrical | 0x0B04 | Power |
