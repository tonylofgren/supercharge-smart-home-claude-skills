# Bluetooth Integration Reference

> Native Bluetooth and BLE device integration for Home Assistant 2024/2025

## Overview

Home Assistant's native Bluetooth integration provides seamless support for Bluetooth Low Energy (BLE) devices. Combined with ESPHome Bluetooth Proxies, you can extend coverage throughout your home for reliable device communication.

### Key Features

- **Native BLE Support** - Direct communication with Bluetooth devices
- **ESPHome Proxy** - Extend Bluetooth range using ESP32 devices
- **Passive Scanning** - Discover devices automatically
- **Active Connections** - Full bidirectional communication
- **Room-Level Presence** - Track device location by signal strength

---

## Bluetooth Adapter Setup

### Built-in Adapters

Most Home Assistant installations detect built-in Bluetooth automatically:

```yaml
# Check Bluetooth status
# Settings → Devices & Services → Bluetooth

# View adapter info via Developer Tools → Services
service: bluetooth.async_scanner_diagnostics
```

### USB Bluetooth Adapters

Recommended USB adapters for better range and reliability:

| Adapter | Chipset | Range | Notes |
|---------|---------|-------|-------|
| **Asus BT-500** | Intel AX200 | Good | BT 5.0, reliable |
| **TP-Link UB500** | RTL8761B | Good | BT 5.0, widely available |
| **Sena UD100** | CSR8510 | Excellent | Long range, industrial |
| **ZEXMTE Long Range** | CSR8510 | Excellent | Budget option |

#### Configuration for USB Adapters

```yaml
# For Docker installations, pass the Bluetooth device:
# docker-compose.yml
services:
  homeassistant:
    ...
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    volumes:
      - /run/dbus:/run/dbus:ro
    privileged: true
```

### Multiple Adapters

Home Assistant supports multiple Bluetooth adapters:

```yaml
# Each adapter creates a separate scanner
# Settings → Devices & Services → Bluetooth
# You'll see multiple entries like:
# - hci0 (Built-in)
# - hci1 (USB Adapter)
```

#### Adapter Selection for Integrations

Some integrations allow choosing which adapter to use:

```yaml
# In integration configuration
bluetooth:
  adapter: hci1  # Specify adapter
```

---

## BLE Device Types

### Temperature/Humidity Sensors

#### Xiaomi Mi Temperature & Humidity Sensors

```yaml
# LYWSD03MMC (small square sensor)
# Automatically discovered via Bluetooth integration

# For sensors with custom firmware (ATC/PVVX):
# No configuration needed - discovered automatically

# Template sensor for battery monitoring
template:
  - sensor:
      - name: "Bedroom Sensor Battery"
        unit_of_measurement: "%"
        device_class: battery
        state: >
          {{ state_attr('sensor.lywsd03mmc_battery', 'battery_level') | int(0) }}
```

#### SwitchBot Meter

```yaml
# SwitchBot devices integrate via Bluetooth
# Discovered automatically when in range

# Automation example
automation:
  - id: switchbot_temp_alert
    alias: "SwitchBot Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.switchbot_meter_temperature
        above: 30
    action:
      - service: notify.mobile_app
        data:
          message: "Room temperature is {{ states('sensor.switchbot_meter_temperature') }}°C"
```

#### Govee Sensors

```yaml
# Govee H5075, H5072, H5101
# Supported via Govee BLE integration

# After discovery, sensors appear as:
# - sensor.govee_h5075_xxxx_temperature
# - sensor.govee_h5075_xxxx_humidity
# - sensor.govee_h5075_xxxx_battery
```

### Presence Trackers

#### iBeacon Devices

```yaml
# iBeacons detected via Bluetooth LE Tracker
# configuration.yaml
device_tracker:
  - platform: bluetooth_le_tracker
    track_new_devices: false
    interval_seconds: 12
    consider_home: 180

# Known devices in known_devices.yaml
ble_ibeacon_uuid:
  name: "My iBeacon"
  mac: XX:XX:XX:XX:XX:XX
  track: true
```

#### Tile Trackers

```yaml
# Tile trackers work with Bluetooth integration
# Passive scanning detects presence

# Create binary sensor for presence
template:
  - binary_sensor:
      - name: "Tile Keys Present"
        device_class: presence
        state: >
          {{ states('sensor.tile_slim_signal_strength') | int(-100) > -90 }}
```

#### Phone/Watch Presence

```yaml
# Track BLE advertisements from phones/watches
# Useful for room-level presence

automation:
  - id: phone_room_presence
    alias: "Phone Room Detection"
    trigger:
      - platform: state
        entity_id: sensor.pixel_phone_ble_rssi
    condition:
      - condition: numeric_state
        entity_id: sensor.pixel_phone_ble_rssi
        above: -70
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.current_room
        data:
          option: "Living Room"
```

### Smart Locks

#### SwitchBot Lock

```yaml
# SwitchBot Lock requires SwitchBot Hub or direct BLE
# Entities created:
# - lock.switchbot_lock_xxxx
# - binary_sensor.switchbot_lock_xxxx_door

automation:
  - id: auto_lock_door
    alias: "Auto Lock Front Door"
    trigger:
      - platform: state
        entity_id: binary_sensor.switchbot_lock_door
        to: "off"  # Door closed
        for:
          minutes: 5
    condition:
      - condition: state
        entity_id: lock.switchbot_lock
        state: "unlocked"
    action:
      - service: lock.lock
        target:
          entity_id: lock.switchbot_lock
```

#### August/Yale Locks

```yaml
# August Connect or Yale Connect required for remote access
# BLE provides local control when in range

# Lock/unlock actions
script:
  lock_all_doors:
    alias: "Lock All Doors"
    sequence:
      - service: lock.lock
        target:
          entity_id:
            - lock.front_door
            - lock.back_door
      - delay:
          seconds: 5
      - condition: template
        value_template: >
          {{ is_state('lock.front_door', 'locked') and
             is_state('lock.back_door', 'locked') }}
      - service: notify.mobile_app
        data:
          message: "All doors locked"
```

### Plant Sensors

#### Xiaomi Mi Flora / HHCC Plant Sensor

```yaml
# Discovered automatically via Bluetooth
# Creates sensors for:
# - Moisture
# - Temperature
# - Conductivity
# - Illuminance
# - Battery

# Plant care automation
automation:
  - id: plant_needs_water
    alias: "Plant Needs Water Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mi_flora_living_room_moisture
        below: 15
        for:
          hours: 2
    action:
      - service: notify.mobile_app
        data:
          title: "Plant Care"
          message: "Living room plant needs water ({{ states('sensor.mi_flora_living_room_moisture') }}%)"
```

#### Parrot Flower Power

```yaml
# Similar to Mi Flora, provides plant metrics
# Use template sensors for plant health status

template:
  - sensor:
      - name: "Plant Health Status"
        state: >
          {% set moisture = states('sensor.flower_power_moisture') | float(0) %}
          {% set light = states('sensor.flower_power_light') | float(0) %}
          {% if moisture < 10 %}
            Critical - Needs Water
          {% elif moisture < 20 %}
            Low Moisture
          {% elif light < 100 %}
            Needs More Light
          {% else %}
            Healthy
          {% endif %}
```

### Other BLE Devices

#### Oral-B Smart Toothbrush

```yaml
# Tracks brushing sessions
# sensor.oral_b_toothbrush_state: idle, running, etc.
# sensor.oral_b_toothbrush_time: brushing duration

automation:
  - id: brushing_reminder
    alias: "Brushing Time Reminder"
    trigger:
      - platform: state
        entity_id: sensor.oral_b_toothbrush_state
        from: "running"
        to: "idle"
    condition:
      - condition: numeric_state
        entity_id: sensor.oral_b_toothbrush_time
        below: 120  # Less than 2 minutes
    action:
      - service: notify.mobile_app
        data:
          message: "Brush longer! Only {{ states('sensor.oral_b_toothbrush_time') }} seconds"
```

#### Inkbird Temperature Probes

```yaml
# BBQ/cooking temperature monitors
# Discovered via Bluetooth integration

automation:
  - id: meat_temp_alert
    alias: "Meat Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.inkbird_probe_1
        above: 63  # Safe internal temp for beef
    action:
      - service: notify.mobile_app
        data:
          title: "BBQ Alert"
          message: "Meat reached {{ states('sensor.inkbird_probe_1') }}°C - Ready!"
```

---

## ESPHome Bluetooth Proxy

Extend Bluetooth coverage throughout your home using ESP32 devices as Bluetooth proxies.

### Basic Proxy Setup

```yaml
# esphome/bluetooth-proxy-living-room.yaml
esphome:
  name: bluetooth-proxy-living-room
  friendly_name: "BT Proxy Living Room"

esp32:
  board: esp32dev
  framework:
    type: esp-idf

# Enable Bluetooth Proxy
esp32_ble_tracker:
  scan_parameters:
    active: true
    interval: 1100ms
    window: 1100ms

bluetooth_proxy:
  active: true

# WiFi connection
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

# Enable logging
logger:

# Enable Home Assistant API
api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

### Proxy with Local Sensors

Combine proxy functionality with local sensors:

```yaml
# esphome/bluetooth-proxy-bedroom.yaml
esphome:
  name: bluetooth-proxy-bedroom
  friendly_name: "BT Proxy Bedroom"

esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: esp-idf

esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true

# Local temperature sensor
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Bedroom Temperature"
    humidity:
      name: "Bedroom Humidity"
    update_interval: 60s

  # WiFi signal for diagnostics
  - platform: wifi_signal
    name: "BT Proxy Bedroom WiFi"
    update_interval: 60s

# Status LED
light:
  - platform: status_led
    name: "BT Proxy Bedroom Status"
    pin: GPIO8

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
```

### Multiple Proxies for Coverage

```yaml
# Recommended proxy placement:
# - One per floor
# - One per 15-20 meters
# - Avoid metal obstructions

# Each proxy reports to Home Assistant independently
# HA aggregates signals for best connection

# Check proxy status in Settings → Devices & Services → ESPHome
# Each proxy shows:
# - Connection status
# - Number of BLE devices seen
# - Signal strength
```

### Proxy Performance Tuning

```yaml
# For better range and stability
esp32_ble_tracker:
  scan_parameters:
    # Longer window = more devices found, more power
    interval: 1100ms
    window: 1100ms
    # Use active scanning for devices that need it
    active: true

# For battery devices (passive only)
esp32_ble_tracker:
  scan_parameters:
    interval: 320ms
    window: 30ms
    active: false

# Memory optimization for ESP32-C3
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
  on_ble_manufacturer_data_advertise:
    - manufacturer_id: 0x004C  # Apple
      then:
        - lambda: 'ESP_LOGD("ble", "Apple device: %s", x.data.data());'
```

### Proxy Diagnostics

```yaml
# Add diagnostic sensors to proxy
sensor:
  - platform: internal_temperature
    name: "BT Proxy Internal Temp"

  - platform: uptime
    name: "BT Proxy Uptime"

  - platform: wifi_signal
    name: "BT Proxy WiFi Signal"

text_sensor:
  - platform: wifi_info
    ip_address:
      name: "BT Proxy IP"
    ssid:
      name: "BT Proxy SSID"

button:
  - platform: restart
    name: "BT Proxy Restart"
```

---

## Bluetooth Tracking

### Device Tracker Setup

```yaml
# Basic BLE device tracking
# configuration.yaml
device_tracker:
  - platform: bluetooth_le_tracker
    consider_home: 300  # 5 minutes
    interval_seconds: 30
    track_new_devices: false

# Known devices
# known_devices.yaml
my_phone_ble:
  name: "My Phone BLE"
  mac: XX:XX:XX:XX:XX:XX
  track: true
  consider_home: 180
```

### Room-Level Presence

Use signal strength from multiple proxies to determine room:

```yaml
# Template sensor for room detection
template:
  - sensor:
      - name: "Phone Current Room"
        state: >
          {% set living = states('sensor.bt_proxy_living_room_phone_rssi') | int(-100) %}
          {% set bedroom = states('sensor.bt_proxy_bedroom_phone_rssi') | int(-100) %}
          {% set kitchen = states('sensor.bt_proxy_kitchen_phone_rssi') | int(-100) %}

          {% set rooms = {
            'Living Room': living,
            'Bedroom': bedroom,
            'Kitchen': kitchen
          } %}

          {% set max_rssi = rooms.values() | max %}
          {% if max_rssi > -80 %}
            {{ rooms | dictsort(by='value', reverse=true) | first | first }}
          {% else %}
            Unknown
          {% endif %}

# Automation based on room
automation:
  - id: room_based_lights
    alias: "Room-Based Lighting"
    trigger:
      - platform: state
        entity_id: sensor.phone_current_room
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: sensor.phone_current_room
                state: "Living Room"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.living_room
          - conditions:
              - condition: state
                entity_id: sensor.phone_current_room
                state: "Bedroom"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.bedroom
```

### Distance Estimation

```yaml
# RSSI to distance approximation
# Note: Very approximate due to environmental factors

template:
  - sensor:
      - name: "Phone Distance from Living Room"
        unit_of_measurement: "m"
        state: >
          {% set rssi = states('sensor.bt_proxy_living_room_phone_rssi') | int(-100) %}
          {% set tx_power = -59 %}  {# Calibrate for your device #}
          {% set n = 2.0 %}  {# Path loss exponent (2.0-4.0) #}

          {% if rssi > -100 %}
            {{ (10 ** ((tx_power - rssi) / (10 * n))) | round(1) }}
          {% else %}
            unknown
          {% endif %}

# Zone-based presence
template:
  - binary_sensor:
      - name: "Phone Near Living Room"
        device_class: presence
        state: >
          {{ states('sensor.phone_distance_from_living_room') | float(100) < 3 }}
```

### Multi-Device Tracking

```yaml
# Track multiple family members
template:
  - sensor:
      - name: "People in Living Room"
        state: >
          {% set count = 0 %}
          {% if states('sensor.bt_proxy_living_room_phone_1_rssi') | int(-100) > -75 %}
            {% set count = count + 1 %}
          {% endif %}
          {% if states('sensor.bt_proxy_living_room_phone_2_rssi') | int(-100) > -75 %}
            {% set count = count + 1 %}
          {% endif %}
          {{ count }}

# Occupancy binary sensor
template:
  - binary_sensor:
      - name: "Living Room Occupied"
        device_class: occupancy
        state: >
          {{ states('sensor.people_in_living_room') | int(0) > 0 }}
```

---

## Troubleshooting

### Interference Issues

Common sources of Bluetooth interference:

```yaml
# WiFi on same frequency (2.4 GHz)
# - Use WiFi channels 1, 6, or 11 to minimize overlap
# - Bluetooth uses channels 0-78 (2402-2480 MHz)

# USB 3.0 ports
# - USB 3.0 emits 2.4 GHz noise
# - Use USB 2.0 port or USB extension cable for BT adapter

# Microwave ovens
# - Operate at 2.45 GHz
# - Temporary interference during use

# Other BLE devices
# - Too many devices can cause congestion
# - Limit to ~10 active connections per adapter
```

### Connection Drops

```yaml
# Check adapter status
# Settings → Devices & Services → Bluetooth → Configure

# Restart Bluetooth integration
# Developer Tools → Services
service: homeassistant.reload_config_entry
data:
  entry_id: <bluetooth_config_entry_id>

# For persistent issues, try:
# 1. Different USB port (preferably USB 2.0)
# 2. USB extension cable to move adapter away from interference
# 3. Additional ESPHome proxies for redundancy
```

### Discovery Problems

```yaml
# Device not discovered:

# 1. Check device is in pairing/advertising mode
# 2. Bring device closer to adapter/proxy
# 3. Check if device needs specific integration:
#    - Xiaomi → Xiaomi BLE
#    - SwitchBot → SwitchBot
#    - Govee → Govee BLE

# Force discovery scan
# Developer Tools → Services
service: bluetooth.start_scan
data:
  timeout: 60

# Check logs for BLE events
# Settings → System → Logs
# Filter: bluetooth
```

### Proxy-Specific Issues

```yaml
# ESPHome proxy not working:

# 1. Check WiFi connection
#    - Strong signal required for proxy
#    - Use dedicated IoT network if available

# 2. Verify ESP-IDF framework (not Arduino)
esp32:
  framework:
    type: esp-idf  # Required for Bluetooth proxy

# 3. Check memory usage
#    - ESP32-C3 has limited RAM
#    - Remove unused components

# 4. Update ESPHome and Home Assistant
#    - BLE proxy requires matching versions

# 5. Check proxy logs
#    - ESPHome Dashboard → Logs
#    - Look for BLE scan results
```

### Battery Drain on Tracked Devices

```yaml
# Reduce scan frequency for battery devices
esp32_ble_tracker:
  scan_parameters:
    # Less aggressive scanning
    interval: 2000ms
    window: 100ms
    active: false  # Passive scanning only

# Consider tracking schedule
automation:
  - id: ble_scan_schedule
    alias: "BLE Scan Schedule"
    trigger:
      - platform: time_pattern
        hours: "/1"  # Every hour
    action:
      - service: bluetooth.start_scan
        data:
          timeout: 30
```

### Signal Strength Calibration

```yaml
# Calibrate RSSI for accurate distance
# Place device at known distance (1 meter) and record RSSI

template:
  - sensor:
      - name: "Phone Distance Calibrated"
        unit_of_measurement: "m"
        state: >
          {% set rssi = states('sensor.phone_rssi') | int(-100) %}

          {# Calibration values - adjust per device #}
          {% set rssi_1m = -55 %}  {# RSSI at 1 meter #}
          {% set path_loss = 2.5 %}  {# Environment factor #}

          {% if rssi > -100 %}
            {{ (10 ** ((rssi_1m - rssi) / (10 * path_loss))) | round(1) }}
          {% else %}
            unknown
          {% endif %}
```

---

## Best Practices

### Adapter Placement

1. **Central location** - Place adapter/proxy centrally for best coverage
2. **Elevated position** - Higher placement reduces ground interference
3. **Away from metal** - Metal reflects/blocks Bluetooth signals
4. **USB extension** - Move adapter away from computer/hub interference

### Proxy Network Design

```
Recommended layout for 2000 sq ft home:

    [Proxy 1]                    [Proxy 2]
    Living Room                  Kitchen
         \                          /
          \                        /
           \                      /
            [Home Assistant]
           /                      \
          /                        \
         /                          \
    [Proxy 3]                    [Proxy 4]
    Bedroom                      Office

- 4 proxies provide overlapping coverage
- Each proxy covers ~500 sq ft radius
- Overlapping zones enable room detection
```

### Device Organization

```yaml
# Group BLE devices by type
# customize.yaml
sensor.lywsd03mmc_*:
  device_class: temperature

binary_sensor.*_ble_presence:
  device_class: presence

# Use areas for organization
# Settings → Devices → Assign to Area
```

### Automation Patterns

```yaml
# Debounce rapid state changes
automation:
  - id: ble_presence_light
    alias: "BLE Presence Light Control"
    trigger:
      - platform: state
        entity_id: binary_sensor.phone_ble_present
        to: "on"
        for:
          seconds: 30  # Debounce
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room

# Handle unavailable states
automation:
  - id: ble_fallback
    alias: "BLE Unavailable Fallback"
    trigger:
      - platform: state
        entity_id: sensor.phone_ble_rssi
        to: "unavailable"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          message: "BLE tracking unavailable - check proxy status"
```

---

## Related References

- [ESPHome Integration](integrations-esphome.md) - ESPHome device setup
- [Presence Detection](automations.md#presence-detection) - Presence automation patterns
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide
