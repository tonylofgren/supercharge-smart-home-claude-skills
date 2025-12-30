# Home Assistant Scenes Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Scene Structure](#scene-structure)
- [Entity States in Scenes](#entity-states-in-scenes)
- [Creating Scenes](#creating-scenes)
- [Scene Snapshots](#scene-snapshots)
- [Scene Transitions](#scene-transitions)
- [Dynamic Scenes](#dynamic-scenes)
- [Scene Activation](#scene-activation)
- [Scene vs Script](#scene-vs-script)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Scenes capture the desired state of multiple entities and apply them all at once. They're ideal for setting up moods, presets, or restoring previous states.

### Key Terms

| Term | Description |
|------|-------------|
| **Scene** | Predefined state for multiple entities |
| **Snapshot** | Capture current entity states as scene |
| **Transition** | Time to gradually apply scene |
| **Activate** | Apply scene states to entities |

### When to Use Scenes

| Use Case | Scene | Script |
|----------|-------|--------|
| Set fixed light/climate states | Yes | Optional |
| Complex logic or conditions | No | Yes |
| Time delays between actions | No | Yes |
| Reusable state presets | Yes | No |
| Save/restore current state | Yes | Possible |

---

## Scene Structure

### Basic Scene (YAML)

```yaml
scene:
  - name: Movie Mode
    entities:
      light.living_room:
        state: "on"
        brightness: 50
      light.kitchen:
        state: "off"
      media_player.tv:
        state: "on"
```

### Scene with ID

```yaml
scene:
  - id: movie_mode
    name: Movie Mode
    icon: mdi:movie
    entities:
      light.living_room:
        state: "on"
        brightness: 50
```

### Complete Scene Example

```yaml
scene:
  - id: evening_relaxation
    name: Evening Relaxation
    icon: mdi:sofa
    entities:
      # Lights
      light.living_room:
        state: "on"
        brightness: 128
        color_temp: 400
        transition: 2
      light.kitchen:
        state: "off"
      light.hallway:
        state: "on"
        brightness: 50

      # Climate
      climate.living_room:
        state: heat
        temperature: 21

      # Media
      media_player.tv:
        state: "on"
        source: "Netflix"

      # Covers
      cover.living_room_blinds:
        state: closed
```

### Scene Options

| Option | Required | Description |
|--------|----------|-------------|
| `id` | No | Unique identifier |
| `name` | Yes | Display name |
| `icon` | No | MDI icon |
| `entities` | Yes | Entity states dictionary |

---

## Entity States in Scenes

### Light States

```yaml
entities:
  # Basic on/off
  light.lamp:
    state: "on"

  light.hallway:
    state: "off"

  # With brightness (0-255)
  light.living_room:
    state: "on"
    brightness: 200

  # With brightness percentage (converted)
  light.bedroom:
    state: "on"
    brightness: 128  # ~50%

  # Color temperature (mireds)
  light.kitchen:
    state: "on"
    brightness: 255
    color_temp: 350

  # RGB color
  light.accent:
    state: "on"
    brightness: 255
    rgb_color: [255, 100, 50]

  # HS color
  light.led_strip:
    state: "on"
    hs_color: [30, 100]

  # With transition
  light.dining:
    state: "on"
    brightness: 200
    transition: 5
```

### Switch States

```yaml
entities:
  switch.coffee_maker:
    state: "on"

  switch.fan:
    state: "off"
```

### Climate States

```yaml
entities:
  climate.thermostat:
    state: heat
    temperature: 22

  climate.bedroom:
    state: "off"

  climate.living_room:
    hvac_mode: cool
    temperature: 24
    fan_mode: auto
```

### Cover States

```yaml
entities:
  cover.blinds:
    state: open

  cover.garage:
    state: closed

  # Partial position
  cover.living_room:
    state: open
    position: 50

  # With tilt
  cover.bedroom:
    state: open
    position: 75
    tilt_position: 45
```

### Media Player States

```yaml
entities:
  media_player.tv:
    state: "on"
    source: "HDMI 1"

  media_player.speaker:
    state: playing
    volume_level: 0.5

  media_player.soundbar:
    state: "off"
```

### Fan States

```yaml
entities:
  fan.ceiling:
    state: "on"
    percentage: 50

  fan.bedroom:
    state: "on"
    preset_mode: sleep
```

### Input Helpers

```yaml
entities:
  input_boolean.guest_mode:
    state: "on"

  input_number.brightness:
    state: 80

  input_select.mode:
    state: "Away"
```

---

## Creating Scenes

### Via YAML

```yaml
# scenes.yaml or configuration.yaml
scene:
  - id: morning
    name: Morning
    entities:
      light.bedroom:
        state: "on"
        brightness: 255
      cover.bedroom:
        state: open

  - id: night
    name: Night
    entities:
      light.bedroom:
        state: "off"
      cover.bedroom:
        state: closed
```

### Via UI

1. Go to Settings > Automations & Scenes > Scenes
2. Click "+ Create Scene"
3. Name the scene
4. Add entities and set their states
5. Click Save

### From Automation

```yaml
# Create scene dynamically
action:
  - service: scene.create
    data:
      scene_id: snapshot_before_party
      snapshot_entities:
        - light.living_room
        - light.kitchen
        - media_player.tv
```

---

## Scene Snapshots

Snapshots capture the current state of entities to restore later.

### Create Snapshot

```yaml
action:
  - service: scene.create
    data:
      scene_id: before_guest_mode
      snapshot_entities:
        - light.living_room
        - light.kitchen
        - light.bedroom
        - climate.thermostat
```

### Restore Snapshot

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.before_guest_mode
```

### Snapshot Pattern

```yaml
automation:
  - id: guest_mode_on
    alias: Guest Mode On
    trigger:
      - platform: state
        entity_id: input_boolean.guest_mode
        to: "on"
    action:
      # Save current state
      - service: scene.create
        data:
          scene_id: before_guest
          snapshot_entities:
            - light.living_room
            - light.guest_room
      # Apply guest settings
      - service: scene.turn_on
        target:
          entity_id: scene.guest_mode_preset

  - id: guest_mode_off
    alias: Guest Mode Off
    trigger:
      - platform: state
        entity_id: input_boolean.guest_mode
        to: "off"
    action:
      # Restore previous state
      - service: scene.turn_on
        target:
          entity_id: scene.before_guest
```

### Snapshot Selected Entities

```yaml
# Snapshot all lights in an area
action:
  - service: scene.create
    data:
      scene_id: living_room_snapshot
      snapshot_entities: >
        {{ states.light
           | selectattr('entity_id', 'search', 'living')
           | map(attribute='entity_id')
           | list }}
```

---

## Scene Transitions

### In Scene Definition

```yaml
scene:
  - id: romantic_dinner
    name: Romantic Dinner
    entities:
      light.dining:
        state: "on"
        brightness: 100
        transition: 10  # 10 second fade
      light.candles:
        state: "on"
        brightness: 50
        transition: 10
```

### When Activating

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.evening
    data:
      transition: 5  # Override scene transitions
```

### Progressive Transition

```yaml
# Gradually change across multiple scenes
action:
  - service: scene.turn_on
    target:
      entity_id: scene.sunset_1
    data:
      transition: 300  # 5 minutes
  - delay: "00:05:00"
  - service: scene.turn_on
    target:
      entity_id: scene.sunset_2
    data:
      transition: 300
```

---

## Dynamic Scenes

### Template-Based Scene Data

```yaml
# Use templates to determine scene content
action:
  - service: scene.apply
    data:
      entities:
        light.living_room:
          state: "on"
          brightness: >
            {% if now().hour < 7 or now().hour > 22 %}
              50
            {% else %}
              255
            {% endif %}
```

### Conditional Scene Selection

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: >
        {% if is_state('sun.sun', 'below_horizon') %}
          scene.evening
        {% else %}
          scene.day
        {% endif %}
```

### Scene from Input Select

```yaml
input_select:
  lighting_scene:
    options:
      - Bright
      - Relaxed
      - Movie
      - Off

automation:
  - id: apply_scene_from_select
    trigger:
      - platform: state
        entity_id: input_select.lighting_scene
    action:
      - service: scene.turn_on
        target:
          entity_id: "scene.{{ states('input_select.lighting_scene') | lower }}"
```

---

## Scene Activation

### Basic Activation

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.movie_mode
```

### With Transition Override

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.evening
    data:
      transition: 10
```

### Apply Scene Data Directly

```yaml
# Apply scene data without creating scene entity
action:
  - service: scene.apply
    data:
      entities:
        light.living_room:
          state: "on"
          brightness: 200
        light.kitchen:
          state: "off"
```

### Apply with Transition

```yaml
action:
  - service: scene.apply
    data:
      transition: 5
      entities:
        light.living_room:
          state: "on"
          brightness: 100
```

### Multiple Scenes in Sequence

```yaml
action:
  - service: scene.turn_on
    target:
      entity_id: scene.wake_up_1
  - delay: "00:10:00"
  - service: scene.turn_on
    target:
      entity_id: scene.wake_up_2
  - delay: "00:10:00"
  - service: scene.turn_on
    target:
      entity_id: scene.wake_up_3
```

---

## Scene vs Script

### When to Use Scene

```yaml
# Fixed state preset - use scene
scene:
  - id: morning
    name: Morning
    entities:
      light.bedroom:
        state: "on"
        brightness: 255
```

### When to Use Script

```yaml
# Logic, delays, conditions - use script
script:
  morning_routine:
    sequence:
      - service: cover.open_cover
        target:
          entity_id: cover.bedroom
      - delay: "00:00:05"
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 50
      - delay: "00:05:00"
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 100
```

### Combine Scene and Script

```yaml
scene:
  - id: movie_lighting
    name: Movie Lighting
    entities:
      light.living_room:
        state: "on"
        brightness: 30

script:
  movie_mode:
    sequence:
      - service: scene.turn_on
        target:
          entity_id: scene.movie_lighting
        data:
          transition: 3
      - service: media_player.turn_on
        target:
          entity_id: media_player.tv
      - service: cover.close_cover
        target:
          entity_id: cover.living_room
```

---

## Common Patterns

### Time-of-Day Scenes

```yaml
scene:
  - id: morning
    name: Morning
    entities:
      light.living_room:
        state: "on"
        brightness: 255
        color_temp: 250  # Cool white

  - id: evening
    name: Evening
    entities:
      light.living_room:
        state: "on"
        brightness: 180
        color_temp: 400  # Warm white

  - id: night
    name: Night
    entities:
      light.living_room:
        state: "on"
        brightness: 50
        color_temp: 500  # Very warm

automation:
  - id: auto_scene_time
    trigger:
      - platform: time
        at: "07:00:00"
        id: morning
      - platform: time
        at: "18:00:00"
        id: evening
      - platform: time
        at: "22:00:00"
        id: night
    action:
      - service: scene.turn_on
        target:
          entity_id: "scene.{{ trigger.id }}"
        data:
          transition: 60
```

### Room Scenes

```yaml
# Define multiple scenes per room
scene:
  - id: living_room_bright
    name: Living Room - Bright
    entities:
      light.living_room_ceiling:
        state: "on"
        brightness: 255
      light.living_room_lamp:
        state: "on"
        brightness: 255

  - id: living_room_movie
    name: Living Room - Movie
    entities:
      light.living_room_ceiling:
        state: "off"
      light.living_room_lamp:
        state: "on"
        brightness: 50

  - id: living_room_off
    name: Living Room - Off
    entities:
      light.living_room_ceiling:
        state: "off"
      light.living_room_lamp:
        state: "off"
```

### Save/Restore Pattern

```yaml
script:
  temporary_alert:
    sequence:
      # Save current state
      - service: scene.create
        data:
          scene_id: before_alert
          snapshot_entities:
            - light.all
      # Flash lights
      - repeat:
          count: 3
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.all
              data:
                color_name: red
                brightness: 255
            - delay: "00:00:01"
            - service: light.turn_off
              target:
                entity_id: light.all
            - delay: "00:00:01"
      # Restore previous state
      - service: scene.turn_on
        target:
          entity_id: scene.before_alert
```

### Activity-Based Scenes

```yaml
scene:
  - id: work_from_home
    name: Work From Home
    entities:
      light.office:
        state: "on"
        brightness: 255
        color_temp: 250
      climate.office:
        temperature: 22
      input_boolean.do_not_disturb:
        state: "on"

  - id: exercise
    name: Exercise
    entities:
      light.gym:
        state: "on"
        brightness: 255
      media_player.gym_speaker:
        state: "on"
        volume_level: 0.7
      climate.gym:
        temperature: 18
```

---

## Best Practices

### Naming Conventions

```yaml
# Use descriptive, consistent names
scene:
  - id: living_room_movie
    name: Living Room - Movie     # Good: Area - Activity

  - id: lr_mv
    name: LR MV                   # Avoid: Unclear abbreviations
```

### Organize by Area

```yaml
# Group scenes by room/area
scene:
  # Living Room
  - id: living_room_bright
  - id: living_room_dim
  - id: living_room_movie
  - id: living_room_off

  # Bedroom
  - id: bedroom_morning
  - id: bedroom_night
  - id: bedroom_sleep
```

### Use Reasonable Transitions

```yaml
entities:
  light.living_room:
    state: "on"
    brightness: 200
    transition: 2    # 2 seconds is usually comfortable

  # Avoid very long transitions in scenes
  # Use automation delays for gradual changes
```

### Include All Relevant Entities

```yaml
# Include everything affected
scene:
  - id: movie_mode
    name: Movie Mode
    entities:
      # Lights
      light.living_room:
        state: "on"
        brightness: 30
      light.kitchen:
        state: "off"

      # Covers
      cover.living_room:
        state: closed

      # TV - important to include!
      media_player.tv:
        state: "on"

      # Even "off" states
      light.hallway:
        state: "off"
```

### Document Complex Scenes

```yaml
# Add comments for clarity
scene:
  # Movie Mode: Optimized for watching movies
  # - Dim ambient lighting
  # - Close blinds
  # - TV on HDMI 1
  - id: movie_mode
    name: Movie Mode
    entities:
      # ...
```

---

## Troubleshooting

### Scene Not Applying

| Problem | Cause | Solution |
|---------|-------|----------|
| Entity unchanged | Entity unavailable | Check entity exists |
| Wrong state | State format wrong | Use correct format ("on" not on) |
| No transition | Entity doesn't support | Remove transition for that entity |
| Partial application | Some entities failed | Check logs for errors |

### Debug Scene Application

```yaml
# Check what's in a scene
{{ state_attr('scene.movie_mode', 'entity_id') }}

# Log scene activation
automation:
  - trigger:
      - platform: event
        event_type: call_service
        event_data:
          domain: scene
          service: turn_on
    action:
      - service: system_log.write
        data:
          message: "Scene activated: {{ trigger.event.data }}"
          level: info
```

### Common Mistakes

```yaml
# Wrong: Invalid state value
entities:
  light.lamp:
    state: true     # Should be "on"

# Correct
entities:
  light.lamp:
    state: "on"

# Wrong: Brightness as percentage
entities:
  light.lamp:
    brightness: 50%   # Should be 0-255

# Correct
entities:
  light.lamp:
    brightness: 128   # ~50%

# Wrong: Missing entity domain
entities:
  living_room:        # Should be light.living_room
    state: "on"

# Correct
entities:
  light.living_room:
    state: "on"
```

### Snapshot Issues

```yaml
# Snapshot entity doesn't exist yet
# Create it first with any entities
action:
  - service: scene.create
    data:
      scene_id: temp_snapshot
      snapshot_entities:
        - light.test  # Must exist

# Then you can reference scene.temp_snapshot
```

### Reload Scenes

```yaml
# After editing scenes.yaml
# Developer Tools > YAML > Reload Scenes

# Or via service
service: scene.reload
```
