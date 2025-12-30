# ESPHome Outputs Reference

Quick reference for all ESPHome output platforms.

## Table of Contents
- [GPIO Output](#gpio-output)
- [ESP32 LEDC PWM](#esp32-ledc-pwm)
- [ESP32 DAC](#esp32-dac)
- [ESP8266 PWM](#esp8266-pwm)
- [Slow PWM](#slow-pwm)
- [AC Dimmer](#ac-dimmer)
- [LED Drivers](#led-drivers)
- [Sigma Delta](#sigma-delta)
- [Template Output](#template-output)

---

## GPIO Output

Basic digital (binary) or analog (float) output on GPIO pins.

### Binary Output
```yaml
output:
  - platform: gpio
    id: relay_output
    pin: GPIO12
```

### Float Output (requires PWM platform)
```yaml
output:
  - platform: gpio
    id: led_output
    pin: GPIO5
```

### Options
| Option | Type | Description |
|--------|------|-------------|
| `pin` | pin | GPIO pin (required) |
| `id` | id | Output ID (required) |
| `inverted` | bool | Invert output logic |
| `power_supply` | id | Power supply to enable |

### Inverted Output
```yaml
output:
  - platform: gpio
    id: relay_output
    pin:
      number: GPIO12
      inverted: true
```

---

## ESP32 LEDC PWM

Hardware PWM for ESP32 with 16 channels.

### Basic Configuration
```yaml
output:
  - platform: ledc
    id: pwm_output
    pin: GPIO5
    frequency: 1000Hz
```

### LED Brightness Control
```yaml
output:
  - platform: ledc
    id: led_pwm
    pin: GPIO2
    frequency: 19531Hz

light:
  - platform: monochromatic
    name: "LED"
    output: led_pwm
```

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `pin` | pin | required | GPIO pin |
| `frequency` | freq | 1000Hz | PWM frequency |
| `channel` | int | auto | LEDC channel (0-15) |
| `zero_means_zero` | bool | false | True 0% at min |

### Motor Speed Control
```yaml
output:
  - platform: ledc
    id: motor_speed
    pin: GPIO25
    frequency: 5000Hz

fan:
  - platform: speed
    name: "Motor"
    output: motor_speed
```

### High-Frequency for LEDs
```yaml
output:
  - platform: ledc
    id: led_pwm
    pin: GPIO5
    frequency: 19531Hz  # No visible flicker
```

---

## ESP32 DAC

True analog output (8-bit) on GPIO25/GPIO26.

### Basic Configuration
```yaml
output:
  - platform: esp32_dac
    id: dac_output
    pin: GPIO25
```

### Voltage Reference
```yaml
output:
  - platform: esp32_dac
    id: voltage_out
    pin: GPIO26

# Set to 1.65V (50% of 3.3V)
button:
  - platform: template
    name: "Set 1.65V"
    on_press:
      - output.set_level:
          id: voltage_out
          level: 50%
```

### Audio Output
```yaml
output:
  - platform: esp32_dac
    id: audio_out
    pin: GPIO25

# Note: For audio, prefer I2S speaker platform
```

---

## ESP8266 PWM

Software PWM for ESP8266.

### Basic Configuration
```yaml
output:
  - platform: esp8266_pwm
    id: pwm_output
    pin: GPIO5
    frequency: 1000Hz
```

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `pin` | pin | required | GPIO pin |
| `frequency` | freq | 1000Hz | PWM frequency (1Hz-40kHz) |

### RGB LED Strip
```yaml
output:
  - platform: esp8266_pwm
    id: red
    pin: GPIO12
    frequency: 1000Hz
  - platform: esp8266_pwm
    id: green
    pin: GPIO13
    frequency: 1000Hz
  - platform: esp8266_pwm
    id: blue
    pin: GPIO14
    frequency: 1000Hz

light:
  - platform: rgb
    name: "RGB LED"
    red: red
    green: green
    blue: blue
```

---

## Slow PWM

Software PWM for slow applications (heaters, pumps).

### Basic Configuration
```yaml
output:
  - platform: slow_pwm
    id: heater_pwm
    pin: GPIO5
    period: 10s
```

### Options
| Option | Type | Description |
|--------|------|-------------|
| `pin` | pin | GPIO pin (required) |
| `period` | time | PWM period (required) |
| `turn_on_action` | action | Custom on action |
| `turn_off_action` | action | Custom off action |

### Heater Control with PID
```yaml
output:
  - platform: slow_pwm
    id: heater_output
    pin: GPIO5
    period: 30s

climate:
  - platform: pid
    name: "Heater"
    sensor: temp_sensor
    default_target_temperature: 21°C
    heat_output: heater_output
    control_parameters:
      kp: 0.5
      ki: 0.01
      kd: 0.1
```

### Pump Duty Cycle
```yaml
output:
  - platform: slow_pwm
    id: pump_output
    period: 60s
    turn_on_action:
      - switch.turn_on: pump_relay
    turn_off_action:
      - switch.turn_off: pump_relay

number:
  - platform: template
    name: "Pump Duty Cycle"
    min_value: 0
    max_value: 100
    step: 5
    unit_of_measurement: "%"
    set_action:
      - output.set_level:
          id: pump_output
          level: !lambda "return x / 100.0;"
```

---

## AC Dimmer

Phase-cut dimmer for AC loads (requires zero-cross detection).

### RobotDyn/Krida Dimmer
```yaml
output:
  - platform: ac_dimmer
    id: dimmer_output
    gate_pin: GPIO5
    zero_cross_pin:
      number: GPIO12
      mode: INPUT
      inverted: true

light:
  - platform: monochromatic
    name: "AC Dimmer"
    output: dimmer_output
```

### Options
| Option | Type | Description |
|--------|------|-------------|
| `gate_pin` | pin | Triac gate pin (required) |
| `zero_cross_pin` | pin | Zero-cross detection (required) |
| `method` | string | leading_pulse/trailing |
| `init_with_half_cycle` | bool | Initialize with half cycle |

### Leading vs Trailing Edge
```yaml
# Leading edge (most common, for resistive loads)
output:
  - platform: ac_dimmer
    id: dimmer_leading
    gate_pin: GPIO5
    zero_cross_pin: GPIO12
    method: leading_pulse

# Trailing edge (for LED drivers, motors)
output:
  - platform: ac_dimmer
    id: dimmer_trailing
    gate_pin: GPIO5
    zero_cross_pin: GPIO12
    method: trailing
```

---

## LED Drivers

### SM16716 (RGB LED driver)
```yaml
sm16716:
  data_pin: GPIO5
  clock_pin: GPIO4
  num_channels: 3
  num_chips: 1

output:
  - platform: sm16716
    id: led_red
    channel: 0
  - platform: sm16716
    id: led_green
    channel: 1
  - platform: sm16716
    id: led_blue
    channel: 2

light:
  - platform: rgb
    name: "SM16716 LED"
    red: led_red
    green: led_green
    blue: led_blue
```

### MY9231 (AI-Thinker RGBW)
```yaml
my9231:
  data_pin: GPIO12
  clock_pin: GPIO14
  num_channels: 4
  num_chips: 1

output:
  - platform: my9231
    id: output_r
    channel: 0
  - platform: my9231
    id: output_g
    channel: 1
  - platform: my9231
    id: output_b
    channel: 2
  - platform: my9231
    id: output_w
    channel: 3

light:
  - platform: rgbw
    name: "RGBW Light"
    red: output_r
    green: output_g
    blue: output_b
    white: output_w
```

### TLC5947 (24-channel PWM driver)
```yaml
tlc5947:
  data_pin: GPIO5
  clock_pin: GPIO4
  lat_pin: GPIO15
  num_chips: 1

output:
  - platform: tlc5947
    id: pwm_0
    channel: 0
  - platform: tlc5947
    id: pwm_1
    channel: 1
  # ... up to 23 channels per chip
```

### PCA9685 (I2C PWM driver)
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

pca9685:
  frequency: 1000Hz
  address: 0x40

output:
  - platform: pca9685
    id: pwm_0
    channel: 0
  - platform: pca9685
    id: pwm_1
    channel: 1
  # ... up to 16 channels
```

### MCP4725 (I2C 12-bit DAC)
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

output:
  - platform: mcp4725
    id: dac_output
    address: 0x60
```

### MCP4728 (I2C Quad 12-bit DAC)
```yaml
mcp4728:
  address: 0x60

output:
  - platform: mcp4728
    id: dac_a
    channel: A
  - platform: mcp4728
    id: dac_b
    channel: B
  - platform: mcp4728
    id: dac_c
    channel: C
  - platform: mcp4728
    id: dac_d
    channel: D
```

---

## Sigma Delta

Sigma-delta modulation output for ESP32.

```yaml
output:
  - platform: sigma_delta_output
    id: sd_output
    pin: GPIO5
```

---

## Template Output

Create virtual outputs with custom write actions.

### Basic Template
```yaml
output:
  - platform: template
    id: custom_output
    type: float
    write_action:
      - logger.log:
          format: "Output value: %.2f"
          args: ["state"]
```

### Controlling External Device
```yaml
output:
  - platform: template
    id: external_dimmer
    type: float
    write_action:
      - uart.write:
          data: !lambda |-
            uint8_t value = state * 255;
            return {0x55, value, 0xAA};
```

### Binary Template
```yaml
output:
  - platform: template
    id: virtual_relay
    type: binary
    write_action:
      - if:
          condition:
            lambda: "return state;"
          then:
            - logger.log: "ON"
          else:
            - logger.log: "OFF"
```

---

## Output Actions

### Set Level
```yaml
on_...:
  - output.set_level:
      id: pwm_output
      level: 75%

  # Or with lambda
  - output.set_level:
      id: pwm_output
      level: !lambda "return 0.5;"
```

### Turn On/Off
```yaml
on_...:
  - output.turn_on: relay_output
  - output.turn_off: relay_output
  - output.toggle: relay_output
```

### ESP32 LEDC Set Frequency
```yaml
on_...:
  - output.ledc.set_frequency:
      id: pwm_output
      frequency: 2000Hz
```

---

## Common Patterns

### Fade LED on Boot
```yaml
esphome:
  on_boot:
    priority: -100
    then:
      - light.turn_on:
          id: status_led
          brightness: 0%
      - delay: 500ms
      - light.turn_on:
          id: status_led
          brightness: 100%
          transition_length: 2s
```

### PWM Fan with Speed Levels
```yaml
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO5
    frequency: 25000Hz  # 25kHz for 4-pin fans

fan:
  - platform: speed
    name: "Fan"
    output: fan_pwm
    speed_count: 10
```

### Multiple Outputs Same Pin (Error)
```yaml
# WRONG - will cause conflicts
output:
  - platform: ledc
    id: pwm1
    pin: GPIO5
  - platform: ledc
    id: pwm2
    pin: GPIO5  # Cannot use same pin!
```

### Power Supply Enable
```yaml
power_supply:
  - id: led_power
    pin: GPIO12
    enable_time: 20ms

output:
  - platform: ledc
    id: led_pwm
    pin: GPIO5
    power_supply: led_power  # Auto-enable PSU
```
