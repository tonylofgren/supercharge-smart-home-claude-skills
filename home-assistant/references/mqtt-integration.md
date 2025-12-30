# MQTT Integration Patterns - Complete Reference

Patterns for integrating MQTT devices with Home Assistant.

## MQTT Discovery Format

Home Assistant uses a specific format for auto-discovering MQTT devices.

### Discovery Topic Structure

```
<discovery_prefix>/<component>/<node_id>/<object_id>/config
```

Example: `homeassistant/switch/bedroom/light/config`

### Common Components

| Component | Description |
|-----------|-------------|
| `switch` | On/off switch |
| `light` | Light (with optional brightness, color) |
| `binary_sensor` | Binary sensor (on/off) |
| `sensor` | Sensor with value |
| `climate` | HVAC/thermostat |
| `cover` | Blinds, garage door |
| `fan` | Fan control |
| `lock` | Door lock |
| `vacuum` | Robot vacuum |

---

## Switch Discovery

```json
{
  "name": "Bedroom Light",
  "unique_id": "bedroom_light_001",
  "command_topic": "home/bedroom/light/set",
  "state_topic": "home/bedroom/light/state",
  "payload_on": "ON",
  "payload_off": "OFF",
  "state_on": "ON",
  "state_off": "OFF",
  "optimistic": false,
  "qos": 1,
  "retain": true,
  "device": {
    "identifiers": ["bedroom_light_001"],
    "name": "Bedroom Light",
    "model": "Smart Switch",
    "manufacturer": "DIY"
  }
}
```

---

## Light Discovery

### Basic On/Off Light

```json
{
  "name": "Kitchen Light",
  "unique_id": "kitchen_light_001",
  "command_topic": "home/kitchen/light/set",
  "state_topic": "home/kitchen/light/state",
  "schema": "json",
  "brightness": false
}
```

### Dimmable Light

```json
{
  "name": "Living Room Light",
  "unique_id": "living_light_001",
  "command_topic": "home/living/light/set",
  "state_topic": "home/living/light/state",
  "schema": "json",
  "brightness": true,
  "brightness_scale": 100,
  "effect": true,
  "effect_list": ["none", "colorloop", "random"]
}
```

### RGB Light

```json
{
  "name": "RGB Strip",
  "unique_id": "rgb_strip_001",
  "command_topic": "home/rgb/light/set",
  "state_topic": "home/rgb/light/state",
  "schema": "json",
  "brightness": true,
  "color_mode": true,
  "supported_color_modes": ["rgb", "color_temp"],
  "min_mireds": 153,
  "max_mireds": 500
}
```

### JSON Schema State Message

```json
{
  "state": "ON",
  "brightness": 255,
  "color_mode": "rgb",
  "color": {
    "r": 255,
    "g": 100,
    "b": 50
  },
  "effect": "none"
}
```

---

## Binary Sensor Discovery

```json
{
  "name": "Front Door",
  "unique_id": "front_door_001",
  "state_topic": "home/front_door/state",
  "payload_on": "open",
  "payload_off": "closed",
  "device_class": "door",
  "expire_after": 600
}
```

### Device Classes for Binary Sensors

| Class | ON Meaning | OFF Meaning |
|-------|------------|-------------|
| `door` | Open | Closed |
| `window` | Open | Closed |
| `motion` | Detected | Clear |
| `moisture` | Wet | Dry |
| `smoke` | Detected | Clear |
| `battery` | Low | Normal |
| `occupancy` | Occupied | Clear |

---

## Sensor Discovery

```json
{
  "name": "Temperature",
  "unique_id": "temp_sensor_001",
  "state_topic": "home/bedroom/temperature",
  "unit_of_measurement": "°C",
  "device_class": "temperature",
  "state_class": "measurement",
  "value_template": "{{ value_json.temperature }}",
  "expire_after": 600
}
```

### Device Classes for Sensors

| Class | Unit |
|-------|------|
| `temperature` | °C, °F |
| `humidity` | % |
| `pressure` | hPa, mbar |
| `power` | W, kW |
| `energy` | Wh, kWh |
| `voltage` | V |
| `current` | A |
| `illuminance` | lx |
| `battery` | % |

### State Classes

| Class | Description |
|-------|-------------|
| `measurement` | Current value (temperature) |
| `total` | Cumulative total (energy) |
| `total_increasing` | Only increases (rain gauge) |

---

## Climate Discovery

```json
{
  "name": "Living Room Thermostat",
  "unique_id": "living_thermostat_001",
  "mode_command_topic": "home/living/hvac/mode/set",
  "mode_state_topic": "home/living/hvac/mode/state",
  "modes": ["off", "heat", "cool", "auto"],
  "temperature_command_topic": "home/living/hvac/temp/set",
  "temperature_state_topic": "home/living/hvac/temp/state",
  "current_temperature_topic": "home/living/hvac/current_temp",
  "min_temp": 15,
  "max_temp": 30,
  "temp_step": 0.5,
  "temperature_unit": "C"
}
```

---

## Cover Discovery

```json
{
  "name": "Garage Door",
  "unique_id": "garage_door_001",
  "command_topic": "home/garage/door/set",
  "state_topic": "home/garage/door/state",
  "payload_open": "OPEN",
  "payload_close": "CLOSE",
  "payload_stop": "STOP",
  "state_open": "open",
  "state_closed": "closed",
  "device_class": "garage",
  "position_topic": "home/garage/door/position",
  "set_position_topic": "home/garage/door/position/set"
}
```

---

## Tasmota Integration

### Standard Tasmota Topics

```
stat/<topic>/RESULT    # Command results
stat/<topic>/POWER     # Power state
tele/<topic>/STATE     # Telemetry state
tele/<topic>/SENSOR    # Sensor readings
cmnd/<topic>/POWER     # Power commands
```

### Tasmota Discovery

Tasmota supports native Home Assistant discovery. Enable with:

```
SetOption19 0  # Use native HA discovery
```

### Manual Tasmota YAML

```yaml
mqtt:
  switch:
    - name: "Tasmota Switch"
      state_topic: "stat/tasmota_device/POWER"
      command_topic: "cmnd/tasmota_device/POWER"
      payload_on: "ON"
      payload_off: "OFF"
      availability_topic: "tele/tasmota_device/LWT"
      payload_available: "Online"
      payload_not_available: "Offline"

  sensor:
    - name: "Tasmota Power"
      state_topic: "tele/tasmota_device/SENSOR"
      value_template: "{{ value_json.ENERGY.Power }}"
      unit_of_measurement: "W"
```

---

## Shelly MQTT

### Shelly Gen1 Topics

```
shellies/<id>/relay/0          # Relay state
shellies/<id>/relay/0/command  # Relay command (on/off)
shellies/<id>/relay/0/power    # Power consumption
shellies/<id>/relay/0/energy   # Energy counter
shellies/<id>/input/0          # Input state
shellies/<id>/temperature      # Device temperature
```

### Shelly Gen2 Topics (RPC)

```
<id>/events/rpc                # RPC events
<id>/status/switch:0           # Switch status
<id>/command/switch:0          # Switch command
```

### Shelly Discovery Config

```json
{
  "name": "Shelly Plug",
  "unique_id": "shelly_plug_001",
  "command_topic": "shellies/shelly1-ABC123/relay/0/command",
  "state_topic": "shellies/shelly1-ABC123/relay/0",
  "payload_on": "on",
  "payload_off": "off",
  "availability_topic": "shellies/shelly1-ABC123/online",
  "payload_available": "true",
  "payload_not_available": "false"
}
```

---

## QoS Levels

| QoS | Description | Use Case |
|-----|-------------|----------|
| 0 | At most once | Sensor telemetry |
| 1 | At least once | Commands, state changes |
| 2 | Exactly once | Critical operations |

---

## Retain Flag

| Setting | Description |
|---------|-------------|
| `true` | Broker stores last message |
| `false` | Message not stored |

**Use retain for:**
- State topics (so HA gets state on startup)
- Availability topics

**Don't use retain for:**
- Command topics
- Sensor readings

---

## Availability

```json
{
  "availability": [
    {
      "topic": "home/device/status",
      "payload_available": "online",
      "payload_not_available": "offline"
    }
  ],
  "availability_mode": "all"  // or "any", "latest"
}
```

---

## Value Templates

### JSON Parsing

```yaml
value_template: "{{ value_json.temperature }}"
value_template: "{{ value_json['sensor']['temp'] }}"
```

### Conditional

```yaml
value_template: >
  {% if value_json.status == 1 %}
    ON
  {% else %}
    OFF
  {% endif %}
```

### Math Operations

```yaml
value_template: "{{ (value | float * 0.001) | round(2) }}"
```

---

## Device Grouping

All entities from same device should share device info:

```json
{
  "device": {
    "identifiers": ["device_unique_id"],
    "name": "Device Name",
    "model": "Model Name",
    "manufacturer": "Manufacturer",
    "sw_version": "1.0.0",
    "hw_version": "rev1",
    "configuration_url": "http://192.168.1.100"
  }
}
```

---

## Example: Complete Device Setup

### Publisher Side (Device)

```python
# Publish discovery
discovery_topic = "homeassistant/switch/my_device/config"
discovery_payload = {
    "name": "My Switch",
    "unique_id": "my_device_switch",
    "command_topic": "my_device/switch/set",
    "state_topic": "my_device/switch/state",
    "availability_topic": "my_device/status",
    "device": {
        "identifiers": ["my_device"],
        "name": "My Device"
    }
}
client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)

# Publish availability
client.publish("my_device/status", "online", retain=True)

# Subscribe to commands
client.subscribe("my_device/switch/set")

# Publish state changes
client.publish("my_device/switch/state", "ON", retain=True)
```

### Home Assistant Side

Once discovery message is published, entity appears automatically.

Manual override in `configuration.yaml`:

```yaml
mqtt:
  switch:
    - name: "My Switch"
      unique_id: "my_device_switch"
      command_topic: "my_device/switch/set"
      state_topic: "my_device/switch/state"
```
