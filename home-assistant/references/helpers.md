# Home Assistant Helpers Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Input Boolean](#input-boolean)
- [Input Number](#input-number)
- [Input Select](#input-select)
- [Input Text](#input-text)
- [Input Datetime](#input-datetime)
- [Input Button](#input-button)
- [Counter](#counter)
- [Timer](#timer)
- [Schedule](#schedule)
- [Group Helpers](#group-helpers)
- [Using Helpers in Automations](#using-helpers-in-automations)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Helpers are entities you create to store and manage values that control your automations. They persist across restarts and can be modified via the UI, automations, or services.

### Key Terms

| Term | Description |
|------|-------------|
| **Helper** | User-created entity for storing values |
| **Input** | Prefix for user-editable helper types |
| **State** | Current value of the helper |
| **Attributes** | Additional metadata on the helper |
| **Service** | Method to modify helper value |

### Helper Types Overview

| Type | Entity Prefix | Use Case |
|------|---------------|----------|
| Input Boolean | `input_boolean.` | On/off toggles, modes |
| Input Number | `input_number.` | Numeric values, thresholds |
| Input Select | `input_select.` | Dropdown options, modes |
| Input Text | `input_text.` | Text values, messages |
| Input Datetime | `input_datetime.` | Date/time values |
| Input Button | `input_button.` | Trigger events |
| Counter | `counter.` | Count events, iterations |
| Timer | `timer.` | Countdowns, durations |
| Schedule | `schedule.` | Weekly schedules |

### Creating Helpers

**Via UI:** Settings > Devices & Services > Helpers > Create Helper

**Via YAML:**
```yaml
# configuration.yaml or included file
input_boolean:
  vacation_mode:
    name: Vacation Mode
    icon: mdi:airplane
```

---

## Input Boolean

Toggle switches for on/off states.

### Basic Configuration

```yaml
input_boolean:
  vacation_mode:
    name: Vacation Mode
    icon: mdi:airplane

  guest_mode:
    name: Guest Mode
    icon: mdi:account-multiple
    initial: false

  automation_enabled:
    name: Automations Enabled
    icon: mdi:robot
    initial: true
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `icon` | string | mdi:toggle-switch | MDI icon |
| `initial` | boolean | none | Initial state on HA start (if no restore) |

### Services

```yaml
# Turn on
service: input_boolean.turn_on
target:
  entity_id: input_boolean.vacation_mode

# Turn off
service: input_boolean.turn_off
target:
  entity_id: input_boolean.vacation_mode

# Toggle
service: input_boolean.toggle
target:
  entity_id: input_boolean.vacation_mode
```

### State Values

```yaml
# States: "on" or "off"
condition:
  - condition: state
    entity_id: input_boolean.vacation_mode
    state: "on"
```

### Common Use Cases

```yaml
# Mode toggles
input_boolean:
  away_mode:
    name: Away Mode
  night_mode:
    name: Night Mode
  party_mode:
    name: Party Mode

# Feature toggles
input_boolean:
  motion_lights_enabled:
    name: Motion Lights
  notifications_enabled:
    name: Notifications
  climate_schedule_enabled:
    name: Climate Schedule
```

---

## Input Number

Store numeric values with defined ranges.

### Basic Configuration

```yaml
input_number:
  target_temperature:
    name: Target Temperature
    min: 15
    max: 28
    step: 0.5
    unit_of_measurement: "°C"
    icon: mdi:thermometer

  motion_timeout:
    name: Motion Timeout
    min: 1
    max: 60
    step: 1
    unit_of_measurement: "min"
    mode: slider
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `min` | float | 0 | Minimum value |
| `max` | float | 100 | Maximum value |
| `step` | float | 1 | Step increment |
| `initial` | float | none | Initial value |
| `unit_of_measurement` | string | none | Unit label |
| `mode` | string | slider | `slider` or `box` |
| `icon` | string | mdi:ray-vertex | MDI icon |

### Services

```yaml
# Set value
service: input_number.set_value
target:
  entity_id: input_number.target_temperature
data:
  value: 22.5

# Increment
service: input_number.increment
target:
  entity_id: input_number.target_temperature

# Decrement
service: input_number.decrement
target:
  entity_id: input_number.target_temperature
```

### Using in Templates

```yaml
# Get value as float
{{ states('input_number.target_temperature') | float }}

# Use in automation
action:
  - service: climate.set_temperature
    target:
      entity_id: climate.living_room
    data:
      temperature: "{{ states('input_number.target_temperature') | float }}"
```

### Common Use Cases

```yaml
input_number:
  # Thresholds
  low_battery_threshold:
    name: Low Battery Alert
    min: 0
    max: 100
    step: 5
    unit_of_measurement: "%"
    initial: 20

  # Timeouts
  light_timeout_minutes:
    name: Light Timeout
    min: 1
    max: 120
    step: 1
    unit_of_measurement: "min"

  # Brightness levels
  night_brightness:
    name: Night Brightness
    min: 0
    max: 100
    step: 5
    unit_of_measurement: "%"
    mode: slider
```

---

## Input Select

Dropdown selection from predefined options.

### Basic Configuration

```yaml
input_select:
  home_mode:
    name: Home Mode
    options:
      - Home
      - Away
      - Night
      - Vacation
      - Guest
    initial: Home
    icon: mdi:home

  climate_preset:
    name: Climate Preset
    options:
      - Comfort
      - Eco
      - Away
      - Sleep
    icon: mdi:thermostat
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `options` | list | required | List of options |
| `initial` | string | first option | Initial selection |
| `icon` | string | mdi:format-list-bulleted | MDI icon |

### Services

```yaml
# Select option
service: input_select.select_option
target:
  entity_id: input_select.home_mode
data:
  option: Away

# Select first option
service: input_select.select_first
target:
  entity_id: input_select.home_mode

# Select last option
service: input_select.select_last
target:
  entity_id: input_select.home_mode

# Select next option (cycles)
service: input_select.select_next
target:
  entity_id: input_select.home_mode
data:
  cycle: true  # Wrap around at end

# Select previous option
service: input_select.select_previous
target:
  entity_id: input_select.home_mode

# Set options dynamically
service: input_select.set_options
target:
  entity_id: input_select.playlist
data:
  options:
    - "{{ states('sensor.playlist_1') }}"
    - "{{ states('sensor.playlist_2') }}"
```

### Using in Automations

```yaml
# Trigger on selection change
automation:
  - id: home_mode_changed
    alias: Home Mode Changed
    trigger:
      - platform: state
        entity_id: input_select.home_mode
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: input_select.home_mode
                state: Away
            sequence:
              - service: script.turn_on
                target:
                  entity_id: script.away_mode
          - conditions:
              - condition: state
                entity_id: input_select.home_mode
                state: Night
            sequence:
              - service: script.turn_on
                target:
                  entity_id: script.night_mode
```

### Common Use Cases

```yaml
input_select:
  # Lighting scenes
  lighting_scene:
    name: Lighting Scene
    options:
      - Bright
      - Relaxed
      - Movie
      - Romantic
      - "Off"

  # Who's home
  who_is_home:
    name: Who's Home
    options:
      - Nobody
      - Adults Only
      - Kids Only
      - Everyone

  # Alarm states
  alarm_mode:
    name: Alarm Mode
    options:
      - Disarmed
      - Armed Home
      - Armed Away
      - Armed Night
```

---

## Input Text

Store text values.

### Basic Configuration

```yaml
input_text:
  notification_message:
    name: Notification Message
    initial: "Welcome home!"
    max: 255

  guest_wifi_password:
    name: Guest WiFi Password
    mode: password
    max: 64

  current_activity:
    name: Current Activity
    pattern: "[a-zA-Z0-9 ]+"
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `initial` | string | none | Initial value |
| `min` | integer | 0 | Minimum length |
| `max` | integer | 100 | Maximum length |
| `pattern` | string | none | Regex validation pattern |
| `mode` | string | text | `text` or `password` |
| `icon` | string | mdi:form-textbox | MDI icon |

### Services

```yaml
# Set value
service: input_text.set_value
target:
  entity_id: input_text.notification_message
data:
  value: "Goodnight!"
```

### Using in Automations

```yaml
# Use text in notification
action:
  - service: notify.mobile_app
    data:
      title: "Home Assistant"
      message: "{{ states('input_text.notification_message') }}"

# Dynamic message
action:
  - service: input_text.set_value
    target:
      entity_id: input_text.current_activity
    data:
      value: >
        {{ trigger.to_state.attributes.friendly_name }}
        changed to {{ trigger.to_state.state }}
```

### Common Use Cases

```yaml
input_text:
  # Custom messages
  away_message:
    name: Away Message
    initial: "Nobody home"
    max: 100

  # Dynamic content
  last_motion_location:
    name: Last Motion
    max: 50

  # User input for automations
  tts_message:
    name: TTS Message
    max: 255
```

---

## Input Datetime

Store date, time, or datetime values.

### Basic Configuration

```yaml
input_datetime:
  # Time only
  morning_alarm:
    name: Morning Alarm
    has_date: false
    has_time: true

  # Date only
  vacation_start:
    name: Vacation Start
    has_date: true
    has_time: false

  # Full datetime
  next_appointment:
    name: Next Appointment
    has_date: true
    has_time: true
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `has_date` | boolean | true | Include date component |
| `has_time` | boolean | true | Include time component |
| `initial` | string | none | Initial value (format depends on type) |
| `icon` | string | mdi:calendar-clock | MDI icon |

### Initial Value Formats

```yaml
input_datetime:
  # Time only: "HH:MM:SS" or "HH:MM"
  wake_time:
    has_date: false
    has_time: true
    initial: "07:00:00"

  # Date only: "YYYY-MM-DD"
  birthday:
    has_date: true
    has_time: false
    initial: "2024-01-15"

  # Datetime: "YYYY-MM-DD HH:MM:SS"
  event_start:
    has_date: true
    has_time: true
    initial: "2024-01-15 10:00:00"
```

### Services

```yaml
# Set datetime
service: input_datetime.set_datetime
target:
  entity_id: input_datetime.morning_alarm
data:
  time: "07:30:00"

# Set with date
service: input_datetime.set_datetime
target:
  entity_id: input_datetime.vacation_start
data:
  date: "2024-06-15"

# Set full datetime
service: input_datetime.set_datetime
target:
  entity_id: input_datetime.next_appointment
data:
  datetime: "2024-06-15 14:30:00"

# Set from timestamp
service: input_datetime.set_datetime
target:
  entity_id: input_datetime.last_event
data:
  timestamp: "{{ as_timestamp(now()) }}"
```

### Using in Automations

```yaml
# Trigger at input time
automation:
  - id: morning_alarm
    alias: Morning Alarm
    trigger:
      - platform: time
        at: input_datetime.morning_alarm
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom

# Check if date is today
condition:
  - condition: template
    value_template: >
      {{ states('input_datetime.vacation_start') == now().strftime('%Y-%m-%d') }}
```

### Attributes

```yaml
# Available attributes for datetime
{{ state_attr('input_datetime.next_appointment', 'year') }}
{{ state_attr('input_datetime.next_appointment', 'month') }}
{{ state_attr('input_datetime.next_appointment', 'day') }}
{{ state_attr('input_datetime.next_appointment', 'hour') }}
{{ state_attr('input_datetime.next_appointment', 'minute') }}
{{ state_attr('input_datetime.next_appointment', 'second') }}
{{ state_attr('input_datetime.next_appointment', 'timestamp') }}
```

---

## Input Button

Stateless buttons that trigger events when pressed.

### Basic Configuration

```yaml
input_button:
  restart_router:
    name: Restart Router
    icon: mdi:restart

  run_vacuum:
    name: Run Vacuum
    icon: mdi:robot-vacuum

  trigger_backup:
    name: Trigger Backup
    icon: mdi:backup-restore
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `icon` | string | mdi:button-pointer | MDI icon |

### Services

```yaml
# Press button
service: input_button.press
target:
  entity_id: input_button.restart_router
```

### Using in Automations

```yaml
# Trigger when button pressed
automation:
  - id: button_restart_router
    alias: Restart Router Button
    trigger:
      - platform: state
        entity_id: input_button.restart_router
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.router_power
      - delay: "00:00:10"
      - service: switch.turn_on
        target:
          entity_id: switch.router_power
```

### State

```yaml
# State is timestamp of last press
{{ states('input_button.restart_router') }}
# Returns: "2024-01-15T10:30:00.000000+00:00"

# Check if pressed recently
{{ as_timestamp(now()) - as_timestamp(states('input_button.run_vacuum')) < 3600 }}
```

---

## Counter

Count events or iterations.

### Basic Configuration

```yaml
counter:
  coffee_count:
    name: Coffee Today
    initial: 0
    step: 1
    minimum: 0
    maximum: 20
    icon: mdi:coffee

  laundry_loads:
    name: Laundry Loads This Week
    initial: 0
    step: 1
    restore: true
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `initial` | integer | 0 | Initial value (and reset value) |
| `step` | integer | 1 | Increment/decrement amount |
| `minimum` | integer | none | Minimum value |
| `maximum` | integer | none | Maximum value |
| `restore` | boolean | true | Restore value after restart |
| `icon` | string | mdi:counter | MDI icon |

### Services

```yaml
# Increment
service: counter.increment
target:
  entity_id: counter.coffee_count

# Decrement
service: counter.decrement
target:
  entity_id: counter.coffee_count

# Reset to initial
service: counter.reset
target:
  entity_id: counter.coffee_count

# Set specific value
service: counter.set_value
target:
  entity_id: counter.coffee_count
data:
  value: 5
```

### Using in Automations

```yaml
# Count door openings
automation:
  - id: count_door_open
    alias: Count Door Openings
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: counter.increment
        target:
          entity_id: counter.door_openings

# Reset daily
automation:
  - id: reset_daily_counters
    alias: Reset Daily Counters
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: counter.reset
        target:
          entity_id:
            - counter.coffee_count
            - counter.door_openings
```

### Common Use Cases

```yaml
counter:
  # Activity tracking
  workout_count:
    name: Workouts This Week
    maximum: 14

  # Usage tracking
  washing_machine_cycles:
    name: Wash Cycles

  # Error counting
  failed_login_attempts:
    name: Failed Logins
    maximum: 5
```

---

## Timer

Countdown and count-up timers.

### Basic Configuration

```yaml
timer:
  laundry:
    name: Laundry Timer
    duration: "01:00:00"
    icon: mdi:washing-machine

  motion_cooldown:
    name: Motion Cooldown
    duration: "00:05:00"

  cooking:
    name: Cooking Timer
    duration: "00:30:00"
    restore: true
```

### All Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | entity_id | Friendly name |
| `duration` | time | 0 | Default duration (HH:MM:SS) |
| `restore` | boolean | false | Continue after restart |
| `icon` | string | mdi:timer | MDI icon |

### Services

```yaml
# Start timer (uses default duration)
service: timer.start
target:
  entity_id: timer.laundry

# Start with custom duration
service: timer.start
target:
  entity_id: timer.cooking
data:
  duration: "00:45:00"

# Pause timer
service: timer.pause
target:
  entity_id: timer.laundry

# Cancel timer
service: timer.cancel
target:
  entity_id: timer.laundry

# Finish timer (triggers finished event)
service: timer.finish
target:
  entity_id: timer.laundry

# Change duration while running
service: timer.change
target:
  entity_id: timer.laundry
data:
  duration: "00:10:00"  # Add/remove time
```

### Timer States

| State | Description |
|-------|-------------|
| `idle` | Timer not running |
| `active` | Timer counting down |
| `paused` | Timer paused |

### Timer Events

```yaml
# Trigger when timer finishes
automation:
  - id: laundry_done
    alias: Laundry Done Notification
    trigger:
      - platform: event
        event_type: timer.finished
        event_data:
          entity_id: timer.laundry
    action:
      - service: notify.mobile_app
        data:
          title: "Laundry"
          message: "Laundry is done!"

# Trigger on timer started
trigger:
  - platform: event
    event_type: timer.started
    event_data:
      entity_id: timer.cooking

# Trigger on timer cancelled
trigger:
  - platform: event
    event_type: timer.cancelled
    event_data:
      entity_id: timer.cooking
```

### Timer Attributes

```yaml
# Get remaining time
{{ state_attr('timer.laundry', 'remaining') }}
# Returns: "0:45:30" when active

# Get duration
{{ state_attr('timer.laundry', 'duration') }}

# Get finish time (when active)
{{ state_attr('timer.laundry', 'finishes_at') }}
```

### Common Use Cases

```yaml
timer:
  # Appliance timers
  dishwasher:
    duration: "01:30:00"
  dryer:
    duration: "00:45:00"

  # Automation cooldowns
  notification_cooldown:
    duration: "00:30:00"

  # Activity timers
  exercise:
    duration: "00:30:00"
    restore: true
```

---

## Schedule

Weekly on/off schedules.

### Basic Configuration

```yaml
schedule:
  thermostat_schedule:
    name: Thermostat Schedule
    monday:
      - from: "06:00:00"
        to: "08:00:00"
      - from: "17:00:00"
        to: "22:00:00"
    tuesday:
      - from: "06:00:00"
        to: "08:00:00"
      - from: "17:00:00"
        to: "22:00:00"
    # ... other days
    icon: mdi:calendar-clock
```

### Full Week Example

```yaml
schedule:
  work_hours:
    name: Work Hours
    monday:
      - from: "09:00:00"
        to: "17:00:00"
    tuesday:
      - from: "09:00:00"
        to: "17:00:00"
    wednesday:
      - from: "09:00:00"
        to: "17:00:00"
    thursday:
      - from: "09:00:00"
        to: "17:00:00"
    friday:
      - from: "09:00:00"
        to: "17:00:00"
    saturday: []  # Empty = off all day
    sunday: []
```

### Multiple Time Blocks

```yaml
schedule:
  lighting_schedule:
    name: Lighting Schedule
    monday:
      - from: "06:00:00"
        to: "08:00:00"
      - from: "12:00:00"
        to: "13:00:00"
      - from: "18:00:00"
        to: "23:00:00"
```

### State Values

```yaml
# State is "on" when within schedule, "off" otherwise
condition:
  - condition: state
    entity_id: schedule.work_hours
    state: "on"
```

### Using in Automations

```yaml
# Condition based on schedule
automation:
  - id: heating_schedule
    alias: Heating Schedule
    trigger:
      - platform: state
        entity_id: schedule.thermostat_schedule
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: schedule.thermostat_schedule
                state: "on"
            sequence:
              - service: climate.set_preset_mode
                target:
                  entity_id: climate.living_room
                data:
                  preset_mode: comfort
          - conditions:
              - condition: state
                entity_id: schedule.thermostat_schedule
                state: "off"
            sequence:
              - service: climate.set_preset_mode
                target:
                  entity_id: climate.living_room
                data:
                  preset_mode: eco
```

---

## Group Helpers

Group related helpers for easier management.

### Grouping Input Booleans

```yaml
group:
  automation_controls:
    name: Automation Controls
    entities:
      - input_boolean.motion_lights_enabled
      - input_boolean.notifications_enabled
      - input_boolean.climate_schedule_enabled
```

### Template for Helper Status

```yaml
template:
  - sensor:
      - name: "Active Modes"
        state: >
          {% set modes = [] %}
          {% if is_state('input_boolean.vacation_mode', 'on') %}
            {% set modes = modes + ['Vacation'] %}
          {% endif %}
          {% if is_state('input_boolean.guest_mode', 'on') %}
            {% set modes = modes + ['Guest'] %}
          {% endif %}
          {% if is_state('input_boolean.night_mode', 'on') %}
            {% set modes = modes + ['Night'] %}
          {% endif %}
          {{ modes | join(', ') if modes else 'Normal' }}
```

---

## Using Helpers in Automations

### As Trigger

```yaml
trigger:
  # Boolean changed
  - platform: state
    entity_id: input_boolean.vacation_mode
    to: "on"

  # Select changed to specific value
  - platform: state
    entity_id: input_select.home_mode
    to: "Away"

  # Number crossed threshold
  - platform: numeric_state
    entity_id: input_number.target_temperature
    above: 25

  # At input time
  - platform: time
    at: input_datetime.morning_alarm

  # Timer finished
  - platform: event
    event_type: timer.finished
    event_data:
      entity_id: timer.laundry

  # Button pressed
  - platform: state
    entity_id: input_button.run_vacuum

  # Schedule became active
  - platform: state
    entity_id: schedule.work_hours
    to: "on"
```

### As Condition

```yaml
condition:
  # Boolean is on
  - condition: state
    entity_id: input_boolean.notifications_enabled
    state: "on"

  # Select is specific value
  - condition: state
    entity_id: input_select.home_mode
    state: "Home"

  # Number in range
  - condition: numeric_state
    entity_id: input_number.brightness
    above: 50
    below: 100

  # Within schedule
  - condition: state
    entity_id: schedule.quiet_hours
    state: "off"

  # Timer not running
  - condition: state
    entity_id: timer.cooldown
    state: "idle"
```

### As Action Data

```yaml
action:
  # Use number value
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: "{{ states('input_number.brightness') | int }}"

  # Use text value
  - service: notify.mobile_app
    data:
      message: "{{ states('input_text.welcome_message') }}"

  # Use datetime
  - service: input_datetime.set_datetime
    target:
      entity_id: input_datetime.last_run
    data:
      timestamp: "{{ as_timestamp(now()) }}"

  # Use select value
  - service: scene.turn_on
    target:
      entity_id: "scene.{{ states('input_select.lighting_scene') | lower | replace(' ', '_') }}"
```

---

## Common Patterns

### Mode-Based Automation Control

```yaml
input_select:
  home_mode:
    name: Home Mode
    options:
      - Home
      - Away
      - Night
      - Vacation

automation:
  - id: mode_based_lights
    alias: Mode-Based Lighting
    trigger:
      - platform: state
        entity_id: input_select.home_mode
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: input_select.home_mode
                state: Away
            sequence:
              - service: light.turn_off
                target:
                  entity_id: all
          - conditions:
              - condition: state
                entity_id: input_select.home_mode
                state: Night
            sequence:
              - service: light.turn_off
                target:
                  area_id: living_room
              - service: light.turn_on
                target:
                  entity_id: light.hallway_night
                data:
                  brightness_pct: 10
```

### Configurable Timeouts

```yaml
input_number:
  motion_timeout:
    name: Motion Light Timeout
    min: 1
    max: 30
    step: 1
    unit_of_measurement: "min"
    initial: 5

automation:
  - id: motion_light
    alias: Motion Light
    mode: restart
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
      - delay:
          minutes: "{{ states('input_number.motion_timeout') | int }}"
      - service: light.turn_off
        target:
          entity_id: light.hallway
```

### Notification Cooldown

```yaml
timer:
  notification_cooldown:
    duration: "00:30:00"

automation:
  - id: door_notification
    alias: Door Left Open
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
        for: "00:10:00"
    condition:
      - condition: state
        entity_id: timer.notification_cooldown
        state: "idle"
    action:
      - service: notify.mobile_app
        data:
          message: "Front door has been open for 10 minutes"
      - service: timer.start
        target:
          entity_id: timer.notification_cooldown
```

### Daily Counter Reset

```yaml
counter:
  daily_notifications:
    name: Notifications Today
    initial: 0

automation:
  - id: reset_daily_counter
    alias: Reset Daily Counter
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: counter.reset
        target:
          entity_id: counter.daily_notifications
```

### User-Adjustable Schedules

```yaml
input_datetime:
  weekday_wake:
    name: Weekday Wake Time
    has_time: true
    has_date: false
  weekend_wake:
    name: Weekend Wake Time
    has_time: true
    has_date: false

automation:
  - id: wake_up_routine
    alias: Wake Up Routine
    trigger:
      - platform: time
        at: input_datetime.weekday_wake
        id: weekday
      - platform: time
        at: input_datetime.weekend_wake
        id: weekend
    condition:
      - condition: or
        conditions:
          - condition: and
            conditions:
              - condition: trigger
                id: weekday
              - condition: time
                weekday:
                  - mon
                  - tue
                  - wed
                  - thu
                  - fri
          - condition: and
            conditions:
              - condition: trigger
                id: weekend
              - condition: time
                weekday:
                  - sat
                  - sun
    action:
      - service: script.turn_on
        target:
          entity_id: script.wake_up_routine
```

---

## Best Practices

### Naming Conventions

```yaml
# Use descriptive names
input_boolean:
  motion_lights_enabled:        # Good - describes purpose
    name: Motion Lights Enabled
  ml_en:                        # Bad - unclear
    name: ML EN

# Prefix by function
input_number:
  threshold_low_battery:        # Good - grouped by type
  threshold_temperature_high:
  timeout_motion_light:
  timeout_door_notification:

# Use consistent patterns
input_select:
  mode_home:                    # Consistent prefix
  mode_climate:
  mode_lighting:
```

### Default Values

```yaml
# Always set sensible defaults
input_number:
  brightness:
    initial: 80               # Users expect a reasonable default
    min: 0
    max: 100

input_boolean:
  notifications_enabled:
    initial: true             # Enable by default for safety features

input_select:
  home_mode:
    initial: Home             # Safe default state
```

### Grouping Related Helpers

```yaml
# Create packages for related helpers
# packages/climate_control.yaml

input_number:
  climate_target_temp_day:
    name: Day Temperature
  climate_target_temp_night:
    name: Night Temperature

input_boolean:
  climate_schedule_enabled:
    name: Climate Schedule

input_datetime:
  climate_day_start:
    name: Day Start Time
  climate_night_start:
    name: Night Start Time

automation:
  - id: pkg_climate_schedule
    # ... automation using above helpers
```

### Documentation

```yaml
# Add comments explaining purpose
input_boolean:
  # Master switch for all motion-activated lights
  # Useful for disabling during parties or maintenance
  motion_lights_enabled:
    name: Motion Lights
    icon: mdi:motion-sensor

input_number:
  # Threshold in lux below which lights should activate
  # Adjust based on room and sensor placement
  illuminance_threshold:
    name: Light Threshold
    min: 0
    max: 500
    unit_of_measurement: "lx"
```

---

## Troubleshooting

### Helper Not Saving Value

| Problem | Cause | Solution |
|---------|-------|----------|
| Value resets on restart | `restore: false` | Set `restore: true` or remove (true is default) |
| Value not updating | Service call error | Check service data and entity_id |
| Initial value ignored | Restored value takes precedence | Delete `.storage/core.restore_state` to reset |

### Timer Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Timer not starting | Duration is 0 | Set duration in config or service call |
| Timer stops on restart | `restore: false` | Set `restore: true` |
| finish event not firing | Timer cancelled | Use `timer.finish` instead of `timer.cancel` |

### Counter Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Counter won't increment | At maximum | Increase or remove `maximum` |
| Counter won't decrement | At minimum | Decrease or remove `minimum` |
| Counter resets unexpectedly | `restore: false` | Set `restore: true` |

### Schedule Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Schedule always off | No time blocks defined | Add time blocks for each day |
| Schedule not updating | State not changing | Check time blocks don't overlap midnight |

### Debug Helper States

```yaml
# Log helper changes
automation:
  - id: debug_helper_changes
    alias: Debug Helper Changes
    trigger:
      - platform: state
        entity_id:
          - input_boolean.test_helper
          - input_number.test_helper
    action:
      - service: system_log.write
        data:
          message: >
            Helper {{ trigger.entity_id }} changed from
            {{ trigger.from_state.state }} to {{ trigger.to_state.state }}
          level: info
```

### Check Helper Services

```yaml
# Test in Developer Tools > Services
service: input_boolean.turn_on
data: {}
target:
  entity_id: input_boolean.test

# Verify state in Developer Tools > States
# Filter by "input_" to see all helpers
```
