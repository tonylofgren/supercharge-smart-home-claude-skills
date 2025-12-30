# ESPHome Device Conversion Guides

## Table of Contents
- [Shelly Devices](#shelly-devices)
- [Sonoff Devices](#sonoff-devices)
- [Tuya Devices](#tuya-devices)
- [Xiaomi/Aqara BLE](#xiaomiaqara-ble)
- [Generic ESP Modules](#generic-esp-modules)

---

## Shelly Devices

### Shelly 1 (ESP8266)

```yaml
substitutions:
  device_name: "shelly-1"
  friendly_name: "Shelly 1"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp01_1m

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${device_name}-fallback"

captive_portal:
api:
ota:
  platform: esphome
logger:

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
    name: "Switch"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO4
    restore_mode: RESTORE_DEFAULT_OFF
```

### Shelly 1PM (ESP8266 with Power Monitoring)

```yaml
substitutions:
  device_name: "shelly-1pm"
  friendly_name: "Shelly 1PM"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp01_1m

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:

captive_portal:
api:
ota:
  platform: esphome
logger:
  baud_rate: 0  # Disable UART logging (uses TX for power monitoring)

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO4
      mode: INPUT_PULLUP
    name: "Switch"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO15
    restore_mode: RESTORE_DEFAULT_OFF

sensor:
  - platform: hlw8012
    sel_pin: GPIO12
    cf_pin: GPIO5
    cf1_pin: GPIO14
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"
    current_resistor: 0.001 ohm
    voltage_divider: 1925
    change_mode_every: 1
    update_interval: 5s

status_led:
  pin:
    number: GPIO0
    inverted: true
```

### Shelly 2.5 (Dual Relay with Power)

```yaml
substitutions:
  device_name: "shelly-25"

esphome:
  name: ${device_name}

esp8266:
  board: esp01_1m

# ... wifi, api, ota, logger ...

i2c:
  sda: GPIO12
  scl: GPIO14

sensor:
  - platform: ade7953_i2c
    irq_pin: GPIO16
    voltage:
      name: "Voltage"
    current_a:
      name: "Current 1"
    current_b:
      name: "Current 2"
    power_a:
      name: "Power 1"
    power_b:
      name: "Power 2"
    energy_a:
      name: "Energy 1"
    energy_b:
      name: "Energy 2"
    update_interval: 5s

  - platform: ntc
    sensor: temp_resistance
    name: "Temperature"
    calibration:
      b_constant: 3350
      reference_resistance: 10kOhm
      reference_temperature: 25C

  - platform: resistance
    id: temp_resistance
    sensor: temp_analog
    configuration: DOWNSTREAM
    resistor: 32kOhm

  - platform: adc
    id: temp_analog
    pin: A0
    update_interval: 10s

switch:
  - platform: gpio
    id: relay1
    name: "Relay 1"
    pin: GPIO4
  - platform: gpio
    id: relay2
    name: "Relay 2"
    pin: GPIO5

binary_sensor:
  - platform: gpio
    pin: GPIO13
    name: "Switch 1"
    on_press:
      - switch.toggle: relay1
  - platform: gpio
    pin: GPIO5
    name: "Switch 2"
    on_press:
      - switch.toggle: relay2
```

### Shelly Plus 1PM (ESP32-based)

```yaml
substitutions:
  device_name: "shelly-plus-1pm"

esphome:
  name: ${device_name}

esp32:
  board: esp32doit-devkit-v1
  framework:
    type: esp-idf

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
ota:
  platform: esphome
logger:

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO4
      mode: INPUT_PULLUP
    name: "Switch"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO26
    restore_mode: RESTORE_DEFAULT_OFF

sensor:
  - platform: bl0937
    cf_pin: GPIO7
    cf1_pin: GPIO8
    sel_pin:
      number: GPIO6
      inverted: true
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"
    update_interval: 5s

  - platform: ntc
    sensor: temp_resistance
    name: "Temperature"
    calibration:
      b_constant: 3350
      reference_resistance: 10kOhm
      reference_temperature: 25C

  - platform: resistance
    id: temp_resistance
    sensor: temp_analog
    configuration: DOWNSTREAM
    resistor: 10kOhm

  - platform: adc
    id: temp_analog
    pin: GPIO35
    attenuation: 11db

status_led:
  pin:
    number: GPIO0
    inverted: true
```

### Shelly Dimmer 2

```yaml
substitutions:
  device_name: "shelly-dimmer"

esphome:
  name: ${device_name}

esp8266:
  board: esp01_1m

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 115200

light:
  - platform: shelly_dimmer
    name: "Dimmer"
    firmware:
      version: "51.6"
    power:
      name: "Power"
    voltage:
      name: "Voltage"
    current:
      name: "Current"
    min_brightness: 100
    max_brightness: 1000
    warmup_brightness: 20

binary_sensor:
  - platform: gpio
    pin: GPIO14
    name: "Switch 1"
  - platform: gpio
    pin: GPIO12
    name: "Switch 2"
```

### Shelly Uni (Universal Input)

```yaml
substitutions:
  device_name: "shelly-uni"

esphome:
  name: ${device_name}

esp8266:
  board: esp01_1m

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO12
      mode: INPUT_PULLUP
    name: "Input 1"
  - platform: gpio
    pin:
      number: GPIO13
      mode: INPUT_PULLUP
    name: "Input 2"

switch:
  - platform: gpio
    id: relay1
    name: "Relay 1"
    pin: GPIO15
  - platform: gpio
    id: relay2
    name: "Relay 2"
    pin: GPIO4

sensor:
  - platform: adc
    pin: A0
    name: "ADC"
    update_interval: 10s
    filters:
      - multiply: 30.3  # Voltage divider for 30V max

  # DS18B20 temperature sensors (optional)
one_wire:
  - platform: gpio
    pin: GPIO5

sensor:
  - platform: dallas_temp
    address: 0xXXXXXXXXXXXXXXXX
    name: "Temperature"
```

---

## Sonoff Devices

### Sonoff Basic R2 (ESP8266)

```yaml
substitutions:
  device_name: "sonoff-basic"
  friendly_name: "Sonoff Basic"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp8285

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:

captive_portal:
api:
ota:
  platform: esphome
logger:

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO12
    restore_mode: RESTORE_DEFAULT_OFF

status_led:
  pin:
    number: GPIO13
    inverted: true
```

### Sonoff Mini R2

```yaml
substitutions:
  device_name: "sonoff-mini"

esphome:
  name: ${device_name}

esp8266:
  board: esp8285

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

  - platform: gpio
    pin:
      number: GPIO4
      mode: INPUT_PULLUP
    name: "Switch"
    on_state:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO12
    restore_mode: RESTORE_DEFAULT_OFF

status_led:
  pin:
    number: GPIO13
    inverted: true
```

### Sonoff 4CH Pro R3

```yaml
substitutions:
  device_name: "sonoff-4ch"

esphome:
  name: ${device_name}

esp8266:
  board: esp8285

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button 1"
    on_press:
      - switch.toggle: relay1

  - platform: gpio
    pin:
      number: GPIO9
      mode: INPUT_PULLUP
      inverted: true
    name: "Button 2"
    on_press:
      - switch.toggle: relay2

  - platform: gpio
    pin:
      number: GPIO10
      mode: INPUT_PULLUP
      inverted: true
    name: "Button 3"
    on_press:
      - switch.toggle: relay3

  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
      inverted: true
    name: "Button 4"
    on_press:
      - switch.toggle: relay4

switch:
  - platform: gpio
    id: relay1
    name: "Relay 1"
    pin: GPIO12
  - platform: gpio
    id: relay2
    name: "Relay 2"
    pin: GPIO5
  - platform: gpio
    id: relay3
    name: "Relay 3"
    pin: GPIO4
  - platform: gpio
    id: relay4
    name: "Relay 4"
    pin: GPIO15

status_led:
  pin:
    number: GPIO13
    inverted: true
```

### Sonoff POW R2 (Power Monitoring)

```yaml
substitutions:
  device_name: "sonoff-pow"

esphome:
  name: ${device_name}

esp8266:
  board: esp8285

logger:
  baud_rate: 0  # Disable UART logging

uart:
  rx_pin: GPIO3
  baud_rate: 4800

sensor:
  - platform: cse7766
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"
    update_interval: 5s

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO12
    restore_mode: RESTORE_DEFAULT_OFF

status_led:
  pin:
    number: GPIO13
    inverted: true
```

### Sonoff TH16 (Temperature/Humidity)

```yaml
substitutions:
  device_name: "sonoff-th16"

esphome:
  name: ${device_name}

esp8266:
  board: esp8285

sensor:
  - platform: dht
    pin: GPIO14
    model: SI7021  # or DHT11, AM2301
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 30s

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO12
    restore_mode: RESTORE_DEFAULT_OFF

status_led:
  pin:
    number: GPIO13
    inverted: true
```

### Sonoff S31 (US Plug with Power)

```yaml
substitutions:
  device_name: "sonoff-s31"

esphome:
  name: ${device_name}

esp8266:
  board: esp8285

logger:
  baud_rate: 0

uart:
  rx_pin: GPIO3
  baud_rate: 4800

sensor:
  - platform: cse7766
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "Relay"
    pin: GPIO12

status_led:
  pin:
    number: GPIO13
    inverted: true
```

---

## Tuya Devices

### Tuya MCU Devices

Many Tuya devices use a separate MCU for control. ESPHome communicates via UART.

```yaml
uart:
  rx_pin: GPIO3
  tx_pin: GPIO1
  baud_rate: 9600

tuya:

switch:
  - platform: tuya
    name: "Switch"
    switch_datapoint: 1

sensor:
  - platform: tuya
    name: "Temperature"
    sensor_datapoint: 2
    unit_of_measurement: "C"
    accuracy_decimals: 1
    filters:
      - multiply: 0.1

number:
  - platform: tuya
    name: "Target Temperature"
    number_datapoint: 3
    min_value: 15
    max_value: 35
    step: 1
```

### Common Tuya Datapoints

| Datapoint | Common Use |
|-----------|-----------|
| 1 | Power/Switch on/off |
| 2 | Temperature (x0.1) |
| 3 | Target temperature |
| 4 | Mode/Speed |
| 5 | Child lock |
| 101+ | Custom functions |

### Tuya Dimmer

```yaml
uart:
  rx_pin: GPIO3
  tx_pin: GPIO1
  baud_rate: 9600

tuya:

light:
  - platform: tuya
    name: "Dimmer"
    switch_datapoint: 1
    dimmer_datapoint: 2
    min_value: 10
    max_value: 1000
```

### Tuya RGB Light

```yaml
uart:
  rx_pin: GPIO3
  tx_pin: GPIO1
  baud_rate: 9600

tuya:

light:
  - platform: tuya
    name: "RGB Light"
    switch_datapoint: 20
    dimmer_datapoint: 22
    color_datapoint: 24
    color_type: rgbhsv  # or hsv
```

### Flashing Tuya Devices

**Methods:**
1. **tuya-convert** - OTA flash (may not work on newer devices)
2. **CloudCutter** - OTA for newer Beken chips
3. **Serial flash** - Direct connection to ESP chip

**tuya-convert (older devices):**
```bash
git clone https://github.com/ct-Open-Source/tuya-convert
cd tuya-convert
./install_prereq.sh
./start_flash.sh
```

**CloudCutter (Beken chips):**
```bash
# See https://github.com/tuya-cloudcutter/tuya-cloudcutter
```

---

## Xiaomi/Aqara BLE

### Enable BLE Tracker

```yaml
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: true
```

### Xiaomi LYWSD03MMC (Temperature/Humidity)

```yaml
sensor:
  - platform: xiaomi_lywsd03mmc
    mac_address: "A4:C1:38:XX:XX:XX"
    bindkey: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    battery_level:
      name: "Battery"
```

### Getting Bindkey

1. Use **TelinkFlasher** to extract bindkey:
   - https://pvvx.github.io/ATC_MiThermometer/TelinkMiFlasher.html
2. Or flash **ATC firmware** (no bindkey needed):
   - Changes protocol to ATC format

### ATC Firmware (Custom)

```yaml
sensor:
  - platform: atc_mithermometer
    mac_address: "A4:C1:38:XX:XX:XX"
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    battery_level:
      name: "Battery"
    battery_voltage:
      name: "Battery Voltage"
```

### Xiaomi MJYD2S Motion Sensor

```yaml
binary_sensor:
  - platform: xiaomi_mjyd2s
    mac_address: "XX:XX:XX:XX:XX:XX"
    bindkey: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    name: "Motion"
    idle_time:
      name: "Idle Time"
    battery_level:
      name: "Battery"
    light:
      name: "Light"
```

### Xiaomi Door/Window Sensor

```yaml
binary_sensor:
  - platform: xiaomi_mccgq02hl
    mac_address: "XX:XX:XX:XX:XX:XX"
    bindkey: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    name: "Door"
    battery_level:
      name: "Battery"
```

### Scanning for BLE Devices

```yaml
# Add to your config temporarily
esp32_ble_tracker:
  on_ble_advertise:
    then:
      - lambda: |-
          ESP_LOGD("ble", "MAC: %s, RSSI: %d",
            x.address_str().c_str(), x.get_rssi());
```

---

## Generic ESP Modules

### ESP-01 (1MB Flash)

```yaml
esphome:
  name: esp01-device

esp8266:
  board: esp01_1m

# Limited GPIO: GPIO0, GPIO2 (with restrictions)
# GPIO0: Must be HIGH during boot
# GPIO2: Must be HIGH during boot (often used for LED)

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
    name: "Button"

status_led:
  pin:
    number: GPIO2
    inverted: true
```

### ESP-12F / NodeMCU

```yaml
esphome:
  name: nodemcu-device

esp8266:
  board: nodemcuv2

# Available GPIO: 0, 2, 4, 5, 12, 13, 14, 15, 16
# GPIO15: Must be LOW during boot
# GPIO0, 2: Must be HIGH during boot
```

### ESP32 DevKit

```yaml
esphome:
  name: esp32-device

esp32:
  board: esp32dev

# ADC1 (usable with WiFi): GPIO32-39
# ADC2 (not usable with WiFi): GPIO0, 2, 4, 12-15, 25-27
# Touch: GPIO0, 2, 4, 12-15, 27, 32, 33
# Strapping pins: GPIO0, 2, 5, 12, 15
```

### ESP32-S3

```yaml
esphome:
  name: esp32s3-device

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf  # Recommended for S3

# USB: GPIO19 (D-), GPIO20 (D+)
# PSRAM: GPIO33-37 (if applicable)
```

### ESP32-C3

```yaml
esphome:
  name: esp32c3-device

esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: esp-idf

# Limited GPIO: 0-10, 18-21
# USB: GPIO18 (D-), GPIO19 (D+)
```

---

## Flashing Methods

### Web Flasher (Easiest)

1. Go to https://web.esphome.io
2. Connect device via USB
3. Flash firmware directly from browser

### ESPHome Dashboard

```bash
# Install ESPHome
pip install esphome

# Compile and flash
esphome run device.yaml

# First flash (serial)
esphome run device.yaml --device /dev/ttyUSB0

# OTA flash
esphome run device.yaml
```

### Serial Flashing Wiring

| ESP Pin | USB-Serial |
|---------|-----------|
| 3V3 | 3.3V |
| GND | GND |
| TX | RX |
| RX | TX |
| GPIO0 | GND (during flash) |

**Boot mode:** Hold GPIO0 LOW, power cycle, then release.

### OTA Updates

```yaml
ota:
  platform: esphome
  password: !secret ota_password

# For HTTP OTA (larger updates)
ota:
  - platform: esphome
  - platform: http_request
```
