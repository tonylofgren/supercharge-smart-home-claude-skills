# Home Assistant ESPHome Integration Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [ESPHome Configuration](#esphome-configuration)
- [Device Types](#device-types)
- [ESPHome Events](#esphome-events)
- [ESPHome Services](#esphome-services)
- [Native API vs MQTT](#native-api-vs-mqtt)
- [Home Assistant Sensors in ESPHome](#home-assistant-sensors-in-esphome)
- [Button and Input Handling](#button-and-input-handling)
- [Deep Sleep](#deep-sleep)
- [Bluetooth Proxy](#bluetooth-proxy)
- [Voice Assist](#voice-assist)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

ESPHome is a firmware framework for ESP8266/ESP32 devices that integrates natively with Home Assistant.

### Key Terms

| Term | Description |
|------|-------------|
| **Native API** | Direct communication protocol with HA |
| **OTA** | Over-the-air firmware updates |
| **Lambda** | C++ code in ESPHome config |
| **Component** | ESPHome module (sensor, switch, etc.) |

### Benefits of ESPHome

- Native Home Assistant integration
- Auto-discovery of entities
- OTA updates from HA
- No MQTT broker required
- Real-time state updates
- Device actions and services

---

## ESPHome Configuration

### Basic Device Configuration

```yaml
# esphome/living_room_sensor.yaml

esphome:
  name: living-room-sensor
  friendly_name: Living Room Sensor

esp32:
  board: esp32dev

# Enable Home Assistant API
api:
  encryption:
    key: !secret api_encryption_key

# Enable OTA updates
ota:
  password: !secret ota_password

# WiFi configuration
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Fallback hotspot
  ap:
    ssid: "Living-Room-Sensor"
    password: !secret ap_password

# Optional: Enable web server
web_server:
  port: 80

# Logging
logger:
  level: INFO
```

### Adding to Home Assistant

1. ESPHome device auto-discovered via mDNS
2. Go to Settings > Devices & Services
3. Click "Configure" on ESPHome discovery
4. Enter encryption key if configured

### Manual Addition

```yaml
# If discovery doesn't work
# Settings > Devices & Services > Add Integration > ESPHome
# Enter: living-room-sensor.local or IP address
```

---

## Device Types

### Sensors

```yaml
# Temperature and Humidity (DHT22)
sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "Temperature"
      id: temp_sensor
    humidity:
      name: "Humidity"
    update_interval: 60s

# Analog sensor
  - platform: adc
    pin: GPIO34
    name: "Light Level"
    unit_of_measurement: "%"
    filters:
      - multiply: 100
    update_interval: 10s

# Template sensor
  - platform: template
    name: "Heat Index"
    unit_of_measurement: "°C"
    lambda: |-
      return id(temp_sensor).state * 1.8 + 32;
```

### Binary Sensors

```yaml
binary_sensor:
  # PIR motion sensor
  - platform: gpio
    pin: GPIO5
    name: "Motion"
    device_class: motion
    filters:
      - delayed_off: 30s

  # Door/window sensor
  - platform: gpio
    pin:
      number: GPIO12
      mode: INPUT_PULLUP
      inverted: true
    name: "Door"
    device_class: door

  # Button
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay
```

### Switches

```yaml
switch:
  # Relay
  - platform: gpio
    pin: GPIO13
    name: "Relay"
    id: relay

  # Template switch
  - platform: template
    name: "Virtual Switch"
    optimistic: true
    turn_on_action:
      - logger.log: "Turned on"
    turn_off_action:
      - logger.log: "Turned off"

  # Restart switch
  - platform: restart
    name: "Restart"
```

### Lights

```yaml
light:
  # Simple on/off
  - platform: binary
    name: "Light"
    output: light_output

  # PWM dimmable
  - platform: monochromatic
    name: "Dimmable Light"
    output: pwm_output
    gamma_correct: 2.8

  # RGB light
  - platform: rgb
    name: "RGB Light"
    red: red_output
    green: green_output
    blue: blue_output

  # Addressable LED (WS2812B)
  - platform: neopixelbus
    type: GRB
    variant: WS2812
    pin: GPIO2
    num_leds: 30
    name: "LED Strip"
    effects:
      - rainbow:
      - pulse:
      - strobe:

output:
  - platform: gpio
    pin: GPIO12
    id: light_output

  - platform: ledc
    pin: GPIO13
    id: pwm_output
```

### Covers

```yaml
cover:
  # Simple cover
  - platform: template
    name: "Garage Door"
    open_action:
      - switch.turn_on: relay_open
    close_action:
      - switch.turn_on: relay_close
    stop_action:
      - switch.turn_off: relay_open
      - switch.turn_off: relay_close

  # Time-based cover
  - platform: time_based
    name: "Blinds"
    open_action:
      - switch.turn_on: motor_up
    open_duration: 30s
    close_action:
      - switch.turn_on: motor_down
    close_duration: 30s
    stop_action:
      - switch.turn_off: motor_up
      - switch.turn_off: motor_down
```

### Climate

```yaml
climate:
  - platform: thermostat
    name: "Thermostat"
    sensor: temp_sensor
    default_preset: Home
    preset:
      - name: Home
        default_target_temperature_low: 20
        default_target_temperature_high: 24
      - name: Away
        default_target_temperature_low: 16
        default_target_temperature_high: 28
    heat_action:
      - switch.turn_on: heater_relay
    idle_action:
      - switch.turn_off: heater_relay
```

### Text Sensors

```yaml
text_sensor:
  # WiFi info
  - platform: wifi_info
    ip_address:
      name: "IP Address"
    ssid:
      name: "Connected SSID"
    mac_address:
      name: "MAC Address"

  # Version
  - platform: version
    name: "ESPHome Version"

  # Template
  - platform: template
    name: "Status"
    lambda: |-
      if (id(motion).state) {
        return {"Motion Detected"};
      } else {
        return {"Clear"};
      }
```

### Numbers

```yaml
number:
  - platform: template
    name: "Brightness"
    min_value: 0
    max_value: 100
    step: 10
    optimistic: true
    set_action:
      - light.turn_on:
          id: my_light
          brightness: !lambda "return x / 100.0;"
```

### Select

```yaml
select:
  - platform: template
    name: "Mode"
    options:
      - "Auto"
      - "Manual"
      - "Off"
    initial_option: "Auto"
    optimistic: true
    set_action:
      - logger.log:
          format: "Mode set to %s"
          args: ['x.c_str()']
```

### Buttons

```yaml
button:
  - platform: restart
    name: "Restart"

  - platform: template
    name: "Identify"
    on_press:
      - light.turn_on:
          id: status_led
          effect: strobe
      - delay: 5s
      - light.turn_off: status_led
```

---

## ESPHome Events

### Firing Events to Home Assistant

```yaml
# ESPHome config
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "Button"
    on_press:
      - homeassistant.event:
          event: esphome.button_pressed
          data:
            device: !lambda 'return App.get_name();'
            button: "main"

    on_double_click:
      - homeassistant.event:
          event: esphome.button_double
          data:
            device: !lambda 'return App.get_name();'
```

### Listening to Events in Home Assistant

```yaml
# Home Assistant automation
automation:
  - id: esphome_button
    trigger:
      - platform: event
        event_type: esphome.button_pressed
        event_data:
          device: "living-room-sensor"
          button: "main"
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

### Event with Dynamic Data

```yaml
# ESPHome
sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery"
    on_value_range:
      - below: 20
        then:
          - homeassistant.event:
              event: esphome.low_battery
              data:
                device: !lambda 'return App.get_name();'
                level: !lambda 'return to_string(x);'
```

---

## ESPHome Services

### Calling HA Services from ESPHome

```yaml
# ESPHome config
binary_sensor:
  - platform: gpio
    pin: GPIO0
    on_press:
      - homeassistant.service:
          service: light.toggle
          data:
            entity_id: light.living_room

      - homeassistant.service:
          service: notify.mobile_app
          data:
            message: "Button pressed!"
```

### Service with Template Data

```yaml
# ESPHome
binary_sensor:
  - platform: gpio
    pin: GPIO0
    on_press:
      - homeassistant.service:
          service: notify.mobile_app
          data:
            title: "ESPHome Alert"
            message: !lambda |-
              return "Temperature is " + to_string(id(temp_sensor).state) + "°C";
```

### Calling ESPHome Services from HA

```yaml
# Home Assistant automation
automation:
  - trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "on"
    action:
      # Call ESPHome service
      - service: esphome.living_room_sensor_set_led_color
        data:
          red: 255
          green: 0
          blue: 255
```

### Defining Custom Services in ESPHome

```yaml
# ESPHome config
api:
  services:
    - service: set_led_color
      variables:
        red: int
        green: int
        blue: int
      then:
        - light.turn_on:
            id: led_strip
            red: !lambda 'return red / 255.0;'
            green: !lambda 'return green / 255.0;'
            blue: !lambda 'return blue / 255.0;'

    - service: play_rtttl
      variables:
        song: string
      then:
        - rtttl.play:
            rtttl: !lambda 'return song;'
```

---

## Native API vs MQTT

### Native API (Recommended)

```yaml
# ESPHome config
api:
  encryption:
    key: "your-32-char-base64-key"
  reboot_timeout: 0s  # Disable reboot on disconnect

# Benefits:
# - Direct connection, lower latency
# - Auto-discovery
# - Services and events
# - Encryption support
# - No MQTT broker needed
```

### MQTT Mode

```yaml
# ESPHome config - disable API, enable MQTT
# api:  # Commented out

mqtt:
  broker: 192.168.1.100
  username: !secret mqtt_user
  password: !secret mqtt_password
  topic_prefix: esphome/living_room

# Use when:
# - Need MQTT for other integrations
# - Multiple HA instances
# - Want standard MQTT topics
```

### Hybrid (Both)

```yaml
# ESPHome config
api:
  encryption:
    key: "..."

mqtt:
  broker: 192.168.1.100
  # Entities available via both API and MQTT
```

---

## Home Assistant Sensors in ESPHome

### Import HA Entity State

```yaml
# ESPHome config
sensor:
  - platform: homeassistant
    name: "Outside Temperature"
    entity_id: sensor.outdoor_temperature
    id: outside_temp

  - platform: homeassistant
    name: "Energy Price"
    entity_id: sensor.electricity_price
    id: energy_price
```

### Use in Automations

```yaml
# ESPHome
sensor:
  - platform: homeassistant
    entity_id: sensor.outdoor_temperature
    id: outside_temp

binary_sensor:
  - platform: template
    name: "Cold Outside"
    lambda: |-
      return id(outside_temp).state < 10;
```

### Import Binary Sensor

```yaml
binary_sensor:
  - platform: homeassistant
    name: "Anyone Home"
    entity_id: binary_sensor.anyone_home
    id: presence
```

### Import Text Sensor

```yaml
text_sensor:
  - platform: homeassistant
    name: "Home Mode"
    entity_id: input_select.home_mode
    id: home_mode
```

### Conditional Logic

```yaml
# ESPHome
light:
  - platform: binary
    name: "Porch Light"
    output: porch_relay
    on_turn_on:
      - if:
          condition:
            lambda: 'return id(home_mode).state == "Away";'
          then:
            - delay: 5min
            - light.turn_off: porch_light
```

---

## Button and Input Handling

### Single Button Multiple Actions

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"

    on_press:
      - light.toggle: status_led

    on_click:
      min_length: 50ms
      max_length: 500ms
      then:
        - homeassistant.service:
            service: light.toggle
            data:
              entity_id: light.main

    on_double_click:
      min_length: 50ms
      max_length: 500ms
      then:
        - homeassistant.service:
            service: scene.turn_on
            data:
              entity_id: scene.movie_mode

    on_multi_click:
      - timing:
          - ON for at most 1s
          - OFF for at most 1s
          - ON for at most 1s
          - OFF for at least 0.2s
        then:
          - logger.log: "Triple click!"
          - homeassistant.service:
              service: script.turn_on
              data:
                entity_id: script.all_off
```

### Long Press

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "Button"

    on_press:
      then:
        - delay: 3s
        - if:
            condition:
              binary_sensor.is_on: button
            then:
              - logger.log: "Long press detected"
              - switch.toggle: relay
```

### Rotary Encoder

```yaml
sensor:
  - platform: rotary_encoder
    name: "Encoder"
    pin_a: GPIO12
    pin_b: GPIO14
    resolution: 4
    min_value: 0
    max_value: 100
    on_value:
      - homeassistant.service:
          service: light.turn_on
          data:
            entity_id: light.lamp
            brightness_pct: !lambda 'return x;'
```

---

## Deep Sleep

### Basic Deep Sleep

```yaml
deep_sleep:
  run_duration: 30s
  sleep_duration: 5min

sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
```

### Conditional Deep Sleep

```yaml
deep_sleep:
  id: deep_sleep_control
  run_duration: 30s
  sleep_duration: 5min

binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Motion"
    on_press:
      - deep_sleep.prevent: deep_sleep_control
    on_release:
      - delay: 1min
      - deep_sleep.allow: deep_sleep_control
```

### Wake on Pin

```yaml
deep_sleep:
  run_duration: 10s
  sleep_duration: 10min
  wakeup_pin: GPIO33
  wakeup_pin_mode: INVERT_WAKEUP
```

### Battery Reporting

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery Voltage"
    attenuation: 11db
    filters:
      - multiply: 2  # Voltage divider ratio
    update_interval: never
    id: battery_voltage

  - platform: template
    name: "Battery Percent"
    unit_of_measurement: "%"
    lambda: |-
      float voltage = id(battery_voltage).state;
      if (voltage > 4.2) return 100;
      if (voltage < 3.0) return 0;
      return (voltage - 3.0) / 1.2 * 100;

esphome:
  on_boot:
    then:
      - component.update: battery_voltage
      - delay: 5s
      - deep_sleep.enter: deep_sleep_control
```

---

## Bluetooth Proxy

### Enable Bluetooth Proxy

```yaml
# ESP32 only
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: true

bluetooth_proxy:
  active: true
```

### With Specific Devices

```yaml
esp32_ble_tracker:

bluetooth_proxy:
  active: true

# Also expose local BLE sensors
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
```

---

## Voice Assist

### Enable Voice Assist

```yaml
# ESP32-S3 with PSRAM recommended
i2s_audio:
  i2s_lrclk_pin: GPIO33
  i2s_bclk_pin: GPIO19

microphone:
  - platform: i2s_audio
    id: my_microphone
    adc_type: external
    i2s_din_pin: GPIO23

speaker:
  - platform: i2s_audio
    id: my_speaker
    dac_type: external
    i2s_dout_pin: GPIO22

voice_assistant:
  microphone: my_microphone
  speaker: my_speaker

  on_listening:
    - light.turn_on:
        id: status_led
        effect: pulse

  on_stt_end:
    - light.turn_off: status_led

  on_error:
    - light.turn_on:
        id: status_led
        red: 100%
        green: 0%
        blue: 0%
    - delay: 1s
    - light.turn_off: status_led
```

### Wake Word

```yaml
voice_assistant:
  microphone: my_microphone
  speaker: my_speaker
  use_wake_word: true

  on_wake_word_detected:
    - light.turn_on: status_led
```

---

## Common Patterns

### Status LED

```yaml
light:
  - platform: status_led
    name: "Status LED"
    pin: GPIO2

# Or with effects
light:
  - platform: binary
    name: "Status"
    output: led_output
    effects:
      - strobe:
      - automation:
          name: "Blink"
          sequence:
            - light.turn_on: status
            - delay: 500ms
            - light.turn_off: status
            - delay: 500ms

output:
  - platform: gpio
    pin: GPIO2
    id: led_output
```

### Connection Status Reporting

```yaml
binary_sensor:
  - platform: status
    name: "Status"

interval:
  - interval: 60s
    then:
      - if:
          condition:
            wifi.connected:
          then:
            - logger.log: "WiFi connected"
          else:
            - logger.log: "WiFi disconnected"
```

### Reboot Counter

```yaml
globals:
  - id: boot_count
    type: int
    restore_value: yes
    initial_value: '0'

esphome:
  on_boot:
    then:
      - lambda: 'id(boot_count) += 1;'

sensor:
  - platform: template
    name: "Boot Count"
    lambda: 'return id(boot_count);'
```

### Uptime Sensor

```yaml
sensor:
  - platform: uptime
    name: "Uptime"
    unit_of_measurement: "h"
    filters:
      - lambda: 'return x / 3600;'

  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s
```

---

## Best Practices

### Use Secrets

```yaml
# secrets.yaml
wifi_ssid: "MyNetwork"
wifi_password: "MyPassword"
api_key: "base64encodedkey=="
ota_password: "otapassword"

# device.yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key
```

### Meaningful Names

```yaml
esphome:
  name: living-room-sensor  # DNS-safe name
  friendly_name: "Living Room Sensor"  # Display name

sensor:
  - platform: dht
    temperature:
      name: "Living Room Temperature"  # Descriptive
```

### Update Intervals

```yaml
sensor:
  # Fast-changing values
  - platform: adc
    update_interval: 1s  # Power monitoring

  # Slow-changing values
  - platform: dht
    update_interval: 60s  # Temperature

  # Battery (deep sleep devices)
    update_interval: never  # Manual trigger
```

### Filters for Noisy Sensors

```yaml
sensor:
  - platform: adc
    name: "Temperature"
    filters:
      - sliding_window_moving_average:
          window_size: 10
          send_every: 5
      - or:
          - throttle: 60s
          - delta: 0.5
```

---

## Troubleshooting

### Device Not Discovered

| Problem | Solution |
|---------|----------|
| Not on network | Check WiFi credentials |
| mDNS blocked | Use IP address directly |
| API disabled | Ensure `api:` is in config |
| Different subnet | Enable mDNS relay on router |

### Connection Issues

```yaml
# Increase timeouts
api:
  reboot_timeout: 0s  # Disable auto-reboot

wifi:
  reboot_timeout: 0s
  power_save_mode: none  # For better stability
```

### Debug Logging

```yaml
logger:
  level: DEBUG
  logs:
    component: DEBUG
    wifi: DEBUG
    api: DEBUG
```

### OTA Update Failed

```yaml
# Increase OTA timeout
ota:
  safe_mode: true
  reboot_timeout: 10min
  num_attempts: 5

# Or use safe mode
# Hold GPIO0 during boot to enter safe mode
```

### Check Device Logs

```bash
# Via ESPHome dashboard
# Or command line
esphome logs living-room-sensor.yaml

# Via web interface
http://device-ip/
```

### Common Errors

```yaml
# Error: Component not found
# Fix: Check component name spelling

# Error: Pin already in use
# Fix: Check for duplicate pin assignments

# Error: API connection failed
# Fix: Verify encryption key matches in HA

# Error: OTA authentication failed
# Fix: Check OTA password
```
