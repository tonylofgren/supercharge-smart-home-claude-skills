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
/plugin install supercharge-esphome-skill                    # Global (default)
/plugin install supercharge-esphome-skill --scope project    # Team (shared via git)
/plugin install supercharge-esphome-skill --scope local      # This project only
```

Restart Claude Code after installation.

---

## Verify Installation

Test by asking:
```
Create a simple ESP32 temperature sensor config
```

**Expected:** A complete ESPHome YAML configuration with an offer to save.

---

## Update

```bash
/plugin update supercharge-esphome-skill
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
3. Select `supercharge-esphome-skill`
4. Choose **Uninstall**

**Note:** The CLI command `/plugin uninstall` only disables plugins.

---

## Change Scope

To move from one scope to another (e.g., user → local):

1. Uninstall via interactive UI (see above)
2. Reinstall with new scope:
   ```bash
   /plugin install supercharge-esphome-skill --scope local
   ```

---

## Secrets Configuration

The skill generates configs using `!secret` references. Add to your ESPHome `secrets.yaml`:

```yaml
wifi_ssid: "YourWiFiName"
wifi_password: "YourWiFiPassword"
api_encryption_key: "your-32-byte-base64-key"  # Generate: openssl rand -base64 32
ota_password: "your-ota-password"
```

---

## Troubleshooting

### Skill Not Triggering

1. Verify installation: `/plugin`
2. Restart Claude Code
3. Try rephrasing with keywords: "ESP32", "ESPHome", "sensor config"

### Generated Config Has Errors

1. Check ESPHome version compatibility
2. Verify pin assignments for your board
3. Ask: "Fix this ESPHome error: [paste error]"

---

## Getting Help

- **Usage examples:** See [USAGE-GUIDE.md](USAGE-GUIDE.md)
- **600+ prompts:** See [PROMPT-IDEAS.md](PROMPT-IDEAS.md)
- **Issues:** [GitHub Issues](https://github.com/tonylofgren/supercharge-smart-home-claude-skills/issues)
