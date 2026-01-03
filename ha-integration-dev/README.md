# Home Assistant Python Integration Development Skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/tonylofgren/aurora-smart-home/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Complete reference for developing **Home Assistant custom integrations in Python**. From config flows to entity platforms, coordinators to services.

> **When to use this skill:** Use when you want to develop a Python custom component (custom_components, HACS).
> For YAML automations, use `home-assistant`. For visual flows, use `node-red`. For device firmware, use `esphome`.

---

## Quick Start

1. **Add the marketplace**
   ```
   /plugin marketplace add tonylofgren/aurora-smart-home
   ```

2. **Install the skill**
   ```
   /plugin install ha-integration@aurora-smart-home
   ```

3. **Restart Claude Code** (exit and reopen)

4. **Start developing**
   ```
   You: Create a Python custom integration for my smart thermostat cloud API
   ```

---

## What Can This Skill Do?

| Category | Coverage |
|----------|----------|
| **Config Flow** | User setup, OAuth2, Zeroconf/SSDP/DHCP discovery, reauth, reconfigure |
| **Data Fetching** | DataUpdateCoordinator, WebSocket push, polling, caching |
| **Entity Platforms** | 20+ types: sensor, switch, climate, cover, light, media_player, vacuum... |
| **Multi-Device Hub** | Parent/child devices, EntityDescription pattern, dynamic entities |
| **Services & Events** | Custom services with responses, event firing/listening |
| **Security** | HTTPS, input validation, credential handling, rate limiting |
| **Testing** | pytest patterns, mocking, config flow tests |
| **Publishing** | HACS preparation, GitHub workflows, Core contribution |

---

## Reference Files

| Topic | File |
|-------|------|
| Architecture & manifest.json | `references/architecture.md` |
| Config & Options flow | `references/config-flow.md` |
| DataUpdateCoordinator | `references/coordinator.md` |
| Entity platforms (20+) | `references/entities.md` |
| EntityDescription pattern | `references/entity-description.md` |
| Services & Events | `references/services-events.md` |
| Device registry | `references/device-registry.md` |
| Security best practices | `references/security.md` |
| Testing patterns | `references/testing.md` |
| HACS & Core publishing | `references/publishing.md` |

---

## Templates

Starter templates for common integration patterns:

| Template | Use Case |
|----------|----------|
| `basic-integration/` | Minimal starter |
| `polling-integration/` | Cloud API with DataUpdateCoordinator |
| `push-integration/` | WebSocket/event-based |
| `oauth-integration/` | OAuth2 authentication |
| `multi-device-hub/` | Hub with child devices |
| `service-integration/` | Custom services with responses |

---

## Disclaimer

Templates and code examples follow [Home Assistant's official development documentation](https://developers.home-assistant.io/) and established community patterns.

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

Created for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) by Anthropic.
