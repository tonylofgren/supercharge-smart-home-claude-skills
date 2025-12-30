# Installation Guide

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and configured
- Active Claude account with API access

---

## Installation

```bash
# Add the marketplace repository
/plugin marketplace add tonylofgren/supercharge-smart-home-claude-skills

# Install the skill (choose one scope)
/plugin install supercharge-home-assistant-skill                    # Global (default)
/plugin install supercharge-home-assistant-skill --scope project    # Team (shared via git)
/plugin install supercharge-home-assistant-skill --scope local      # This project only
```

Restart Claude Code after installation.

---

## Verify Installation

Test by asking:
```
Create a simple automation that turns on a light when motion is detected
```

**Expected:** A complete Home Assistant YAML configuration with an offer to save.

---

## Update

```bash
/plugin update supercharge-home-assistant-skill
```

### Enable Auto-Update

1. Run `/plugin` to open the plugin manager
2. Go to **Marketplaces** tab
3. Select `supercharge-smart-home-claude-skills`
4. Choose **Enable auto-update**

---

## Uninstall

Use the interactive UI for complete removal:

1. Run `/plugin`
2. Go to **Installed** tab
3. Select `supercharge-home-assistant-skill`
4. Choose **Uninstall**

**Note:** The CLI command `/plugin uninstall` only disables plugins.

---

## Change Scope

To move from one scope to another (e.g., user → local):

1. Uninstall via interactive UI (see above)
2. Reinstall with new scope:
   ```bash
   /plugin install supercharge-home-assistant-skill --scope local
   ```

---

## Troubleshooting

### Skill Not Triggering

1. Verify installation: `/plugin`
2. Restart Claude Code
3. Try rephrasing with keywords: "Home Assistant", "automation", "smart home"

### Template Errors

1. Specify your HA version in requests
2. Report issues on [GitHub](https://github.com/tonylofgren/supercharge-smart-home-claude-skills/issues)

---

## Getting Help

- **Usage examples:** See [USAGE-GUIDE.md](USAGE-GUIDE.md)
- **300+ prompts:** See [PROMPT-IDEAS.md](PROMPT-IDEAS.md)
- **Issues:** [GitHub Issues](https://github.com/tonylofgren/supercharge-smart-home-claude-skills/issues)
