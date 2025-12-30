# Home Assistant Entity Customization Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Customize.yaml Structure](#customizeyaml-structure)
- [Entity Customization](#entity-customization)
- [Pattern Matching](#pattern-matching)
- [Common Customizations](#common-customizations)
- [UI Customization](#ui-customization)
- [Per-Domain Defaults](#per-domain-defaults)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Entity customization allows you to modify how entities appear and behave in Home Assistant without changing the underlying integration.

### Key Terms

| Term | Description |
|------|-------------|
| **Customize** | Modify entity attributes |
| **customize_glob** | Apply to entities matching pattern |
| **Friendly Name** | Display name in UI |
| **Device Class** | Semantic type (motion, door, etc.) |
| **Hidden** | Hide from default UI |

### What Can Be Customized

| Attribute | Description | Example |
|-----------|-------------|---------|
| `friendly_name` | Display name | "Living Room Light" |
| `icon` | MDI icon | mdi:ceiling-light |
| `entity_picture` | Custom image URL | /local/images/lamp.png |
| `device_class` | Entity type | motion, door, temperature |
| `unit_of_measurement` | Display unit | °C, kWh, % |
| `assumed_state` | Optimistic state | true/false |
| `hidden` | Hide in UI | true/false |

---

## Customize.yaml Structure

### Setup in Configuration

```yaml
# configuration.yaml
homeassistant:
  customize: !include customize.yaml
  customize_glob: !include customize_glob.yaml
```

### Basic Customize File

```yaml
# customize.yaml

# Single entity
light.living_room:
  friendly_name: Living Room Ceiling Light
  icon: mdi:ceiling-light

# Another entity
switch.coffee_maker:
  friendly_name: Coffee Machine
  icon: mdi:coffee
```

### Inline Configuration

```yaml
# configuration.yaml
homeassistant:
  customize:
    light.living_room:
      friendly_name: Living Room Light
      icon: mdi:ceiling-light
    sensor.temperature:
      friendly_name: Outside Temperature
```

---

## Entity Customization

### Friendly Name

```yaml
light.bedroom_1:
  friendly_name: Master Bedroom Light

sensor.temp_outside:
  friendly_name: Outdoor Temperature

binary_sensor.pir_1:
  friendly_name: Living Room Motion
```

### Icon

```yaml
# Using MDI icons (https://materialdesignicons.com)
light.desk_lamp:
  icon: mdi:desk-lamp

switch.pump:
  icon: mdi:water-pump

sensor.battery_phone:
  icon: mdi:cellphone-charging

cover.garage:
  icon: mdi:garage

climate.hvac:
  icon: mdi:hvac
```

### Entity Picture

```yaml
person.john:
  entity_picture: /local/images/john.jpg

media_player.tv:
  entity_picture: /local/icons/samsung_tv.png

camera.front_door:
  entity_picture: /local/camera_icons/front.png
```

### Device Class

```yaml
# Binary sensors
binary_sensor.front_door_sensor:
  device_class: door

binary_sensor.motion_living:
  device_class: motion

binary_sensor.water_leak:
  device_class: moisture

binary_sensor.smoke_sensor:
  device_class: smoke

# Sensors
sensor.temp_1:
  device_class: temperature

sensor.power_meter:
  device_class: power

sensor.battery_level:
  device_class: battery

# Covers
cover.blinds:
  device_class: blind

cover.garage:
  device_class: garage
```

### Unit of Measurement

```yaml
sensor.temperature:
  unit_of_measurement: "°C"

sensor.power:
  unit_of_measurement: "W"

sensor.humidity:
  unit_of_measurement: "%"

sensor.distance:
  unit_of_measurement: "km"
```

### Assumed State

```yaml
# For entities that don't report actual state
switch.ir_tv:
  assumed_state: true

light.rf_lamp:
  assumed_state: true
```

### Initial State

```yaml
# DEPRECATED in modern HA
# Use automation or initial option in entity config
input_boolean.vacation_mode:
  initial: false
```

### Hidden (Deprecated)

```yaml
# Use entity registry instead (UI > Entities > Hide)
# Legacy support
automation.internal_helper:
  hidden: true
```

---

## Pattern Matching

### Customize Glob

Apply customizations to multiple entities matching a pattern.

```yaml
# configuration.yaml
homeassistant:
  customize_glob: !include customize_glob.yaml
```

```yaml
# customize_glob.yaml

# All lights in living room
"light.living_room_*":
  icon: mdi:floor-lamp

# All motion sensors
"binary_sensor.*_motion":
  device_class: motion
  icon: mdi:motion-sensor

# All temperature sensors
"sensor.*_temperature":
  device_class: temperature
  unit_of_measurement: "°C"
  icon: mdi:thermometer

# All battery sensors
"sensor.*_battery":
  device_class: battery
  unit_of_measurement: "%"
  icon: mdi:battery

# All door sensors
"binary_sensor.*_door":
  device_class: door
  icon: mdi:door

# Zigbee devices
"*zigbee*":
  icon: mdi:zigbee
```

### Multiple Patterns

```yaml
# customize_glob.yaml

# Pattern 1: All motion binary sensors
"binary_sensor.*motion*":
  device_class: motion

# Pattern 2: All occupancy sensors
"binary_sensor.*occupancy*":
  device_class: occupancy

# Pattern 3: Power sensors
"sensor.*power*":
  device_class: power
  unit_of_measurement: "W"

# Pattern 4: Energy sensors
"sensor.*energy*":
  device_class: energy
  unit_of_measurement: "kWh"
```

### Glob Patterns

| Pattern | Matches |
|---------|---------|
| `*` | Any characters |
| `?` | Single character |
| `[abc]` | Character in set |
| `[!abc]` | Character not in set |

```yaml
# Examples
"light.*":              # All lights
"sensor.temp_?":        # temp_1, temp_2, etc.
"binary_sensor.[fm]*":  # Starts with f or m
"*_living_room":        # Ends with _living_room
```

---

## Common Customizations

### Lights

```yaml
light.ceiling_living:
  friendly_name: Living Room Ceiling
  icon: mdi:ceiling-light

light.lamp_bedroom:
  friendly_name: Bedside Lamp
  icon: mdi:lamp

light.led_strip:
  friendly_name: LED Strip
  icon: mdi:led-strip-variant
```

### Switches

```yaml
switch.coffee:
  friendly_name: Coffee Machine
  icon: mdi:coffee

switch.heater:
  friendly_name: Space Heater
  icon: mdi:radiator

switch.pump:
  friendly_name: Water Pump
  icon: mdi:water-pump
```

### Binary Sensors

```yaml
binary_sensor.front_door:
  friendly_name: Front Door
  device_class: door
  icon: mdi:door

binary_sensor.motion_hall:
  friendly_name: Hallway Motion
  device_class: motion
  icon: mdi:motion-sensor

binary_sensor.water_kitchen:
  friendly_name: Kitchen Water Leak
  device_class: moisture
  icon: mdi:water-alert

binary_sensor.window_bedroom:
  friendly_name: Bedroom Window
  device_class: window
  icon: mdi:window-closed
```

### Sensors

```yaml
sensor.outdoor_temp:
  friendly_name: Outdoor Temperature
  device_class: temperature
  icon: mdi:thermometer

sensor.power_total:
  friendly_name: Total Power Usage
  device_class: power
  unit_of_measurement: "W"
  icon: mdi:flash

sensor.battery_remote:
  friendly_name: Remote Battery
  device_class: battery
  unit_of_measurement: "%"
  icon: mdi:battery
```

### Climate

```yaml
climate.living_room:
  friendly_name: Living Room Thermostat
  icon: mdi:thermostat

climate.bedroom:
  friendly_name: Bedroom AC
  icon: mdi:air-conditioner
```

### Covers

```yaml
cover.garage:
  friendly_name: Garage Door
  device_class: garage
  icon: mdi:garage

cover.blinds_living:
  friendly_name: Living Room Blinds
  device_class: blind
  icon: mdi:blinds
```

### Persons

```yaml
person.john:
  friendly_name: John
  entity_picture: /local/images/john.jpg

person.jane:
  friendly_name: Jane
  entity_picture: /local/images/jane.jpg
```

---

## UI Customization

### Via Settings UI

1. Go to Settings > Entities
2. Find and select entity
3. Click gear icon
4. Edit Name, Icon, Area
5. Save

### Entity Registry

Modern HA uses entity registry for customizations:
- Friendly name
- Icon
- Area
- Hide entity
- Disable entity

```yaml
# Most customizations now managed via UI
# customize.yaml is mainly for:
# - device_class
# - unit_of_measurement
# - assumed_state
# - Pattern-based customizations (customize_glob)
```

### Dashboard Customization

```yaml
# Lovelace entity customization
type: entities
entities:
  - entity: light.living_room
    name: Custom Name  # Override in dashboard only
    icon: mdi:lamp
```

---

## Per-Domain Defaults

Set defaults for all entities in a domain.

```yaml
# customize_glob.yaml

# All binary sensors default to motion
"binary_sensor.*":
  device_class: motion

# All sensors show thermometer icon
"sensor.*":
  icon: mdi:thermometer

# All lights use lightbulb icon
"light.*":
  icon: mdi:lightbulb
```

### Override Specific Entities

```yaml
# customize_glob.yaml sets defaults
"binary_sensor.*":
  device_class: motion

# customize.yaml overrides specific entities
binary_sensor.front_door:
  device_class: door

binary_sensor.window_bedroom:
  device_class: window
```

---

## Common Patterns

### Naming Convention Setup

```yaml
# Apply friendly names based on pattern

# Room prefix pattern
"*_living_room":
  friendly_name_suffix: " (Living Room)"

# Can't dynamically change friendly_name
# Use template sensors or manual customization
```

### Multi-Room Sensors

```yaml
# customize.yaml

# Temperature sensors by room
sensor.temp_living_room:
  friendly_name: Living Room Temperature
  icon: mdi:thermometer

sensor.temp_bedroom:
  friendly_name: Bedroom Temperature
  icon: mdi:thermometer

sensor.temp_kitchen:
  friendly_name: Kitchen Temperature
  icon: mdi:thermometer

# Humidity sensors
sensor.humidity_living_room:
  friendly_name: Living Room Humidity
  icon: mdi:water-percent

sensor.humidity_bedroom:
  friendly_name: Bedroom Humidity
  icon: mdi:water-percent
```

### Device Integration

```yaml
# customize_glob.yaml

# Zigbee2MQTT devices
"*.0x*":
  icon: mdi:zigbee

# ESPHome devices
"*esphome*":
  icon: mdi:chip

# Tasmota devices
"*tasmota*":
  icon: mdi:memory
```

### Battery Monitoring

```yaml
# customize_glob.yaml
"sensor.*_battery":
  device_class: battery
  unit_of_measurement: "%"

"sensor.*_battery_level":
  device_class: battery
  unit_of_measurement: "%"

"sensor.battery_*":
  device_class: battery
  unit_of_measurement: "%"
```

---

## Best Practices

### Organize by Type

```yaml
# customize.yaml organized by domain

# === LIGHTS ===
light.living_room:
  friendly_name: Living Room Light

light.bedroom:
  friendly_name: Bedroom Light

# === SWITCHES ===
switch.coffee:
  friendly_name: Coffee Machine

# === SENSORS ===
sensor.temperature:
  friendly_name: Temperature
```

### Use Glob for Patterns

```yaml
# Good: Use glob for consistent patterns
"binary_sensor.*_motion":
  device_class: motion

# Avoid: Repeating same customization
binary_sensor.living_motion:
  device_class: motion
binary_sensor.bedroom_motion:
  device_class: motion
binary_sensor.kitchen_motion:
  device_class: motion
```

### Keep Device Class Accurate

```yaml
# Correct device classes enable proper icons and behavior
binary_sensor.door:
  device_class: door     # Shows open/closed correctly

sensor.temperature:
  device_class: temperature  # Enables statistics
  unit_of_measurement: "°C"
```

### Prefer UI for Simple Changes

```yaml
# Use customize.yaml for:
# - device_class changes
# - Pattern-based customizations
# - Integration-specific fixes

# Use UI for:
# - Friendly names
# - Icons
# - Areas
# - Hiding entities
```

---

## Troubleshooting

### Customization Not Applied

| Problem | Cause | Solution |
|---------|-------|----------|
| No change | Typo in entity_id | Check exact entity ID |
| Override not working | Order of processing | Put specific after glob |
| Device class ignored | Integration override | May need integration config |

### Check Entity ID

```yaml
# Developer Tools > States
# Find exact entity_id

# Common mistakes
light.living_room  # Correct
Light.Living_Room  # Wrong - case sensitive
light.living room  # Wrong - no spaces
```

### Debug Customization

```yaml
# Enable debug logging
logger:
  default: info
  logs:
    homeassistant.components.homeassistant: debug
```

### Reload Customizations

```yaml
# Developer Tools > YAML > Reload Core Config

# Or service call
service: homeassistant.reload_core_config
```

### Priority Order

```yaml
# Customization priority (lowest to highest):
# 1. customize_glob patterns (first match wins)
# 2. customize.yaml specific entities
# 3. Entity registry (UI settings)
# 4. Dashboard overrides

# Example:
"sensor.*":            # Priority 1
  icon: mdi:flash

sensor.temperature:    # Priority 2 - overrides glob
  icon: mdi:thermometer

# UI settings override both
```

### Common Mistakes

```yaml
# Wrong: Using domain without entity
light:
  icon: mdi:lightbulb

# Correct: Full entity_id
light.living_room:
  icon: mdi:lightbulb

# Wrong: Glob without quotes
binary_sensor.*_motion:
  device_class: motion

# Correct: Glob in quotes
"binary_sensor.*_motion":
  device_class: motion

# Wrong: Invalid device_class
binary_sensor.test:
  device_class: sensor  # Not valid for binary_sensor

# Correct: Valid device_class
binary_sensor.test:
  device_class: motion  # Valid for binary_sensor
```

### Valid Device Classes

```yaml
# Binary Sensor device classes:
# battery, battery_charging, cold, connectivity, door,
# garage_door, gas, heat, light, lock, moisture, motion,
# moving, occupancy, opening, plug, power, presence,
# problem, running, safety, smoke, sound, tamper,
# update, vibration, window

# Sensor device classes:
# apparent_power, aqi, battery, carbon_dioxide,
# carbon_monoxide, current, date, duration, energy,
# frequency, gas, humidity, illuminance, monetary,
# nitrogen_dioxide, nitrogen_monoxide, nitrous_oxide,
# ozone, pm1, pm10, pm25, power, power_factor,
# pressure, reactive_power, signal_strength,
# sulphur_dioxide, temperature, timestamp,
# volatile_organic_compounds, voltage
```
