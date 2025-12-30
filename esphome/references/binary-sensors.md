# ESPHome Binary Sensors Reference

Complete guide to binary sensors: motion, door/window, touch, NFC, buttons, and more.

## Table of Contents

- [GPIO Binary Sensors](#gpio-binary-sensors)
- [Motion Sensors (PIR)](#motion-sensors-pir)
- [Door/Window Sensors](#doorwindow-sensors)
- [Touch Sensors](#touch-sensors)
- [NFC/RFID Readers](#nfcrfid-readers)
- [Capacitive Touch ICs](#capacitive-touch-ics)
- [Radar/Microwave Sensors](#radarmicrowave-sensors)
- [Status Sensors](#status-sensors)
- [Template Sensors](#template-sensors)
- [Filters and Debouncing](#filters-and-debouncing)
- [Automation Triggers](#automation-triggers)

---

## GPIO Binary Sensors

### Basic GPIO Input

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Button"
```

### With Pull-up (Most Common)

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true  # Button connects to GND
    name: "Button"
```

### With Pull-down

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLDOWN
    name: "Button"
```

### Device Classes

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Motion Sensor"
    device_class: motion  # Affects icon in HA

# Available device classes:
# - battery, battery_charging
# - cold, heat
# - connectivity, plug, power
# - door, garage_door, opening, window
# - gas, moisture, problem, safety, smoke, tamper
# - light, motion, moving, occupancy, presence, vibration
# - lock, running, sound, update
```

---

## Motion Sensors (PIR)

### HC-SR501 (Most Common)

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO27
    name: "Motion"
    device_class: motion
    filters:
      - delayed_off: 10s  # Keep active after motion stops
```

### AM312 (Mini PIR)

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO26
    name: "Mini Motion"
    device_class: motion
```

### Multiple PIR Zones

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO27
    name: "Zone 1 Motion"
    device_class: motion
    id: zone1

  - platform: gpio
    pin: GPIO26
    name: "Zone 2 Motion"
    device_class: motion
    id: zone2

  # Combined motion sensor
  - platform: template
    name: "Any Motion"
    device_class: motion
    lambda: |-
      return id(zone1).state || id(zone2).state;
```

### Motion with Light Control

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO27
    name: "Motion"
    device_class: motion
    on_press:
      - light.turn_on:
          id: ceiling_light
          transition_length: 1s
    on_release:
      - delay: 5min
      - light.turn_off:
          id: ceiling_light
          transition_length: 3s
```

---

## Door/Window Sensors

### Reed Switch (Magnetic)

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
    name: "Front Door"
    device_class: door
    filters:
      - delayed_on: 50ms
      - delayed_off: 50ms
```

### Window Sensor

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO12
      mode: INPUT_PULLUP
    name: "Window"
    device_class: window
```

### Garage Door State

```yaml
binary_sensor:
  # Open sensor
  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
    name: "Garage Open"
    id: garage_open

  # Closed sensor
  - platform: gpio
    pin:
      number: GPIO27
      mode: INPUT_PULLUP
    name: "Garage Closed"
    id: garage_closed

cover:
  - platform: template
    name: "Garage Door"
    device_class: garage
    lambda: |-
      if (id(garage_open).state) return COVER_OPEN;
      if (id(garage_closed).state) return COVER_CLOSED;
      return {};
```

### Door with Notification

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
    name: "Front Door"
    device_class: door
    on_press:
      - homeassistant.event:
          event: esphome.door_opened
          data:
            door: "front"
    on_release:
      - homeassistant.event:
          event: esphome.door_closed
          data:
            door: "front"
```

---

## Touch Sensors

### ESP32 Built-in Touch

```yaml
esp32_touch:
  setup_mode: false  # Set true to calibrate

binary_sensor:
  - platform: esp32_touch
    pin: GPIO4
    name: "Touch Button 1"
    threshold: 1000

  - platform: esp32_touch
    pin: GPIO15
    name: "Touch Button 2"
    threshold: 1000

  - platform: esp32_touch
    pin: GPIO13
    name: "Touch Button 3"
    threshold: 1200
```

### Touch Pins by ESP32 Variant

| ESP32 | Touch Pins |
|-------|------------|
| ESP32 | GPIO0,2,4,12,13,14,15,27,32,33 |
| ESP32-S2 | GPIO1-14 |
| ESP32-S3 | GPIO1-14 |

### Calibration Mode

```yaml
esp32_touch:
  setup_mode: true  # Enable to see threshold values in logs

binary_sensor:
  - platform: esp32_touch
    pin: GPIO4
    name: "Touch"
    threshold: 1000
```

Check logs for actual values, then set threshold ~80% of untouched value.

### Touch with Long Press

```yaml
binary_sensor:
  - platform: esp32_touch
    pin: GPIO4
    name: "Touch Button"
    threshold: 1000
    on_press:
      - logger.log: "Touched"
    on_click:
      min_length: 50ms
      max_length: 500ms
      then:
        - light.toggle: led
    on_click:
      min_length: 1s
      max_length: 5s
      then:
        - switch.toggle: relay
```

---

## NFC/RFID Readers

### RC522 (SPI)

```yaml
spi:
  clk_pin: GPIO18
  miso_pin: GPIO19
  mosi_pin: GPIO23

rc522_spi:
  cs_pin: GPIO5
  update_interval: 1s

binary_sensor:
  - platform: rc522
    uid: AA-BB-CC-DD
    name: "NFC Tag 1"
    on_press:
      - switch.turn_on: door_lock
      - delay: 5s
      - switch.turn_off: door_lock

  - platform: rc522
    uid: 11-22-33-44
    name: "NFC Tag 2"
```

### PN532 (I2C)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

pn532_i2c:
  update_interval: 500ms

binary_sensor:
  - platform: pn532
    uid: AA-BB-CC-DD
    name: "Card 1"
```

### PN532 (SPI)

```yaml
spi:
  clk_pin: GPIO18
  miso_pin: GPIO19
  mosi_pin: GPIO23

pn532_spi:
  cs_pin: GPIO5
  update_interval: 500ms

binary_sensor:
  - platform: pn532
    uid: AA-BB-CC-DD
    name: "Card 1"
```

### Tag UID Text Sensor

```yaml
text_sensor:
  - platform: pn532
    name: "NFC Tag UID"
    on_value:
      - logger.log:
          format: "Tag scanned: %s"
          args: ['x.c_str()']
```

### RDM6300 (125kHz RFID)

```yaml
uart:
  rx_pin: GPIO16
  baud_rate: 9600

rdm6300:

binary_sensor:
  - platform: rdm6300
    uid: 12345678
    name: "RFID Card 1"
```

---

## Capacitive Touch ICs

### TTP223 (Single Button)

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Touch Button"
    filters:
      - delayed_on: 50ms
```

### MPR121 (12 Channels)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

mpr121:
  id: mpr121_hub
  address: 0x5A

binary_sensor:
  - platform: mpr121
    id: touch_0
    channel: 0
    name: "Touch Pad 0"

  - platform: mpr121
    id: touch_1
    channel: 1
    name: "Touch Pad 1"

  # ... up to channel 11
```

### CAP1188 (8 Channels)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

cap1188:
  id: cap1188_hub
  address: 0x29
  touch_threshold: 0x20
  allow_multiple_touches: true

binary_sensor:
  - platform: cap1188
    id: touch_0
    channel: 0
    name: "Touch 0"
```

### Touch Panel Controllers

#### GT911 (Capacitive Touch Screen)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

gt911:
  id: touch_screen
  interrupt_pin: GPIO36

binary_sensor:
  - platform: gt911
    name: "Touch Detected"
```

#### FT5x06 (Capacitive Touch Screen)

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

ft5x06:
  id: touch_screen
  interrupt_pin: GPIO36

binary_sensor:
  - platform: ft5x06
    name: "Screen Touched"
```

---

## Radar/Microwave Sensors

### RCWL-0516 (Doppler Radar)

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO27
    name: "Radar Motion"
    device_class: motion
```

### HLK-LD2410 (mmWave)

```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 256000
  parity: NONE
  stop_bits: 1

ld2410:

binary_sensor:
  - platform: ld2410
    has_target:
      name: "Presence"
    has_moving_target:
      name: "Moving"
    has_still_target:
      name: "Still"

sensor:
  - platform: ld2410
    moving_distance:
      name: "Moving Distance"
    still_distance:
      name: "Still Distance"
    detection_distance:
      name: "Detection Distance"
```

### HLK-LD2420

```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 115200

ld2420:

binary_sensor:
  - platform: ld2420
    has_target:
      name: "Presence"
```

---

## Status Sensors

### Device Status

```yaml
binary_sensor:
  - platform: status
    name: "Device Status"
```

### WiFi Connection Status

```yaml
binary_sensor:
  - platform: template
    name: "WiFi Connected"
    lambda: |-
      return WiFi.status() == WL_CONNECTED;
```

### Home Assistant API Status

```yaml
binary_sensor:
  - platform: template
    name: "HA Connected"
    lambda: |-
      return global_api_server->is_connected();
```

---

## Template Sensors

### Basic Template

```yaml
binary_sensor:
  - platform: template
    name: "High Temperature"
    lambda: |-
      return id(temperature).state > 30;
```

### Combining Sensors

```yaml
binary_sensor:
  - platform: template
    name: "Occupied"
    device_class: occupancy
    lambda: |-
      return id(motion).state || id(door).state;
```

### With Delay

```yaml
binary_sensor:
  - platform: template
    name: "Room Occupied"
    lambda: |-
      return id(motion).state;
    filters:
      - delayed_off: 10min
```

### Threshold-based

```yaml
binary_sensor:
  - platform: template
    name: "Low Battery"
    device_class: battery
    lambda: |-
      return id(battery_voltage).state < 3.3;
```

---

## Filters and Debouncing

### Available Filters

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Filtered Input"
    filters:
      # Delay turning on
      - delayed_on: 100ms

      # Delay turning off
      - delayed_off: 100ms

      # Delay both
      - delayed_on_off: 100ms

      # Invert state
      - invert:

      # Auto-off after time
      - autooff: 5s

      # Lambda filter
      - lambda: |-
          return x && id(enable_switch).state;
```

### Mechanical Button Debounce

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
    name: "Button"
    filters:
      - delayed_on: 10ms
      - delayed_off: 10ms
```

### Reed Switch Debounce

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
    name: "Door"
    device_class: door
    filters:
      - delayed_on: 50ms
      - delayed_off: 50ms
```

### PIR Motion Hold

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO27
    name: "Motion"
    device_class: motion
    filters:
      - delayed_off: 30s  # Stay on 30s after motion stops
```

---

## Automation Triggers

### Button Press Events

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"

    on_press:
      - logger.log: "Button pressed"

    on_release:
      - logger.log: "Button released"

    on_state:
      - logger.log:
          format: "Button state: %d"
          args: ['x']
```

### Click Detection

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"

    # Single click
    on_click:
      min_length: 50ms
      max_length: 350ms
      then:
        - light.toggle: led

    # Double click
    on_double_click:
      min_length: 50ms
      max_length: 350ms
      then:
        - switch.toggle: relay

    # Long press
    on_click:
      min_length: 1s
      max_length: 5s
      then:
        - button.press: restart_button
```

### Multi-click Detection

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_multi_click:
      # Single click
      - timing:
          - ON for at most 0.5s
          - OFF for at least 0.3s
        then:
          - light.toggle: led

      # Double click
      - timing:
          - ON for at most 0.5s
          - OFF for at most 0.3s
          - ON for at most 0.5s
          - OFF for at least 0.2s
        then:
          - light.turn_on:
              id: led
              brightness: 100%

      # Triple click
      - timing:
          - ON for at most 0.5s
          - OFF for at most 0.3s
          - ON for at most 0.5s
          - OFF for at most 0.3s
          - ON for at most 0.5s
          - OFF for at least 0.2s
        then:
          - switch.toggle: relay

      # Long press
      - timing:
          - ON for at least 1s
        then:
          - button.press: restart_button
```

---

## Complete Examples

### Smart Doorbell

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "Doorbell"
    on_press:
      - homeassistant.event:
          event: esphome.doorbell_pressed
      - rtttl.play: "doorbell:d=4,o=5,b=100:e,g,c6"
```

### Security Zone

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
    name: "Entry Door"
    device_class: door
    id: entry_door

  - platform: gpio
    pin:
      number: GPIO27
      mode: INPUT_PULLUP
    name: "Window 1"
    device_class: window
    id: window1

  - platform: template
    name: "Security Breach"
    device_class: safety
    lambda: |-
      if (!id(alarm_armed).state) return false;
      return id(entry_door).state || id(window1).state;
    on_press:
      - homeassistant.event:
          event: esphome.security_breach
```

### Water Leak Detector

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO34
      mode: INPUT
    name: "Water Leak"
    device_class: moisture
    filters:
      - delayed_on: 1s
    on_press:
      - homeassistant.event:
          event: esphome.water_leak
          data:
            location: "Kitchen"
```
