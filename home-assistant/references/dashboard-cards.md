# Home Assistant Dashboard Cards Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Entity Cards](#entity-cards)
- [Media Cards](#media-cards)
- [Information Cards](#information-cards)
- [Control Cards](#control-cards)
- [Layout Cards](#layout-cards)
- [Special Cards](#special-cards)
- [Popular Custom Cards](#popular-custom-cards)
- [Card Actions](#card-actions)
- [Card Styling](#card-styling)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Cards are the building blocks of Home Assistant dashboards.

### Card Structure

```yaml
# Basic card structure
type: card-type           # Required
entity: entity_id         # Usually required
title: "Card Title"       # Optional
name: "Override Name"     # Optional
icon: mdi:icon-name       # Optional
```

### Card Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Entity** | Display/control entities | entities, button, light |
| **Media** | Media players, cameras | media-control, picture |
| **Information** | Display data | markdown, gauge, history |
| **Control** | User input | input controls |
| **Layout** | Organize cards | grid, horizontal-stack |
| **Special** | Maps, iframes | map, iframe, webpage |

---

## Entity Cards

### Entities Card

Display multiple entities in a list.

```yaml
type: entities
title: Living Room
show_header_toggle: true  # Toggle all entities
state_color: true
entities:
  # Simple entity
  - light.living_room

  # With options
  - entity: switch.tv
    name: Television
    icon: mdi:television

  # Secondary info
  - entity: sensor.temperature
    secondary_info: last-changed

  # With action buttons
  - entity: cover.blinds
    type: custom:slider-entity-row

  # Section divider
  - type: section
    label: Climate

  # Buttons row
  - type: buttons
    entities:
      - script.scene_bright
      - script.scene_dim

  # Attribute display
  - type: attribute
    entity: climate.thermostat
    attribute: current_temperature
    name: Current Temp
    suffix: "°C"

  # Conditional row
  - type: conditional
    conditions:
      - entity: sun.sun
        state: below_horizon
    row:
      entity: light.outdoor
```

### Entity Card (Single)

Single entity with large display.

```yaml
type: entity
entity: sensor.temperature
name: Room Temperature
icon: mdi:thermometer
unit: "°C"
state_color: true
attribute: current_temperature  # Show attribute instead
```

### Button Card

Simple toggle button.

```yaml
type: button
entity: light.living_room
name: Living Room
icon: mdi:lightbulb
show_name: true
show_icon: true
show_state: true
tap_action:
  action: toggle
hold_action:
  action: more-info
icon_height: 40px
```

### Light Card

Specialized light control.

```yaml
type: light
entity: light.living_room
name: Main Light
icon: mdi:ceiling-light
features:
  - type: light-brightness
  - type: light-color-temp
```

### Glance Card

Compact overview of multiple entities.

```yaml
type: glance
title: Quick Status
columns: 5
show_name: true
show_icon: true
show_state: true
state_color: true
entities:
  - entity: person.john
    name: John
  - entity: alarm_control_panel.home
    name: Alarm
  - entity: lock.front_door
    name: Lock
    tap_action:
      action: toggle
  - entity: binary_sensor.motion
    name: Motion
  - entity: sensor.temperature
    name: Temp
```

### Sensor Card

Display sensor with optional graph.

```yaml
type: sensor
entity: sensor.temperature
name: Temperature
icon: mdi:thermometer
graph: line  # line or none
hours_to_show: 24
detail: 2  # 1 (hourly) or 2 (detailed)
unit: "°C"
```

### Thermostat Card

Climate control interface.

```yaml
type: thermostat
entity: climate.living_room
name: Living Room Climate
features:
  - type: climate-hvac-modes
    hvac_modes:
      - heat
      - cool
      - auto
      - "off"
  - type: climate-preset-modes
```

### Humidifier Card

Humidifier control.

```yaml
type: humidifier
entity: humidifier.bedroom
name: Bedroom Humidifier
features:
  - type: humidifier-modes
  - type: humidifier-toggle
```

### Tile Card

Modern compact entity card.

```yaml
type: tile
entity: light.living_room
name: Living Room
icon: mdi:lightbulb
color: amber
show_entity_picture: false
vertical: false
features:
  - type: light-brightness
  - type: light-color-temp
tap_action:
  action: toggle
icon_tap_action:
  action: more-info
```

### Area Card

Overview of an area.

```yaml
type: area
area: living_room
navigation_path: /lovelace/living-room
show_camera: true
```

---

## Media Cards

### Media Control Card

Full media player control.

```yaml
type: media-control
entity: media_player.living_room
```

### Picture Card

Simple image display.

```yaml
type: picture
image: /local/images/room.jpg
tap_action:
  action: navigate
  navigation_path: /lovelace/rooms
```

### Picture Entity Card

Entity overlaid on image.

```yaml
type: picture-entity
entity: camera.front_door
name: Front Door
show_name: true
show_state: true
camera_view: live  # auto, live
tap_action:
  action: more-info
```

### Picture Glance Card

Multiple entities over image.

```yaml
type: picture-glance
title: Living Room
image: /local/images/living-room.jpg
camera_image: camera.living_room  # Alternative to image
entities:
  - entity: light.living_room
    tap_action:
      action: toggle
  - entity: binary_sensor.motion
  - entity: sensor.temperature
```

### Picture Elements Card

Interactive floor plan.

```yaml
type: picture-elements
image: /local/floorplan.svg
elements:
  # State icon
  - type: state-icon
    entity: light.living_room
    style:
      top: 30%
      left: 25%
    tap_action:
      action: toggle

  # State badge
  - type: state-badge
    entity: sensor.temperature
    style:
      top: 50%
      left: 75%

  # State label
  - type: state-label
    entity: sensor.humidity
    style:
      top: 60%
      left: 75%
      color: white

  # Icon element
  - type: icon
    icon: mdi:door
    style:
      top: 10%
      left: 50%
    tap_action:
      action: toggle
      entity: lock.front_door

  # Image element
  - type: image
    entity: binary_sensor.motion
    image: /local/icons/motion-off.png
    state_image:
      "on": /local/icons/motion-on.png
    style:
      top: 40%
      left: 10%
      width: 50px

  # Conditional element
  - type: conditional
    conditions:
      - entity: alarm_control_panel.home
        state: armed_away
    elements:
      - type: icon
        icon: mdi:shield-lock
        style:
          top: 5%
          right: 5%
```

---

## Information Cards

### Markdown Card

Rich text with templates.

```yaml
type: markdown
title: Welcome
content: |
  ## Good {{ 'morning' if now().hour < 12 else 'evening' }}!

  **Current Status:**
  - Temperature: {{ states('sensor.temperature') }}°C
  - Humidity: {{ states('sensor.humidity') }}%

  {% if is_state('person.john', 'home') %}
  👤 John is home
  {% else %}
  🚗 John is away
  {% endif %}

  ### Upcoming Events
  {% for event in state_attr('calendar.home', 'events')[:3] %}
  - {{ event.summary }}
  {% endfor %}
```

### Gauge Card

Visual gauge display.

```yaml
type: gauge
entity: sensor.cpu_usage
name: CPU
min: 0
max: 100
unit: "%"
needle: true
severity:
  green: 0
  yellow: 50
  red: 80
```

### History Graph Card

Historical data visualization.

```yaml
type: history-graph
title: Temperature History
hours_to_show: 24
refresh_interval: 60
entities:
  - entity: sensor.living_room_temperature
    name: Living Room
  - entity: sensor.bedroom_temperature
    name: Bedroom
  - entity: sensor.outdoor_temperature
    name: Outside
```

### Statistics Graph Card

Statistical data display.

```yaml
type: statistics-graph
title: Energy Statistics
entities:
  - sensor.daily_energy
period:
  calendar:
    period: day
stat_types:
  - mean
  - min
  - max
  - sum
days_to_show: 7
```

### Logbook Card

Activity log display.

```yaml
type: logbook
title: Recent Activity
entities:
  - binary_sensor.motion
  - lock.front_door
  - alarm_control_panel.home
hours_to_show: 24
```

### Calendar Card

Calendar events display.

```yaml
type: calendar
entities:
  - calendar.home
  - calendar.work
initial_view: dayGridMonth  # dayGridMonth, dayGridWeek, dayGridDay, listWeek
```

### Weather Forecast Card

Weather display.

```yaml
type: weather-forecast
entity: weather.home
show_forecast: true
forecast_type: daily  # daily, hourly, twice_daily
secondary_info_attribute: humidity
```

### Energy Cards

```yaml
# Energy distribution
type: energy-distribution
link_dashboard: true

# Energy date picker
type: energy-date-selection

# Energy usage graph
type: energy-usage-graph

# Solar production
type: energy-solar-graph

# Energy sources
type: energy-sources-table
```

### Todo List Card

Task list display.

```yaml
type: todo-list
entity: todo.shopping_list
title: Shopping List
```

---

## Control Cards

### Alarm Panel Card

```yaml
type: alarm-panel
entity: alarm_control_panel.home
name: Home Alarm
states:
  - arm_home
  - arm_away
  - arm_night
```

### Conditional Card

Show/hide based on conditions.

```yaml
type: conditional
conditions:
  - condition: state
    entity: sun.sun
    state: below_horizon
  - condition: numeric_state
    entity: sensor.illuminance
    below: 100
card:
  type: entities
  title: Night Lights
  entities:
    - light.porch
    - light.pathway
```

### Entity Filter Card

Dynamic entity list.

```yaml
type: entity-filter
entities:
  - entity: light.living_room
  - entity: light.bedroom
  - entity: light.kitchen
  - entity: light.bathroom
state_filter:
  - "on"
card:
  type: glance
  title: Lights On
show_empty: false
```

---

## Layout Cards

### Grid Card

Arrange cards in a grid.

```yaml
type: grid
columns: 3
square: true
cards:
  - type: button
    entity: light.living_room
  - type: button
    entity: light.bedroom
  - type: button
    entity: light.kitchen
  - type: button
    entity: switch.tv
  - type: button
    entity: cover.garage
  - type: button
    entity: lock.front_door
```

### Horizontal Stack

Side by side cards.

```yaml
type: horizontal-stack
cards:
  - type: button
    entity: script.leave_home
    name: Leave
  - type: button
    entity: script.arrive_home
    name: Home
  - type: button
    entity: script.goodnight
    name: Night
```

### Vertical Stack

Cards stacked vertically.

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Lights
    entities:
      - light.living_room
      - light.bedroom
  - type: entities
    title: Climate
    entities:
      - climate.thermostat
      - sensor.humidity
```

---

## Special Cards

### Map Card

Display entity locations.

```yaml
type: map
entities:
  - entity: person.john
  - entity: device_tracker.car
  - entity: zone.home
    label_mode: name
geo_location_sources:
  - all
default_zoom: 14
hours_to_show: 24
dark_mode: true
```

### Iframe Card

Embed external content.

```yaml
type: iframe
url: https://embed.windy.com/embed2.html
aspect_ratio: 16:9
title: Weather Radar
```

### Webpage Card

Embedded web content.

```yaml
type: webpage
url: https://www.home-assistant.io
title: Home Assistant
aspect_ratio: 16:9
```

### Empty State Card

Placeholder content.

```yaml
type: custom:hui-element
card_type: empty-state
icon: mdi:home
title: Welcome
content: Add your first card to get started
```

---

## Popular Custom Cards

### Button Card (HACS)

Highly customizable button.

```yaml
type: custom:button-card
entity: light.living_room
name: Living Room
icon: mdi:ceiling-light
color_type: icon
show_state: true
show_last_changed: true
tap_action:
  action: toggle
hold_action:
  action: more-info
state:
  - value: "on"
    color: rgb(255, 200, 100)
    icon: mdi:ceiling-light
  - value: "off"
    color: var(--disabled-text-color)
styles:
  card:
    - border-radius: 15px
    - padding: 10px
  icon:
    - width: 40px
  name:
    - font-size: 14px
    - font-weight: bold
```

### Mini Graph Card (HACS)

Compact sensor graphs.

```yaml
type: custom:mini-graph-card
entities:
  - entity: sensor.temperature
    name: Temperature
  - entity: sensor.humidity
    name: Humidity
    y_axis: secondary
hours_to_show: 24
points_per_hour: 2
line_width: 2
hour24: true
show:
  labels: true
  points: false
  legend: true
  fill: fade
```

### Mushroom Cards (HACS)

Modern minimalist cards.

```yaml
# Mushroom Light Card
type: custom:mushroom-light-card
entity: light.living_room
name: Living Room
icon: mdi:ceiling-light
show_brightness_control: true
show_color_temp_control: true
show_color_control: true
use_light_color: true
collapsible_controls: true

# Mushroom Entity Card
type: custom:mushroom-entity-card
entity: sensor.temperature
name: Temperature
icon: mdi:thermometer
primary_info: state
secondary_info: last-changed
icon_color: orange

# Mushroom Template Card
type: custom:mushroom-template-card
entity: sensor.power
primary: "Power"
secondary: "{{ states('sensor.power') }} W"
icon: mdi:flash
icon_color: >
  {% if states('sensor.power') | float > 1000 %}
    red
  {% else %}
    green
  {% endif %}
```

### Card Mod (HACS)

CSS styling for any card.

```yaml
type: entities
entities:
  - light.living_room
card_mod:
  style: |
    ha-card {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .card-header {
      color: white;
      font-weight: 600;
    }
```

### Stack In Card (HACS)

Combine cards without borders.

```yaml
type: custom:stack-in-card
mode: vertical
cards:
  - type: custom:mushroom-entity-card
    entity: sensor.temperature
  - type: custom:mini-graph-card
    entities:
      - sensor.temperature
    show:
      name: false
      icon: false
      state: false
```

### Swipe Card (HACS)

Swipeable card container.

```yaml
type: custom:swipe-card
cards:
  - type: picture-entity
    entity: camera.front_door
  - type: picture-entity
    entity: camera.back_yard
  - type: picture-entity
    entity: camera.garage
parameters:
  pagination:
    type: bullets
```

### Layout Card (HACS)

Advanced layout control.

```yaml
type: custom:layout-card
layout_type: custom:grid-layout
layout:
  grid-template-columns: 1fr 2fr
  grid-template-rows: auto
  grid-template-areas: |
    "sidebar main"
cards:
  - type: entities
    view_layout:
      grid-area: sidebar
    entities:
      - light.living_room
  - type: picture-entity
    view_layout:
      grid-area: main
    entity: camera.living_room
```

### Auto Entities (HACS)

Automatically generate entity lists.

```yaml
type: custom:auto-entities
card:
  type: entities
  title: All Lights
filter:
  include:
    - domain: light
      state: "on"
  exclude:
    - entity_id: "*_group"
sort:
  method: name
```

### ApexCharts Card (HACS)

Advanced charting.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Energy Usage
graph_span: 7d
span:
  start: day
series:
  - entity: sensor.daily_energy
    type: column
    group_by:
      func: sum
      duration: 1d
```

---

## Card Actions

### Action Types

| Action | Description |
|--------|-------------|
| `toggle` | Toggle entity state |
| `more-info` | Show entity dialog |
| `call-service` | Call a service |
| `navigate` | Navigate to view |
| `url` | Open external URL |
| `fire-dom-event` | Custom event |
| `none` | No action |

### Action Configuration

```yaml
type: button
entity: light.living_room
tap_action:
  action: toggle

hold_action:
  action: call-service
  service: light.turn_on
  service_data:
    entity_id: light.living_room
    brightness_pct: 100

double_tap_action:
  action: navigate
  navigation_path: /lovelace/lights
```

### Call Service Action

```yaml
tap_action:
  action: call-service
  service: script.turn_on
  target:
    entity_id: script.movie_mode
  data:
    variables:
      brightness: 50
  confirmation:
    text: "Start movie mode?"
```

### Navigate Action

```yaml
tap_action:
  action: navigate
  navigation_path: /lovelace/room-detail

# To another dashboard
tap_action:
  action: navigate
  navigation_path: /mobile-dashboard/home
```

### URL Action

```yaml
tap_action:
  action: url
  url_path: https://www.home-assistant.io
```

### Fire DOM Event

```yaml
# For browser_mod integration
tap_action:
  action: fire-dom-event
  browser_mod:
    service: browser_mod.popup
    data:
      title: Detailed View
      content:
        type: entities
        entities:
          - light.living_room
```

---

## Card Styling

### Basic CSS with Card Mod

```yaml
type: entities
card_mod:
  style: |
    ha-card {
      /* Background */
      background: rgba(0, 0, 0, 0.5);
      background-image: url("/local/bg.jpg");
      background-size: cover;

      /* Border */
      border: 2px solid var(--primary-color);
      border-radius: 20px;

      /* Shadow */
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);

      /* Text */
      color: white;
      font-family: 'Roboto', sans-serif;
    }
```

### State-Based Styling

```yaml
type: entities
card_mod:
  style: |
    ha-card {
      {% if is_state('alarm_control_panel.home', 'armed_away') %}
        border: 2px solid red;
        background: rgba(255, 0, 0, 0.1);
      {% elif is_state('alarm_control_panel.home', 'armed_home') %}
        border: 2px solid orange;
      {% else %}
        border: 2px solid green;
      {% endif %}
    }
```

### Element Styling

```yaml
type: entities
card_mod:
  style: |
    /* Card header */
    .card-header {
      background: linear-gradient(90deg, #1a237e, #3949ab);
      color: white;
      padding: 16px;
    }

    /* Entity rows */
    .entities {
      padding: 8px;
    }

    /* Individual state */
    state-badge {
      transform: scale(1.2);
    }
```

### Theme Variables in CSS

```yaml
card_mod:
  style: |
    ha-card {
      background: var(--card-background-color);
      border-color: var(--primary-color);
      color: var(--primary-text-color);
      border-radius: var(--ha-card-border-radius);
    }
```

### Animation

```yaml
card_mod:
  style: |
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }

    ha-card {
      {% if is_state('binary_sensor.motion', 'on') %}
        animation: pulse 1s infinite;
        border: 2px solid red;
      {% endif %}
    }
```

---

## Common Patterns

### Room Card Pattern

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-template-card
    primary: Living Room
    secondary: >
      {{ states('sensor.living_room_temperature') }}°C •
      {{ states('sensor.living_room_humidity') }}%
    icon: mdi:sofa
    icon_color: >
      {% if is_state('light.living_room', 'on') %}amber{% else %}grey{% endif %}
    tap_action:
      action: navigate
      navigation_path: /lovelace/living-room

  - type: custom:mushroom-chips-card
    chips:
      - type: entity
        entity: light.living_room
        tap_action:
          action: toggle
      - type: entity
        entity: climate.living_room
      - type: entity
        entity: media_player.living_room
```

### Climate Control Card

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.living_room

  - type: horizontal-stack
    cards:
      - type: button
        entity: climate.living_room
        name: Heat
        icon: mdi:fire
        tap_action:
          action: call-service
          service: climate.set_hvac_mode
          target:
            entity_id: climate.living_room
          data:
            hvac_mode: heat
      - type: button
        entity: climate.living_room
        name: Cool
        icon: mdi:snowflake
        tap_action:
          action: call-service
          service: climate.set_hvac_mode
          target:
            entity_id: climate.living_room
          data:
            hvac_mode: cool
      - type: button
        entity: climate.living_room
        name: "Off"
        icon: mdi:power
        tap_action:
          action: call-service
          service: climate.set_hvac_mode
          target:
            entity_id: climate.living_room
          data:
            hvac_mode: "off"
```

### Security Overview

```yaml
type: vertical-stack
cards:
  - type: alarm-panel
    entity: alarm_control_panel.home

  - type: glance
    title: Doors & Windows
    columns: 4
    entities:
      - entity: binary_sensor.front_door
        name: Front
      - entity: binary_sensor.back_door
        name: Back
      - entity: binary_sensor.garage_door
        name: Garage
      - entity: lock.front_door
        name: Lock

  - type: conditional
    conditions:
      - entity: binary_sensor.any_door_open
        state: "on"
    card:
      type: markdown
      content: |
        ## ⚠️ Warning
        One or more doors are open!
```

### Media Center

```yaml
type: vertical-stack
cards:
  - type: media-control
    entity: media_player.living_room

  - type: horizontal-stack
    cards:
      - type: button
        icon: mdi:spotify
        name: Spotify
        tap_action:
          action: call-service
          service: media_player.select_source
          target:
            entity_id: media_player.living_room
          data:
            source: Spotify
      - type: button
        icon: mdi:television
        name: TV
        tap_action:
          action: call-service
          service: media_player.select_source
          target:
            entity_id: media_player.living_room
          data:
            source: TV

  - type: custom:mini-media-player
    entity: media_player.living_room
    artwork: cover
    source: full
```

---

## Best Practices

### Performance

| Practice | Benefit |
|----------|---------|
| Limit cards per view | Faster loading |
| Use native cards | Better optimization |
| Reduce history range | Less data processing |
| Lazy load images | Faster initial render |

```yaml
# Optimize history graph
type: history-graph
hours_to_show: 12  # Instead of 24
refresh_interval: 300  # 5 minutes instead of default
```

### Accessibility

```yaml
# Use clear names
type: button
entity: light.living_room
name: "Living Room Light"  # Not "lr_l"

# High contrast
card_mod:
  style: |
    ha-card {
      color: white;
      background: #1a1a1a;
    }

# Large touch targets
type: grid
square: true
cards:
  - type: button
    icon_height: 60px
```

### Mobile Considerations

```yaml
# Touch-friendly
type: grid
columns: 2
square: true
cards:
  - type: button
    entity: light.living_room
    tap_action:
      action: toggle
    hold_action:
      action: more-info

# Responsive columns
# Use view-level settings
type: masonry
```

### Consistency

```yaml
# Use templates for repeated patterns
# cards/light-button.yaml
type: button
entity: "{{ entity }}"
name: "{{ name }}"
icon: mdi:lightbulb
tap_action:
  action: toggle
hold_action:
  action: more-info
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Card not loading | Missing resource | Add resource in dashboard settings |
| Styling not applied | Wrong selector | Check CSS specificity |
| Template not updating | Caching | Force refresh browser |
| Action not working | Wrong service format | Check service syntax |

### Debug Cards

```yaml
# Show all entity attributes
type: markdown
content: |
  ```json
  {{ state_attr('light.living_room', 'supported_color_modes') | tojson(indent=2) }}
  ```

# Check if entity exists
type: conditional
conditions:
  - entity: light.living_room
    state_not: unavailable
card:
  type: light
  entity: light.living_room
```

### Resource Issues

```yaml
# Check resource loading in browser console
# F12 > Network > Filter by JS

# Force reload
# Settings > Dashboards > Resources > (edit URL with ?v=1.0.1)
```

### Template Debugging

```yaml
type: markdown
content: |
  Entity state: {{ states('light.living_room') }}
  Is on: {{ is_state('light.living_room', 'on') }}
  Brightness: {{ state_attr('light.living_room', 'brightness') }}
  Type check: {{ states('light.living_room') | float(0) }}
```

### Custom Card Errors

```yaml
# Common issues:
# 1. Wrong type name
type: custom:button-card  # Correct
type: button-card         # Wrong - missing custom:

# 2. Resource not loaded
# Add in Settings > Dashboards > Resources

# 3. Version mismatch
# Update card via HACS
```

---

## Heading Card (2024.8+)

The Heading card creates section titles within your dashboard views. Available since Home Assistant 2024.8.

### Basic Heading

```yaml
type: heading
heading: Living Room
heading_style: title  # title, subtitle
icon: mdi:sofa
```

### Heading Styles

```yaml
# Large title style (default)
type: heading
heading: Climate Control
heading_style: title
icon: mdi:thermometer

# Smaller subtitle style
type: heading
heading: Temperature Sensors
heading_style: subtitle
icon: mdi:thermometer-lines
```

### Collapsible Sections

Use heading cards to create collapsible sections in sections-style views:

```yaml
# In a sections view
type: sections
sections:
  - type: grid
    cards:
      - type: heading
        heading: Lights
        icon: mdi:lightbulb-group
        tap_action:
          action: navigate
          navigation_path: /lovelace/lights
      - type: tile
        entity: light.living_room
      - type: tile
        entity: light.bedroom

  - type: grid
    cards:
      - type: heading
        heading: Climate
        icon: mdi:home-thermometer
      - type: tile
        entity: climate.living_room
```

### Heading with Action

```yaml
type: heading
heading: Security
icon: mdi:shield-home
tap_action:
  action: navigate
  navigation_path: /lovelace/security

# Or with service call
type: heading
heading: All Lights Off
icon: mdi:lightbulb-off
tap_action:
  action: call-service
  service: light.turn_off
  target:
    entity_id: all
```

### Dynamic Heading with Template

```yaml
type: heading
heading: >
  {% set count = states.light | selectattr('state', 'eq', 'on') | list | count %}
  Lights ({{ count }} on)
heading_style: title
icon: mdi:lightbulb-group
```

### Styling Heading Cards

```yaml
type: heading
heading: Important Section
icon: mdi:alert
card_mod:
  style: |
    ha-card {
      --heading-color: var(--error-color);
      --heading-icon-color: var(--error-color);
    }
```

---

## Badge Card

Badges appear at the top of views or sections, providing compact status indicators.

### Basic Badge

```yaml
# In view configuration
badges:
  - entity: person.john
  - entity: sensor.temperature
  - entity: binary_sensor.front_door
```

### Badge with Customization

```yaml
badges:
  - type: entity
    entity: sensor.temperature
    name: Temp
    icon: mdi:thermometer
    color: >
      {% set temp = states('sensor.temperature') | float(20) %}
      {% if temp < 18 %}blue{% elif temp > 26 %}red{% else %}green{% endif %}

  - type: entity
    entity: binary_sensor.motion
    name: Motion
    show_state: true
```

### Badge Types

```yaml
badges:
  # Entity badge (default)
  - type: entity
    entity: person.john
    show_name: true
    show_state: true

  # State label badge
  - entity: sensor.visitors
    name: Visitors

  # Conditional badge
  - type: conditional
    conditions:
      - entity: binary_sensor.door
        state: "on"
    badge:
      entity: binary_sensor.door
      name: Door Open!
```

### Badge in Sections View

```yaml
type: sections
sections:
  - type: grid
    title: Status
    badges:
      - entity: person.john
      - entity: sensor.temperature
      - entity: alarm_control_panel.home
    cards:
      - type: tile
        entity: light.living_room
```

### State-Based Badge Colors

```yaml
badges:
  - type: entity
    entity: alarm_control_panel.home
    color: >
      {% if is_state('alarm_control_panel.home', 'disarmed') %}
        green
      {% elif is_state('alarm_control_panel.home', 'armed_away') %}
        red
      {% else %}
        orange
      {% endif %}
```

---

## Mobile Responsiveness

### Responsive Column Count

```yaml
# Grid automatically adjusts on mobile
type: grid
columns: 4  # Desktop: 4 columns
# Mobile automatically reduces to 2

# Force specific column count
type: grid
columns: 2
square: false  # Allow non-square cards for better mobile display
```

### View-Level Responsive Settings

```yaml
views:
  - title: Home
    path: home
    type: sections
    max_columns: 4  # Maximum columns on wide screens
    # Automatically reduces on smaller screens
```

### Conditional Cards for Screen Size

```yaml
# Using browser_mod or conditional
type: conditional
conditions:
  - condition: screen
    media_query: "(min-width: 768px)"  # Requires custom card
card:
  type: picture-glance
  # Large card for desktop only
```

### Touch-Friendly Sizing

```yaml
# Minimum touch target: 48x48px
type: grid
columns: 2
square: true
cards:
  - type: button
    entity: light.living_room
    icon_height: 60px  # Larger for easy tapping

  - type: button
    entity: light.bedroom
    icon_height: 60px
```

### Mobile-Optimized Layout

```yaml
# Vertical stack better for mobile
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: tile
        entity: light.living_room
      - type: tile
        entity: light.bedroom

  - type: tile
    entity: climate.thermostat
    features:
      - type: target-temperature
```

### Swipe Navigation for Mobile

```yaml
# Swipeable cards (requires HACS swipe-card)
type: custom:swipe-card
cards:
  - type: picture-entity
    entity: camera.front
  - type: picture-entity
    entity: camera.back
  - type: picture-entity
    entity: camera.side
```

### Hiding Cards on Mobile

```yaml
# With card-mod
type: entities
card_mod:
  style: |
    @media (max-width: 600px) {
      ha-card {
        display: none;
      }
    }
```

---

## Card Features Matrix

Quick reference for which features work with which card types.

### Tile Card Features

| Feature Type | Purpose | Example |
|--------------|---------|---------|
| `light-brightness` | Brightness slider | Lights |
| `light-color-temp` | Color temperature | Lights |
| `light-color` | Color picker | RGB lights |
| `cover-open-close` | Open/Close buttons | Covers |
| `cover-position` | Position slider | Blinds |
| `cover-tilt` | Tilt control | Blinds |
| `cover-tilt-position` | Tilt slider | Blinds |
| `fan-speed` | Speed control | Fans |
| `fan-preset-modes` | Preset modes | Fans |
| `fan-direction` | Direction toggle | Ceiling fans |
| `fan-oscillate` | Oscillation toggle | Fans |
| `climate-hvac-modes` | HVAC mode buttons | Thermostats |
| `climate-preset-modes` | Preset modes | Thermostats |
| `climate-fan-modes` | Fan modes | HVAC |
| `target-temperature` | Temperature control | Thermostats |
| `humidifier-modes` | Mode selection | Humidifiers |
| `humidifier-toggle` | On/off toggle | Humidifiers |
| `lawn-mower-commands` | Mower controls | Lawn mowers |
| `lock-commands` | Lock/unlock | Locks |
| `lock-open-door` | Open door button | Smart locks |
| `vacuum-commands` | Vacuum controls | Robot vacuums |
| `water-heater-operation-modes` | Mode selection | Water heaters |
| `alarm-modes` | Arm/disarm buttons | Alarm panels |
| `select-options` | Dropdown selection | Selects |
| `numeric-input` | Number input | Numbers |
| `update-actions` | Update buttons | Update entities |

### Feature Configuration Examples

```yaml
# Light with all features
type: tile
entity: light.living_room
features:
  - type: light-brightness
  - type: light-color-temp
  - type: light-color

# Climate with custom HVAC modes
type: tile
entity: climate.thermostat
features:
  - type: climate-hvac-modes
    hvac_modes:
      - "off"
      - heat
      - cool
      - auto
  - type: target-temperature

# Cover with position control
type: tile
entity: cover.blinds
features:
  - type: cover-open-close
  - type: cover-position
  - type: cover-tilt-position

# Vacuum with specific commands
type: tile
entity: vacuum.robot
features:
  - type: vacuum-commands
    commands:
      - start_pause
      - stop
      - return_home
      - locate

# Fan with multiple features
type: tile
entity: fan.bedroom
features:
  - type: fan-speed
  - type: fan-preset-modes
  - type: fan-oscillate
```

### Card Capability Matrix

| Card Type | Toggle | More-Info | Actions | Features | Templates |
|-----------|--------|-----------|---------|----------|-----------|
| Button | ✓ | ✓ | ✓ | ✗ | ✗ |
| Entity | ✗ | ✓ | ✓ | ✗ | ✗ |
| Tile | ✓ | ✓ | ✓ | ✓ | ✗ |
| Light | ✓ | ✓ | ✗ | ✓ | ✗ |
| Thermostat | ✗ | ✓ | ✗ | ✓ | ✗ |
| Glance | ✓ | ✓ | ✓ | ✗ | ✗ |
| Entities | ✓ | ✓ | ✓ | ✗ | ✓ |
| Markdown | ✗ | ✗ | ✓ | ✗ | ✓ |
| Picture-Glance | ✓ | ✓ | ✓ | ✗ | ✗ |
| Picture-Elements | ✓ | ✓ | ✓ | ✗ | ✓ |

### When to Use Which Card

| Scenario | Recommended Card |
|----------|------------------|
| Simple toggle | Button, Tile |
| Light with controls | Light, Tile with features |
| Entity overview | Glance, Entities |
| Climate control | Thermostat, Tile with features |
| Camera feed | Picture-Entity, Picture-Glance |
| Floor plan | Picture-Elements |
| Sensor graphs | History Graph, Statistics Graph |
| Custom display | Markdown with templates |
| Room overview | Area card |
| Status chips | Mushroom chips (HACS) |

---

## Card Feature Reference

### Light Card Features

```yaml
type: light
entity: light.living_room
features:
  - type: light-brightness
  - type: light-color-temp
    # No additional config needed
```

### Climate Card Features

```yaml
type: thermostat
entity: climate.thermostat
features:
  - type: climate-hvac-modes
    hvac_modes:
      - auto
      - heat
      - cool
      - "off"
  - type: climate-preset-modes
  - type: climate-fan-modes
```

### Cover Card Features

```yaml
type: tile
entity: cover.garage
features:
  - type: cover-open-close
  - type: cover-position
  - type: cover-tilt
  - type: cover-tilt-position
```

### Fan Card Features

```yaml
type: tile
entity: fan.bedroom
features:
  - type: fan-speed
  - type: fan-preset-modes
  - type: fan-direction
  - type: fan-oscillate
```

### Vacuum Card Features

```yaml
type: tile
entity: vacuum.robot
features:
  - type: vacuum-commands
    commands:
      - start_pause
      - stop
      - return_home
```

### Lock Card Features

```yaml
type: tile
entity: lock.front_door
features:
  - type: lock-commands
  - type: lock-open-door
```

