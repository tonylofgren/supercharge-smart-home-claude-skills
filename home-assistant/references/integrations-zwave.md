# Z-Wave Integration Reference

## Table of Contents
- [Overview](#overview)
- [Z-Wave vs Zigbee Comparison](#z-wave-vs-zigbee-comparison)
- [Hardware Requirements](#hardware-requirements)
- [Z-Wave JS Setup](#z-wave-js-setup)
- [Device Pairing](#device-pairing)
- [Network Management](#network-management)
- [Automations & Scenes](#automations--scenes)
- [Device Configuration](#device-configuration)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

### What is Z-Wave?

Z-Wave is a wireless communication protocol designed specifically for home automation. It operates on sub-GHz frequencies (800-900 MHz depending on region) and uses a mesh network topology.

### Key Characteristics

| Feature | Z-Wave |
|---------|--------|
| **Frequency** | 868.42 MHz (EU), 908.42 MHz (US), varies by region |
| **Range** | 30-100m (outdoor), 10-30m (indoor) |
| **Max devices** | 232 per network |
| **Hops** | Up to 4 hops in mesh |
| **Protocol** | Proprietary (Z-Wave Alliance) |
| **Security** | S0, S2 encryption |

### Z-Wave Generations

| Generation | Year | Features |
|------------|------|----------|
| Z-Wave | 2001 | Basic mesh networking |
| Z-Wave Plus | 2013 | Extended range, more battery life |
| Z-Wave Plus V2 (700) | 2018 | S2 security, SmartStart |
| Z-Wave Long Range | 2020 | Up to 1.6km range, 4000 devices |
| 800 Series | 2023 | Improved range, lower power |

---

## Z-Wave vs Zigbee Comparison

| Aspect | Z-Wave | Zigbee |
|--------|--------|--------|
| **Frequency** | Sub-GHz (region-specific) | 2.4 GHz (global) |
| **Interference** | Less (fewer devices on frequency) | More (WiFi, Bluetooth) |
| **Range** | Generally longer | Generally shorter |
| **Device limit** | 232 per controller | 65,000+ (coordinator-dependent) |
| **Certification** | Mandatory (interoperability) | Optional (fragmentation) |
| **Cost** | Typically higher | Typically lower |
| **Power consumption** | Higher | Lower |
| **Mesh** | Always routing | Coordinator + routers |
| **Smart home brands** | Yale, Schlage, Aeotec, Fibaro | Philips Hue, IKEA, Aqara |

### When to Choose Z-Wave

- High reliability requirements (locks, security)
- Less WiFi interference concerns
- Premium device quality preference
- Established smart home ecosystem
- Long range needed

### When to Choose Zigbee

- Budget-conscious setup
- Many small sensors needed
- Global frequency preference
- Large device count
- Battery-powered devices

---

## Hardware Requirements

### Recommended Controllers

#### USB Controllers

| Controller | Series | Features | Price Range |
|------------|--------|----------|-------------|
| **Aeotec Z-Stick 7** | 700 | S2, SmartStart, backup | $45-55 |
| **Zooz ZST39** | 800 | Latest series, LR support | $35-45 |
| **Silicon Labs UZB-7** | 700 | Reference design | $30-40 |
| **Nortek HUSBZB-1** | 500 | Z-Wave + Zigbee combo | $35-45 |

#### GPIO/HAT Controllers (Raspberry Pi)

| Controller | Series | Features |
|------------|--------|----------|
| **RaZberry 7** | 700 | GPIO connected |
| **Z-Wave.Me UZB** | 700 | Small form factor |

### Regional Compatibility

```markdown
IMPORTANT: Z-Wave devices are region-locked!

- EU: 868.42 MHz
- US: 908.42 MHz
- AU/NZ: 921.42 MHz
- Other regions vary

Do NOT mix regions - devices will not communicate!
```

---

## Z-Wave JS Setup

### Installation Methods

#### Home Assistant Add-on (Recommended)

```markdown
1. Settings > Add-ons > Add-on Store
2. Search "Z-Wave JS"
3. Install "Z-Wave JS" add-on
4. Configure USB device path
5. Start add-on
6. Add Z-Wave JS integration
```

#### Add-on Configuration

```yaml
# Z-Wave JS Add-on Configuration
device: /dev/ttyUSB0  # USB path
network_key: "YOUR_NETWORK_KEY"  # S0 key (generated or custom)
s0_legacy_key: ""  # For migrated networks
s2_access_control_key: ""
s2_authenticated_key: ""
s2_unauthenticated_key: ""
log_level: info
```

### Finding USB Device Path

```bash
# SSH to Home Assistant
# List USB devices
ls -l /dev/serial/by-id/

# Example output:
# usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge-if00-port0 -> ../../ttyUSB0

# Use full path for stability:
# /dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge-if00-port0
```

### Integration Setup

```markdown
1. Settings > Devices & Services
2. Add Integration
3. Search "Z-Wave"
4. Select "Z-Wave JS"
5. Use Z-Wave JS add-on (or external server URL)
6. Complete setup
```

### Z-Wave JS UI Access

```yaml
# Z-Wave JS UI (optional, for advanced management)
# Install "Z-Wave JS UI" add-on for full control panel
# Access via sidebar or http://[ha-ip]:8091
```

---

## Device Pairing

### Inclusion Modes

#### Standard Inclusion (Default)

```markdown
1. Settings > Devices & Services > Z-Wave JS
2. Click "Add Device"
3. Put device in inclusion mode (usually hold button 3x)
4. Device appears and interviews
5. Wait for interview to complete
```

#### SmartStart (Automatic Inclusion)

```markdown
SmartStart devices can be pre-provisioned:

1. Z-Wave JS UI > SmartStart
2. Scan QR code or enter DSK
3. Power on device
4. Device automatically joins network
```

#### S2 Security Inclusion

```markdown
During inclusion, device may request DSK (Device Specific Key):

1. Find DSK on device (sticker/QR code)
2. Enter first 5 digits when prompted
3. Device joins with S2 security
```

### Exclusion (Remove Device)

```markdown
# Proper exclusion
1. Settings > Devices & Services > Z-Wave JS
2. Click device > "Remove device"
3. Follow prompts

# Force remove (device not responding)
1. Z-Wave JS UI > Nodes
2. Select node > "Remove Failed Node"
```

### Device Interview

```yaml
# After inclusion, devices are interviewed to discover capabilities
# Interview status visible in device details

# If interview fails:
# 1. Wake battery device (press button)
# 2. Move device closer temporarily
# 3. Re-interview from Z-Wave JS UI
```

---

## Network Management

### Network Topology

```markdown
Z-Wave mesh structure:

Primary Controller (your USB stick)
    │
    ├── Mains-powered devices (always routing)
    │   ├── Smart plug
    │   ├── Light switch
    │   └── Outlet
    │
    └── Battery devices (sleeping, no routing)
        ├── Door sensor
        ├── Motion sensor
        └── Remote control
```

### Network Heal

```yaml
# Repairs network routes for all devices
# Run after adding/moving devices

# Via Home Assistant
service: zwave_js.refresh_node_info
data:
  entity_id: sensor.any_zwave_entity

# Via Z-Wave JS UI
# Settings > Network > Begin Healing Network
# Best run at night (can take hours)
```

### Route Optimization

```yaml
# Check device routes
# Z-Wave JS UI > Nodes > [Device] > Statistics

# Indicators of routing issues:
# - High "Failed TX" count
# - Low RSSI values
# - RTT > 1000ms

# Solutions:
# 1. Add more mains-powered devices (routers)
# 2. Move device closer to router
# 3. Run network heal
```

### Controller Backup

```markdown
# Z-Wave JS UI > Settings > Backup and Restore

1. Click "Create Backup"
2. Download NVM backup file
3. Store safely

# Restore to new controller:
1. Install new controller
2. Z-Wave JS UI > Backup and Restore
3. Upload backup file
4. Confirm restore
```

---

## Automations & Scenes

### Basic Automation

```yaml
# Light automation with Z-Wave switch
automation:
  - id: zwave_motion_light
    alias: "Z-Wave Motion Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.zwave_motion_sensor
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.zwave_dimmer
        data:
          brightness_pct: 100

  - id: zwave_motion_off
    alias: "Z-Wave Motion Light Off"
    trigger:
      - platform: state
        entity_id: binary_sensor.zwave_motion_sensor
        to: "off"
        for: "00:05:00"
    action:
      - service: light.turn_off
        target:
          entity_id: light.zwave_dimmer
```

### Scene Controller Events

```yaml
# Many Z-Wave scene controllers send events instead of entity states
# Listen to zwave_js_value_notification events

automation:
  - id: scene_controller_button
    alias: "Scene Controller Button Press"
    trigger:
      - platform: event
        event_type: zwave_js_value_notification
        event_data:
          device_id: "abc123"  # Your device ID
          property: "scene"
          value: 1  # Button number
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

### Central Scene Actions

```yaml
# Common scene controller values:
# - KeyPressed: Single press
# - KeyReleased: Button released
# - KeyHeldDown: Hold started
# - KeyPressed2x: Double press
# - KeyPressed3x: Triple press

automation:
  - id: dimmer_scene_control
    alias: "Dimmer Scene Control"
    trigger:
      - platform: event
        event_type: zwave_js_value_notification
        event_data:
          device_id: "your_device_id"
          command_class_name: "Central Scene"
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.value == 'KeyPressed' }}"
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.overhead

          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.value == 'KeyPressed2x' }}"
            sequence:
              - service: scene.turn_on
                target:
                  entity_id: scene.movie_mode

          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.value == 'KeyHeldDown' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: all
                data:
                  brightness_pct: 100
```

### Association Groups

```yaml
# Direct association between devices (no hub involved)
# Z-Wave JS UI > Nodes > Device > Associations

# Example: Link motion sensor directly to light
# Group 2 (Basic Set) -> Light node

# Advantages:
# - Instant response (no HA delay)
# - Works even if HA is down

# Disadvantages:
# - No conditions possible
# - No logging
# - Simple on/off only
```

---

## Device Configuration

### Configuration Parameters

```yaml
# Set device parameters via service
service: zwave_js.set_config_parameter
data:
  entity_id: light.zwave_dimmer
  parameter: 3  # LED indicator mode
  value: 1      # LED on when load off

# Common parameters (device-specific):
# Dimmer ramp rate
# LED indicator behavior
# Motion sensor sensitivity
# Wakeup interval
```

### Device-Specific Examples

#### Aeotec MultiSensor 6

```yaml
# Configuration via service calls
script:
  configure_multisensor:
    sequence:
      # Motion sensitivity (1-5, 1=highest)
      - service: zwave_js.set_config_parameter
        data:
          entity_id: binary_sensor.multisensor_motion
          parameter: 4
          value: 3

      # Motion timeout (seconds)
      - service: zwave_js.set_config_parameter
        data:
          entity_id: binary_sensor.multisensor_motion
          parameter: 3
          value: 240

      # Report temperature changes (0.1°C units)
      - service: zwave_js.set_config_parameter
        data:
          entity_id: sensor.multisensor_temperature
          parameter: 41
          value: 10  # 1.0°C change triggers report
```

#### Fibaro Dimmer 2

```yaml
# Set minimum brightness
service: zwave_js.set_config_parameter
data:
  entity_id: light.fibaro_dimmer
  parameter: 1
  value: 5  # 5% minimum

# Set maximum brightness
service: zwave_js.set_config_parameter
data:
  entity_id: light.fibaro_dimmer
  parameter: 2
  value: 99  # 99% maximum

# Dimming step (1-99%)
service: zwave_js.set_config_parameter
data:
  entity_id: light.fibaro_dimmer
  parameter: 5
  value: 1  # 1% steps
```

#### Inovelli Red Series

```yaml
# LED color when on (0-255, color wheel)
service: zwave_js.set_config_parameter
data:
  entity_id: light.inovelli_switch
  parameter: 13
  value: 170  # Blue

# LED color when off
service: zwave_js.set_config_parameter
data:
  entity_id: light.inovelli_switch
  parameter: 14
  value: 0  # Red

# LED brightness
service: zwave_js.set_config_parameter
data:
  entity_id: light.inovelli_switch
  parameter: 14
  value: 5  # 50% (0-10 scale)
```

---

## Security

### Security Levels

| Level | Encryption | Use Case |
|-------|------------|----------|
| **None** | No encryption | Non-critical devices |
| **S0** | AES-128 | Legacy security |
| **S2 Unauthenticated** | AES-128 + authentication | Basic security |
| **S2 Authenticated** | AES-128 + DSK verification | High security |
| **S2 Access Control** | Highest | Locks, garages |

### Including with S2

```markdown
1. Start inclusion in HA
2. Device prompts for DSK
3. Enter first 5 digits from device label
4. Select security level:
   - Access Control (locks, garage)
   - Authenticated (most devices)
   - Unauthenticated (low risk)
```

### Security Best Practices

```yaml
# Store network keys securely
# Keys are in Z-Wave JS add-on configuration
# Backup these keys separately

# Security recommendations:
# - Locks: S2 Access Control
# - Thermostats: S2 Authenticated
# - Motion sensors: S2 Unauthenticated or None
# - Light switches: None (unless paranoid)
```

---

## Troubleshooting

### Common Issues

#### Device Not Responding

```markdown
## Symptoms
- Entity unavailable
- Commands not executed
- "Node dead" in Z-Wave JS UI

## Solutions
1. Check if device has power
2. For battery devices:
   - Press button to wake
   - Replace battery
3. Try "Ping" in Z-Wave JS UI
4. Check route (Z-Wave JS UI > Statistics)
5. Move closer to controller or add router
6. Re-interview device
7. Exclude and re-include as last resort
```

#### Slow Response

```markdown
## Causes
- Poor mesh routing
- Network congestion
- Interference
- Long route to controller

## Solutions
1. Add more mains-powered devices
2. Run network heal
3. Check for interference sources
4. Review route in Z-Wave JS UI
```

#### Ghost Nodes

```markdown
## Symptoms
- Node shows as "Dead" or "Unknown"
- Cannot exclude
- Slows down network

## Solutions
1. Z-Wave JS UI > Nodes
2. Select ghost node
3. "Remove Failed Node"
4. If fails, try "Replace Failed Node" then remove
```

#### Inclusion Fails

```markdown
## Troubleshooting Steps
1. Ensure device not already included
   - Try exclusion first
2. Move device close to controller
3. Check device battery
4. Factory reset device
5. Try multiple times
6. Check for region mismatch
```

### Network Diagnostics

```yaml
# Check device health via template sensor
template:
  - sensor:
      - name: "Z-Wave Network Health"
        state: >
          {% set dead = states.zwave | selectattr('state', 'eq', 'dead') | list | length %}
          {% set total = states.zwave | list | length %}
          {% if dead == 0 %}
            Healthy
          {% elif dead < 3 %}
            Warning ({{ dead }} dead)
          {% else %}
            Critical ({{ dead }} dead)
          {% endif %}
```

### Debug Logging

```yaml
# Enable Z-Wave debug logging
logger:
  default: info
  logs:
    homeassistant.components.zwave_js: debug
    zwave_js_server: debug
```

---

## Best Practices

### Network Design

```markdown
## Placement Guidelines
1. Controller central to home
2. Router devices (mains-powered) every 10-15m
3. Avoid long single-hop chains
4. Battery devices near routers

## Device Ratio
- Aim for 1 router per 3-4 battery devices
- More routers = more reliability
```

### Device Selection

```markdown
## Recommendations
1. Buy 700/800 series devices for new installs
2. Check certification for your region
3. Prefer S2-capable devices
4. Read reviews for HA compatibility
5. Consider parameter configurability
```

### Maintenance Schedule

```yaml
# Regular maintenance automation
automation:
  - id: zwave_monthly_maintenance
    alias: "Z-Wave Monthly Maintenance"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 1 }}"  # First of month
    action:
      - service: zwave_js.heal_network
      - service: notify.admin
        data:
          message: "Z-Wave network heal started"
```

### Migration from Legacy Z-Wave

```markdown
## From deprecated Z-Wave integration
1. Create NVM backup of controller
2. Note all device parameters
3. Remove old integration
4. Install Z-Wave JS add-on
5. Restore NVM backup to controller
6. Add Z-Wave JS integration
7. Re-configure device parameters
```
