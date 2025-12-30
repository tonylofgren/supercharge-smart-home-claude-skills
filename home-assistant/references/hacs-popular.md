# Popular HACS Integrations

Complete guide for the most popular HACS custom components for Home Assistant.

---

## Overview

HACS (Home Assistant Community Store) provides access to custom integrations, cards, and themes. This guide covers the most downloaded and useful custom components.

| Integration | Purpose | Downloads |
|-------------|---------|-----------|
| **Local Tuya** | Local control of Tuya devices | #1 Most Popular |
| **Alarmo** | Full-featured alarm system | Top 10 |
| **Browser Mod** | Browser control & popups | Top 10 |
| **Powercalc** | Virtual power sensors | Top 20 |
| **Adaptive Lighting** | Circadian rhythm lights | Top 20 |
| **Battery Notes** | Battery tracking | Top 30 |
| **Auto Backup** | Automated backups | Top 30 |

---

## HACS Installation

### Prerequisites

1. Home Assistant 2023.1 or newer
2. Access to configuration files
3. GitHub account (recommended)

### Installation

1. Download HACS:
```bash
# In terminal/SSH
wget -O - https://get.hacs.xyz | bash -
```

2. Restart Home Assistant
3. Go to **Settings > Devices & Services**
4. Click **Add Integration** > **HACS**
5. Follow authorization flow with GitHub

---

## Local Tuya

Local control for Tuya devices without cloud dependency.

### Why Use Local Tuya?

| Feature | Cloud Tuya | Local Tuya |
|---------|------------|------------|
| **Latency** | 1-3 seconds | Instant |
| **Internet Required** | Yes | No (after setup) |
| **Privacy** | Data via cloud | Local only |
| **Reliability** | Cloud dependent | Very reliable |

### Installation

1. In HACS, search for **Local Tuya**
2. Install and restart Home Assistant
3. Go to **Settings > Devices & Services**
4. Click **Add Integration** > **LocalTuya**

### Getting Local Keys

See [integrations-tuya.md](integrations-tuya.md) for detailed key extraction methods.

Quick method with tinytuya:
```bash
pip install tinytuya
python -m tinytuya wizard
# Follow prompts with Tuya credentials
```

### Device Configuration

```yaml
# Common Data Points (DPs):

# Smart Plug
# DP 1: Switch (on/off)
# DP 17: Current (mA)
# DP 18: Power (W * 10)
# DP 19: Voltage (V * 10)

# Light Bulb
# DP 20: Switch (on/off)
# DP 21: Mode (white/colour/scene)
# DP 22: Brightness (10-1000)
# DP 23: Color temperature (0-1000)
# DP 24: Color (HSV format)

# Cover/Blind
# DP 1: Control (open/close/stop)
# DP 2: Percent control (0-100)
# DP 3: Current position (0-100)
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Device not found | Check IP address, use DHCP reservation |
| Wrong local key | Re-extract using tinytuya |
| Connection refused | Try protocol 3.3, then 3.4 |
| Intermittent connection | Block device internet access |

---

## Alarmo

Full-featured alarm system with professional features.

### Features

- Multiple arm modes (away, home, night, vacation)
- Entry/exit delays
- Bypass sensors
- Area/zone support
- Code management
- MQTT support
- Notifications

### Installation

1. In HACS, search for **Alarmo**
2. Install and restart Home Assistant
3. Go to **Settings > Devices & Services**
4. Click **Add Integration** > **Alarmo**

### Configuration via UI

Access Alarmo panel at **Configuration > Alarmo** or sidebar.

### Sensors Setup

```yaml
# Supported sensor types:
# - Door (binary_sensor with device_class: door)
# - Window (binary_sensor with device_class: window)
# - Motion (binary_sensor with device_class: motion)
# - Tamper (binary_sensor with device_class: tamper)
# - Environmental (smoke, gas, moisture)
```

### Arm Modes

```yaml
# Configure per mode:
# - Exit delay: Time to leave after arming
# - Entry delay: Time to disarm after trigger
# - Trigger time: Alarm duration
# - Which sensors are active
```

### Automations with Alarmo

```yaml
# Arm alarm when leaving
automation:
  - alias: "Arm Alarm When Away"
    trigger:
      - platform: state
        entity_id: group.family
        to: "not_home"
        for: "00:05:00"
    action:
      - service: alarmo.arm
        data:
          entity_id: alarm_control_panel.alarmo
          mode: away
          skip_delay: false

# Disarm when arriving
automation:
  - alias: "Disarm Alarm When Home"
    trigger:
      - platform: state
        entity_id: person.me
        to: "home"
    action:
      - service: alarmo.disarm
        data:
          entity_id: alarm_control_panel.alarmo
          code: !secret alarm_code

# Notification on trigger
automation:
  - alias: "Alarm Triggered Notification"
    trigger:
      - platform: state
        entity_id: alarm_control_panel.alarmo
        to: "triggered"
    action:
      - service: notify.mobile_app
        data:
          title: "🚨 ALARM TRIGGERED"
          message: "{{ state_attr('alarm_control_panel.alarmo', 'open_sensors') | join(', ') }}"
          data:
            priority: high
            ttl: 0
```

### Areas Configuration

```yaml
# Multiple areas for different zones:
# - Main House: All perimeter sensors
# - Garage: Garage door, motion
# - Outbuilding: Separate entry delays

# Each area has independent:
# - Arm modes
# - Sensors
# - Delays
# - Codes
```

---

## Browser Mod

Control browsers and create popups from Home Assistant.

### Features

- Browser as media player
- Popup cards
- Navigate between views
- Execute JavaScript
- Browser sensors (battery, screen size)

### Installation

1. In HACS, search for **Browser Mod**
2. Install and restart Home Assistant
3. Add to Lovelace resources
4. Register browsers at `/browser_mod/`

### Browser Registration

Each browser gets a unique ID. Register at:
```
http://your-ha:8123/browser_mod/
```

### Popup Cards

```yaml
# Button that opens popup
type: button
name: Lights
tap_action:
  action: fire-dom-event
  browser_mod:
    service: browser_mod.popup
    data:
      title: "Light Controls"
      content:
        type: entities
        entities:
          - light.living_room
          - light.kitchen
          - light.bedroom

# Popup with custom card
tap_action:
  action: fire-dom-event
  browser_mod:
    service: browser_mod.popup
    data:
      title: "Thermostat"
      size: normal  # normal, wide, fullscreen
      content:
        type: thermostat
        entity: climate.living_room
```

### Services

```yaml
# Navigate to view
service: browser_mod.navigate
data:
  path: /lovelace/cameras

# Show popup
service: browser_mod.popup
data:
  content:
    type: markdown
    content: "Hello World!"

# Execute JavaScript
service: browser_mod.javascript
data:
  code: "alert('Hello from Home Assistant!')"

# Refresh browser
service: browser_mod.refresh

# Close popup
service: browser_mod.close_popup
```

### Browser Sensors

```yaml
# Available sensors per registered browser:
# - sensor.browser_*_battery_level
# - sensor.browser_*_path
# - binary_sensor.browser_*_fullscreen
# - binary_sensor.browser_*_dark_mode
```

---

## Powercalc

Create virtual power sensors for devices without built-in power monitoring.

### Features

- Power estimation from device state
- Energy accumulation
- Device profiles library
- Smart groups
- Utility meter integration

### Installation

1. In HACS, search for **Powercalc**
2. Install and restart Home Assistant
3. Add sensors via UI or YAML

### Configuration Methods

#### Method 1: UI Configuration

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Powercalc**
3. Select configuration type
4. Configure power values

#### Method 2: YAML Configuration

```yaml
# configuration.yaml
powercalc:
  sensors:
    # Fixed power device
    - entity_id: switch.coffee_maker
      name: Coffee Maker Power
      fixed:
        power: 1200  # Watts when on

    # Linear brightness-based
    - entity_id: light.living_room
      name: Living Room Light Power
      linear:
        min_power: 5    # Power at 1% brightness
        max_power: 50   # Power at 100% brightness

    # Using device profile (from library)
    - entity_id: light.hue_bulb
      manufacturer: signify
      model: LCA001  # Hue Color A19

    # Media player states
    - entity_id: media_player.tv
      name: TV Power
      fixed:
        states_power:
          playing: 120
          paused: 100
          idle: 80
          standby: 1
          "off": 0

    # Fan with multiple speeds
    - entity_id: fan.ceiling_fan
      name: Ceiling Fan Power
      fixed:
        states_power:
          low: 15
          medium: 35
          high: 70
```

### Smart Groups

```yaml
# Group multiple sensors
powercalc:
  sensors:
    - create_group: Living Room
      entities:
        - entity_id: light.living_room_1
        - entity_id: light.living_room_2
        - entity_id: media_player.tv
        - entity_id: switch.speaker
```

### Utility Meter Integration

```yaml
# Track daily/monthly energy
utility_meter:
  living_room_energy_daily:
    source: sensor.living_room_energy
    cycle: daily
  living_room_energy_monthly:
    source: sensor.living_room_energy
    cycle: monthly
```

### Device Library

Powercalc includes profiles for thousands of devices:
- Philips Hue bulbs
- IKEA TRÅDFRI
- LIFX bulbs
- TP-Link Kasa
- Sonos speakers
- Many more

Search at: [Powercalc Profile Library](https://library.powercalc.nl/)

---

## Adaptive Lighting

Automatically adjust light color temperature and brightness based on time of day.

### Features

- Circadian rhythm lighting
- Sunrise/sunset adaptation
- Sleep mode
- Per-light configuration
- Manual override detection

### Installation

1. In HACS, search for **Adaptive Lighting**
2. Install and restart Home Assistant
3. Go to **Settings > Devices & Services**
4. Click **Add Integration** > **Adaptive Lighting**

### Configuration

```yaml
# Via UI:
# 1. Add integration
# 2. Select lights to control
# 3. Configure parameters:
#    - Min/max brightness
#    - Min/max color temperature
#    - Sunrise/sunset offset
#    - Transition duration
#    - Sleep mode settings
```

### Entities Created

```yaml
# Per configuration:
switch.adaptive_lighting_living_room          # Main on/off
switch.adaptive_lighting_adapt_brightness_living_room
switch.adaptive_lighting_adapt_color_living_room
switch.adaptive_lighting_sleep_mode_living_room
```

### Sleep Mode

```yaml
# Activate sleep mode (dim warm light)
automation:
  - alias: "Bedtime Adaptive Lighting"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.adaptive_lighting_sleep_mode_living_room

# Deactivate in morning
automation:
  - alias: "Morning Adaptive Lighting"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.adaptive_lighting_sleep_mode_living_room
```

### Manual Override Detection

Adaptive Lighting detects when you manually change a light and stops adapting it until:
- Light is turned off and on again
- A configurable timeout expires
- You manually reset the override

```yaml
# Reset manual override
service: adaptive_lighting.set_manual_control
data:
  entity_id: switch.adaptive_lighting_living_room
  lights:
    - light.living_room
  manual_control: false
```

### Automation Integration

```yaml
# Disable during movie mode
automation:
  - alias: "Movie Mode Lighting"
    trigger:
      - platform: state
        entity_id: media_player.tv
        to: "playing"
        attribute: media_content_type
    condition:
      - condition: template
        value_template: "{{ state_attr('media_player.tv', 'media_content_type') == 'movie' }}"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.adaptive_lighting_living_room
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness_pct: 10
          color_temp_kelvin: 2200
```

---

## Battery Notes

Track battery levels and types across all devices.

### Features

- Battery level dashboard
- Low battery notifications
- Battery type information
- Device library with battery specs
- Replacement reminders

### Installation

1. In HACS, search for **Battery Notes**
2. Install and restart Home Assistant
3. Go to **Settings > Devices & Services**
4. Click **Add Integration** > **Battery Notes**

### Automatic Detection

Battery Notes automatically detects devices with battery sensors and adds metadata from its device library.

### Entities Created

```yaml
# Per battery device:
sensor.device_name_battery_plus          # Enhanced battery sensor
binary_sensor.device_name_battery_low    # Low battery indicator
sensor.device_name_battery_type          # Battery type (CR2032, AA, etc.)
```

### Low Battery Automation

```yaml
automation:
  - alias: "Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id:
          - sensor.front_door_battery
          - sensor.motion_sensor_battery
          - sensor.temperature_sensor_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "🔋 Low Battery"
          message: "{{ trigger.to_state.name }} battery is at {{ trigger.to_state.state }}%"

# Weekly battery summary
automation:
  - alias: "Weekly Battery Report"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: notify.mobile_app
        data:
          title: "🔋 Weekly Battery Report"
          message: >
            Low batteries:
            {% for state in states.sensor
               if 'battery' in state.entity_id
               and state.state | int(100) < 30 %}
            - {{ state.name }}: {{ state.state }}%
            {% endfor %}
```

### Dashboard Card

```yaml
type: entities
title: Battery Status
entities:
  - type: custom:auto-entities
    card:
      type: entities
    filter:
      include:
        - entity_id: "*_battery"
          state: "< 30"
      exclude: []
    sort:
      method: state
      numeric: true
```

---

## Auto Backup

Automated backup creation and management.

### Features

- Scheduled backups
- Backup retention policies
- Exclude folders
- Backup before updates
- Cloud upload support

### Installation

1. In HACS, search for **Auto Backup**
2. Install and restart Home Assistant
3. Go to **Settings > Devices & Services**
4. Click **Add Integration** > **Auto Backup**

### Configuration

```yaml
# Via UI Configuration:
# - Backup time
# - Backup frequency (daily, weekly)
# - Retention: Keep X backups
# - Exclude folders (media, tmp)
# - Password protection
```

### Manual Backup Service

```yaml
# Create backup via automation
automation:
  - alias: "Backup Before Update"
    trigger:
      - platform: state
        entity_id: update.home_assistant_core_update
        attribute: in_progress
        to: true
    action:
      - service: auto_backup.backup
        data:
          name: "Pre-Update Backup {{ now().strftime('%Y-%m-%d') }}"
```

### Backup Retention

```yaml
# Automatic cleanup:
# - Keep last 7 daily backups
# - Keep last 4 weekly backups
# - Keep last 3 monthly backups
```

---

## HACS Best Practices

### Regular Updates

```yaml
# Check for HACS updates
automation:
  - alias: "HACS Update Notification"
    trigger:
      - platform: state
        entity_id: sensor.hacs
    condition:
      - condition: numeric_state
        entity_id: sensor.hacs
        above: 0
    action:
      - service: notify.mobile_app
        data:
          message: "{{ states('sensor.hacs') }} HACS updates available"
```

### Backup Before Installing

Always backup before installing new HACS integrations.

### Check Compatibility

1. Read HACS integration page
2. Check GitHub issues
3. Verify HA version compatibility
4. Test in development instance if possible

### Performance Considerations

- Too many custom integrations can slow HA
- Monitor system resources
- Remove unused integrations
- Check logs for errors

---

## Troubleshooting

### HACS Issues

| Issue | Solution |
|-------|----------|
| HACS not showing | Clear browser cache, check resources |
| Download fails | Check GitHub rate limits, try later |
| Integration not loading | Check logs, verify dependencies |
| Updates not showing | Click HACS > ⋮ > Reload |

### Integration-Specific

```yaml
# Check logs for specific integration
# Logger configuration:
logger:
  default: warning
  logs:
    custom_components.localtuya: debug
    custom_components.alarmo: debug
    custom_components.powercalc: debug
```

---

## Reference

### Useful Links

- [HACS Documentation](https://hacs.xyz/)
- [Local Tuya GitHub](https://github.com/rospogriern/localtuya)
- [Alarmo GitHub](https://github.com/nielsfaber/alarmo)
- [Browser Mod GitHub](https://github.com/thomasloven/hass-browser_mod)
- [Powercalc GitHub](https://github.com/bramstroker/homeassistant-powercalc)
- [Adaptive Lighting GitHub](https://github.com/basnijholt/adaptive-lighting)
- [Battery Notes GitHub](https://github.com/andrew-codechimp/ha-battery-notes)
- [Auto Backup GitHub](https://github.com/jcwillox/hass-auto-backup)

### Popular Card Recommendations

For dashboards, see also:
- [Mushroom Cards](mushroom-cards.md) - Modern minimalist cards
- [Dashboard Cards Reference](dashboard-cards.md) - Built-in card types
