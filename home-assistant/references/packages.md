# Home Assistant Packages Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Package Structure](#package-structure)
- [Enabling Packages](#enabling-packages)
- [Domain Merging](#domain-merging)
- [Organization Strategies](#organization-strategies)
- [Package Examples](#package-examples)
- [Multi-File Packages](#multi-file-packages)
- [Package Dependencies](#package-dependencies)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Packages bundle related configuration components into self-contained files. Instead of splitting by domain (all automations in one file), you group by feature or area.

### Key Terms

| Term | Description |
|------|-------------|
| **Package** | Self-contained configuration bundle |
| **Domain** | Configuration type (automation, sensor, etc.) |
| **Merge** | Combine package domains with main config |
| **Namespace** | Package name prefixed to IDs |

### Packages vs Split Config

| Approach | Use Case | Example |
|----------|----------|---------|
| Split by domain | Large single-purpose configs | All sensors in sensors.yaml |
| Packages | Feature-based grouping | All lighting config together |

### Benefits of Packages

- **Self-contained**: All related config in one file
- **Portable**: Easy to share or move between installs
- **Organized**: Group by feature, room, or device
- **Maintainable**: Find related config quickly

---

## Package Structure

### Basic Package

```yaml
# packages/lighting.yaml

# Input helpers for this feature
input_boolean:
  motion_lights_enabled:
    name: Motion Lights Enabled
    icon: mdi:motion-sensor

input_number:
  motion_timeout:
    name: Motion Timeout
    min: 1
    max: 30
    step: 1
    unit_of_measurement: min

# Automations for this feature
automation:
  - id: pkg_motion_light
    alias: "[Lighting] Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.motion_lights_enabled
        state: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway

# Scripts for this feature
script:
  all_lights_off:
    alias: "[Lighting] All Lights Off"
    sequence:
      - service: light.turn_off
        target:
          entity_id: all
```

### Complete Package Example

```yaml
# packages/climate_control.yaml

# ===== INPUT HELPERS =====
input_boolean:
  climate_schedule_enabled:
    name: Climate Schedule
    icon: mdi:calendar-clock

  climate_away_mode:
    name: Climate Away Mode
    icon: mdi:airplane

input_number:
  climate_comfort_temp:
    name: Comfort Temperature
    min: 18
    max: 26
    step: 0.5
    unit_of_measurement: "°C"
    icon: mdi:thermometer

  climate_away_temp:
    name: Away Temperature
    min: 15
    max: 20
    step: 0.5
    unit_of_measurement: "°C"
    icon: mdi:thermometer-low

input_datetime:
  climate_morning_time:
    name: Morning Heat Time
    has_date: false
    has_time: true

  climate_night_time:
    name: Night Setback Time
    has_date: false
    has_time: true

# ===== TEMPLATE SENSORS =====
template:
  - sensor:
      - name: "Climate Target Temperature"
        unit_of_measurement: "°C"
        state: >
          {% if is_state('input_boolean.climate_away_mode', 'on') %}
            {{ states('input_number.climate_away_temp') }}
          {% else %}
            {{ states('input_number.climate_comfort_temp') }}
          {% endif %}

# ===== AUTOMATIONS =====
automation:
  - id: pkg_climate_morning
    alias: "[Climate] Morning Schedule"
    trigger:
      - platform: time
        at: input_datetime.climate_morning_time
    condition:
      - condition: state
        entity_id: input_boolean.climate_schedule_enabled
        state: "on"
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.climate_comfort_temp') | float }}"

  - id: pkg_climate_night
    alias: "[Climate] Night Setback"
    trigger:
      - platform: time
        at: input_datetime.climate_night_time
    condition:
      - condition: state
        entity_id: input_boolean.climate_schedule_enabled
        state: "on"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.climate_away_temp') | float }}"

  - id: pkg_climate_away
    alias: "[Climate] Away Mode Changed"
    trigger:
      - platform: state
        entity_id: input_boolean.climate_away_mode
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: >
            {% if trigger.to_state.state == 'on' %}
              {{ states('input_number.climate_away_temp') | float }}
            {% else %}
              {{ states('input_number.climate_comfort_temp') | float }}
            {% endif %}

# ===== SCRIPTS =====
script:
  climate_boost:
    alias: "[Climate] Boost Mode"
    sequence:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: 24
      - delay: "01:00:00"
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ states('input_number.climate_comfort_temp') | float }}"
```

---

## Enabling Packages

### Directory-Based (Recommended)

```yaml
# configuration.yaml
homeassistant:
  packages: !include_dir_named packages/
```

```
config/
├── configuration.yaml
└── packages/
    ├── lighting.yaml
    ├── climate.yaml
    ├── security.yaml
    └── presence.yaml
```

### Single File Include

```yaml
# configuration.yaml
homeassistant:
  packages:
    lighting: !include packages/lighting.yaml
    climate: !include packages/climate.yaml
```

### Inline Packages

```yaml
# configuration.yaml
homeassistant:
  packages:
    simple_package:
      input_boolean:
        test_toggle:
          name: Test Toggle
```

### Mixed Approach

```yaml
# configuration.yaml
homeassistant:
  packages:
    # Directory-based
    !include_dir_named packages/

    # Additional inline
    debug:
      logger:
        default: debug
```

---

## Domain Merging

### How Domains Merge

Packages merge their domains with the main configuration. Same domains from different packages are combined.

```yaml
# packages/package_a.yaml
automation:
  - id: auto_a
    alias: Automation A
    trigger: ...

# packages/package_b.yaml
automation:
  - id: auto_b
    alias: Automation B
    trigger: ...

# Result: Both automations exist
```

### Unique ID Requirements

```yaml
# Each entity needs unique ID across all packages

# packages/lighting.yaml
automation:
  - id: pkg_lighting_motion  # Unique!
    alias: Motion Light

# packages/security.yaml
automation:
  - id: pkg_security_motion  # Different!
    alias: Motion Alert

# Naming convention: pkg_[package]_[function]
```

### Domain Restrictions

Some domains can only be defined once:

```yaml
# These can be in packages (mergeable):
# - automation
# - script
# - sensor
# - binary_sensor
# - input_boolean, input_number, input_select, etc.
# - template
# - group

# These typically can't be split:
# - homeassistant (core settings)
# - http
# - recorder
# - logger (can be, but may conflict)
```

---

## Organization Strategies

### By Feature

```
packages/
├── lighting.yaml         # All lighting automation
├── climate.yaml          # HVAC control
├── security.yaml         # Alarms, locks, cameras
├── presence.yaml         # Person tracking
├── notifications.yaml    # Alert system
└── media.yaml           # Entertainment control
```

### By Room/Area

```
packages/
├── living_room.yaml
├── kitchen.yaml
├── bedroom.yaml
├── bathroom.yaml
├── garage.yaml
└── outdoor.yaml
```

### By Device/Integration

```
packages/
├── hue_lights.yaml
├── zwave_devices.yaml
├── zigbee_sensors.yaml
├── esphome_devices.yaml
└── tasmota_switches.yaml
```

### Hybrid Approach

```
packages/
├── core/                 # System-wide
│   ├── presence.yaml
│   └── notifications.yaml
├── rooms/               # Room-specific
│   ├── living_room.yaml
│   └── bedroom.yaml
└── integrations/        # Integration-specific
    ├── hue.yaml
    └── sonos.yaml
```

---

## Package Examples

### Vacation Mode Package

```yaml
# packages/vacation_mode.yaml

input_boolean:
  vacation_mode:
    name: Vacation Mode
    icon: mdi:airplane-takeoff

input_datetime:
  vacation_start:
    name: Vacation Start
    has_date: true
    has_time: false

  vacation_end:
    name: Vacation End
    has_date: true
    has_time: false

automation:
  - id: pkg_vacation_auto_enable
    alias: "[Vacation] Auto Enable"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: template
        value_template: >
          {{ states('input_datetime.vacation_start') == now().strftime('%Y-%m-%d') }}
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.vacation_mode

  - id: pkg_vacation_auto_disable
    alias: "[Vacation] Auto Disable"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: template
        value_template: >
          {{ states('input_datetime.vacation_end') == now().strftime('%Y-%m-%d') }}
    action:
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.vacation_mode

  - id: pkg_vacation_lights_simulation
    alias: "[Vacation] Light Simulation"
    trigger:
      - platform: sun
        event: sunset
    condition:
      - condition: state
        entity_id: input_boolean.vacation_mode
        state: "on"
    action:
      - delay:
          minutes: "{{ range(5, 30) | random }}"
      - service: light.turn_on
        target:
          entity_id: light.living_room
      - delay:
          minutes: "{{ range(60, 180) | random }}"
      - service: light.turn_off
        target:
          entity_id: light.living_room

script:
  vacation_quick_enable:
    alias: "[Vacation] Quick Enable"
    sequence:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.vacation_mode
      - service: climate.set_preset_mode
        target:
          entity_id: climate.thermostat
        data:
          preset_mode: away
      - service: notify.mobile_app
        data:
          message: "Vacation mode enabled"
```

### Guest Mode Package

```yaml
# packages/guest_mode.yaml

input_boolean:
  guest_mode:
    name: Guest Mode
    icon: mdi:account-multiple

input_text:
  guest_wifi_password:
    name: Guest WiFi Password
    mode: text
    max: 32

automation:
  - id: pkg_guest_mode_on
    alias: "[Guest] Mode Activated"
    trigger:
      - platform: state
        entity_id: input_boolean.guest_mode
        to: "on"
    action:
      # Unlock smart lock temporarily
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      # Set comfortable temperature
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: 22
      # Turn on guest room light
      - service: light.turn_on
        target:
          entity_id: light.guest_room
        data:
          brightness_pct: 80
      # Disable motion-triggered alarms
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.motion_alarms_enabled

  - id: pkg_guest_mode_off
    alias: "[Guest] Mode Deactivated"
    trigger:
      - platform: state
        entity_id: input_boolean.guest_mode
        to: "off"
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.motion_alarms_enabled
      - service: lock.lock
        target:
          entity_id: lock.front_door

script:
  guest_welcome:
    alias: "[Guest] Welcome Announcement"
    sequence:
      - service: tts.speak
        target:
          entity_id: tts.google
        data:
          message: "Welcome! The WiFi password is {{ states('input_text.guest_wifi_password') }}"
          media_player_entity_id: media_player.living_room
```

### Notification System Package

```yaml
# packages/notifications.yaml

input_boolean:
  notifications_enabled:
    name: Notifications Enabled
    icon: mdi:bell

  critical_only:
    name: Critical Alerts Only
    icon: mdi:bell-alert

input_select:
  notification_mode:
    name: Notification Mode
    options:
      - All
      - Important
      - Critical Only
      - Silent
    icon: mdi:bell-cog

timer:
  notification_cooldown:
    name: Notification Cooldown
    duration: "00:30:00"

counter:
  daily_notifications:
    name: Daily Notifications
    initial: 0
    step: 1

automation:
  - id: pkg_notify_reset_counter
    alias: "[Notify] Reset Daily Counter"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: counter.reset
        target:
          entity_id: counter.daily_notifications

script:
  notify_family:
    alias: "[Notify] Send to Family"
    mode: queued
    fields:
      title:
        description: Notification title
        example: "Alert"
      message:
        description: Notification message
        example: "Something happened"
      priority:
        description: Priority level
        example: "normal"
    sequence:
      - condition: state
        entity_id: input_boolean.notifications_enabled
        state: "on"
      - choose:
          - conditions:
              - condition: state
                entity_id: input_select.notification_mode
                state: "Silent"
            sequence:
              - stop: "Notifications silenced"
          - conditions:
              - condition: state
                entity_id: input_select.notification_mode
                state: "Critical Only"
              - condition: template
                value_template: "{{ priority != 'critical' }}"
            sequence:
              - stop: "Only critical notifications allowed"
      - service: counter.increment
        target:
          entity_id: counter.daily_notifications
      - service: notify.mobile_app_phone
        data:
          title: "{{ title }}"
          message: "{{ message }}"
```

---

## Multi-File Packages

### Nested Package Structure

```yaml
# configuration.yaml
homeassistant:
  packages: !include_dir_named packages/
```

```
packages/
└── lighting/
    ├── __init__.yaml    # Main package file
    ├── helpers.yaml
    └── automations.yaml
```

```yaml
# packages/lighting/__init__.yaml
# Import other files
!include helpers.yaml
!include automations.yaml
```

### Alternative: Merge in Package

```yaml
# packages/lighting.yaml
# Combine multiple includes

input_boolean: !include lighting/helpers.yaml
automation: !include lighting/automations.yaml
```

---

## Package Dependencies

### Handling Dependencies

```yaml
# Package that depends on another

# packages/security.yaml
# Depends on: notifications.yaml

automation:
  - id: pkg_security_alert
    alias: "[Security] Motion Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.alarm_armed
        state: "on"
    action:
      # Uses script from notifications.yaml
      - service: script.notify_family
        data:
          title: "Security Alert"
          message: "Motion detected!"
          priority: critical
```

### Document Dependencies

```yaml
# packages/security.yaml
# ======================
# Security Package
# ======================
#
# Dependencies:
# - packages/notifications.yaml (provides script.notify_family)
# - packages/presence.yaml (provides input_boolean.away_mode)
#
# Entities provided:
# - input_boolean.alarm_armed
# - automation.security_*
# - script.arm_security
```

---

## Common Patterns

### Package Naming Convention

```yaml
# Use consistent ID prefixes
automation:
  - id: pkg_lighting_motion    # pkg_[package]_[function]
  - id: pkg_lighting_sunset

script:
  lighting_all_off:            # [package]_[function]
  lighting_movie_mode:

input_boolean:
  lighting_motion_enabled:     # [package]_[feature]_[type]
```

### Automation Aliases

```yaml
# Use prefixed aliases for clarity
automation:
  - id: pkg_climate_morning
    alias: "[Climate] Morning Schedule"  # [Package] Description

  - id: pkg_security_arm
    alias: "[Security] Auto Arm"
```

### Package Header Template

```yaml
# =============================================
# Package: [Name]
# Description: [What this package does]
# Author: [Your name]
# Version: 1.0.0
# =============================================
#
# Dependencies:
# - [Other packages this depends on]
#
# Entities Created:
# - input_boolean.[list]
# - automation.[list]
# - script.[list]
#
# =============================================

# Package content below...
```

---

## Best Practices

### Self-Contained Packages

```yaml
# Good: Package includes everything it needs
# packages/motion_lights.yaml

input_boolean:
  motion_lights_enabled:
    name: Motion Lights

input_number:
  motion_timeout:
    name: Timeout
    min: 1
    max: 30

automation:
  - id: pkg_motion_lights
    alias: "[Motion] Lights"
    # Uses entities defined above
```

### Unique IDs

```yaml
# Always use unique IDs with package prefix
automation:
  - id: pkg_vacation_enable     # Unique
    alias: "[Vacation] Enable"

  - id: pkg_vacation_disable    # Unique
    alias: "[Vacation] Disable"
```

### Documentation

```yaml
# Document package purpose and usage
# ====================================
# Guest Mode Package
# ====================================
#
# Enable guest mode when visitors arrive.
# Disables security alerts and unlocks door.
#
# To use:
# 1. Toggle input_boolean.guest_mode
# 2. Or call script.guest_mode_enable
#
# ====================================
```

### Group Related Entities

```yaml
# Keep related items together in package

# ===== HELPERS =====
input_boolean:
  feature_enabled:
    name: Feature Enabled

# ===== SENSORS =====
template:
  - sensor:
      - name: Feature Status
        state: "..."

# ===== AUTOMATIONS =====
automation:
  - id: pkg_feature_auto
    alias: Feature Automation

# ===== SCRIPTS =====
script:
  feature_run:
    alias: Run Feature
```

---

## Troubleshooting

### Package Not Loading

| Problem | Cause | Solution |
|---------|-------|----------|
| Package ignored | Not in packages dir | Check directory name |
| Syntax error | Invalid YAML | Validate YAML syntax |
| Duplicate ID | Same ID in another package | Use unique prefixed IDs |
| Domain conflict | Same key twice | Check for duplicates |

### Debug Package Loading

```yaml
# Enable debug logging
logger:
  default: info
  logs:
    homeassistant.config: debug
```

### Check Configuration

```bash
# Validate configuration
ha core check

# Or in Docker
docker exec homeassistant python -m homeassistant --script check_config
```

### Common Errors

```yaml
# Error: Duplicate key
# Two packages define same input_boolean name
input_boolean:
  my_toggle:  # Conflict if defined elsewhere!

# Fix: Use package prefix
input_boolean:
  pkg_lighting_my_toggle:

# Error: Entity not found
# Automation references entity from another package not loaded
action:
  - service: script.other_package_script
    # May fail if other package has error

# Fix: Check dependent packages load correctly
```

### Reload Packages

```yaml
# Most package contents can be reloaded
# Developer Tools > YAML > Reload:
# - Automations
# - Scripts
# - Input helpers
# - Template entities

# Some require restart:
# - New packages added
# - Package file renamed
# - Structural changes
```

### Validate Package Structure

```yaml
# Correct structure
homeassistant:
  packages: !include_dir_named packages/

# packages/test.yaml content:
input_boolean:
  test:
    name: Test

# NOT:
packages:  # Wrong! This key shouldn't be in package file
  input_boolean:
    test:
      name: Test
```
