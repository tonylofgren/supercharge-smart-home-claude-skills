# Blueprint Anatomy - Complete Reference

This document provides a comprehensive reference for creating Home Assistant blueprints.

## Blueprint Structure Overview

```yaml
blueprint:
  name: "Blueprint Name"
  description: "Detailed description of what this blueprint does"
  domain: automation  # or script
  author: "Your Name"
  source_url: "https://github.com/..."
  homeassistant:
    min_version: "2024.1.0"
  input:
    # Input definitions go here

# Trigger/action/condition sections follow
trigger:
  # ...
condition:
  # ...
action:
  # ...
```

---

## Input Selectors - Complete Reference

### Entity Selector

```yaml
input:
  motion_sensor:
    name: Motion Sensor
    description: The motion sensor to monitor
    selector:
      entity:
        domain: binary_sensor
        device_class: motion
        multiple: false  # Set true for multiple entities

  # Multiple domains
  target_device:
    selector:
      entity:
        domain:
          - light
          - switch

  # Filter by integration
  zigbee_device:
    selector:
      entity:
        integration: zha
```

### Device Selector

```yaml
input:
  controller:
    name: Controller Device
    selector:
      device:
        integration: zha
        manufacturer: IKEA
        model: "E1743"
        # Can also use entity for filtering
        entity:
          domain: sensor
          device_class: battery
```

### Target Selector

```yaml
input:
  lights:
    name: Target Lights
    description: Lights to control
    selector:
      target:
        entity:
          domain: light
        # Can target areas, devices, or entities
```

### Area Selector

```yaml
input:
  room:
    name: Room
    selector:
      area:
        multiple: false
        # Can filter by devices/entities in area
        device:
          integration: zha
```

### Number Selector

```yaml
input:
  brightness:
    name: Brightness
    default: 100
    selector:
      number:
        min: 1
        max: 100
        step: 1
        unit_of_measurement: "%"
        mode: slider  # or box

  temperature:
    name: Temperature
    default: 21
    selector:
      number:
        min: 15
        max: 30
        step: 0.5
        unit_of_measurement: "C"
        mode: box
```

### Boolean Selector

```yaml
input:
  enable_notifications:
    name: Enable Notifications
    default: true
    selector:
      boolean:
```

### Text Selector

```yaml
input:
  notification_message:
    name: Message
    default: "Hello!"
    selector:
      text:
        multiline: false
        type: text  # or password, email, url

  description:
    name: Description
    selector:
      text:
        multiline: true
```

### Time Selector

```yaml
input:
  start_time:
    name: Start Time
    default: "07:00:00"
    selector:
      time:
```

### Date Selector

```yaml
input:
  start_date:
    name: Start Date
    selector:
      date:
```

### DateTime Selector

```yaml
input:
  event_time:
    name: Event Date/Time
    selector:
      datetime:
```

### Duration Selector

```yaml
input:
  timeout:
    name: Timeout
    default:
      minutes: 5
    selector:
      duration:
        enable_day: false
```

### Select Selector (Dropdown)

```yaml
input:
  mode:
    name: Operating Mode
    default: "auto"
    selector:
      select:
        options:
          - label: "Automatic"
            value: "auto"
          - label: "Manual"
            value: "manual"
          - label: "Schedule"
            value: "schedule"
        multiple: false
        custom_value: false  # Allow free text
        mode: dropdown  # or list
```

### Color Temperature Selector

```yaml
input:
  color_temp:
    name: Color Temperature
    default: 4000
    selector:
      color_temp:
        min_mireds: 153
        max_mireds: 500
        # Or use kelvin
        unit: kelvin
        min: 2000
        max: 6500
```

### Color RGB Selector

```yaml
input:
  color:
    name: Light Color
    selector:
      color_rgb:
```

### Object Selector (JSON/YAML)

```yaml
input:
  custom_config:
    name: Custom Configuration
    selector:
      object:
```

### Action Selector

```yaml
input:
  custom_actions:
    name: Additional Actions
    default: []
    selector:
      action:
```

### Trigger Selector

```yaml
input:
  additional_triggers:
    name: Additional Triggers
    default: []
    selector:
      trigger:
```

### Condition Selector

```yaml
input:
  extra_conditions:
    name: Extra Conditions
    default: []
    selector:
      condition:
```

### Template Selector

```yaml
input:
  message_template:
    name: Message Template
    selector:
      template:
```

### Icon Selector

```yaml
input:
  custom_icon:
    name: Icon
    default: "mdi:lightbulb"
    selector:
      icon:
        placeholder: "mdi:lightbulb"
```

### Theme Selector

```yaml
input:
  dashboard_theme:
    name: Theme
    selector:
      theme:
```

### Location Selector

```yaml
input:
  coordinates:
    name: Location
    selector:
      location:
        radius: true
        icon: "mdi:map-marker"
```

### Attribute Selector

```yaml
input:
  attr:
    name: Attribute
    selector:
      attribute:
        entity_id: !input target_entity
```

### State Selector

```yaml
input:
  target_state:
    name: Target State
    selector:
      state:
        entity_id: !input target_entity
```

---

## Using Inputs in Automations

### Basic !input Usage

```yaml
trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"

action:
  - service: light.turn_on
    target: !input target_lights
    data:
      brightness_pct: !input brightness
```

### Input in Templates

```yaml
action:
  - service: notify.mobile_app
    data:
      message: >
        Motion detected in {{ area_name(trigger.entity_id) }}
        at brightness {{ !input brightness }}%
```

### Conditional Input Usage

```yaml
action:
  - if:
      - condition: template
        value_template: "{{ !input enable_notifications }}"
    then:
      - service: notify.mobile_app
        data:
          message: !input notification_message
```

---

## Trigger Templates in Blueprints

### Basic Trigger Variables

```yaml
trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"
    id: motion_on
  - platform: state
    entity_id: !input motion_sensor
    to: "off"
    for: !input no_motion_wait
    id: motion_off

action:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_on
        sequence:
          - service: light.turn_on
            target: !input target_lights
      - conditions:
          - condition: trigger
            id: motion_off
        sequence:
          - service: light.turn_off
            target: !input target_lights
```

### Trigger Variables

```yaml
trigger:
  - platform: device
    device_id: !input controller_device
    domain: zha
    type: remote_button_short_press
    subtype: button_1

trigger_variables:
  motion_sensor: !input motion_sensor

condition:
  - condition: state
    entity_id: !input motion_sensor
    state: "off"
```

---

## Advanced Patterns

### Optional Inputs

```yaml
input:
  optional_sensor:
    name: Optional Sensor
    default: []  # Empty default makes it optional
    selector:
      entity:
        domain: sensor

condition:
  - condition: template
    value_template: >
      {{ !input optional_sensor == [] or
         states(!input optional_sensor) | float < 100 }}
```

### Input Groups (Collapsible Sections)

```yaml
input:
  # Group header
  timing_section:
    name: Timing Settings
    icon: mdi:clock
    collapsed: true
    input:
      delay:
        name: Delay
        selector:
          number:
            min: 0
            max: 60
```

### Dynamic Input Visibility

```yaml
input:
  mode:
    name: Mode
    selector:
      select:
        options:
          - simple
          - advanced

  # This shows only when mode is "advanced"
  advanced_setting:
    name: Advanced Setting
    selector:
      number:
        min: 0
        max: 100
```

---

## Mode Configuration

```yaml
mode: restart  # restart, single, parallel, queued

# For queued mode
max: 10

# For parallel mode
max: 5
```

---

## Variables Section

```yaml
variables:
  motion: !input motion_sensor
  light: !input target_light
  is_dark: "{{ state_attr('sun.sun', 'elevation') < 0 }}"
```

---

## Complete Blueprint Example

```yaml
blueprint:
  name: Motion-Activated Light with Brightness
  description: >
    Turn on a light when motion is detected.
    Supports day/night brightness levels.
  domain: automation
  author: Example Author
  source_url: https://github.com/example/blueprint
  homeassistant:
    min_version: "2024.1.0"

  input:
    motion_sensor:
      name: Motion Sensor
      description: The sensor that triggers the light
      selector:
        entity:
          domain: binary_sensor
          device_class: motion

    target_light:
      name: Light
      description: The light to control
      selector:
        target:
          entity:
            domain: light

    day_brightness:
      name: Day Brightness
      description: Brightness during the day (%)
      default: 100
      selector:
        number:
          min: 1
          max: 100
          unit_of_measurement: "%"

    night_brightness:
      name: Night Brightness
      description: Brightness at night (%)
      default: 30
      selector:
        number:
          min: 1
          max: 100
          unit_of_measurement: "%"

    no_motion_wait:
      name: Wait Time
      description: Time to wait before turning off
      default:
        minutes: 5
      selector:
        duration:

    night_start:
      name: Night Starts
      default: "22:00:00"
      selector:
        time:

    night_end:
      name: Night Ends
      default: "07:00:00"
      selector:
        time:

mode: restart

trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"
    id: motion_on
  - platform: state
    entity_id: !input motion_sensor
    to: "off"
    for: !input no_motion_wait
    id: motion_off

variables:
  night_start_time: !input night_start
  night_end_time: !input night_end
  is_night: >
    {% set current = now().strftime('%H:%M:%S') %}
    {{ current >= night_start_time or current < night_end_time }}

action:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_on
        sequence:
          - service: light.turn_on
            target: !input target_light
            data:
              brightness_pct: >
                {% if is_night %}
                  {{ !input night_brightness }}
                {% else %}
                  {{ !input day_brightness }}
                {% endif %}
              transition: 1

      - conditions:
          - condition: trigger
            id: motion_off
        sequence:
          - service: light.turn_off
            target: !input target_light
            data:
              transition: 5
```

---

## Best Practices

1. **Always provide defaults** - Makes blueprint easier to use
2. **Use descriptive names** - Help users understand each input
3. **Group related inputs** - Use collapsible sections
4. **Validate inputs** - Use appropriate selector constraints
5. **Handle edge cases** - Check for empty/invalid inputs
6. **Document thoroughly** - Include examples in description
7. **Test with different configurations** - Ensure all combinations work
8. **Use meaningful trigger IDs** - Makes debugging easier
9. **Provide source_url** - Helps users find updates
10. **Specify min_version** - Prevents compatibility issues
