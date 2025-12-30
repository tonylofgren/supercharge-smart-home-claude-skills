# Home Assistant Troubleshooting Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Common Startup Issues](#common-startup-issues)
- [Configuration Errors](#configuration-errors)
- [Entity Issues](#entity-issues)
- [Automation Debugging](#automation-debugging)
- [Integration Problems](#integration-problems)
- [Performance Issues](#performance-issues)
- [Network Problems](#network-problems)
- [Database Issues](#database-issues)
- [Log Analysis](#log-analysis)
- [Recovery Procedures](#recovery-procedures)
- [Diagnostic Tools](#diagnostic-tools)
- [Best Practices](#best-practices)

---

## Core Concepts

Effective troubleshooting requires systematic diagnosis and understanding of Home Assistant's architecture.

### Key Locations

| Location | Purpose |
|----------|---------|
| `home-assistant.log` | Main log file |
| `.storage/` | State and config storage |
| `home-assistant_v2.db` | History database |
| `.homeassistant/` | Alternative config path |

### Error Severity

| Level | Description |
|-------|-------------|
| **DEBUG** | Detailed diagnostic info |
| **INFO** | General operational info |
| **WARNING** | Potential issues |
| **ERROR** | Failed operations |
| **CRITICAL** | System failures |

### Troubleshooting Flow

```
1. Identify symptoms
2. Check logs
3. Isolate component
4. Test fixes
5. Verify resolution
6. Document solution
```

---

## Common Startup Issues

### Home Assistant Won't Start

**Check Configuration:**
```bash
# Validate configuration
ha core check

# Or via command line
hass --script check_config -c /config

# Docker
docker exec homeassistant hass --script check_config
```

**Common Causes:**

| Issue | Solution |
|-------|----------|
| YAML syntax error | Check indentation, quotes |
| Missing file | Verify !include paths |
| Invalid entity | Check entity_id format |
| Circular dependency | Review package includes |

### Safe Mode

```bash
# Start in safe mode (UI only)
# Settings > System > Restart > Safe Mode

# Via command line
hass --safe-mode

# Safe mode disables:
# - Integrations
# - Automations
# - Scripts
# - Custom components
```

### Recovery Mode

```yaml
# If web UI unavailable:

# 1. SSH access
ssh root@homeassistant.local

# 2. Check logs
tail -f /config/home-assistant.log

# 3. Rename problematic config
mv /config/configuration.yaml /config/configuration.yaml.bak

# 4. Create minimal config
echo "homeassistant:" > /config/configuration.yaml

# 5. Restart
ha core restart
```

---

## Configuration Errors

### YAML Syntax Errors

**Common Mistakes:**

```yaml
# Wrong: Tabs instead of spaces
automation:
	alias: Test  # TAB character

# Correct: Use spaces
automation:
  alias: Test  # 2 spaces

# Wrong: Missing quotes for special characters
name: Test: Automation  # Colon without quotes

# Correct: Quote strings with special characters
name: "Test: Automation"

# Wrong: Missing dash for list item
entities:
  light.living_room

# Correct: Include dash
entities:
  - light.living_room
```

### Validation Errors

```yaml
# Check configuration
# Developer Tools > YAML > Check Configuration

# Common validation errors:

# "Invalid config for [domain]"
# - Check required fields
# - Verify value types

# "Platform not found"
# - Check platform name spelling
# - Verify integration installed

# "Entity not found"
# - Check entity_id exists
# - Wait for integration to load
```

### Include File Errors

```yaml
# Verify include paths are relative to configuration.yaml

# configuration.yaml location: /config/configuration.yaml

# Correct include
automation: !include automations.yaml
# Looks for: /config/automations.yaml

# Subdirectory include
automation: !include automations/lights.yaml
# Looks for: /config/automations/lights.yaml

# Directory include
automation: !include_dir_list automations/
# Includes all YAML files in: /config/automations/

# Check file exists
# Developer Tools > YAML > Check Configuration
```

### Secret File Issues

```yaml
# secrets.yaml must be in config directory

# Check secrets file
cat /config/secrets.yaml

# Verify format
api_key: your_actual_key  # No quotes needed usually

# Usage in configuration.yaml
api_key: !secret api_key

# Common issues:
# - secrets.yaml not found
# - Key name mismatch
# - Extra whitespace in values
```

---

## Entity Issues

### Entity Unavailable

```yaml
# Causes:
# 1. Device offline
# 2. Integration not loaded
# 3. Configuration error

# Diagnosis:
# Developer Tools > States > Filter: unavailable

# Check integration
# Settings > Devices & Services > [Integration]

# Force update
service: homeassistant.update_entity
target:
  entity_id: sensor.problematic_sensor
```

### Entity Not Appearing

```yaml
# 1. Check integration loaded
# Settings > Devices & Services

# 2. Check entity disabled
# Settings > Devices & Services > [Device] > Entities
# Enable if disabled

# 3. Check entity registry
# .storage/core.entity_registry

# 4. Restart integration
# Settings > Devices & Services > [Integration] > Reload
```

### Entity State Issues

```yaml
# Wrong state value
# Check in Developer Tools > States

# Force state (for testing)
service: homeassistant.set_state
target:
  entity_id: sensor.test
data:
  state: "new_value"

# Note: set_state doesn't persist through restarts
# Use for diagnosis only
```

### Duplicate Entities

```yaml
# Causes:
# - Multiple integrations discovering same device
# - Re-added integration without removing old

# Fix:
# 1. Settings > Devices & Services
# 2. Find duplicate entries
# 3. Remove older/incorrect one
# 4. Restart if needed

# Clean entity registry
# Settings > Devices & Services > [Integration]
# Delete unused entities
```

---

## Automation Debugging

### Automation Traces

```yaml
# View traces
# Settings > Automations > [Automation] > Traces

# Trace shows:
# - Trigger details
# - Condition results
# - Action execution
# - Errors encountered

# Enable trace debugging
automation:
  - alias: "Test Automation"
    trace:
      stored_traces: 10  # Keep last 10 traces
```

### Manual Trigger

```yaml
# Test automation manually
service: automation.trigger
target:
  entity_id: automation.test_automation
data:
  skip_condition: false  # Set true to skip conditions
```

### Debug with Notifications

```yaml
automation:
  - alias: "Debug Automation"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
    action:
      # Debug: Log trigger data
      - service: system_log.write
        data:
          message: >
            Motion triggered:
            Entity: {{ trigger.entity_id }}
            From: {{ trigger.from_state.state }}
            To: {{ trigger.to_state.state }}
          level: info

      # Debug: Send notification
      - service: notify.mobile_app
        data:
          message: "Debug: Motion detected at {{ now() }}"

      # Actual actions...
      - service: light.turn_on
        target:
          entity_id: light.living_room
```

### Condition Testing

```yaml
# Test conditions in Developer Tools > Template

{% if is_state('sun.sun', 'below_horizon') %}
  Sun is down
{% else %}
  Sun is up
{% endif %}

# Test numeric conditions
{% set temp = states('sensor.temperature') | float %}
{% if temp > 25 %}
  Too hot
{% elif temp < 18 %}
  Too cold
{% else %}
  Comfortable
{% endif %}
```

### Script Debugging

```yaml
# Add trace to scripts
script:
  test_script:
    alias: "Test Script"
    trace:
      stored_traces: 5
    sequence:
      - service: system_log.write
        data:
          message: "Script started"
      # ... actions
      - service: system_log.write
        data:
          message: "Script completed"
```

### Trace API Deep Dive

The Trace API provides detailed execution history for automations and scripts.

#### Accessing Traces

```yaml
# Via UI
# Settings > Automations > [Automation] > Traces (clock icon)
# Shows last 5 runs by default

# Configure trace storage per automation
automation:
  - alias: "Important Automation"
    trace:
      stored_traces: 20  # Keep more traces for debugging

# Global trace configuration
trace:
  stored_traces: 10  # Default for all automations
```

#### Understanding Trace Output

A trace contains these key sections:

| Section | Information |
|---------|-------------|
| **Trigger** | What started the automation, entity states |
| **Condition** | Each condition evaluated, result (true/false) |
| **Action** | Each action executed, any errors |
| **Variables** | Context variables at each step |

#### Trace Timeline

```yaml
# Example trace timeline:
#
# [0.000s] Trigger: state of binary_sensor.motion changed to 'on'
# [0.002s] Condition: sun.sun is 'below_horizon' → TRUE
# [0.003s] Condition: numeric_state temperature < 20 → TRUE
# [0.005s] Action: service light.turn_on → SUCCESS
# [0.150s] Action: delay 2 seconds → STARTED
# [2.151s] Action: service notify.mobile → SUCCESS
# [2.200s] Automation completed
```

#### Interpreting Condition Results

```yaml
# Trace shows why conditions passed or failed:

# PASSED condition example:
# Condition: template
#   value_template: "{{ states('sensor.temp') | float > 20 }}"
#   result: true
#   rendered: "True"

# FAILED condition example:
# Condition: state
#   entity_id: person.john
#   state: home
#   result: false
#   actual_state: not_home  # ← Shows actual value
```

#### Debugging Failed Actions

```yaml
# Trace shows errors with context:

# Example error in trace:
# Action: service.call
#   domain: light
#   service: turn_on
#   target: {'entity_id': 'light.nonexistent'}
#   error: "Entity light.nonexistent not found"

# Fix: Verify entity_id exists
# Developer Tools > States > Search for entity
```

#### Variables in Traces

```yaml
# Traces show variable values at each step:

automation:
  - alias: "Debug Variables"
    variables:
      room: "living_room"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
    action:
      - variables:
          brightness: "{{ 100 if is_state('sun.sun', 'above_horizon') else 30 }}"
      - service: light.turn_on
        target:
          entity_id: "light.{{ room }}"
        data:
          brightness_pct: "{{ brightness }}"

# Trace shows:
# Variables after step 1:
#   room: "living_room"
#   brightness: "100"
#
# Service call resolved:
#   entity_id: light.living_room
#   brightness_pct: 100
```

#### Trace Comparison

```yaml
# Compare multiple trace runs to find patterns:

# Trace 1 (Success):
#   Trigger time: 08:00:00
#   Condition 'is_daytime': TRUE
#   Actions: All completed

# Trace 2 (Failed):
#   Trigger time: 22:00:00
#   Condition 'is_daytime': FALSE  ← Condition failed
#   Actions: Not executed

# Pattern: Automation only runs during day
```

#### Downloading Traces

```yaml
# Export trace for sharing/analysis:
# 1. Open trace in UI
# 2. Click "Download trace" button
# 3. Save JSON file

# Trace JSON structure:
# {
#   "domain": "automation",
#   "item_id": "automation.my_automation",
#   "run_id": "abc123...",
#   "state": "stopped",
#   "timestamp": {...},
#   "trace": {
#     "0": {"path": "trigger/0", ...},
#     "1": {"path": "condition/0", ...},
#     ...
#   },
#   "context": {...}
# }
```

#### Trace-Based Debugging Workflow

```markdown
## Debugging Steps

1. **Reproduce the issue**
   - Trigger the automation manually or wait for natural trigger
   - Note the approximate time

2. **Open trace**
   - Settings > Automations > [Automation] > Traces
   - Find trace at the relevant time

3. **Check trigger**
   - Was the right trigger activated?
   - Are trigger variables correct?

4. **Check conditions**
   - Did all conditions pass/fail as expected?
   - Look at actual values vs expected

5. **Check actions**
   - Which actions executed?
   - Any errors reported?
   - Were template values correct?

6. **Fix and re-test**
   - Make changes
   - Trigger again
   - Verify new trace shows success
```

#### Common Trace Patterns

| Pattern | Meaning |
|---------|---------|
| No trace exists | Trigger never fired |
| Trace stops at condition | Condition evaluated false |
| Error at action | Service call failed |
| Empty response_variable | Service returned no data |
| Timeout at action | External service slow/down |

---

## Integration Problems

### Integration Not Loading

```yaml
# Check logs
logger:
  logs:
    homeassistant.components.integration_name: debug

# Common causes:
# 1. Missing dependencies
# 2. Network unavailable
# 3. Invalid credentials
# 4. API changes

# Reload integration
# Settings > Devices & Services > [Integration] > Reload

# Remove and re-add
# Settings > Devices & Services > [Integration] > Delete
# Then add again
```

### Authentication Failures

```yaml
# Cloud services
# 1. Check credentials valid
# 2. Re-authenticate via UI
# 3. Check API quotas/limits

# Local services
# 1. Verify IP address
# 2. Check port accessibility
# 3. Verify username/password

# Token-based
# 1. Generate new token
# 2. Update configuration
# 3. Restart integration
```

### Discovery Issues

```yaml
# mDNS/Bonjour issues
# 1. Check network allows multicast
# 2. Verify device on same network
# 3. Try manual configuration

# SSDP issues
# 1. Check UPnP enabled on router
# 2. Verify device broadcasting
# 3. Check firewall rules

# Bluetooth issues
# 1. Verify Bluetooth adapter
# 2. Check device in pairing mode
# 3. Distance/interference
```

### API Errors

```yaml
# Rate limiting
# - Reduce polling interval
# - Use webhooks if available
# - Check API documentation

# Timeout errors
# - Increase timeout in config
# - Check network latency
# - Verify service availability

# Example: Increase timeout
rest:
  - resource: https://api.example.com/data
    scan_interval: 60
    timeout: 30  # Increase from default
```

---

## Performance Issues

### Slow UI

```yaml
# Causes:
# - Too many entities on dashboard
# - Complex templates
# - Large history database
# - Slow custom cards

# Solutions:

# 1. Reduce dashboard complexity
# - Split into multiple views
# - Use pagination

# 2. Optimize templates
# - Avoid expensive operations in templates
# - Cache results where possible

# 3. Limit history
recorder:
  purge_keep_days: 5
  exclude:
    entities:
      - sensor.high_frequency_sensor
```

### High CPU Usage

```yaml
# Identify cause
# Settings > System > Logs (Debug)

# Common causes:
# 1. Polling integrations
# 2. Complex templates
# 3. Recorder database
# 4. Custom components

# Reduce polling
integration_name:
  scan_interval: 60  # Increase interval

# Exclude from recorder
recorder:
  exclude:
    domains:
      - automation
      - script
    entities:
      - sensor.fast_changing
```

### Memory Issues

```yaml
# Check memory usage
# Settings > System > Hardware

# Reduce memory:

# 1. Limit recorder history
recorder:
  purge_keep_days: 3
  commit_interval: 1

# 2. Exclude verbose entities
recorder:
  exclude:
    domains:
      - media_player
      - camera

# 3. Reduce log verbosity
logger:
  default: warning
```

### Database Performance

```yaml
# Recorder optimization
recorder:
  db_url: sqlite:///config/home-assistant_v2.db
  purge_keep_days: 7
  commit_interval: 1
  exclude:
    domains:
      - automation
      - script
      - scene
    entity_globs:
      - sensor.*_battery
    event_types:
      - service_removed
      - service_executed
      - platform_discovered
      - homeassistant_start
      - homeassistant_stop

# Purge database manually
service: recorder.purge
data:
  keep_days: 3
  repack: true
```

---

## Network Problems

### Connection Refused

```yaml
# Check service running
# For integrations requiring local access

# Verify port open
# Developer Tools > Services > homeassistant.check_config

# Common causes:
# - Firewall blocking
# - Wrong IP address
# - Service not running
# - SSL/TLS issues

# Test connectivity
# From HA terminal:
ping device_ip
curl http://device_ip:port
```

### SSL Certificate Issues

```yaml
# Self-signed certificates
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem

# Certificate expired
# Renew via your certificate provider
# Let's Encrypt auto-renews with proper setup

# Mixed content warnings
# Ensure all resources use HTTPS
```

### DNS Resolution

```yaml
# If hostnames not resolving:

# 1. Check DNS settings
# System > Network

# 2. Use IP addresses instead
# Replace hostname with IP in configs

# 3. Configure local DNS
# Add to /etc/hosts if needed
```

### WebSocket Issues

```yaml
# Companion app connection problems:

# 1. Check external URL
# Settings > System > Network > External URL

# 2. Verify port forwarding
# Router: external_port -> HA_IP:8123

# 3. Check SSL certificate valid
# Use Let's Encrypt or similar

# 4. Verify no proxy issues
# Ensure WebSocket headers passed through
```

---

## Database Issues

### Corrupt Database

```bash
# Symptoms:
# - HA won't start
# - History not loading
# - Errors about database

# Solution 1: Repair
sqlite3 home-assistant_v2.db "PRAGMA integrity_check"
sqlite3 home-assistant_v2.db "REINDEX"
sqlite3 home-assistant_v2.db "VACUUM"

# Solution 2: Reset database
# Backup first!
mv home-assistant_v2.db home-assistant_v2.db.corrupt
# HA will create new database on restart
```

### Database Too Large

```yaml
# Check size
# ls -lh home-assistant_v2.db

# Reduce with purge
service: recorder.purge
data:
  keep_days: 3
  repack: true

# Configure exclusions
recorder:
  purge_keep_days: 5
  exclude:
    domains:
      - media_player
      - camera
    entity_globs:
      - sensor.*_linkquality
```

### Migration Issues

```yaml
# After HA upgrade, database migration may fail

# Check logs for migration errors
grep -i "migration" home-assistant.log

# If migration fails:
# 1. Backup database
# 2. Check HA version compatibility
# 3. May need fresh database

# Force migration (caution!)
# Usually not recommended - prefer clean start
```

---

## Log Analysis

### Log Configuration

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    # Specific component debugging
    homeassistant.components.automation: debug
    homeassistant.components.script: debug

    # Integration debugging
    homeassistant.components.mqtt: debug
    custom_components.my_integration: debug

    # Reduce noise
    homeassistant.components.recorder: warning
    homeassistant.components.http: warning
```

### Log Locations

```bash
# Main log
/config/home-assistant.log

# System logs (Supervised/HAOS)
ha host logs
ha supervisor logs

# Docker logs
docker logs homeassistant

# Container logs
journalctl -u home-assistant
```

### Log Filtering

```bash
# Search for errors
grep -i "error" home-assistant.log

# Search for specific entity
grep "light.living_room" home-assistant.log

# Search for time range
grep "2024-01-15 14:" home-assistant.log

# Tail with filtering
tail -f home-assistant.log | grep -i "automation"

# Last N lines
tail -n 100 home-assistant.log
```

### Common Log Patterns

```yaml
# Connection error
# "Unable to connect to [host]"
# Check: Network, credentials, service status

# Entity unavailable
# "Entity not found: [entity_id]"
# Check: Entity exists, integration loaded

# Template error
# "Error rendering template"
# Check: Template syntax, entity availability

# Authentication failed
# "Invalid authentication"
# Check: Credentials, API tokens

# Rate limited
# "Too many requests"
# Check: Polling interval, API limits
```

---

## Recovery Procedures

### Backup Restoration

```bash
# HAOS/Supervised
# Settings > System > Backups > [Backup] > Restore

# Manual restoration
# 1. Stop HA
ha core stop

# 2. Extract backup
tar -xzf backup.tar.gz -C /config

# 3. Start HA
ha core start
```

### Factory Reset

```bash
# HAOS - Full reset
# Settings > System > Restart > Factory Reset

# Keep add-ons, reset config
# Delete config files except:
# - .storage/core.uuid
# - .storage/auth*

# Manual config reset
rm -rf /config/*
# Restart will create default config
```

### Integration Reset

```yaml
# Remove and re-add integration

# 1. Document current settings
# 2. Settings > Devices & Services
# 3. Click integration
# 4. Delete
# 5. Restart HA
# 6. Re-add integration
# 7. Restore settings
```

### Emergency Config

```yaml
# Minimal working configuration
# configuration.yaml

homeassistant:
  name: Home
  unit_system: metric
  time_zone: Europe/Stockholm

# This gets HA running for further troubleshooting
```

---

## Diagnostic Tools

### Developer Tools

```yaml
# States
# View all entity states
# Filter, search, modify

# Services
# Call any service
# Test service parameters

# Template
# Test Jinja2 templates
# Check entity availability

# Events
# Listen to events
# Fire test events

# Statistics
# View long-term statistics
# Fix statistics issues
```

### Check Configuration

```yaml
# Via UI
# Developer Tools > YAML > Check Configuration

# Via CLI
hass --script check_config

# Output shows:
# - Syntax errors
# - Invalid configurations
# - Missing dependencies
```

### System Health

```yaml
# Settings > System > Repairs
# Shows:
# - Integration issues
# - Configuration problems
# - Update requirements

# Settings > System > Logs
# Real-time log viewing
# Downloadable log file
```

### Network Diagnostics

```bash
# Check connectivity
ping 8.8.8.8

# Check DNS
nslookup google.com

# Check specific port
nc -zv host port

# Trace route
traceroute host
```

---

## Best Practices

### Preventive Measures

| Practice | Benefit |
|----------|---------|
| Regular backups | Easy recovery |
| Version control | Track changes |
| Staged updates | Catch issues early |
| Log monitoring | Early detection |

### Backup Strategy

```yaml
# Automated backups
automation:
  - alias: "Weekly Backup"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: backup.create
```

### Update Strategy

```yaml
# 1. Read release notes
# 2. Wait 24-48h after release
# 3. Backup before updating
# 4. Update core first, then add-ons
# 5. Test critical automations
# 6. Monitor logs for 24h
```

### Documentation

```yaml
# Keep notes on:
# - Custom configurations
# - Workarounds applied
# - Integration settings
# - Network setup

# Example: config/NOTES.md
# Home Assistant Notes
#
# ## Custom Integrations
# - localtuya: Local keys in secrets.yaml
#
# ## Known Issues
# - Hue bridge needs restart after power outage
```

---

## Quick Reference

### Emergency Commands

```bash
# HAOS/Supervised
ha core restart
ha core rebuild
ha supervisor repair
ha host reboot

# Docker
docker restart homeassistant
docker logs homeassistant --tail 100

# Core installation
systemctl restart home-assistant
```

### Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Entity unavailable | Restart integration |
| Automation not running | Check traces, conditions |
| UI not loading | Clear browser cache |
| Integration error | Delete and re-add |
| Database corrupt | Rename, restart |
| Config error | Check YAML syntax |

### Useful Templates

```yaml
# Debug entity state
{{ states('entity_id') }}
{{ state_attr('entity_id', 'attribute') }}
{{ is_state('entity_id', 'state') }}

# Check entity availability
{{ states('entity_id') not in ['unknown', 'unavailable'] }}

# List unavailable entities
{% for state in states if state.state == 'unavailable' %}
  {{ state.entity_id }}
{% endfor %}
```

