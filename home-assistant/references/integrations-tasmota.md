# Tasmota Integration

Complete guide for integrating Tasmota-flashed devices with Home Assistant.

---

## Overview

Tasmota is open-source firmware for ESP8266/ESP32 devices, providing local control without cloud dependency.

### Why Use Tasmota?

| Feature | Benefit |
|---------|---------|
| **Local Control** | No cloud, instant response |
| **Open Source** | Full transparency, community support |
| **Customizable** | Rules, scripts, sensors |
| **MQTT Native** | Perfect HA integration |
| **OTA Updates** | Easy firmware updates |
| **Cost Effective** | Flash cheap devices |

---

## Integration Methods

### Method 1: Tasmota Integration (Native)

Home Assistant has native Tasmota integration via MQTT discovery.

```yaml
# Prerequisites:
# 1. MQTT broker running
# 2. Tasmota device configured for MQTT

# Enable discovery in Tasmota console:
SetOption19 0   # Use new discovery format
```

### Method 2: MQTT Integration

Manual MQTT configuration for full control.

```yaml
# See integrations-mqtt.md for MQTT setup
```

---

## Initial Setup

### Flashing Tasmota

#### OTA Flash (Easy - if supported)

1. Use **tuya-convert** for Tuya devices
2. Use **Tasmotizer** tool
3. Follow device-specific guides

#### Serial Flash (Reliable)

Required hardware:
- USB-to-Serial adapter (FTDI, CH340, CP2102)
- Jumper wires
- 3.3V power supply (not 5V!)

Steps:
1. Connect GPIO0 to GND
2. Connect TX, RX, GND, 3.3V
3. Use **Tasmotizer** or **esptool**
4. Flash firmware
5. Disconnect GPIO0, reboot

### Initial Configuration

After flashing:
1. Connect to **tasmota-XXXX** WiFi
2. Go to 192.168.4.1
3. Configure WiFi credentials
4. Device reboots on your network

### MQTT Configuration

In Tasmota web UI > Configuration > MQTT:

```
Host: 192.168.1.100        # Your MQTT broker
Port: 1883
Client: tasmota_%06X       # Unique per device
User: mqtt_user
Password: mqtt_password
Topic: kitchen_light       # Friendly name
Full Topic: %prefix%/%topic%/
```

### Enable Home Assistant Discovery

In Tasmota console:

```
# Enable HA discovery
SetOption19 0

# Set device name for discovery
DeviceName Kitchen Light

# Set friendly name
FriendlyName1 Kitchen Light
```

---

## Device Templates

Templates define GPIO pin assignments for specific devices.

### Applying a Template

In Tasmota console:

```
# Apply template (example: Sonoff Basic)
Template {"NAME":"Sonoff Basic","GPIO":[17,255,255,255,255,0,0,0,21,56,0,0,0],"FLAG":0,"BASE":1}
Module 0
```

### Finding Templates

Use [Tasmota Devices Repository](https://templates.blakadder.com/) to find templates for your device.

### Common Device Templates

```json
// Sonoff Basic R2
{"NAME":"Sonoff Basic","GPIO":[17,255,255,255,0,0,0,0,21,56,0,0,0],"FLAG":0,"BASE":1}

// Sonoff S31 (with power monitoring)
{"NAME":"Sonoff S31","GPIO":[17,145,0,146,0,0,0,0,21,56,0,0,0],"FLAG":0,"BASE":41}

// Generic RGB Bulb
{"NAME":"RGB Bulb","GPIO":[0,0,0,0,0,37,0,0,38,39,0,40,0],"FLAG":0,"BASE":18}

// Tuya Smart Plug
{"NAME":"Tuya Plug","GPIO":[0,0,0,0,52,21,0,0,0,17,0,0,0],"FLAG":0,"BASE":18}
```

---

## Device Types

### Switches and Relays

```yaml
# Sonoff Basic example
# Discovered automatically as switch.kitchen_light

automation:
  - alias: "Turn on kitchen light"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.kitchen_light
```

### Lights (PWM/RGB)

```yaml
# RGB bulb discovered as light.rgb_bulb

automation:
  - alias: "Set warm white at night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.tasmota_bulb
        data:
          brightness_pct: 30
          color_temp_kelvin: 2700
```

### Power Monitoring Plugs

```yaml
# Sonoff POW or S31 - creates:
# - switch.plug
# - sensor.plug_power
# - sensor.plug_voltage
# - sensor.plug_current
# - sensor.plug_energy_today

automation:
  - alias: "Appliance finished"
    trigger:
      - platform: numeric_state
        entity_id: sensor.washing_machine_power
        below: 5
        for: "00:02:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Washing machine finished!"
```

### Temperature/Humidity Sensors

```yaml
# DHT22 or BME280 connected to Tasmota device
# Creates sensor entities automatically

automation:
  - alias: "High humidity alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tasmota_humidity
        above: 70
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.dehumidifier
```

### Motion Sensors (PIR)

```yaml
# PIR connected to Tasmota GPIO
# Creates binary_sensor via MQTT

binary_sensor:
  - platform: mqtt
    name: "Motion Sensor"
    state_topic: "tasmota/motion/stat/POWER"
    payload_on: "ON"
    payload_off: "OFF"
    device_class: motion
```

---

## Tasmota Rules

Rules enable device-level automation without Home Assistant.

### Rule Syntax

```
Rule1 ON <trigger> DO <command> ENDON
```

### Common Rules

```
# Rule 1: Auto-off after 5 minutes
Rule1 ON Power1#state=1 DO RuleTimer1 300 ENDON ON Rules#Timer=1 DO Power1 off ENDON
Rule1 1

# Rule 2: Button double-press for scene
Rule2 ON Button1#state=3 DO Publish cmnd/living_room/scene night ENDON
Rule2 1

# Rule 3: Motion sensor with timeout
Rule1 ON Switch1#state=1 DO Backlog Power1 1; RuleTimer1 120 ENDON ON Rules#Timer=1 DO Power1 0 ENDON
Rule1 1

# Rule 4: Temperature-based control
Rule1 ON BME280#Temperature>25 DO Power1 1 ENDON ON BME280#Temperature<23 DO Power1 0 ENDON
Rule1 1
```

### Enable Rules

```
Rule1 1    # Enable Rule1
Rule1 0    # Disable Rule1
Rule1      # Show Rule1
```

---

## MQTT Topics

### Topic Structure

```
%prefix%/%topic%/%command%

# Prefixes:
cmnd/    # Commands to device
stat/    # Status from device
tele/    # Telemetry (periodic)
```

### Common Topics

```yaml
# Turn on/off
Topic: cmnd/kitchen_light/POWER
Payload: ON / OFF / TOGGLE

# Get status
Topic: cmnd/kitchen_light/STATUS
Payload: (empty)

# Response (stat topic)
Topic: stat/kitchen_light/POWER
Payload: ON / OFF

# Telemetry (every 5 minutes default)
Topic: tele/kitchen_light/STATE
Payload: {"Time":"...","Uptime":"...","POWER":"ON",...}
```

### MQTT Automation Examples

```yaml
# Manual MQTT control
automation:
  - alias: "Toggle via MQTT"
    trigger:
      - platform: state
        entity_id: input_boolean.toggle_light
    action:
      - service: mqtt.publish
        data:
          topic: "cmnd/kitchen_light/POWER"
          payload: "TOGGLE"

# Listen to button events
automation:
  - alias: "Tasmota button press"
    trigger:
      - platform: mqtt
        topic: "stat/tasmota_switch/BUTTON1"
        payload: "SINGLE"
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

---

## Console Commands

### Essential Commands

```
# Network
Status 5              # Network status
IPAddress1 x.x.x.x    # Set static IP
Restart 1             # Restart device

# MQTT
MqttHost x.x.x.x      # Set MQTT broker
MqttUser username     # Set MQTT user
MqttPassword pass     # Set MQTT password
Topic new_topic       # Change topic

# GPIO
GPIO                  # Show GPIO assignment
Template              # Show current template
Module 0              # Use template

# Power
Power                 # Show power state
Power ON              # Turn on
Power OFF             # Turn off
Power TOGGLE          # Toggle

# Settings
SetOption19 0         # HA discovery format
SetOption57 1         # Index relay names
Backlog cmd1;cmd2     # Run multiple commands
```

### Telemetry Configuration

```
# Telemetry period (seconds)
TelePeriod 60         # Report every 60 seconds

# Sensor reporting
SensorRetain 1        # Retain sensor messages
```

---

## Troubleshooting

### Device Not Discovered

1. **Check MQTT connection** in Tasmota console
2. **Verify SetOption19** is 0 (new format)
3. **Check HA MQTT integration** is running
4. **Look for discovery messages** in MQTT Explorer

```
# In Tasmota console:
Status 6    # MQTT status
```

### Connection Issues

```
# Check WiFi
Status 5    # Network status
WifiConfig  # WiFi configuration

# Check MQTT
MqttHost    # Show MQTT host
MqttClient  # Show client ID
```

### Device Randomly Disconnecting

```
# Increase MQTT keepalive
MqttKeepAlive 30

# Set static IP
IPAddress1 192.168.1.100
IPAddress2 192.168.1.1      # Gateway
IPAddress3 255.255.255.0    # Subnet
IPAddress4 192.168.1.1      # DNS
```

### Wrong Entity Type

```
# Force device type for HA discovery
DeviceName "My Light"
SetOption30 1    # Use as light instead of switch

# Or configure template correctly
```

---

## Advanced Features

### Berry Scripting (ESP32)

For ESP32 devices, Berry scripting provides advanced automation:

```berry
# autoexec.be - runs on boot
import mqtt

def on_mqtt_message(topic, payload)
  if topic == 'cmnd/test'
    tasmota.cmd('Power TOGGLE')
  end
end

mqtt.subscribe('cmnd/test', on_mqtt_message)
```

### Web Sensors

Add I2C/SPI sensors:

```
# BME280 temperature/humidity/pressure
I2CDriver 15    # Enable BME280

# ADS1115 ADC
I2CDriver 2     # Enable ADS1115
```

### Display Support

```
# SSD1306 OLED
DisplayModel 2
DisplayMode 0

# Show text
DisplayText [z] [f1] Hello World
```

---

## Best Practices

### Naming Convention

```
# Use consistent topic names
Topic: room_device
# Examples: living_room_light, kitchen_plug, garage_motion

# Set device and friendly names
DeviceName Living Room Light
FriendlyName1 Living Room Light
```

### Security

```
# Set web admin password
WebPassword your_password

# Disable web server if not needed
WebServer 0

# Use MQTT authentication
MqttUser username
MqttPassword secure_password
```

### Reliability

```
# Enable auto-restart on crash
SetOption36 1

# Boot wait for WiFi
WifiConfig 4

# Backup configuration
# Download config from web UI: Configuration > Backup Configuration
```

### Firmware Updates

```
# OTA Update
OtaUrl http://ota.tasmota.com/tasmota/release/tasmota.bin.gz
Upgrade 1

# Or use web UI: Firmware Upgrade
```

---

## Reference

### Useful Links

- [Tasmota Documentation](https://tasmota.github.io/docs/)
- [Device Templates](https://templates.blakadder.com/)
- [Tasmota Commands](https://tasmota.github.io/docs/Commands/)
- [Berry Scripting](https://tasmota.github.io/docs/Berry/)

### GPIO Types

| GPIO | Function |
|------|----------|
| 0 | None |
| 21-28 | Relay 1-8 |
| 17-20 | Button 1-4 |
| 37-40 | PWM 1-4 |
| 52-53 | LED 1-2 |
| 9-14 | Switch 1-6 |
| 145-148 | Counter 1-4 |

### SetOptions Reference

| Option | Function |
|--------|----------|
| 0 | Save state on power cycle |
| 19 | HA discovery format |
| 30 | Use as light (not switch) |
| 57 | Index relay names |
| 36 | Auto-restart on crash |
