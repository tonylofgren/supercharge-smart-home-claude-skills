# Home Assistant YAML Automation Skill

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.x%20%2F%202025.x-blue.svg)](https://www.home-assistant.io/)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-purple.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Claude Code skill for creating **Home Assistant YAML automations**, scripts, blueprints, templates, and dashboard configurations.

> **When to use this skill:** Use when you want YAML-based automations (automations.yaml, blueprints).
> For visual flows, use `node-red`. For device firmware, use `esphome`. For Python custom components, use `ha-integration`.

## Features

- **Complete Automation Support** - Create automations in YAML or UI format with all trigger, condition, and action types
- **Script Generation** - Build reusable scripts with sequences, variables, and conditional logic
- **Blueprint Creation** - Design reusable automation blueprints with configurable inputs
- **Jinja2 Templates** - Write template sensors, conditions, and notifications with proper syntax
- **Integration Guides** - MQTT, ESPHome, Zigbee2MQTT, ZHA, Z-Wave, Matter, Node-RED, Bluetooth, Frigate NVR, Shelly, Tuya, Tasmota, Samsung/LG/Android TV, and cameras
- **AI/LLM Integration** - Local LLM (Ollama), OpenAI Conversation, prompt engineering, and LLM-based automations
- **Dashboard Configuration** - Create Lovelace dashboards with modern cards (Tile, Grid, Sections, Heading)
- **Mushroom Cards** - Comprehensive guide to the most popular custom card collection
- **Voice Assistants** - Set up Assist pipeline with Whisper, Piper, Wyoming satellites, and LLM conversation agents
- **Advanced Triggers** - Wait for State (2024.4+), Conversation triggers, debouncing, and performance optimization
- **Device Class Reference** - Complete device_class to unit_of_measurement mapping and validation rules
- **Energy Management** - Grid-aware scheduling, solar surplus, EV charging, and spot price optimization
- **Advanced Patterns** - State machines, multi-area coordination, error handling, and rate limiting
- **Backup & Migration** - Backup strategies, restore procedures, and version upgrade guides
- **Troubleshooting Help** - Debug automations, fix template errors, and resolve common issues
- **Best Practices** - Follow naming conventions, security guidelines, and performance tips

## What's Included

```
home-assistant/
├── SKILL.md                    # Main skill definition (700+ lines)
├── README.md                   # This file
├── INSTALLATION.md             # Setup guide
├── USAGE-GUIDE.md              # 70+ practical usage examples
├── PROMPT-IDEAS.md             # 600+ categorized prompt ideas
├── LICENSE                     # MIT license
│
├── references/                 # 48 reference files (~1.1 MB)
│   ├── automations.md          # Complete automation reference
│   ├── scripts.md              # Script patterns
│   ├── blueprints.md           # Blueprint creation
│   ├── scenes.md               # Scene configuration
│   ├── helpers.md              # input_boolean, input_number, etc.
│   ├── configuration.md        # configuration.yaml structure
│   ├── packages.md             # Package organization
│   ├── jinja2-templates.md     # Jinja2 templating guide
│   ├── template-sensors.md     # Template sensors + advanced patterns
│   ├── conditions.md           # Condition types
│   ├── actions.md              # Action types
│   ├── triggers-advanced.md    # Wait for State, Conversation triggers
│   ├── device-class-units.md   # Device class to units mapping
│   ├── integrations-mqtt.md    # MQTT setup
│   ├── integrations-esphome.md # ESPHome integration
│   ├── integrations-zigbee2mqtt.md # Zigbee2MQTT
│   ├── integrations-zwave.md   # Z-Wave JS setup
│   ├── integrations-matter.md  # Matter/Thread devices
│   ├── integrations-nodered.md # Node-RED connection
│   ├── integrations-common.md  # Hue, Sonos, Google, Alexa
│   ├── integrations-ai-llm.md  # Ollama, OpenAI, LLM automations
│   ├── integrations-bluetooth.md # Native BLE, ESPHome proxy, tracking
│   ├── integrations-frigate.md # Frigate NVR, object detection
│   ├── dashboards.md           # Lovelace + modern cards (2024+)
│   ├── dashboard-cards.md      # Card types, heading cards, features
│   ├── mushroom-cards.md       # Mushroom cards comprehensive guide
│   ├── custom-components.md    # HACS components
│   ├── custom-card-development.md # Creating custom cards
│   ├── voice-assistants.md     # Assist, Whisper, Piper, LLM agents
│   ├── energy-ev-charging.md   # EV charging, smart charging, solar
│   ├── advanced-patterns.md    # State machines, multi-area
│   ├── backup-restore-migration.md # Backup & disaster recovery
│   ├── troubleshooting.md      # Common issues + Trace API
│   ├── best-practices.md       # Guidelines
│   ├── migration-guide.md      # Version upgrades
│   ├── cookbook.md             # Complete project examples
│   ├── integrations-zha.md     # ZHA native Zigbee
│   ├── integrations-tuya.md    # Tuya + Local Tuya (HACS)
│   ├── integrations-tasmota.md # Tasmota firmware
│   ├── integrations-shelly.md  # Shelly devices
│   ├── integrations-media.md   # Samsung, LG, Android TV
│   ├── integrations-cameras.md # Reolink, Synology, RTSP
│   ├── hacs-popular.md         # Popular HACS integrations
│   ├── utility-meter.md        # Energy tracking, tariffs
│   ├── system-monitor.md       # System health
│   ├── statistics.md           # Long-term statistics
│   └── weather-integration.md  # Met.no, weather automations
│
└── assets/templates/           # 15 ready-to-use YAML templates
    ├── automation-motion-light.yaml
    ├── automation-presence-away.yaml
    ├── automation-climate-schedule.yaml
    ├── automation-state-machine.yaml
    ├── automation-error-handling.yaml   # NEW: Retry/rollback patterns
    ├── automation-weather-based.yaml    # NEW: Weather forecast automation
    ├── automation-energy-optimization.yaml # NEW: Grid-aware scheduling
    ├── script-notification-actionable.yaml
    ├── script-scene-controller.yaml
    ├── script-rate-limiting.yaml        # NEW: Rate-limited actions
    ├── blueprint-motion-light.yaml
    ├── template-sensor-aggregation.yaml
    ├── dashboard-home-view.yaml
    ├── dashboard-energy-monitoring.yaml # NEW: Energy dashboard
    └── package-room-template.yaml
```

## Quick Start

### Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

**Quick install via Claude Code:**

```bash
# In Claude Code, add the marketplace repository
/plugin marketplace add tonylofgren/aurora-smart-home

# Then install the skill
/plugin install ha-yaml@aurora-smart-home
```

See [INSTALLATION.md](INSTALLATION.md) for all installation options including scope selection.

### Usage

Once installed, the skill activates automatically when you ask about Home Assistant topics:

```
"Create an automation that turns on the porch light at sunset"
"Help me write a script for a movie mode"
"How do I create a blueprint for motion lights?"
"Why isn't my automation triggering?"
```

See [USAGE-GUIDE.md](USAGE-GUIDE.md) for 70+ detailed examples including debugging workflows.

## Example Outputs

### Motion-Activated Light Automation

```yaml
# Generated by ha-yaml@aurora-smart-home v1.0.0
# https://github.com/tonylofgren/aurora-smart-home

automation:
  - id: motion_light_hallway
    alias: "Motion Light - Hallway"
    description: "Turn on hallway light when motion detected"
    mode: restart
    trigger:
      - platform: state
        entity_id: binary_sensor.hallway_motion
        to: "on"
    condition:
      - condition: numeric_state
        entity_id: sensor.hallway_illuminance
        below: 30
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
        data:
          brightness_pct: >
            {% if now().hour >= 22 or now().hour < 6 %}
              20
            {% else %}
              100
            {% endif %}
          transition: 1
      - wait_for_trigger:
          - platform: state
            entity_id: binary_sensor.hallway_motion
            to: "off"
            for:
              minutes: 3
      - service: light.turn_off
        target:
          entity_id: light.hallway
        data:
          transition: 2
```

### Template Sensor

```yaml
# Generated by ha-yaml@aurora-smart-home v1.0.0
# https://github.com/tonylofgren/aurora-smart-home

template:
  - sensor:
      - name: "HVAC Running Time Today"
        unit_of_measurement: "h"
        state: >
          {% set hvac = states('climate.living_room') %}
          {% if hvac in ['heat', 'cool'] %}
            {{ (states('sensor.hvac_runtime_minutes') | float(0) / 60) | round(1) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:clock-outline
```

### Blueprint

```yaml
# Generated by ha-yaml@aurora-smart-home v1.0.0
# https://github.com/tonylofgren/aurora-smart-home

blueprint:
  name: Motion-Activated Light with Timeout
  description: Turn on a light when motion is detected, with configurable timeout
  domain: automation
  input:
    motion_sensor:
      name: Motion Sensor
      selector:
        entity:
          domain: binary_sensor
          device_class: motion
    target_light:
      name: Light
      selector:
        target:
          entity:
            domain: light
    timeout:
      name: Timeout
      description: Time to wait after motion stops
      default: 300
      selector:
        number:
          min: 30
          max: 3600
          unit_of_measurement: seconds

trigger:
  - platform: state
    entity_id: !input motion_sensor
    to: "on"

action:
  - service: light.turn_on
    target: !input target_light
  - wait_for_trigger:
      - platform: state
        entity_id: !input motion_sensor
        to: "off"
        for:
          seconds: !input timeout
  - service: light.turn_off
    target: !input target_light
```

## Skill Triggers

The skill activates when you want to:

1. Create or modify Home Assistant automations
2. Write scripts with sequences and logic
3. Create blueprints for reusable automations
4. Configure scenes
5. Set up helpers (input_boolean, input_number, etc.)
6. Organize configuration using packages
7. Write Jinja2 templates
8. Create template sensors
9. Configure MQTT entities
10. Integrate ESPHome devices
11. Set up Zigbee2MQTT
12. Connect Node-RED
13. Create Lovelace dashboards
14. Troubleshoot automation issues
15. Migrate from deprecated YAML
16. Customize entities
17. Set up notifications
18. Configure device triggers
19. Create calendar-based automations
20. Set up presence detection
21. Configure media player automations
22. Debug automation traces

## Coverage

### Trigger Types
- State, Numeric State, Time, Time Pattern
- Sun (sunrise/sunset), Zone, Event
- MQTT, Webhook, Device, Calendar
- Template, Tag, Sentence (voice)

### Condition Types
- State, Numeric State, Time, Sun
- Zone, Template, Device
- And, Or, Not (logical combinations)
- Trigger condition

### Action Types
- Service calls, Delay, Wait template
- Wait for trigger, Choose, If/Then/Else
- Repeat, Parallel, Stop, Variables

### Integrations
- **MQTT** - Entities, discovery, topics
- **ESPHome** - Services, events, entities
- **Zigbee2MQTT** - Groups, bindings, availability
- **ZHA** - Native Zigbee, pairing, bindings, device triggers
- **Z-Wave** - Z-Wave JS setup, pairing, network management
- **Matter** - Matter/Thread devices, commissioning, bridges
- **Bluetooth** - Native BLE, ESPHome proxy, presence tracking
- **Frigate** - NVR setup, object detection, zone alerts
- **Shelly** - Gen1/Gen2+ devices, CoAP, MQTT, scripting
- **Tuya** - Cloud + Local Tuya (HACS), DP configuration
- **Tasmota** - Firmware setup, templates, rules
- **Media Players** - Samsung TV, LG webOS, Android TV, Apple TV
- **Cameras** - Reolink, Synology, generic RTSP, ONVIF
- **Node-RED** - Webhooks, WebSocket API
- **AI/LLM** - Ollama, OpenAI Conversation, prompt engineering
- **Common** - Hue, Sonos, Google, Alexa, Calendar

### Dashboard
- Lovelace modes (storage/YAML)
- Modern cards (Tile, Grid, Sections, Heading - 2024+)
- Mushroom cards comprehensive guide
- All native card types
- Themes and resources
- Custom card development guide
- Custom cards via HACS

### Energy Management
- EV charging integrations (Easee, Wallbox, Tesla, Zaptec)
- Smart charging with spot prices
- Solar surplus charging
- Multi-vehicle support
- Grid load balancing

### Voice Assistants
- Assist pipeline configuration
- Whisper (local speech-to-text)
- Piper (local text-to-speech)
- Wyoming protocol and satellites
- Custom intents and sentences

### Advanced Patterns
- State machines (presence, appliance cycles)
- Multi-area coordination
- Error handling with retries
- Cascading automations

## Target Version

This skill targets **Home Assistant 2024.x / 2025.x** and follows current best practices. Deprecated syntax is noted where relevant, with migration guides included.

## Documentation

- [SKILL.md](SKILL.md) - Complete skill reference
- [INSTALLATION.md](INSTALLATION.md) - Setup instructions
- [USAGE-GUIDE.md](USAGE-GUIDE.md) - 70+ usage examples with debugging guides
- [PROMPT-IDEAS.md](PROMPT-IDEAS.md) - 600+ prompt ideas
- [references/](references/) - 48 topic-specific reference files

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Created for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic.

---

**Note:** This skill generates Home Assistant configurations based on your requirements. Always review generated code before applying to your production Home Assistant instance.
