# Matter Integration Reference

## Table of Contents
- [Overview](#overview)
- [Matter vs Traditional Protocols](#matter-vs-traditional-protocols)
- [Requirements](#requirements)
- [Setup & Configuration](#setup--configuration)
- [Device Commissioning](#device-commissioning)
- [Thread Border Router](#thread-border-router)
- [Bridge Mode](#bridge-mode)
- [Automations](#automations)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

### What is Matter?

Matter is a unified smart home protocol developed by the Connectivity Standards Alliance (CSA). It provides a common language for smart home devices to communicate, regardless of manufacturer.

### Key Features

| Feature | Description |
|---------|-------------|
| **Interoperability** | Works across platforms (Apple, Google, Amazon, Samsung) |
| **Local Control** | No cloud required for basic operations |
| **Security** | Built-in encryption and authentication |
| **Multi-Admin** | Device can be controlled by multiple ecosystems |
| **IPv6** | Modern network protocol support |

### Transport Protocols

| Protocol | Use Case | Range |
|----------|----------|-------|
| **Thread** | Low-power devices (sensors, locks) | Mesh network |
| **WiFi** | High-bandwidth devices (cameras) | Standard WiFi |
| **Ethernet** | Stationary devices (hubs, bridges) | Wired |

### Supported Device Types

- Lights and switches
- Smart plugs and outlets
- Thermostats and HVAC
- Door locks
- Sensors (motion, contact, temperature)
- Window coverings
- Fans
- Bridges (Hue, IKEA, etc.)

---

## Matter vs Traditional Protocols

| Aspect | Matter | Zigbee | Z-Wave | WiFi |
|--------|--------|--------|--------|------|
| **Interoperability** | Excellent | Limited | Limited | Varies |
| **Cloud dependency** | Optional | Optional | Optional | Often required |
| **Setup complexity** | Moderate | High | High | Low |
| **Multi-platform** | Yes | No | No | Sometimes |
| **Power usage** | Thread: Low, WiFi: High | Low | Medium | High |
| **Mesh support** | Thread: Yes | Yes | Yes | No |
| **Maturity** | New (2022+) | Mature | Mature | Mature |

### When to Use Matter

- New smart home setup
- Multi-platform household (Apple + Google + HA)
- Desire for local-first control
- Future-proofing investment

### When to Use Traditional

- Existing Zigbee/Z-Wave investment
- Specific device requirements
- Advanced configuration needs
- Better device selection (for now)

---

## Requirements

### Home Assistant Requirements

```markdown
## Minimum Requirements
- Home Assistant 2022.12 or later
- Home Assistant OS, Supervised, or Container
- Python 3.10+

## Recommended
- Home Assistant OS on dedicated hardware
- Yellow, Green, or compatible Thread border router
- SSD storage
```

### Hardware Options

#### Thread Border Routers

| Device | Thread Support | Notes |
|--------|---------------|-------|
| **Home Assistant Yellow** | Built-in | Recommended |
| **Home Assistant SkyConnect** | Yes (via firmware) | USB dongle |
| **Apple TV 4K (2021+)** | Yes | Also Apple Home controller |
| **Apple HomePod Mini** | Yes | Also Apple Home controller |
| **Google Nest Hub (2nd gen)** | Yes | Also Google Home controller |
| **Nanoleaf Shapes** | Yes | Light panels |
| **Eve Energy (Thread)** | Thread device | |

#### Matter Controllers

Home Assistant can be a Matter controller alongside:
- Apple Home
- Google Home
- Amazon Alexa
- Samsung SmartThings

---

## Setup & Configuration

### Enable Matter Integration

```markdown
## Via UI
1. Settings > Devices & Services
2. Add Integration
3. Search "Matter"
4. Click "Matter (BETA)"
5. Follow setup wizard

## First Setup
- Integration uses Matter Server add-on
- Server handles Matter protocol
- Auto-installs on Home Assistant OS
```

### Matter Server Add-on

```yaml
# Automatic with Home Assistant OS
# Manual for Container/Supervised:

# docker-compose.yml
services:
  matter-server:
    image: ghcr.io/home-assistant-libs/python-matter-server:stable
    container_name: matter-server
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./matter-server:/data
```

### Configuration Options

```yaml
# Through UI: Settings > Devices & Services > Matter > Configure

# Options:
# - Use Thread border router discovery
# - Matter Server URL (for external server)
```

---

## Device Commissioning

### Commissioning Process

```markdown
## Step 1: Put Device in Pairing Mode
- Usually: Hold button for 5-10 seconds
- Check device manual for specific instructions
- Device LED should indicate pairing mode

## Step 2: Commission in Home Assistant
1. Settings > Devices & Services
2. Click "+ Add Integration"
3. Select "Add Matter device"
4. Scan QR code OR enter manual code
5. Wait for commissioning to complete

## Step 3: Verify
- Device appears in Matter integration
- Entities created for device features
- Test basic control
```

### QR Code vs Manual Code

```markdown
## QR Code (Preferred)
- Contains all commissioning information
- Found on device, packaging, or app
- Scan with HA Companion app or webcam

## Manual Pairing Code
- 11-digit or 21-digit code
- Format: XXXX-XXX-XXXX or XXX-XXXX-XXXX
- Found on device label
```

### Commission with Thread

```markdown
## Thread Device Commissioning
1. Ensure Thread border router is active
2. Put device in pairing mode
3. Commission via Matter integration
4. Device automatically joins Thread network
5. No additional WiFi credentials needed

## Check Thread Network
- Settings > Devices & Services > Thread
- View Thread network topology
- See connected Thread devices
```

### Multi-Admin Setup

```markdown
## Share Device with Other Platforms
Matter devices can belong to multiple controllers:

1. Device > "..." menu
2. "Share device"
3. Generate sharing code
4. Use code in other platform (Apple Home, Google Home)

## Notes
- Device remains in HA
- Both platforms can control
- Local control preserved
```

---

## Thread Border Router

### What is Thread?

Thread is a low-power mesh networking protocol designed for IoT devices. Matter uses Thread for battery-powered and low-bandwidth devices.

### Thread Network Setup

```markdown
## Automatic (Home Assistant Yellow/SkyConnect)
1. Insert SkyConnect or use Yellow
2. Thread integration auto-discovers
3. Thread network created automatically

## Check Thread Status
Settings > Devices & Services > Thread

## Thread Network Info
- Network Name: Displayed in settings
- Extended PAN ID: Unique network identifier
- Active Router Count: Mesh nodes
```

### Thread Topology

```
Thread Border Router (Yellow/SkyConnect)
    │
    ├── Router Nodes (mains-powered Matter devices)
    │   ├── Eve Energy
    │   └── Nanoleaf Bulb
    │
    └── End Devices (battery devices)
        ├── Eve Door Sensor
        └── Eve Motion Sensor
```

### Multiple Border Routers

```markdown
## Benefits
- Redundancy if one fails
- Better coverage
- Load distribution

## Setup
- Each border router joins same Thread network
- Automatic credential sharing
- Devices use nearest router

## Compatible Border Routers
Can coexist:
- Home Assistant (Yellow/SkyConnect)
- Apple TV/HomePod
- Google Nest Hub
- Nanoleaf bulbs
```

---

## Bridge Mode

### Matter Bridges

Existing smart home systems can expose devices to Matter via bridges.

### Philips Hue Bridge

```markdown
## Enable Matter on Hue
1. Open Hue app
2. Settings > Smart Home
3. Enable Matter pairing
4. Generate QR code

## Add to Home Assistant
1. Add Matter device
2. Scan Hue bridge QR code
3. Hue lights appear as Matter devices

## Notes
- Hue bridge required (not direct bulb)
- Some features may be limited
- Both Hue and Matter control work
```

### IKEA DIRIGERA Hub

```markdown
## Enable Matter
1. IKEA Home smart app
2. Settings > Integrations
3. Add to Matter-enabled app
4. Generate pairing code

## Supported Devices
- TRÅDFRI bulbs
- STYRBAR remotes
- VINDSTYRKA air quality sensor
```

### Other Bridges

| Bridge | Matter Support |
|--------|---------------|
| Aqara Hub M2 | Yes |
| Aqara Hub M3 | Yes |
| SwitchBot Hub 2 | Yes |
| Meross Smart Hub | Yes |
| TP-Link Tapo Hub | Coming |

---

## Automations

### Basic Automation

```yaml
automation:
  - id: matter_light_motion
    alias: "Matter Light - Motion Activated"
    trigger:
      - platform: state
        entity_id: binary_sensor.matter_motion
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.matter_bulb

  - id: matter_light_off
    alias: "Matter Light - Motion Timeout"
    trigger:
      - platform: state
        entity_id: binary_sensor.matter_motion
        to: "off"
        for: "00:05:00"
    action:
      - service: light.turn_off
        target:
          entity_id: light.matter_bulb
```

### Multi-Platform Scene

```yaml
# Scene that works regardless of Matter device controller
scene:
  - name: "Movie Mode"
    entities:
      # Matter lights (may be controlled by multiple platforms)
      light.living_room_matter:
        state: on
        brightness: 50
      light.tv_backlight_matter:
        state: on
        brightness: 30
        rgb_color: [255, 147, 41]
```

### Thread Device Battery Monitor

```yaml
# Monitor Thread device batteries
automation:
  - id: matter_battery_alert
    alias: "Matter Device Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id:
          - sensor.eve_door_battery
          - sensor.eve_motion_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "Low Battery"
          message: "{{ trigger.to_state.attributes.friendly_name }} battery at {{ trigger.to_state.state }}%"
```

---

## Troubleshooting

### Common Issues

#### Device Won't Commission

```markdown
## Checklist
1. Device in pairing mode? (LED indicator)
2. QR code/manual code correct?
3. Device on same network/Thread?
4. Matter Server running?

## Solutions
- Factory reset device
- Try manual pairing code instead of QR
- Restart Matter Server add-on
- Check Home Assistant logs
```

#### Device Unavailable

```markdown
## Causes
- Device offline
- Thread network issues
- WiFi connectivity (for WiFi Matter devices)
- Matter Server issue

## Solutions
1. Check device power
2. Restart device
3. Check Thread network status
4. Restart Matter Server
5. Re-commission device
```

#### Thread Network Issues

```markdown
## Symptoms
- Thread devices intermittent
- Long response times
- Devices not joining

## Solutions
1. Check border router status
2. Add more router nodes (mains-powered devices)
3. Reduce distance between devices
4. Check for interference (2.4GHz)
```

### Debug Logging

```yaml
# Enable Matter debug logging
logger:
  default: info
  logs:
    homeassistant.components.matter: debug
    matter_server: debug
```

### Matter Server Logs

```bash
# Home Assistant OS
ha addons logs core_matter_server

# Docker
docker logs matter-server
```

### Re-commission Device

```markdown
1. Remove device from Home Assistant
   - Devices & Services > Matter > Device > Delete
2. Factory reset device
3. Add device again
4. Re-commission from scratch
```

---

## Best Practices

### Network Design

```markdown
## Thread Network
- Place border router centrally
- Add mains-powered devices as routers
- Avoid more than 3 hops to border router
- Multiple border routers for redundancy

## WiFi Matter Devices
- Ensure strong WiFi coverage
- Use 2.4GHz for compatibility
- Static IP or DHCP reservation recommended
```

### Device Selection

```markdown
## Recommended First Devices
1. Smart plugs (easy setup, act as Thread routers)
2. Light bulbs (common, well-supported)
3. Sensors (showcase Thread low-power)

## Check Before Buying
- "Works with Matter" certification
- Thread vs WiFi support
- Home Assistant compatibility list
```

### Multi-Platform Tips

```markdown
## Best Practices
1. Commission to Home Assistant first
2. Share to other platforms as needed
3. Use HA for automation, others for voice
4. Keep firmware updated on all platforms

## Avoid
- Commissioning same device to HA multiple times
- Removing from one platform to add to another (unless necessary)
- Mixing very old and new Matter firmware
```

### Security

```markdown
## Matter Security Features
- End-to-end encryption
- Device attestation
- Secure commissioning

## Recommendations
1. Only commission devices you trust
2. Don't share pairing codes publicly
3. Keep Home Assistant updated
4. Regularly audit connected devices
```

---

## Matter Device Support Status

### Well Supported

| Type | Examples |
|------|----------|
| Lights | Eve, Nanoleaf, Philips Hue (bridge) |
| Plugs | Eve Energy, Meross, TP-Link |
| Sensors | Eve Door, Eve Motion |
| Climate | Ecobee, some Nest |

### Limited Support

| Type | Notes |
|------|-------|
| Locks | Basic lock/unlock, some advanced features missing |
| Cameras | Not yet in Matter spec |
| Vacuum | Not yet in Matter spec |
| Garage | Limited implementations |

### Coming Soon

- Media players
- Robot vacuums
- Cameras
- Appliances

---

## Resources

- [Home Assistant Matter Documentation](https://www.home-assistant.io/integrations/matter/)
- [Matter Specification](https://csa-iot.org/all-solutions/matter/)
- [Thread Group](https://www.threadgroup.org/)
- [Compatible Device List](https://www.home-assistant.io/integrations/matter/#known-working-devices)
