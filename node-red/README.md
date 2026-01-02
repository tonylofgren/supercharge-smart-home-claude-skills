# Node-RED Flow Automation Skill

A comprehensive Claude Code skill for building visual automations with Node-RED and Home Assistant.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/tonylofgren/aurora-smart-home)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Node-RED](https://img.shields.io/badge/Node--RED-3.0+-red.svg)](https://nodered.org/)

## Features

| Category | Coverage |
|----------|----------|
| **Core Concepts** | Flows, nodes, wires, messages, context, subflows |
| **HA Integration** | All 31 nodes from node-red-contrib-home-assistant-websocket |
| **Patterns** | Motion lights, presence, notifications, state machines |
| **Templates** | 12 ready-to-import JSON flows |
| **Troubleshooting** | Common issues, debug techniques, flowcharts |

## Quick Start

### Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

**As Claude Code Plugin:**
```bash
# Add to Claude Code
claude mcp add aurora-smart-home -- npx -y @anthropic-ai/claude-code-mcp@latest \
  /path/to/aurora-smart-home/node-red
```

**Project-based (in .mcp.json):**
```json
{
  "mcpServers": {
    "node-red": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/claude-code-mcp@latest", "/path/to/node-red"]
    }
  }
}
```

### Usage

Simply ask Claude about Node-RED:

```
"Help me create a motion-triggered light automation in Node-RED"
"How do I use the Trigger: state node?"
"Create a subflow for notification handling"
"Debug my flow - it's not triggering"
```

## What's Included

### References (25 files)

**Core Concepts:**
- `core-concepts.md` - Flows, nodes, wires, messages
- `node-types.md` - Input, output, function, config nodes
- `message-handling.md` - msg object, payload, routing
- `context-storage.md` - Node, flow, global context
- `subflows.md` - Creating reusable components

**Home Assistant Integration:**
- `ha-setup.md` - Installation, addon vs external
- `ha-trigger-nodes.md` - Events:state, Trigger:state, Device, Time, Zone
- `ha-action-nodes.md` - Action, Fire Event, API
- `ha-state-nodes.md` - Current State, Get Entities, Get History
- `ha-entity-nodes.md` - Sensor, Binary Sensor, Switch, Button
- `ha-advanced-nodes.md` - Webhook, Tag, Sentence, Render Template

**Patterns & Best Practices:**
- `automation-patterns.md` - Common automation recipes
- `flow-organization.md` - Tabs, naming, groups
- `state-machines.md` - Complex state management
- `error-handling.md` - Catch nodes, retry logic
- `performance.md` - Caching, debouncing
- `security.md` - Token management, webhook auth

**Advanced Topics:**
- `function-nodes.md` - JavaScript in Node-RED
- `jsonata.md` - JSONata expressions
- `mqtt-integration.md` - MQTT + HA patterns
- `external-apis.md` - HTTP requests, webhooks

**Troubleshooting:**
- `troubleshooting.md` - Common issues and solutions
- `troubleshooting-flowcharts.md` - Visual debug guides
- `node-reference.md` - All 31 HA nodes quick reference
- `cookbook.md` - Copy-paste examples

### Templates (12 flows)

| Template | Description |
|----------|-------------|
| `basic-motion-light.json` | Simple motion lighting |
| `advanced-motion-light.json` | Day/night, manual override |
| `presence-detection.json` | Multi-sensor presence |
| `notification-router.json` | Smart notifications |
| `climate-control.json` | Temperature-based HVAC |
| `security-alerts.json` | Door/window monitoring |
| `scene-controller.json` | Button scenes |
| `energy-monitor.json` | Power tracking |
| `appliance-tracker.json` | Washer/dryer state |
| `subflow-debounce.json` | Reusable debounce |
| `subflow-notification.json` | Standard notifications |

## Node-RED HA Nodes Covered

**Config Nodes (3):**
Device Config, Entity Config, Server Config

**Trigger/General Nodes (19):**
Action, API, Current State, Device, Events:all, Events:calendar, Events:state, Fire Event, Get Entities, Get History, Poll State, Render Template, Sentence, Tag, Time, Trigger:state, Wait Until, Webhook, Zone

**Entity Nodes (9):**
Binary Sensor, Button, Entity, Number, Select, Sensor, Switch, Text, Time, Update Config

## Example Prompts

### Beginner
- "Create a simple motion light automation"
- "How do I connect Node-RED to Home Assistant?"
- "Explain the difference between Events:state and Trigger:state"

### Intermediate
- "Create a presence detection system using multiple sensors"
- "Build a notification router that checks who's home"
- "Help me create a subflow for debouncing rapid events"

### Advanced
- "Implement a state machine for my alarm system"
- "Create an integration with an external weather API"
- "Build a self-healing flow with retry logic"

See [PROMPT-IDEAS.md](PROMPT-IDEAS.md) for 500+ example prompts.

## Contributing

Contributions welcome! See the main repository's [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE)

---

Part of [Aurora Smart Home](https://github.com/tonylofgren/aurora-smart-home) - Claude Code skills for home automation.
