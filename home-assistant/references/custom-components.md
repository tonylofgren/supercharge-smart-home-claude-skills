# Home Assistant Custom Components Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [HACS Installation](#hacs-installation)
- [Managing Integrations](#managing-integrations)
- [Popular Integrations](#popular-integrations)
- [Popular Frontend Cards](#popular-frontend-cards)
- [Manual Installation](#manual-installation)
- [Creating Custom Components](#creating-custom-components)
- [Security Considerations](#security-considerations)
- [Maintenance](#maintenance)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Custom components extend Home Assistant beyond official integrations.

### Key Terms

| Term | Description |
|------|-------------|
| **Custom Component** | Third-party integration |
| **HACS** | Home Assistant Community Store |
| **Integration** | Backend functionality |
| **Frontend/Lovelace** | UI cards and themes |
| **Repository** | GitHub source for component |

### Component Types

| Type | Location | Purpose |
|------|----------|---------|
| **Integrations** | `custom_components/` | New entities, services |
| **Lovelace Cards** | Resources | Dashboard cards |
| **Themes** | `themes/` | Visual styling |
| **Python Scripts** | `python_scripts/` | Custom scripts |
| **AppDaemon Apps** | `appdaemon/apps/` | Python automations |

### File Structure

```
config/
├── custom_components/
│   └── integration_name/
│       ├── __init__.py
│       ├── manifest.json
│       ├── sensor.py
│       └── config_flow.py
├── www/
│   └── community/
│       └── card-name/
│           └── card-name.js
└── themes/
    └── theme_name.yaml
```

---

## HACS Installation

### Requirements

- Home Assistant Core 2024.4.0+
- GitHub account (for rate limits)
- Network access to GitHub

### Installation Methods

**Method 1: Download Script**

```bash
# SSH into Home Assistant
wget -O - https://get.hacs.xyz | bash -
# Restart Home Assistant
```

**Method 2: Manual**

```bash
# Create custom_components directory
mkdir -p config/custom_components

# Download HACS
cd config/custom_components
wget https://github.com/hacs/integration/releases/latest/download/hacs.zip
unzip hacs.zip -d hacs
rm hacs.zip

# Restart Home Assistant
```

### Initial Configuration

1. Add integration via UI:
   - Settings > Devices & Services > Add Integration
   - Search "HACS"

2. Authorize GitHub:
   - Click provided link
   - Enter authorization code
   - Grant repository access

3. Configure options:
   ```yaml
   # Optional configuration
   # Most settings are in the UI
   ```

### HACS Categories

| Category | Content |
|----------|---------|
| **Integrations** | Custom components |
| **Frontend** | Lovelace cards |
| **Automation** | AppDaemon/NetDaemon |
| **Python Scripts** | python_scripts |
| **Themes** | Frontend themes |

---

## Managing Integrations

### Installing via HACS

1. Navigate to HACS in sidebar
2. Select category (Integrations/Frontend)
3. Click "+ Explore & Download Repositories"
4. Search for component
5. Click Download
6. Restart Home Assistant (integrations only)
7. Add integration via Settings > Devices & Services

### Updating Components

```yaml
# HACS checks for updates automatically
# Manual check: HACS > Updates

# Update all at once
# HACS > Menu (three dots) > Update all
```

### Removing Components

1. Remove integration configuration first:
   - Settings > Devices & Services
   - Delete integration entry

2. Remove from HACS:
   - HACS > Find component
   - Click > Delete

3. Restart Home Assistant

### Version Pinning

```yaml
# In HACS, you can select specific versions
# HACS > Component > Menu > Redownload
# Select version from dropdown
```

---

## Popular Integrations

### Browser Mod

Control browsers as devices.

```yaml
# After HACS installation, add integration
# Settings > Devices & Services > Add > Browser Mod

# Service examples
service: browser_mod.popup
data:
  browser_id: main_browser
  title: Settings
  content:
    type: entities
    entities:
      - light.living_room

# Navigate browser
service: browser_mod.navigate
data:
  browser_id: main_browser
  path: /lovelace/home

# JavaScript execution
service: browser_mod.javascript
data:
  browser_id: main_browser
  code: alert('Hello!')
```

### Alexa Media Player

Full Alexa integration.

```yaml
# After HACS install and HA restart:
# Settings > Devices & Services > Add > Alexa Media Player

# Login with Amazon credentials (2FA supported)

# Example services
service: notify.alexa_media
data:
  message: "The laundry is done"
  target:
    - media_player.echo_kitchen
  data:
    type: announce

# Play music
service: media_player.play_media
target:
  entity_id: media_player.echo_living_room
data:
  media_content_type: SPOTIFY
  media_content_id: "spotify:playlist:abc123"
```

### Local Tuya

Local control of Tuya devices.

```yaml
# After installation, you need:
# 1. Tuya IoT Platform account
# 2. Device IDs and local keys

# Add via integrations UI
# Supports: switches, lights, covers, fans, climate
```

### Frigate

NVR with AI object detection.

```yaml
# Requires Frigate server running separately
# HACS installs the HA integration

# Configuration in frigate.yml (external)
# Integration provides:
# - camera entities
# - binary_sensor for detection
# - event entities
```

### Adaptive Lighting

Automatic circadian lighting.

```yaml
# After installation, configure via UI
# Creates switch entities for each light

# Example: Manual override
automation:
  - alias: "Disable adaptive lighting on manual change"
    trigger:
      - platform: event
        event_type: call_service
        event_data:
          domain: light
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.service_data.entity_id is defined }}"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.adaptive_lighting_living_room
```

### Waste Collection Schedule

Garbage/recycling reminders.

```yaml
# Configure via UI after installation
# Creates sensors for next collection dates

# Example automation
automation:
  - alias: "Trash Reminder"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: state
        entity_id: sensor.trash_collection
        state: "1"  # Tomorrow
    action:
      - service: notify.mobile_app
        data:
          message: "Put out the trash tonight!"
```

### Presence Simulation

Simulate occupancy when away.

```yaml
# Learns patterns from history
# Replays lighting patterns when away

# Enable via UI switch
# switch.presence_simulation
```

### Scheduler

Visual automation scheduler.

```yaml
# Creates schedule entities via UI
# More visual than native HA schedules

# Supports:
# - Time-based actions
# - Weekday selection
# - Entity targeting
```

---

## Popular Frontend Cards

### Button Card

Highly customizable buttons.

```yaml
# Add resource via HACS (auto) or manually
resources:
  - url: /hacsfiles/button-card/button-card.js
    type: module
```

```yaml
type: custom:button-card
entity: light.living_room
name: Living Room
icon: mdi:lightbulb
show_state: true
styles:
  card:
    - background: >
        [[[ return entity.state === 'on' ?
            'linear-gradient(135deg, #ffcc00, #ff9500)' :
            'var(--card-background-color)' ]]]
  icon:
    - color: >
        [[[ return entity.state === 'on' ? 'white' : 'var(--primary-text-color)' ]]]
state:
  - value: "on"
    styles:
      card:
        - box-shadow: 0 0 20px rgba(255, 200, 0, 0.5)
```

### Mini Graph Card

Compact graphs.

```yaml
type: custom:mini-graph-card
entities:
  - entity: sensor.temperature
    name: Temperature
    color: "#e74c3c"
  - entity: sensor.humidity
    name: Humidity
    color: "#3498db"
    y_axis: secondary
hours_to_show: 24
points_per_hour: 4
line_width: 2
animate: true
show:
  labels: true
  points: hover
  legend: true
  average: true
  extrema: true
```

### Mushroom Cards

Modern minimalist design.

```yaml
# Mushroom Entity Card
type: custom:mushroom-entity-card
entity: sensor.temperature
primary_info: state
secondary_info: name
icon_color: red

# Mushroom Chips Card
type: custom:mushroom-chips-card
chips:
  - type: entity
    entity: person.john
  - type: entity
    entity: alarm_control_panel.home
  - type: weather
    entity: weather.home
    show_temperature: true
    show_conditions: true

# Mushroom Light Card
type: custom:mushroom-light-card
entity: light.living_room
show_brightness_control: true
show_color_temp_control: true
show_color_control: true
collapsible_controls: true
use_light_color: true
```

### Card Mod

CSS styling for any card.

```yaml
type: entities
entities:
  - light.living_room
card_mod:
  style: |
    ha-card {
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
    }
    .card-header {
      color: white;
      padding: 16px;
    }
```

### ApexCharts Card

Advanced charting.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Energy Usage
  show_states: true
graph_span: 7d
series:
  - entity: sensor.daily_energy
    type: column
    name: Daily
    group_by:
      func: sum
      duration: 1d
    color: "#3498db"
  - entity: sensor.energy_cost
    type: line
    name: Cost
    group_by:
      func: sum
      duration: 1d
    color: "#e74c3c"
    y_axis_id: cost
yaxis:
  - id: energy
    min: 0
  - id: cost
    opposite: true
    min: 0
```

### Swipe Card

Swipeable containers.

```yaml
type: custom:swipe-card
cards:
  - type: picture-entity
    entity: camera.front
  - type: picture-entity
    entity: camera.back
  - type: picture-entity
    entity: camera.side
parameters:
  slidesPerView: 1
  spaceBetween: 8
  pagination:
    type: bullets
```

### Auto Entities

Dynamic entity lists.

```yaml
type: custom:auto-entities
card:
  type: entities
  title: Active Lights
filter:
  include:
    - domain: light
      state: "on"
  exclude:
    - entity_id: "*group*"
sort:
  method: name
show_empty: false
```

### Layout Card

Custom layouts.

```yaml
type: custom:layout-card
layout_type: custom:grid-layout
layout:
  grid-template-columns: 1fr 1fr 1fr
  grid-template-rows: auto auto
  grid-template-areas: |
    "header header header"
    "left center right"
cards:
  - type: markdown
    view_layout:
      grid-area: header
    content: "# Dashboard"
```

### Stack In Card

Combine cards seamlessly.

```yaml
type: custom:stack-in-card
mode: vertical
cards:
  - type: custom:mushroom-entity-card
    entity: sensor.temperature
  - type: custom:mini-graph-card
    entities:
      - sensor.temperature
    show:
      name: false
      icon: false
      state: false
    height: 100
```

---

## Manual Installation

### Custom Integration

```bash
# Download from GitHub releases
cd config/custom_components
mkdir integration_name
cd integration_name

# Download files (example)
wget https://github.com/user/repo/releases/latest/download/integration_name.zip
unzip integration_name.zip
rm integration_name.zip

# Verify structure
ls -la
# Should see: __init__.py, manifest.json, etc.

# Restart Home Assistant
```

### Lovelace Card

```bash
# Create www directory if needed
mkdir -p config/www

# Download card
cd config/www
wget https://github.com/user/card-repo/releases/latest/download/card-name.js

# Add resource (UI or YAML)
```

```yaml
# configuration.yaml (YAML mode)
lovelace:
  resources:
    - url: /local/card-name.js
      type: module
```

### Version Management

```bash
# Keep track of installed versions
# Create versions.txt
echo "button-card: 4.0.0" >> config/custom_components/versions.txt
echo "mini-graph-card: 0.12.0" >> config/www/versions.txt
```

---

## Creating Custom Components

### Basic Structure

```python
# custom_components/my_integration/__init__.py
"""My Custom Integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "my_integration"
PLATFORMS = ["sensor", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
```

### Manifest File

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "codeowners": ["@your_github"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/user/repo",
  "integration_type": "device",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/user/repo/issues",
  "requirements": ["some_library==1.0.0"],
  "version": "1.0.0"
}
```

### Simple Sensor

```python
# custom_components/my_integration/sensor.py
"""Sensor platform for My Integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    async_add_entities([MySensor(entry)])

class MySensor(SensorEntity):
    """My custom sensor."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        self._attr_name = "My Sensor"
        self._attr_unique_id = f"{entry.entry_id}_sensor"
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Update sensor."""
        # Fetch data and update
        self._attr_native_value = 42
```

### Config Flow

```python
# custom_components/my_integration/config_flow.py
"""Config flow for My Integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .const import DOMAIN

class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow handler."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        errors = {}

        if user_input is not None:
            # Validate input
            return self.async_create_entry(
                title="My Integration",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
            }),
            errors=errors
        )
```

---

## Security Considerations

### Evaluation Checklist

| Check | Description |
|-------|-------------|
| **Source** | Verified GitHub repository |
| **Maintainer** | Active, responsive developer |
| **Code Review** | Check for suspicious code |
| **Permissions** | What access does it need? |
| **Dependencies** | Are libraries trustworthy? |
| **Issues** | Check for security reports |

### Code Review Tips

When reviewing custom component code, watch for these security concerns:

**Red flags to look for:**
- Network requests to unknown/suspicious servers
- Hardcoded API keys or credentials
- Dynamic code evaluation from user input
- File system access outside the config directory
- Shell command execution with user-provided input
- Obfuscated or minimized Python code

### Recommended Sources

| Source | Trust Level | Reason |
|--------|-------------|--------|
| **HACS Default** | High | Reviewed for inclusion |
| **Known Developers** | High | Community reputation |
| **New Repositories** | Medium | Review code first |
| **Forks** | Low | Verify changes |

### Sandboxing

```yaml
# Home Assistant runs with user permissions
# Additional protection via:

# 1. Dedicated user account
# 2. Docker with limited privileges
# 3. Network segmentation
# 4. Regular backups before updates
```

---

## Maintenance

### Update Strategy

```yaml
# Recommended approach:
# 1. Wait 24-48h after releases (let others find bugs)
# 2. Read changelogs
# 3. Backup before updating
# 4. Update one component at a time
# 5. Test after each update
```

### Backup Considerations

```bash
# Include in backups:
config/
├── custom_components/     # All custom integrations
├── www/                   # Frontend resources
├── themes/                # Custom themes
└── configuration.yaml     # Resource references

# HACS stores state in:
config/.storage/hacs*
```

### Handling Breaking Changes

```yaml
# Check release notes for:
# - Configuration changes
# - Removed features
# - New requirements

# Common issues after updates:
# 1. Entity names changed
# 2. Service syntax changed
# 3. New configuration required
```

### Orphan Detection

```yaml
# Find unused custom components
# Developer Tools > Services > homeassistant.check_config

# Manual check:
# 1. List custom_components
# 2. Compare with active integrations in UI
# 3. Remove unused directories
```

---

## Best Practices

### Selection Criteria

| Factor | Weight | Consideration |
|--------|--------|---------------|
| **Active Development** | High | Recent commits, responses |
| **Documentation** | High | Setup guides, examples |
| **Community** | Medium | Issues, discussions |
| **Compatibility** | High | HA version support |
| **Performance** | Medium | Resource usage |

### Organization

```
custom_components/
├── integration_a/          # One folder per integration
├── integration_b/
└── _disabled/              # For testing removals
    └── old_integration/

www/
├── community/              # HACS managed
│   └── card-name/
└── custom/                 # Manually managed
    └── my-card.js
```

### Documentation

```yaml
# Keep a record of:
# 1. Why each component was installed
# 2. Configuration used
# 3. Known issues/workarounds
# 4. Update history

# Example: custom_components/README.md
# Custom Components

## browser_mod
- Purpose: Browser control, popups
- Installed: 2024-01-15
- Version: 2.3.0
- Config: UI only
- Notes: Required for tablet dashboard

## alexa_media_player
- Purpose: Alexa announcements
- Installed: 2024-01-10
- Version: 4.5.0
- Config: credentials in UI
- Notes: Re-auth needed monthly
```

### Testing Updates

```yaml
# Before updating:
# 1. Check current working state
# 2. Note automation dependencies
# 3. Full backup

# After updating:
# 1. Check HA logs for errors
# 2. Test affected automations
# 3. Verify dashboard cards
# 4. Monitor for 24h
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Component not loading | Missing dependency | Check logs, install requirements |
| Card not rendering | Resource not loaded | Verify resource URL |
| Entity unavailable | Integration error | Check logs, re-add integration |
| HACS not updating | GitHub rate limit | Wait or add token |

### Log Analysis

```yaml
# Enable debug logging
logger:
  default: info
  logs:
    custom_components.integration_name: debug
    hacs: debug
```

```bash
# Check logs
tail -f config/home-assistant.log | grep custom_components
tail -f config/home-assistant.log | grep hacs
```

### Integration Not Loading

```bash
# 1. Check manifest.json exists
cat config/custom_components/integration_name/manifest.json

# 2. Verify Python syntax
python3 -m py_compile config/custom_components/integration_name/__init__.py

# 3. Check requirements
# Look in manifest.json for requirements
# Verify they're installed

# 4. Check HA logs
grep "integration_name" config/home-assistant.log
```

### Card Not Displaying

```yaml
# 1. Check resource URL
# Settings > Dashboards > Resources

# 2. Verify file exists
# /local/ maps to config/www/

# 3. Clear browser cache
# Ctrl+Shift+R / Cmd+Shift+R

# 4. Check browser console
# F12 > Console > Look for errors
```

### HACS Issues

```yaml
# Rate limiting
# Solution: Add GitHub Personal Access Token
# HACS > Menu > Custom Repositories > Token

# Repository not found
# 1. Check repository URL
# 2. Ensure it's public
# 3. Verify HACS category matches

# Update not showing
# HACS > Menu > Reload window
# Or: Clear HACS cache
```

### Recovery Steps

```bash
# If HA won't start after custom component:
# 1. Access via SSH or file manager

# 2. Rename problematic component
mv config/custom_components/broken_integration config/custom_components/broken_integration.disabled

# 3. Start HA

# 4. Check logs for root cause

# 5. Fix or remove permanently
```

---

## Resource Checklist

```markdown
## Custom Component Checklist

### Before Installing
- [ ] Check HACS default repository first
- [ ] Review GitHub repository
- [ ] Check recent activity
- [ ] Read documentation
- [ ] Check compatibility with HA version
- [ ] Review open issues

### After Installing
- [ ] Add integration via UI
- [ ] Test basic functionality
- [ ] Document configuration
- [ ] Set up dependent automations
- [ ] Monitor logs for errors

### Maintenance
- [ ] Enable update notifications
- [ ] Review changelogs before updating
- [ ] Backup before major updates
- [ ] Test after updates
- [ ] Clean up unused components
```

