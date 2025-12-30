# ESPHome Power Management Reference

Complete guide to deep sleep, battery monitoring, and power optimization for battery-powered devices.

## Table of Contents

- [Deep Sleep Overview](#deep-sleep-overview)
- [Deep Sleep Configuration](#deep-sleep-configuration)
- [Wakeup Sources](#wakeup-sources)
- [Battery Monitoring](#battery-monitoring)
- [Power Optimization](#power-optimization)
- [ESP32 vs ESP8266](#esp32-vs-esp8266)
- [Real-World Battery Life](#real-world-battery-life)
- [Low-Power Sensors](#low-power-sensors)
- [Complete Examples](#complete-examples)

---

## Deep Sleep Overview

Deep sleep dramatically reduces power consumption by shutting down most of the chip.

| State | ESP32 Current | ESP8266 Current |
|-------|---------------|-----------------|
| Active + WiFi | 80-260 mA | 70-200 mA |
| Modem Sleep | 3-20 mA | 15-20 mA |
| Light Sleep | 0.8-2 mA | 0.4-1 mA |
| Deep Sleep | 10-150 µA | 10-20 µA |
| Deep Sleep + RTC | 5-10 µA | N/A |

---

## Deep Sleep Configuration

### Basic Deep Sleep

```yaml
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
```

### With ID for Control

```yaml
deep_sleep:
  id: deep_sleep_control
  run_duration: 30s
  sleep_duration: 5min
```

### Prevent Sleep (For OTA)

```yaml
deep_sleep:
  id: deep_sleep_control
  run_duration: 30s
  sleep_duration: 5min

# Keep awake when Home Assistant connected
api:
  on_client_connected:
    - deep_sleep.prevent: deep_sleep_control
  on_client_disconnected:
    - deep_sleep.allow: deep_sleep_control
```

### OTA-Safe Configuration

```yaml
deep_sleep:
  id: deep_sleep_control
  run_duration: 30s
  sleep_duration: 5min

# OTA keeps device awake
ota:
  on_begin:
    - deep_sleep.prevent: deep_sleep_control
  on_end:
    - deep_sleep.allow: deep_sleep_control
  on_error:
    - deep_sleep.allow: deep_sleep_control

# Button to prevent sleep for OTA
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "OTA Mode"
    on_press:
      - deep_sleep.prevent: deep_sleep_control
      - logger.log: "Deep sleep prevented for OTA"
```

### Dynamic Sleep Duration

```yaml
deep_sleep:
  id: deep_sleep_control
  run_duration: 30s

globals:
  - id: sleep_minutes
    type: int
    initial_value: '5'

script:
  - id: enter_sleep
    then:
      - deep_sleep.enter:
          id: deep_sleep_control
          sleep_duration: !lambda "return id(sleep_minutes) * 60000;"
```

---

## Wakeup Sources

### Timer Wakeup (Default)

```yaml
deep_sleep:
  sleep_duration: 10min
```

### GPIO Wakeup (ESP32)

```yaml
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
  wakeup_pin: GPIO33
  wakeup_pin_mode: INVERT_WAKEUP  # Wake on LOW
```

### Multiple GPIO Wakeup (ESP32)

```yaml
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
  esp32_ext1_wakeup:
    pins:
      - GPIO33
      - GPIO34
      - GPIO35
    mode: ANY_HIGH  # Wake if ANY pin goes high
    # mode: ALL_LOW  # Wake if ALL pins go low
```

### Touch Wakeup (ESP32)

```yaml
esp32_touch:
  setup_mode: false
  sleep_duration: 10ms
  measurement_duration: 1ms

deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
  touch_wakeup: true

binary_sensor:
  - platform: esp32_touch
    pin: GPIO4
    name: "Touch Pad"
    threshold: 1000
    wakeup_threshold: 800  # More sensitive for wakeup
```

### Wakeup Cause Detection

```yaml
text_sensor:
  - platform: template
    name: "Wakeup Reason"
    id: wakeup_reason
    update_interval: never

esphome:
  on_boot:
    priority: 600
    then:
      - lambda: |-
          #ifdef USE_ESP32
          switch(esp_sleep_get_wakeup_cause()) {
            case ESP_SLEEP_WAKEUP_TIMER:
              id(wakeup_reason).publish_state("Timer");
              break;
            case ESP_SLEEP_WAKEUP_EXT0:
              id(wakeup_reason).publish_state("External GPIO");
              break;
            case ESP_SLEEP_WAKEUP_EXT1:
              id(wakeup_reason).publish_state("External GPIO (EXT1)");
              break;
            case ESP_SLEEP_WAKEUP_TOUCHPAD:
              id(wakeup_reason).publish_state("Touch");
              break;
            default:
              id(wakeup_reason).publish_state("Power On / Reset");
          }
          #endif
```

---

## Battery Monitoring

### Basic ADC Battery

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery Voltage"
    id: battery_voltage
    update_interval: 60s
    attenuation: 11db
    filters:
      - multiply: 2  # Voltage divider 2:1
    unit_of_measurement: "V"
```

### Battery Percentage

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    id: battery_voltage
    attenuation: 11db
    filters:
      - multiply: 2

  - platform: template
    name: "Battery Percentage"
    unit_of_measurement: "%"
    accuracy_decimals: 0
    lambda: |-
      float voltage = id(battery_voltage).state;
      // LiPo: 4.2V = 100%, 3.0V = 0%
      float percentage = (voltage - 3.0) / (4.2 - 3.0) * 100;
      if (percentage > 100) percentage = 100;
      if (percentage < 0) percentage = 0;
      return percentage;
    update_interval: 60s
```

### Low Battery Warning

```yaml
binary_sensor:
  - platform: template
    name: "Low Battery"
    device_class: battery
    lambda: |-
      return id(battery_voltage).state < 3.3;

sensor:
  - platform: adc
    pin: GPIO34
    id: battery_voltage
    attenuation: 11db
    filters:
      - multiply: 2
    on_value_range:
      - below: 3.2
        then:
          - logger.log: "CRITICAL: Battery very low!"
          - deep_sleep.enter:
              id: deep_sleep_control
              sleep_duration: 1h  # Sleep longer to preserve battery
```

### Battery with Averaging

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery Voltage"
    attenuation: 11db
    filters:
      - multiply: 2
      - sliding_window_moving_average:
          window_size: 10
          send_every: 5
    update_interval: 10s
```

---

## Power Optimization

### Reduce WiFi Power

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  power_save_mode: light  # or: none, light, high
  fast_connect: true  # Skip scanning, connect directly
  output_power: 17dB  # Reduce from 20dB default
```

### Disable Unused Features

```yaml
# Only enable what you need
logger:
  level: WARN  # Less logging = less power
  baud_rate: 0  # Disable serial logging

# Remove if not needed:
# captive_portal:
# web_server:
```

### Efficient Sensor Reading

```yaml
sensor:
  - platform: dht
    pin: GPIO4
    update_interval: never  # Manual updates only
    id: dht_sensor

interval:
  - interval: 30s
    then:
      - component.update: dht_sensor
      - delay: 2s  # Wait for reading
      - deep_sleep.enter: deep_sleep_control
```

### GPIO Power Control

```yaml
# Power sensor via GPIO (cut power during sleep)
output:
  - platform: gpio
    pin: GPIO5
    id: sensor_power

sensor:
  - platform: adc
    pin: GPIO34
    id: soil_moisture

script:
  - id: read_sensor
    then:
      - output.turn_on: sensor_power
      - delay: 100ms  # Let sensor stabilize
      - component.update: soil_moisture
      - output.turn_off: sensor_power
```

### Disable LEDs

```yaml
status_led:
  pin:
    number: GPIO2
    inverted: true
# Or remove status_led entirely

# Disable WiFi LED on some modules
esphome:
  on_boot:
    then:
      - lambda: |-
          // Disable onboard LED
          gpio_set_direction(GPIO_NUM_2, GPIO_MODE_OUTPUT);
          gpio_set_level(GPIO_NUM_2, 0);
```

---

## ESP32 vs ESP8266

### ESP32 Deep Sleep

```yaml
# ESP32 specific features
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
  # GPIO wakeup (RTC GPIOs only)
  wakeup_pin: GPIO33
  # Or multiple pins
  esp32_ext1_wakeup:
    pins: [GPIO33, GPIO34]
    mode: ANY_HIGH
  # Touch wakeup
  touch_wakeup: true
```

RTC GPIOs (usable for wakeup): GPIO0, 2, 4, 12-15, 25-27, 32-39

### ESP8266 Deep Sleep

```yaml
# ESP8266 requires GPIO16 connected to RST
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
  # No GPIO wakeup support
  # Must wire GPIO16 -> RST for timer wakeup
```

**Hardware requirement**: Connect GPIO16 to RST pin for wakeup.

### ESP32-C3/S2/S3

```yaml
# Similar to ESP32, check specific GPIO numbers
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min
  wakeup_pin: GPIO3  # Check your variant's RTC GPIOs
```

---

## Real-World Battery Life

### Calculation Formula

```
Battery Life (hours) = Battery Capacity (mAh) / Average Current (mA)
```

### Example Calculations

| Scenario | Sleep | Wake | Duty Cycle | Avg Current | 2000mAh Life |
|----------|-------|------|------------|-------------|--------------|
| Always on | - | 80mA | 100% | 80mA | 25 hours |
| 30s/5min | 50µA | 80mA | 10% | 8mA | 250 hours |
| 30s/30min | 50µA | 80mA | 1.7% | 1.4mA | 60 days |
| 30s/60min | 50µA | 80mA | 0.8% | 0.7mA | 120 days |

### Measuring Current

```yaml
# Debug: log actual wake time
globals:
  - id: boot_time
    type: uint32_t
    initial_value: '0'

esphome:
  on_boot:
    then:
      - lambda: id(boot_time) = millis();

deep_sleep:
  run_duration: 30s
  sleep_duration: 5min

sensor:
  - platform: template
    name: "Wake Duration"
    unit_of_measurement: "ms"
    lambda: return millis() - id(boot_time);
    update_interval: 25s  # Just before sleep
```

---

## Low-Power Sensors

### I2C Power Control

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22
  scan: false  # Faster boot

output:
  - platform: gpio
    pin: GPIO5
    id: i2c_power

sensor:
  - platform: bme280
    # ...
    update_interval: never

script:
  - id: read_sensors
    then:
      - output.turn_on: i2c_power
      - delay: 50ms
      - component.update: bme280_sensor
      - delay: 100ms
      - output.turn_off: i2c_power
```

### Recommended Low-Power Sensors

| Sensor | Sleep Current | Active Current | Use Case |
|--------|---------------|----------------|----------|
| BME280 | 0.1 µA | 350 µA | Temp/Humidity/Pressure |
| HDC1080 | 0.1 µA | 190 µA | Temp/Humidity |
| SHT40 | 0.08 µA | 600 µA | Temp/Humidity |
| BH1750 | 1 µA | 120 µA | Light |
| VL53L0X | 5 µA | 19 mA | Distance |

---

## Complete Examples

### Battery Temperature Sensor

```yaml
esphome:
  name: battery-temp-sensor

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true
  power_save_mode: light

api:
  encryption:
    key: !secret api_key

ota:
  platform: esphome
  on_begin:
    - deep_sleep.prevent: deep_sleep_1

logger:
  level: WARN
  baud_rate: 0

deep_sleep:
  id: deep_sleep_1
  run_duration: 30s
  sleep_duration: 5min

sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery"
    attenuation: 11db
    filters:
      - multiply: 2
    on_value_range:
      - below: 3.2
        then:
          - deep_sleep.enter:
              sleep_duration: 1h

  - platform: dht
    pin: GPIO4
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
```

### Door Sensor (Wake on Open)

```yaml
esphome:
  name: door-sensor

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true

api:
  encryption:
    key: !secret api_key

logger:
  level: WARN
  baud_rate: 0

deep_sleep:
  id: deep_sleep_1
  run_duration: 5s
  sleep_duration: 0s  # Sleep forever until wakeup
  wakeup_pin:
    number: GPIO33
    mode: INPUT_PULLUP
  wakeup_pin_mode: INVERT_WAKEUP

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO33
      mode: INPUT_PULLUP
    name: "Door"
    device_class: door
    on_press:
      - homeassistant.event:
          event: esphome.door_opened
      - delay: 3s
      - deep_sleep.enter: deep_sleep_1
    on_release:
      - homeassistant.event:
          event: esphome.door_closed
      - delay: 3s
      - deep_sleep.enter: deep_sleep_1

sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery"
    attenuation: 11db
    filters:
      - multiply: 2
```

### Solar-Powered Weather Station

```yaml
esphome:
  name: solar-weather

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true
  power_save_mode: high

api:
  encryption:
    key: !secret api_key

logger:
  level: ERROR
  baud_rate: 0

deep_sleep:
  id: deep_sleep_1
  run_duration: 45s

# Adjust sleep based on battery
globals:
  - id: sleep_minutes
    type: int
    initial_value: '10'

sensor:
  - platform: adc
    pin: GPIO34
    id: battery_voltage
    attenuation: 11db
    filters:
      - multiply: 2
    on_value:
      - lambda: |-
          if (x > 4.0) id(sleep_minutes) = 5;    // Plenty of charge
          else if (x > 3.7) id(sleep_minutes) = 10;
          else if (x > 3.5) id(sleep_minutes) = 30;
          else id(sleep_minutes) = 60;            // Low battery

  - platform: template
    name: "Battery"
    unit_of_measurement: "V"
    lambda: return id(battery_voltage).state;

  - platform: bme280_i2c
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    pressure:
      name: "Pressure"

script:
  - id: enter_sleep
    then:
      - deep_sleep.enter:
          id: deep_sleep_1
          sleep_duration: !lambda "return id(sleep_minutes) * 60 * 1000;"

esphome:
  on_boot:
    priority: -100
    then:
      - delay: 40s
      - script.execute: enter_sleep
```
