# Mushroom Cards Reference

> The most popular custom card collection for Home Assistant dashboards

## Overview

Mushroom Cards provide a clean, modern UI for Home Assistant with minimal configuration. They're designed to work seamlessly with HA's theming system and offer a consistent look across all card types.

### Key Features

- **Clean Design** - Minimalist aesthetic with soft colors
- **Easy Configuration** - Simple YAML with sensible defaults
- **Template Support** - Jinja2 templates for dynamic content
- **Animation Support** - Subtle animations for state changes
- **Mobile Optimized** - Touch-friendly with responsive layouts
- **Theme Integration** - Adapts to HA themes automatically

---

## Installation

### Via HACS

```yaml
# 1. Open HACS → Frontend
# 2. Search "Mushroom"
# 3. Install "Mushroom"
# 4. Add to resources (automatic via HACS)

# Verify installation:
# Developer Tools → Check Configuration
# Resources should include mushroom
```

### Manual Installation

```yaml
# Download from GitHub:
# https://github.com/piitaya/lovelace-mushroom

# Add to resources:
# configuration.yaml
lovelace:
  mode: yaml
  resources:
    - url: /local/mushroom/mushroom.js
      type: module
```

---

## Card Types

### mushroom-entity-card

The most versatile card - works with any entity:

```yaml
type: custom:mushroom-entity-card
entity: sensor.living_room_temperature
name: Temperature
icon: mdi:thermometer
icon_color: orange

# With secondary info
type: custom:mushroom-entity-card
entity: sensor.living_room_temperature
secondary_info: last-changed

# Secondary info options:
# - state
# - last-changed
# - last-updated
# - position
# - tilt-position
# - brightness
# - none
```

### mushroom-light-card

Optimized for light entities:

```yaml
type: custom:mushroom-light-card
entity: light.living_room
name: Living Room
icon: mdi:ceiling-light
use_light_color: true

# With controls
type: custom:mushroom-light-card
entity: light.bedroom
show_brightness_control: true
show_color_temp_control: true
show_color_control: true
collapsible_controls: true

# Layout options
type: custom:mushroom-light-card
entity: light.kitchen
layout: horizontal  # or vertical
fill_container: true
```

### mushroom-climate-card

For climate/thermostat entities:

```yaml
type: custom:mushroom-climate-card
entity: climate.living_room
name: Thermostat
show_temperature_control: true
collapsible_controls: true

# HVAC modes display
type: custom:mushroom-climate-card
entity: climate.bedroom
hvac_modes:
  - heat
  - cool
  - auto
  - "off"
```

### mushroom-cover-card

For covers (blinds, garage doors, etc.):

```yaml
type: custom:mushroom-cover-card
entity: cover.bedroom_blinds
name: Blinds
show_position_control: true
show_buttons_control: true

# Specific buttons
type: custom:mushroom-cover-card
entity: cover.garage_door
show_buttons_control: true
buttons:
  - open
  - stop
  - close
```

### mushroom-fan-card

For fan entities:

```yaml
type: custom:mushroom-fan-card
entity: fan.bedroom
name: Ceiling Fan
show_percentage_control: true
show_oscillate_control: true
collapsible_controls: true

# Custom icon animation
type: custom:mushroom-fan-card
entity: fan.living_room
icon_animation: true  # Spins when on
```

### mushroom-media-player-card

For media players:

```yaml
type: custom:mushroom-media-player-card
entity: media_player.living_room_speaker
name: Speaker
use_media_info: true
show_volume_level: true
media_controls:
  - on_off
  - play_pause_stop
  - previous
  - next
volume_controls:
  - volume_mute
  - volume_set
  - volume_buttons

# Collapsible controls
type: custom:mushroom-media-player-card
entity: media_player.tv
collapsible_controls: true
```

### mushroom-person-card

For person entities:

```yaml
type: custom:mushroom-person-card
entity: person.john
name: John

# Customized
type: custom:mushroom-person-card
entity: person.jane
layout: vertical
primary_info: name
secondary_info: state
```

### mushroom-vacuum-card

For vacuum entities:

```yaml
type: custom:mushroom-vacuum-card
entity: vacuum.roborock
name: Robot Vacuum
commands:
  - start_pause
  - stop
  - locate
  - return_home

# Icon animation when cleaning
icon_animation: true
```

### mushroom-lock-card

For lock entities:

```yaml
type: custom:mushroom-lock-card
entity: lock.front_door
name: Front Door
```

### mushroom-alarm-control-panel-card

For alarm panels:

```yaml
type: custom:mushroom-alarm-control-panel-card
entity: alarm_control_panel.home
name: Alarm
states:
  - armed_home
  - armed_away
  - disarmed
```

### mushroom-select-card

For select/input_select entities:

```yaml
type: custom:mushroom-select-card
entity: input_select.home_mode
name: Home Mode
icon: mdi:home
```

### mushroom-number-card

For number/input_number entities:

```yaml
type: custom:mushroom-number-card
entity: input_number.volume_level
name: Volume
icon: mdi:volume-high
display_mode: slider  # or buttons

# Custom layout
type: custom:mushroom-number-card
entity: input_number.thermostat_offset
layout: horizontal
```

---

## Chips Card

Display multiple small badges/chips:

```yaml
type: custom:mushroom-chips-card
chips:
  # Entity chip
  - type: entity
    entity: sensor.outside_temperature
    icon: mdi:thermometer

  # Weather chip
  - type: weather
    entity: weather.home
    show_temperature: true
    show_conditions: true

  # Light chip
  - type: light
    entity: light.all_lights
    name: Lights

  # Action chip
  - type: action
    icon: mdi:door
    tap_action:
      action: navigate
      navigation_path: /lovelace/security

  # Back chip (navigation)
  - type: back

  # Spacer chip
  - type: spacer

  # Template chip
  - type: template
    icon: mdi:account-group
    content: "{{ states('sensor.people_home') }} home"
    tap_action:
      action: more-info
      entity: group.family

  # Conditional chip
  - type: conditional
    conditions:
      - entity: binary_sensor.front_door
        state: "on"
    chip:
      type: entity
      entity: binary_sensor.front_door
      icon_color: red
```

### Chips Layout Options

```yaml
type: custom:mushroom-chips-card
chips:
  - type: entity
    entity: sensor.temp
  - type: entity
    entity: sensor.humidity
alignment: center  # start, center, end, justify
```

---

## Template Card

The most powerful card - fully customizable:

```yaml
type: custom:mushroom-template-card
entity: sensor.living_room_temperature
primary: "Living Room"
secondary: "{{ states(entity) }}°C"
icon: mdi:thermometer
icon_color: >
  {% set temp = states(entity) | float(20) %}
  {% if temp < 18 %}
    blue
  {% elif temp < 24 %}
    green
  {% else %}
    red
  {% endif %}

# Multi-entity template
type: custom:mushroom-template-card
primary: "Climate Status"
secondary: >
  {{ states('sensor.indoor_temp') }}°C /
  {{ states('sensor.indoor_humidity') }}%
icon: mdi:home-thermometer
icon_color: |
  {% if is_state('climate.living_room', 'heat') %}
    orange
  {% elif is_state('climate.living_room', 'cool') %}
    blue
  {% else %}
    grey
  {% endif %}
tap_action:
  action: navigate
  navigation_path: /lovelace/climate

# Badge template
type: custom:mushroom-template-card
primary: Security
secondary: >
  {% set open = states.binary_sensor
    | selectattr('attributes.device_class', 'eq', 'door')
    | selectattr('state', 'eq', 'on')
    | list | count %}
  {% if open > 0 %}
    {{ open }} door{{ 's' if open > 1 }} open
  {% else %}
    All secure
  {% endif %}
icon: >
  {% set open = states.binary_sensor
    | selectattr('attributes.device_class', 'eq', 'door')
    | selectattr('state', 'eq', 'on')
    | list | count %}
  {{ 'mdi:door-open' if open > 0 else 'mdi:door-closed-lock' }}
icon_color: >
  {% set open = states.binary_sensor
    | selectattr('attributes.device_class', 'eq', 'door')
    | selectattr('state', 'eq', 'on')
    | list | count %}
  {{ 'red' if open > 0 else 'green' }}
```

---

## Title Card

Section headers for your dashboard:

```yaml
type: custom:mushroom-title-card
title: Living Room
subtitle: Lights and climate
alignment: center  # left, center, right

# With action
type: custom:mushroom-title-card
title: Security
subtitle: "{{ states('sensor.open_doors') }} doors open"
tap_action:
  action: navigate
  navigation_path: /lovelace/security
```

---

## Styling and Customization

### Icon Colors

```yaml
# Named colors
icon_color: red
icon_color: green
icon_color: blue
icon_color: orange
icon_color: yellow
icon_color: purple
icon_color: pink
icon_color: cyan
icon_color: teal
icon_color: amber
icon_color: deep-orange
icon_color: deep-purple
icon_color: indigo
icon_color: light-blue
icon_color: light-green
icon_color: lime
icon_color: brown
icon_color: grey
icon_color: blue-grey
icon_color: disabled

# CSS variable
icon_color: var(--primary-color)

# RGB (template only)
icon_color: rgb(255, 128, 0)
```

### Layout Options

```yaml
# Layout mode
layout: horizontal  # Default - icon left, text right
layout: vertical    # Icon above text

# Fill container
fill_container: true  # Card fills grid cell

# Hide elements
primary_info: none  # Hide primary text
secondary_info: none  # Hide secondary text
icon: none  # Hide icon (some cards)
```

### Card-Mod Integration

Customize with CSS using card-mod:

```yaml
type: custom:mushroom-entity-card
entity: light.bedroom
card_mod:
  style: |
    ha-card {
      --ha-card-background: rgba(0,0,0,0.3);
      --ha-card-border-radius: 20px;
      --ha-card-box-shadow: none;
    }
    mushroom-shape-icon {
      --icon-size: 48px;
    }

# Glow effect when on
type: custom:mushroom-light-card
entity: light.living_room
card_mod:
  style: |
    ha-card {
      {% if is_state('light.living_room', 'on') %}
      box-shadow: 0 0 20px 5px rgba(255, 200, 100, 0.5);
      {% endif %}
    }

# Pulsing animation
type: custom:mushroom-entity-card
entity: binary_sensor.motion
card_mod:
  style: |
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }
    ha-card {
      {% if is_state('binary_sensor.motion', 'on') %}
      animation: pulse 2s ease-in-out infinite;
      {% endif %}
    }
```

---

## Common Patterns

### Room Card

```yaml
type: custom:mushroom-template-card
entity: light.living_room
primary: Living Room
secondary: >
  {% set lights_on = states.light
    | selectattr('entity_id', 'search', 'living_room')
    | selectattr('state', 'eq', 'on')
    | list | count %}
  {% set temp = states('sensor.living_room_temperature') %}
  {{ lights_on }} lights on · {{ temp }}°C
icon: mdi:sofa
icon_color: >
  {% set lights_on = states.light
    | selectattr('entity_id', 'search', 'living_room')
    | selectattr('state', 'eq', 'on')
    | list | count %}
  {{ 'amber' if lights_on > 0 else 'disabled' }}
tap_action:
  action: navigate
  navigation_path: /lovelace/living-room
hold_action:
  action: call-service
  service: light.toggle
  target:
    entity_id: light.living_room_all
```

### Status Chip Bar

```yaml
type: custom:mushroom-chips-card
chips:
  # Presence
  - type: template
    icon: mdi:account-group
    content: "{{ states('sensor.people_home') }}"
    icon_color: "{{ 'green' if states('sensor.people_home') | int > 0 else 'grey' }}"
    tap_action:
      action: more-info
      entity: group.family

  # Lights
  - type: template
    icon: mdi:lightbulb-group
    content: "{{ states('sensor.lights_on') }}"
    icon_color: "{{ 'amber' if states('sensor.lights_on') | int > 0 else 'grey' }}"
    tap_action:
      action: call-service
      service: light.turn_off
      target:
        entity_id: light.all_lights

  # Climate
  - type: template
    icon: mdi:thermometer
    content: "{{ states('sensor.indoor_temperature') }}°C"
    icon_color: >
      {% set temp = states('sensor.indoor_temperature') | float(20) %}
      {{ 'blue' if temp < 18 else 'red' if temp > 26 else 'green' }}

  # Security
  - type: template
    icon: >
      {{ 'mdi:shield-check' if is_state('alarm_control_panel.home', 'armed_away')
         else 'mdi:shield-home' if is_state('alarm_control_panel.home', 'armed_home')
         else 'mdi:shield-off' }}
    icon_color: >
      {{ 'green' if 'armed' in states('alarm_control_panel.home') else 'red' }}
    tap_action:
      action: navigate
      navigation_path: /lovelace/security
alignment: end
```

### Quick Action Buttons

```yaml
type: horizontal-stack
cards:
  - type: custom:mushroom-template-card
    primary: Home
    icon: mdi:home
    tap_action:
      action: call-service
      service: script.home_mode
    layout: vertical

  - type: custom:mushroom-template-card
    primary: Away
    icon: mdi:home-export-outline
    tap_action:
      action: call-service
      service: script.away_mode
    layout: vertical

  - type: custom:mushroom-template-card
    primary: Night
    icon: mdi:weather-night
    tap_action:
      action: call-service
      service: script.night_mode
    layout: vertical

  - type: custom:mushroom-template-card
    primary: Guest
    icon: mdi:account-multiple
    tap_action:
      action: call-service
      service: script.guest_mode
    layout: vertical
```

### Device Status Overview

```yaml
type: custom:mushroom-template-card
primary: Device Status
secondary: >
  {% set unavailable = states | selectattr('state', 'eq', 'unavailable') | list | count %}
  {% set low_battery = states.sensor
    | selectattr('attributes.device_class', 'defined')
    | selectattr('attributes.device_class', 'eq', 'battery')
    | selectattr('state', 'lt', '20')
    | list | count %}
  {% if unavailable > 0 or low_battery > 0 %}
    {{ unavailable }} offline · {{ low_battery }} low battery
  {% else %}
    All systems normal
  {% endif %}
icon: >
  {% set unavailable = states | selectattr('state', 'eq', 'unavailable') | list | count %}
  {{ 'mdi:alert-circle' if unavailable > 0 else 'mdi:check-circle' }}
icon_color: >
  {% set unavailable = states | selectattr('state', 'eq', 'unavailable') | list | count %}
  {{ 'red' if unavailable > 0 else 'green' }}
tap_action:
  action: navigate
  navigation_path: /lovelace/system
```

---

## Tap Actions

All Mushroom cards support tap, hold, and double-tap actions:

```yaml
type: custom:mushroom-entity-card
entity: light.living_room
tap_action:
  action: toggle

hold_action:
  action: more-info

double_tap_action:
  action: call-service
  service: light.turn_on
  data:
    brightness_pct: 100

# Available actions:
# - toggle
# - more-info
# - navigate
# - url
# - call-service
# - assist
# - none

# Navigate action
tap_action:
  action: navigate
  navigation_path: /lovelace/room

# URL action
tap_action:
  action: url
  url_path: https://example.com

# Service call
tap_action:
  action: call-service
  service: script.movie_mode
  target:
    entity_id: script.movie_mode
  data:
    variable: value

# Voice assistant
tap_action:
  action: assist
```

---

## Grid Layouts

### Standard Grid

```yaml
type: grid
columns: 3
square: false
cards:
  - type: custom:mushroom-light-card
    entity: light.living_room
  - type: custom:mushroom-light-card
    entity: light.bedroom
  - type: custom:mushroom-light-card
    entity: light.kitchen
  - type: custom:mushroom-light-card
    entity: light.bathroom
  - type: custom:mushroom-light-card
    entity: light.office
  - type: custom:mushroom-light-card
    entity: light.hallway
```

### Responsive Grid

```yaml
# Works well with layout-card (HACS)
type: custom:layout-card
layout_type: masonry
layout:
  width: 150
  max_cols: 4
cards:
  - type: custom:mushroom-entity-card
    entity: sensor.temperature
  - type: custom:mushroom-entity-card
    entity: sensor.humidity
```

---

## Performance Tips

### Reduce Template Evaluations

```yaml
# Instead of multiple template cards checking same entity
# Use one template card with combined info

# Bad - 3 template evaluations
type: vertical-stack
cards:
  - type: custom:mushroom-template-card
    primary: "{{ states('sensor.temp') }}"
  - type: custom:mushroom-template-card
    primary: "{{ states('sensor.temp') | float > 25 }}"
  - type: custom:mushroom-template-card
    icon_color: "{{ 'red' if states('sensor.temp') | float > 25 }}"

# Good - 1 template evaluation
type: custom:mushroom-template-card
entity: sensor.temp
primary: "{{ states(entity) }}°C"
icon_color: "{{ 'red' if states(entity) | float > 25 else 'green' }}"
```

### Use Entity Instead of Template

```yaml
# Use entity-card when possible
# Template-card is more CPU intensive

# Simple display - use entity card
type: custom:mushroom-entity-card
entity: sensor.temperature

# Complex logic - use template card
type: custom:mushroom-template-card
entity: sensor.temperature
primary: >
  {% if states(entity) | float > 25 %}
    Hot: {{ states(entity) }}°C
  {% else %}
    {{ states(entity) }}°C
  {% endif %}
```

### Limit Card-Mod Animations

```yaml
# Animations consume CPU
# Limit to important indicators

# OK - single important indicator
type: custom:mushroom-entity-card
entity: binary_sensor.smoke
card_mod:
  style: |
    @keyframes blink {
      50% { opacity: 0.5; }
    }
    ha-card {
      {% if is_state('binary_sensor.smoke', 'on') %}
      animation: blink 1s infinite;
      {% endif %}
    }

# Avoid - animations on every card
```

---

## Troubleshooting

### Cards Not Loading

```yaml
# 1. Clear browser cache
# 2. Check resources are loaded
#    Developer Tools → Resources

# 3. Verify HACS installation
#    HACS → Frontend → Mushroom

# 4. Check console for errors
#    F12 → Console

# 5. Manual resource add
lovelace:
  resources:
    - url: /hacsfiles/lovelace-mushroom/mushroom.js
      type: module
```

### Templates Not Working

```yaml
# Check template syntax in Developer Tools
# Developer Tools → Template

# Common issues:
# - Missing entity: in template card
# - Wrong template delimiters
# - Entity not available

# Debug with secondary
type: custom:mushroom-template-card
entity: sensor.temperature
primary: Debug
secondary: "State: {{ states(entity) }} | Type: {{ states(entity) | type_debug }}"
```

### Icon Colors Not Changing

```yaml
# Verify template syntax
icon_color: >
  {% if is_state('light.bedroom', 'on') %}
    amber
  {% else %}
    disabled
  {% endif %}

# Note: icon_color requires exact color names
# or CSS variables, not hex codes in templates
```

---

## Related References

- [Dashboard Cards](dashboard-cards.md) - Native card reference
- [Jinja2 Templates](jinja2-templates.md) - Template syntax
- [Custom Components](custom-components.md) - HACS setup
- [Dashboards](dashboards.md) - Dashboard configuration
