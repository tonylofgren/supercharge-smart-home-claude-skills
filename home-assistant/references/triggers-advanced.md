# Advanced Triggers in Home Assistant

> Comprehensive guide to advanced trigger types and optimization patterns

## Overview

Home Assistant 2024/2025 introduces powerful new trigger capabilities. This guide covers advanced trigger patterns, the new Wait for State trigger (2024.4+), enhanced Conversation triggers (2024.11+), and performance optimization strategies.

---

## Wait for State Trigger (2024.4+)

### Introduction

The `wait_for_trigger` action with state triggers was enhanced in 2024.4 to support comparison operators, making it easier to wait for specific state conditions without complex template logic.

### Basic Syntax

```yaml
automation:
  - id: wait_for_state_basic
    alias: "Wait for Door to Close"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Front door opened, waiting for it to close..."
      - wait_for_trigger:
          - platform: state
            entity_id: binary_sensor.front_door
            to: "off"
        timeout:
          minutes: 5
      - choose:
          - conditions: "{{ wait.trigger == none }}"
            sequence:
              - service: notify.mobile_app
                data:
                  message: "Warning: Front door still open after 5 minutes!"
          - conditions: "{{ wait.trigger != none }}"
            sequence:
              - service: notify.mobile_app
                data:
                  message: "Front door closed"
```

### Comparison Operators (2024.4+)

Wait for numeric state changes with operators:

```yaml
automation:
  - id: wait_for_temperature
    alias: "Wait for Temperature to Drop"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 30
    action:
      - service: climate.turn_on
        target:
          entity_id: climate.living_room
      - wait_for_trigger:
          - platform: numeric_state
            entity_id: sensor.outdoor_temperature
            below: 25
        timeout:
          hours: 4
      - service: climate.turn_off
        target:
          entity_id: climate.living_room
```

### Available Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `above` | Value greater than | `above: 25` |
| `below` | Value less than | `below: 20` |
| `to` | Exact state match | `to: "on"` |
| `from` | Previous state match | `from: "off"` |
| `for` | Duration held | `for: "00:05:00"` |

### Advanced Wait Patterns

#### Multiple Conditions Wait

```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
        for:
          minutes: 10
      - platform: state
        entity_id: input_boolean.override
        to: "on"
    timeout:
      minutes: 30
  # wait.trigger contains whichever triggered first
  - choose:
      - conditions: "{{ wait.trigger.platform == 'state' and wait.trigger.entity_id == 'input_boolean.override' }}"
        sequence:
          - service: notify.mobile_app
            data:
              message: "Override activated"
```

#### Wait with Template Condition

```yaml
action:
  - wait_for_trigger:
      - platform: template
        value_template: >
          {{ states('sensor.power_usage') | float(0) < 100
             and is_state('binary_sensor.grid_available', 'on') }}
    timeout:
      hours: 2
    continue_on_timeout: true
```

#### Timeout Handling

```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: lock.front_door
        to: "locked"
    timeout:
      minutes: 2
    continue_on_timeout: true  # Don't stop if timeout
  - if:
      - condition: template
        value_template: "{{ wait.trigger == none }}"
    then:
      - service: lock.lock
        target:
          entity_id: lock.front_door
      - service: notify.mobile_app
        data:
          message: "Auto-locked front door after timeout"
```

---

## Conversation Trigger (2024.11+)

### Introduction

Conversation triggers allow automations to respond to natural language commands through Assist. The 2024.11+ update brings enhanced slot handling and response variables.

### Basic Syntax

```yaml
automation:
  - id: voice_lights
    alias: "Voice: Control Lights"
    trigger:
      - platform: conversation
        command:
          - "turn on the {area} lights"
          - "turn off the {area} lights"
          - "lights on in {area}"
          - "lights off in {area}"
    action:
      - variables:
          action: >
            {% if 'on' in trigger.sentence | lower %}
              turn_on
            {% else %}
              turn_off
            {% endif %}
          target_area: "{{ trigger.slots.area }}"
      - service: "light.{{ action }}"
        target:
          area_id: "{{ target_area }}"
```

### Slot Types

```yaml
automation:
  - id: voice_temperature
    alias: "Voice: Set Temperature"
    trigger:
      - platform: conversation
        command:
          - "set temperature to {temperature}"
          - "set thermostat to {temperature} degrees"
          - "make it {temperature} degrees"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ trigger.slots.temperature | float }}"
```

### Response Variables (2024.11+)

```yaml
automation:
  - id: voice_status
    alias: "Voice: Get Status"
    trigger:
      - platform: conversation
        command:
          - "what is the {entity_type} in the {area}"
          - "how is the {entity_type} in {area}"
    action:
      - variables:
          entity_type: "{{ trigger.slots.entity_type }}"
          area: "{{ trigger.slots.area }}"
          response_text: >
            {% set domain_map = {
              'temperature': 'sensor',
              'humidity': 'sensor',
              'light': 'light',
              'lights': 'light'
            } %}
            {% set domain = domain_map.get(entity_type, 'sensor') %}
            {% set entities = area_entities(area) | select('match', domain ~ '.*') | list %}
            {% if entities %}
              {% set entity = entities[0] %}
              The {{ entity_type }} in {{ area }} is {{ states(entity) }}
            {% else %}
              I couldn't find {{ entity_type }} in {{ area }}
            {% endif %}
      - stop: ""
        response_variable: response_text
```

### Advanced Conversation Patterns

#### Wildcards and Alternatives

```yaml
trigger:
  - platform: conversation
    command:
      - "[please|] turn {state} [the|] {area} [light|lights]"
      - "[please|] {state} [the|] {area} [light|lights]"
```

Syntax:
- `[option1|option2]` - alternatives (either/or)
- `[optional|]` - optional word
- `{slot}` - capture variable

#### Context-Aware Commands

```yaml
automation:
  - id: voice_contextual
    alias: "Voice: Contextual Commands"
    trigger:
      - platform: conversation
        command:
          - "I'm going to bed"
          - "goodnight"
          - "time for bed"
    condition:
      - condition: time
        after: "20:00:00"
        before: "06:00:00"
    action:
      - service: script.bedtime_routine
      - stop: ""
        response_variable: "Good night! Running bedtime routine."
```

#### Multi-Intent Handling

```yaml
automation:
  - id: voice_multi_intent
    alias: "Voice: Complex Commands"
    trigger:
      - platform: conversation
        command:
          - "turn on {device1} and {device2}"
          - "{device1} and {device2} on"
    action:
      - service: homeassistant.turn_on
        target:
          entity_id: "{{ trigger.slots.device1 }}"
      - service: homeassistant.turn_on
        target:
          entity_id: "{{ trigger.slots.device2 }}"
```

---

## Template Triggers - Advanced

### Multi-Entity Monitoring

```yaml
automation:
  - id: template_multi_entity
    alias: "Monitor Multiple Sensors"
    trigger:
      - platform: template
        value_template: >
          {% set sensors = [
            'sensor.temp_living_room',
            'sensor.temp_bedroom',
            'sensor.temp_kitchen'
          ] %}
          {% set temps = sensors | map('states') | map('float', 0) | list %}
          {% set avg = temps | average %}
          {{ avg > 25 }}
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.main
        data:
          hvac_mode: cool
```

### Rate-Limited Template Trigger

```yaml
automation:
  - id: template_rate_limited
    alias: "Rate Limited Trigger"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.power_usage') | float(0) > 5000 }}
        for:
          seconds: 30  # Debounce: must be true for 30s
    mode: single
    max_exceeded: silent
    action:
      - service: notify.mobile_app
        data:
          message: "High power usage detected"
      - delay:
          minutes: 15  # Rate limit: don't trigger again for 15min
```

### State Change Rate Detection

```yaml
automation:
  - id: template_rate_of_change
    alias: "Detect Rapid Temperature Change"
    trigger:
      - platform: template
        value_template: >
          {% set current = states('sensor.temperature') | float(0) %}
          {% set previous = state_attr('sensor.temperature', 'last_value') | float(current) %}
          {% set change_rate = (current - previous) | abs %}
          {{ change_rate > 2 }}  # More than 2 degrees change
    action:
      - service: notify.mobile_app
        data:
          message: "Rapid temperature change detected!"
```

### Combined Condition Template

```yaml
automation:
  - id: template_complex_condition
    alias: "Complex State Monitoring"
    trigger:
      - platform: template
        value_template: >
          {% set occupancy = is_state('binary_sensor.occupancy', 'on') %}
          {% set time_ok = now().hour >= 8 and now().hour < 22 %}
          {% set not_vacation = is_state('input_boolean.vacation', 'off') %}
          {% set lights_off = expand('group.all_lights')
             | selectattr('state', 'eq', 'on') | list | count == 0 %}
          {{ occupancy and time_ok and not_vacation and lights_off }}
    action:
      - service: light.turn_on
        target:
          area_id: living_room
```

---

## Device Triggers - Edge Cases

### Button Events

```yaml
automation:
  - id: device_button_multi
    alias: "Multi-Click Button Handler"
    trigger:
      - platform: device
        domain: mqtt
        device_id: abc123
        type: action
        subtype: single
        id: single_click
      - platform: device
        domain: mqtt
        device_id: abc123
        type: action
        subtype: double
        id: double_click
      - platform: device
        domain: mqtt
        device_id: abc123
        type: action
        subtype: hold
        id: hold
    action:
      - choose:
          - conditions: "{{ trigger.id == 'single_click' }}"
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.ceiling
          - conditions: "{{ trigger.id == 'double_click' }}"
            sequence:
              - service: scene.turn_on
                target:
                  entity_id: scene.bright
          - conditions: "{{ trigger.id == 'hold' }}"
            sequence:
              - service: light.turn_off
                target:
                  area_id: living_room
```

### Remote Control Events

```yaml
automation:
  - id: device_remote
    alias: "Handle Remote Control"
    trigger:
      - platform: event
        event_type: zha_event
        event_data:
          device_ieee: "00:11:22:33:44:55:66:77"
    action:
      - variables:
          command: "{{ trigger.event.data.command }}"
          args: "{{ trigger.event.data.args }}"
      - choose:
          - conditions: "{{ command == 'on' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.main
          - conditions: "{{ command == 'off' }}"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: light.main
          - conditions: "{{ command == 'move_with_on_off' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.main
                data:
                  brightness_step_pct: >
                    {% if args.move_mode == 0 %}
                      10
                    {% else %}
                      -10
                    {% endif %}
```

### State vs Event Triggers

| Use Case | Trigger Type | Why |
|----------|-------------|-----|
| Light turned on | State | Persistent state |
| Button pressed | Event | Momentary action |
| Temperature crossed threshold | Numeric State | Value comparison |
| Motion detected | State | Binary sensor state |
| Zigbee command received | Event | No persistent state |
| Webhook received | Webhook | External event |

```yaml
# State trigger - for persistent states
trigger:
  - platform: state
    entity_id: light.living_room
    to: "on"

# Event trigger - for momentary events
trigger:
  - platform: event
    event_type: zha_event
    event_data:
      command: "toggle"
```

---

## Time-Based Trigger Patterns

### Dynamic Time Triggers

```yaml
automation:
  - id: time_dynamic
    alias: "Dynamic Wake Up Time"
    trigger:
      - platform: time
        at: input_datetime.wake_up_time
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom
```

### Workday-Aware Triggers

```yaml
automation:
  - id: time_workday
    alias: "Workday Morning Routine"
    trigger:
      - platform: time
        at: "06:30:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday_sensor
        state: "on"
      - condition: state
        entity_id: person.john
        state: "home"
    action:
      - service: script.morning_routine
```

### Sunrise/Sunset with Offset

```yaml
automation:
  - id: time_sun_offset
    alias: "Lights Before Sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"  # 30 minutes before
    condition:
      - condition: state
        entity_id: group.family
        state: "home"
    action:
      - service: light.turn_on
        target:
          area_id: living_room
        data:
          brightness_pct: 30
```

### Time Pattern Triggers

```yaml
automation:
  - id: time_pattern
    alias: "Every 15 Minutes Check"
    trigger:
      - platform: time_pattern
        minutes: "/15"  # Every 15 minutes
    action:
      - service: script.periodic_check
```

---

## MQTT Trigger Patterns

### JSON Payload Parsing

```yaml
automation:
  - id: mqtt_json
    alias: "MQTT JSON Trigger"
    trigger:
      - platform: mqtt
        topic: "sensors/outdoor/weather"
    condition:
      - condition: template
        value_template: >
          {{ trigger.payload_json.temperature | float(0) > 30 }}
    action:
      - service: notify.mobile_app
        data:
          message: "Outdoor temperature is {{ trigger.payload_json.temperature }}°C"
```

### MQTT with Wildcards

```yaml
automation:
  - id: mqtt_wildcard
    alias: "All Room Sensors"
    trigger:
      - platform: mqtt
        topic: "home/+/temperature"  # + = single level wildcard
    action:
      - variables:
          room: "{{ trigger.topic.split('/')[1] }}"
          temp: "{{ trigger.payload | float }}"
      - service: input_number.set_value
        target:
          entity_id: "input_number.temp_{{ room }}"
        data:
          value: "{{ temp }}"
```

---

## Performance Optimization

### High-Frequency Trigger Management

```yaml
# BAD: Triggers on every state change
automation:
  - id: bad_high_frequency
    alias: "Bad: Every Power Update"
    trigger:
      - platform: state
        entity_id: sensor.power_usage
    action:
      # Fires hundreds of times per hour

# GOOD: Debounced with threshold
automation:
  - id: good_debounced
    alias: "Good: Power Threshold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.power_usage
        above: 3000
        for:
          seconds: 30
    action:
      # Fires only when sustained above threshold
```

### Template Caching

```yaml
# BAD: Complex template evaluated constantly
trigger:
  - platform: template
    value_template: >
      {% set entities = states.light | list %}
      {% set on_count = entities | selectattr('state', 'eq', 'on') | list | count %}
      {{ on_count > 5 }}

# GOOD: Use dedicated sensor
template:
  - sensor:
      - name: "Lights On Count"
        state: >
          {{ states.light | selectattr('state', 'eq', 'on') | list | count }}

automation:
  trigger:
    - platform: numeric_state
      entity_id: sensor.lights_on_count
      above: 5
```

### State Change Batching

```yaml
automation:
  - id: batched_triggers
    alias: "Batched State Changes"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.door_1
          - binary_sensor.door_2
          - binary_sensor.door_3
          - binary_sensor.door_4
        to: "on"
    mode: queued
    max: 10
    action:
      - service: notify.mobile_app
        data:
          message: "{{ trigger.to_state.name }} opened"
```

### Trigger ID for Efficiency

```yaml
automation:
  - id: efficient_multi_trigger
    alias: "Efficient Multi-Trigger"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
        id: front
      - platform: state
        entity_id: binary_sensor.back_door
        to: "on"
        id: back
      - platform: state
        entity_id: binary_sensor.garage_door
        to: "on"
        id: garage
    action:
      - service: notify.mobile_app
        data:
          message: >
            {% set door_names = {
              'front': 'Front door',
              'back': 'Back door',
              'garage': 'Garage door'
            } %}
            {{ door_names[trigger.id] }} opened
```

---

## Debouncing Strategies

### For Clause Debouncing

```yaml
automation:
  - id: debounce_for
    alias: "Debounced Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
        for:
          seconds: 5  # Must stay "on" for 5 seconds
    action:
      - service: light.turn_on
        target:
          entity_id: light.room
```

### Mode-Based Debouncing

```yaml
automation:
  - id: debounce_mode
    alias: "Single Mode Debounce"
    mode: single  # Ignore new triggers while running
    trigger:
      - platform: state
        entity_id: binary_sensor.button
        to: "on"
    action:
      - service: light.toggle
        target:
          entity_id: light.room
      - delay:
          milliseconds: 500  # Minimum delay between executions
```

### Counter-Based Rate Limiting

```yaml
automation:
  - id: rate_limit_counter
    alias: "Rate Limited Notifications"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    condition:
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - as_timestamp(state_attr('automation.rate_limit_counter', 'last_triggered') | default(0))) > 30 }}
    action:
      - service: notify.mobile_app
        data:
          message: "Doorbell pressed"
```

---

## Best Practices

### Trigger Selection Guide

| Scenario | Recommended Trigger | Why |
|----------|-------------------|-----|
| Light state change | `state` | Simple, efficient |
| Temperature threshold | `numeric_state` with `for` | Avoids rapid firing |
| Button press | `device` or `event` | Momentary action |
| Complex condition | `template` with sensor | Pre-calculate |
| Time-based | `time` or `time_pattern` | Built-in scheduling |
| Voice command | `conversation` | Natural language |
| External webhook | `webhook` | API integration |

### Performance Checklist

1. **Avoid** template triggers that evaluate complex expressions
2. **Use** `for` clause to debounce rapid state changes
3. **Prefer** `numeric_state` over template for value comparisons
4. **Create** template sensors for frequently-used calculations
5. **Use** trigger IDs instead of complex condition logic
6. **Set** appropriate `mode` (single, queued, restart)
7. **Batch** related triggers in single automation
8. **Monitor** automation traces for performance issues

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Trigger never fires | Check entity exists, conditions met |
| Triggers too often | Add `for` clause, debounce |
| Template trigger slow | Move calculation to sensor |
| Missing events | Use event trigger instead of state |
| Timeout not working | Check `continue_on_timeout` setting |

---

## Resources

- [Home Assistant Trigger Documentation](https://www.home-assistant.io/docs/automation/trigger/)
- [Wait for Trigger](https://www.home-assistant.io/docs/scripts/#wait-for-trigger)
- [Conversation Integration](https://www.home-assistant.io/integrations/conversation/)
- [Template Triggers](https://www.home-assistant.io/docs/automation/trigger/#template-trigger)
