# ESPHome Climate Reference

Complete reference for climate/HVAC platforms including thermostats, PID controllers, and IR air conditioners.

## Table of Contents
- [Climate Basics](#climate-basics)
- [Thermostat Controller](#thermostat-controller)
- [PID Controller](#pid-controller)
- [Bang Bang Controller](#bang-bang-controller)
- [IR Remote Climate](#ir-remote-climate)
- [Direct AC Protocols](#direct-ac-protocols)
- [Climate Actions](#climate-actions)

---

## Climate Basics

All climate platforms share common configuration options.

### Common Options
| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Name in Home Assistant |
| `visual` | visual | Temperature display settings |
| `on_state` | action | Triggered on state change |

### Visual Configuration
```yaml
climate:
  - platform: ...
    visual:
      min_temperature: 16°C
      max_temperature: 30°C
      temperature_step: 0.5°C
```

---

## Thermostat Controller

Software thermostat with heat/cool/auto modes.

### Basic Heating Thermostat
```yaml
climate:
  - platform: thermostat
    name: "Thermostat"
    sensor: temp_sensor
    default_preset: Home

    min_heating_off_time: 300s
    min_heating_run_time: 300s
    min_idle_time: 30s

    heat_action:
      - switch.turn_on: heater_relay
    idle_action:
      - switch.turn_off: heater_relay

    preset:
      - name: Home
        default_target_temperature_low: 21°C
      - name: Away
        default_target_temperature_low: 16°C
      - name: Sleep
        default_target_temperature_low: 18°C
```

### Heating + Cooling Thermostat
```yaml
climate:
  - platform: thermostat
    name: "HVAC"
    sensor: temp_sensor

    min_heating_off_time: 300s
    min_heating_run_time: 300s
    min_cooling_off_time: 300s
    min_cooling_run_time: 300s
    min_idle_time: 30s

    heat_action:
      - switch.turn_on: heat_relay
    cool_action:
      - switch.turn_on: cool_relay
    idle_action:
      - switch.turn_off: heat_relay
      - switch.turn_off: cool_relay

    heat_deadband: 0.5°C
    heat_overrun: 0.5°C
    cool_deadband: 0.5°C
    cool_overrun: 0.5°C
```

### Thermostat Options
| Option | Type | Description |
|--------|------|-------------|
| `sensor` | sensor | Temperature sensor (required) |
| `heat_action` | action | Action when heating needed |
| `cool_action` | action | Action when cooling needed |
| `idle_action` | action | Action when idle |
| `dry_action` | action | Action for dehumidify mode |
| `fan_only_action` | action | Action for fan only mode |
| `min_heating_off_time` | time | Min time heater stays off |
| `min_heating_run_time` | time | Min time heater runs |
| `min_cooling_off_time` | time | Min time cooler stays off |
| `min_cooling_run_time` | time | Min time cooler runs |
| `min_idle_time` | time | Min time in idle |
| `heat_deadband` | temp | Start heating below setpoint-deadband |
| `heat_overrun` | temp | Stop heating at setpoint+overrun |
| `cool_deadband` | temp | Start cooling above setpoint+deadband |
| `cool_overrun` | temp | Stop cooling at setpoint-overrun |

### Two-Point Thermostat (Heat + Cool Range)
```yaml
climate:
  - platform: thermostat
    name: "Dual Setpoint"
    sensor: temp_sensor

    set_point_minimum_differential: 2°C

    heat_action:
      - switch.turn_on: heat_relay
    cool_action:
      - switch.turn_on: cool_relay
    idle_action:
      - switch.turn_off: heat_relay
      - switch.turn_off: cool_relay

    default_preset: Home
    preset:
      - name: Home
        default_target_temperature_low: 20°C
        default_target_temperature_high: 24°C
```

### Supplemental Heating
```yaml
climate:
  - platform: thermostat
    name: "Heat Pump"
    sensor: temp_sensor

    # Primary heat
    heat_action:
      - switch.turn_on: heat_pump_relay

    # Supplemental heat (kicks in when primary can't keep up)
    supplemental_heating_action:
      - switch.turn_on: aux_heat_relay
    supplemental_heating_delta: 2°C

    idle_action:
      - switch.turn_off: heat_pump_relay
      - switch.turn_off: aux_heat_relay
```

### Thermostat with Fan Modes
```yaml
climate:
  - platform: thermostat
    name: "HVAC with Fan"
    sensor: temp_sensor

    fan_mode_on_action:
      - switch.turn_on: fan_relay
    fan_mode_off_action:
      - switch.turn_off: fan_relay
    fan_mode_auto_action:
      # Fan runs only with heating/cooling
      - switch.turn_off: fan_relay

    # Fan also runs during heat/cool
    heat_action:
      - switch.turn_on: heat_relay
      - switch.turn_on: fan_relay
```

---

## PID Controller

Proportional-Integral-Derivative controller for precise temperature control.

### Basic PID Heating
```yaml
output:
  - platform: slow_pwm
    id: heater_output
    pin: GPIO5
    period: 30s

climate:
  - platform: pid
    name: "PID Heater"
    sensor: temp_sensor
    default_target_temperature: 21°C
    heat_output: heater_output

    control_parameters:
      kp: 0.5
      ki: 0.02
      kd: 0.1
```

### PID Cooling
```yaml
output:
  - platform: ledc
    id: fan_output
    pin: GPIO5
    frequency: 25000Hz

climate:
  - platform: pid
    name: "PID Cooler"
    sensor: temp_sensor
    default_target_temperature: 25°C
    cool_output: fan_output

    control_parameters:
      kp: 0.3
      ki: 0.01
      kd: 0.05
```

### PID Heat + Cool
```yaml
climate:
  - platform: pid
    name: "PID HVAC"
    sensor: temp_sensor
    default_target_temperature: 22°C
    heat_output: heat_pwm
    cool_output: cool_pwm

    control_parameters:
      kp: 0.4
      ki: 0.015
      kd: 0.08
```

### PID Tuning
```yaml
climate:
  - platform: pid
    id: pid_climate
    # ...

button:
  - platform: template
    name: "Start PID Autotune"
    on_press:
      - climate.pid.autotune: pid_climate
```

### PID Control Parameters
| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `kp` | Proportional gain | 0.1 - 2.0 |
| `ki` | Integral gain | 0.001 - 0.1 |
| `kd` | Derivative gain | 0.01 - 0.5 |
| `output_averaging_samples` | Smooth output | 1 - 10 |
| `derivative_averaging_samples` | Smooth derivative | 1 - 10 |

### PID with Deadband
```yaml
climate:
  - platform: pid
    name: "PID with Deadband"
    sensor: temp_sensor
    default_target_temperature: 21°C
    heat_output: heater_output

    control_parameters:
      kp: 0.5
      ki: 0.02
      kd: 0.1

    deadband_parameters:
      threshold_high: 0.5°C
      threshold_low: -0.5°C
```

---

## Bang Bang Controller

Simple on/off controller.

### Basic Bang Bang
```yaml
climate:
  - platform: bang_bang
    name: "Simple Thermostat"
    sensor: temp_sensor
    default_target_temperature: 21°C

    heat_action:
      - switch.turn_on: heater
    idle_action:
      - switch.turn_off: heater

    # Turn on below 20.5°C, off above 21.5°C
    default_target_temperature: 21°C
```

---

## IR Remote Climate

Control AC units via infrared.

### Generic Coolix (Many brands)
```yaml
remote_transmitter:
  pin: GPIO5
  carrier_duty_percent: 50%

climate:
  - platform: coolix
    name: "AC"
    receiver_id: ir_receiver  # Optional for feedback
    supports_heat: true
    supports_cool: true
```

### Fujitsu
```yaml
climate:
  - platform: fujitsu_general
    name: "Fujitsu AC"
```

### Daikin
```yaml
climate:
  - platform: daikin
    name: "Daikin AC"
```

### Daikin BRC
```yaml
climate:
  - platform: daikin_brc
    name: "Daikin BRC AC"
```

### Mitsubishi
```yaml
climate:
  - platform: mitsubishi
    name: "Mitsubishi AC"
```

### LG
```yaml
climate:
  - platform: climate_ir_lg
    name: "LG AC"
```

### Samsung
```yaml
climate:
  - platform: samsung_ac
    name: "Samsung AC"
```

### Toshiba
```yaml
climate:
  - platform: toshiba
    name: "Toshiba AC"
```

### Whirlpool
```yaml
climate:
  - platform: whirlpool
    name: "Whirlpool AC"
    model: DG11J1-3A
```

### Gree/Eberg
```yaml
climate:
  - platform: gree
    name: "Gree AC"
    model: YAW1F
```

### TCL/Tekno
```yaml
climate:
  - platform: tcl112
    name: "TCL AC"
```

### Haier
```yaml
climate:
  - platform: haier
    name: "Haier AC"
```

### IR Climate Options
| Option | Type | Description |
|--------|------|-------------|
| `supports_cool` | bool | Support cooling mode |
| `supports_heat` | bool | Support heating mode |
| `sensor` | sensor | Room temperature sensor |
| `receiver_id` | id | IR receiver for feedback |

### IR Climate with Receiver
```yaml
remote_receiver:
  id: ir_receiver
  pin:
    number: GPIO14
    inverted: true
    mode: INPUT_PULLUP
  dump: all

remote_transmitter:
  pin: GPIO5
  carrier_duty_percent: 50%

climate:
  - platform: coolix
    name: "AC"
    receiver_id: ir_receiver
    sensor: room_temp
```

---

## Direct AC Protocols

### Midea (UART)
```yaml
uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 9600

climate:
  - platform: midea
    name: "Midea AC"
    period: 1s
    timeout: 2s
    num_attempts: 3

    visual:
      min_temperature: 16°C
      max_temperature: 30°C
      temperature_step: 1°C

    beeper: true
    outdoor_temperature:
      name: "Outdoor Temperature"
    power_usage:
      name: "Power Usage"
    humidity_setpoint:
      name: "Humidity Setpoint"
```

### Haier (UART)
```yaml
uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 9600

climate:
  - platform: haier
    name: "Haier AC"
    protocol: hOn
    wifi_signal: true
    beeper: true
    outdoor_temperature:
      name: "Outdoor Temperature"
```

### Zhongxin / ZH/LT-01
```yaml
uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 9600

climate:
  - platform: climate_ir
    name: "Generic IR AC"
    protocol: zhlt01
```

---

## Climate Actions

### Set Mode
```yaml
on_...:
  - climate.control:
      id: my_climate
      mode: HEAT  # OFF, HEAT, COOL, HEAT_COOL, AUTO, DRY, FAN_ONLY

  # Or with lambda
  - climate.control:
      id: my_climate
      mode: !lambda |-
        return CLIMATE_MODE_HEAT;
```

### Set Target Temperature
```yaml
on_...:
  - climate.control:
      id: my_climate
      target_temperature: 22°C

  # For dual setpoint
  - climate.control:
      id: my_climate
      target_temperature_low: 20°C
      target_temperature_high: 24°C
```

### Set Fan Mode
```yaml
on_...:
  - climate.control:
      id: my_climate
      fan_mode: AUTO  # ON, OFF, AUTO, LOW, MEDIUM, HIGH, MIDDLE, FOCUS, DIFFUSE
```

### Set Swing Mode
```yaml
on_...:
  - climate.control:
      id: my_climate
      swing_mode: VERTICAL  # OFF, BOTH, VERTICAL, HORIZONTAL
```

### Set Preset
```yaml
on_...:
  - climate.control:
      id: my_climate
      preset: HOME  # HOME, AWAY, BOOST, COMFORT, ECO, SLEEP, ACTIVITY
```

### Custom Preset
```yaml
on_...:
  - climate.control:
      id: my_climate
      custom_preset: "Night Mode"
```

---

## Common Patterns

### Floor Heating with Safety Limit
```yaml
sensor:
  - platform: dallas
    address: 0x1234567890ABCDEF
    id: floor_temp
  - platform: dallas
    address: 0xFEDCBA0987654321
    id: room_temp

climate:
  - platform: thermostat
    name: "Floor Heating"
    sensor: room_temp

    heat_action:
      - if:
          condition:
            sensor.in_range:
              id: floor_temp
              below: 35  # Safety limit
          then:
            - switch.turn_on: heat_relay
          else:
            - switch.turn_off: heat_relay
    idle_action:
      - switch.turn_off: heat_relay
```

### Schedule via Home Assistant
```yaml
climate:
  - platform: thermostat
    name: "Smart Thermostat"
    sensor: temp_sensor

    preset:
      - name: Home
        default_target_temperature_low: 21°C
      - name: Away
        default_target_temperature_low: 16°C
      - name: Sleep
        default_target_temperature_low: 18°C
      - name: Boost
        default_target_temperature_low: 24°C
```

### Multi-Zone Heating
```yaml
climate:
  - platform: thermostat
    name: "Zone 1 - Living Room"
    sensor: temp_zone1
    heat_action:
      - switch.turn_on: valve_zone1
    idle_action:
      - switch.turn_off: valve_zone1

  - platform: thermostat
    name: "Zone 2 - Bedroom"
    sensor: temp_zone2
    heat_action:
      - switch.turn_on: valve_zone2
    idle_action:
      - switch.turn_off: valve_zone2
```

### Humidity Control
```yaml
sensor:
  - platform: dht
    pin: GPIO4
    humidity:
      id: room_humidity

climate:
  - platform: thermostat
    name: "Dehumidifier"
    sensor: room_humidity

    cool_action:  # Using cool for dehumidify
      - switch.turn_on: dehumidifier_relay
    idle_action:
      - switch.turn_off: dehumidifier_relay

    default_preset: Normal
    preset:
      - name: Normal
        default_target_temperature_low: 50  # Target 50% humidity
```

### External Thermostat Override
```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO14
    id: external_thermostat
    name: "External Thermostat Call"
    on_press:
      - switch.turn_on: boiler_relay
    on_release:
      - switch.turn_off: boiler_relay
```
