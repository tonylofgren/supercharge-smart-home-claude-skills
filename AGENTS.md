# AGENTS.md

Aurora Smart Home is a reference library for building and troubleshooting
Home Assistant, ESPHome, Node-RED, and related smart-home projects. It ships
as a Claude Code plugin, but the reference content underneath is plain
Markdown, readable and usable from Codex too.

## How to use this repo from Codex

There is no installer step. When a request touches one of the domains below,
open the matching `SKILL.md` first: it is the entry point for that domain
and links out to the detailed reference files (board/component data,
official HA/ESPHome doc snapshots, recipes, troubleshooting guides). Treat
its instructions as authoritative for that domain, the same way you would
follow any other file this repo tells you to read.

| Domain                                         | Read first                            |
|-------------------------------------------------|----------------------------------------|
| Not sure which domain, or it spans more than one| `aurora/SKILL.md`                      |
| ESPHome firmware (ESP32, ESP8266, Shelly, boards, sensors, BLE/Matter/Thread, audio, power) | `esphome/SKILL.md` |
| Home Assistant YAML (automations, scripts, dashboards, templates, blueprints) | `home-assistant/SKILL.md` |
| Custom Python integrations (HACS, config_flow, coordinators) | `ha-integration-dev/SKILL.md` |
| Node-RED visual flows | `node-red/SKILL.md` |
| External API integration (Tibber, SMHI, SL, Spotify, etc.) | `api-catalog/SKILL.md` |
| Dashboard visual styling (Mushroom, card-mod, themes) | `ha-dashboard-design/SKILL.md` |

`aurora/SKILL.md` also documents the routing logic in full (which specialist
persona owns which keywords, model recommendations, delivery conventions).
Read it when a request could plausibly belong to more than one domain above.

## What does not carry over from Claude Code

This repo also ships Claude Code-specific plugin plumbing:
`.claude-plugin/marketplace.json`, hooks, and the `/aurora:aurora` slash
command. None of that applies to Codex; it is packaging for the Claude Code
plugin marketplace, not part of the reference content. Codex should read the
`SKILL.md` files directly as documentation, as described above.

## Repo-wide conventions

Everything committed to this repo (docs, code, commit messages) is written
in English, even though maintainers may discuss it in other languages. See
`CLAUDE.md` for the full contributor rules (copyright/attribution handling
for third-party doc content, commit message style, etc.). They apply
regardless of which agent is doing the writing.
