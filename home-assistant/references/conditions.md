# Home Assistant Conditions Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [State Condition](#state-condition)
- [Numeric State Condition](#numeric-state-condition)
- [Time Condition](#time-condition)
- [Sun Condition](#sun-condition)
- [Zone Condition](#zone-condition)
- [Template Condition](#template-condition)
- [Device Condition](#device-condition)
- [Trigger Condition](#trigger-condition)
- [Logical Conditions](#logical-conditions)
- [Shorthand Conditions](#shorthand-conditions)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Conditions determine whether an automation's actions should run. If any condition evaluates to false, the actions are skipped.

### Key Terms

| Term | Description |
|------|-------------|
| **Condition** | Check that must pass for actions to run |
| **And** | All conditions must be true |
| **Or** | At least one condition must be true |
| **Not** | Inverts the condition result |
| **Shorthand** | Simplified condition syntax |

### Condition Evaluation

```yaml
# Conditions are evaluated in order
# All must pass for actions to run (implicit AND)
condition:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  - condition: time
    after: "08:00:00"
    before: "22:00:00"
  # Both must be true
```

### Condition Location

```yaml
automation:
  - id: example
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    condition:
      # Conditions go here
      - condition: state
        entity_id: input_boolean.enabled
        state: "on"
    action:
      # Actions only run if conditions pass
      - service: light.turn_on
```

---

## State Condition

Check if an entity is in a specific state.

### Basic State Condition

```yaml
condition:
  - condition: state
    entity_id: light.living_room
    state: "on"
```

### Multiple States (OR)

```yaml
# Entity can be in any of these states
condition:
  - condition: state
    entity_id: vacuum.robot
    state:
      - cleaning
      - returning
```

### Multiple Entities (AND)

```yaml
# All entities must be in specified state
condition:
  - condition: state
    entity_id:
      - light.living_room
      - light.kitchen
    state: "off"
```

### State with Duration (for)

```yaml
# Entity must have been in state for duration
condition:
  - condition: state
    entity_id: binary_sensor.motion
    state: "off"
    for: "00:10:00"

# With dynamic duration
condition:
  - condition: state
    entity_id: binary_sensor.motion
    state: "off"
    for:
      minutes: "{{ states('input_number.timeout') | int }}"
```

### Attribute Check

```yaml
# Check entity attribute instead of state
condition:
  - condition: state
    entity_id: light.living_room
    attribute: brightness
    state: 255

# Multiple attribute values
condition:
  - condition: state
    entity_id: climate.thermostat
    attribute: hvac_action
    state:
      - heating
      - cooling
```

### Not Equal (match: any)

```yaml
# Using 'not' for "not equal" (deprecated in 2024.x)
# Use template condition or logic instead
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: disarmed
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Entity or list of entities |
| `state` | string/list | Expected state(s) |
| `attribute` | string | Attribute to check (optional) |
| `for` | time | Minimum duration in state |
| `match` | string | `all` (default) or `any` for multiple entities |

---

## Numeric State Condition

Check if a numeric value is above or below thresholds.

### Basic Numeric Condition

```yaml
# Value above threshold
condition:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 25

# Value below threshold
condition:
  - condition: numeric_state
    entity_id: sensor.temperature
    below: 18

# Value in range
condition:
  - condition: numeric_state
    entity_id: sensor.humidity
    above: 30
    below: 70
```

### With Attribute

```yaml
# Check attribute value
condition:
  - condition: numeric_state
    entity_id: light.living_room
    attribute: brightness
    above: 100
```

### Template Threshold

```yaml
# Dynamic threshold from helper
condition:
  - condition: numeric_state
    entity_id: sensor.battery
    below: "{{ states('input_number.low_battery_threshold') | int }}"
```

### Value Template

```yaml
# Apply template to entity value before comparison
condition:
  - condition: numeric_state
    entity_id: sensor.data
    value_template: "{{ state.state | float * 1.8 + 32 }}"
    above: 77  # Compare converted value
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Entity to check |
| `above` | number/template | Minimum value (exclusive) |
| `below` | number/template | Maximum value (exclusive) |
| `attribute` | string | Attribute to check |
| `value_template` | template | Transform value before comparison |

---

## Time Condition

Check if current time is within a range.

### Basic Time Range

```yaml
# Between 8 AM and 10 PM
condition:
  - condition: time
    after: "08:00:00"
    before: "22:00:00"
```

### Weekday Filter

```yaml
# Only on weekdays
condition:
  - condition: time
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri

# Only on weekends
condition:
  - condition: time
    weekday:
      - sat
      - sun
```

### Combined Time and Weekday

```yaml
# Weekdays between 7 AM and 9 AM
condition:
  - condition: time
    after: "07:00:00"
    before: "09:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
```

### Input Datetime as Time

```yaml
# Use input_datetime helper
condition:
  - condition: time
    after: input_datetime.quiet_hours_start
    before: input_datetime.quiet_hours_end
```

### Crossing Midnight

```yaml
# For times crossing midnight, use template
condition:
  - condition: template
    value_template: >
      {% set now_time = now().strftime('%H:%M:%S') %}
      {{ now_time >= '22:00:00' or now_time < '06:00:00' }}

# Or use two conditions with OR
condition:
  - condition: or
    conditions:
      - condition: time
        after: "22:00:00"
      - condition: time
        before: "06:00:00"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `after` | time/input_datetime | Start time (inclusive) |
| `before` | time/input_datetime | End time (exclusive) |
| `weekday` | list | Days of week (mon, tue, wed, thu, fri, sat, sun) |

---

## Sun Condition

Check position relative to sunrise/sunset.

### Basic Sun Condition

```yaml
# After sunset
condition:
  - condition: sun
    after: sunset

# Before sunrise
condition:
  - condition: sun
    before: sunrise

# Between sunset and sunrise (nighttime)
condition:
  - condition: sun
    after: sunset
    before: sunrise
```

### With Offset

```yaml
# 30 minutes after sunset
condition:
  - condition: sun
    after: sunset
    after_offset: "00:30:00"

# 1 hour before sunset
condition:
  - condition: sun
    before: sunset
    before_offset: "-01:00:00"

# Golden hour (1 hour before sunset)
condition:
  - condition: sun
    after: sunset
    after_offset: "-01:00:00"
    before: sunset
```

### Combined Example

```yaml
# Evening: after sunset but before midnight
condition:
  - condition: and
    conditions:
      - condition: sun
        after: sunset
      - condition: time
        before: "23:59:59"
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `after` | string | `sunrise` or `sunset` |
| `after_offset` | time | Offset from after time |
| `before` | string | `sunrise` or `sunset` |
| `before_offset` | time | Offset from before time |

---

## Zone Condition

Check if a person/device tracker is in a zone.

### Basic Zone Condition

```yaml
# Person is home
condition:
  - condition: zone
    entity_id: person.john
    zone: zone.home

# Device tracker in zone
condition:
  - condition: zone
    entity_id: device_tracker.phone
    zone: zone.work
```

### Multiple Entities

```yaml
# All family members home
condition:
  - condition: zone
    entity_id:
      - person.john
      - person.jane
    zone: zone.home
```

### Any Person in Zone

```yaml
# At least one person in zone
condition:
  - condition: or
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
      - condition: zone
        entity_id: person.jane
        zone: zone.home
```

### Not in Zone

```yaml
# Person is not home
condition:
  - condition: not
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `entity_id` | string/list | Person or device_tracker entity |
| `zone` | string | Zone entity (zone.home, zone.work, etc.) |

---

## Template Condition

Use Jinja2 templates for complex conditions.

### Basic Template

```yaml
# Simple comparison
condition:
  - condition: template
    value_template: "{{ states('sensor.temperature') | float > 25 }}"
```

### Complex Logic

```yaml
# Multiple conditions in template
condition:
  - condition: template
    value_template: >
      {{ is_state('binary_sensor.motion', 'on') and
         is_state('input_boolean.enabled', 'on') and
         states('sensor.illuminance') | float < 50 }}
```

### Using Trigger Variables

```yaml
# Access trigger data in condition
condition:
  - condition: template
    value_template: >
      {{ trigger.to_state.state != trigger.from_state.state }}
```

### Attribute Comparisons

```yaml
# Compare attributes
condition:
  - condition: template
    value_template: >
      {{ state_attr('climate.thermostat', 'current_temperature') | float >
         state_attr('climate.thermostat', 'temperature') | float }}
```

### Time-Based Logic

```yaml
# Complex time conditions
condition:
  - condition: template
    value_template: >
      {% set hour = now().hour %}
      {% set is_weekday = now().weekday() < 5 %}
      {{ (is_weekday and 7 <= hour < 22) or
         (not is_weekday and 9 <= hour < 23) }}
```

### Entity Availability

```yaml
# Check entity is available
condition:
  - condition: template
    value_template: >
      {{ states('sensor.temperature') not in ['unknown', 'unavailable'] }}
```

### Last Changed

```yaml
# Entity changed recently
condition:
  - condition: template
    value_template: >
      {{ (now() - states.binary_sensor.motion.last_changed).total_seconds() < 300 }}
```

### Count Matching Entities

```yaml
# At least 2 lights on
condition:
  - condition: template
    value_template: >
      {{ states.light | selectattr('state', 'eq', 'on') | list | count >= 2 }}
```

---

## Device Condition

Check device-specific conditions.

### Basic Device Condition

```yaml
# Device is on
condition:
  - condition: device
    device_id: abc123def456
    domain: light
    type: is_on
```

### Battery Level

```yaml
# Battery above threshold
condition:
  - condition: device
    device_id: abc123def456
    domain: sensor
    type: is_battery_level
    above: 20
```

### Common Device Types

```yaml
# Light is on
condition:
  - condition: device
    device_id: abc123def456
    domain: light
    type: is_on

# Switch is off
condition:
  - condition: device
    device_id: abc123def456
    domain: switch
    type: is_off

# Binary sensor is on
condition:
  - condition: device
    device_id: abc123def456
    domain: binary_sensor
    type: is_on
```

### All Options

| Option | Type | Description |
|--------|------|-------------|
| `device_id` | string | Device ID |
| `domain` | string | Entity domain |
| `type` | string | Condition type |
| `entity_id` | string | Entity (if device has multiple) |
| `above` / `below` | number | For numeric conditions |

---

## Trigger Condition

Check which trigger fired the automation.

### Basic Trigger Condition

```yaml
automation:
  - id: multi_trigger
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_living
        to: "on"
        id: living_room
      - platform: state
        entity_id: binary_sensor.motion_kitchen
        to: "on"
        id: kitchen
    condition:
      - condition: trigger
        id: living_room
    action:
      # Only runs for living room trigger
```

### Multiple Trigger IDs

```yaml
condition:
  - condition: trigger
    id:
      - morning_trigger
      - evening_trigger
```

### In Choose Block

```yaml
action:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_detected
        sequence:
          - service: light.turn_on
      - conditions:
          - condition: trigger
            id: motion_cleared
        sequence:
          - service: light.turn_off
```

---

## Logical Conditions

Combine conditions with AND, OR, NOT logic.

### AND Condition

```yaml
# All conditions must be true (explicit)
condition:
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.enabled
        state: "on"
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
      - condition: numeric_state
        entity_id: sensor.temperature
        below: 25
```

### OR Condition

```yaml
# At least one condition must be true
condition:
  - condition: or
    conditions:
      - condition: state
        entity_id: binary_sensor.motion_living
        state: "on"
      - condition: state
        entity_id: binary_sensor.motion_kitchen
        state: "on"
```

### NOT Condition

```yaml
# Inverts the condition result
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: alarm_control_panel.home
        state: armed_away
```

### Nested Logic

```yaml
# Complex nested conditions
condition:
  - condition: and
    conditions:
      # Must be enabled
      - condition: state
        entity_id: input_boolean.enabled
        state: "on"
      # AND either daytime OR motion detected
      - condition: or
        conditions:
          - condition: sun
            after: sunrise
            before: sunset
          - condition: state
            entity_id: binary_sensor.motion
            state: "on"
```

### Implicit AND

```yaml
# Multiple conditions at root level are implicitly ANDed
condition:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  - condition: time
    after: "08:00:00"
# Both must be true
```

---

## Shorthand Conditions

Simplified syntax for common conditions.

### Shorthand State

```yaml
# Full syntax
condition:
  - condition: state
    entity_id: light.living_room
    state: "on"

# Shorthand
condition:
  - "{{ is_state('light.living_room', 'on') }}"
```

### Shorthand Numeric

```yaml
# Full syntax
condition:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 25

# Shorthand
condition:
  - "{{ states('sensor.temperature') | float > 25 }}"
```

### Shorthand OR

```yaml
# Full syntax
condition:
  - condition: or
    conditions:
      - condition: state
        entity_id: light.a
        state: "on"
      - condition: state
        entity_id: light.b
        state: "on"

# Shorthand
condition:
  - "{{ is_state('light.a', 'on') or is_state('light.b', 'on') }}"
```

### Mixed Syntax

```yaml
# Can mix full and shorthand
condition:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  - "{{ now().hour >= 8 }}"
```

---

## Common Patterns

### Someone Home

```yaml
# At least one person home
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: group.family
        state: not_home

# Or using zone
condition:
  - condition: or
    conditions:
      - condition: zone
        entity_id: person.john
        zone: zone.home
      - condition: zone
        entity_id: person.jane
        zone: zone.home
```

### Nobody Home

```yaml
condition:
  - condition: state
    entity_id: group.family
    state: not_home
```

### Dark Outside

```yaml
# After sunset
condition:
  - condition: sun
    after: sunset
    before: sunrise

# Or low illuminance
condition:
  - condition: numeric_state
    entity_id: sensor.outdoor_illuminance
    below: 50
```

### Quiet Hours

```yaml
# Using time condition
condition:
  - condition: time
    after: "22:00:00"
    before: "07:00:00"

# Using input_datetime
condition:
  - condition: time
    after: input_datetime.quiet_start
    before: input_datetime.quiet_end

# Using schedule helper
condition:
  - condition: state
    entity_id: schedule.quiet_hours
    state: "on"
```

### Automation Not Recently Run

```yaml
condition:
  - condition: template
    value_template: >
      {{ (now() - state_attr('automation.door_notification', 'last_triggered')).total_seconds() > 1800 }}
```

### Entity Available

```yaml
condition:
  - condition: template
    value_template: >
      {{ states('sensor.temperature') not in ['unknown', 'unavailable', 'none'] }}
```

### Workday Check

```yaml
# Using workday integration
condition:
  - condition: state
    entity_id: binary_sensor.workday
    state: "on"
```

### Rate Limiting

```yaml
# With counter
condition:
  - condition: numeric_state
    entity_id: counter.daily_notifications
    below: 10

# With timer cooldown
condition:
  - condition: state
    entity_id: timer.notification_cooldown
    state: "idle"
```

### Mode-Based Conditions

```yaml
# Check input_select mode
condition:
  - condition: state
    entity_id: input_select.home_mode
    state:
      - Home
      - Guest

# Not in certain modes
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: input_select.home_mode
        state:
          - Away
          - Vacation
```

---

## Best Practices

### Order Conditions Efficiently

```yaml
# Put fast/cheap conditions first
condition:
  # Boolean check is fast
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  # Then time check
  - condition: time
    after: "08:00:00"
  # Template checks last (more expensive)
  - condition: template
    value_template: "{{ complex_calculation }}"
```

### Use Appropriate Condition Type

```yaml
# Use state for simple state checks
condition:
  - condition: state
    entity_id: light.lamp
    state: "on"  # Good

# Don't use template for simple checks
condition:
  - condition: template
    value_template: "{{ is_state('light.lamp', 'on') }}"  # Unnecessary
```

### Handle Edge Cases

```yaml
# Always handle unavailable states
condition:
  - condition: template
    value_template: >
      {{ states('sensor.temperature') not in ['unknown', 'unavailable'] and
         states('sensor.temperature') | float > 25 }}
```

### Document Complex Conditions

```yaml
condition:
  # Only proceed if:
  # - Automation is enabled by user
  # - It's during active hours
  # - Not in vacation mode
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.automation_enabled
        state: "on"
      - condition: time
        after: "07:00:00"
        before: "23:00:00"
      - condition: state
        entity_id: input_boolean.vacation_mode
        state: "off"
```

### Test Conditions

```yaml
# Test in Developer Tools > Template
{{ is_state('input_boolean.test', 'on') and
   is_state('binary_sensor.motion', 'on') }}
```

---

## Troubleshooting

### Condition Never Passes

| Problem | Cause | Solution |
|---------|-------|----------|
| State mismatch | State is string | Quote values: `state: "on"` not `state: on` |
| Entity unavailable | Entity not ready | Add availability check |
| Time zone issue | Wrong time zone | Check HA time zone config |
| Attribute check fails | Wrong attribute name | Check entity attributes |

### Debug Conditions

```yaml
# Add logging to trace condition evaluation
automation:
  - id: debug_condition
    trigger:
      - platform: state
        entity_id: binary_sensor.test
    action:
      - service: system_log.write
        data:
          message: >
            Conditions met! States:
            - enabled: {{ states('input_boolean.enabled') }}
            - motion: {{ states('binary_sensor.motion') }}
          level: info
```

### Check Condition in Template

```yaml
# Developer Tools > Template
# Test your condition logic

{% set enabled = is_state('input_boolean.enabled', 'on') %}
{% set motion = is_state('binary_sensor.motion', 'on') %}
{% set dark = states('sensor.illuminance') | float < 50 %}

enabled: {{ enabled }}
motion: {{ motion }}
dark: {{ dark }}
all conditions: {{ enabled and motion and dark }}
```

### Common Mistakes

```yaml
# Wrong: state without quotes for "on"/"off"
condition:
  - condition: state
    entity_id: switch.test
    state: on  # YAML interprets as boolean True

# Correct: quoted string
condition:
  - condition: state
    entity_id: switch.test
    state: "on"

# Wrong: above/below are exclusive
condition:
  - condition: numeric_state
    entity_id: sensor.temp
    above: 25  # Means > 25, not >= 25

# Wrong: time crossing midnight
condition:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"  # This NEVER matches!

# Correct: use OR for midnight crossing
condition:
  - condition: or
    conditions:
      - condition: time
        after: "22:00:00"
      - condition: time
        before: "06:00:00"
```

### Trace Analysis

```yaml
# Check automation trace in UI
# Settings > Automations > (automation) > Traces

# Trace shows:
# - Trigger that fired
# - Each condition and result
# - Actions executed

# Failed condition shows:
# Result: false
# Reason: State is 'off', expected 'on'
```
