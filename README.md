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

|  | Home Assistant | ESPHome | Integration Dev |
|---|:---:|:---:|:---:|
| **Reference Guides** | 49 | 24 | 17 |
| **Example Prompts** | 300+ | 600+ | 129 |
| **Code Examples** | 700+ | 950+ | 200+ |
| **Ready Templates** | 17 | 15 | 6 |
| **Coverage** | 50+ integrations | 160+ components | Full HA framework |

---

## Quick Start

```bash
# Add the marketplace repository
/plugin marketplace add tonylofgren/aurora-smart-home

# Install for yourself globally (default - works across all projects)
/plugin install ha-yaml@aurora-smart-home
/plugin install esphome@aurora-smart-home
/plugin install ha-integration@aurora-smart-home

# OR install for your team (shared via git)
/plugin install ha-yaml@aurora-smart-home --scope project
/plugin install esphome@aurora-smart-home --scope project
/plugin install ha-integration@aurora-smart-home --scope project

# OR install for yourself in this project only (gitignored)
/plugin install ha-yaml@aurora-smart-home --scope local
/plugin install esphome@aurora-smart-home --scope local
/plugin install ha-integration@aurora-smart-home --scope local
```

---

## What's Included

### Home Assistant Skill (`ha-yaml`)

Your complete companion for Home Assistant configuration and automation.

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

### ESPHome Skill (`esphome`)

Everything you need for ESP32/ESP8266 device development.

| Feature | Count |
|---------|-------|
| Reference guides | 24 |
| Project prompts | 600+ |
| Configuration examples | 950+ |
| Device templates | 15 |
| Components covered | 160+ |

**Covers:** Sensors, displays, climate control, LED strips, BLE, motors, IR/RF remotes, power monitoring, voice assistants, and device conversions (Shelly, Sonoff, Tuya).

**Supports:** ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP8266

[View ESPHome documentation](./esphome/README.md)

---

### Integration Development Skill (`ha-integration`)

Build custom Home Assistant integrations in Python.

| Feature | Count |
|---------|-------|
| Reference guides | 17 |
| Development prompts | 129 |
| Code examples | 200+ |
| Starter templates | 6 |

**Covers:** Config flows, DataUpdateCoordinator, entity platforms (20+), services, events, device registry, OAuth2, WebSocket, HACS publishing, Core contribution.

**Templates:** Basic, polling, push, OAuth2, multi-device hub, service integration.

[View Integration Dev documentation](./ha-integration-dev/README.md)

---

## Why This Skill Pack?

- **Saves hours** - No more searching through docs and forums
- **Always current** - Covers HA 2024.x/2025.x and latest ESPHome
- **Copy-paste ready** - 38 templates you can use immediately
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
/plugin update esphome@aurora-smart-home
/plugin update ha-integration@aurora-smart-home

# Uninstall a skill (use interactive UI - see note below)
/plugin uninstall ha-yaml@aurora-smart-home
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

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Created for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic.
