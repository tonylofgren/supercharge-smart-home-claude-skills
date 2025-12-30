# Home Assistant Blueprints Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Blueprint Structure](#blueprint-structure)
- [Input Types](#input-types)
- [Selector Reference](#selector-reference)
- [Using Inputs](#using-inputs)
- [Blueprint Variables](#blueprint-variables)
- [Default Values](#default-values)
- [Publishing Blueprints](#publishing-blueprints)
- [Importing Blueprints](#importing-blueprints)
- [Complete Examples](#complete-examples)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Blueprints are reusable automation templates that users can configure through the UI. They define inputs that get substituted into the automation.

### Key Terms

| Term | Description |
|------|-------------|
| **Blueprint** | Reusable automation template |
| **Input** | User-configurable parameter |
| **Selector** | UI element type for input |
| **!input** | Reference to input value |
| **Domain** | Type of blueprint (automation, script) |

### Blueprint vs Automation

| Feature | Automation | Blueprint |
|---------|------------|-----------|
| Reusability | Single use | Multiple instances |
| Configuration | Direct YAML | Input parameters |
| Sharing | Full YAML export | Blueprint file |
| Updates | Manual per automation | Update blueprint, recreate instances |

### File Location

```
/config/blueprints/
├── automation/
│   ├── motion_light.yaml
│   └── notification.yaml
└── script/
    └── announce.yaml
```

---

## Blueprint Structure

### Minimal Blueprint

```yaml
blueprint:
  name: Motion Light
  description: Turn on light when motion detected
  domain: automation
  input:
    motion_sensor:
      name: Motion Sensor
      selector:
        entity:
          domain: binary_sensor
          device_class: motion
    light_entity:
      name: Light
      selector:
        entity:
          domain: light

trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"

action:
  - service: light.turn_on
    target:
      entity_id: !input light_entity
```

### Complete Blueprint Structure

```yaml
blueprint:
  name: Motion-Activated Light with Timeout
  description: >
    Turn on a light when motion is detected.
    Light turns off after configurable timeout.
  domain: automation
  author: Your Name
  homeassistant:
    min_version: "2024.1.0"
  source_url: https://github.com/user/repo/blob/main/blueprints/motion_light.yaml
  input:
    # Input definitions here

# Automation content
mode: restart
max_exceeded: silent

trigger:
  # Triggers using !input

condition:
  # Conditions using !input (optional)

action:
  # Actions using !input
```

### Blueprint Metadata

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name |
| `description` | Yes | What the blueprint does |
| `domain` | Yes | `automation` or `script` |
| `author` | No | Creator name |
| `homeassistant.min_version` | No | Minimum HA version |
| `source_url` | No | Link to source code |
| `input` | Yes | Input definitions |

---

## Input Types

### Basic Input

```yaml
input:
  motion_sensor:
    name: Motion Sensor
    description: Sensor that triggers the automation
    selector:
      entity:
        domain: binary_sensor
```

### Required vs Optional

```yaml
input:
  # Required input (no default)
  motion_sensor:
    name: Motion Sensor
    selector:
      entity:
        domain: binary_sensor

  # Optional input (has default)
  timeout:
    name: Timeout
    description: Time to wait before turning off
    default: 300
    selector:
      number:
        min: 30
        max: 3600
        unit_of_measurement: seconds
```

### Input with Default Entity

```yaml
input:
  target_light:
    name: Light
    default: light.living_room
    selector:
      entity:
        domain: light
```

### Collapsed (Advanced) Input

```yaml
input:
  advanced_options:
    name: Advanced Options
    collapsed: true
    input:
      transition_time:
        name: Transition Time
        default: 2
        selector:
          number:
            min: 0
            max: 10
```

---

## Selector Reference

### Entity Selector

```yaml
# Single entity
selector:
  entity:
    domain: light

# With device class
selector:
  entity:
    domain: binary_sensor
    device_class: motion

# Multiple domains
selector:
  entity:
    domain:
      - light
      - switch

# Integration filter
selector:
  entity:
    integration: hue

# Multiple entities
selector:
  entity:
    multiple: true
    domain: light
```

### Target Selector

```yaml
# Flexible target (entity, device, or area)
selector:
  target:
    entity:
      domain: light

# With device filter
selector:
  target:
    device:
      integration: zwave_js
    entity:
      domain: switch
```

### Device Selector

```yaml
# Any device
selector:
  device:

# With integration
selector:
  device:
    integration: zha

# With manufacturer
selector:
  device:
    manufacturer: Philips

# Multiple devices
selector:
  device:
    multiple: true
```

### Area Selector

```yaml
# Single area
selector:
  area:

# Multiple areas
selector:
  area:
    multiple: true
```

### Number Selector

```yaml
# Slider (default)
selector:
  number:
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "%"
    mode: slider

# Box input
selector:
  number:
    min: 0
    max: 3600
    mode: box
    unit_of_measurement: seconds
```

### Boolean Selector

```yaml
selector:
  boolean:
```

### Text Selector

```yaml
# Single line
selector:
  text:

# Multi-line
selector:
  text:
    multiline: true

# With type
selector:
  text:
    type: password

selector:
  text:
    type: url

selector:
  text:
    type: email
```

### Select Selector

```yaml
# Dropdown options
selector:
  select:
    options:
      - label: "Low"
        value: "low"
      - label: "Medium"
        value: "medium"
      - label: "High"
        value: "high"

# Simple list
selector:
  select:
    options:
      - "option1"
      - "option2"
      - "option3"

# Allow custom value
selector:
  select:
    custom_value: true
    options:
      - "preset1"
      - "preset2"

# Multiple selection
selector:
  select:
    multiple: true
    options:
      - "monday"
      - "tuesday"
      - "wednesday"
```

### Time Selector

```yaml
selector:
  time:
```

### Date Selector

```yaml
selector:
  date:
```

### Datetime Selector

```yaml
selector:
  datetime:
```

### Duration Selector

```yaml
selector:
  duration:

# With enable_day
selector:
  duration:
    enable_day: true
```

### Color Temp Selector

```yaml
selector:
  color_temp:
    min_mireds: 153
    max_mireds: 500
```

### Color RGB Selector

```yaml
selector:
  color_rgb:
```

### Icon Selector

```yaml
selector:
  icon:
    placeholder: mdi:lightbulb
```

### Theme Selector

```yaml
selector:
  theme:
```

### Action Selector

```yaml
# Allow user to define actions
selector:
  action:
```

### Trigger Selector

```yaml
# Allow user to define triggers
selector:
  trigger:
```

### Condition Selector

```yaml
# Allow user to define conditions
selector:
  condition:
```

### Object Selector

```yaml
# Free-form YAML/JSON object
selector:
  object:
```

### Attribute Selector

```yaml
# Select entity attribute
selector:
  attribute:
    entity_id: !input some_entity
```

### State Selector

```yaml
# Select state value
selector:
  state:
    entity_id: !input some_entity
```

### Location Selector

```yaml
selector:
  location:
    radius: true
    icon: mdi:home
```

---

## Using Inputs

### Basic !input Reference

```yaml
trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"
```

### In Target

```yaml
action:
  - service: light.turn_on
    target: !input target_light
```

### In Data

```yaml
action:
  - service: light.turn_on
    target:
      entity_id: !input light_entity
    data:
      brightness_pct: !input brightness
```

### In Templates

```yaml
action:
  - service: notify.mobile_app
    data:
      message: >
        Motion detected by {{ states[!input motion_sensor].name }}
```

### In Duration

```yaml
action:
  - delay:
      seconds: !input timeout
```

### In Conditions

```yaml
condition:
  - condition: state
    entity_id: !input enable_toggle
    state: "on"
```

### Multiple Input References

```yaml
trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"
  - platform: state
    entity_id: !input motion_sensor
    to: "off"
    for:
      seconds: !input timeout
```

---

## Blueprint Variables

### Using Variables with Inputs

```yaml
blueprint:
  input:
    motion_sensor:
      selector:
        entity:
          domain: binary_sensor

variables:
  sensor: !input motion_sensor
  sensor_name: "{{ state_attr(sensor, 'friendly_name') }}"

action:
  - service: notify.mobile_app
    data:
      message: "Motion detected by {{ sensor_name }}"
```

### Complex Variable Calculations

```yaml
variables:
  brightness_input: !input brightness
  adjusted_brightness: >
    {% if now().hour < 7 or now().hour > 22 %}
      {{ (brightness_input * 0.3) | int }}
    {% else %}
      {{ brightness_input }}
    {% endif %}

action:
  - service: light.turn_on
    data:
      brightness_pct: "{{ adjusted_brightness }}"
```

---

## Default Values

### Static Defaults

```yaml
input:
  timeout:
    name: Timeout
    default: 300
    selector:
      number:
        min: 30
        max: 3600

  enabled:
    name: Enabled
    default: true
    selector:
      boolean:
```

### Entity Defaults

```yaml
input:
  target_light:
    name: Light
    default: light.living_room
    selector:
      entity:
        domain: light

  notification_service:
    name: Notification Service
    default: notify.mobile_app
    selector:
      text:
```

### List Defaults

```yaml
input:
  days:
    name: Days to Run
    default:
      - mon
      - tue
      - wed
      - thu
      - fri
    selector:
      select:
        multiple: true
        options:
          - mon
          - tue
          - wed
          - thu
          - fri
          - sat
          - sun
```

---

## Publishing Blueprints

### File Structure

```yaml
# motion_light.yaml
blueprint:
  name: Motion-Activated Light
  description: |
    ## Motion-Activated Light

    Turns on a light when motion is detected.

    ### Features
    - Configurable timeout
    - Brightness control
    - Night mode

    ### Requirements
    - Motion sensor
    - Light entity
  domain: automation
  author: Your Name
  source_url: https://github.com/user/repo/blob/main/blueprints/motion_light.yaml
  homeassistant:
    min_version: "2024.1.0"
  input:
    # ...
```

### Markdown Description

```yaml
description: |
  ## Motion Light Blueprint

  This blueprint creates an automation that:
  - Turns on lights when motion is detected
  - Turns off after a configurable timeout
  - Supports brightness adjustment

  ### Configuration
  | Input | Description | Default |
  |-------|-------------|---------|
  | Motion Sensor | Sensor to trigger | Required |
  | Light | Light to control | Required |
  | Timeout | Off delay | 5 minutes |

  ### Notes
  - Works with any motion sensor
  - Supports transition effects
```

### GitHub Repository Structure

```
my-blueprints/
├── README.md
├── motion_light.yaml
├── presence_simulation.yaml
└── screenshots/
    └── config.png
```

---

## Importing Blueprints

### From URL

1. Go to Settings > Automations & Scenes > Blueprints
2. Click "Import Blueprint"
3. Enter URL to raw YAML file

### From File

1. Copy YAML file to `/config/blueprints/automation/`
2. Reload blueprints in Developer Tools

### Creating Automation from Blueprint

```yaml
# automations.yaml (auto-generated by UI)
- id: '1234567890'
  alias: Living Room Motion Light
  description: ''
  use_blueprint:
    path: motion_light.yaml
    input:
      motion_sensor: binary_sensor.living_room_motion
      light_entity: light.living_room
      timeout: 300
```

### Manual Blueprint Usage

```yaml
automation:
  - id: motion_light_kitchen
    alias: Kitchen Motion Light
    use_blueprint:
      path: homeassistant/motion_light.yaml
      input:
        motion_entity: binary_sensor.kitchen_motion
        light_target:
          entity_id: light.kitchen
```

---

## Complete Examples

### Motion Light with Timeout

```yaml
blueprint:
  name: Motion-Activated Light with Timeout
  description: Turn on light when motion detected, off after timeout
  domain: automation
  input:
    motion_sensor:
      name: Motion Sensor
      description: Sensor that detects motion
      selector:
        entity:
          domain: binary_sensor
          device_class: motion
    light_target:
      name: Light
      description: Light to control
      selector:
        target:
          entity:
            domain: light
    timeout:
      name: Timeout
      description: Time to wait before turning off
      default: 300
      selector:
        number:
          min: 30
          max: 3600
          step: 30
          unit_of_measurement: seconds
          mode: slider
    brightness:
      name: Brightness
      description: Brightness level (0-100)
      default: 100
      selector:
        number:
          min: 0
          max: 100
          step: 5
          unit_of_measurement: "%"

mode: restart
max_exceeded: silent

trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"

action:
  - service: light.turn_on
    target: !input light_target
    data:
      brightness_pct: !input brightness
  - wait_for_trigger:
      - platform: state
        entity_id: !input motion_sensor
        to: "off"
        for:
          seconds: !input timeout
  - service: light.turn_off
    target: !input light_target
```

### Low Battery Notification

```yaml
blueprint:
  name: Low Battery Notification
  description: Send notification when device battery is low
  domain: automation
  input:
    battery_sensor:
      name: Battery Sensor
      selector:
        entity:
          domain: sensor
          device_class: battery
    threshold:
      name: Battery Threshold
      default: 20
      selector:
        number:
          min: 5
          max: 50
          unit_of_measurement: "%"
    notification_service:
      name: Notification Service
      default: notify.notify
      selector:
        text:

trigger:
  - platform: numeric_state
    entity_id: !input battery_sensor
    below: !input threshold

condition:
  - condition: template
    value_template: >
      {{ states(!input battery_sensor) not in ['unknown', 'unavailable'] }}

action:
  - service: !input notification_service
    data:
      title: "Low Battery Alert"
      message: >
        {{ state_attr(!input battery_sensor, 'friendly_name') }}
        battery is at {{ states(!input battery_sensor) }}%
```

### Climate Schedule

```yaml
blueprint:
  name: Climate Schedule
  description: Set temperature based on time schedule
  domain: automation
  input:
    climate_entity:
      name: Climate Device
      selector:
        entity:
          domain: climate
    morning_time:
      name: Morning Time
      default: "06:00:00"
      selector:
        time:
    morning_temp:
      name: Morning Temperature
      default: 22
      selector:
        number:
          min: 15
          max: 30
          step: 0.5
          unit_of_measurement: "°C"
    night_time:
      name: Night Time
      default: "22:00:00"
      selector:
        time:
    night_temp:
      name: Night Temperature
      default: 18
      selector:
        number:
          min: 15
          max: 30
          step: 0.5
          unit_of_measurement: "°C"
    weekdays_only:
      name: Weekdays Only
      default: false
      selector:
        boolean:

trigger:
  - platform: time
    at: !input morning_time
    id: morning
  - platform: time
    at: !input night_time
    id: night

condition:
  - condition: or
    conditions:
      - condition: template
        value_template: "{{ not !input weekdays_only }}"
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri

action:
  - choose:
      - conditions:
          - condition: trigger
            id: morning
        sequence:
          - service: climate.set_temperature
            target:
              entity_id: !input climate_entity
            data:
              temperature: !input morning_temp
      - conditions:
          - condition: trigger
            id: night
        sequence:
          - service: climate.set_temperature
            target:
              entity_id: !input climate_entity
            data:
              temperature: !input night_temp
```

### Button Press Actions

```yaml
blueprint:
  name: Button Press Actions
  description: Configure actions for different button presses
  domain: automation
  input:
    button_device:
      name: Button Device
      selector:
        device:
          integration: zha
    single_press_action:
      name: Single Press Action
      default: []
      selector:
        action:
    double_press_action:
      name: Double Press Action
      default: []
      selector:
        action:
    long_press_action:
      name: Long Press Action
      default: []
      selector:
        action:

trigger:
  - platform: device
    device_id: !input button_device
    domain: zha
    type: remote_button_short_press
    subtype: button_1
    id: single
  - platform: device
    device_id: !input button_device
    domain: zha
    type: remote_button_double_press
    subtype: button_1
    id: double
  - platform: device
    device_id: !input button_device
    domain: zha
    type: remote_button_long_press
    subtype: button_1
    id: long

action:
  - choose:
      - conditions:
          - condition: trigger
            id: single
        sequence: !input single_press_action
      - conditions:
          - condition: trigger
            id: double
        sequence: !input double_press_action
      - conditions:
          - condition: trigger
            id: long
        sequence: !input long_press_action
```

---

## Common Patterns

### Optional Condition Toggle

```yaml
input:
  condition_toggle:
    name: Enable Conditions
    default: true
    selector:
      boolean:
  illuminance_threshold:
    name: Light Level Threshold
    default: 50
    selector:
      number:
        min: 0
        max: 500

condition:
  - condition: or
    conditions:
      - condition: template
        value_template: "{{ not !input condition_toggle }}"
      - condition: numeric_state
        entity_id: sensor.illuminance
        below: !input illuminance_threshold
```

### User-Defined Actions

```yaml
input:
  on_action:
    name: Turn On Actions
    description: Actions to run when turning on
    default: []
    selector:
      action:

action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ !input on_action | length > 0 }}"
        sequence: !input on_action
    default:
      - service: light.turn_on
        target:
          entity_id: !input light_entity
```

### Multiple Trigger Sources

```yaml
input:
  motion_sensors:
    name: Motion Sensors
    description: Select one or more motion sensors
    selector:
      entity:
        domain: binary_sensor
        device_class: motion
        multiple: true

trigger:
  - platform: state
    entity_id: !input motion_sensors
    to: "on"
```

---

## Best Practices

### Clear Naming

```yaml
input:
  # Good: Descriptive names
  motion_sensor:
    name: Motion Sensor
    description: The sensor that will trigger the automation

  # Avoid: Unclear names
  ms1:
    name: MS1
```

### Sensible Defaults

```yaml
input:
  timeout:
    name: Timeout
    default: 300  # 5 minutes - reasonable for most motion lights
    selector:
      number:
        min: 30
        max: 3600
```

### Comprehensive Description

```yaml
blueprint:
  description: |
    ## What it does
    Turns on lights when motion is detected.

    ## Requirements
    - Motion sensor with device_class: motion
    - Light entity

    ## Configuration
    - Set motion sensor
    - Set light(s) to control
    - Adjust timeout as needed
```

### Version Compatibility

```yaml
blueprint:
  homeassistant:
    min_version: "2024.1.0"
```

### Input Grouping

```yaml
input:
  # Basic inputs first
  motion_sensor:
    name: Motion Sensor
  light_entity:
    name: Light

  # Advanced options grouped
  advanced:
    name: Advanced Settings
    collapsed: true
    input:
      transition:
        name: Transition Time
        default: 2
      brightness:
        name: Brightness
        default: 100
```

---

## Troubleshooting

### Blueprint Not Appearing

| Problem | Cause | Solution |
|---------|-------|----------|
| Not in list | Wrong location | Put in `blueprints/automation/` |
| Syntax error | Invalid YAML | Check YAML syntax |
| Missing required field | Incomplete metadata | Add name, description, domain |

### Input Not Working

| Problem | Cause | Solution |
|---------|-------|----------|
| Empty value | No default, not set | Add default or require input |
| Wrong type | Selector mismatch | Match selector to expected type |
| !input not substituted | Syntax error | Ensure `!input name` format |

### Validate Blueprint

```yaml
# Check Developer Tools > YAML for errors
# Look for blueprint validation messages in logs

# Enable debug logging
logger:
  logs:
    homeassistant.components.blueprint: debug
```

### Debug Blueprint Variables

```yaml
action:
  - service: system_log.write
    data:
      message: >
        Motion sensor: {{ !input motion_sensor }}
        Timeout: {{ !input timeout }}
      level: info
```

### Common Mistakes

```yaml
# Wrong: Using input directly in template
action:
  - service: notify.mobile_app
    data:
      message: "{{ states(!input sensor) }}"  # Won't work

# Correct: Use variables
variables:
  sensor: !input sensor
action:
  - service: notify.mobile_app
    data:
      message: "{{ states(sensor) }}"

# Wrong: Missing selector
input:
  timeout:
    name: Timeout
    default: 300
    # Missing selector!

# Correct
input:
  timeout:
    name: Timeout
    default: 300
    selector:
      number:
        min: 0
        max: 3600
```
