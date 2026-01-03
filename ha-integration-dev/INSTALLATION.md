# Installation Guide

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and configured
- Active Claude account with API access
- Python 3.11+ (for running generated integrations)
- Home Assistant development environment (recommended)

---

## Installation

```bash
# Add the marketplace repository
/plugin marketplace add tonylofgren/aurora-smart-home

# Install the skill (choose one scope)
/plugin install ha-integration@aurora-smart-home                    # Global (default)
/plugin install ha-integration@aurora-smart-home --scope project    # Team (shared via git)
/plugin install ha-integration@aurora-smart-home --scope local      # This project only
```

Restart Claude Code after installation.

---

## Verify Installation

Test by asking:
```
Create a basic Python custom integration skeleton for Home Assistant
```

**Expected:** A complete custom_components structure with:
- `__init__.py` with async_setup_entry
- `config_flow.py` with ConfigFlow class
- `manifest.json` with proper metadata
- `strings.json` for UI labels

---

## Update

```bash
/plugin update ha-integration@aurora-smart-home
```

### Enable Auto-Update

1. Run `/plugin` to open the plugin manager
2. Go to **Marketplaces** tab
3. Select `aurora-smart-home`
4. Choose **Enable auto-update**

---

## Uninstall

Use the interactive UI for complete removal:

1. Run `/plugin`
2. Go to **Installed** tab
3. Select `ha-integration`
4. Choose **Uninstall**

**Note:** The CLI command `/plugin uninstall` only disables plugins.

---

## Change Scope

To move from one scope to another (e.g., user → local):

1. Uninstall via interactive UI (see above)
2. Reinstall with new scope:
   ```bash
   /plugin install ha-integration@aurora-smart-home --scope local
   ```

---

## Development Environment Setup

For testing generated integrations, set up a Home Assistant development environment:

### Option 1: Home Assistant Container (Quick Start)

```bash
# Create custom_components directory
mkdir -p config/custom_components

# Run Home Assistant
docker run -d \
  --name homeassistant \
  -v $(pwd)/config:/config \
  -p 8123:8123 \
  homeassistant/home-assistant:latest
```

### Option 2: Core Development (Full)

```bash
# Clone Home Assistant Core
git clone https://github.com/home-assistant/core.git
cd core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Create custom_components symlink
mkdir -p config/custom_components
```

See [Home Assistant Development Docs](https://developers.home-assistant.io/docs/development_environment) for full setup.

---

## Troubleshooting

### Skill Not Triggering

1. Verify installation: `/plugin`
2. Restart Claude Code
3. Try rephrasing with keywords: "custom integration", "Python", "config_flow", "HACS"

### Generated Code Has Errors

1. Check Home Assistant Core version compatibility
2. Verify import statements match your HA version
3. Ask: "Fix this integration error: [paste error]"

### Type Errors

Common issues:
- `datetime.now()` → Use `dt_util.now()` instead
- `datetime` in attributes → Convert to ISO string
- `requests` library → Use `aiohttp` or `async_get_clientsession`

---

## Getting Help

- **Usage examples:** See [USAGE-GUIDE.md](USAGE-GUIDE.md)
- **129 prompts:** See [PROMPT-IDEAS.md](PROMPT-IDEAS.md)
- **Cheatsheet:** See [CHEATSHEET.md](CHEATSHEET.md)
- **Issues:** [GitHub Issues](https://github.com/tonylofgren/aurora-smart-home/issues)
