# Home Assistant Best Practices Reference

## Table of Contents
- [Core Principles](#core-principles)
- [Naming Conventions](#naming-conventions)
- [File Organization](#file-organization)
- [Configuration Structure](#configuration-structure)
- [Automation Design](#automation-design)
- [Security Practices](#security-practices)
- [Performance Optimization](#performance-optimization)
- [Maintenance Procedures](#maintenance-procedures)
- [Testing Strategies](#testing-strategies)
- [Documentation Standards](#documentation-standards)
- [Common Patterns](#common-patterns)
- [Anti-Patterns](#anti-patterns)

---

## Core Principles

### Guiding Philosophy

| Principle | Description |
|-----------|-------------|
| **Simplicity** | Prefer simple solutions over complex ones |
| **Reliability** | Prioritize stable, predictable behavior |
| **Maintainability** | Write configs that are easy to understand and modify |
| **Modularity** | Separate concerns, use packages |
| **Testability** | Design for easy testing and debugging |

### Design Goals

```yaml
# Good automation characteristics:
# 1. Single responsibility - one purpose per automation
# 2. Clear naming - purpose obvious from name
# 3. Documented - comments explain "why"
# 4. Testable - can trigger manually
# 5. Observable - traces/logs available
```

---

## Naming Conventions

### Entity Naming

```yaml
# Pattern: domain.location_device_function
# Use: snake_case (lowercase with underscores)

# Good
light.living_room_ceiling
sensor.bedroom_temperature
binary_sensor.front_door_contact
switch.kitchen_coffee_maker

# Bad
light.LivingRoomLight      # CamelCase
sensor.temp1               # Unclear
binary_sensor.sensor_23    # Meaningless
switch.SW001               # Device code only
```

### Location Prefixes

```yaml
# Use consistent location names across all entities

# Recommended prefixes:
# living_room, bedroom, kitchen, bathroom
# garage, office, basement, attic
# front_yard, back_yard, porch
# hallway, entrance, stairs

# Examples
light.living_room_main
light.living_room_lamp
sensor.living_room_temperature
sensor.living_room_humidity
binary_sensor.living_room_motion
```

### Function Suffixes

```yaml
# Indicate entity purpose with suffix

# Sensors
sensor.office_temperature      # Measurement type
sensor.washer_power            # What it measures
sensor.car_battery_level       # Device + measurement

# Binary sensors
binary_sensor.garage_door      # Device name implies open/close
binary_sensor.kitchen_motion   # Detection type
binary_sensor.basement_water   # What it detects

# Switches
switch.garden_irrigation       # What it controls
switch.bedroom_fan             # Device controlled
```

### Automation Naming

```yaml
# Pattern: [Area] - [Trigger] - [Action]
# Be descriptive enough to understand from name alone

# Good
automation:
  - alias: "Living Room - Motion - Lights On"
  - alias: "Kitchen - Sunset - Close Blinds"
  - alias: "System - Startup - Send Notification"
  - alias: "Security - Door Open - Alert If Away"

# Bad
automation:
  - alias: "automation_1"        # Meaningless
  - alias: "test"                # Unclear
  - alias: "lights"              # Too vague
  - alias: "Motion Light Auto"   # Inconsistent format
```

### Script Naming

```yaml
# Pattern: action_target or target_action

# Good
script:
  morning_routine:
  goodnight_all:
  notify_all_devices:
  set_vacation_mode:
  reset_guest_access:

# Bad
script:
  script_1:
  do_stuff:
  misc:
```

### Helper Naming

```yaml
# Pattern: type_purpose

input_boolean:
  vacation_mode:
  guest_mode:
  automation_override:
  debug_mode:

input_select:
  home_mode:           # Options: home, away, vacation
  lighting_scene:      # Options: bright, dim, movie
  climate_preset:      # Options: comfort, eco, away

input_number:
  target_temperature:
  motion_timeout:
  notification_volume:
```

---

## File Organization

### Directory Structure

```
config/
├── configuration.yaml       # Main config (minimal)
├── secrets.yaml             # Sensitive data
├── automations.yaml         # Simple automations (UI)
├── scripts.yaml             # Simple scripts (UI)
├── scenes.yaml              # Scenes (UI)
│
├── packages/                # Modular configs
│   ├── areas/
│   │   ├── living_room.yaml
│   │   ├── bedroom.yaml
│   │   └── kitchen.yaml
│   ├── integrations/
│   │   ├── climate.yaml
│   │   ├── lighting.yaml
│   │   └── security.yaml
│   └── system/
│       ├── notifications.yaml
│       ├── presence.yaml
│       └── backup.yaml
│
├── custom_components/       # Third-party integrations
│
├── www/                     # Local web files
│   └── images/
│
├── blueprints/              # Automation blueprints
│   └── automation/
│
└── themes/                  # UI themes
```

### Package Organization

```yaml
# configuration.yaml
homeassistant:
  packages: !include_dir_named packages/

# Packages structure
packages/
├── areas/
│   └── living_room.yaml     # All living room configs
├── integrations/
│   └── lighting.yaml        # All lighting configs
└── features/
    └── presence.yaml        # Presence detection feature
```

### Package Example

```yaml
# packages/areas/living_room.yaml

# All living room related configuration in one file

# Helpers
input_boolean:
  living_room_occupied:
    name: Living Room Occupied

input_number:
  living_room_brightness:
    name: Living Room Brightness
    min: 0
    max: 100
    step: 10

# Template sensors
template:
  - sensor:
      - name: "Living Room Average Temperature"
        state: >
          {{ ((states('sensor.living_room_temp_1') | float +
               states('sensor.living_room_temp_2') | float) / 2) | round(1) }}
        unit_of_measurement: "°C"

# Automations
automation:
  - alias: "Living Room - Motion - Lights On"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    condition:
      - condition: state
        entity_id: sun.sun
        state: "below_horizon"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room_main

# Scripts
script:
  living_room_movie_mode:
    alias: "Living Room Movie Mode"
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.living_room_tv_backlight
        data:
          brightness: 50
      - service: light.turn_off
        target:
          entity_id: light.living_room_main
```

---

## Configuration Structure

### Main Configuration

```yaml
# configuration.yaml - Keep minimal

homeassistant:
  name: Home
  unit_system: metric
  time_zone: Europe/Stockholm
  currency: SEK
  packages: !include_dir_named packages/
  customize: !include customize.yaml

# Core integrations only
logger:
  default: info
  logs:
    homeassistant.components.automation: warning

recorder:
  purge_keep_days: 7
  exclude:
    domains:
      - automation
      - script

http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 172.30.33.0/24
```

### Secrets Management

```yaml
# secrets.yaml
# NEVER commit to version control

# API Keys
openweathermap_api_key: abcd1234
google_api_key: xyz789

# Credentials
mqtt_username: homeassistant
mqtt_password: secure_password

# Network
internal_url: http://192.168.1.100:8123
external_url: https://home.example.com

# Device IPs
hue_bridge_ip: 192.168.1.50
printer_ip: 192.168.1.60
```

```yaml
# Usage in configuration
weather:
  - platform: openweathermap
    api_key: !secret openweathermap_api_key
```

### Include Patterns

```yaml
# Single file include
automation: !include automations.yaml

# Directory of files as list
automation: !include_dir_list automations/
# Each file contains list items (starting with -)

# Directory as named mapping
homeassistant:
  packages: !include_dir_named packages/
# Each file name becomes key

# Directory merged into single mapping
sensor: !include_dir_merge_named sensors/
# Combines all files into single mapping
```

---

## Automation Design

### Single Responsibility

```yaml
# Good: One automation, one purpose
automation:
  - alias: "Living Room - Motion - Lights On"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room

  - alias: "Living Room - No Motion - Lights Off"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "off"
        for:
          minutes: 5
    action:
      - service: light.turn_off
        target:
          entity_id: light.living_room

# Bad: Multiple unrelated actions
automation:
  - alias: "Motion Handler"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
    action:
      - if: motion on
        then: turn on lights, send notification, start music, adjust climate
        else: turn off everything
```

### Condition Usage

```yaml
# Use conditions to prevent unwanted triggers

automation:
  - alias: "Motion Light with Conditions"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    condition:
      # Multiple conditions = AND logic
      - condition: state
        entity_id: sun.sun
        state: "below_horizon"
      - condition: state
        entity_id: input_boolean.automation_enabled
        state: "on"
      - condition: not
        conditions:
          - condition: state
            entity_id: input_boolean.guest_mode
            state: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

### Error Handling

```yaml
automation:
  - alias: "Robust Automation"
    trigger:
      - platform: state
        entity_id: binary_sensor.trigger
        to: "on"
    action:
      # Check entity availability before use
      - if:
          - condition: template
            value_template: "{{ states('light.target') not in ['unavailable', 'unknown'] }}"
        then:
          - service: light.turn_on
            target:
              entity_id: light.target
        else:
          - service: notify.admin
            data:
              message: "Light unavailable - automation failed"
```

### Variables Usage

```yaml
automation:
  - alias: "Dynamic Brightness Based on Time"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    variables:
      brightness: >
        {% set hour = now().hour %}
        {% if hour < 6 or hour > 22 %}
          30
        {% elif hour < 8 or hour > 20 %}
          70
        {% else %}
          100
        {% endif %}
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
        data:
          brightness_pct: "{{ brightness }}"
```

---

## Security Practices

### Authentication

```yaml
# Enable MFA
# Profile > Multi-factor Authentication

# Use long-lived tokens sparingly
# Regenerate periodically
# Store securely

# Limit API access
http:
  ip_ban_enabled: true
  login_attempts_threshold: 5
```

### Network Security

```yaml
# Use HTTPS externally
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem

# Trusted proxies only
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 172.30.33.0/24

# No direct external exposure
# Use reverse proxy (NGINX, Traefik)
```

### Secrets Protection

```yaml
# 1. Use secrets.yaml for all sensitive data
api_key: !secret service_api_key

# 2. Never log secrets
logger:
  filters:
    # Prevent secret logging
    homeassistant.core:
      - ".*password.*"

# 3. Exclude from backups if needed
# Or encrypt backups

# 4. Version control ignores
# .gitignore
secrets.yaml
*.pem
*.key
```

### Access Control

```yaml
# User permissions
# Settings > People > Users

# Create users with appropriate access:
# - Administrator: Full access
# - User: Basic control
# - Local only: No remote access

# Limit service exposure
homeassistant:
  # Control which services are exposed to voice assistants
  customize:
    switch.dangerous_switch:
      google_assistant: false
      alexa: false
```

---

## Performance Optimization

### Recorder Configuration

```yaml
recorder:
  # Reduce database size
  purge_keep_days: 5
  commit_interval: 1

  # Exclude high-frequency entities
  exclude:
    domains:
      - automation
      - script
      - scene
      - persistent_notification
    entity_globs:
      - sensor.*_linkquality
      - sensor.*_battery
    event_types:
      - service_removed
      - service_executed
      - platform_discovered

  # Include only what you need for history
  include:
    domains:
      - sensor
      - binary_sensor
      - climate
    entities:
      - light.living_room
```

### Template Optimization

```yaml
# Bad: Expensive template evaluated frequently
template:
  - sensor:
      - name: "All Lights On"
        state: >
          {{ states.light
             | selectattr('state', 'eq', 'on')
             | list
             | count }}
        # Evaluates on every state change

# Good: Use trigger-based for complex calculations
template:
  - trigger:
      - platform: time_pattern
        minutes: "/5"  # Every 5 minutes
      - platform: homeassistant
        event: start
    sensor:
      - name: "All Lights On"
        state: >
          {{ states.light
             | selectattr('state', 'eq', 'on')
             | list
             | count }}
```

### Polling Reduction

```yaml
# Reduce polling where possible
# Use push-based integrations when available

# If polling required, increase intervals
sensor:
  - platform: rest
    scan_interval: 300  # 5 minutes instead of default 30s

# Disable unused entities
# Settings > Devices & Services > [Device] > Disable
```

### Dashboard Performance

```yaml
# Limit entities per view
# Target: 30-50 entities max per view

# Use pagination
views:
  - title: Lights
    cards:
      - type: entity-filter
        # Shows only what's relevant
        entities: [...]
        state_filter:
          - "on"

# Reduce history graphs
type: history-graph
hours_to_show: 12  # Not 24
refresh_interval: 60  # Not real-time
```

---

## Maintenance Procedures

### Backup Strategy

```yaml
# Automated backups
automation:
  - alias: "System - Daily Backup"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: backup.create

# Backup retention
# Keep: 7 daily, 4 weekly, 3 monthly

# What to backup:
# - Full HA backup (includes everything)
# - Or selective: configuration only
```

### Update Procedure

```yaml
# 1. Read release notes
# 2. Check breaking changes
# 3. Backup current state
# 4. Update in test environment if possible
# 5. Update production
# 6. Verify critical automations
# 7. Monitor logs for 24h

# Update automation
automation:
  - alias: "System - Update Available Notification"
    trigger:
      - platform: state
        entity_id: update.home_assistant_core_update
        to: "on"
    action:
      - service: notify.admin
        data:
          title: "Update Available"
          message: >
            Home Assistant {{ state_attr('update.home_assistant_core_update', 'latest_version') }}
            is available
```

### Health Monitoring

```yaml
# Monitor system health
template:
  - sensor:
      - name: "System Health"
        state: >
          {% set unavailable = states | selectattr('state', 'eq', 'unavailable') | list | length %}
          {% if unavailable == 0 %}healthy
          {% elif unavailable < 5 %}degraded
          {% else %}critical{% endif %}
        attributes:
          unavailable_count: >
            {{ states | selectattr('state', 'eq', 'unavailable') | list | length }}

automation:
  - alias: "System - Health Alert"
    trigger:
      - platform: state
        entity_id: sensor.system_health
        to: "critical"
        for:
          minutes: 5
    action:
      - service: notify.admin
        data:
          title: "System Health Critical"
          message: "Multiple entities unavailable"
```

---

## Testing Strategies

### Manual Testing

```yaml
# Test automations manually
# Developer Tools > Services

service: automation.trigger
target:
  entity_id: automation.test_automation
data:
  skip_condition: false  # or true to bypass conditions

# Test scripts
service: script.turn_on
target:
  entity_id: script.test_script
```

### Template Testing

```yaml
# Developer Tools > Template

# Test conditions
{% if is_state('sun.sun', 'below_horizon') %}
  Condition passes
{% else %}
  Condition fails
{% endif %}

# Test service data
{{ {
  'entity_id': 'light.living_room',
  'brightness': 255
} }}

# Test complex templates
{% set lights_on = states.light | selectattr('state', 'eq', 'on') | list %}
Lights on: {{ lights_on | length }}
{% for light in lights_on %}
  - {{ light.entity_id }}
{% endfor %}
```

### Staging Environment

```yaml
# Create test helpers
input_boolean:
  test_mode:
    name: Test Mode
    icon: mdi:test-tube

# Use in automations
automation:
  - alias: "Test - Motion Light"
    trigger:
      - platform: state
        entity_id: input_boolean.test_trigger
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.test_mode
        state: "on"
    action:
      - service: system_log.write
        data:
          message: "Test automation triggered"
          level: info
```

### Trace Analysis

```yaml
# Enable traces for debugging
automation:
  - alias: "Debug Automation"
    trace:
      stored_traces: 20  # Keep more traces

# View traces:
# Settings > Automations > [Automation] > Traces

# Trace shows:
# - Trigger information
# - Condition evaluation
# - Action execution
# - Variable values
# - Errors
```

---

## Documentation Standards

### Code Comments

```yaml
automation:
  # Purpose: Turn on lights when motion detected after sunset
  # Trigger: Motion sensor state change
  # Dependencies: sun integration, motion sensor
  # Author: John Doe
  # Last updated: 2024-01-15
  - alias: "Living Room - Motion - Lights On"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    condition:
      # Only when dark outside
      - condition: state
        entity_id: sun.sun
        state: "below_horizon"
      # Not when TV is on (movie mode)
      - condition: state
        entity_id: media_player.living_room_tv
        state: "off"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room_main
```

### README Files

```markdown
# config/README.md

# Home Assistant Configuration

## Structure
- `configuration.yaml` - Main configuration
- `packages/` - Modular configurations by area/feature
- `www/` - Local web files

## Conventions
- Entity naming: `domain.location_device_function`
- Automation naming: `Area - Trigger - Action`

## Dependencies
- HACS integrations: [list]
- Custom components: [list]

## Credentials
Stored in `secrets.yaml` (not in version control)
Required secrets:
- `mqtt_password`
- `api_key_weather`

## Troubleshooting
[Common issues and solutions]
```

### Change Log

```markdown
# config/CHANGELOG.md

# Changelog

## [2024-01-15]
### Added
- Motion-activated lighting for hallway
- Vacation mode automation

### Changed
- Increased motion timeout from 5 to 10 minutes
- Updated climate schedules for winter

### Fixed
- Garage door notification delay

## [2024-01-10]
### Added
- Initial configuration
```

---

## Common Patterns

### Presence-Based Automation

```yaml
# Use binary sensor for "anyone home"
template:
  - binary_sensor:
      - name: "Anyone Home"
        state: >
          {{ is_state('person.john', 'home')
             or is_state('person.jane', 'home') }}
        device_class: presence

automation:
  - alias: "Presence - Away - Secure Home"
    trigger:
      - platform: state
        entity_id: binary_sensor.anyone_home
        to: "off"
        for:
          minutes: 10
    action:
      - service: lock.lock
        target:
          entity_id: all
      - service: climate.set_preset_mode
        target:
          entity_id: climate.thermostat
        data:
          preset_mode: away
```

### Notification Patterns

```yaml
# Centralized notification script
script:
  notify_family:
    alias: "Notify Family"
    fields:
      message:
        description: "Message to send"
      title:
        description: "Notification title"
        default: "Home Assistant"
      priority:
        description: "Priority level"
        default: "normal"
    sequence:
      - service: notify.mobile_app_john
        data:
          title: "{{ title }}"
          message: "{{ message }}"
      - if:
          - condition: template
            value_template: "{{ priority == 'high' }}"
        then:
          - service: notify.mobile_app_jane
            data:
              title: "{{ title }}"
              message: "{{ message }}"
```

### Mode-Based Control

```yaml
input_select:
  home_mode:
    name: Home Mode
    options:
      - Normal
      - Away
      - Sleep
      - Guest
      - Vacation

automation:
  - alias: "Mode - Away - Set Climate"
    trigger:
      - platform: state
        entity_id: input_select.home_mode
        to: "Away"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.thermostat
        data:
          temperature: 16
```

---

## Anti-Patterns

### Avoid These

```yaml
# Bad: Hardcoded values
action:
  - service: light.turn_on
    data:
      brightness: 255  # Use input_number instead

# Bad: Duplicate automations
# Copy-pasted for each room
# Use: Scripts with variables, or templates

# Bad: Overly complex single automation
# 200+ lines with multiple if/then/else
# Use: Split into focused automations

# Bad: No conditions
automation:
  - alias: "Always Run"
    trigger: [...]
    # Missing conditions = runs regardless of context

# Bad: Polling when events available
sensor:
  - platform: command_line
    command: "check_status.sh"
    scan_interval: 1  # Every second!
# Use: Event-based triggers
```

### Common Mistakes

```yaml
# Wrong: Missing "to" state
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    # Triggers on ANY state change, including attributes

# Correct: Specify state
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: "on"

# Wrong: Using default values that might fail
{{ states('sensor.temp') | float }}
# Fails if unavailable

# Correct: Provide default
{{ states('sensor.temp') | float(0) }}

# Wrong: Service call with wrong target format
service: light.turn_on
entity_id: light.living_room  # Deprecated

# Correct: Use target
service: light.turn_on
target:
  entity_id: light.living_room
```

### Performance Anti-Patterns

```yaml
# Bad: History graph with too much data
type: history-graph
hours_to_show: 168  # 1 week of data!

# Bad: Real-time polling for slow-changing data
scan_interval: 1

# Bad: Complex template in frequently-triggered automation
# Template re-evaluates every trigger

# Bad: Recording everything
recorder:
  # No exclusions = huge database
```

