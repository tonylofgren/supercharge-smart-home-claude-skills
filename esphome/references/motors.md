# ESPHome Motors Reference

Complete reference for stepper motors and servo control.

## Table of Contents
- [Stepper Motors](#stepper-motors)
- [Servo Motors](#servo-motors)
- [DC Motors (H-Bridge)](#dc-motors-h-bridge)

---

## Stepper Motors

### Stepper Drivers

#### A4988/DRV8825 (Step/Dir Interface)
```yaml
stepper:
  - platform: a4988
    id: my_stepper
    step_pin: GPIO5
    dir_pin: GPIO4
    max_speed: 500 steps/s
    acceleration: 200 steps/s^2
    deceleration: 200 steps/s^2
```

#### ULN2003 (Unipolar, 28BYJ-48)
```yaml
stepper:
  - platform: uln2003
    id: my_stepper
    pin_a: GPIO5
    pin_b: GPIO4
    pin_c: GPIO14
    pin_d: GPIO12
    max_speed: 500 steps/s
    acceleration: 200 steps/s^2
    deceleration: 200 steps/s^2
    sleep_when_done: true
```

### Stepper Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_speed` | speed | required | Maximum speed |
| `acceleration` | accel | inf | Acceleration rate |
| `deceleration` | accel | inf | Deceleration rate |
| `sleep_when_done` | bool | false | Disable coils at rest (ULN2003) |

### A4988 with Enable Pin
```yaml
stepper:
  - platform: a4988
    id: my_stepper
    step_pin: GPIO5
    dir_pin: GPIO4
    sleep_pin:
      number: GPIO15
      inverted: true  # Low = enabled for A4988

output:
  - platform: gpio
    id: stepper_enable
    pin:
      number: GPIO15
      inverted: true
```

### Microstepping (A4988/DRV8825)
```yaml
# Set MS1, MS2, MS3 pins for microstepping
# A4988: 1/16 step = MS1=HIGH, MS2=HIGH, MS3=HIGH
# DRV8825: 1/32 step = M0=HIGH, M1=HIGH, M2=HIGH

output:
  - platform: gpio
    id: ms1
    pin: GPIO12
  - platform: gpio
    id: ms2
    pin: GPIO13
  - platform: gpio
    id: ms3
    pin: GPIO14

esphome:
  on_boot:
    - output.turn_on: ms1
    - output.turn_on: ms2
    - output.turn_on: ms3  # 1/16 microstepping
```

### Stepper Actions

#### Set Target Position
```yaml
on_...:
  # Absolute position
  - stepper.set_target:
      id: my_stepper
      target: 1000

  # With lambda
  - stepper.set_target:
      id: my_stepper
      target: !lambda "return 500;"
```

#### Report Position
```yaml
on_...:
  # Reset current position to 0
  - stepper.report_position:
      id: my_stepper
      position: 0
```

#### Set Speed
```yaml
on_...:
  - stepper.set_speed:
      id: my_stepper
      speed: 1000 steps/s
```

#### Set Acceleration
```yaml
on_...:
  - stepper.set_acceleration:
      id: my_stepper
      acceleration: 500 steps/s^2

  - stepper.set_deceleration:
      id: my_stepper
      deceleration: 500 steps/s^2
```

### Stepper Position Sensor
```yaml
sensor:
  - platform: template
    name: "Stepper Position"
    lambda: |-
      return id(my_stepper).current_position;
    update_interval: 500ms
```

### Homing with Endstop
```yaml
binary_sensor:
  - platform: gpio
    id: home_switch
    pin:
      number: GPIO14
      mode: INPUT_PULLUP
      inverted: true

button:
  - platform: template
    name: "Home Stepper"
    on_press:
      # Move towards home switch
      - stepper.set_target:
          id: my_stepper
          target: -10000  # Move negative direction
      # Wait for home switch
      - wait_until:
          binary_sensor.is_on: home_switch
      # Stop immediately
      - stepper.set_target:
          id: my_stepper
          target: !lambda "return id(my_stepper).current_position;"
      # Reset position to 0
      - stepper.report_position:
          id: my_stepper
          position: 0
      # Move slightly off switch
      - stepper.set_target:
          id: my_stepper
          target: 50
```

### Number Control (HA Integration)
```yaml
number:
  - platform: template
    name: "Stepper Position"
    min_value: 0
    max_value: 10000
    step: 100
    lambda: |-
      return id(my_stepper).current_position;
    set_action:
      - stepper.set_target:
          id: my_stepper
          target: !lambda "return x;"
```

---

## Servo Motors

### Basic Setup
```yaml
servo:
  - id: my_servo
    output: servo_pwm
    auto_detach_time: 2s  # Disable after movement
    transition_length: 1s  # Smooth movement

output:
  - platform: ledc
    id: servo_pwm
    pin: GPIO5
    frequency: 50Hz
```

### Servo Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output` | output | required | PWM output |
| `min_level` | float | 3% | PWM for -100% position |
| `idle_level` | float | 7.5% | PWM for 0% position |
| `max_level` | float | 12% | PWM for +100% position |
| `auto_detach_time` | time | 0s | Disable output after move |
| `transition_length` | time | 0s | Movement duration |

### Custom Pulse Range
```yaml
# For servos with non-standard pulse widths
servo:
  - id: my_servo
    output: servo_pwm
    min_level: 2.5%   # ~0.5ms pulse
    idle_level: 7.5%  # ~1.5ms pulse
    max_level: 12.5%  # ~2.5ms pulse
```

### Servo Actions

#### Write Position
```yaml
on_...:
  # Position from -100% to +100% (or -1.0 to 1.0)
  - servo.write:
      id: my_servo
      level: 50%  # Half way to max

  # Full range examples
  - servo.write:
      id: my_servo
      level: -100%  # Minimum position

  - servo.write:
      id: my_servo
      level: 0%     # Center position

  - servo.write:
      id: my_servo
      level: 100%   # Maximum position
```

#### Detach (Disable)
```yaml
on_...:
  - servo.detach: my_servo
```

### Number Control (HA Integration)
```yaml
number:
  - platform: template
    name: "Servo Position"
    min_value: -100
    max_value: 100
    step: 5
    unit_of_measurement: "%"
    set_action:
      - servo.write:
          id: my_servo
          level: !lambda "return x / 100.0;"
```

### Continuous Rotation Servo
```yaml
# Continuous servos use position as speed
# 0% = stop, -100% = full reverse, +100% = full forward

servo:
  - id: wheel_servo
    output: servo_pwm

number:
  - platform: template
    name: "Wheel Speed"
    min_value: -100
    max_value: 100
    step: 10
    initial_value: 0
    set_action:
      - servo.write:
          id: wheel_servo
          level: !lambda "return x / 100.0;"
```

### Multiple Servos (PCA9685)
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

pca9685:
  frequency: 50Hz
  address: 0x40

output:
  - platform: pca9685
    id: servo_0
    channel: 0
  - platform: pca9685
    id: servo_1
    channel: 1
  - platform: pca9685
    id: servo_2
    channel: 2

servo:
  - id: pan_servo
    output: servo_0
  - id: tilt_servo
    output: servo_1
  - id: grip_servo
    output: servo_2
```

---

## DC Motors (H-Bridge)

### L298N / TB6612 Control
```yaml
# Direction + Speed control
output:
  - platform: ledc
    id: motor_speed
    pin: GPIO5
    frequency: 1000Hz

switch:
  - platform: gpio
    id: motor_dir_1
    pin: GPIO12
  - platform: gpio
    id: motor_dir_2
    pin: GPIO14

fan:
  - platform: template
    name: "DC Motor"
    has_speed: true
    has_direction: true
    speed_count: 100

    turn_on_action:
      - if:
          condition:
            lambda: "return direction == FAN_DIRECTION_FORWARD;"
          then:
            - switch.turn_on: motor_dir_1
            - switch.turn_off: motor_dir_2
          else:
            - switch.turn_off: motor_dir_1
            - switch.turn_on: motor_dir_2

    turn_off_action:
      - switch.turn_off: motor_dir_1
      - switch.turn_off: motor_dir_2

    set_speed_action:
      - output.set_level:
          id: motor_speed
          level: !lambda "return speed / 100.0;"

    set_direction_action:
      - if:
          condition:
            lambda: "return direction == FAN_DIRECTION_FORWARD;"
          then:
            - switch.turn_on: motor_dir_1
            - switch.turn_off: motor_dir_2
          else:
            - switch.turn_off: motor_dir_1
            - switch.turn_on: motor_dir_2
```

### Simple H-Bridge (Two PWM)
```yaml
output:
  - platform: ledc
    id: motor_forward
    pin: GPIO5
  - platform: ledc
    id: motor_reverse
    pin: GPIO4

number:
  - platform: template
    name: "Motor Speed"
    min_value: -100
    max_value: 100
    step: 10
    initial_value: 0
    set_action:
      - if:
          condition:
            lambda: "return x >= 0;"
          then:
            - output.set_level:
                id: motor_forward
                level: !lambda "return x / 100.0;"
            - output.set_level:
                id: motor_reverse
                level: 0
          else:
            - output.set_level:
                id: motor_forward
                level: 0
            - output.set_level:
                id: motor_reverse
                level: !lambda "return -x / 100.0;"
```

---

## Common Patterns

### Pan-Tilt Camera Mount
```yaml
servo:
  - id: pan_servo
    output: pan_pwm
    transition_length: 0.5s
  - id: tilt_servo
    output: tilt_pwm
    transition_length: 0.5s

number:
  - platform: template
    name: "Camera Pan"
    min_value: -90
    max_value: 90
    step: 5
    unit_of_measurement: "°"
    set_action:
      - servo.write:
          id: pan_servo
          level: !lambda "return x / 90.0;"

  - platform: template
    name: "Camera Tilt"
    min_value: -45
    max_value: 45
    step: 5
    unit_of_measurement: "°"
    set_action:
      - servo.write:
          id: tilt_servo
          level: !lambda "return x / 45.0;"
```

### Stepper-Driven Linear Actuator
```yaml
stepper:
  - platform: a4988
    id: actuator
    step_pin: GPIO5
    dir_pin: GPIO4
    max_speed: 1000 steps/s
    acceleration: 500 steps/s^2

# 2000 steps = 10mm travel (example)
number:
  - platform: template
    name: "Actuator Position"
    min_value: 0
    max_value: 100
    step: 1
    unit_of_measurement: "mm"
    set_action:
      - stepper.set_target:
          id: actuator
          target: !lambda "return x * 200;"  # 200 steps/mm
```

### Stepper Curtain Controller
```yaml
stepper:
  - platform: a4988
    id: curtain_motor
    step_pin: GPIO5
    dir_pin: GPIO4
    max_speed: 500 steps/s
    acceleration: 200 steps/s^2

binary_sensor:
  - platform: gpio
    id: limit_open
    pin: GPIO12
  - platform: gpio
    id: limit_closed
    pin: GPIO14

cover:
  - platform: template
    name: "Curtain"
    device_class: curtain
    has_position: true

    open_action:
      - stepper.set_target:
          id: curtain_motor
          target: 10000
      - wait_until:
          binary_sensor.is_on: limit_open
      - stepper.set_target:
          id: curtain_motor
          target: !lambda "return id(curtain_motor).current_position;"

    close_action:
      - stepper.set_target:
          id: curtain_motor
          target: 0
      - wait_until:
          binary_sensor.is_on: limit_closed
      - stepper.set_target:
          id: curtain_motor
          target: !lambda "return id(curtain_motor).current_position;"

    stop_action:
      - stepper.set_target:
          id: curtain_motor
          target: !lambda "return id(curtain_motor).current_position;"

    position_action:
      - stepper.set_target:
          id: curtain_motor
          target: !lambda "return pos * 10000;"
```

### Door Lock Servo
```yaml
servo:
  - id: lock_servo
    output: servo_pwm
    auto_detach_time: 1s

lock:
  - platform: template
    name: "Door Lock"
    lambda: |-
      return id(lock_state);
    lock_action:
      - servo.write:
          id: lock_servo
          level: 100%
      - globals.set:
          id: lock_state
          value: "true"
    unlock_action:
      - servo.write:
          id: lock_servo
          level: -100%
      - globals.set:
          id: lock_state
          value: "false"

globals:
  - id: lock_state
    type: bool
    initial_value: "false"
```

### Robot Arm (Multiple Steppers)
```yaml
stepper:
  - platform: a4988
    id: base_motor
    step_pin: GPIO5
    dir_pin: GPIO4
    max_speed: 500 steps/s
  - platform: a4988
    id: shoulder_motor
    step_pin: GPIO14
    dir_pin: GPIO12
    max_speed: 500 steps/s
  - platform: a4988
    id: elbow_motor
    step_pin: GPIO27
    dir_pin: GPIO26
    max_speed: 500 steps/s

number:
  - platform: template
    name: "Base Rotation"
    min_value: 0
    max_value: 360
    step: 5
    unit_of_measurement: "°"
    set_action:
      - stepper.set_target:
          id: base_motor
          target: !lambda "return x * 10;"  # 10 steps/degree
```
