# ESPHome Bluetooth Reference

Complete guide to BLE tracker, proxy, presence detection, and Bluetooth devices.

## Table of Contents

- [BLE Overview](#ble-overview)
- [BLE Tracker](#ble-tracker)
- [BLE Presence Detection](#ble-presence-detection)
- [Bluetooth Proxy](#bluetooth-proxy)
- [Xiaomi BLE Sensors](#xiaomi-ble-sensors)
- [iBeacon](#ibeacon)
- [BLE Client](#ble-client)
- [BLE Keyboard/Mouse](#ble-keyboardmouse)
- [Troubleshooting](#troubleshooting)
- [Complete Examples](#complete-examples)

---

## BLE Overview

ESP32 supports Bluetooth Low Energy (BLE). ESP8266 does NOT support Bluetooth.

| Feature | Purpose |
|---------|---------|
| BLE Tracker | Passive scanning, detect nearby devices |
| BLE Presence | Detect specific MAC addresses |
| Bluetooth Proxy | Extend Home Assistant's BLE range |
| BLE Client | Connect to and control BLE devices |
| Xiaomi BLE | Decode Xiaomi sensor broadcasts |

**Resource Usage**: BLE uses significant memory. Expect 50-100KB RAM usage.

---

## BLE Tracker

### Basic Configuration

```yaml
esp32_ble_tracker:
```

### With Custom Parameters

```yaml
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms  # Scan window interval
    window: 1100ms    # Active scan duration
    active: true      # Request scan responses
    continuous: true  # Scan continuously
```

### Passive vs Active Scanning

```yaml
# Passive: listen only (lower power, less data)
esp32_ble_tracker:
  scan_parameters:
    active: false

# Active: request responses (more data, more power)
esp32_ble_tracker:
  scan_parameters:
    active: true
```

### On BLE Advertise Trigger

```yaml
esp32_ble_tracker:
  on_ble_advertise:
    - mac_address: "AA:BB:CC:DD:EE:FF"
      then:
        - lambda: |-
            ESP_LOGD("ble", "Device found: %s, RSSI: %d",
                     x.address_str().c_str(), x.get_rssi());
```

### Scan for All Devices (Debug)

```yaml
esp32_ble_tracker:
  on_ble_advertise:
    then:
      - lambda: |-
          ESP_LOGD("ble", "Found: %s (%s) RSSI=%d",
                   x.get_name().c_str(),
                   x.address_str().c_str(),
                   x.get_rssi());
```

---

## BLE Presence Detection

### By MAC Address

```yaml
esp32_ble_tracker:

binary_sensor:
  - platform: ble_presence
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Phone Present"
    device_class: presence
```

### Multiple Devices

```yaml
esp32_ble_tracker:

binary_sensor:
  - platform: ble_presence
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Person 1 Phone"
    id: phone1

  - platform: ble_presence
    mac_address: "11:22:33:44:55:66"
    name: "Person 2 Phone"
    id: phone2

  # Combined presence
  - platform: template
    name: "Anyone Home"
    device_class: occupancy
    lambda: |-
      return id(phone1).state || id(phone2).state;
```

### By iBeacon UUID

```yaml
esp32_ble_tracker:

binary_sensor:
  - platform: ble_presence
    ibeacon_uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    name: "iBeacon Present"
```

### By Service UUID

```yaml
esp32_ble_tracker:

binary_sensor:
  - platform: ble_presence
    service_uuid: "0000180f-0000-1000-8000-00805f9b34fb"
    name: "Device with Battery Service"
```

### RSSI Signal Strength

```yaml
esp32_ble_tracker:

sensor:
  - platform: ble_rssi
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Phone Signal Strength"
    filters:
      - sliding_window_moving_average:
          window_size: 10
```

### Timeout Configuration

```yaml
binary_sensor:
  - platform: ble_presence
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Phone Present"
    # Default timeout is 5 minutes
    # Customize with filters:
    filters:
      - delayed_off: 10min  # Wait 10 min before marking absent
```

---

## Bluetooth Proxy

Extend Home Assistant's Bluetooth range with ESP32 devices.

### Active Proxy (Recommended)

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true
```

### Passive Proxy

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: false

bluetooth_proxy:
  active: false
```

### Memory Optimization

```yaml
# If running low on memory
esp32_ble_tracker:
  scan_parameters:
    interval: 320ms
    window: 30ms
    active: false

bluetooth_proxy:
  active: false
```

### Combined with Local Sensors

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true

# Local presence detection still works
binary_sensor:
  - platform: ble_presence
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Phone Present"

# Xiaomi sensors still work locally
sensor:
  - platform: xiaomi_hhccjcy01
    mac_address: "AA:BB:CC:DD:EE:FF"
    temperature:
      name: "Plant Temperature"
```

---

## Xiaomi BLE Sensors

### MiFlora Plant Sensor (HHCCJCY01)

```yaml
esp32_ble_tracker:

sensor:
  - platform: xiaomi_hhccjcy01
    mac_address: "AA:BB:CC:DD:EE:FF"
    temperature:
      name: "Plant Temperature"
    moisture:
      name: "Plant Moisture"
    illuminance:
      name: "Plant Light"
    conductivity:
      name: "Plant Conductivity"
    battery_level:
      name: "Plant Battery"
```

### LYWSD03MMC (Temperature/Humidity)

```yaml
esp32_ble_tracker:

sensor:
  - platform: xiaomi_lywsd03mmc
    mac_address: "AA:BB:CC:DD:EE:FF"
    bindkey: "your-32-char-bindkey"  # For encrypted versions
    temperature:
      name: "Room Temperature"
    humidity:
      name: "Room Humidity"
    battery_level:
      name: "Sensor Battery"
```

### CGG1 (Temperature/Humidity)

```yaml
esp32_ble_tracker:

sensor:
  - platform: xiaomi_cgg1
    mac_address: "AA:BB:CC:DD:EE:FF"
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    battery_level:
      name: "Battery"
```

### MJYD2S Motion Sensor

```yaml
esp32_ble_tracker:

binary_sensor:
  - platform: xiaomi_mjyd02yla
    mac_address: "AA:BB:CC:DD:EE:FF"
    bindkey: "your-bindkey"
    name: "Motion"
    idle_time:
      name: "Idle Time"
    light:
      name: "Light"
    battery_level:
      name: "Battery"
```

### MiScale (Weight)

```yaml
esp32_ble_tracker:

sensor:
  - platform: xiaomi_miscale
    mac_address: "AA:BB:CC:DD:EE:FF"
    weight:
      name: "Weight"
```

---

## iBeacon

### Detect iBeacons

```yaml
esp32_ble_tracker:

binary_sensor:
  - platform: ble_presence
    ibeacon_uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    ibeacon_major: 1
    ibeacon_minor: 1
    name: "iBeacon 1"
```

### iBeacon RSSI for Distance

```yaml
esp32_ble_tracker:

sensor:
  - platform: ble_rssi
    ibeacon_uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    name: "iBeacon Signal"

  - platform: template
    name: "iBeacon Distance"
    unit_of_measurement: "m"
    lambda: |-
      float rssi = id(ibeacon_rssi).state;
      if (isnan(rssi)) return NAN;
      // Simple distance estimation (not accurate)
      float txPower = -59;  // RSSI at 1 meter
      return pow(10, (txPower - rssi) / 20);
```

### Create iBeacon (Transmit)

```yaml
esp32_ble_beacon:
  type: iBeacon
  uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  major: 1
  minor: 1
```

---

## BLE Client

Connect to BLE peripherals.

### Basic Connection

```yaml
esp32_ble_tracker:

ble_client:
  - mac_address: "AA:BB:CC:DD:EE:FF"
    id: my_ble_device

sensor:
  - platform: ble_client
    ble_client_id: my_ble_device
    name: "Battery Level"
    service_uuid: "180f"
    characteristic_uuid: "2a19"
    notify: true
```

### Read Characteristic

```yaml
ble_client:
  - mac_address: "AA:BB:CC:DD:EE:FF"
    id: my_device
    on_connect:
      then:
        - lambda: |-
            ESP_LOGD("ble", "Connected");
    on_disconnect:
      then:
        - lambda: |-
            ESP_LOGD("ble", "Disconnected");

sensor:
  - platform: ble_client
    ble_client_id: my_device
    name: "Temperature"
    service_uuid: "1809"  # Health Thermometer
    characteristic_uuid: "2a1c"
    notify: true
    lambda: |-
      uint16_t raw = (x[1] << 8) | x[0];
      return raw / 100.0;
```

### Write Characteristic

```yaml
button:
  - platform: template
    name: "Send Command"
    on_press:
      - ble_client.ble_write:
          id: my_device
          service_uuid: "xxxx"
          characteristic_uuid: "yyyy"
          value: [0x01, 0x02, 0x03]
```

---

## BLE Keyboard/Mouse

### BLE Keyboard (ESP32)

```yaml
external_components:
  - source: github://dmamontov/esphome-blekeyboard@main
    components: [ble_keyboard]

ble_keyboard:
  id: kb
  name: "ESP32 Keyboard"
  manufacturer: "ESPHome"

button:
  - platform: template
    name: "Send Enter"
    on_press:
      - ble_keyboard.key:
          id: kb
          key: RETURN

  - platform: template
    name: "Send Text"
    on_press:
      - ble_keyboard.print:
          id: kb
          text: "Hello World"
```

---

## Troubleshooting

### Debug Logging

```yaml
logger:
  level: DEBUG
  logs:
    esp32_ble_tracker: DEBUG
    ble_client: DEBUG
```

### Common Issues

**No devices found:**
```yaml
# Enable scan logging
esp32_ble_tracker:
  on_ble_advertise:
    then:
      - lambda: ESP_LOGD("scan", "Found: %s", x.address_str().c_str());
```

**Memory issues:**
```yaml
# Reduce memory usage
esp32_ble_tracker:
  scan_parameters:
    interval: 300ms
    window: 30ms
    active: false
```

**Intermittent detection:**
```yaml
# Increase detection reliability
binary_sensor:
  - platform: ble_presence
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Phone"
    filters:
      - delayed_off: 5min  # Longer timeout
```

**Conflicts with WiFi:**
```yaml
# BLE and WiFi share antenna
# Reduce BLE scan aggressiveness
esp32_ble_tracker:
  scan_parameters:
    interval: 1000ms
    window: 100ms
```

### Finding MAC Addresses

```yaml
esp32_ble_tracker:
  on_ble_advertise:
    then:
      - lambda: |-
          if (x.get_name().length() > 0) {
            ESP_LOGD("ble", "Device: %s (%s)",
                     x.get_name().c_str(),
                     x.address_str().c_str());
          }
```

### Getting Bindkeys (Xiaomi)

For encrypted Xiaomi sensors, use tools like:
- Xiaomi Cloud Tokens Extractor
- HACS Xiaomi Miot Auto integration

---

## Complete Examples

### Room Presence System

```yaml
esphome:
  name: room-presence

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

logger:

esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: true

bluetooth_proxy:
  active: true

binary_sensor:
  - platform: ble_presence
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Person 1"
    id: person1
    device_class: presence

  - platform: ble_presence
    mac_address: "11:22:33:44:55:66"
    name: "Person 2"
    id: person2
    device_class: presence

  - platform: template
    name: "Room Occupied"
    device_class: occupancy
    lambda: return id(person1).state || id(person2).state;
    on_press:
      - homeassistant.event:
          event: esphome.room_occupied
          data:
            room: "living_room"
    on_release:
      - homeassistant.event:
          event: esphome.room_empty
          data:
            room: "living_room"

sensor:
  - platform: ble_rssi
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Person 1 RSSI"
    filters:
      - sliding_window_moving_average:
          window_size: 5
```

### Plant Monitor Hub

```yaml
esphome:
  name: plant-monitor

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

logger:

esp32_ble_tracker:

sensor:
  # Plant 1 - Living Room
  - platform: xiaomi_hhccjcy01
    mac_address: "AA:BB:CC:DD:EE:FF"
    temperature:
      name: "Plant 1 Temperature"
    moisture:
      name: "Plant 1 Moisture"
      on_value_range:
        - below: 20
          then:
            - homeassistant.event:
                event: esphome.plant_needs_water
                data:
                  plant: "Plant 1"
    illuminance:
      name: "Plant 1 Light"
    conductivity:
      name: "Plant 1 Fertility"
    battery_level:
      name: "Plant 1 Battery"

  # Plant 2 - Bedroom
  - platform: xiaomi_hhccjcy01
    mac_address: "11:22:33:44:55:66"
    temperature:
      name: "Plant 2 Temperature"
    moisture:
      name: "Plant 2 Moisture"
    illuminance:
      name: "Plant 2 Light"
    conductivity:
      name: "Plant 2 Fertility"
    battery_level:
      name: "Plant 2 Battery"
```

### Multi-Room Climate Sensors

```yaml
esphome:
  name: climate-hub

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

logger:

esp32_ble_tracker:

bluetooth_proxy:
  active: true

sensor:
  - platform: xiaomi_lywsd03mmc
    mac_address: "AA:BB:CC:DD:EE:FF"
    bindkey: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    temperature:
      name: "Living Room Temperature"
    humidity:
      name: "Living Room Humidity"
    battery_level:
      name: "Living Room Sensor Battery"

  - platform: xiaomi_lywsd03mmc
    mac_address: "11:22:33:44:55:66"
    bindkey: "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    temperature:
      name: "Bedroom Temperature"
    humidity:
      name: "Bedroom Humidity"
    battery_level:
      name: "Bedroom Sensor Battery"

  - platform: xiaomi_lywsd03mmc
    mac_address: "77:88:99:AA:BB:CC"
    bindkey: "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
    temperature:
      name: "Kitchen Temperature"
    humidity:
      name: "Kitchen Humidity"
    battery_level:
      name: "Kitchen Sensor Battery"
```
