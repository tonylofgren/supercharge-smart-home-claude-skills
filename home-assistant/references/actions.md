# Home Assistant Actions Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Service Calls](#service-calls)
- [Delay](#delay)
- [Wait Template](#wait-template)
- [Wait for Trigger](#wait-for-trigger)
- [Choose](#choose)
- [If Then Else](#if-then-else)
- [Repeat](#repeat)
- [Parallel](#parallel)
- [Stop](#stop)
- [Variables](#variables)
- [Fire Event](#fire-event)
- [Device Actions](#device-actions)
- [Scene Actions](#scene-actions)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Actions are the things that happen when an automation runs. They execute in sequence unless you use parallel actions.

### Key Terms

| Term | Description |
|------|-------------|
| **Action** | Single step in automation sequence |
| **Service** | Function to call on entity/domain |
| **Target** | Entity/area/device to act on |
| **Data** | Parameters for the service call |
| **Sequence** | Ordered list of actions |

### Action Structure

```yaml
action:
  # Actions run in sequence
  - service: light.turn_on
    target:
      entity_id: light.living_room
  - delay: "00:00:05"
  - service: light.turn_off
    target:
      entity_id: light.living_room
```

---

## Service Calls

Call Home Assistant services to control entities.

### Basic Service Call

```yaml
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
```

### With Data

```yaml
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      color_temp: 400
```

### Target Options

```yaml
# Single entity
target:
  entity_id: light.living_room

# Multiple entities
target:
  entity_id:
    - light.living_room
    - light.kitchen

# By area
target:
  area_id: living_room

# By device
target:
  device_id: abc123def456

# Combined (all receive the service call)
target:
  entity_id: light.hallway
  area_id: bedroom
```

### Dynamic Entity (Template)

```yaml
action:
  - service: light.turn_on
    target:
      entity_id: "{{ trigger.entity_id }}"

# Multiple dynamic entities
action:
  - service: light.turn_off
    target:
      entity_id: >
        {{ states.light
           | selectattr('state', 'eq', 'on')
           | map(attribute='entity_id')
           | list }}
```

### Dynamic Service

```yaml
action:
  - service: "light.turn_{{ 'on' if is_state('sun.sun', 'below_horizon') else 'off' }}"
    target:
      entity_id: light.porch
```

### Template Data

```yaml
action:
  - service: light.turn_on
    target:
      entity_id: light.bedroom
    data:
      brightness_pct: >
        {% if now().hour < 7 %}
          20
        {% elif now().hour < 21 %}
          100
        {% else %}
          50
        {% endif %}
```

### Common Services

```yaml
# Lights
- service: light.turn_on
  target:
    entity_id: light.lamp
  data:
    brightness_pct: 80
    transition: 2

- service: light.turn_off

- service: light.toggle

# Switches
- service: switch.turn_on
- service: switch.turn_off
- service: switch.toggle

# Climate
- service: climate.set_temperature
  target:
    entity_id: climate.thermostat
  data:
    temperature: 22

- service: climate.set_hvac_mode
  data:
    hvac_mode: heat

# Media player
- service: media_player.play_media
  target:
    entity_id: media_player.speaker
  data:
    media_content_id: "spotify:playlist:123"
    media_content_type: playlist

# Notifications
- service: notify.mobile_app_phone
  data:
    title: "Alert"
    message: "Motion detected"

# Scripts
- service: script.turn_on
  target:
    entity_id: script.morning_routine

# Scenes
- service: scene.turn_on
  target:
    entity_id: scene.movie_mode
```

### Response Variable

```yaml
# Capture service response
action:
  - service: weather.get_forecasts
    target:
      entity_id: weather.home
    data:
      type: daily
    response_variable: forecast
  - service: notify.mobile_app
    data:
      message: "Tomorrow: {{ forecast['weather.home'].forecast[0].condition }}"
```

---

## Delay

Pause execution for a duration.

### Fixed Delay

```yaml
action:
  - delay: "00:00:30"  # 30 seconds

  - delay: "00:05:00"  # 5 minutes

  - delay: "01:00:00"  # 1 hour
```

### Structured Delay

```yaml
action:
  - delay:
      hours: 1
      minutes: 30
      seconds: 0
      milliseconds: 0
```

### Template Delay

```yaml
action:
  - delay:
      minutes: "{{ states('input_number.delay_minutes') | int }}"

  - delay: "{{ states('input_text.delay_duration') }}"
```

### Dynamic Duration

```yaml
action:
  - delay:
      seconds: >
        {% if is_state('input_boolean.quick_mode', 'on') %}
          5
        {% else %}
          30
        {% endif %}
```

---

## Wait Template

Wait until a condition becomes true.

### Basic Wait Template

```yaml
action:
  - wait_template: "{{ is_state('binary_sensor.door', 'off') }}"
```

### With Timeout

```yaml
action:
  - wait_template: "{{ is_state('binary_sensor.motion', 'off') }}"
    timeout: "00:10:00"
    continue_on_timeout: true  # Continue if timeout reached
```

### Check If Timed Out

```yaml
action:
  - wait_template: "{{ is_state('lock.door', 'locked') }}"
    timeout: "00:01:00"
    continue_on_timeout: true
  - if:
      - condition: template
        value_template: "{{ wait.completed }}"
    then:
      - service: notify.mobile_app
        data:
          message: "Door is locked"
    else:
      - service: notify.mobile_app
        data:
          message: "Door lock timed out!"
```

### Complex Wait Condition

```yaml
action:
  - wait_template: >
      {{ is_state('binary_sensor.motion', 'off') and
         is_state('binary_sensor.door', 'off') }}
    timeout: "00:05:00"
```

---

## Wait for Trigger

Wait for a specific event to occur.

### Basic Wait for Trigger

```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
```

### With Timeout

```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
        for: "00:05:00"
    timeout: "00:30:00"
    continue_on_timeout: true
```

### Multiple Triggers

```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
        id: motion_off
      - platform: state
        entity_id: input_boolean.override
        to: "on"
        id: override
    timeout: "00:10:00"
  - choose:
      - conditions: "{{ wait.trigger.id == 'motion_off' }}"
        sequence:
          - service: light.turn_off
      - conditions: "{{ wait.trigger.id == 'override' }}"
        sequence:
          - service: notify.mobile_app
            data:
              message: "Override activated"
```

### Access Wait Trigger Data

```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: sensor.temperature
    timeout: "01:00:00"
  - service: notify.mobile_app
    data:
      message: >
        Temperature changed to {{ wait.trigger.to_state.state }}°C
```

---

## Choose

Execute different actions based on conditions.

### Basic Choose

```yaml
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "Home"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.living_room
      - conditions:
          - condition: state
            entity_id: input_select.mode
            state: "Away"
        sequence:
          - service: light.turn_off
            target:
              entity_id: all
```

### With Default

```yaml
action:
  - choose:
      - conditions:
          - condition: numeric_state
            entity_id: sensor.temperature
            above: 25
        sequence:
          - service: climate.set_hvac_mode
            data:
              hvac_mode: cool
      - conditions:
          - condition: numeric_state
            entity_id: sensor.temperature
            below: 18
        sequence:
          - service: climate.set_hvac_mode
            data:
              hvac_mode: heat
    default:
      - service: climate.set_hvac_mode
        data:
          hvac_mode: "off"
```

### Shorthand Conditions

```yaml
action:
  - choose:
      - conditions: "{{ trigger.to_state.state == 'on' }}"
        sequence:
          - service: light.turn_on
      - conditions: "{{ trigger.to_state.state == 'off' }}"
        sequence:
          - service: light.turn_off
```

### Based on Trigger ID

```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.motion_living
    to: "on"
    id: living
  - platform: state
    entity_id: binary_sensor.motion_kitchen
    to: "on"
    id: kitchen
action:
  - choose:
      - conditions:
          - condition: trigger
            id: living
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.living_room
      - conditions:
          - condition: trigger
            id: kitchen
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.kitchen
```

---

## If Then Else

Conditional execution with clearer syntax.

### Basic If

```yaml
action:
  - if:
      - condition: state
        entity_id: input_boolean.notifications_enabled
        state: "on"
    then:
      - service: notify.mobile_app
        data:
          message: "Alert!"
```

### If Then Else

```yaml
action:
  - if:
      - condition: sun
        after: sunset
    then:
      - service: light.turn_on
        target:
          entity_id: light.porch
        data:
          brightness_pct: 100
    else:
      - service: light.turn_on
        target:
          entity_id: light.porch
        data:
          brightness_pct: 30
```

### Nested If

```yaml
action:
  - if:
      - condition: state
        entity_id: binary_sensor.motion
        state: "on"
    then:
      - if:
          - condition: sun
            after: sunset
        then:
          - service: light.turn_on
            data:
              brightness_pct: 100
        else:
          - service: light.turn_on
            data:
              brightness_pct: 50
```

### Shorthand Condition

```yaml
action:
  - if: "{{ is_state('binary_sensor.motion', 'on') }}"
    then:
      - service: light.turn_on
```

---

## Repeat

Loop actions multiple times.

### Repeat Count

```yaml
action:
  - repeat:
      count: 3
      sequence:
        - service: light.toggle
          target:
            entity_id: light.alert
        - delay: "00:00:01"
```

### Repeat While

```yaml
action:
  - repeat:
      while:
        - condition: state
          entity_id: binary_sensor.door
          state: "on"
        - condition: template
          value_template: "{{ repeat.index <= 10 }}"
      sequence:
        - service: notify.mobile_app
          data:
            message: "Door still open! (attempt {{ repeat.index }})"
        - delay: "00:01:00"
```

### Repeat Until

```yaml
action:
  - repeat:
      until:
        - condition: state
          entity_id: lock.front_door
          state: "locked"
      sequence:
        - service: lock.lock
          target:
            entity_id: lock.front_door
        - delay: "00:00:05"
        - condition: template
          value_template: "{{ repeat.index < 3 }}"  # Max 3 attempts
```

### Repeat For Each

```yaml
action:
  - repeat:
      for_each:
        - light.living_room
        - light.kitchen
        - light.bedroom
      sequence:
        - service: light.turn_on
          target:
            entity_id: "{{ repeat.item }}"
        - delay: "00:00:01"
```

### For Each with Templates

```yaml
action:
  - repeat:
      for_each: >
        {{ states.light
           | selectattr('state', 'eq', 'on')
           | map(attribute='entity_id')
           | list }}
      sequence:
        - service: light.turn_off
          target:
            entity_id: "{{ repeat.item }}"
        - delay: "00:00:00.5"
```

### Repeat Variables

```yaml
# Available in repeat block:
# repeat.index - Current iteration (1-based)
# repeat.first - True on first iteration
# repeat.last - True on last iteration (for_each only)
# repeat.item - Current item (for_each only)

action:
  - repeat:
      count: 5
      sequence:
        - service: notify.mobile_app
          data:
            message: "Iteration {{ repeat.index }} of 5"
```

---

## Parallel

Run actions simultaneously.

### Basic Parallel

```yaml
action:
  - parallel:
      - service: light.turn_on
        target:
          entity_id: light.living_room
      - service: light.turn_on
        target:
          entity_id: light.kitchen
      - service: media_player.turn_on
        target:
          entity_id: media_player.tv
```

### Parallel Sequences

```yaml
action:
  - parallel:
      - sequence:
          - service: light.turn_on
            target:
              entity_id: light.living_room
          - delay: "00:00:05"
          - service: light.turn_off
            target:
              entity_id: light.living_room
      - sequence:
          - service: notify.mobile_app
            data:
              message: "Light sequence started"
```

### Mixed Parallel

```yaml
action:
  - parallel:
      # Service call
      - service: light.turn_on
        target:
          entity_id: light.lamp
      # Sequence
      - sequence:
          - delay: "00:00:02"
          - service: switch.turn_on
            target:
              entity_id: switch.fan
      # Another service
      - service: media_player.volume_set
        target:
          entity_id: media_player.speaker
        data:
          volume_level: 0.5
```

---

## Stop

Stop automation execution.

### Basic Stop

```yaml
action:
  - if:
      - condition: state
        entity_id: input_boolean.disabled
        state: "on"
    then:
      - stop: "Automation disabled by user"
  - service: light.turn_on
```

### Stop with Error

```yaml
action:
  - if:
      - condition: template
        value_template: "{{ states('sensor.battery') | float < 10 }}"
    then:
      - stop: "Battery too low"
        error: true
```

### Stop in Choose

```yaml
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: alarm_control_panel.home
            state: armed_away
        sequence:
          - stop: "Cannot run while alarm is armed"
```

### Response Variables (for Scripts)

```yaml
script:
  calculate_something:
    sequence:
      - stop: "Calculation complete"
        response_variable: result
    variables:
      result: "{{ some_calculation }}"
```

---

## Variables

Define and use local variables.

### Set Variables

```yaml
action:
  - variables:
      light_entity: light.living_room
      brightness: 80
  - service: light.turn_on
    target:
      entity_id: "{{ light_entity }}"
    data:
      brightness_pct: "{{ brightness }}"
```

### Dynamic Variables

```yaml
action:
  - variables:
      target_temp: >
        {% if now().hour < 7 %}
          18
        {% elif now().hour < 22 %}
          22
        {% else %}
          20
        {% endif %}
  - service: climate.set_temperature
    target:
      entity_id: climate.thermostat
    data:
      temperature: "{{ target_temp }}"
```

### Variables from Trigger

```yaml
action:
  - variables:
      entity: "{{ trigger.entity_id }}"
      old_state: "{{ trigger.from_state.state }}"
      new_state: "{{ trigger.to_state.state }}"
  - service: notify.mobile_app
    data:
      message: "{{ entity }} changed from {{ old_state }} to {{ new_state }}"
```

### Computed Variables

```yaml
action:
  - variables:
      lights_on: >
        {{ states.light
           | selectattr('state', 'eq', 'on')
           | map(attribute='entity_id')
           | list }}
      count: "{{ lights_on | count }}"
  - service: notify.mobile_app
    data:
      message: "{{ count }} lights are on"
```

---

## Fire Event

Trigger custom events.

### Basic Event

```yaml
action:
  - event: custom_event
    event_data:
      message: "Something happened"
```

### With Data

```yaml
action:
  - event: motion_detected
    event_data:
      location: living_room
      timestamp: "{{ now().isoformat() }}"
      person: "{{ trigger.to_state.attributes.friendly_name }}"
```

### Listen for Event

```yaml
# In another automation
trigger:
  - platform: event
    event_type: motion_detected
    event_data:
      location: living_room
action:
  - service: notify.mobile_app
    data:
      message: "Motion in {{ trigger.event.data.location }}"
```

---

## Device Actions

Device-specific actions from the UI.

### Basic Device Action

```yaml
action:
  - device_id: abc123def456
    domain: light
    type: turn_on
```

### With Options

```yaml
action:
  - device_id: abc123def456
    domain: light
    type: turn_on
    brightness_pct: 80
```

### Multiple Devices

```yaml
action:
  - device_id: abc123
    domain: cover
    type: close
  - device_id: def456
    domain: lock
    type: lock
```

---

## Scene Actions

Activate scenes.

### Activate Scene

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.movie_mode
```

### With Transition

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.evening
    data:
      transition: 5
```

### Create Scene on the Fly

```yaml
action:
  - service: scene.create
    data:
      scene_id: before_change
      snapshot_entities:
        - light.living_room
        - light.kitchen
  # Make changes
  - service: light.turn_off
    target:
      entity_id: all
  - delay: "00:00:30"
  # Restore
  - service: scene.turn_on
    target:
      entity_id: scene.before_change
```

---

## Common Patterns

### Notification with Timeout

```yaml
action:
  - service: notify.mobile_app
    data:
      title: "Door Open"
      message: "Front door has been open for 5 minutes"
      data:
        actions:
          - action: "ACKNOWLEDGE"
            title: "OK"
  - wait_for_trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: ACKNOWLEDGE
      - platform: state
        entity_id: binary_sensor.front_door
        to: "off"
    timeout: "00:05:00"
  - if:
      - condition: template
        value_template: "{{ not wait.completed }}"
    then:
      - service: notify.mobile_app
        data:
          message: "Door still open!"
```

### Retry Logic

```yaml
action:
  - repeat:
      until:
        - condition: state
          entity_id: lock.front_door
          state: "locked"
      sequence:
        - service: lock.lock
          target:
            entity_id: lock.front_door
        - delay: "00:00:05"
        - if:
            - condition: template
              value_template: "{{ repeat.index >= 3 }}"
          then:
            - service: notify.mobile_app
              data:
                message: "Failed to lock door after 3 attempts"
            - stop: "Lock failed"
```

### Fade Light

```yaml
action:
  - variables:
      start: 100
      end: 0
      steps: 10
  - repeat:
      count: "{{ steps }}"
      sequence:
        - service: light.turn_on
          target:
            entity_id: light.bedroom
          data:
            brightness_pct: >
              {{ start - ((start - end) / steps * repeat.index) | int }}
        - delay: "00:00:01"
```

### Sequential Device Control

```yaml
action:
  - repeat:
      for_each:
        - entity_id: light.light_1
          brightness: 100
        - entity_id: light.light_2
          brightness: 80
        - entity_id: light.light_3
          brightness: 60
      sequence:
        - service: light.turn_on
          target:
            entity_id: "{{ repeat.item.entity_id }}"
          data:
            brightness_pct: "{{ repeat.item.brightness }}"
        - delay: "00:00:00.5"
```

### Conditional Notification

```yaml
action:
  - if:
      - condition: state
        entity_id: input_boolean.notifications_enabled
        state: "on"
    then:
      - choose:
          - conditions:
              - condition: state
                entity_id: person.john
                state: home
            sequence:
              - service: tts.speak
                target:
                  entity_id: tts.google
                data:
                  message: "{{ message }}"
                  media_player_entity_id: media_player.speaker
          - conditions:
              - condition: state
                entity_id: person.john
                state: not_home
            sequence:
              - service: notify.mobile_app
                data:
                  message: "{{ message }}"
```

### Save and Restore State

```yaml
action:
  # Save current state
  - service: scene.create
    data:
      scene_id: temp_state
      snapshot_entities:
        - light.living_room
        - light.kitchen
  # Do something
  - service: light.turn_on
    target:
      area_id: living_room
    data:
      color_name: red
      brightness_pct: 100
  - delay: "00:00:10"
  # Restore
  - service: scene.turn_on
    target:
      entity_id: scene.temp_state
```

---

## Best Practices

### Use Meaningful Variable Names

```yaml
# Good
action:
  - variables:
      target_brightness: 80
      notification_message: "Motion detected in {{ area }}"

# Avoid
action:
  - variables:
      x: 80
      msg: "Motion"
```

### Handle Errors Gracefully

```yaml
action:
  - if:
      - condition: template
        value_template: >
          {{ states('sensor.api_data') not in ['unknown', 'unavailable'] }}
    then:
      - service: notify.mobile_app
        data:
          message: "{{ states('sensor.api_data') }}"
    else:
      - service: system_log.write
        data:
          message: "API data unavailable"
          level: warning
```

### Avoid Long Delays

```yaml
# Avoid: Long blocking delay
action:
  - delay: "01:00:00"  # Blocks for 1 hour
  - service: light.turn_off

# Better: Use wait_for_trigger with timeout
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout: "01:00:00"
  - service: light.turn_off
```

### Use Parallel for Independent Actions

```yaml
# Slow: Sequential
action:
  - service: light.turn_on
    target:
      entity_id: light.1
  - service: light.turn_on
    target:
      entity_id: light.2
  - service: light.turn_on
    target:
      entity_id: light.3

# Fast: Parallel
action:
  - parallel:
      - service: light.turn_on
        target:
          entity_id: light.1
      - service: light.turn_on
        target:
          entity_id: light.2
      - service: light.turn_on
        target:
          entity_id: light.3

# Best: Single call with multiple targets
action:
  - service: light.turn_on
    target:
      entity_id:
        - light.1
        - light.2
        - light.3
```

---

## Troubleshooting

### Action Not Executing

| Problem | Cause | Solution |
|---------|-------|----------|
| Service not found | Typo in service name | Check service in Developer Tools |
| Entity not found | Wrong entity_id | Verify entity exists |
| No target | Missing target | Add target section |
| Invalid data | Wrong data format | Check service documentation |

### Debug Actions

```yaml
# Add logging
action:
  - service: system_log.write
    data:
      message: "Starting action sequence"
      level: info
  - service: light.turn_on
    target:
      entity_id: light.test
  - service: system_log.write
    data:
      message: "Light turn_on called"
      level: info
```

### Check Service in Developer Tools

```yaml
# Go to Developer Tools > Services
# Enter service name and parameters
# Click "Call Service" to test

service: light.turn_on
data:
  entity_id: light.living_room
  brightness_pct: 80
```

### Common Mistakes

```yaml
# Wrong: target inside data
action:
  - service: light.turn_on
    data:
      entity_id: light.lamp  # Wrong location

# Correct: target separate from data
action:
  - service: light.turn_on
    target:
      entity_id: light.lamp
    data:
      brightness_pct: 80

# Wrong: Missing quotes on template
action:
  - delay:
      minutes: {{ states('input_number.delay') }}  # Missing quotes

# Correct
action:
  - delay:
      minutes: "{{ states('input_number.delay') | int }}"
```

### Trace Analysis

```yaml
# Check automation trace:
# Settings > Automations > (automation) > Traces

# Trace shows:
# - Each action executed
# - Variables at each step
# - Errors and their location
# - Time taken per action
```
