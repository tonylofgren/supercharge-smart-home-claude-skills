# Home Assistant Configuration Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Configuration Structure](#configuration-structure)
- [Secrets Management](#secrets-management)
- [Include Directives](#include-directives)
- [Environment Variables](#environment-variables)
- [Configuration Validation](#configuration-validation)
- [File Organization](#file-organization)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Home Assistant's configuration is stored in YAML files in the `/config` directory. The main entry point is `configuration.yaml`, which can include other files for better organization.

### Key Terms

| Term | Description |
|------|-------------|
| **configuration.yaml** | Main configuration file, loaded on startup |
| **secrets.yaml** | Stores sensitive values (API keys, passwords) |
| **!include** | Directive to include another YAML file |
| **!secret** | Directive to reference a value from secrets.yaml |
| **Package** | Self-contained configuration bundle |
| **Domain** | Integration type (light, switch, automation, etc.) |

### Configuration Directory Structure

```
/config/
├── configuration.yaml      # Main configuration
├── secrets.yaml           # Sensitive data
├── automations.yaml       # Automations (UI-managed)
├── scripts.yaml           # Scripts (UI-managed)
├── scenes.yaml            # Scenes (UI-managed)
├── customize.yaml         # Entity customizations
├── packages/              # Package directory
│   ├── lighting.yaml
│   └── climate.yaml
├── includes/              # Split configuration
│   ├── sensors.yaml
│   └── binary_sensors.yaml
└── www/                   # Local web assets
```

---

## Configuration Structure

### Minimal Configuration

```yaml
# configuration.yaml - Minimal setup
homeassistant:
  name: Home
  unit_system: metric
  time_zone: Europe/Stockholm
  currency: SEK

# Enable default integrations
default_config:

# Enable frontend
frontend:

# Enable HTTP API
http:

# Logging
logger:
  default: info
```

### Complete Configuration Example

```yaml
# configuration.yaml - Complete example

# Core settings
homeassistant:
  name: Home
  latitude: !secret home_latitude
  longitude: !secret home_longitude
  elevation: 50
  unit_system: metric
  currency: SEK
  country: SE
  time_zone: Europe/Stockholm
  external_url: !secret external_url
  internal_url: "http://homeassistant.local:8123"

  # Customizations
  customize: !include customize.yaml
  customize_glob: !include customize_glob.yaml

  # Allow list for domains
  allowlist_external_dirs:
    - /config/www
    - /media

  # Media directories
  media_dirs:
    media: /media
    recordings: /config/www/recordings

# Enable default integrations (recorder, history, logbook, etc.)
default_config:

# Frontend configuration
frontend:
  themes: !include_dir_merge_named themes/

# HTTP settings
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  ip_ban_enabled: true
  login_attempts_threshold: 5

# Recorder settings
recorder:
  db_url: !secret db_url
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
      - sensor.last_boot

# Logger configuration
logger:
  default: warning
  logs:
    homeassistant.core: info
    homeassistant.components.mqtt: debug
    custom_components.hacs: debug

# Include external files
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# Include split configuration
sensor: !include_dir_merge_list includes/sensors/
binary_sensor: !include includes/binary_sensors.yaml
template: !include includes/templates.yaml

# Enable packages
homeassistant:
  packages: !include_dir_named packages/
```

### Domain Configuration

Each integration domain has its own configuration structure:

```yaml
# Single platform configuration
sensor:
  - platform: time_date
    display_options:
      - time
      - date

# Multiple platforms
light:
  - platform: group
    name: Living Room Lights
    entities:
      - light.ceiling
      - light.lamp

# Integration-specific
mqtt:
  broker: !secret mqtt_broker
  username: !secret mqtt_username
  password: !secret mqtt_password
```

---

## Secrets Management

### secrets.yaml Structure

```yaml
# secrets.yaml - Store all sensitive values here
# NEVER commit this file to version control!

# Location
home_latitude: "59.3293"
home_longitude: "18.0686"

# URLs
external_url: "https://home.example.com"
internal_url: "http://192.168.1.100:8123"

# Database
db_url: "postgresql://user:password@localhost/homeassistant"

# MQTT
mqtt_broker: "192.168.1.50"
mqtt_username: "homeassistant"
mqtt_password: "secure_password_here"

# API Keys
openweathermap_api_key: "your_api_key_here"
pushover_api_key: "your_pushover_key"
pushover_user_key: "your_user_key"

# Notifications
telegram_bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
telegram_chat_id: "-1001234567890"

# Device credentials
camera_username: "admin"
camera_password: "camera_password"

# OAuth tokens (auto-managed by integrations)
# spotify_token: "auto_generated"
```

### Using Secrets

```yaml
# In configuration.yaml
mqtt:
  broker: !secret mqtt_broker
  username: !secret mqtt_username
  password: !secret mqtt_password

notify:
  - platform: pushover
    api_key: !secret pushover_api_key
    user_key: !secret pushover_user_key
```

### Multi-Level Secrets

```yaml
# secrets.yaml - Nested structure not supported
# Each secret must be a single value

# Good - flat structure
influxdb_host: "192.168.1.60"
influxdb_port: "8086"
influxdb_username: "homeassistant"
influxdb_password: "secure_password"

# Usage
influxdb:
  host: !secret influxdb_host
  port: !secret influxdb_port
  username: !secret influxdb_username
  password: !secret influxdb_password
```

### Secret Files for Complex Values

```yaml
# For multiline secrets, use separate files
tls:
  certificate: !include_dir_merge_list ssl/certificate.pem

# Or use the file directly
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

---

## Include Directives

### !include - Single File

```yaml
# Include a single YAML file
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# Include from subdirectory
sensor: !include includes/sensors.yaml
```

### !include_dir_list - List from Directory

Merges files as a list (for domains that accept lists).

```yaml
# Directory structure:
# includes/sensors/
# ├── temperature.yaml
# └── power.yaml

# temperature.yaml
- platform: template
  sensors:
    average_temperature:
      value_template: "{{ states('sensor.temp') }}"

# power.yaml
- platform: template
  sensors:
    total_power:
      value_template: "{{ states('sensor.power') }}"

# configuration.yaml
sensor: !include_dir_list includes/sensors/

# Result: Both sensors merged into a list
```

### !include_dir_named - Named Dictionary

Merges files as named dictionary entries.

```yaml
# Directory structure:
# packages/
# ├── lighting.yaml
# └── climate.yaml

# lighting.yaml
automation:
  - id: motion_light
    alias: Motion Light
    trigger: ...

# climate.yaml
automation:
  - id: climate_schedule
    alias: Climate Schedule
    trigger: ...

# configuration.yaml
homeassistant:
  packages: !include_dir_named packages/

# Result: packages.lighting.automation and packages.climate.automation
```

### !include_dir_merge_list - Merge All as List

Combines all files into a single list.

```yaml
# Directory structure:
# automations/
# ├── lights.yaml      # Contains list of automations
# └── climate.yaml     # Contains list of automations

# configuration.yaml
automation: !include_dir_merge_list automations/

# All automations from both files merged into one list
```

### !include_dir_merge_named - Merge Named Dictionaries

```yaml
# Directory structure:
# themes/
# ├── dark.yaml        # dark_theme: { ... }
# └── light.yaml       # light_theme: { ... }

# configuration.yaml
frontend:
  themes: !include_dir_merge_named themes/

# All themes merged into frontend.themes
```

### Nested Includes

```yaml
# configuration.yaml
homeassistant:
  customize: !include customize.yaml

# customize.yaml
light.living_room:
  friendly_name: Living Room Light
  icon: mdi:ceiling-light

# Can also include within included files
# customize.yaml
!include customize_lights.yaml
!include customize_sensors.yaml
```

---

## Environment Variables

### Using Environment Variables

```yaml
# configuration.yaml
homeassistant:
  name: !env_var HOME_NAME
  latitude: !env_var HOME_LAT
  longitude: !env_var HOME_LONG

http:
  server_port: !env_var HA_PORT 8123  # With default value
```

### Setting Environment Variables

```bash
# In Docker
docker run -e HOME_NAME="My Home" -e HOME_LAT="59.33" ...

# In docker-compose.yml
environment:
  - HOME_NAME=My Home
  - HOME_LAT=59.33
  - HOME_LONG=18.07

# In systemd service
Environment="HOME_NAME=My Home"
```

### Environment Variables in Secrets

```yaml
# secrets.yaml
db_password: !env_var DB_PASSWORD

# configuration.yaml
recorder:
  db_url: !secret db_url
```

---

## Configuration Validation

### Check Configuration

```bash
# From terminal
ha core check

# In Docker
docker exec homeassistant python -m homeassistant --script check_config

# From Developer Tools > YAML
# Click "Check Configuration" button
```

### Validation Output

```
# Success
Configuration valid!

# Error
Invalid config for [sensor.template]: required key not provided @ data['sensors']
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `required key not provided` | Missing required field | Add the required field |
| `not a valid value` | Invalid value for field | Check valid options in docs |
| `extra keys not allowed` | Typo or wrong key | Fix spelling or remove key |
| `Unable to read file` | File not found | Check file path and permissions |
| `found duplicate key` | Same key twice | Remove duplicate |

### YAML Syntax Validation

```yaml
# Common YAML issues

# Bad - tabs instead of spaces
automation:
	alias: Test  # Tab character - INVALID

# Good - use spaces (2 spaces recommended)
automation:
  alias: Test

# Bad - missing quotes on special values
sensor:
  name: on  # 'on' is a boolean in YAML

# Good - quote special values
sensor:
  name: "on"

# Bad - colon in value without quotes
sensor:
  name: Time: 12:00

# Good
sensor:
  name: "Time: 12:00"
```

---

## File Organization

### Recommended Directory Structure

```
/config/
├── configuration.yaml          # Main config (minimal)
├── secrets.yaml               # Sensitive data
├── customize.yaml             # Entity customizations
│
├── automations/               # Split automations by area
│   ├── lighting.yaml
│   ├── climate.yaml
│   ├── security.yaml
│   └── presence.yaml
│
├── scripts/                   # Split scripts by function
│   ├── routines.yaml
│   └── notifications.yaml
│
├── includes/                  # Additional config files
│   ├── sensors/
│   │   ├── template.yaml
│   │   └── mqtt.yaml
│   ├── binary_sensors.yaml
│   └── input_helpers.yaml
│
├── packages/                  # Self-contained packages
│   ├── lighting_system.yaml
│   ├── climate_control.yaml
│   └── guest_mode.yaml
│
├── themes/                    # Dashboard themes
│   ├── dark_theme.yaml
│   └── light_theme.yaml
│
├── www/                       # Local web assets
│   ├── icons/
│   └── images/
│
├── custom_components/         # Custom integrations
│   └── hacs/
│
└── blueprints/               # Automation blueprints
    └── automation/
        └── motion_light.yaml
```

### Splitting Large Configuration

```yaml
# configuration.yaml - Keep minimal
homeassistant:
  name: Home
  packages: !include_dir_named packages/

default_config:

# UI-managed files
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# Split configuration
sensor: !include_dir_merge_list includes/sensors/
binary_sensor: !include includes/binary_sensors.yaml
template: !include includes/template.yaml
input_boolean: !include includes/input_boolean.yaml
input_number: !include includes/input_number.yaml
input_select: !include includes/input_select.yaml
```

### Package-Based Organization

```yaml
# packages/lighting_system.yaml
# Self-contained lighting configuration

input_boolean:
  motion_lights_enabled:
    name: Motion Lights Enabled
    icon: mdi:motion-sensor

input_number:
  motion_light_timeout:
    name: Motion Light Timeout
    min: 1
    max: 30
    step: 1
    unit_of_measurement: minutes

automation:
  - id: pkg_motion_light
    alias: "[Lighting] Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.motion_lights_enabled
        state: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

---

## Common Patterns

### Conditional Configuration

```yaml
# Use packages to enable/disable features
# packages/debug.yaml - only include when debugging

logger:
  default: debug
  logs:
    homeassistant.core: debug
    homeassistant.components.automation: debug
```

### Multi-Environment Configuration

```yaml
# secrets.yaml - Development
mqtt_broker: "localhost"
external_url: "http://localhost:8123"

# secrets.yaml - Production
mqtt_broker: "mqtt.example.com"
external_url: "https://home.example.com"

# Same configuration.yaml works in both environments
mqtt:
  broker: !secret mqtt_broker
```

### Backup-Friendly Configuration

```yaml
# Keep secrets separate for easy backup exclusion

# .gitignore
secrets.yaml
*.db
*.log
home-assistant_v2.db
.storage/

# Backup command (exclude sensitive files)
tar --exclude='secrets.yaml' --exclude='*.db' -cvf backup.tar /config/
```

### Template Variables in Configuration

```yaml
# Using templates in some configuration fields
# Note: Not all fields support templates!

template:
  - sensor:
      - name: "Greeting"
        state: >
          {% if now().hour < 12 %}
            Good morning
          {% elif now().hour < 18 %}
            Good afternoon
          {% else %}
            Good evening
          {% endif %}
```

### Reload Without Restart

```yaml
# These domains can be reloaded without restart:
# Developer Tools > YAML > Reload

# Reloadable:
# - automation
# - script
# - scene
# - input_boolean, input_number, input_select, input_text, input_datetime
# - template (sensors, binary_sensors)
# - group
# - timer
# - person
# - zone
# - customize
# - core (homeassistant section)

# Requires restart:
# - Most integrations
# - http
# - recorder
# - logger
# - packages (mostly)
```

---

## Best Practices

### Naming Conventions

```yaml
# Files: lowercase with underscores
automations.yaml          # Good
Automations.yaml          # Avoid
my-automations.yaml       # Avoid

# Directories: lowercase, descriptive
packages/                 # Good
Packages/                 # Avoid

# Package names: descriptive, area-based
packages/lighting_system.yaml    # Good
packages/stuff.yaml              # Avoid
```

### Documentation

```yaml
# Document your configuration
# configuration.yaml

# ====================
# Home Assistant Core
# ====================
homeassistant:
  name: Home
  # ... settings ...

# ====================
# Network Settings
# ====================
http:
  # Enable SSL for external access
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem

# ====================
# Integrations
# ====================

# MQTT broker for IoT devices
mqtt:
  broker: !secret mqtt_broker
```

### Security

```yaml
# Never commit secrets
# .gitignore
secrets.yaml

# Use strong passwords
# secrets.yaml
mqtt_password: "Use_A_Strong_Random_Password_Here_123!"

# Limit external access
http:
  ip_ban_enabled: true
  login_attempts_threshold: 5

# Use SSL for external access
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

### Version Control

```yaml
# Track configuration in git
git init
git add .
git commit -m "Initial configuration"

# Exclude sensitive and generated files
# .gitignore
secrets.yaml
*.db
*.log
.storage/
tts/
custom_components/
```

---

## Troubleshooting

### Configuration Won't Load

| Problem | Check | Solution |
|---------|-------|----------|
| YAML syntax error | Validation output | Fix indentation, quotes, colons |
| File not found | File path | Check spelling and path |
| Permission denied | File permissions | Fix ownership: `chown -R homeassistant:homeassistant /config` |
| Duplicate key | YAML structure | Remove duplicate entries |

### Debug Configuration Loading

```yaml
# Enable debug logging for core
logger:
  default: info
  logs:
    homeassistant.config: debug
    homeassistant.loader: debug
```

### Common YAML Errors

```yaml
# Error: found character '\t' that cannot start any token
# Cause: Tab character used
# Fix: Replace tabs with spaces

# Error: mapping values are not allowed here
# Cause: Missing space after colon
# Fix: Add space after colon
name:value   # Bad
name: value  # Good

# Error: could not determine a constructor for the tag
# Cause: Unknown YAML tag
# Fix: Check for typos in !include, !secret, etc.
```

### Test Configuration in Safe Mode

```bash
# Start Home Assistant in safe mode (no custom components)
ha core restart --safe-mode

# Check if configuration loads
ha core check

# Restart normally
ha core restart
```

### Backup and Recovery

```bash
# Create backup
ha backup new --name "before_changes"

# Restore from backup
ha backup restore <backup_slug>

# Manual backup
cp -r /config /config_backup_$(date +%Y%m%d)
```

---

## Reference

### YAML Include Directives

| Directive | Description | Use Case |
|-----------|-------------|----------|
| `!include file.yaml` | Include single file | Split config files |
| `!include_dir_list dir/` | Merge files as list | Multiple sensor files |
| `!include_dir_named dir/` | Named dictionary merge | Packages |
| `!include_dir_merge_list dir/` | Merge all as single list | Automations split by area |
| `!include_dir_merge_named dir/` | Merge named dictionaries | Themes |
| `!secret key` | Value from secrets.yaml | Sensitive data |
| `!env_var VAR` | Environment variable | Docker configuration |
| `!env_var VAR default` | Env var with default | Optional settings |

### Reloadable Domains

| Domain | Reload Method |
|--------|--------------|
| automation | YAML reload or service |
| script | YAML reload |
| scene | YAML reload |
| input_* | YAML reload |
| template | YAML reload |
| group | YAML reload |
| timer | YAML reload |
| person | YAML reload |
| zone | YAML reload |
| customize | YAML reload |

### Required Restart

| Domain | Reason |
|--------|--------|
| http | Web server configuration |
| recorder | Database connection |
| logger | Logging configuration |
| Most integrations | Integration initialization |
| packages | Package loading |
