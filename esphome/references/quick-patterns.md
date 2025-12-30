# ESPHome Quick Patterns

Common code patterns for quickly adding components to ESPHome configurations.

---

## Adding Sensors

### Temperature/Humidity (DHT)

```yaml
sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 60s
```

### Analog Input (ADC)

```yaml
sensor:
  - platform: adc
    pin: GPIO34  # ESP32 only (input-only pins)
    name: "Voltage"
    attenuation: 11db  # For 0-3.3V range
    update_interval: 5s
```

### Power Monitoring (Pulse Meter)

```yaml
sensor:
  - platform: pulse_meter
    pin: GPIO5
    name: "Power"
    unit_of_measurement: "W"
    filters:
      - multiply: 0.06  # Convert pulses to watts
```

### WiFi Signal Strength

```yaml
sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s
    entity_category: diagnostic
```

### Uptime

```yaml
sensor:
  - platform: uptime
    name: "Uptime"
    entity_category: diagnostic
```

---

## Adding Switches

### GPIO Relay

```yaml
switch:
  - platform: gpio
    pin: GPIO12
    name: "Relay"
    restore_mode: RESTORE_DEFAULT_OFF
    on_turn_on:
      - logger.log: "Relay turned on"
    on_turn_off:
      - logger.log: "Relay turned off"
```

### Template Switch (Virtual)

```yaml
switch:
  - platform: template
    name: "Virtual Switch"
    optimistic: true
    turn_on_action:
      - logger.log: "Virtual switch ON"
    turn_off_action:
      - logger.log: "Virtual switch OFF"
```

### Restart Button

```yaml
switch:
  - platform: restart
    name: "Restart Device"
```

---

## Adding Lights

### Simple On/Off Light

```yaml
output:
  - platform: gpio
    pin: GPIO13
    id: gpio_output

light:
  - platform: binary
    output: gpio_output
    name: "Light"
```

### Dimmable Light (PWM)

```yaml
output:
  - platform: ledc
    pin: GPIO16
    id: pwm_output

light:
  - platform: monochromatic
    output: pwm_output
    name: "Dimmable Light"
```

### RGB LED Strip (WS2812)

```yaml
light:
  - platform: esp32_rmt_led_strip  # ESP32 only
    pin: GPIO25
    num_leds: 30
    rmt_channel: 0
    chipset: WS2812
    name: "LED Strip"
    effects:
      - random:
      - strobe:
      - rainbow:
```

### RGBW Light

```yaml
output:
  - platform: ledc
    pin: GPIO12
    id: output_red
  - platform: ledc
    pin: GPIO13
    id: output_green
  - platform: ledc
    pin: GPIO14
    id: output_blue
  - platform: ledc
    pin: GPIO15
    id: output_white

light:
  - platform: rgbw
    name: "RGBW Light"
    red: output_red
    green: output_green
    blue: output_blue
    white: output_white
```

---

## Adding Binary Sensors

### GPIO Button

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay
```

### PIR Motion Sensor

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO14
    name: "Motion"
    device_class: motion
```

### Door/Window Contact

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO16
      mode: INPUT_PULLUP
    name: "Door"
    device_class: door
```

### Device Status

```yaml
binary_sensor:
  - platform: status
    name: "Device Status"
```

---

## Adding Text Sensors

### WiFi Info

```yaml
text_sensor:
  - platform: wifi_info
    ip_address:
      name: "IP Address"
    ssid:
      name: "Connected SSID"
```

### Version

```yaml
text_sensor:
  - platform: version
    name: "ESPHome Version"
```

---

## Complete Example: Multi-Sensor Node

```yaml
esphome:
  name: multi-sensor

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
ota:
  platform: esphome
logger:

# Temperature & Humidity
sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "Living Room Temperature"
    humidity:
      name: "Living Room Humidity"

  # WiFi Signal
  - platform: wifi_signal
    name: "WiFi Signal"
    entity_category: diagnostic

# Motion Sensor
binary_sensor:
  - platform: gpio
    pin: GPIO14
    name: "Living Room Motion"
    device_class: motion

# Relay Control
switch:
  - platform: gpio
    pin: GPIO12
    name: "Living Room Light"
    restore_mode: RESTORE_DEFAULT_OFF
```

---

## See Also

- [sensors.md](sensors.md) - Complete sensor component reference
- [lights.md](lights.md) - Advanced lighting configurations
- [automations.md](automations.md) - Triggers, conditions, and actions
- [home-assistant.md](home-assistant.md) - Home Assistant integration
