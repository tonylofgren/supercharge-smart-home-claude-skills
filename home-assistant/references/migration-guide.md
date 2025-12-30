# Home Assistant Migration Guide

## Table of Contents
- [Version Upgrades](#version-upgrades)
- [Breaking Changes by Version](#breaking-changes-by-version)
- [Deprecated Syntax Migration](#deprecated-syntax-migration)
- [YAML to UI Migration](#yaml-to-ui-migration)
- [Platform Migrations](#platform-migrations)
- [Database Migrations](#database-migrations)
- [Add-on Migrations](#add-on-migrations)
- [Pre-Upgrade Checklist](#pre-upgrade-checklist)
- [Post-Upgrade Verification](#post-upgrade-verification)
- [Rollback Procedures](#rollback-procedures)
- [Common Migration Issues](#common-migration-issues)

---

## Version Upgrades

### General Upgrade Process

```markdown
## Before Upgrading
1. Create full backup (Settings > System > Backups)
2. Read release notes for target version
3. Check breaking changes
4. Review deprecated warnings in logs
5. Test add-ons compatibility

## During Upgrade
1. Stop all automations (optional but recommended)
2. Install update via Settings > System > Updates
3. Wait for restart to complete
4. Check logs for errors

## After Upgrade
1. Verify all integrations load
2. Check automations run correctly
3. Test critical functionality
4. Review logs for deprecation warnings
```

### Skip Version Upgrades

```yaml
# IMPORTANT: Home Assistant supports skipping versions, BUT:
# - Read ALL release notes between your version and target
# - Check ALL breaking changes in between
# - Some changes compound - migration paths may differ

# Example: Upgrading from 2023.12 to 2024.12
# Read: 2024.1, 2024.2, ..., 2024.12 release notes
```

### Upgrade Paths

| From Version | To Version | Special Considerations |
|--------------|------------|----------------------|
| 2023.x | 2024.x | Template syntax changes, entity ID changes |
| 2024.1-6 | 2024.7+ | Sections dashboard, new card types |
| 2024.x | 2025.x | Check Matter/Thread changes |

---

## Breaking Changes by Version

### Home Assistant 2024.x Notable Changes

#### 2024.1
```yaml
# Weather entity forecast attribute deprecated
# OLD:
{{ state_attr('weather.home', 'forecast')[0].temperature }}

# NEW: Use weather.get_forecasts service
action:
  - service: weather.get_forecasts
    target:
      entity_id: weather.home
    data:
      type: daily
    response_variable: forecast
  - service: notify.mobile
    data:
      message: "Tomorrow: {{ forecast['weather.home'].forecast[0].temperature }}°C"
```

#### 2024.2
```yaml
# Template sensors: 'unit_of_measurement' now validates against device_class
# If device_class is set, unit must be compatible

# OLD (may warn):
template:
  - sensor:
      - name: "Power"
        device_class: power
        unit_of_measurement: "kW"  # Should be W for power

# NEW:
template:
  - sensor:
      - name: "Power"
        device_class: power
        unit_of_measurement: "W"
```

#### 2024.4
```yaml
# Script 'sequence' key is now optional for single actions
# OLD:
script:
  my_script:
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.living_room

# NEW (both work):
script:
  my_script:
    - service: light.turn_on
      target:
        entity_id: light.living_room
```

#### 2024.6
```yaml
# Sections dashboard introduced (experimental)
# New view type 'sections' available

views:
  - type: sections
    title: Home
    sections:
      - title: Lights
        cards:
          - type: tile
            entity: light.living_room
```

#### 2024.8
```yaml
# Template 'is_state_attr' behavior change for unavailable entities
# Now returns False for unavailable entities

# OLD behavior: might error or return unexpected
# NEW behavior: consistently returns False

# Add explicit availability check if needed:
{% if states('sensor.test') not in ['unavailable', 'unknown'] %}
  {{ is_state_attr('sensor.test', 'attr', 'value') }}
{% endif %}
```

#### 2024.10
```yaml
# Python 3.12 minimum requirement
# Some custom components may need updates

# MQTT discovery: device.name required when using device object
# OLD (deprecated):
mqtt:
  sensor:
    - state_topic: "sensor/temp"
      device:
        identifiers: ["my_device"]

# NEW:
mqtt:
  sensor:
    - state_topic: "sensor/temp"
      device:
        identifiers: ["my_device"]
        name: "My Device"  # Required
```

#### 2024.12
```yaml
# Service data validation stricter
# Extra keys in service data now generate warnings

# Check your automations for typos in service data:
action:
  - service: light.turn_on
    data:
      brightness_pct: 100
      typo_key: "value"  # Will warn in 2024.12+
```

---

## Deprecated Syntax Migration

### Automation Syntax

#### State Trigger 'to' and 'from'

```yaml
# OLD (deprecated):
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: 'on'  # Quotes around boolean-like strings

# NEW (preferred):
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: "on"  # Use double quotes consistently
    # OR for actual boolean (some integrations):
    to: true
```

#### Service Call Syntax

```yaml
# OLD (deprecated in newer versions):
action:
  - service: light.turn_on
    entity_id: light.living_room  # Direct entity_id

# NEW (current):
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 100
```

#### Condition Shorthand

```yaml
# OLD:
condition:
  condition: state
  entity_id: binary_sensor.motion
  state: 'on'

# NEW (both work, list format preferred):
condition:
  - condition: state
    entity_id: binary_sensor.motion
    state: "on"
```

### Template Syntax

#### States Object

```yaml
# OLD (deprecated):
{{ states.sensor.temperature.state }}

# NEW (recommended):
{{ states('sensor.temperature') }}

# OLD attribute access (deprecated):
{{ states.sensor.temperature.attributes.unit_of_measurement }}

# NEW:
{{ state_attr('sensor.temperature', 'unit_of_measurement') }}
```

#### Timestamp Conversions

```yaml
# OLD:
{{ as_timestamp(states.sensor.time.last_changed) }}

# NEW:
{{ as_timestamp(states.sensor.time.last_changed) }}  # Still works
# OR more explicit:
{{ states.sensor.time.last_changed | as_timestamp }}
```

#### Float/Int Defaults

```yaml
# OLD (could error on unavailable):
{{ states('sensor.temp') | float }}

# NEW (always provide default):
{{ states('sensor.temp') | float(0) }}
{{ states('sensor.count') | int(0) }}
```

### Configuration Syntax

#### Platform vs Integration

```yaml
# OLD (legacy format):
sensor:
  - platform: template
    sensors:
      my_sensor:
        value_template: "{{ states('sensor.temp') }}"

# NEW (modern format):
template:
  - sensor:
      - name: "My Sensor"
        state: "{{ states('sensor.temp') }}"
```

#### Binary Sensor Template

```yaml
# OLD:
binary_sensor:
  - platform: template
    sensors:
      motion_detected:
        value_template: "{{ is_state('binary_sensor.pir', 'on') }}"

# NEW:
template:
  - binary_sensor:
      - name: "Motion Detected"
        state: "{{ is_state('binary_sensor.pir', 'on') }}"
```

---

## YAML to UI Migration

### Why Migrate?

| YAML | UI |
|------|-----|
| Version controlled | Easier editing |
| Include support | Visual debugging |
| Complex templating | Trace view |
| Bulk editing | Mobile friendly |

### Migration Process

```markdown
## Step 1: Export from YAML
1. Open Developer Tools > Services
2. Run: automation.reload or script.reload
3. Note current automation IDs

## Step 2: Recreate in UI
1. Settings > Automations & Scenes
2. Create New Automation
3. Copy trigger/condition/action logic

## Step 3: Verify
1. Test automation manually
2. Check trace for correct execution
3. Disable YAML version
4. Monitor for issues

## Step 4: Remove YAML
1. Comment out YAML automation
2. Restart Home Assistant
3. Verify UI automation still works
4. Delete YAML version
```

### Converting Complex Templates

```yaml
# YAML version with complex template:
automation:
  - id: complex_template_example
    trigger:
      - platform: template
        value_template: >
          {% set temp = states('sensor.outside_temp') | float(0) %}
          {% set humidity = states('sensor.humidity') | float(0) %}
          {{ temp > 25 and humidity > 70 }}
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.living_room
        data:
          hvac_mode: cool

# In UI:
# 1. Create trigger type "Template"
# 2. Paste the value_template content
# 3. UI will validate and show errors
```

### Keeping Hybrid Setup

```yaml
# configuration.yaml
# Keep complex automations in YAML
automation manual: !include automations_manual.yaml

# Let UI manage its automations
automation ui: !include automations.yaml
```

---

## Platform Migrations

### Hue to Native

```yaml
# OLD: Using hue platform directly
light:
  - platform: hue
    host: 192.168.1.100

# NEW: Use integration via UI
# 1. Remove YAML config
# 2. Settings > Devices & Services > Add Integration
# 3. Search "Philips Hue"
# 4. Follow discovery/manual setup
```

### MQTT Sensor to Modern Format

```yaml
# OLD:
sensor:
  - platform: mqtt
    name: "Temperature"
    state_topic: "home/sensor/temp"
    unit_of_measurement: "°C"

# NEW (mqtt integration format):
mqtt:
  sensor:
    - name: "Temperature"
      state_topic: "home/sensor/temp"
      unit_of_measurement: "°C"
```

### Z-Wave to Z-Wave JS

```markdown
## Migration Steps
1. Backup current Z-Wave network
2. Remove old Z-Wave integration
3. Install Z-Wave JS add-on
4. Connect to existing USB stick
5. Devices should auto-migrate
6. Update automations for new entity IDs

## Entity ID Changes
OLD: zwave.living_room_dimmer
NEW: light.living_room_dimmer

OLD: sensor.living_room_dimmer_power
NEW: sensor.living_room_dimmer_electric_consumption_w
```

### Zigbee (deconz/ZHA) to Zigbee2MQTT

```markdown
## Before Migration
1. Document all devices and entity IDs
2. Note custom device names
3. Export automations using these devices

## Migration Steps
1. Remove deconz/ZHA integration
2. Flash Zigbee2MQTT firmware to coordinator
3. Set up Zigbee2MQTT add-on
4. Re-pair devices (cannot migrate network)
5. Update entity IDs in automations

## Entity ID Mapping
Create a mapping file:
```

```yaml
# entity_mapping.yaml
old_entities:
  - old: light.living_room_hue
    new: light.living_room_0x00158d0001234567
  - old: sensor.motion_sensor_battery
    new: sensor.motion_sensor_battery_2
```

---

## Database Migrations

### SQLite to MariaDB

```yaml
# 1. Install MariaDB add-on or external server

# 2. Update configuration.yaml
recorder:
  db_url: mysql://user:password@core-mariadb/homeassistant?charset=utf8mb4

# 3. Restart Home Assistant
# Note: History will start fresh - old SQLite data not migrated
```

### Purge Old Data

```yaml
# configuration.yaml
recorder:
  purge_keep_days: 10
  commit_interval: 1
  exclude:
    domains:
      - automation
      - updater
    entity_globs:
      - sensor.weather_*
    entities:
      - sun.sun
```

### Manual Database Cleanup

```bash
# SSH to Home Assistant
# Stop Home Assistant
ha core stop

# Backup database
cp /config/home-assistant_v2.db /config/home-assistant_v2.db.backup

# Start Home Assistant
ha core start

# Use recorder.purge service for controlled cleanup
```

---

## Add-on Migrations

### Node-RED Backup/Restore

```markdown
## Export Flows
1. Node-RED UI > Menu > Export > All Flows
2. Save JSON file

## After Migration
1. Install Node-RED add-on
2. Import flows from JSON
3. Update Home Assistant server connection
4. Deploy and test
```

### ESPHome Migration

```markdown
## Device Configs Backup
1. Copy /config/esphome/*.yaml files

## After Fresh Install
1. Install ESPHome add-on
2. Copy YAML files back
3. Devices will auto-reconnect
4. May need to re-adopt in dashboard
```

---

## Pre-Upgrade Checklist

```markdown
## 24 Hours Before Upgrade

### Backup
- [ ] Create full backup
- [ ] Download backup to external location
- [ ] Test backup restoration on test system (optional)

### Research
- [ ] Read all release notes since current version
- [ ] Check breaking changes list
- [ ] Search forums for known issues
- [ ] Check custom component compatibility

### Prepare
- [ ] Document current custom components versions
- [ ] Note any workarounds currently in use
- [ ] Disable non-critical automations
- [ ] Plan upgrade during low-activity time

### Dependencies
- [ ] Check add-on compatibility
- [ ] Verify custom cards work with new frontend
- [ ] Check HACS components for updates
```

```yaml
# Create pre-upgrade snapshot script
script:
  pre_upgrade_check:
    alias: "Pre-Upgrade System Check"
    sequence:
      - service: system_log.write
        data:
          message: "Starting pre-upgrade check"
          level: info
      - service: backup.create
        data:
          name: "pre_upgrade_{{ now().strftime('%Y%m%d_%H%M') }}"
      - service: notify.admin
        data:
          title: "Upgrade Ready"
          message: "Backup created. Review logs before proceeding."
```

---

## Post-Upgrade Verification

```markdown
## Immediate Checks (First 15 minutes)

### Core Systems
- [ ] Home Assistant starts without errors
- [ ] Frontend loads correctly
- [ ] All integrations initialize
- [ ] Recorder database accessible

### Critical Functions
- [ ] Lights respond to controls
- [ ] Climate systems functional
- [ ] Security sensors reporting
- [ ] Notifications working

### Automations
- [ ] Test one automation from each category
- [ ] Check automation traces for errors
- [ ] Verify time-based triggers
- [ ] Test device triggers

## Extended Checks (First 24 hours)

### Performance
- [ ] Memory usage normal
- [ ] CPU usage normal
- [ ] Database size growth normal
- [ ] Frontend responsiveness

### Functionality
- [ ] All daily automations run
- [ ] Sensor history recording
- [ ] Remote access working
- [ ] Mobile app connected
```

```yaml
# Post-upgrade verification automation
automation:
  - id: post_upgrade_verification
    alias: "Post-Upgrade System Verification"
    trigger:
      - platform: homeassistant
        event: start
    condition:
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - as_timestamp(states('sensor.uptime'))) < 600 }}
    action:
      - delay: "00:02:00"  # Wait for systems to stabilize
      - service: notify.admin
        data:
          title: "Home Assistant Restarted"
          message: >
            Version: {{ state_attr('update.home_assistant_core_update', 'installed_version') }}
            Uptime: {{ states('sensor.uptime') }}
            Integrations: {{ states.integration | list | length }}
            Automations: {{ states.automation | list | length }}
```

---

## Rollback Procedures

### Quick Rollback (Within Minutes)

```markdown
## If Upgrade Fails Immediately

1. DO NOT make any changes
2. Settings > System > Backups
3. Select pre-upgrade backup
4. Choose "Restore"
5. Wait for system to restore and restart

## If UI Not Accessible

SSH/Terminal method:
```

```bash
# SSH to Home Assistant
ha backup list
ha backup restore <backup_slug> --homeassistant
```

### Downgrade Home Assistant

```markdown
## Manual Version Downgrade

WARNING: Not officially supported, may cause issues

1. SSH to Home Assistant
2. ha core update --version 2024.X.X
3. Wait for downgrade to complete
4. Check for database compatibility issues
```

### Partial Rollback

```yaml
# If only specific integration fails:

# 1. Check integration logs
# Developer Tools > Logs > Filter by integration

# 2. Disable integration temporarily
# Settings > Devices & Services > Integration > Disable

# 3. Check for updates
# HACS > Updates (for custom integrations)

# 4. Report issue if needed
# GitHub issue with logs and version info
```

---

## Common Migration Issues

### Entity ID Changes

```yaml
# Problem: Automations fail because entity IDs changed
# Solution: Use entity registry to find new IDs

# Developer Tools > States
# Filter by device name to find new entity ID

# Update automations:
# Find/replace old entity ID with new
```

### Template Errors After Upgrade

```yaml
# Problem: Templates that worked before now fail

# Common causes:
# 1. Stricter type checking
# 2. Changed function behavior
# 3. New required parameters

# Debug in Developer Tools > Template:
{% set test = states('sensor.test') %}
Type: {{ test | type_debug }}
Value: {{ test }}
Float: {{ test | float('unavailable') }}  # Default for conversion
```

### Database Corruption

```markdown
## Symptoms
- "Database is locked" errors
- History not updating
- Slow startup

## Solution
1. Stop Home Assistant
2. Rename database: mv home-assistant_v2.db home-assistant_v2.db.corrupt
3. Start Home Assistant (creates new DB)
4. History starts fresh

## Prevention
- Regular backups
- Use SSD instead of SD card
- Consider external database (MariaDB/PostgreSQL)
```

### Custom Component Incompatibility

```markdown
## Diagnosis
1. Check logs for custom component errors
2. Visit component GitHub for version compatibility
3. Check HACS for available updates

## Temporary Fix
1. Remove custom component from /config/custom_components/
2. Restart Home Assistant
3. Wait for component update
4. Reinstall when compatible version available
```

### Automation Migration Issues

```yaml
# Problem: YAML automations lost after upgrade

# Check if automation file is loaded:
# Developer Tools > YAML > Automations

# Verify configuration.yaml:
automation: !include automations.yaml
# OR
automation manual: !include_dir_merge_list automations/
automation ui: !include automations.yaml

# Check file permissions:
# SSH: ls -la /config/automations.yaml
```

---

## Migration Scripts and Tools

### Entity ID Update Script

```yaml
# Automation to help identify entity changes
automation:
  - id: log_unavailable_entities
    alias: "Log Unavailable Entities"
    trigger:
      - platform: time_pattern
        hours: "/1"
    action:
      - service: system_log.write
        data:
          message: >
            Unavailable entities:
            {% for state in states %}
              {% if state.state == 'unavailable' %}
                {{ state.entity_id }}
              {% endif %}
            {% endfor %}
          level: warning
```

### Configuration Validator

```bash
# Before upgrade, validate configuration
ha core check

# Check specific file
python -c "import yaml; yaml.safe_load(open('configuration.yaml'))"
```

### Backup Verification

```yaml
# Automation to verify backups exist
automation:
  - id: backup_verification
    alias: "Weekly Backup Verification"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: hassio.backup_full
        data:
          name: "weekly_{{ now().strftime('%Y%m%d') }}"
      - delay: "00:30:00"
      - service: notify.admin
        data:
          title: "Backup Complete"
          message: "Weekly backup created successfully"
```

---

## Resources

### Official Documentation
- [Home Assistant Release Notes](https://www.home-assistant.io/blog/categories/release-notes/)
- [Breaking Changes](https://www.home-assistant.io/blog/categories/breaking-changes/)
- [Integration Documentation](https://www.home-assistant.io/integrations/)

### Community Resources
- [Home Assistant Community Forums](https://community.home-assistant.io/)
- [Home Assistant Discord](https://discord.gg/home-assistant)
- [Reddit r/homeassistant](https://www.reddit.com/r/homeassistant/)

### Tools
- [HACS (Home Assistant Community Store)](https://hacs.xyz/)
- [Home Assistant CLI](https://www.home-assistant.io/common-tasks/os/#home-assistant-via-the-command-line)
