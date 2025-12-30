# Tuya Integration

Complete guide for integrating Tuya and Tuya-based smart devices with Home Assistant.

---

## Overview

Tuya is a major IoT platform powering thousands of smart device brands. Home Assistant supports Tuya through:

1. **Official Tuya Integration** - Cloud-based, official support
2. **Local Tuya (HACS)** - Local control, no cloud dependency

### Cloud vs Local Comparison

| Feature | Official Tuya | Local Tuya (HACS) |
|---------|---------------|-------------------|
| **Setup Complexity** | Medium | High |
| **Cloud Required** | Yes | No (after setup) |
| **Latency** | 1-3 seconds | Instant |
| **Privacy** | Data via cloud | Local only |
| **Reliability** | Depends on cloud | Very reliable |
| **Device Support** | Good | Varies by device |
| **Updates** | Automatic | Manual HACS |

**Recommendation:** Start with official integration. Switch to Local Tuya for critical devices requiring instant response.

---

## Official Tuya Integration

### Prerequisites

1. **Tuya IoT Platform Account** (not just Smart Life app)
2. **Tuya Developer Account**
3. **Cloud Project** with API access

### Step 1: Create Tuya Developer Account

1. Go to [Tuya IoT Platform](https://iot.tuya.com/)
2. Register for a developer account
3. Complete email verification

### Step 2: Create Cloud Project

1. Click **Cloud** > **Development** > **Create Cloud Project**
2. Configure:
   - **Project Name**: Home Assistant
   - **Industry**: Smart Home
   - **Development Method**: Smart Home
   - **Data Center**: Choose nearest to you

3. Note your:
   - **Client ID** (Access ID)
   - **Client Secret** (Access Secret)

### Step 3: Link API Products

In your cloud project, authorize these APIs:
- **IoT Core**
- **Authorization Token Management**
- **Smart Home Scene Linkage**
- **Smart Home Device Management**
- **Smart Home Data Service**
- **Device Status Notification**

### Step 4: Link Devices

1. In cloud project, go to **Devices** > **Link Tuya App Account**
2. Click **Add App Account**
3. Scan QR code with **Tuya Smart** or **Smart Life** app
4. Verify devices appear in the list

### Step 5: Add Integration to HA

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Tuya**
3. Enter:
   - **Country Code** (from app)
   - **Client ID**
   - **Client Secret**
4. Authenticate via QR code scan

### Configuration

```yaml
# No YAML needed - configured via UI

# Optional: Polling interval in configuration.yaml
tuya:
  polling_interval: 60  # seconds, default 60
```

---

## Local Tuya (HACS)

### Installation

1. Install [HACS](https://hacs.xyz/) if not already installed
2. In HACS, search for **Local Tuya**
3. Install and restart Home Assistant

### Getting Device Local Keys

The local key is essential for local control. Methods to obtain:

#### Method 1: Tuya IoT Platform (Recommended)

1. In your Tuya cloud project
2. Go to **Devices** > **All Devices**
3. Click on device > **Get Device Debugging Key**
4. Or use **API Explorer** > **Get Device Local Key**

#### Method 2: Using tinytuya

```bash
# Install tinytuya
pip install tinytuya

# Run wizard
python -m tinytuya wizard

# Follow prompts with your Tuya credentials
# Outputs JSON with all device keys
```

#### Method 3: Android ADB Method

```bash
# Requires rooted device or emulator
# Extract from Tuya/Smart Life app data
# Not recommended - complex process
```

### Adding Devices to Local Tuya

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **LocalTuya**
3. Choose **Add a new device**
4. Enter:
   - **Device ID** (from IoT platform)
   - **IP Address** (find via router or Tuya app)
   - **Local Key**
   - **Protocol Version** (usually 3.3)

### Device Configuration

Each device type needs different Data Points (DPs):

#### Smart Plug/Switch

```yaml
# Common DPs for switches:
# DP 1: Switch (on/off)
# DP 2: Countdown timer
# DP 9: Countdown remaining

# Energy monitoring (if supported):
# DP 17: Current (mA)
# DP 18: Power (W * 10)
# DP 19: Voltage (V * 10)
# DP 20: Energy (kWh * 100)
```

#### Light Bulb

```yaml
# Common DPs for lights:
# DP 20: Switch (on/off)
# DP 21: Mode (white/colour/scene/music)
# DP 22: Brightness (10-1000)
# DP 23: Color temperature (0-1000)
# DP 24: Color (HSV format)
# DP 25: Scene data
# DP 26: Countdown
```

#### Cover/Blind

```yaml
# Common DPs for covers:
# DP 1: Control (open/close/stop)
# DP 2: Percent control (0-100)
# DP 3: Current position (0-100)
# DP 7: Work state (opening/closing/stopped)
```

#### Climate/Thermostat

```yaml
# Common DPs:
# DP 1: Switch (on/off)
# DP 2: Set temperature (scaled)
# DP 3: Current temperature (scaled)
# DP 4: Mode (auto/heat/cool)
# DP 5: Fan speed
# DP 6: Eco mode
```

### Protocol Versions

| Version | Usage |
|---------|-------|
| 3.1 | Older devices |
| 3.3 | Most common |
| 3.4 | Newer devices |
| 3.5 | Latest (2024+) |

Try 3.3 first, then 3.4 if it doesn't work.

---

## Device Types

### Smart Plugs

```yaml
# Basic on/off automation
automation:
  - alias: "Turn off plug at midnight"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.tuya_smart_plug

# Power monitoring automation
automation:
  - alias: "High power alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tuya_plug_power
        above: 2000  # Watts
    action:
      - service: notify.mobile_app
        data:
          message: "High power consumption detected!"
```

### Smart Bulbs

```yaml
# Color and brightness control
automation:
  - alias: "Evening lighting"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.tuya_bulb
        data:
          brightness_pct: 70
          color_temp_kelvin: 2700  # Warm white
          transition: 30

# Color scene
script:
  party_mode:
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.tuya_bulb
        data:
          rgb_color: [255, 0, 0]
          brightness_pct: 100
      - delay: "00:00:02"
      - service: light.turn_on
        target:
          entity_id: light.tuya_bulb
        data:
          rgb_color: [0, 255, 0]
```

### Smart Covers/Blinds

```yaml
# Position control
automation:
  - alias: "Open blinds at sunrise"
    trigger:
      - platform: sun
        event: sunrise
        offset: "00:30:00"
    action:
      - service: cover.set_cover_position
        target:
          entity_id: cover.tuya_blind
        data:
          position: 100  # Fully open

# Close based on sun elevation
automation:
  - alias: "Close blinds when sun is strong"
    trigger:
      - platform: numeric_state
        entity_id: sun.sun
        attribute: elevation
        above: 60
    action:
      - service: cover.set_cover_position
        target:
          entity_id: cover.tuya_blind
        data:
          position: 30  # Partially closed
```

### Thermostats

```yaml
# Climate control
automation:
  - alias: "Heating schedule"
    trigger:
      - platform: time
        at: "06:30:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.tuya_thermostat
        data:
          temperature: 21
          hvac_mode: heat

# Away mode
automation:
  - alias: "Away - reduce heating"
    trigger:
      - platform: state
        entity_id: group.family
        to: "not_home"
        for: "00:30:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.tuya_thermostat
        data:
          temperature: 16
```

### Sensors

```yaml
# Temperature/humidity sensors
automation:
  - alias: "Humidity alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tuya_humidity
        above: 70
        for: "00:30:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.dehumidifier

# Door/window sensors
automation:
  - alias: "Door left open"
    trigger:
      - platform: state
        entity_id: binary_sensor.tuya_door
        to: "on"
        for: "00:10:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Door has been open for 10 minutes"
```

---

## Scenes and Integration

### Using Tuya Scenes

Tuya scenes created in the app are available as buttons:

```yaml
# Trigger Tuya scene
automation:
  - alias: "Good night via Tuya"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: button.press
        target:
          entity_id: button.tuya_goodnight_scene
```

### Combining with Other Integrations

```yaml
# Sync Tuya with other systems
automation:
  - alias: "Sync Tuya light with Hue"
    trigger:
      - platform: state
        entity_id: light.hue_living_room
    action:
      - service: light.turn_{{ trigger.to_state.state }}
        target:
          entity_id: light.tuya_living_room
```

---

## Troubleshooting

### Official Integration Issues

#### Devices Not Appearing

1. **Check device linking** in Tuya IoT Platform
2. **Verify API subscriptions** are active
3. **Re-link app account** in cloud project
4. **Check data center** matches your region

#### Authentication Errors

```yaml
# Common fixes:
# 1. Regenerate Client ID/Secret
# 2. Check API subscriptions (may expire)
# 3. Verify country code matches app
# 4. Re-authenticate via QR code
```

#### Slow Response

```yaml
# Cloud latency is normal (1-3 seconds)
# For instant response, use Local Tuya

# Adjust polling interval:
tuya:
  polling_interval: 30  # Faster updates, more API calls
```

### Local Tuya Issues

#### Device Not Responding

1. **Verify IP address** hasn't changed (use DHCP reservation)
2. **Check local key** is correct
3. **Try different protocol version**
4. **Ensure device is on same network**

#### Wrong Entity Type

```yaml
# Incorrect DP configuration
# 1. Find correct DPs using tinytuya:
python -m tinytuya scan

# 2. Check device debug output
# 3. Reconfigure with correct DPs
```

#### Connection Issues

```yaml
# Firewall may block local communication
# Ensure UDP port 6666-6668 accessible

# Device may need cloud for initial setup
# Connect to cloud first, then switch to local
```

### Finding DPs for Unknown Devices

```python
# Using tinytuya to discover DPs
import tinytuya

d = tinytuya.Device('DEVICE_ID', 'IP_ADDRESS', 'LOCAL_KEY')
d.set_version(3.3)

# Get current status
data = d.status()
print(data)

# Monitor changes
d.set_socketPersistent(True)
while True:
    data = d.receive()
    if data:
        print(data)
```

---

## Best Practices

### Network Setup

```yaml
# 1. Use static IP or DHCP reservations for Tuya devices
# 2. Create separate IoT VLAN if possible
# 3. Block internet access for local-only devices (after setup)
# 4. Keep devices on 2.4GHz WiFi (required by most Tuya devices)
```

### Security

```yaml
# 1. Use unique Tuya account for Home Assistant
# 2. Don't share local keys
# 3. Consider blocking cloud access for critical devices
# 4. Regularly check for firmware updates
```

### Reliability

```yaml
# 1. Use Local Tuya for critical automations
# 2. Keep official integration as backup
# 3. Monitor device availability
# 4. Test automations after HA updates
```

### Entity Naming

```yaml
# Tuya creates entities with long IDs
# Rename for clarity:
# switch.bf123456789abc_1 → switch.living_room_lamp
# sensor.bf123456789abc_power → sensor.living_room_lamp_power
```

---

## Common Tuya Brands

Many brands use Tuya platform:

| Brand | Product Types |
|-------|---------------|
| **Gosund** | Plugs, bulbs |
| **Teckin** | Plugs, power strips |
| **Treatlife** | Switches, dimmers |
| **Avatar Controls** | Plugs, bulbs |
| **Merkury** | Bulbs |
| **Globe Electric** | Bulbs, plugs |
| **Feit Electric** | Bulbs |
| **Wyze** | Bulbs (early models) |
| **Nedis** | Various |
| **LSC Smart Connect** | Various |
| **Calex** | Bulbs |
| **Deltaco** | Various |

Check if your device uses Tuya by:
1. App requires Tuya/Smart Life
2. Device follows Tuya pairing process
3. Search device on [templates.blakadder.com](https://templates.blakadder.com/)

---

## Reference

### Useful Links

- [Tuya Integration Docs](https://www.home-assistant.io/integrations/tuya/)
- [Local Tuya GitHub](https://github.com/rospogriern/localtuya)
- [Tuya IoT Platform](https://iot.tuya.com/)
- [tinytuya Documentation](https://github.com/jasonacox/tinytuya)

### Common DPs by Device Type

| Device | DP | Function |
|--------|----|-----------|
| Switch | 1 | On/Off |
| Light | 20 | On/Off |
| Light | 21 | Mode |
| Light | 22 | Brightness |
| Light | 23 | Color Temp |
| Light | 24 | Color |
| Cover | 1 | Control |
| Cover | 2 | Position |
| Climate | 1 | On/Off |
| Climate | 2 | Target Temp |
| Climate | 3 | Current Temp |
| Plug | 17 | Current |
| Plug | 18 | Power |
| Plug | 19 | Voltage |
