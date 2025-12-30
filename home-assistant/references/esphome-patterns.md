# ESPHome Patterns - Complete Reference

Common ESPHome configurations for Home Assistant integration.

## Basic Device Configuration

```yaml
esphome:
  name: device-name
  friendly_name: "Device Name"

esp32:
  board: esp32dev
  # Or for ESP8266:
  # esp8266:
  #   board: nodemcuv2

# Enable logging
logger:

# Enable Home Assistant API
api:
  encryption:
    key: "your-encryption-key"

# Enable OTA updates
ota:
  password: "ota-password"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Optional fallback AP
  ap:
    ssid: "Device Fallback"
    password: "fallback-password"

captive_portal:
```

---

## Common Sensor Patterns

### Temperature & Humidity (DHT22)

```yaml
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Temperature"
      filters:
        - sliding_window_moving_average:
            window_size: 5
            send_every: 5
    humidity:
      name: "Humidity"
    update_interval: 60s
    model: DHT22
```

### Temperature (Dallas DS18B20)

```yaml
dallas:
  - pin: GPIO4

sensor:
  - platform: dallas
    address: 0x1234567890ABCDEF
    name: "Temperature"
    filters:
      - filter_out: nan
```

### BME280 (Temperature, Humidity, Pressure)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: bme280
    temperature:
      name: "Temperature"
      oversampling: 16x
    pressure:
      name: "Pressure"
    humidity:
      name: "Humidity"
    address: 0x76
    update_interval: 60s
```

### Power Monitoring (BL0937/HLW8012)

```yaml
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
    update_interval: 10s
    current_resistor: 0.001
    voltage_divider: 2351
```

### Light Sensor (BH1750)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: bh1750
    name: "Illuminance"
    address: 0x23
    update_interval: 30s
```

### Distance Sensor (Ultrasonic HC-SR04)

```yaml
sensor:
  - platform: ultrasonic
    trigger_pin: GPIO5
    echo_pin: GPIO18
    name: "Distance"
    update_interval: 5s
    filters:
      - median:
          window_size: 5
          send_every: 5
```

---

## Binary Sensor Patterns

### PIR Motion Sensor

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLDOWN
    name: "Motion"
    device_class: motion
    filters:
      - delayed_off: 10s
```

### Door/Window Contact Sensor

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO4
      mode: INPUT_PULLUP
      inverted: true
    name: "Door"
    device_class: door
    filters:
      - delayed_on: 100ms
      - delayed_off: 100ms
```

### Water Leak Sensor

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "Water Leak"
    device_class: moisture
```

### Button

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    filters:
      - delayed_on: 10ms
    on_press:
      - light.toggle: main_light
    on_multi_click:
      - timing:
          - ON for at most 1s
          - OFF for at most 1s
          - ON for at most 1s
          - OFF for at least 0.2s
        then:
          - logger.log: "Double click"
      - timing:
          - ON for 1s to 3s
          - OFF for at least 0.2s
        then:
          - logger.log: "Long press"
```

---

## Switch Patterns

### Relay

```yaml
switch:
  - platform: gpio
    pin: GPIO12
    name: "Relay"
    id: relay
    restore_mode: RESTORE_DEFAULT_OFF
```

### Relay with Interlock (2-Channel)

```yaml
switch:
  - platform: gpio
    pin: GPIO12
    name: "Relay 1"
    id: relay1
    interlock: [relay2]
    interlock_wait_time: 100ms

  - platform: gpio
    pin: GPIO14
    name: "Relay 2"
    id: relay2
    interlock: [relay1]
    interlock_wait_time: 100ms
```

---

## Light Patterns

### Simple On/Off Light

```yaml
light:
  - platform: binary
    name: "Light"
    output: relay_output

output:
  - platform: gpio
    pin: GPIO12
    id: relay_output
```

### Dimmable Light (PWM)

```yaml
light:
  - platform: monochromatic
    name: "Dimmable Light"
    output: pwm_output
    gamma_correct: 2.8
    default_transition_length: 500ms

output:
  - platform: ledc
    pin: GPIO12
    id: pwm_output
    frequency: 1000Hz
```

### RGB Light Strip (WS2812B/NeoPixel)

```yaml
light:
  - platform: neopixelbus
    type: GRB
    variant: WS2812X
    pin: GPIO4
    num_leds: 60
    name: "LED Strip"
    effects:
      - addressable_rainbow:
      - addressable_color_wipe:
      - addressable_scan:
      - addressable_twinkle:
      - addressable_fireworks:
```

### RGBW Light

```yaml
light:
  - platform: rgbw
    name: "RGBW Light"
    red: red_output
    green: green_output
    blue: blue_output
    white: white_output

output:
  - platform: ledc
    pin: GPIO4
    id: red_output
  - platform: ledc
    pin: GPIO5
    id: green_output
  - platform: ledc
    pin: GPIO12
    id: blue_output
  - platform: ledc
    pin: GPIO14
    id: white_output
```

### RGBWW (Warm/Cold White)

```yaml
light:
  - platform: rgbww
    name: "RGBWW Light"
    red: red_output
    green: green_output
    blue: blue_output
    cold_white: cw_output
    warm_white: ww_output
    cold_white_color_temperature: 6500 K
    warm_white_color_temperature: 2700 K
```

---

## mmWave Presence Sensor (LD2410)

```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 256000
  parity: NONE
  stop_bits: 1

ld2410:
  id: ld2410_radar

binary_sensor:
  - platform: ld2410
    has_target:
      name: "Presence"
    has_moving_target:
      name: "Moving Target"
    has_still_target:
      name: "Still Target"

sensor:
  - platform: ld2410
    moving_distance:
      name: "Moving Distance"
    still_distance:
      name: "Still Distance"
    detection_distance:
      name: "Detection Distance"

switch:
  - platform: ld2410
    engineering_mode:
      name: "Engineering Mode"
    bluetooth:
      name: "Bluetooth"
```

---

## Cover/Blind Control

```yaml
cover:
  - platform: time_based
    name: "Blinds"
    open_action:
      - switch.turn_on: relay_up
    open_duration: 30s
    close_action:
      - switch.turn_on: relay_down
    close_duration: 30s
    stop_action:
      - switch.turn_off: relay_up
      - switch.turn_off: relay_down
```

---

## Bluetooth Proxy

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true
```

---

## Voice Assistant (ESP32-S3)

```yaml
esphome:
  name: voice-assistant
  platformio_options:
    board_build.flash_mode: dio

esp32:
  board: esp32-s3-devkitc-1
  variant: esp32s3
  framework:
    type: esp-idf

i2s_audio:
  i2s_lrclk_pin: GPIO3
  i2s_bclk_pin: GPIO2

microphone:
  - platform: i2s_audio
    adc_type: external
    i2s_din_pin: GPIO4
    pdm: false
    id: mic

speaker:
  - platform: i2s_audio
    dac_type: external
    i2s_dout_pin: GPIO5
    id: speaker_out

voice_assistant:
  microphone: mic
  speaker: speaker_out
  use_wake_word: true
  on_wake_word_detected:
    - light.turn_on: led
  on_end:
    - light.turn_off: led
```

---

## Text Sensor (WiFi Info)

```yaml
text_sensor:
  - platform: wifi_info
    ip_address:
      name: "IP Address"
    ssid:
      name: "Connected SSID"
    mac_address:
      name: "MAC Address"
```

---

## Diagnostic Sensors

```yaml
sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s

  - platform: uptime
    name: "Uptime"

button:
  - platform: restart
    name: "Restart"

  - platform: safe_mode
    name: "Safe Mode"
```

---

## Common Filters

```yaml
filters:
  # Remove invalid readings
  - filter_out: nan
  - filter_out: 0.0

  # Smoothing
  - sliding_window_moving_average:
      window_size: 5
      send_every: 5

  - exponential_moving_average:
      alpha: 0.1
      send_every: 5

  - median:
      window_size: 5
      send_every: 5

  # Calibration
  - calibrate_linear:
      - 0.0 -> 0.0
      - 100.0 -> 102.5

  # Unit conversion
  - multiply: 0.001
  - offset: -273.15

  # Throttle updates
  - throttle: 60s
  - heartbeat: 300s

  # Delta (only send on change)
  - delta: 0.5

  # Round
  - round: 1
```

---

## Substitutions (Variables)

```yaml
substitutions:
  device_name: "living-room-sensor"
  friendly_name: "Living Room Sensor"
  update_interval: "60s"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "${friendly_name} Temperature"
    update_interval: ${update_interval}
```

---

## Packages (Modular Config)

```yaml
# Base package: common.yaml
esphome:
  name: ${device_name}

logger:
api:
ota:

# Device config
packages:
  common: !include common.yaml

substitutions:
  device_name: "my-device"
```

---

## Secrets

```yaml
# secrets.yaml
wifi_ssid: "MyNetwork"
wifi_password: "MyPassword"
api_key: "generated-key"
ota_password: "ota-secret"

# Device config
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  password: !secret ota_password
```
