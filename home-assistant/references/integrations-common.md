# Home Assistant Common Integrations Reference

## Table of Contents
- [Philips Hue](#philips-hue)
- [Sonos](#sonos)
- [Google Assistant](#google-assistant)
- [Amazon Alexa](#amazon-alexa)
- [Apple HomeKit](#apple-homekit)
- [Samsung SmartThings](#samsung-smartthings)
- [Tuya / Smart Life](#tuya--smart-life)
- [Shelly](#shelly)
- [TP-Link Kasa](#tp-link-kasa)
- [Google Calendar](#google-calendar)
- [Integration Patterns](#integration-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Philips Hue

### Configuration

```yaml
# Automatic discovery via UI (recommended)
# Configuration > Integrations > Add Integration > Philips Hue

# Legacy YAML (deprecated)
hue:
  bridges:
    - host: 192.168.1.100
```

### Entity Patterns

| Entity Type | Pattern | Example |
|-------------|---------|---------|
| Light | `light.hue_*` | `light.hue_living_room` |
| Group | `light.hue_room_*` | `light.hue_room_bedroom` |
| Scene | `scene.hue_*` | `scene.hue_relax` |
| Sensor | `sensor.hue_*` | `sensor.hue_motion_temperature` |
| Binary Sensor | `binary_sensor.hue_*` | `binary_sensor.hue_motion` |

### Light Services

```yaml
# Turn on with color
service: light.turn_on
target:
  entity_id: light.hue_living_room
data:
  brightness: 255
  rgb_color: [255, 100, 50]

# Use Hue scene
service: hue.activate_scene
data:
  group_name: "Living Room"
  scene_name: "Relax"

# Color transition
service: light.turn_on
target:
  entity_id: light.hue_bulb_1
data:
  xy_color: [0.5, 0.4]
  transition: 5

# Color temperature
service: light.turn_on
target:
  entity_id: light.hue_bedroom
data:
  color_temp: 300  # Mireds (warm)
  brightness_pct: 80
```

### Hue Groups

```yaml
# Activate all lights in Hue group
service: light.turn_on
target:
  entity_id: light.hue_room_living_room
data:
  brightness_pct: 100

# Entertainment areas
service: hue.hue_activate_scene
data:
  group_name: "Entertainment Area"
  scene_name: "Movie"
```

### Motion Sensor Automation

```yaml
automation:
  - alias: "Hue Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.hue_motion_sensor_motion
        to: "on"
    condition:
      - condition: numeric_state
        entity_id: sensor.hue_motion_sensor_light_level
        below: 100
    action:
      - service: light.turn_on
        target:
          entity_id: light.hue_hallway
        data:
          brightness_pct: "{{ 30 if now().hour < 6 else 100 }}"
```

### Hue Tap / Dimmer Switch

```yaml
automation:
  - alias: "Hue Dimmer Button Press"
    trigger:
      - platform: event
        event_type: hue_event
        event_data:
          device_id: abc123  # Get from event logs
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.type == 'short_release' }}"
              - condition: template
                value_template: "{{ trigger.event.data.subtype == 1 }}"  # Button 1
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.hue_living_room
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.subtype == 4 }}"  # Button 4
            sequence:
              - service: light.turn_off
                target:
                  entity_id: all
```

---

## Sonos

### Configuration

```yaml
# Auto-discovered via UI
# Configuration > Integrations > Sonos

# For advanced options
sonos:
  media_player:
    hosts:
      - 192.168.1.101
      - 192.168.1.102
```

### Entity Patterns

| Entity Type | Pattern | Example |
|-------------|---------|---------|
| Media Player | `media_player.sonos_*` | `media_player.sonos_living_room` |
| Sensor (battery) | `sensor.sonos_*_battery` | `sensor.sonos_move_battery` |

### Playback Services

```yaml
# Play media
service: media_player.play_media
target:
  entity_id: media_player.sonos_living_room
data:
  media_content_type: music
  media_content_id: "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"

# Set volume
service: media_player.volume_set
target:
  entity_id: media_player.sonos_kitchen
data:
  volume_level: 0.3

# Text-to-speech
service: tts.speak
target:
  entity_id: media_player.sonos_living_room
data:
  message: "Motion detected at front door"
  cache: true
```

### Grouping Speakers

```yaml
# Join speakers
service: media_player.join
target:
  entity_id: media_player.sonos_living_room
data:
  group_members:
    - media_player.sonos_kitchen
    - media_player.sonos_bedroom

# Unjoin speaker
service: media_player.unjoin
target:
  entity_id: media_player.sonos_kitchen
```

### Sonos Announcements

```yaml
automation:
  - alias: "Doorbell Announcement"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      # Snapshot current state
      - service: sonos.snapshot
        target:
          entity_id: media_player.sonos_living_room
        data:
          with_group: true
      # Play announcement
      - service: tts.speak
        target:
          entity_id: media_player.sonos_living_room
        data:
          message: "Someone is at the front door"
      - delay: "00:00:03"
      # Restore previous state
      - service: sonos.restore
        target:
          entity_id: media_player.sonos_living_room
        data:
          with_group: true
```

### Sonos with Spotify

```yaml
automation:
  - alias: "Morning Music"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: person.john
        state: "home"
    action:
      - service: media_player.select_source
        target:
          entity_id: media_player.sonos_bedroom
        data:
          source: "Spotify"
      - service: media_player.play_media
        target:
          entity_id: media_player.sonos_bedroom
        data:
          media_content_type: playlist
          media_content_id: "spotify:playlist:your_playlist_id"
      - service: media_player.volume_set
        target:
          entity_id: media_player.sonos_bedroom
        data:
          volume_level: 0.2
```

---

## Google Assistant

### Configuration Methods

| Method | Use Case |
|--------|----------|
| **Nabu Casa** | Easiest, subscription required |
| **Manual** | Self-hosted, complex setup |
| **Local SDK** | Advanced local control |

### Nabu Casa Setup

```yaml
# Configuration > Home Assistant Cloud
# Enable Google Assistant
# Select entities to expose
```

### Expose Entities

```yaml
# In entity customization or via UI
homeassistant:
  customize:
    light.living_room:
      google_assistant: true
    switch.coffee_maker:
      google_assistant: true
      google_assistant_name: "Coffee Machine"
    cover.garage:
      google_assistant: true
      google_assistant_room: "Garage"
```

### Entity Filters (Cloud)

```yaml
# configuration.yaml
cloud:
  google_actions:
    filter:
      include_domains:
        - light
        - switch
        - climate
      exclude_entities:
        - light.test_light
        - switch.internal_relay
```

### Google Assistant Routines

```yaml
# Create a script for Google to trigger
script:
  goodnight:
    alias: "Good Night"
    sequence:
      - service: light.turn_off
        target:
          entity_id: all
      - service: lock.lock
        target:
          entity_id: lock.front_door
      - service: cover.close_cover
        target:
          entity_id: cover.garage
      - service: climate.set_temperature
        target:
          entity_id: climate.thermostat
        data:
          temperature: 18

# Then in Google Home app:
# Create routine "Good Night" -> "Run Home Assistant script goodnight"
```

### Custom Commands via Scripts

```yaml
script:
  movie_mode:
    alias: "Movie Mode"
    sequence:
      - service: light.turn_off
        target:
          entity_id: light.living_room
      - service: light.turn_on
        target:
          entity_id: light.tv_backlight
        data:
          brightness: 50
          rgb_color: [100, 100, 255]
      - service: media_player.turn_on
        target:
          entity_id: media_player.tv
```

---

## Amazon Alexa

### Configuration Methods

| Method | Use Case |
|--------|----------|
| **Nabu Casa** | Easiest, subscription |
| **haaska** | Self-hosted Lambda |
| **Alexa Media Player** | HACS integration |

### Nabu Casa Setup

```yaml
# Home Assistant Cloud > Enable Alexa
# No additional YAML needed
```

### Entity Filters

```yaml
cloud:
  alexa:
    filter:
      include_domains:
        - light
        - switch
        - lock
        - climate
      include_entities:
        - script.goodnight
      exclude_entities:
        - light.test
```

### Entity Configuration

```yaml
cloud:
  alexa:
    entity_config:
      light.living_room:
        name: "Living Room Light"
        display_categories: LIGHT
      switch.coffee_maker:
        name: "Coffee Machine"
        display_categories: SMARTPLUG
      script.goodnight:
        name: "Good Night Routine"
        display_categories: SCENE_TRIGGER
```

### Alexa Media Player (HACS)

```yaml
# Installed via HACS
# Enables:
# - Play TTS on Echo devices
# - Trigger routines
# - View last Alexa command

# Example: TTS announcement
service: notify.alexa_media
data:
  message: "Laundry is done"
  target:
    - media_player.echo_kitchen
  data:
    type: announce  # or tts

# Play music
service: media_player.play_media
target:
  entity_id: media_player.echo_living_room
data:
  media_content_type: "SPOTIFY"
  media_content_id: "playlist/37i9dQZF1DXcBWIGoYBM5M"
```

### Alexa Routines via Home Assistant

```yaml
automation:
  - alias: "Alexa Motion Detected Announcement"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_motion
        to: "on"
    action:
      - service: notify.alexa_media
        data:
          message: "Motion detected at the front door"
          target: media_player.echo_hallway
          data:
            type: announce
```

---

## Apple HomeKit

### Controller Setup (HomeKit Devices in HA)

```yaml
# Auto-discovery via UI for HomeKit devices
# Configuration > Integrations > HomeKit Controller
```

### Bridge Setup (Expose HA to HomeKit)

```yaml
# configuration.yaml
homekit:
  - name: "Home Assistant Bridge"
    port: 21063
    filter:
      include_domains:
        - light
        - switch
        - lock
        - climate
        - cover
      exclude_entities:
        - light.test_light
```

### Multiple Bridges

```yaml
homekit:
  - name: "Lights Bridge"
    port: 21063
    filter:
      include_domains:
        - light
  - name: "Climate Bridge"
    port: 21064
    filter:
      include_domains:
        - climate
        - fan
  - name: "Security Bridge"
    port: 21065
    filter:
      include_domains:
        - lock
        - cover
        - alarm_control_panel
```

### Entity Configuration

```yaml
homekit:
  - name: "Home Assistant"
    filter:
      include_domains:
        - light
    entity_config:
      light.living_room:
        name: "Living Room"
      light.bedroom:
        name: "Bedroom Light"
        linked_battery_sensor: sensor.bedroom_light_battery
```

### Supported Domains

| Domain | HomeKit Type |
|--------|-------------|
| `light` | Lightbulb |
| `switch` | Switch |
| `cover` | Window Covering / Garage Door |
| `climate` | Thermostat |
| `fan` | Fan |
| `lock` | Lock |
| `alarm_control_panel` | Security System |
| `camera` | Camera |
| `media_player` | Television |
| `sensor` | Sensor (limited) |
| `binary_sensor` | Sensor |

### Camera in HomeKit

```yaml
homekit:
  - name: "Camera Bridge"
    port: 21066
    filter:
      include_entities:
        - camera.front_door
    entity_config:
      camera.front_door:
        video_codec: copy  # or h264_omx for Pi
        audio_codec: copy
        stream_count: 3
        linked_doorbell_sensor: binary_sensor.doorbell
        linked_motion_sensor: binary_sensor.front_door_motion
```

---

## Samsung SmartThings

### Configuration

```yaml
# Via UI: Configuration > Integrations > SmartThings
# Requires Personal Access Token from SmartThings

# No YAML needed after setup
```

### Automation with SmartThings

```yaml
automation:
  - alias: "SmartThings Button Press"
    trigger:
      - platform: state
        entity_id: sensor.smartthings_button_action
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: sensor.smartthings_button_action
                state: "pushed"
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.living_room
          - conditions:
              - condition: state
                entity_id: sensor.smartthings_button_action
                state: "held"
            sequence:
              - service: scene.turn_on
                target:
                  entity_id: scene.movie_mode
```

### Device Health Monitoring

```yaml
automation:
  - alias: "SmartThings Device Offline Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.smartthings_hub_status
        to: "off"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "SmartThings Alert"
          message: "SmartThings Hub appears to be offline"
```

---

## Tuya / Smart Life

### Configuration Methods

| Method | Pros | Cons |
|--------|------|------|
| **Cloud** | Easy setup | Cloud dependency |
| **Local Tuya (HACS)** | Local control | Setup complexity |
| **Tuya Local** | No cloud | Device compatibility |

### Cloud Integration

```yaml
# Via UI: Configuration > Integrations > Tuya
# Requires Tuya IoT Platform account
```

### Local Tuya (HACS)

```yaml
# After HACS install and getting local keys
# Configure via UI or YAML

localtuya:
  - host: 192.168.1.50
    device_id: "your_device_id"
    local_key: "your_local_key"
    friendly_name: "Smart Plug"
    protocol_version: "3.3"
    entities:
      - platform: switch
        friendly_name: "Power"
        id: 1
      - platform: sensor
        friendly_name: "Current"
        id: 18
        device_class: current
        unit_of_measurement: "mA"
        scaling: 0.001
```

### Common Tuya Entities

```yaml
automation:
  - alias: "Tuya Smart Plug Power Monitor"
    trigger:
      - platform: numeric_state
        entity_id: sensor.smart_plug_power
        above: 500
    action:
      - service: notify.mobile_app
        data:
          message: "High power consumption detected on smart plug"
```

---

## Shelly

### Configuration Methods

| Method | Use Case |
|--------|----------|
| **Native Integration** | Easy, cloud optional |
| **MQTT** | Full local control |
| **CoIoT** | Local without MQTT |

### Native Integration

```yaml
# Auto-discovered
# Configuration > Integrations > Shelly
```

### MQTT Configuration

```yaml
# In Shelly device settings:
# Enable MQTT
# Set broker IP and credentials

# No HA YAML needed if using discovery
```

### Shelly Services

```yaml
# OTA update
service: update.install
target:
  entity_id: update.shelly_1_firmware

# Reboot device
service: button.press
target:
  entity_id: button.shelly_1_reboot
```

### Cover Control (Shelly 2.5)

```yaml
automation:
  - alias: "Close Blinds at Sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "+00:30:00"
    action:
      - service: cover.close_cover
        target:
          entity_id: cover.shelly_25_blinds

# Set position
service: cover.set_cover_position
target:
  entity_id: cover.shelly_25_blinds
data:
  position: 50  # 50% open
```

### Energy Monitoring

```yaml
sensor:
  - platform: template
    sensors:
      daily_energy_cost:
        friendly_name: "Daily Energy Cost"
        value_template: >
          {{ (states('sensor.shelly_em_channel_1_energy') | float * 0.15) | round(2) }}
        unit_of_measurement: "$"
```

---

## TP-Link Kasa

### Configuration

```yaml
# Auto-discovered via UI
# Configuration > Integrations > TP-Link Kasa Smart
```

### Manual Configuration

```yaml
# For static IP devices
tplink:
  discovery: false
  switch:
    - host: 192.168.1.100
    - host: 192.168.1.101
  light:
    - host: 192.168.1.102
```

### Device Features

| Device | Features |
|--------|----------|
| **HS100/110** | Switch, power monitoring |
| **KP115** | Switch, detailed energy |
| **HS200/210** | Wall switch |
| **KL130** | Color bulb |
| **KL50/60** | Dimmable bulb |
| **HS300** | Power strip |

### Power Monitoring Automation

```yaml
automation:
  - alias: "Washing Machine Done"
    trigger:
      - platform: numeric_state
        entity_id: sensor.washing_machine_current_consumption
        below: 5
        for:
          minutes: 2
    condition:
      - condition: numeric_state
        entity_id: sensor.washing_machine_current_consumption
        above: 0.1
    action:
      - service: notify.mobile_app
        data:
          message: "Washing machine cycle complete!"
```

---

## Google Calendar

Google Calendar enables schedule-based automations using your calendar events.

### Setup

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Google Calendar**
3. Follow OAuth authentication flow
4. Select calendars to import

### Entities Created

```yaml
# One calendar entity per calendar
calendar.personal
calendar.work
calendar.holidays

# Each calendar has:
# - State: on (event now) / off (no event)
# - Attributes: message, start_time, end_time, all_day, etc.
```

### Event Triggers

```yaml
# Trigger when event starts
automation:
  - alias: "Work Hours Started"
    trigger:
      - platform: calendar
        entity_id: calendar.work
        event: start
        offset: "-00:05:00"  # 5 minutes before
    action:
      - service: light.turn_on
        target:
          entity_id: light.office

# Trigger when event ends
automation:
  - alias: "Meeting Ended"
    trigger:
      - platform: calendar
        entity_id: calendar.work
        event: end
    action:
      - service: notify.mobile_app
        data:
          message: "Meeting '{{ trigger.calendar_event.summary }}' ended"
```

### Event Filtering

```yaml
# Trigger only for specific events
automation:
  - alias: "Vacation Mode"
    trigger:
      - platform: calendar
        entity_id: calendar.personal
        event: start
    condition:
      - condition: template
        value_template: >
          {{ 'vacation' in trigger.calendar_event.summary | lower
             or 'holiday' in trigger.calendar_event.summary | lower }}
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.vacation_mode
```

### Accessing Event Data

```yaml
# Current event details
automation:
  - alias: "Event Notification"
    trigger:
      - platform: calendar
        entity_id: calendar.work
        event: start
    action:
      - service: notify.mobile_app
        data:
          title: "Event Starting"
          message: >
            {{ trigger.calendar_event.summary }}
            {% if trigger.calendar_event.location %}
            📍 {{ trigger.calendar_event.location }}
            {% endif %}
            ⏰ {{ trigger.calendar_event.start.strftime('%H:%M') }} -
               {{ trigger.calendar_event.end.strftime('%H:%M') }}
```

### Template Sensor for Upcoming Events

```yaml
template:
  - trigger:
      - platform: time_pattern
        minutes: /15
    action:
      - service: calendar.get_events
        target:
          entity_id: calendar.work
        data:
          duration:
            hours: 24
        response_variable: events
    sensor:
      - name: "Next Work Event"
        state: >
          {% if events['calendar.work'].events %}
            {{ events['calendar.work'].events[0].summary }}
          {% else %}
            No events
          {% endif %}
        attributes:
          start: >
            {% if events['calendar.work'].events %}
              {{ events['calendar.work'].events[0].start }}
            {% endif %}
          event_count: "{{ events['calendar.work'].events | length }}"
```

### Schedule-Based Automations

```yaml
# Use calendar for complex schedules
automation:
  - alias: "Office Hours Lighting"
    trigger:
      - platform: calendar
        entity_id: calendar.work_schedule
        event: start
      - platform: calendar
        entity_id: calendar.work_schedule
        event: end
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event == 'start' }}"
            sequence:
              - service: scene.turn_on
                target:
                  entity_id: scene.office_daytime
        default:
          - service: light.turn_off
            target:
              entity_id: light.office

# Garbage collection reminder from calendar
automation:
  - alias: "Garbage Day Reminder"
    trigger:
      - platform: calendar
        entity_id: calendar.home
        event: start
        offset: "-12:00:00"  # 12 hours before
    condition:
      - condition: template
        value_template: >
          {{ 'garbage' in trigger.calendar_event.summary | lower
             or 'trash' in trigger.calendar_event.summary | lower }}
    action:
      - service: notify.mobile_app
        data:
          title: "🗑️ Garbage Day Tomorrow"
          message: "Don't forget to take out the bins!"
```

### Creating Calendar Events

```yaml
# Create event from automation
service: calendar.create_event
target:
  entity_id: calendar.home
data:
  summary: "HVAC Maintenance"
  description: "Annual furnace inspection"
  start_date_time: "2024-03-15 09:00:00"
  end_date_time: "2024-03-15 11:00:00"
  location: "123 Main St"

# All-day event
service: calendar.create_event
target:
  entity_id: calendar.home
data:
  summary: "Vacation"
  start_date: "2024-07-01"
  end_date: "2024-07-08"
```

### Dashboard Card

```yaml
# Calendar card
type: calendar
entities:
  - calendar.personal
  - calendar.work
  - calendar.holidays
initial_view: dayGridMonth  # listWeek, dayGridDay

# Custom agenda view
type: custom:atomic-calendar-revive
entities:
  - entity: calendar.personal
    color: blue
  - entity: calendar.work
    color: red
showProgressBar: true
maxDaysToShow: 7
```

### Multiple Calendar Patterns

```yaml
# Check if any calendar has events
template:
  - binary_sensor:
      - name: "Busy Now"
        state: >
          {{ is_state('calendar.work', 'on')
             or is_state('calendar.personal', 'on') }}

# Get events from multiple calendars
automation:
  - alias: "Morning Briefing"
    trigger:
      - platform: time
        at: "07:30:00"
    action:
      - service: calendar.get_events
        target:
          entity_id:
            - calendar.work
            - calendar.personal
        data:
          duration:
            hours: 12
        response_variable: all_events
      - service: notify.mobile_app
        data:
          title: "📅 Today's Schedule"
          message: >
            Work: {{ all_events['calendar.work'].events | length }} events
            Personal: {{ all_events['calendar.personal'].events | length }} events
```

---

## Integration Patterns

### Universal Device Control

```yaml
# Script for any media player
script:
  media_play_pause:
    alias: "Play/Pause Media"
    fields:
      target:
        description: "Target media player"
        example: "media_player.sonos_living_room"
    sequence:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ is_state(target, 'playing') }}"
            sequence:
              - service: media_player.media_pause
                target:
                  entity_id: "{{ target }}"
        default:
          - service: media_player.media_play
            target:
              entity_id: "{{ target }}"
```

### Multi-Platform Presence

```yaml
# Combine multiple presence sources
template:
  - binary_sensor:
      - name: "Anyone Home"
        state: >
          {{ is_state('device_tracker.phone_john', 'home')
             or is_state('device_tracker.phone_jane', 'home')
             or is_state('binary_sensor.hue_motion', 'on')
             or is_state('person.john', 'home')
             or is_state('person.jane', 'home') }}
        device_class: presence
```

### Unified Lighting Control

```yaml
script:
  set_room_brightness:
    alias: "Set Room Brightness"
    fields:
      room:
        description: "Room name"
      brightness:
        description: "Brightness percentage"
    sequence:
      - service: light.turn_on
        target:
          area_id: "{{ room }}"
        data:
          brightness_pct: "{{ brightness }}"
```

### Cross-Platform Scenes

```yaml
scene:
  - name: "Movie Night"
    entities:
      # Hue lights
      light.hue_living_room:
        state: "on"
        brightness: 30
        rgb_color: [100, 100, 255]
      # Sonos
      media_player.sonos_soundbar:
        state: "on"
        volume_level: 0.4
      # Smart plug (TV)
      switch.tv_power:
        state: "on"
      # Shelly blinds
      cover.living_room_blinds:
        state: "closed"
```

### Voice Assistant Fallback

```yaml
automation:
  - alias: "Announcement Fallback"
    mode: single
    trigger:
      - platform: event
        event_type: announcement_request
    action:
      - choose:
          # Try Alexa first
          - conditions:
              - condition: state
                entity_id: media_player.echo_kitchen
                state: "on"
            sequence:
              - service: notify.alexa_media
                data:
                  target: media_player.echo_kitchen
                  message: "{{ trigger.event.data.message }}"
                  data:
                    type: announce
          # Fallback to Sonos
          - conditions:
              - condition: state
                entity_id: media_player.sonos_kitchen
                state: "idle"
            sequence:
              - service: tts.speak
                target:
                  entity_id: media_player.sonos_kitchen
                data:
                  message: "{{ trigger.event.data.message }}"
        # Final fallback to phone notification
        default:
          - service: notify.mobile_app
            data:
              message: "{{ trigger.event.data.message }}"
```

---

## Best Practices

### Integration Selection

| Factor | Consideration |
|--------|---------------|
| **Local vs Cloud** | Prefer local for reliability |
| **Protocol** | Z-Wave/Zigbee for battery devices |
| **Ecosystem** | Balance features vs vendor lock-in |
| **Updates** | Consider firmware update frequency |

### Network Organization

```yaml
# VLAN separation recommended
# IoT devices: 192.168.10.x
# Home Assistant: 192.168.1.x with access to IoT VLAN

# Static IP for critical devices
# Hue Bridge, Sonos, Security cameras
```

### Entity Organization

```yaml
# Use consistent naming
# pattern: domain.location_device_function

light.living_room_ceiling_main
light.living_room_lamp_corner
sensor.living_room_temperature_hue
binary_sensor.living_room_motion_hue
```

### Fallback Automations

```yaml
automation:
  - alias: "Light Control with Fallback"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    action:
      - choose:
          # Primary: Hue
          - conditions:
              - condition: state
                entity_id: light.hue_living
                attribute: available
                state: true
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.hue_living
          # Fallback: Generic Zigbee
          - conditions:
              - condition: state
                entity_id: light.zigbee_living
                attribute: available
                state: true
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.zigbee_living
```

### Performance Tips

```yaml
# Limit polling intervals
sensor:
  - platform: template
    scan_interval: 60  # Reduce for non-critical sensors

# Group related automations
automation:
  - alias: "Multi-Motion Handler"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.motion_1
          - binary_sensor.motion_2
          - binary_sensor.motion_3
        to: "on"
    # Single automation handles multiple triggers
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Device unavailable | Network issue | Check device IP, ping |
| Slow response | Cloud latency | Use local integration |
| Missing entities | Discovery disabled | Re-add integration |
| Authentication fail | Token expired | Re-authenticate |

### Debug Logging

```yaml
# Enable debug for specific integration
logger:
  default: info
  logs:
    homeassistant.components.hue: debug
    homeassistant.components.sonos: debug
    homeassistant.components.tplink: debug
    aiohue: debug
    soco: debug
```

### Network Diagnostics

```yaml
# Template sensor for device availability
template:
  - sensor:
      - name: "Integration Health"
        state: >
          {% set unavailable = states | selectattr('state', 'eq', 'unavailable') | list | length %}
          {% if unavailable == 0 %}healthy
          {% elif unavailable < 5 %}degraded
          {% else %}critical{% endif %}
        attributes:
          unavailable_count: >
            {{ states | selectattr('state', 'eq', 'unavailable') | list | length }}
          unavailable_entities: >
            {{ states | selectattr('state', 'eq', 'unavailable') | map(attribute='entity_id') | list }}
```

### Integration Recovery

```yaml
automation:
  - alias: "Restart Integration on Failure"
    trigger:
      - platform: state
        entity_id: binary_sensor.hue_bridge_status
        to: "off"
        for:
          minutes: 5
    action:
      - service: homeassistant.reload_config_entry
        data:
          entry_id: "abc123"  # Get from .storage/core.config_entries
      - service: notify.mobile_app
        data:
          message: "Hue integration restarted due to connectivity issues"
```

### Factory Reset Procedures

| Device | Reset Method |
|--------|--------------|
| **Hue Bridge** | Hold button 10s until lights flash |
| **Sonos** | Settings > System > Factory Reset |
| **Shelly** | Hold button during boot until LED |
| **TP-Link** | Hold reset button 10s |
| **Tuya** | Device-specific, usually long press |

### Entity Not Updating

```yaml
# Force state refresh
service: homeassistant.update_entity
target:
  entity_id: sensor.problematic_sensor

# For specific integrations
service: hue.hue_refresh
data:
  bridge_id: "001788fffe123456"
```

---

## Integration Health Dashboard

```yaml
# Lovelace card for monitoring integrations
type: entities
title: Integration Health
entities:
  - entity: binary_sensor.hue_bridge
    name: Hue Bridge
  - entity: sensor.sonos_living_room_activity
    name: Sonos
  - entity: binary_sensor.smartthings_hub_status
    name: SmartThings
  - type: section
    label: Availability
  - entity: sensor.integration_health
    name: Overall Health
```

