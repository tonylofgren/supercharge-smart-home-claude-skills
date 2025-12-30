# ESPHome Covers and Fans Reference

Complete reference for cover (blinds, garage doors) and fan platforms.

## Table of Contents
- [Cover Basics](#cover-basics)
- [Time-Based Cover](#time-based-cover)
- [Endstop Cover](#endstop-cover)
- [Template Cover](#template-cover)
- [Current-Based Cover](#current-based-cover)
- [Fan Basics](#fan-basics)
- [Speed Fan](#speed-fan)
- [Binary Fan](#binary-fan)
- [Tuya Fan](#tuya-fan)
- [Template Fan](#template-fan)

---

## Cover Basics

All cover platforms share common configuration.

### Common Options
| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Name in Home Assistant |
| `device_class` | string | blind, curtain, garage, door, etc. |
| `assumed_state` | bool | Show buttons even if state unknown |

### Device Classes
```yaml
cover:
  - platform: ...
    device_class: blind     # Blinds/shades
    # device_class: curtain   # Curtains
    # device_class: garage    # Garage door
    # device_class: door      # Generic door
    # device_class: gate      # Gate
    # device_class: shade     # Window shade
    # device_class: shutter   # Roller shutter
    # device_class: awning    # Awning
    # device_class: damper    # Damper
```

---

## Time-Based Cover

Controls covers by timing motor run duration.

### Basic Roller Blind
```yaml
cover:
  - platform: time_based
    name: "Roller Blind"
    device_class: blind

    open_action:
      - switch.turn_on: motor_up
    open_duration: 15s

    close_action:
      - switch.turn_on: motor_down
    close_duration: 14s

    stop_action:
      - switch.turn_off: motor_up
      - switch.turn_off: motor_down

switch:
  - platform: gpio
    id: motor_up
    pin: GPIO5
    interlock: [motor_down]
  - platform: gpio
    id: motor_down
    pin: GPIO4
    interlock: [motor_up]
```

### Options
| Option | Type | Description |
|--------|------|-------------|
| `open_action` | action | Actions to open cover |
| `open_duration` | time | Time for full open (required) |
| `close_action` | action | Actions to close cover |
| `close_duration` | time | Time for full close (required) |
| `stop_action` | action | Actions to stop cover (required) |
| `has_built_in_endstop` | bool | Motor stops automatically |
| `manual_control` | bool | Allow manual button control |

### With Built-in Endstop
```yaml
cover:
  - platform: time_based
    name: "Motorized Shade"
    has_built_in_endstop: true

    open_action:
      - switch.turn_on: motor_up
    open_duration: 20s

    close_action:
      - switch.turn_on: motor_down
    close_duration: 19s

    stop_action:
      - switch.turn_off: motor_up
      - switch.turn_off: motor_down
```

### Manual Control Buttons
```yaml
cover:
  - platform: time_based
    id: my_cover
    manual_control: true
    # ...

binary_sensor:
  - platform: gpio
    pin: GPIO12
    name: "Up Button"
    on_press:
      - cover.open: my_cover
    on_release:
      - cover.stop: my_cover

  - platform: gpio
    pin: GPIO13
    name: "Down Button"
    on_press:
      - cover.close: my_cover
    on_release:
      - cover.stop: my_cover
```

---

## Endstop Cover

Uses physical endstop sensors for position.

### Basic Setup
```yaml
cover:
  - platform: endstop
    name: "Garage Door"
    device_class: garage

    open_action:
      - switch.turn_on: motor_open
    open_duration: 30s
    open_endstop: endstop_open

    close_action:
      - switch.turn_on: motor_close
    close_duration: 28s
    close_endstop: endstop_closed

    stop_action:
      - switch.turn_off: motor_open
      - switch.turn_off: motor_close

    max_duration: 35s

binary_sensor:
  - platform: gpio
    id: endstop_open
    pin: GPIO14
    filters:
      - delayed_on: 100ms
  - platform: gpio
    id: endstop_closed
    pin: GPIO12
    filters:
      - delayed_on: 100ms
```

### Options
| Option | Type | Description |
|--------|------|-------------|
| `open_endstop` | sensor | Sensor for fully open |
| `close_endstop` | sensor | Sensor for fully closed |
| `max_duration` | time | Safety timeout |

---

## Template Cover

Fully custom cover logic.

### Simple Template
```yaml
cover:
  - platform: template
    name: "Custom Cover"
    lambda: |-
      if (id(endstop_open).state) {
        return COVER_OPEN;
      } else if (id(endstop_closed).state) {
        return COVER_CLOSED;
      } else {
        return {};  // Unknown
      }
    open_action:
      - switch.turn_on: motor_open
    close_action:
      - switch.turn_on: motor_close
    stop_action:
      - switch.turn_off: motor_open
      - switch.turn_off: motor_close
```

### With Position
```yaml
cover:
  - platform: template
    name: "Positioned Cover"
    lambda: |-
      return id(cover_position);
    open_action:
      - globals.set:
          id: cover_moving
          value: "1"  # Opening
      - switch.turn_on: motor_open
    close_action:
      - globals.set:
          id: cover_moving
          value: "-1"  # Closing
      - switch.turn_on: motor_close
    stop_action:
      - globals.set:
          id: cover_moving
          value: "0"
      - switch.turn_off: motor_open
      - switch.turn_off: motor_close
    position_action:
      - logger.log:
          format: "Move to position: %.2f"
          args: ["pos"]
    has_position: true

globals:
  - id: cover_position
    type: float
    initial_value: "0.5"
  - id: cover_moving
    type: int
    initial_value: "0"
```

### Tilt Support
```yaml
cover:
  - platform: template
    name: "Venetian Blind"
    has_position: true
    tilt_lambda: |-
      return id(tilt_position);
    tilt_action:
      - servo.write:
          id: tilt_servo
          level: !lambda "return tilt * 2 - 1;"  # -1 to 1

globals:
  - id: tilt_position
    type: float
    initial_value: "0.5"
```

---

## Current-Based Cover

Detects endstop by motor current spike.

### Using ADC
```yaml
sensor:
  - platform: adc
    pin: GPIO34
    id: motor_current
    update_interval: 100ms
    filters:
      - multiply: 3.3  # Convert to current

cover:
  - platform: template
    name: "Current Cover"
    open_action:
      - switch.turn_on: motor_open
      - wait_until:
          condition:
            sensor.in_range:
              id: motor_current
              above: 2.0  # Current spike = endstop
          timeout: 30s
      - switch.turn_off: motor_open
```

---

## Cover Actions

### Open/Close/Stop
```yaml
on_...:
  - cover.open: my_cover
  - cover.close: my_cover
  - cover.stop: my_cover
  - cover.toggle: my_cover
```

### Set Position
```yaml
on_...:
  - cover.control:
      id: my_cover
      position: 50%  # 0% = closed, 100% = open

  # Or with lambda
  - cover.control:
      id: my_cover
      position: !lambda "return 0.75;"
```

### Set Tilt
```yaml
on_...:
  - cover.control:
      id: my_cover
      tilt: 45%
```

---

## Fan Basics

All fan platforms share common options.

### Common Options
| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Name in Home Assistant |
| `speed_count` | int | Number of speed levels |
| `on_speed_set` | trigger | When speed changes |
| `on_turn_on` | trigger | When turned on |
| `on_turn_off` | trigger | When turned off |

---

## Speed Fan

PWM-controlled variable speed fan.

### Basic Setup
```yaml
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO5
    frequency: 25000Hz  # 25kHz for 4-pin fans

fan:
  - platform: speed
    name: "Ceiling Fan"
    output: fan_pwm
    speed_count: 10
```

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output` | output | required | PWM output |
| `speed_count` | int | 100 | Number of speed steps |
| `oscillation_output` | output | - | For oscillation |
| `direction_output` | output | - | For direction |

### With Oscillation
```yaml
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO5
  - platform: gpio
    id: oscillate_output
    pin: GPIO4

fan:
  - platform: speed
    name: "Oscillating Fan"
    output: fan_pwm
    oscillation_output: oscillate_output
```

### With Direction Control
```yaml
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO5
  - platform: gpio
    id: direction_output
    pin: GPIO4

fan:
  - platform: speed
    name: "Reversible Fan"
    output: fan_pwm
    direction_output: direction_output
```

### 3-Speed Fan (Preset Levels)
```yaml
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO5

fan:
  - platform: speed
    name: "3-Speed Fan"
    output: fan_pwm
    speed_count: 3  # Low, Medium, High
```

---

## Binary Fan

Simple on/off fan.

```yaml
output:
  - platform: gpio
    id: fan_output
    pin: GPIO5

fan:
  - platform: binary
    name: "Exhaust Fan"
    output: fan_output
```

---

## Tuya Fan

For Tuya-based smart fans.

```yaml
uart:
  rx_pin: GPIO3
  tx_pin: GPIO1
  baud_rate: 9600

tuya:

fan:
  - platform: tuya
    name: "Tuya Fan"
    switch_datapoint: 1
    speed_datapoint: 3
    speed_count: 4
    direction_datapoint: 4
```

---

## Template Fan

Custom fan logic.

### Basic Template
```yaml
fan:
  - platform: template
    name: "Custom Fan"
    has_speed: true
    has_oscillating: true
    has_direction: true
    speed_count: 3

    turn_on_action:
      - switch.turn_on: fan_relay
    turn_off_action:
      - switch.turn_off: fan_relay

    set_speed_action:
      - output.set_level:
          id: fan_pwm
          level: !lambda |-
            if (speed == 1) return 0.33;
            if (speed == 2) return 0.66;
            return 1.0;

    set_oscillating_action:
      - if:
          condition:
            lambda: "return oscillating;"
          then:
            - switch.turn_on: oscillate_relay
          else:
            - switch.turn_off: oscillate_relay

    set_direction_action:
      - if:
          condition:
            lambda: "return direction == FAN_DIRECTION_FORWARD;"
          then:
            - switch.turn_on: direction_relay
          else:
            - switch.turn_off: direction_relay
```

### Preset Modes
```yaml
fan:
  - platform: template
    name: "Fan with Presets"
    has_speed: true
    preset_modes:
      - "Normal"
      - "Sleep"
      - "Turbo"

    set_preset_mode_action:
      - if:
          condition:
            lambda: "return preset_mode == \"Sleep\";"
          then:
            - output.set_level:
                id: fan_pwm
                level: 20%
      - if:
          condition:
            lambda: "return preset_mode == \"Turbo\";"
          then:
            - output.set_level:
                id: fan_pwm
                level: 100%
```

---

## Fan Actions

### Turn On/Off
```yaml
on_...:
  - fan.turn_on: my_fan
  - fan.turn_off: my_fan
  - fan.toggle: my_fan
```

### Set Speed
```yaml
on_...:
  - fan.turn_on:
      id: my_fan
      speed: 3  # 1 to speed_count
```

### Set All Properties
```yaml
on_...:
  - fan.turn_on:
      id: my_fan
      speed: 2
      oscillating: true
      direction: forward  # or reverse
```

### Cycle Speed
```yaml
on_...:
  - fan.cycle_speed: my_fan
```

---

## Common Patterns

### Ceiling Fan with Light
```yaml
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO5
  - platform: ledc
    id: light_pwm
    pin: GPIO4

fan:
  - platform: speed
    name: "Ceiling Fan"
    output: fan_pwm
    speed_count: 4

light:
  - platform: monochromatic
    name: "Ceiling Light"
    output: light_pwm
```

### Bathroom Exhaust with Humidity
```yaml
sensor:
  - platform: dht
    pin: GPIO4
    humidity:
      id: bathroom_humidity

fan:
  - platform: binary
    name: "Bathroom Fan"
    output: fan_output

  - platform: template
    name: "Auto Bathroom Fan"
    turn_on_action:
      - switch.turn_on: fan_auto_mode
    turn_off_action:
      - switch.turn_off: fan_auto_mode

switch:
  - platform: template
    id: fan_auto_mode
    optimistic: true

interval:
  - interval: 30s
    then:
      - if:
          condition:
            and:
              - switch.is_on: fan_auto_mode
              - sensor.in_range:
                  id: bathroom_humidity
                  above: 60
          then:
            - fan.turn_on: bathroom_fan
          else:
            - if:
                condition:
                  and:
                    - switch.is_on: fan_auto_mode
                    - sensor.in_range:
                        id: bathroom_humidity
                        below: 50
                then:
                  - fan.turn_off: bathroom_fan
```

### Garage Door with Safety
```yaml
binary_sensor:
  - platform: gpio
    id: obstruction_sensor
    pin: GPIO14

cover:
  - platform: template
    name: "Garage Door"
    device_class: garage
    lambda: |-
      if (id(door_closed).state) return COVER_CLOSED;
      if (id(door_open).state) return COVER_OPEN;
      return {};
    open_action:
      - switch.turn_on: door_motor
      - delay: 500ms
      - switch.turn_off: door_motor
    close_action:
      - if:
          condition:
            binary_sensor.is_off: obstruction_sensor
          then:
            - switch.turn_on: door_motor
            - delay: 500ms
            - switch.turn_off: door_motor
          else:
            - logger.log: "Obstruction detected!"
    stop_action:
      - switch.turn_on: door_motor
      - delay: 500ms
      - switch.turn_off: door_motor
```

### Multi-Zone Blind Control
```yaml
cover:
  - platform: time_based
    name: "Living Room Blind 1"
    id: blind_1
    # ...

  - platform: time_based
    name: "Living Room Blind 2"
    id: blind_2
    # ...

button:
  - platform: template
    name: "All Blinds Open"
    on_press:
      - cover.open: blind_1
      - cover.open: blind_2

  - platform: template
    name: "All Blinds Close"
    on_press:
      - cover.close: blind_1
      - cover.close: blind_2
```
