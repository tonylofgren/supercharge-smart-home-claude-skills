# Home Assistant Cookbook

Complete project examples and real-world solutions for common home automation scenarios.

## Table of Contents
- [Lighting Projects](#lighting-projects)
- [Climate Control](#climate-control)
- [Security & Safety](#security--safety)
- [Presence & Location](#presence--location)
- [Energy Management](#energy-management)
- [Media & Entertainment](#media--entertainment)
- [Notifications & Alerts](#notifications--alerts)
- [Voice Control](#voice-control)
- [Maintenance & System](#maintenance--system)
- [Seasonal & Holiday](#seasonal--holiday)

---

## Lighting Projects

### Smart Motion Lighting System

Complete motion-activated lighting with time-based brightness, ambient light sensing, and manual override.

```yaml
# helpers.yaml
input_boolean:
  motion_lights_enabled:
    name: "Motion Lights Enabled"
    icon: mdi:motion-sensor

input_number:
  motion_light_timeout:
    name: "Motion Light Timeout"
    min: 1
    max: 30
    step: 1
    unit_of_measurement: "min"
    icon: mdi:timer

input_select:
  lighting_mode:
    name: "Lighting Mode"
    options:
      - Auto
      - Manual
      - Away
      - Night
    icon: mdi:lightbulb-auto
```

```yaml
# automations/motion_lights.yaml
automation:
  - id: motion_light_on
    alias: "Motion Light - Turn On"
    description: "Activate lights on motion detection"
    mode: restart
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
        id: motion_detected
    condition:
      - condition: state
        entity_id: input_boolean.motion_lights_enabled
        state: "on"
      - condition: state
        entity_id: input_select.lighting_mode
        state: "Auto"
      - condition: numeric_state
        entity_id: sensor.living_room_illuminance
        below: 100
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness_pct: >
            {% set hour = now().hour %}
            {% if hour < 6 or hour >= 22 %}
              20
            {% elif hour < 8 or hour >= 20 %}
              50
            {% else %}
              100
            {% endif %}
          transition: 2
      - wait_for_trigger:
          - platform: state
            entity_id: binary_sensor.living_room_motion
            to: "off"
            for:
              minutes: "{{ states('input_number.motion_light_timeout') | int }}"
        timeout:
          minutes: 60
      - service: light.turn_off
        target:
          entity_id: light.living_room
        data:
          transition: 5

  - id: motion_light_manual_override
    alias: "Motion Light - Manual Override"
    description: "Disable motion control when light manually adjusted"
    trigger:
      - platform: state
        entity_id: light.living_room
        attribute: brightness
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.context.user_id is not none }}"
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.lighting_mode
        data:
          option: "Manual"
      - delay:
          hours: 2
      - service: input_select.select_option
        target:
          entity_id: input_select.lighting_mode
        data:
          option: "Auto"
```

### Circadian Lighting

Automatically adjust light color temperature throughout the day.

```yaml
# template_sensors.yaml
template:
  - sensor:
      - name: "Circadian Color Temp"
        unit_of_measurement: "K"
        state: >
          {% set hour = now().hour + now().minute / 60 %}
          {% if hour < 6 %}
            2700
          {% elif hour < 9 %}
            {{ 2700 + ((hour - 6) / 3 * 2000) | round }}
          {% elif hour < 17 %}
            4700
          {% elif hour < 21 %}
            {{ 4700 - ((hour - 17) / 4 * 2000) | round }}
          {% else %}
            2700
          {% endif %}

      - name: "Circadian Brightness"
        unit_of_measurement: "%"
        state: >
          {% set hour = now().hour + now().minute / 60 %}
          {% if hour < 6 %}
            30
          {% elif hour < 9 %}
            {{ 30 + ((hour - 6) / 3 * 70) | round }}
          {% elif hour < 17 %}
            100
          {% elif hour < 21 %}
            {{ 100 - ((hour - 17) / 4 * 50) | round }}
          {% else %}
            30
          {% endif %}
```

```yaml
# automations/circadian.yaml
automation:
  - id: circadian_lighting_update
    alias: "Circadian Lighting Update"
    trigger:
      - platform: time_pattern
        minutes: "/15"
      - platform: state
        entity_id: light.living_room
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.circadian_enabled
        state: "on"
      - condition: state
        entity_id: light.living_room
        state: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          kelvin: "{{ states('sensor.circadian_color_temp') | int }}"
          brightness_pct: "{{ states('sensor.circadian_brightness') | int }}"
          transition: 60
```

### Whole House Light Control

Control all lights by area with one command.

```yaml
# scripts/lighting.yaml
script:
  all_lights_off:
    alias: "All Lights Off"
    sequence:
      - service: light.turn_off
        target:
          entity_id: all
        data:
          transition: 5

  lights_by_floor:
    alias: "Control Lights by Floor"
    fields:
      floor:
        description: "Floor to control"
        selector:
          select:
            options:
              - ground
              - first
              - basement
      state:
        description: "On or off"
        selector:
          boolean:
    sequence:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ floor == 'ground' }}"
            sequence:
              - service: "light.turn_{{ 'on' if state else 'off' }}"
                target:
                  area_id:
                    - living_room
                    - kitchen
                    - dining_room
          - conditions:
              - condition: template
                value_template: "{{ floor == 'first' }}"
            sequence:
              - service: "light.turn_{{ 'on' if state else 'off' }}"
                target:
                  area_id:
                    - master_bedroom
                    - bedroom_2
                    - bathroom

  movie_mode:
    alias: "Movie Mode"
    sequence:
      - service: light.turn_off
        target:
          area_id: living_room
      - service: light.turn_on
        target:
          entity_id: light.tv_backlight
        data:
          brightness_pct: 20
          rgb_color: [255, 147, 41]
      - service: media_player.turn_on
        target:
          entity_id: media_player.tv
```

---

## Climate Control

### Smart Thermostat Schedule

Temperature management based on presence, time, and weather.

```yaml
# helpers.yaml
input_number:
  comfort_temp_home:
    name: "Comfort Temperature (Home)"
    min: 16
    max: 26
    step: 0.5
    unit_of_measurement: "°C"

  comfort_temp_away:
    name: "Comfort Temperature (Away)"
    min: 14
    max: 20
    step: 0.5
    unit_of_measurement: "°C"

  comfort_temp_sleep:
    name: "Comfort Temperature (Sleep)"
    min: 14
    max: 22
    step: 0.5
    unit_of_measurement: "°C"

input_boolean:
  climate_schedule_enabled:
    name: "Climate Schedule Enabled"
    icon: mdi:calendar-clock

schedule:
  climate_home_schedule:
    name: "Climate Home Schedule"
    monday:
      - from: "07:00:00"
        to: "08:30:00"
      - from: "17:00:00"
        to: "22:30:00"
    tuesday:
      - from: "07:00:00"
        to: "08:30:00"
      - from: "17:00:00"
        to: "22:30:00"
    # ... repeat for other days
    saturday:
      - from: "08:00:00"
        to: "23:00:00"
    sunday:
      - from: "08:00:00"
        to: "22:00:00"
```

```yaml
# automations/climate.yaml
automation:
  - id: climate_scheduled_home
    alias: "Climate - Scheduled Home Temperature"
    trigger:
      - platform: state
        entity_id: schedule.climate_home_schedule
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.climate_schedule_enabled
        state: "on"
      - condition: not
        conditions:
          - condition: state
            entity_id: group.family
            state: "not_home"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.comfort_temp_home') | float }}"
          hvac_mode: heat

  - id: climate_scheduled_away
    alias: "Climate - Scheduled Away Temperature"
    trigger:
      - platform: state
        entity_id: schedule.climate_home_schedule
        to: "off"
    condition:
      - condition: state
        entity_id: input_boolean.climate_schedule_enabled
        state: "on"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.comfort_temp_away') | float }}"

  - id: climate_presence_override
    alias: "Climate - Presence Override"
    trigger:
      - platform: state
        entity_id: group.family
        to: "not_home"
        for: "00:30:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.comfort_temp_away') | float }}"

  - id: climate_arrival_preheat
    alias: "Climate - Arrival Preheat"
    trigger:
      - platform: zone
        entity_id: person.john
        zone: zone.home
        event: enter
    condition:
      - condition: numeric_state
        entity_id: sensor.living_room_temperature
        below: "{{ states('input_number.comfort_temp_home') | float - 2 }}"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.comfort_temp_home') | float }}"
          hvac_mode: heat
```

### Window Open Detection

Pause climate control when windows are open.

```yaml
automation:
  - id: climate_window_open
    alias: "Climate - Window Open"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.living_room_window
          - binary_sensor.bedroom_window
          - binary_sensor.kitchen_window
        to: "on"
        for: "00:02:00"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: >
            {% set room = trigger.entity_id.split('.')[1].replace('_window', '') %}
            {{ 'climate.' ~ room }}
        data:
          hvac_mode: "off"
      - service: notify.mobile_app
        data:
          message: "{{ trigger.to_state.attributes.friendly_name }} open - climate paused"

  - id: climate_window_closed
    alias: "Climate - Window Closed"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.living_room_window
          - binary_sensor.bedroom_window
        to: "off"
        for: "00:05:00"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: >
            {% set room = trigger.entity_id.split('.')[1].replace('_window', '') %}
            {{ 'climate.' ~ room }}
        data:
          hvac_mode: "heat"
```

---

## Security & Safety

### Complete Alarm System

DIY alarm system with arming modes, entry/exit delays, and notifications.

```yaml
# helpers.yaml
input_select:
  alarm_mode:
    name: "Alarm Mode"
    options:
      - Disarmed
      - Armed Home
      - Armed Away
      - Armed Night
      - Triggered
    icon: mdi:shield-home

input_boolean:
  alarm_triggered:
    name: "Alarm Triggered"
    icon: mdi:alarm-light

input_number:
  alarm_entry_delay:
    name: "Entry Delay"
    min: 0
    max: 120
    step: 5
    unit_of_measurement: "sec"
    initial: 30

  alarm_exit_delay:
    name: "Exit Delay"
    min: 0
    max: 120
    step: 5
    unit_of_measurement: "sec"
    initial: 60

timer:
  alarm_entry:
    name: "Entry Countdown"
    duration: "00:00:30"
  alarm_exit:
    name: "Exit Countdown"
    duration: "00:01:00"
```

```yaml
# automations/alarm.yaml
automation:
  - id: alarm_arm_away
    alias: "Alarm - Arm Away"
    trigger:
      - platform: state
        entity_id: input_select.alarm_mode
        to: "Armed Away"
    action:
      - service: timer.start
        target:
          entity_id: timer.alarm_exit
        data:
          duration: "{{ states('input_number.alarm_exit_delay') | int }}"
      - service: notify.mobile_app
        data:
          message: "Alarm arming in {{ states('input_number.alarm_exit_delay') }} seconds"

  - id: alarm_exit_complete
    alias: "Alarm - Exit Complete"
    trigger:
      - platform: event
        event_type: timer.finished
        event_data:
          entity_id: timer.alarm_exit
    action:
      - service: notify.mobile_app
        data:
          message: "Alarm is now armed"
          data:
            tag: "alarm_status"

  - id: alarm_sensor_trigger
    alias: "Alarm - Sensor Trigger"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.front_door
          - binary_sensor.back_door
          - binary_sensor.garage_door
        to: "on"
    condition:
      - condition: state
        entity_id: input_select.alarm_mode
        state:
          - "Armed Away"
          - "Armed Home"
          - "Armed Night"
      - condition: state
        entity_id: timer.alarm_exit
        state: "idle"
    action:
      - choose:
          # Entry sensors - start countdown
          - conditions:
              - condition: template
                value_template: "{{ trigger.entity_id in ['binary_sensor.front_door', 'binary_sensor.garage_door'] }}"
            sequence:
              - service: timer.start
                target:
                  entity_id: timer.alarm_entry
                data:
                  duration: "{{ states('input_number.alarm_entry_delay') | int }}"
              - service: notify.mobile_app
                data:
                  message: "Entry detected! Disarm alarm within {{ states('input_number.alarm_entry_delay') }} seconds"
                  data:
                    actions:
                      - action: "DISARM_ALARM"
                        title: "Disarm"
        # Instant sensors - trigger immediately
        default:
          - service: input_select.select_option
            target:
              entity_id: input_select.alarm_mode
            data:
              option: "Triggered"

  - id: alarm_entry_expired
    alias: "Alarm - Entry Countdown Expired"
    trigger:
      - platform: event
        event_type: timer.finished
        event_data:
          entity_id: timer.alarm_entry
    condition:
      - condition: not
        conditions:
          - condition: state
            entity_id: input_select.alarm_mode
            state: "Disarmed"
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.alarm_mode
        data:
          option: "Triggered"

  - id: alarm_triggered
    alias: "Alarm - Triggered Response"
    trigger:
      - platform: state
        entity_id: input_select.alarm_mode
        to: "Triggered"
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.alarm_triggered
      - service: light.turn_on
        target:
          entity_id: all
        data:
          flash: long
      - service: notify.mobile_app
        data:
          title: "ALARM TRIGGERED!"
          message: "Security breach detected at home"
          data:
            priority: high
            ttl: 0
            actions:
              - action: "DISARM_ALARM"
                title: "Disarm"
              - action: "CALL_POLICE"
                title: "Call Police"
      - repeat:
          count: 10
          sequence:
            - service: tts.speak
              target:
                entity_id: tts.google_en
              data:
                media_player_entity_id: media_player.living_room
                message: "Warning! Security alarm activated!"
            - delay: "00:00:30"

  - id: alarm_disarm
    alias: "Alarm - Disarm"
    trigger:
      - platform: state
        entity_id: input_select.alarm_mode
        to: "Disarmed"
    action:
      - service: timer.cancel
        target:
          entity_id:
            - timer.alarm_entry
            - timer.alarm_exit
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.alarm_triggered
      - service: media_player.media_stop
        target:
          entity_id: media_player.living_room
```

### Smoke & CO Detection

```yaml
automation:
  - id: safety_smoke_detected
    alias: "Safety - Smoke Detected"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.smoke_detector_kitchen
          - binary_sensor.smoke_detector_bedroom
          - binary_sensor.smoke_detector_hallway
        to: "on"
    action:
      - parallel:
          - service: light.turn_on
            target:
              entity_id: all
            data:
              brightness_pct: 100
          - service: notify.all_phones
            data:
              title: "FIRE ALARM!"
              message: "Smoke detected at {{ trigger.to_state.attributes.friendly_name }}"
              data:
                priority: high
          - service: tts.speak
            target:
              entity_id: tts.google_en
            data:
              media_player_entity_id: all
              message: "Warning! Smoke detected. Please evacuate immediately."

  - id: safety_co_detected
    alias: "Safety - CO Detected"
    trigger:
      - platform: state
        entity_id: binary_sensor.co_detector
        to: "on"
    action:
      - service: notify.all_phones
        data:
          title: "CO ALARM!"
          message: "Carbon monoxide detected! Evacuate and call emergency services!"
          data:
            priority: high
      - service: climate.set_hvac_mode
        target:
          entity_id: all
        data:
          hvac_mode: "off"
```

---

## Presence & Location

### Advanced Presence Detection

Combine multiple sensors for reliable presence detection.

```yaml
# template_sensors.yaml
template:
  - binary_sensor:
      - name: "Living Room Occupied"
        state: >
          {{ is_state('binary_sensor.living_room_motion', 'on')
             or is_state('binary_sensor.living_room_presence', 'on')
             or is_state('media_player.living_room_tv', 'playing')
             or (states('sensor.living_room_power') | float(0) > 50) }}
        delay_off:
          minutes: 10

      - name: "Anyone Home"
        state: >
          {{ is_state('person.john', 'home')
             or is_state('person.jane', 'home')
             or is_state('binary_sensor.living_room_occupied', 'on')
             or is_state('binary_sensor.kitchen_occupied', 'on') }}
        delay_off:
          minutes: 30

      - name: "House Empty"
        state: >
          {{ is_state('group.family', 'not_home')
             and is_state('binary_sensor.anyone_home', 'off') }}
        delay_on:
          minutes: 15
```

```yaml
# automations/presence.yaml
automation:
  - id: presence_everyone_left
    alias: "Presence - Everyone Left"
    trigger:
      - platform: state
        entity_id: binary_sensor.house_empty
        to: "on"
    action:
      - service: script.turn_on
        target:
          entity_id: script.away_mode

  - id: presence_first_person_home
    alias: "Presence - First Person Home"
    trigger:
      - platform: state
        entity_id: group.family
        to: "home"
    condition:
      - condition: state
        entity_id: input_select.home_mode
        state: "Away"
    action:
      - service: script.turn_on
        target:
          entity_id: script.welcome_home

script:
  away_mode:
    alias: "Away Mode"
    sequence:
      - service: input_select.select_option
        target:
          entity_id: input_select.home_mode
        data:
          option: "Away"
      - service: climate.set_temperature
        target:
          entity_id: all
        data:
          temperature: "{{ states('input_number.comfort_temp_away') | float }}"
      - service: light.turn_off
        target:
          entity_id: all
      - service: media_player.turn_off
        target:
          entity_id: all
      - delay: "00:05:00"
      - service: input_select.select_option
        target:
          entity_id: input_select.alarm_mode
        data:
          option: "Armed Away"

  welcome_home:
    alias: "Welcome Home"
    sequence:
      - service: input_select.select_option
        target:
          entity_id: input_select.alarm_mode
        data:
          option: "Disarmed"
      - service: input_select.select_option
        target:
          entity_id: input_select.home_mode
        data:
          option: "Home"
      - condition: numeric_state
        entity_id: sensor.living_room_illuminance
        below: 100
      - service: light.turn_on
        target:
          entity_id: light.hallway
        data:
          brightness_pct: 100
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.comfort_temp_home') | float }}"
```

### Location-Based Automations

```yaml
automation:
  - id: location_leaving_work
    alias: "Location - Leaving Work"
    trigger:
      - platform: zone
        entity_id: person.john
        zone: zone.work
        event: leave
    condition:
      - condition: time
        after: "15:00:00"
        before: "20:00:00"
    action:
      - service: notify.jane_phone
        data:
          message: "John left work. ETA home: {{ state_attr('sensor.john_commute', 'duration') }} minutes"
      - condition: numeric_state
        entity_id: sensor.home_temperature
        below: 19
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.comfort_temp_home') | float }}"

  - id: location_near_home
    alias: "Location - Approaching Home"
    trigger:
      - platform: numeric_state
        entity_id: sensor.john_distance_home
        below: 1
    condition:
      - condition: state
        entity_id: input_select.home_mode
        state: "Away"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.garage_door
```

---

## Energy Management

### Solar & Battery Management

```yaml
# template_sensors.yaml
template:
  - sensor:
      - name: "Net Power"
        unit_of_measurement: "W"
        device_class: power
        state: >
          {{ (states('sensor.grid_power') | float(0)) -
             (states('sensor.solar_power') | float(0)) }}

      - name: "Self Consumption Rate"
        unit_of_measurement: "%"
        state: >
          {% set solar = states('sensor.solar_power') | float(0) %}
          {% set consumption = states('sensor.home_power') | float(0) %}
          {% if solar > 0 %}
            {{ ((min(solar, consumption) / solar) * 100) | round(1) }}
          {% else %}
            0
          {% endif %}
```

```yaml
# automations/energy.yaml
automation:
  - id: energy_high_solar_appliances
    alias: "Energy - Run Appliances on Solar"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power
        above: 3000
        for: "00:05:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.battery_soc
        above: 80
    action:
      - service: notify.mobile_app
        data:
          message: "High solar production! Good time to run dishwasher or washing machine."
          data:
            actions:
              - action: "START_DISHWASHER"
                title: "Start Dishwasher"
              - action: "START_WASHER"
                title: "Start Washer"

  - id: energy_battery_backup_mode
    alias: "Energy - Battery Backup Mode"
    trigger:
      - platform: state
        entity_id: binary_sensor.grid_status
        to: "off"
    action:
      - service: notify.all_phones
        data:
          title: "Power Outage"
          message: "Grid power lost. Running on battery backup."
      - service: switch.turn_off
        target:
          entity_id:
            - switch.water_heater
            - switch.pool_pump
      - service: light.turn_off
        target:
          entity_id: all
      - service: light.turn_on
        target:
          entity_id:
            - light.hallway
            - light.kitchen
        data:
          brightness_pct: 50
```

### Time-of-Use Optimization

```yaml
# helpers.yaml
input_select:
  electricity_rate:
    name: "Electricity Rate Period"
    options:
      - Peak
      - Off-Peak
      - Super Off-Peak

template:
  - sensor:
      - name: "Current Electricity Rate"
        unit_of_measurement: "SEK/kWh"
        state: >
          {% set hour = now().hour %}
          {% set weekday = now().weekday() < 5 %}
          {% if weekday and (hour >= 7 and hour < 9) or (hour >= 17 and hour < 21) %}
            2.50
          {% elif hour >= 22 or hour < 6 %}
            0.80
          {% else %}
            1.50
          {% endif %}
```

```yaml
automation:
  - id: energy_schedule_high_power
    alias: "Energy - Schedule High Power Devices"
    trigger:
      - platform: numeric_state
        entity_id: sensor.current_electricity_rate
        below: 1.0
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.water_heater
      - condition: state
        entity_id: binary_sensor.car_plugged_in
        state: "on"
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

---

## Media & Entertainment

### Multi-Room Audio

```yaml
script:
  play_music_everywhere:
    alias: "Play Music Everywhere"
    fields:
      playlist:
        description: "Playlist or station to play"
        selector:
          text:
    sequence:
      - service: media_player.join
        target:
          entity_id: media_player.living_room_speaker
        data:
          group_members:
            - media_player.kitchen_speaker
            - media_player.bedroom_speaker
            - media_player.office_speaker
      - service: media_player.play_media
        target:
          entity_id: media_player.living_room_speaker
        data:
          media_content_type: playlist
          media_content_id: "{{ playlist }}"

  follow_me_audio:
    alias: "Follow Me Audio"
    sequence:
      - variables:
          active_room: >
            {% if is_state('binary_sensor.living_room_occupied', 'on') %}
              living_room
            {% elif is_state('binary_sensor.kitchen_occupied', 'on') %}
              kitchen
            {% elif is_state('binary_sensor.bedroom_occupied', 'on') %}
              bedroom
            {% else %}
              living_room
            {% endif %}
      - service: media_player.media_pause
        target:
          entity_id: all
      - service: media_player.media_play
        target:
          entity_id: "media_player.{{ active_room }}_speaker"
```

### TV Control Automation

```yaml
automation:
  - id: media_tv_on_lights
    alias: "Media - Dim Lights When TV On"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        to: "playing"
    condition:
      - condition: sun
        after: sunset
    action:
      - service: light.turn_on
        target:
          area_id: living_room
        data:
          brightness_pct: 20
          transition: 5

  - id: media_tv_off_lights
    alias: "Media - Restore Lights When TV Off"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        from: "playing"
        to:
          - "paused"
          - "idle"
          - "off"
        for: "00:00:30"
    condition:
      - condition: sun
        after: sunset
    action:
      - service: light.turn_on
        target:
          area_id: living_room
        data:
          brightness_pct: 80
          transition: 5
```

---

## Notifications & Alerts

### Smart Notification System

```yaml
# scripts/notifications.yaml
script:
  smart_notify:
    alias: "Smart Notification"
    fields:
      title:
        description: "Notification title"
        selector:
          text:
      message:
        description: "Notification message"
        selector:
          text:
      priority:
        description: "Priority level"
        selector:
          select:
            options:
              - low
              - normal
              - high
              - critical
    sequence:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ priority == 'critical' }}"
            sequence:
              - parallel:
                  - service: notify.all_phones
                    data:
                      title: "{{ title }}"
                      message: "{{ message }}"
                      data:
                        priority: high
                        ttl: 0
                  - service: tts.speak
                    target:
                      entity_id: tts.google_en
                    data:
                      media_player_entity_id: all
                      message: "{{ message }}"
          - conditions:
              - condition: template
                value_template: "{{ priority == 'high' }}"
            sequence:
              - service: notify.all_phones
                data:
                  title: "{{ title }}"
                  message: "{{ message }}"
                  data:
                    priority: high
          - conditions:
              - condition: template
                value_template: "{{ priority == 'normal' }}"
            sequence:
              - condition: time
                after: "08:00:00"
                before: "22:00:00"
              - service: notify.all_phones
                data:
                  title: "{{ title }}"
                  message: "{{ message }}"
        default:
          - service: notify.persistent_notification
            data:
              title: "{{ title }}"
              message: "{{ message }}"
```

### Daily Summary

```yaml
automation:
  - id: notification_morning_briefing
    alias: "Notification - Morning Briefing"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: person.john
        state: "home"
    action:
      - service: notify.mobile_app_john
        data:
          title: "Good Morning!"
          message: >
            Weather: {{ states('weather.home') }}, {{ state_attr('weather.home', 'temperature') }}°C

            {% if states('calendar.work') != 'off' %}
            First meeting: {{ state_attr('calendar.work', 'message') }} at {{ state_attr('calendar.work', 'start_time') }}
            {% endif %}

            {% if states('binary_sensor.trash_day') == 'on' %}
            Reminder: Today is trash day!
            {% endif %}

            Energy yesterday: {{ states('sensor.daily_energy') }} kWh
```

---

## Voice Control

### Custom Voice Commands

```yaml
# intent_scripts.yaml
intent_script:
  GoodNight:
    speech:
      text: "Good night! Setting everything up for sleep."
    action:
      - service: script.turn_on
        target:
          entity_id: script.goodnight_routine

  MovieTime:
    speech:
      text: "Starting movie mode. Enjoy your movie!"
    action:
      - service: script.turn_on
        target:
          entity_id: script.movie_mode

  WhereIs:
    speech:
      text: >
        {% set person = person %}
        {{ person }} is currently {{ states('person.' ~ person | lower) }}.
    action: []
```

```yaml
# custom_sentences/en/intents.yaml
language: en
intents:
  GoodNight:
    data:
      - sentences:
          - "good night"
          - "time for bed"
          - "going to sleep"

  MovieTime:
    data:
      - sentences:
          - "movie time"
          - "start movie mode"
          - "watch a movie"

  WhereIs:
    data:
      - sentences:
          - "where is {person}"
          - "where's {person}"
          - "find {person}"
```

---

## Maintenance & System

### System Health Monitoring

```yaml
automation:
  - id: system_disk_space_warning
    alias: "System - Disk Space Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.disk_use_percent
        above: 80
    action:
      - service: notify.admin
        data:
          title: "Disk Space Warning"
          message: "Disk usage at {{ states('sensor.disk_use_percent') }}%. Consider cleanup."

  - id: system_backup_reminder
    alias: "System - Weekly Backup Reminder"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: hassio.backup_full
        data:
          name: "weekly_{{ now().strftime('%Y%m%d') }}"
      - service: notify.admin
        data:
          message: "Weekly backup completed"

  - id: system_update_available
    alias: "System - Update Available"
    trigger:
      - platform: state
        entity_id: update.home_assistant_core_update
        to: "on"
    action:
      - service: notify.admin
        data:
          title: "Home Assistant Update Available"
          message: >
            Version {{ state_attr('update.home_assistant_core_update', 'latest_version') }} is available.
            Current: {{ state_attr('update.home_assistant_core_update', 'installed_version') }}
```

---

## Seasonal & Holiday

### Christmas Lighting

```yaml
automation:
  - id: christmas_lights_schedule
    alias: "Christmas - Lights Schedule"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    condition:
      - condition: template
        value_template: "{{ now().month == 12 and now().day >= 1 }}"
    action:
      - service: switch.turn_on
        target:
          entity_id:
            - switch.christmas_tree
            - switch.outdoor_lights
            - switch.window_candles
      - wait_template: "{{ now().hour >= 23 }}"
      - service: switch.turn_off
        target:
          entity_id:
            - switch.christmas_tree
            - switch.outdoor_lights
```

### Vacation Mode

```yaml
automation:
  - id: vacation_random_lights
    alias: "Vacation - Random Lights"
    trigger:
      - platform: time_pattern
        minutes: "/30"
    condition:
      - condition: state
        entity_id: input_boolean.vacation_mode
        state: "on"
      - condition: sun
        after: sunset
      - condition: time
        before: "23:00:00"
    action:
      - service: light.turn_{{ ['on', 'off'] | random }}
        target:
          entity_id: >
            {{ ['light.living_room', 'light.bedroom', 'light.kitchen'] | random }}
        data:
          brightness_pct: "{{ range(40, 100) | random }}"
```

---

## Dashboard Examples

### Home Overview Dashboard

```yaml
# dashboards/home.yaml
title: Home
views:
  - title: Overview
    path: overview
    icon: mdi:home
    cards:
      - type: custom:mushroom-chips-card
        chips:
          - type: entity
            entity: person.john
          - type: entity
            entity: person.jane
          - type: entity
            entity: alarm_control_panel.home

      - type: weather-forecast
        entity: weather.home
        show_forecast: true

      - type: grid
        columns: 4
        square: true
        cards:
          - type: button
            entity: script.leaving_home
            name: Leaving
            icon: mdi:door-open
          - type: button
            entity: script.arriving_home
            name: Home
            icon: mdi:home
          - type: button
            entity: scene.movie_mode
            name: Movie
            icon: mdi:movie
          - type: button
            entity: script.goodnight
            name: Night
            icon: mdi:sleep

      - type: entities
        title: Climate
        entities:
          - entity: climate.living_room
          - entity: sensor.living_room_temperature
          - entity: sensor.living_room_humidity

      - type: energy-distribution
        link_dashboard: true
```

This cookbook provides complete, tested examples you can adapt for your own home automation setup.
