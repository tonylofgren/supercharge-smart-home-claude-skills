# Home Assistant Scripts Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Script Structure](#script-structure)
- [Script Modes](#script-modes)
- [Fields (Input Parameters)](#fields-input-parameters)
- [Response Variables](#response-variables)
- [All Action Types](#all-action-types)
- [Calling Scripts](#calling-scripts)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Scripts are reusable sequences of actions that can be called from automations, other scripts, or manually. Unlike automations, scripts don't have triggers—they run when explicitly called.

### Scripts vs Automations

| Feature | Scripts | Automations |
|---------|---------|-------------|
| Triggers | No | Yes |
| Callable | Yes | Yes (but less common) |
| Parameters | Yes (fields) | No |
| Return values | Yes | No |
| Reusability | High | Medium |
| Use case | Actions to call | Event responses |

---

## Script Structure

### Basic Script

```yaml
script:
  turn_on_morning_lights:
    alias: "Turn On Morning Lights"
    description: "Gradually turn on lights for morning routine"
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 30
          transition: 60
```

### Complete Script Structure

```yaml
script:
  example_script:
    alias: "Example Script"
    description: "A complete example script"
    icon: mdi:script-text
    mode: single
    max: 10
    max_exceeded: warning

    # Input parameters
    fields:
      target_light:
        description: "Light to control"
        required: true
        selector:
          entity:
            domain: light
      brightness:
        description: "Brightness level"
        default: 100
        selector:
          number:
            min: 0
            max: 100

    # Local variables
    variables:
      transition_time: 2

    # Actions to perform
    sequence:
      - service: light.turn_on
        target:
          entity_id: "{{ target_light }}"
        data:
          brightness_pct: "{{ brightness }}"
          transition: "{{ transition_time }}"
```

### Script Properties

| Property | Required | Description |
|----------|----------|-------------|
| `alias` | No | Human-readable name |
| `description` | No | What the script does |
| `icon` | No | MDI icon (e.g., `mdi:lightbulb`) |
| `mode` | No | Execution mode (default: `single`) |
| `max` | No | Max concurrent runs (for queued/parallel) |
| `max_exceeded` | No | Log level when max exceeded |
| `fields` | No | Input parameters |
| `variables` | No | Local variables |
| `sequence` | Yes | Actions to perform |

---

## Script Modes

### Available Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `single` | Only one instance, reject new calls | Default, most scripts |
| `restart` | Stop current, start new | Reset sequences |
| `queued` | Queue calls, run sequentially | Notifications |
| `parallel` | Run all calls simultaneously | Independent actions |

### Mode Examples

```yaml
script:
  # Single - Reject if already running
  single_script:
    mode: single
    sequence:
      - delay: "00:01:00"
      - service: notify.mobile_app
        data:
          message: "Script completed"

  # Restart - Stop and restart
  restart_script:
    mode: restart
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.indicator
      - delay: "00:00:30"
      - service: light.turn_off
        target:
          entity_id: light.indicator

  # Queued - Process one at a time
  queued_script:
    mode: queued
    max: 5
    sequence:
      - service: tts.speak
        data:
          message: "{{ message }}"
      - delay: "00:00:05"

  # Parallel - Run all simultaneously
  parallel_script:
    mode: parallel
    max: 10
    sequence:
      - service: logbook.log
        data:
          name: "Script"
          message: "Called with: {{ data }}"
```

---

## Fields (Input Parameters)

### Basic Field Definition

```yaml
script:
  notify_person:
    alias: "Notify Person"
    fields:
      person:
        description: "Person to notify"
        required: true
        example: "John"
      message:
        description: "Message to send"
        required: true
        example: "Hello!"
      priority:
        description: "Notification priority"
        required: false
        default: "normal"
    sequence:
      - service: notify.mobile_app_{{ person | lower }}_phone
        data:
          message: "{{ message }}"
          data:
            priority: "{{ priority }}"
```

### Field Selectors

Selectors provide UI widgets for field input:

```yaml
script:
  example_fields:
    fields:
      # Entity selector
      target_entity:
        description: "Entity to control"
        selector:
          entity:
            domain: light

      # Multiple entities
      target_entities:
        description: "Entities to control"
        selector:
          entity:
            domain:
              - light
              - switch
            multiple: true

      # Area selector
      target_area:
        description: "Area to control"
        selector:
          area:

      # Device selector
      target_device:
        description: "Device to control"
        selector:
          device:
            integration: zwave_js

      # Number selector
      brightness:
        description: "Brightness level"
        selector:
          number:
            min: 0
            max: 100
            step: 5
            unit_of_measurement: "%"
            mode: slider  # or "box"

      # Boolean selector
      enable_sound:
        description: "Play sound"
        selector:
          boolean:

      # Text selector
      custom_message:
        description: "Custom message"
        selector:
          text:
            multiline: false

      # Select (dropdown)
      color:
        description: "Color to use"
        selector:
          select:
            options:
              - red
              - green
              - blue

      # Time selector
      start_time:
        description: "Start time"
        selector:
          time:

      # Date selector
      event_date:
        description: "Event date"
        selector:
          date:

      # Datetime selector
      reminder:
        description: "Reminder time"
        selector:
          datetime:

      # Duration selector
      timeout:
        description: "Timeout duration"
        selector:
          duration:

      # Color RGB selector
      light_color:
        description: "Light color"
        selector:
          color_rgb:

      # Color temp selector
      color_temp:
        description: "Color temperature"
        selector:
          color_temp:
            min_mireds: 153
            max_mireds: 500

      # Target selector (entity/device/area)
      target:
        description: "Target"
        selector:
          target:
            entity:
              domain: light

      # Action selector (for nested actions)
      custom_action:
        description: "Action to perform"
        selector:
          action:

      # Object selector (for complex data)
      data:
        description: "Additional data"
        selector:
          object:
```

### Using Fields in Sequence

```yaml
script:
  set_light_scene:
    alias: "Set Light Scene"
    fields:
      light:
        description: "Light entity"
        required: true
        selector:
          entity:
            domain: light
      scene:
        description: "Scene type"
        required: true
        selector:
          select:
            options:
              - relax
              - concentrate
              - energize
    sequence:
      - choose:
          - conditions:
              - "{{ scene == 'relax' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: "{{ light }}"
                data:
                  brightness_pct: 40
                  color_temp: 400
          - conditions:
              - "{{ scene == 'concentrate' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: "{{ light }}"
                data:
                  brightness_pct: 100
                  color_temp: 250
          - conditions:
              - "{{ scene == 'energize' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: "{{ light }}"
                data:
                  brightness_pct: 100
                  color_temp: 153
```

---

## Response Variables

Scripts can return data to the caller:

### Basic Response

```yaml
script:
  get_weather_summary:
    alias: "Get Weather Summary"
    sequence:
      - variables:
          temp: "{{ states('sensor.temperature') }}"
          humidity: "{{ states('sensor.humidity') }}"
          conditions: "{{ states('weather.home') }}"
      - stop: "Weather summary complete"
        response_variable: weather_data
        # Returns: { temp: "22", humidity: "45", conditions: "sunny" }
```

### Using Response in Automation

```yaml
automation:
  - id: weather_announcement
    alias: "Weather Announcement"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: script.get_weather_summary
        response_variable: weather
      - service: tts.speak
        target:
          entity_id: media_player.speaker
        data:
          message: >
            Good morning! It's {{ weather.temp }} degrees
            with {{ weather.humidity }}% humidity.
            Conditions are {{ weather.conditions }}.
```

### Response from Choose

```yaml
script:
  get_greeting:
    alias: "Get Time-Based Greeting"
    sequence:
      - choose:
          - conditions:
              - "{{ now().hour < 12 }}"
            sequence:
              - stop: "Morning greeting"
                response_variable: greeting
        default:
          - stop: "Afternoon greeting"
            response_variable: greeting
```

### Response from Service Calls

```yaml
script:
  check_calendar:
    alias: "Check Calendar Events"
    sequence:
      - service: calendar.get_events
        target:
          entity_id: calendar.work
        data:
          duration:
            hours: 24
        response_variable: events
      - stop: "Calendar check complete"
        response_variable: result
```

---

## All Action Types

Scripts use the same actions as automations. Here's a quick reference:

### Service Call

```yaml
sequence:
  - service: light.turn_on
    target:
      entity_id: light.bedroom
    data:
      brightness_pct: 80
```

### Delay

```yaml
sequence:
  - delay: "00:00:30"

  # Dynamic delay
  - delay:
      seconds: "{{ delay_seconds }}"
```

### Wait Template

```yaml
sequence:
  - wait_template: "{{ is_state('binary_sensor.door', 'off') }}"
    timeout: "00:01:00"
    continue_on_timeout: true
```

### Wait for Trigger

```yaml
sequence:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout: "00:05:00"
```

### Condition (as action)

```yaml
sequence:
  - condition: state
    entity_id: input_boolean.enabled
    state: "on"
  # Actions below only run if condition passes
  - service: light.turn_on
    target:
      entity_id: light.bedroom
```

### Choose

```yaml
sequence:
  - choose:
      - conditions:
          - "{{ mode == 'morning' }}"
        sequence:
          - service: scene.turn_on
            target:
              entity_id: scene.morning
      - conditions:
          - "{{ mode == 'evening' }}"
        sequence:
          - service: scene.turn_on
            target:
              entity_id: scene.evening
    default:
      - service: light.turn_on
        target:
          entity_id: light.default
```

### If/Then/Else

```yaml
sequence:
  - if:
      - "{{ brightness > 50 }}"
    then:
      - service: light.turn_on
        data:
          brightness_pct: "{{ brightness }}"
    else:
      - service: light.turn_on
        data:
          brightness_pct: 50
```

### Repeat

```yaml
sequence:
  # Count-based
  - repeat:
      count: 3
      sequence:
        - service: light.toggle
          target:
            entity_id: light.indicator
        - delay: "00:00:01"

  # While condition
  - repeat:
      while:
        - "{{ repeat.index <= 5 }}"
      sequence:
        - service: notify.mobile_app
          data:
            message: "Attempt {{ repeat.index }}"
        - delay: "00:00:10"

  # Until condition
  - repeat:
      until:
        - "{{ is_state('lock.door', 'locked') }}"
      sequence:
        - service: lock.lock
          target:
            entity_id: lock.door
        - delay: "00:00:05"

  # For each
  - repeat:
      for_each: "{{ lights }}"
      sequence:
        - service: light.turn_off
          target:
            entity_id: "{{ repeat.item }}"
```

### Parallel

```yaml
sequence:
  - parallel:
      - service: light.turn_on
        target:
          entity_id: light.bedroom
      - service: cover.open_cover
        target:
          entity_id: cover.bedroom_blinds
      - service: media_player.volume_set
        target:
          entity_id: media_player.bedroom
        data:
          volume_level: 0.3
```

### Variables

```yaml
sequence:
  - variables:
      calculated_brightness: >
        {{ (states('sensor.light_level') | float / 100 * 255) | int }}
  - service: light.turn_on
    target:
      entity_id: light.adaptive
    data:
      brightness: "{{ calculated_brightness }}"
```

### Stop

```yaml
sequence:
  - if:
      - "{{ not is_state('alarm_control_panel.home', 'disarmed') }}"
    then:
      - stop: "Alarm is armed, cannot proceed"

  # Continue with rest of script...
  - service: lock.unlock
    target:
      entity_id: lock.front_door
```

### Fire Event

```yaml
sequence:
  - event: custom_script_event
    event_data:
      script_name: "morning_routine"
      status: "completed"
```

---

## Calling Scripts

### From UI

1. Go to **Settings → Automations & Scenes → Scripts**
2. Click the script
3. Fill in any fields
4. Click **Run**

### From Developer Tools

1. Go to **Developer Tools → Services**
2. Select `script.turn_on` or `script.<script_name>`
3. Fill in service data (fields)
4. Click **Call Service**

### From Automation

```yaml
automation:
  - id: call_script_example
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    action:
      # Method 1: script.turn_on
      - service: script.turn_on
        target:
          entity_id: script.morning_lights
        data:
          variables:
            brightness: 80

      # Method 2: Direct call (preferred)
      - service: script.morning_lights
        data:
          brightness: 80
```

### From Another Script

```yaml
script:
  main_routine:
    sequence:
      - service: script.sub_routine_1
        data:
          param: "value"
      - service: script.sub_routine_2
```

### With Response Variable

```yaml
automation:
  - id: use_script_response
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: script.get_weather
        response_variable: weather
      - service: notify.mobile_app
        data:
          message: "Today: {{ weather.summary }}"
```

### Controlling Script Execution

```yaml
action:
  # Start script
  - service: script.turn_on
    target:
      entity_id: script.long_running

  # Stop script
  - service: script.turn_off
    target:
      entity_id: script.long_running

  # Toggle script
  - service: script.toggle
    target:
      entity_id: script.toggle_lights

  # Reload all scripts
  - service: script.reload
```

---

## Common Patterns

### Morning Routine

```yaml
script:
  morning_routine:
    alias: "Morning Routine"
    icon: mdi:weather-sunny
    sequence:
      # Gradually turn on bedroom light
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 10
          transition: 60

      - delay: "00:01:00"

      # Increase brightness
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 50
          transition: 120

      # Open blinds
      - service: cover.open_cover
        target:
          entity_id: cover.bedroom_blinds

      # Start coffee maker
      - service: switch.turn_on
        target:
          entity_id: switch.coffee_maker

      # Weather announcement
      - delay: "00:00:30"
      - service: tts.speak
        target:
          entity_id: media_player.bedroom_speaker
        data:
          message: >
            Good morning! It's {{ states('sensor.temperature') }} degrees outside.
            {{ states('weather.home') | replace('_', ' ') }} today.
```

### Goodnight Sequence

```yaml
script:
  goodnight:
    alias: "Goodnight"
    icon: mdi:weather-night
    sequence:
      # Turn off all lights
      - service: light.turn_off
        target:
          entity_id: all

      # Lock all doors
      - service: lock.lock
        target:
          entity_id: all

      # Arm alarm
      - service: alarm_control_panel.alarm_arm_night
        target:
          entity_id: alarm_control_panel.home

      # Set thermostat to sleep mode
      - service: climate.set_preset_mode
        target:
          entity_id: climate.home
        data:
          preset_mode: "sleep"

      # Turn on night lights (low brightness)
      - service: light.turn_on
        target:
          entity_id:
            - light.hallway_night
            - light.bathroom_night
        data:
          brightness_pct: 5

      # Confirm via TTS
      - service: tts.speak
        target:
          entity_id: media_player.bedroom
        data:
          message: "Goodnight. All lights off, doors locked, alarm armed."
```

### Notification Dispatcher

```yaml
script:
  notify:
    alias: "Centralized Notification"
    fields:
      title:
        description: "Notification title"
        selector:
          text:
      message:
        description: "Notification message"
        required: true
        selector:
          text:
            multiline: true
      severity:
        description: "Severity level"
        default: "normal"
        selector:
          select:
            options:
              - normal
              - important
              - critical
    sequence:
      - choose:
          # Critical - All channels
          - conditions:
              - "{{ severity == 'critical' }}"
            sequence:
              - parallel:
                  - service: notify.mobile_app_all
                    data:
                      title: "{{ title }}"
                      message: "{{ message }}"
                      data:
                        priority: high
                        ttl: 0
                  - service: tts.speak
                    target:
                      entity_id: media_player.all_speakers
                    data:
                      message: "Critical alert: {{ message }}"
                  - service: persistent_notification.create
                    data:
                      title: "{{ title }}"
                      message: "{{ message }}"

          # Important - Mobile + persistent
          - conditions:
              - "{{ severity == 'important' }}"
            sequence:
              - service: notify.mobile_app_all
                data:
                  title: "{{ title }}"
                  message: "{{ message }}"
              - service: persistent_notification.create
                data:
                  title: "{{ title }}"
                  message: "{{ message }}"

        # Normal - Mobile only
        default:
          - service: notify.mobile_app_all
            data:
              title: "{{ title }}"
              message: "{{ message }}"
```

### Scene Selector

```yaml
script:
  set_room_scene:
    alias: "Set Room Scene"
    fields:
      room:
        description: "Room to control"
        required: true
        selector:
          select:
            options:
              - living_room
              - bedroom
              - kitchen
      scene:
        description: "Scene to activate"
        required: true
        selector:
          select:
            options:
              - bright
              - relax
              - movie
              - off
    sequence:
      - service: scene.turn_on
        target:
          entity_id: "scene.{{ room }}_{{ scene }}"
```

### Device Finder

```yaml
script:
  find_device:
    alias: "Find Device"
    fields:
      device:
        description: "Device to find"
        required: true
        selector:
          select:
            options:
              - phone
              - tablet
              - keys
    sequence:
      - choose:
          - conditions:
              - "{{ device == 'phone' }}"
            sequence:
              - service: notify.mobile_app_phone
                data:
                  message: "TTS"
                  data:
                    tts_text: "Here I am!"
                    channel: alarm_stream

          - conditions:
              - "{{ device == 'tablet' }}"
            sequence:
              - service: notify.mobile_app_tablet
                data:
                  message: "TTS"
                  data:
                    tts_text: "Here I am!"
                    channel: alarm_stream

          - conditions:
              - "{{ device == 'keys' }}"
            sequence:
              - service: button.press
                target:
                  entity_id: button.tile_keys_ring
```

### Retry with Backoff

```yaml
script:
  retry_lock:
    alias: "Retry Lock Door"
    sequence:
      - repeat:
          count: 5
          sequence:
            - service: lock.lock
              target:
                entity_id: lock.front_door
            - delay:
                seconds: "{{ repeat.index * 5 }}"
            - if:
                - condition: state
                  entity_id: lock.front_door
                  state: "locked"
              then:
                - stop: "Door locked successfully"
      - service: notify.mobile_app
        data:
          title: "Lock Failed"
          message: "Could not lock front door after 5 attempts"
```

---

## Best Practices

### Naming Conventions

```yaml
script:
  # Use descriptive, action-oriented names
  turn_on_morning_lights:     # Good
  morning:                     # Too vague
  script1:                     # Bad

  # Prefix related scripts
  climate_set_away:
  climate_set_home:
  climate_boost:

  # Use snake_case
  notify_all_phones:          # Good
  NotifyAllPhones:            # Avoid
```

### Documentation

```yaml
script:
  complex_script:
    alias: "Complex Script with Documentation"
    description: |
      This script performs multiple actions:
      1. Checks if anyone is home
      2. Adjusts climate based on presence
      3. Sends notification if changes made

      Called by: automation.daily_climate_check
      Dependencies: climate.home, person.john, person.jane
    fields:
      override:
        description: "Skip presence check and force action"
        default: false
        selector:
          boolean:
```

### Error Handling

```yaml
script:
  safe_script:
    sequence:
      # Check prerequisites
      - condition: state
        entity_id: input_boolean.script_enabled
        state: "on"

      # Validate inputs
      - if:
          - "{{ target_entity is not defined }}"
        then:
          - stop: "Missing required field: target_entity"

      # Check entity availability
      - if:
          - "{{ states(target_entity) in ['unavailable', 'unknown'] }}"
        then:
          - service: script.notify
            data:
              message: "{{ target_entity }} is unavailable"
          - stop: "Entity unavailable"

      # Proceed with action
      - service: light.turn_on
        target:
          entity_id: "{{ target_entity }}"
```

### Modularity

```yaml
script:
  # Base building block
  light_fade:
    fields:
      light:
        required: true
        selector:
          entity:
            domain: light
      target_brightness:
        required: true
        selector:
          number:
            min: 0
            max: 100
      duration:
        default: 5
        selector:
          number:
            min: 1
            max: 60
    sequence:
      - service: light.turn_on
        target:
          entity_id: "{{ light }}"
        data:
          brightness_pct: "{{ target_brightness }}"
          transition: "{{ duration }}"

  # Composed script using base
  sunrise_simulation:
    sequence:
      - service: script.light_fade
        data:
          light: light.bedroom
          target_brightness: 10
          duration: 60
      - delay: "00:01:00"
      - service: script.light_fade
        data:
          light: light.bedroom
          target_brightness: 50
          duration: 120
      - delay: "00:02:00"
      - service: script.light_fade
        data:
          light: light.bedroom
          target_brightness: 100
          duration: 60
```

### Performance

```yaml
script:
  efficient_script:
    sequence:
      # Use parallel for independent actions
      - parallel:
          - service: light.turn_on
            target:
              entity_id: light.living_room
          - service: light.turn_on
            target:
              entity_id: light.kitchen
          - service: light.turn_on
            target:
              entity_id: light.bedroom

      # Instead of:
      # - service: light.turn_on
      #     target:
      #       entity_id: light.living_room
      # - service: light.turn_on
      #     target:
      #       entity_id: light.kitchen
      # - service: light.turn_on
      #     target:
      #       entity_id: light.bedroom
```

---

## Troubleshooting

### Script Not Running

| Check | Solution |
|-------|----------|
| Script enabled | Verify script isn't disabled |
| Mode conflict | Check if single mode and already running |
| Condition failed | Review any conditions in sequence |
| Field missing | Ensure required fields are provided |

### Field Not Passed

```yaml
# Wrong - fields not in data
- service: script.my_script
  target:
    entity_id: script.my_script
  data:
    my_field: value  # Ignored!

# Correct - use service directly
- service: script.my_script
  data:
    my_field: value
```

### Response Variable Empty

```yaml
# Wrong - no stop with response_variable
script:
  get_data:
    sequence:
      - variables:
          data: "{{ states('sensor.x') }}"
      # Missing stop!

# Correct - use stop with response_variable
script:
  get_data:
    sequence:
      - variables:
          data: "{{ states('sensor.x') }}"
      - stop: "Complete"
        response_variable: result
```

### Debugging Scripts

```yaml
sequence:
  # Add logging
  - service: system_log.write
    data:
      message: "Script started with: {{ field_value }}"
      level: info

  # Add persistent notification
  - service: persistent_notification.create
    data:
      title: "Debug"
      message: "Step 1 complete"

  # Check script state
  # Script running: states('script.my_script') == 'on'
```

### View Script Traces

1. Go to **Settings → Automations & Scenes → Scripts**
2. Click on the script
3. Click **Traces** in the top right
4. Select a trace to view execution details
