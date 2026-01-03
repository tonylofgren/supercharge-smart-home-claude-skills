<p align="center">
  <img src="assets/banner.png" alt="Aurora Smart Home - Claude Skills" width="100%">
</p>

# Aurora Smart Home

> **75,000+ lines** of documentation | **900+ example prompts** | **1,500+ code examples**

The most comprehensive Claude Code skill pack for smart home development.

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skills-7c3aed.svg)](https://docs.anthropic.com/en/docs/claude-code)
[![Home Assistant](https://img.shields.io/badge/Home_Assistant-2024.x%2F2025.x-41BDF5.svg)](https://www.home-assistant.io/)
[![ESPHome](https://img.shields.io/badge/ESPHome-ESP32%2FESP8266-000000.svg)](https://esphome.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## At a Glance

|  | Home Assistant | Node-RED | ESPHome | Integration Dev |
|---|:---:|:---:|:---:|:---:|
| **Reference Guides** | 49 | 12 | 25 | 17 |
| **Example Prompts** | 300+ | 100+ | 600+ | 129 |
| **Code Examples** | 700+ | 200+ | 1000+ | 200+ |
| **Ready Templates** | 17 | 15 | 27 | 10 |
| **Coverage** | 50+ integrations | 31 nodes | 160+ components | Full HA framework |

---

## Choosing the Right Skill

| I want to... | Use this skill |
|--------------|----------------|
| Create **YAML automations** (automations.yaml, blueprints) | `ha-yaml` |
| Build **visual Node-RED flows** (drag-and-drop, JSON) | `node-red` |
| Configure **ESP32/ESP8266 device firmware** | `esphome` |
| Develop **Python custom components** (HACS) | `ha-integration` |

> **Tip:** If your request is ambiguous (e.g., "make a motion light"), the skill will ask which platform you prefer.

---

## Quick Start

```bash
# Add the marketplace repository
/plugin marketplace add tonylofgren/aurora-smart-home

# Install for yourself globally (default - works across all projects)
/plugin install ha-yaml@aurora-smart-home
/plugin install node-red@aurora-smart-home
/plugin install esphome@aurora-smart-home
/plugin install ha-integration@aurora-smart-home

# OR install for your team (shared via git)
/plugin install ha-yaml@aurora-smart-home --scope project
/plugin install node-red@aurora-smart-home --scope project
/plugin install esphome@aurora-smart-home --scope project
/plugin install ha-integration@aurora-smart-home --scope project

# OR install for yourself in this project only (gitignored)
/plugin install ha-yaml@aurora-smart-home --scope local
/plugin install node-red@aurora-smart-home --scope local
/plugin install esphome@aurora-smart-home --scope local
/plugin install ha-integration@aurora-smart-home --scope local
```

---

## How Skills Activate

Skills activate in two ways:

### 1. Automatic (Contextual)

Just mention keywords naturally - skills load automatically:

| Skill | Triggers on |
|-------|-------------|
| `node-red` | "node-red" anywhere (even "node-redflöde", "Node-RED-flow") |
| `esphome` | "ESPHome", "ESP32", "ESP8266", device firmware |
| `ha-yaml` | "YAML automation", "blueprint", "automations.yaml" |
| `ha-integration` | "custom integration", "HACS", "custom_components" |

> **Language-independent:** Product names like "Node-RED" and "ESPHome" work in any language.

### 2. Explicit (Slash Commands)

Use slash commands when contextual activation misses:

```
/aurora:node-red       - Node-RED flows
/aurora:esphome        - ESPHome configs
/aurora:ha-yaml        - Home Assistant YAML
/aurora:ha-integration - Python custom integrations
```

> **Tip:** Type `/aurora:` to see all available commands.

---

## Getting Started with Your First Project

After installation, be explicit about which platform you want. Examples:

```
💬 "Create an ESPHome config for an ESP32 temperature sensor with OLED display"
   → ESPHome skill activates, asks about board, generates complete config

💬 "Create a Home Assistant automation that turns on lights at sunset"
   → HA-YAML skill activates, clarifies format, creates YAML automation

💬 "Create a Node-RED flow for motion-activated lights"
   → Node-RED skill activates, generates importable JSON flow

💬 "Create a Python custom integration for the Acme cloud API"
   → HA-Integration skill activates, guides through architecture
```

### Example Projects

The `examples/` folder contains complete, working projects:

| Example | Description |
|---------|-------------|
| [complete-smart-room](./examples/complete-smart-room/) | Full room with sensors, voice control, automations |
| [smart-greenhouse](./examples/smart-greenhouse/) | Automated irrigation, climate monitoring, grow lights |
| [smart-garage](./examples/smart-garage/) | Garage door control, car detection, safety features |
| [energy-monitor](./examples/energy-monitor/) | CT clamp power monitoring, cost tracking, alerts |

### How Skills Work Together

See [SKILL-INTEGRATION.md](./SKILL-INTEGRATION.md) for detailed workflows showing how ESPHome → HA Integration → HA Automation skills connect.

---

## What's Included

### Home Assistant YAML Skill (`ha-yaml`)

Create **YAML-based automations**, scripts, blueprints, templates, and dashboards.

| Feature | Count |
|---------|-------|
| Reference guides | 49 |
| Example prompts | 300+ |
| YAML code examples | 700+ |
| Production-ready templates | 17 |
| Integrations covered | 50+ |

**Covers:** Automations, scripts, blueprints, templates, dashboards, Jinja2, MQTT, Zigbee2MQTT, ZHA, Z-Wave, Matter, Bluetooth, Frigate, Tuya, Shelly, and more.

[View Home Assistant documentation](./home-assistant/README.md)

---

### Node-RED Skill (`node-red`)

Build **visual automation flows** using node-red-contrib-home-assistant-websocket.

| Feature | Count |
|---------|-------|
| Reference guides | 12 |
| Example prompts | 100+ |
| Flow examples | 200+ |
| Ready-to-import templates | 15 |
| Nodes covered | 31 |

**Covers:** All HA websocket nodes, motion lights, presence detection, notifications, climate control, media, voice commands, state machines, and more.

[View Node-RED documentation](./node-red/README.md)

---

### ESPHome Skill (`esphome`)

Configure **ESP32/ESP8266 device firmware** - sensors, displays, LEDs, and more.

| Feature | Count |
|---------|-------|
| Reference guides | 25 |
| Project prompts | 600+ |
| Configuration examples | 1000+ |
| Device templates | 27 |
| Components covered | 160+ |

**Covers:** Sensors, displays, climate control, LED strips, BLE, motors, IR/RF remotes, power monitoring, voice assistants, and device conversions (Shelly, Sonoff, Tuya).

**Supports:** ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP8266

[View ESPHome documentation](./esphome/README.md)

---

### Integration Development Skill (`ha-integration`)

Develop **Python custom components** for Home Assistant (custom_components, HACS).

| Feature | Count |
|---------|-------|
| Reference guides | 17 |
| Development prompts | 129 |
| Code examples | 200+ |
| Starter templates | 10 |

**Covers:** Config flows, DataUpdateCoordinator, entity platforms (20+), services, events, device registry, OAuth2, WebSocket, HACS publishing, Core contribution.

**Templates:** Basic, polling, push, OAuth2, multi-device hub, service, Bluetooth, conversation agent, media player, webhook.

[View Integration Dev documentation](./ha-integration-dev/README.md)

---

## Why This Skill Pack?

- **Saves hours** - No more searching through docs and forums
- **Always current** - Covers HA 2024.x/2025.x and latest ESPHome
- **Copy-paste ready** - 54 templates you can use immediately
- **Battle-tested patterns** - Based on community best practices
- **Complete coverage** - From beginner to advanced use cases

---

## Installation

See individual skill READMEs for detailed installation and usage:
- [Home Assistant Installation](./home-assistant/INSTALLATION.md)
- [ESPHome Installation](./esphome/INSTALLATION.md)

## Update & Uninstall

```bash
# Update a skill
/plugin update ha-yaml@aurora-smart-home
/plugin update node-red@aurora-smart-home
/plugin update esphome@aurora-smart-home
/plugin update ha-integration@aurora-smart-home

# Uninstall a skill (use interactive UI - see note below)
/plugin uninstall ha-yaml@aurora-smart-home
/plugin uninstall node-red@aurora-smart-home
/plugin uninstall esphome@aurora-smart-home
/plugin uninstall ha-integration@aurora-smart-home
```

---

## Enable Auto-Update

Auto-update keeps your skills current automatically.

1. Run `/plugin` to open the plugin manager
2. Go to **Marketplaces** tab
3. Select `aurora-smart-home`
4. Choose **Enable auto-update**

Skills will update automatically when Claude Code starts.

---

## Change Installation Scope

To move a plugin from one scope to another (e.g., user → local):

1. Run `/plugin` to open the plugin manager
2. Go to **Installed** tab
3. Select the plugin and choose **Uninstall**
4. Reinstall with new scope:
   ```bash
   /plugin install ha-yaml@aurora-smart-home --scope local
   ```

**Note:** Use the interactive UI to uninstall - the CLI command `/plugin uninstall` only disables plugins.

---

## Troubleshooting

Having issues? Check the [Troubleshooting Guide](./TROUBLESHOOTING.md) for common problems and solutions across all skills.

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and recent updates.

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Created for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic.
