# Home Assistant Dashboards Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Dashboard Types](#dashboard-types)
- [YAML Configuration](#yaml-configuration)
- [Views](#views)
- [Themes](#themes)
- [Resources](#resources)
- [Subviews and Navigation](#subviews-and-navigation)
- [Mobile Optimization](#mobile-optimization)
- [User-Specific Dashboards](#user-specific-dashboards)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Dashboards (formerly Lovelace) provide the user interface for Home Assistant.

### Key Terms

| Term | Description |
|------|-------------|
| **Dashboard** | A complete UI configuration |
| **View** | A tab/page within a dashboard |
| **Card** | A UI component displaying data |
| **Badge** | Small status indicator at top |
| **Resource** | External JS/CSS files |
| **Theme** | Visual styling configuration |

### Dashboard Structure

```
Dashboard
├── Views (tabs)
│   ├── Cards
│   │   ├── Entities
│   │   └── Features
│   ├── Badges
│   └── Subviews
├── Resources
└── Theme
```

### Configuration Locations

| Method | Location | Use Case |
|--------|----------|----------|
| **Storage** | `.storage/lovelace*` | UI editing, default |
| **YAML** | `ui-lovelace.yaml` | Version control |
| **Per-dashboard** | `dashboards/` folder | Multiple dashboards |

---

## Dashboard Types

### Storage Mode (Default)

```yaml
# Configured via UI
# Settings > Dashboards > Add Dashboard

# Data stored in:
# .storage/lovelace
# .storage/lovelace.dashboard_name
```

**Pros:**
- Visual editing
- No YAML knowledge needed
- Automatic backups

**Cons:**
- Harder to version control
- No include support

### YAML Mode

```yaml
# configuration.yaml
lovelace:
  mode: yaml

# Creates ui-lovelace.yaml in config directory
```

**Pros:**
- Full version control
- Include support
- Copy/paste friendly

**Cons:**
- Manual reload required
- No visual editor

### Mixed Mode

```yaml
# configuration.yaml
lovelace:
  mode: storage
  dashboards:
    yaml-dashboard:
      mode: yaml
      filename: dashboards/yaml-dashboard.yaml
      title: YAML Dashboard
      icon: mdi:file-code
      show_in_sidebar: true
```

---

## YAML Configuration

### Basic Structure

```yaml
# ui-lovelace.yaml
title: My Home
views:
  - title: Home
    path: home
    icon: mdi:home
    cards:
      - type: entities
        entities:
          - light.living_room
          - light.bedroom
```

### Complete Dashboard

```yaml
# ui-lovelace.yaml
title: My Smart Home
background: var(--background-image)

views:
  - title: Overview
    path: overview
    icon: mdi:home
    type: masonry
    badges:
      - entity: person.john
      - entity: sun.sun
    cards:
      - type: weather-forecast
        entity: weather.home
        show_forecast: true

  - title: Lights
    path: lights
    icon: mdi:lightbulb
    cards:
      - type: light
        entity: light.living_room
```

### Including Files

```yaml
# ui-lovelace.yaml
title: My Home
views:
  - !include views/home.yaml
  - !include views/lights.yaml
  - !include views/climate.yaml
  - !include views/security.yaml
```

```yaml
# views/home.yaml
title: Home
path: home
icon: mdi:home
cards:
  - !include ../cards/weather.yaml
  - !include ../cards/quick-actions.yaml
```

### Using Anchors

```yaml
# Define anchors
.light_card_defaults: &light_defaults
  type: light
  features:
    - type: light-brightness

views:
  - title: Lights
    cards:
      - <<: *light_defaults
        entity: light.living_room
      - <<: *light_defaults
        entity: light.bedroom
      - <<: *light_defaults
        entity: light.kitchen
```

### Secrets in Dashboards

```yaml
# Don't use secrets.yaml for dashboards
# Use template sensors instead for sensitive data

# Bad: Direct API key in card
type: iframe
url: !secret camera_url

# Good: Template sensor
type: picture-entity
entity: camera.front_door
```

---

## Views

### View Properties

```yaml
views:
  - title: Living Room          # Tab title
    path: living-room           # URL path (lowercase, hyphens)
    icon: mdi:sofa              # Tab icon
    type: masonry               # Layout type
    panel: false                # Full-width single card
    visible: true               # Show in navigation
    theme: dark                 # View-specific theme
    background: center / cover no-repeat url("/local/bg.jpg") fixed
    badges:                     # Top badges
      - entity: person.john
    cards:                      # Card list
      - type: entities
        entities:
          - light.living_room
```

### View Types

| Type | Description |
|------|-------------|
| `masonry` | Default, auto-arranging columns |
| `sidebar` | Fixed sidebar + main area |
| `panel` | Single card, full width |
| `sections` | Grid-based sections (2024.6+) |

```yaml
# Masonry (default)
views:
  - title: Home
    type: masonry
    cards: [...]

# Sidebar
views:
  - title: Media
    type: sidebar
    cards:
      # First card becomes sidebar
      - type: entities
        entities: [...]
      # Rest in main area
      - type: media-control
        entity: media_player.living_room

# Panel (single full-width card)
views:
  - title: Floor Plan
    type: panel
    panel: true
    cards:
      - type: picture-elements
        image: /local/floorplan.png
        elements: [...]
```

### Sections Dashboard (2024.6+)

The sections view type provides a modern, grid-based layout with automatic responsive design.

```yaml
views:
  - type: sections
    title: Home
    path: home
    sections:
      - title: Lights
        cards:
          - type: tile
            entity: light.living_room
          - type: tile
            entity: light.kitchen

      - title: Climate
        cards:
          - type: tile
            entity: climate.living_room
          - type: sensor
            entity: sensor.temperature

      - title: Security
        cards:
          - type: tile
            entity: lock.front_door
          - type: tile
            entity: alarm_control_panel.home
```

#### Section Properties

```yaml
sections:
  - title: "Section Name"
    type: grid  # Default, can be omitted
    column_span: 1  # How many columns this section spans
    cards:
      - type: tile
        entity: light.room
```

#### Sections with Badges (2024.8+)

```yaml
views:
  - type: sections
    title: Home
    badges:
      # Badges appear at top of sections view
      - entity: person.john
      - entity: sun.sun
      - entity: weather.home
        show_name: false
      - type: entity
        entity: sensor.power_consumption
        name: "Power"
        color: yellow
    sections:
      - title: Living Room
        cards:
          - type: tile
            entity: light.living_room
```

#### Badge Customization

```yaml
badges:
  # Simple entity badge
  - entity: person.john

  # Named badge
  - entity: sensor.temperature
    name: "Temp"
    show_name: true
    show_state: true

  # Colored badge
  - type: entity
    entity: binary_sensor.alarm
    color: |
      {% if is_state('binary_sensor.alarm', 'on') %}
        red
      {% else %}
        green
      {% endif %}

  # Badge with tap action
  - entity: lock.front_door
    tap_action:
      action: toggle
```

#### Full-Width Sections

```yaml
views:
  - type: sections
    title: Dashboard
    max_columns: 4  # Default is 4
    sections:
      # Standard section (1 column)
      - title: Lights
        cards:
          - type: tile
            entity: light.living_room

      # Wide section (spans 2 columns)
      - title: Camera Feed
        column_span: 2
        cards:
          - type: picture-entity
            entity: camera.front_door

      # Full-width section (spans all columns)
      - title: Energy Overview
        column_span: 4
        cards:
          - type: energy-distribution
```

#### Sections Without Titles

```yaml
sections:
  # Section with title
  - title: Climate
    cards:
      - type: tile
        entity: climate.living_room

  # Section without title (seamless)
  - cards:
      - type: tile
        entity: light.hallway
      - type: tile
        entity: light.kitchen
```

#### Mobile Responsiveness in Sections

Sections automatically adapt to screen size:
- Desktop (4 columns): Full layout
- Tablet (2-3 columns): Sections stack
- Mobile (1 column): Single column, scrollable

```yaml
views:
  - type: sections
    title: Home
    max_columns: 4
    sections:
      # These sections will reflow on smaller screens
      - title: Room 1
        cards: [...]
      - title: Room 2
        cards: [...]
      - title: Room 3
        cards: [...]
      - title: Room 4
        cards: [...]
```

---

## Modern Card Types (2024+)

### Tile Card

The tile card is the modern replacement for button and entity cards.

```yaml
# Basic tile
- type: tile
  entity: light.living_room

# With features
- type: tile
  entity: light.living_room
  features:
    - type: light-brightness
    - type: light-color-temp

# Custom appearance
- type: tile
  entity: cover.garage
  name: "Garage Door"
  icon: mdi:garage
  color: primary
  tap_action:
    action: toggle
  hold_action:
    action: more-info
```

#### Tile Features

| Feature | Entity Types | Description |
|---------|--------------|-------------|
| `light-brightness` | light | Brightness slider |
| `light-color-temp` | light | Color temperature |
| `cover-open-close` | cover | Open/close buttons |
| `cover-position` | cover | Position slider |
| `fan-speed` | fan | Speed control |
| `climate-hvac-modes` | climate | Mode selector |
| `climate-preset-modes` | climate | Preset selector |
| `alarm-modes` | alarm_control_panel | Arm/disarm |
| `vacuum-commands` | vacuum | Start/pause/return |
| `lawn-mower-commands` | lawn_mower | Commands |

```yaml
# Climate tile with features
- type: tile
  entity: climate.living_room
  features:
    - type: climate-hvac-modes
      hvac_modes:
        - heat
        - cool
        - auto
        - "off"
    - type: target-temperature
```

### Grid Card

Modern replacement for horizontal-stack and vertical-stack with responsive design.

```yaml
# Basic grid
- type: grid
  columns: 3
  square: false
  cards:
    - type: tile
      entity: light.living_room
    - type: tile
      entity: light.kitchen
    - type: tile
      entity: light.bedroom

# Responsive grid
- type: grid
  columns: 4  # Desktop
  cards:
    - type: button
      entity: script.leave_home
    - type: button
      entity: script.arrive_home
    - type: button
      entity: scene.movie_mode
    - type: button
      entity: script.goodnight
```

#### Grid vs Stack Cards

| Card | Use Case |
|------|----------|
| `grid` | Responsive, wraps on smaller screens |
| `horizontal-stack` | Fixed horizontal, no wrapping |
| `vertical-stack` | Fixed vertical stacking |

### Heading Card (2024.8+)

Creates visual section headers within views. Use this to organize cards into logical groups.

```yaml
# Basic heading
- type: heading
  heading: Living Room
  heading_style: title  # title, subtitle
  icon: mdi:sofa

# With badges showing status
- type: heading
  heading: Climate
  badges:
    - entity: sensor.temperature
    - entity: sensor.humidity

# Heading with tap action (navigate to subview)
- type: heading
  heading: Security
  icon: mdi:shield-home
  tap_action:
    action: navigate
    navigation_path: /lovelace/security

# Heading with multiple badges
- type: heading
  heading: Energy
  icon: mdi:lightning-bolt
  badges:
    - type: entity
      entity: sensor.power_consumption
      name: "Now"
    - type: entity
      entity: sensor.daily_energy
      name: "Today"
```

#### Heading Styles

| Style | Appearance |
|-------|------------|
| `title` | Large, prominent heading |
| `subtitle` | Smaller, secondary heading |

```yaml
# Primary section
- type: heading
  heading: Living Room
  heading_style: title
  icon: mdi:sofa

# Sub-sections
- type: heading
  heading: Lights
  heading_style: subtitle
  icon: mdi:lightbulb

- type: tile
  entity: light.living_room_main

- type: heading
  heading: Climate
  heading_style: subtitle
  icon: mdi:thermometer

- type: tile
  entity: climate.living_room
```

#### Collapsible Heading Pattern

While heading cards don't natively collapse, you can simulate this with conditional cards:

```yaml
# Toggle for collapsing
- type: entities
  entities:
    - entity: input_boolean.show_advanced
      name: "Show Advanced"

# Conditional content
- type: conditional
  conditions:
    - entity: input_boolean.show_advanced
      state: "on"
  card:
    type: vertical-stack
    cards:
      - type: heading
        heading: Advanced Settings
        heading_style: subtitle
      - type: entities
        entities:
          - input_number.threshold
          - input_boolean.debug_mode
```

### Statistics Card (Enhanced)

```yaml
- type: statistic
  entity: sensor.daily_energy
  stat_type: sum  # sum, mean, min, max, change
  period:
    calendar:
      period: month

# Multiple statistics
- type: statistics-graph
  entities:
    - entity: sensor.energy
      name: Energy
  stat_types:
    - sum
    - mean
  period:
    calendar:
      period: week
  days_to_show: 30
```

### Area Card (2024.4+)

Display and control all entities in an area.

```yaml
- type: area
  area: living_room
  navigation_path: /lovelace/living-room
  show_camera: true
```

### Todo List Card

```yaml
- type: todo-list
  entity: todo.shopping_list
  title: Shopping List
```

### Calendar Card (Enhanced)

```yaml
- type: calendar
  entities:
    - calendar.personal
    - calendar.work
  initial_view: dayGridMonth  # dayGridMonth, dayGridWeek, dayGridDay, listWeek
```

### Picture Elements (Enhanced)

```yaml
- type: picture-elements
  image: /local/floorplan.svg
  elements:
    # State badge
    - type: state-badge
      entity: binary_sensor.motion
      style:
        top: 10%
        left: 20%

    # State icon
    - type: state-icon
      entity: light.living_room
      tap_action:
        action: toggle
      style:
        top: 50%
        left: 50%

    # State label
    - type: state-label
      entity: sensor.temperature
      style:
        top: 80%
        left: 30%
        color: white

    # Conditional element (2024+)
    - type: conditional
      conditions:
        - entity: binary_sensor.motion
          state: "on"
      elements:
        - type: icon
          icon: mdi:motion-sensor
          style:
            top: 10%
            left: 10%
```

---

## Responsive Dashboard Design

### Mobile-First Approach

```yaml
views:
  - type: sections
    title: Home
    sections:
      # Essential controls first
      - title: Quick Actions
        cards:
          - type: grid
            columns: 2
            square: true
            cards:
              - type: tile
                entity: script.leaving
                icon_height: 60px
              - type: tile
                entity: script.arriving
                icon_height: 60px

      # Status second
      - title: Status
        cards:
          - type: tile
            entity: alarm_control_panel.home
```

### Conditional Cards

```yaml
# Show different cards based on screen size using card-mod
- type: conditional
  conditions:
    - condition: user
      users:
        - admin_user_id
  card:
    type: entities
    title: Admin Only
    entities:
      - script.restart_ha
```

### Dashboard Per Device

```yaml
# configuration.yaml
lovelace:
  mode: storage
  dashboards:
    mobile-dashboard:
      mode: yaml
      filename: dashboards/mobile.yaml
      title: Mobile
      icon: mdi:cellphone
      show_in_sidebar: true

    tablet-dashboard:
      mode: yaml
      filename: dashboards/tablet.yaml
      title: Tablet
      icon: mdi:tablet
      show_in_sidebar: true
```

### Conditional Visibility

```yaml
views:
  - title: Admin
    path: admin
    visible:
      - user: admin_user_id
    cards: [...]

  - title: Guest View
    visible:
      - user: guest_user_id
    cards: [...]
```

### View Badges

```yaml
views:
  - title: Home
    badges:
      # Simple entity
      - entity: person.john

      # With name override
      - entity: sun.sun
        name: Sun

      # Template badge
      - type: entity
        entity: sensor.power_consumption
        name: "Power"
```

---

## Themes

### Theme Configuration

```yaml
# configuration.yaml
frontend:
  themes: !include_dir_merge_named themes/
```

### Theme Structure

```yaml
# themes/dark_theme.yaml
dark_theme:
  # Primary colors
  primary-color: "#1976d2"
  accent-color: "#ff9800"

  # Background
  primary-background-color: "#121212"
  secondary-background-color: "#1e1e1e"

  # Text
  primary-text-color: "#ffffff"
  secondary-text-color: "#b0b0b0"

  # Cards
  card-background-color: "#1e1e1e"
  ha-card-border-radius: "8px"
  ha-card-box-shadow: "0 2px 4px rgba(0,0,0,0.3)"

  # Header
  app-header-background-color: "#1e1e1e"
  app-header-text-color: "#ffffff"

  # Sidebar
  sidebar-background-color: "#1e1e1e"
  sidebar-text-color: "#ffffff"
  sidebar-selected-background-color: "#333333"
```

### Common Theme Variables

| Variable | Description |
|----------|-------------|
| `primary-color` | Main accent color |
| `accent-color` | Secondary accent |
| `primary-background-color` | Main background |
| `card-background-color` | Card background |
| `primary-text-color` | Main text color |
| `ha-card-border-radius` | Card corner radius |
| `ha-card-box-shadow` | Card shadow |

### Setting Themes

```yaml
# Per-user default
automation:
  - alias: "Set Theme on Login"
    trigger:
      - platform: event
        event_type: user_logged_in
    action:
      - service: frontend.set_theme
        data:
          name: dark_theme

# Service call
service: frontend.set_theme
data:
  name: dark_theme
  mode: dark  # light or dark
```

### Per-View Themes

```yaml
views:
  - title: Dark Room
    theme: dark_theme
    cards: [...]

  - title: Light Room
    theme: light_theme
    cards: [...]
```

### Card-Level Styling

```yaml
# Using card-mod (HACS)
type: entities
card_mod:
  style: |
    ha-card {
      background-color: rgba(0, 0, 0, 0.8);
      border-radius: 16px;
    }
entities:
  - light.living_room
```

---

## Resources

### Adding Resources

```yaml
# configuration.yaml (YAML mode)
lovelace:
  mode: yaml
  resources:
    - url: /local/custom-card.js
      type: module
    - url: /hacsfiles/card-name/card-name.js
      type: module
    - url: /local/styles.css
      type: css
```

### Resource Types

| Type | Use Case |
|------|----------|
| `module` | ES6 JavaScript modules |
| `js` | Legacy JavaScript |
| `css` | Stylesheets |

### HACS Resources

```yaml
# HACS manages resources automatically
# Located in: /hacsfiles/integration-name/

resources:
  - url: /hacsfiles/button-card/button-card.js
    type: module
  - url: /hacsfiles/mini-graph-card/mini-graph-card-bundle.js
    type: module
```

### Local Resources

```yaml
# Place files in config/www/
# Access via /local/

resources:
  - url: /local/my-custom-card.js?v=1.0.0
    type: module
```

### Version Cache Busting

```yaml
# Add version parameter to force refresh
resources:
  - url: /local/custom-card.js?v=1.2.3
    type: module
```

---

## Subviews and Navigation

### Subviews

```yaml
views:
  - title: Home
    path: home
    cards:
      - type: custom:button-card
        entity: light.living_room
        tap_action:
          action: navigate
          navigation_path: /lovelace/living-room

  - title: Living Room
    path: living-room
    subview: true  # Back button instead of tabs
    cards:
      - type: entities
        entities:
          - light.living_room
          - light.lamp
```

### Navigation Actions

```yaml
# In any card with tap_action
tap_action:
  action: navigate
  navigation_path: /lovelace/lights

# External URL
tap_action:
  action: url
  url_path: https://example.com

# Different dashboard
tap_action:
  action: navigate
  navigation_path: /yaml-dashboard/overview
```

### Conditional Navigation

```yaml
type: custom:button-card
entity: light.living_room
tap_action:
  action: |
    [[[
      if (entity.state === 'on') {
        return { action: 'toggle' };
      } else {
        return { action: 'navigate', navigation_path: '/lovelace/lights' };
      }
    ]]]
```

### Deep Linking

```yaml
# Link directly to specific views
# Format: /dashboard-name/view-path

# Default dashboard
/lovelace/home
/lovelace/lights

# Named dashboard
/yaml-dashboard/overview
/mobile-dashboard/home
```

---

## Mobile Optimization

### Responsive Layout

```yaml
views:
  - title: Home
    type: masonry
    cards:
      # Full width on mobile
      - type: weather-forecast
        entity: weather.home

      # Stack cards for mobile
      - type: horizontal-stack
        cards:
          - type: button
            entity: light.living_room
          - type: button
            entity: light.bedroom
```

### Mobile-Specific Dashboard

```yaml
# configuration.yaml
lovelace:
  mode: storage
  dashboards:
    mobile:
      mode: yaml
      filename: dashboards/mobile.yaml
      title: Mobile
      icon: mdi:cellphone
      show_in_sidebar: true
```

```yaml
# dashboards/mobile.yaml
title: Mobile
views:
  - title: Quick
    icon: mdi:lightning-bolt
    cards:
      # Large touch targets
      - type: grid
        columns: 2
        square: true
        cards:
          - type: button
            entity: light.living_room
            icon_height: 60px
          - type: button
            entity: lock.front_door
            icon_height: 60px
          - type: button
            entity: cover.garage
            icon_height: 60px
          - type: button
            entity: script.goodnight
            icon_height: 60px
```

### Hiding Elements on Mobile

```yaml
# Using card-mod
type: entities
card_mod:
  style: |
    @media (max-width: 600px) {
      ha-card {
        /* Hide on mobile */
        display: none;
      }
    }
entities:
  - light.living_room
```

### Touch-Friendly Cards

```yaml
# Use buttons instead of entities for touch
type: grid
columns: 2
cards:
  - type: button
    entity: light.living_room
    tap_action:
      action: toggle
    hold_action:
      action: more-info

  - type: button
    entity: cover.garage
    tap_action:
      action: toggle
    hold_action:
      action: more-info
```

### Mobile Companion App Integration

```yaml
views:
  - title: Home
    cards:
      # Sensor card showing phone battery
      - type: entities
        entities:
          - sensor.phone_battery_level
          - sensor.phone_battery_state
          - binary_sensor.phone_charging

      # Location card
      - type: map
        entities:
          - device_tracker.phone
        hours_to_show: 24
```

---

## User-Specific Dashboards

### Per-User Dashboard

```yaml
# configuration.yaml
lovelace:
  dashboards:
    admin-dashboard:
      mode: yaml
      filename: dashboards/admin.yaml
      title: Admin
      show_in_sidebar: true
      require_admin: true

    family-dashboard:
      mode: yaml
      filename: dashboards/family.yaml
      title: Family
      show_in_sidebar: true
```

### User-Based View Visibility

```yaml
views:
  - title: Settings
    path: settings
    visible:
      - user: abc123-user-id  # Get from Developer Tools
    cards:
      - type: entities
        title: Admin Functions
        entities:
          - script.restart_ha
          - script.backup
```

### Default Dashboard per User

```yaml
# Set via user profile or automation
automation:
  - alias: "Set Dashboard for Guest"
    trigger:
      - platform: event
        event_type: user_logged_in
        event_data:
          user_id: guest_user_id
    action:
      - service: frontend.set_theme
        data:
          name: guest_theme
```

---

## Common Patterns

### Dashboard Organization

```yaml
# Recommended view structure
views:
  # 1. Overview - Quick glance
  - title: Home
    path: home
    icon: mdi:home

  # 2. Room-based views
  - title: Living Room
    path: living-room
    icon: mdi:sofa

  - title: Bedroom
    path: bedroom
    icon: mdi:bed

  # 3. Function-based views
  - title: Climate
    path: climate
    icon: mdi:thermostat

  - title: Security
    path: security
    icon: mdi:shield

  # 4. Admin/settings
  - title: System
    path: system
    icon: mdi:cog
    visible:
      - user: admin_id
```

### Quick Actions Card

```yaml
type: grid
title: Quick Actions
columns: 4
square: true
cards:
  - type: button
    entity: script.leave_home
    name: Leaving
    icon: mdi:door-open

  - type: button
    entity: script.arrive_home
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
```

### Status Overview

```yaml
type: glance
title: Status
columns: 5
entities:
  - entity: person.john
    name: John
  - entity: alarm_control_panel.home
    name: Alarm
  - entity: lock.front_door
    name: Front Door
  - entity: cover.garage
    name: Garage
  - entity: binary_sensor.anyone_home
    name: Presence
```

### Room Summary Card

```yaml
type: custom:mushroom-template-card
primary: Living Room
secondary: >
  {{ states('sensor.living_room_temperature') }}°C •
  {{ states('sensor.living_room_humidity') }}%
icon: mdi:sofa
tap_action:
  action: navigate
  navigation_path: /lovelace/living-room
icon_color: >
  {% if is_state('light.living_room', 'on') %}
    amber
  {% else %}
    grey
  {% endif %}
```

### Energy Dashboard

```yaml
type: energy-distribution
link_dashboard: true

# Alternative with gauges
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.power_consumption
    name: Current Power
    min: 0
    max: 5000
    severity:
      green: 0
      yellow: 2000
      red: 4000

  - type: statistics-graph
    entities:
      - sensor.daily_energy
    days_to_show: 7
    stat_types:
      - sum
```

---

## Best Practices

### Performance

| Practice | Implementation |
|----------|----------------|
| Limit cards per view | 20-30 cards max |
| Use masonry layout | Auto-optimizes columns |
| Lazy load images | Use native camera cards |
| Minimize custom cards | Each adds JS load |

```yaml
# Optimize with sections
views:
  - title: Home
    type: sections
    sections:
      - title: Lights
        cards: [...]
      - title: Climate
        cards: [...]
```

### Organization

```yaml
# File structure for YAML mode
config/
├── ui-lovelace.yaml
├── dashboards/
│   ├── mobile.yaml
│   └── tablet.yaml
├── views/
│   ├── home.yaml
│   ├── lights.yaml
│   └── climate.yaml
├── cards/
│   ├── weather.yaml
│   └── quick-actions.yaml
└── themes/
    ├── light.yaml
    └── dark.yaml
```

### Naming Conventions

```yaml
# Views: lowercase with hyphens
views:
  - path: living-room    # Good
  - path: Living Room    # Bad - spaces and caps
  - path: livingRoom     # Bad - camelCase

# Consistent titles
views:
  - title: Living Room   # Room name
  - title: Climate       # Function
  - title: System        # Admin
```

### Maintainability

```yaml
# Use includes for reusability
cards:
  # Reusable card template
  - !include
    file: cards/room-card.yaml
    vars:
      room: living_room
      name: Living Room
```

```yaml
# cards/room-card.yaml
type: vertical-stack
title: ${name}
cards:
  - type: entities
    entities:
      - light.${room}
      - sensor.${room}_temperature
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Cards not loading | Resource error | Check browser console |
| YAML not updating | Cache | Clear browser cache |
| Theme not applying | Missing reload | Reload themes service |
| View not visible | Visibility setting | Check user permissions |

### Debug Mode

```yaml
# Developer Tools > Services
service: lovelace.reload_resources

# Check for YAML errors
service: homeassistant.check_config
```

### Browser Console

```javascript
// Check for custom card errors
// F12 > Console

// Common errors:
// - "Custom element doesn't exist" - resource not loaded
// - "Invalid config" - YAML syntax error
// - "Entity not found" - wrong entity_id
```

### YAML Validation

```yaml
# Common YAML mistakes

# Wrong: Missing quotes for special characters
title: Lights & More  # & is special
# Correct:
title: "Lights & More"

# Wrong: Wrong indentation
cards:
- type: entities  # Should be indented
# Correct:
cards:
  - type: entities

# Wrong: Tabs instead of spaces
views:
	- title: Home  # Tab character
# Correct:
views:
  - title: Home  # 2 spaces
```

### Card Not Rendering

```yaml
# 1. Check resource loaded
# Settings > Dashboards > Resources

# 2. Verify card type exists
type: custom:button-card  # Must match installed card

# 3. Check entity exists
entity: light.living_room  # Developer Tools > States

# 4. Validate card config
type: entities
entities:
  - light.living_room  # Not just "living_room"
```

### Theme Issues

```yaml
# Reload themes
service: frontend.reload_themes

# Check theme file syntax
# themes/my_theme.yaml
my_theme:  # Theme name (no indent)
  primary-color: "#1976d2"  # Variables indented

# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
```

### Performance Issues

```yaml
# Identify slow cards
# Browser DevTools > Performance > Record

# Reduce complexity
# - Fewer entities per card
# - Less frequent updates
# - Simpler templates

# Optimize history graphs
type: history-graph
entities:
  - sensor.temperature
hours_to_show: 12  # Reduce from 24
refresh_interval: 60  # Less frequent updates
```

---

## Dashboard Checklist

```markdown
## Dashboard Setup Checklist

### Initial Setup
- [ ] Decide: Storage vs YAML mode
- [ ] Create dashboard structure
- [ ] Set up themes
- [ ] Configure resources

### Views
- [ ] Home/Overview view
- [ ] Room-based views
- [ ] Function-based views (climate, security)
- [ ] Admin view (if needed)

### Mobile
- [ ] Test on mobile devices
- [ ] Create mobile-optimized dashboard
- [ ] Configure touch-friendly cards

### Maintenance
- [ ] Back up configuration
- [ ] Document custom cards used
- [ ] Test after HA updates
```

