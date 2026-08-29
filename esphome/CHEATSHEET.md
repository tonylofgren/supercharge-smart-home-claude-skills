# ESPHome Cheat Sheet

Quick reference for common ESPHome patterns and configurations.

## Board Selection

```yaml
# ESP32 (most common)
esp32:
  board: esp32dev
  framework:
    type: arduino

# ESP32-S3
esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: arduino

# ESP32-C3
esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: arduino

# ESP8266
esp8266:
  board: d1_mini
```

## Common Sensors

```yaml
# DHT22 Temperature/Humidity
sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 30s

# BME280 (I2C)
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: bme280_i2c
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    pressure:
      name: "Pressure"
    address: 0x76

# DS18B20 (Dallas)
one_wire:
  - platform: gpio
    pin: GPIO4

sensor:
  - platform: dallas_temp
    name: "Temperature"

# PIR Motion
binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Motion"
    device_class: motion
```

## Common Outputs

```yaml
# Relay
switch:
  - platform: gpio
    pin: GPIO16
    name: "Relay"

# PWM LED
output:
  - platform: ledc
    pin: GPIO4
    id: pwm_output

light:
  - platform: monochromatic
    output: pwm_output
    name: "LED"

# RGB LED Strip
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO48
    num_leds: 60
    name: "LED Strip"
    chipset: WS2812
    channel_colors: GRB
    rmt_channel: 0
```

## Filters

```yaml
sensor:
  - platform: ...
    filters:
      # Smooth readings
      - sliding_window_moving_average:
          window_size: 5
          send_every: 1

      # Calibration
      - calibrate_linear:
          - 0.0 -> 0
          - 1.0 -> 100

      # Offset/multiply
      - offset: -2.0
      - multiply: 1.8

      # Throttle updates
      - throttle: 10s

      # Remove outliers
      - median:
          window_size: 5
          send_every: 1

      # Clamp range
      - clamp:
          min_value: 0
          max_value: 100

      # Convert units
      - lambda: return x * 1.8 + 32;  # C to F
```

## Automation Actions

```yaml
# Turn on/off
- switch.turn_on: relay_id
- switch.turn_off: relay_id
- switch.toggle: relay_id

# Delay
- delay: 5s
- delay:
    minutes: 2

# Logger
- logger.log: "Something happened"
- logger.log:
    level: WARN
    format: "Value is %.2f"
    args: [id(sensor_id).state]

# Home Assistant event
- homeassistant.event:
    event: esphome.my_event
    data:
      value: !lambda 'return id(sensor_id).state;'

# Conditional
- if:
    condition:
      binary_sensor.is_on: motion_sensor
    then:
      - switch.turn_on: light
    else:
      - switch.turn_off: light

# Repeat
- repeat:
    count: 5
    then:
      - switch.toggle: led
      - delay: 200ms

# While loop
- while:
    condition:
      binary_sensor.is_on: button
    then:
      - logger.log: "Button held"
      - delay: 100ms
```

## Conditions

```yaml
condition:
  # Binary sensor state
  - binary_sensor.is_on: sensor_id
  - binary_sensor.is_off: sensor_id

  # Numeric comparison
  - lambda: 'return id(temp_sensor).state > 25;'

  # Time
  - time.has_time:

  # WiFi connected
  - wifi.connected:

  # API connected
  - api.connected:

  # Combine conditions
  - and:
      - binary_sensor.is_on: sensor1
      - binary_sensor.is_on: sensor2
  - or:
      - binary_sensor.is_on: sensor1
      - binary_sensor.is_on: sensor2
  - not:
      binary_sensor.is_on: sensor1
```

## Global Variables

```yaml
globals:
  - id: counter
    type: int
    restore_value: no
    initial_value: '0'

  - id: calibration
    type: float
    restore_value: yes
    initial_value: '1.0'

# Usage in lambda
lambda: |-
  id(counter)++;
  return id(counter);
```

## Time-Based Automation

```yaml
time:
  - platform: homeassistant
    id: ha_time
    on_time:
      - seconds: 0
        minutes: 0
        hours: 7
        then:
          - switch.turn_on: morning_light

      # Cron-style
      - cron: '0 0 7 * * *'
        then:
          - switch.turn_on: morning_light

interval:
  - interval: 5min
    then:
      - sensor.update: slow_sensor
```

## Deep Sleep

```yaml
deep_sleep:
  id: deep_sleep_control
  run_duration: 30s
  sleep_duration: 5min

# Wake on GPIO
deep_sleep:
  wakeup_pin:
    number: GPIO4
    inverted: true
    mode: INPUT_PULLUP

# Prevent/allow sleep
button:
  - platform: template
    name: "Stay Awake"
    on_press:
      - deep_sleep.prevent: deep_sleep_control

  - platform: template
    name: "Allow Sleep"
    on_press:
      - deep_sleep.allow: deep_sleep_control
```

## WiFi Configuration

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Static IP
  manual_ip:
    static_ip: 192.168.1.100
    gateway: 192.168.1.1
    subnet: 255.255.255.0

  # Fallback hotspot
  ap:
    ssid: "Device-Fallback"
    password: "password123"

  # Fast reconnect
  fast_connect: true

  # Power save mode
  power_save_mode: light  # none, light, high
```

## Common Patterns

### Button Press Duration

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO0
    id: button
    on_multi_click:
      - timing:
          - ON for at most 1s
        then:
          - logger.log: "Short press"
      - timing:
          - ON for 1s to 3s
        then:
          - logger.log: "Long press"
      - timing:
          - ON for at least 3s
        then:
          - logger.log: "Very long press"
```

### Status LED

```yaml
status_led:
  pin:
    number: GPIO2
    inverted: true
```

### Safe Boot Mode

```yaml
safe_mode:
  boot_is_good_after: 1min
  num_attempts: 5
```

### Web Server

```yaml
web_server:
  port: 80
  auth:
    username: admin
    password: !secret web_password
```

## Useful Entity Categories

```yaml
sensor:
  - platform: ...
    entity_category: diagnostic  # For WiFi signal, uptime, etc.

button:
  - platform: restart
    entity_category: config      # For restart, calibration, etc.
```

## Template Sensors

```yaml
sensor:
  - platform: template
    name: "Calculated Value"
    lambda: |-
      return id(sensor1).state + id(sensor2).state;
    update_interval: 5s

text_sensor:
  - platform: template
    name: "Status Text"
    lambda: |-
      if (id(temp).state > 25) return {"Hot"};
      if (id(temp).state > 15) return {"Normal"};
      return {"Cold"};
```

## Import from Home Assistant

```yaml
sensor:
  - platform: homeassistant
    id: outside_temp
    entity_id: sensor.outdoor_temperature

binary_sensor:
  - platform: homeassistant
    id: alarm_status
    entity_id: binary_sensor.alarm_armed

text_sensor:
  - platform: homeassistant
    id: weather_condition
    entity_id: weather.home
    attribute: condition
```

## Quick Debug

```text
logger:
  level: DEBUG

# In lambda
ESP_LOGD("tag", "Debug: %.2f", value);
ESP_LOGI("tag", "Info message");
ESP_LOGW("tag", "Warning message");
ESP_LOGE("tag", "Error message");
```
