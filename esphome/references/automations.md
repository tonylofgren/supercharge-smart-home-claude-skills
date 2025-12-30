# ESPHome Automations Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Triggers](#triggers)
- [Conditions](#conditions)
- [Actions](#actions)
- [Lambda Expressions](#lambda-expressions)
- [Scripts](#scripts)
- [Globals](#globals)
- [Intervals](#intervals)
- [Time-based Automations](#time-based-automations)

---

## Core Concepts

ESPHome automations follow a trigger -> condition -> action pattern:

```yaml
sensor:
  - platform: dht
    temperature:
      name: "Temperature"
      on_value:                    # Trigger
        - if:                      # Condition
            condition:
              lambda: 'return x > 25;'
            then:                  # Action
              - switch.turn_on: fan
```

### Automation Structure

```yaml
on_<trigger>:
  - if:
      condition:
        <condition_type>: ...
      then:
        - <action>: ...
      else:
        - <action>: ...
```

---

## Triggers

### Sensor Triggers

```yaml
sensor:
  - platform: dht
    temperature:
      on_value:                    # Every value update
        then:
          - logger.log: "New value"

      on_value_range:              # When value in range
        above: 25.0
        below: 30.0
        then:
          - switch.turn_on: fan

      on_raw_value:                # Before filters applied
        then:
          - logger.log: "Raw value received"
```

### Binary Sensor Triggers

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_press:                      # State becomes ON
      then:
        - light.toggle: led

    on_release:                    # State becomes OFF
      then:
        - light.turn_off: led

    on_click:                      # Short press
      min_length: 50ms
      max_length: 350ms
      then:
        - switch.toggle: relay

    on_double_click:               # Double press
      min_length: 50ms
      max_length: 350ms
      then:
        - script.execute: double_action

    on_multi_click:                # Complex click patterns
      - timing:
          - ON for at most 1s
          - OFF for at most 1s
          - ON for at most 1s
          - OFF for at least 0.2s
        then:
          - logger.log: "Triple click"
      - timing:
          - ON for 1s to 3s
          - OFF for at least 0.5s
        then:
          - logger.log: "Long press"

    on_state:                      # Any state change
      then:
        - logger.log:
            format: "State: %d"
            args: ['x']
```

### Switch Triggers

```yaml
switch:
  - platform: gpio
    pin: GPIO12
    on_turn_on:
      then:
        - delay: 5s
        - switch.turn_off: this_switch

    on_turn_off:
      then:
        - logger.log: "Switch turned off"
```

### Boot Triggers

```yaml
esphome:
  on_boot:
    priority: 600                  # -100 to 800, higher = later
    then:
      - logger.log: "Device booted"
      - script.execute: startup_sequence

  on_shutdown:
    then:
      - logger.log: "Shutting down"

  on_loop:                         # Every loop iteration (use carefully!)
    then:
      - lambda: |-
          // Fast periodic code
```

### WiFi Triggers

```yaml
wifi:
  on_connect:
    then:
      - logger.log: "WiFi connected"
      - light.turn_on: status_led

  on_disconnect:
    then:
      - light.turn_off: status_led
```

### MQTT Triggers

```yaml
mqtt:
  on_connect:
    then:
      - mqtt.publish:
          topic: "devices/online"
          payload: "${device_name}"

  on_disconnect:
    then:
      - logger.log: "MQTT disconnected"

  on_message:
    topic: "commands/${device_name}"
    then:
      - logger.log:
          format: "Received: %s"
          args: ['x.c_str()']
```

### API Triggers

```yaml
api:
  on_client_connected:
    then:
      - logger.log:
          format: "Client connected: %s"
          args: ['client_info.c_str()']

  on_client_disconnected:
    then:
      - logger.log: "Client disconnected"
```

### Time Triggers

```yaml
time:
  - platform: homeassistant
    on_time:
      - seconds: 0
        minutes: 0
        hours: 7
        then:
          - switch.turn_on: morning_lights

      - cron: "0 */5 * * * *"     # Every 5 minutes
        then:
          - script.execute: periodic_check

    on_time_sync:
      then:
        - logger.log: "Time synchronized"
```

---

## Conditions

### Basic Conditions

```yaml
on_press:
  - if:
      condition:
        binary_sensor.is_on: motion_sensor
      then:
        - light.turn_on: hallway_light
```

### Lambda Condition

```yaml
condition:
  lambda: 'return id(temperature).state > 25;'
```

### Comparison Conditions

```yaml
condition:
  - sensor.in_range:
      id: temperature
      above: 20
      below: 30

  - binary_sensor.is_on: motion
  - binary_sensor.is_off: door

  - switch.is_on: relay
  - switch.is_off: relay

  - light.is_on: led
  - light.is_off: led

  - wifi.connected:
  - api.connected:
  - mqtt.connected:
```

### Boolean Logic

```yaml
condition:
  and:
    - binary_sensor.is_on: motion
    - sensor.in_range:
        id: light_level
        below: 100

condition:
  or:
    - binary_sensor.is_on: door
    - binary_sensor.is_on: window

condition:
  not:
    binary_sensor.is_on: away_mode
```

### Time Conditions

```yaml
condition:
  time.has_time:            # Time is synchronized

condition:
  - lambda: |-
      auto time = id(ha_time).now();
      return time.hour >= 8 && time.hour < 22;
```

### For Condition (State Duration)

```yaml
condition:
  for:
    time: 5min
    condition:
      binary_sensor.is_off: motion
```

---

## Actions

### Component Actions

```yaml
# Switch actions
- switch.turn_on: relay
- switch.turn_off: relay
- switch.toggle: relay

# Light actions
- light.turn_on:
    id: led
    brightness: 80%
    red: 100%
    green: 50%
    blue: 0%
    transition_length: 1s
- light.turn_off: led
- light.toggle: led

# Output actions
- output.turn_on: gpio_output
- output.turn_off: gpio_output
- output.set_level:
    id: pwm_output
    level: 50%

# Fan actions
- fan.turn_on:
    id: ceiling_fan
    speed: HIGH
- fan.turn_off: ceiling_fan

# Cover actions
- cover.open: garage_door
- cover.close: garage_door
- cover.stop: garage_door
- cover.control:
    id: blinds
    position: 50%
```

### Flow Control

```yaml
# Delay
- delay: 5s
- delay: !lambda return id(delay_time).state * 1000;

# Wait until
- wait_until:
    binary_sensor.is_off: motion
    timeout: 30s

- wait_until:
    condition:
      lambda: 'return id(counter) >= 10;'
    timeout: 1min

# While loop
- while:
    condition:
      binary_sensor.is_on: button
    then:
      - light.turn_on: led
      - delay: 100ms
      - light.turn_off: led
      - delay: 100ms

# Repeat
- repeat:
    count: 5
    then:
      - switch.toggle: relay
      - delay: 500ms
```

### Logging

```yaml
- logger.log: "Simple message"

- logger.log:
    format: "Temperature: %.1f C, Humidity: %.0f %%"
    args: ['id(temp).state', 'id(humidity).state']
    level: INFO    # DEBUG, VERBOSE, INFO, WARN, ERROR

- lambda: |-
    ESP_LOGI("main", "Custom log: %f", id(sensor).state);
```

### Component Updates

```yaml
- component.update: temperature_sensor
- component.suspend: power_sensor
- component.resume: power_sensor
```

### Scripts

```yaml
- script.execute: my_script
- script.execute:
    id: parameterized_script
    param1: 100
- script.stop: running_script
- script.wait: async_script
```

### Globals

```yaml
- globals.set:
    id: counter
    value: !lambda return id(counter) + 1;

- lambda: |-
    id(my_global) = 42;
```

### Home Assistant

```yaml
- homeassistant.event:
    event: esphome.button_pressed
    data:
      button: "main"
      count: !lambda return id(press_count);

- homeassistant.service:
    service: light.turn_on
    data:
      entity_id: light.living_room
      brightness_pct: "75"

- homeassistant.tag_scanned:
    tag: "my-tag-id"
```

### MQTT

```yaml
- mqtt.publish:
    topic: "home/sensor/temperature"
    payload: !lambda return to_string(id(temp).state);
    qos: 1
    retain: true

- mqtt.publish_json:
    topic: "home/sensor/data"
    payload: |-
      root["temperature"] = id(temp).state;
      root["humidity"] = id(hum).state;
```

---

## Lambda Expressions

### Basic Syntax

```yaml
lambda: |-
  // C++ code here
  return id(sensor).state * 2;
```

### Accessing Components

```yaml
lambda: |-
  // Sensors
  float temp = id(temperature_sensor).state;

  // Binary sensors
  bool motion = id(motion_sensor).state;

  // Switches
  bool is_on = id(relay).state;
  id(relay).turn_on();
  id(relay).turn_off();
  id(relay).toggle();

  // Lights
  auto call = id(led).turn_on();
  call.set_brightness(0.5);
  call.set_rgb(1.0, 0.5, 0.0);
  call.perform();

  // Globals
  int count = id(counter);
  id(counter) = count + 1;

  // Text sensors
  std::string version = id(version_sensor).state;
```

### Common Patterns

```yaml
# Conditional return
lambda: |-
  if (id(motion).state) {
    return 100.0;
  } else {
    return 0.0;
  }

# Time-based logic
lambda: |-
  auto time = id(ha_time).now();
  if (!time.is_valid())
    return {};
  return (time.hour * 60) + time.minute;

# String formatting
lambda: |-
  char buf[32];
  snprintf(buf, sizeof(buf), "%.1f C", id(temp).state);
  return std::string(buf);

# Multiple sensor aggregation
lambda: |-
  float sum = 0;
  sum += id(temp1).state;
  sum += id(temp2).state;
  sum += id(temp3).state;
  return sum / 3.0;
```

### Logging in Lambda

```yaml
lambda: |-
  ESP_LOGD("custom", "Debug message");
  ESP_LOGI("custom", "Info: %.2f", value);
  ESP_LOGW("custom", "Warning!");
  ESP_LOGE("custom", "Error!");
```

---

## Scripts

### Basic Script

```yaml
script:
  - id: my_script
    then:
      - light.turn_on: led
      - delay: 5s
      - light.turn_off: led
```

### Script Modes

```yaml
script:
  - id: single_script
    mode: single           # Cancel if already running (default)
    then: [...]

  - id: restart_script
    mode: restart          # Restart from beginning
    then: [...]

  - id: queued_script
    mode: queued           # Queue and run sequentially
    max_runs: 5
    then: [...]

  - id: parallel_script
    mode: parallel         # Run multiple instances
    max_runs: 10
    then: [...]
```

### Parameterized Scripts

```yaml
script:
  - id: blink_led
    parameters:
      times: int
      delay_ms: int
    then:
      - repeat:
          count: !lambda return times;
          then:
            - light.toggle: led
            - delay: !lambda return delay_ms;

# Usage
- script.execute:
    id: blink_led
    times: 5
    delay_ms: 200
```

### Script Control

```yaml
# Execute
- script.execute: my_script

# Stop
- script.stop: my_script

# Wait for completion
- script.wait: async_script

# Check if running
lambda: |-
  if (id(my_script).is_running()) {
    // ...
  }
```

---

## Globals

### Definition

```yaml
globals:
  - id: boot_count
    type: int
    restore_value: yes
    initial_value: '0'

  - id: last_motion_time
    type: unsigned long
    restore_value: no
    initial_value: '0'

  - id: device_mode
    type: std::string
    restore_value: no
    initial_value: '"normal"'

  - id: temperature_offset
    type: float
    restore_value: yes
    initial_value: '0.0'
```

### Types

| Type | Example Values |
|------|----------------|
| bool | true, false |
| int | 0, -10, 42 |
| float | 0.0, 3.14, -1.5 |
| unsigned long | 0, millis() |
| std::string | "hello" |

### Usage

```yaml
# Set in action
- globals.set:
    id: counter
    value: !lambda return id(counter) + 1;

# Use in lambda
lambda: |-
  id(boot_count) += 1;
  float offset = id(temperature_offset);
  return temp + offset;

# Restore on boot
globals:
  - id: setting
    type: int
    restore_value: yes    # Persists across reboots
```

---

## Intervals

### Basic Interval

```yaml
interval:
  - interval: 1s
    then:
      - logger.log: "Every second"

  - interval: 5min
    then:
      - component.update: slow_sensor
```

### Startup Delay

```yaml
interval:
  - interval: 1min
    startup_delay: 10s    # Wait before first run
    then:
      - script.execute: periodic_task
```

---

## Time-based Automations

### On Time

```yaml
time:
  - platform: homeassistant
    id: ha_time
    on_time:
      # Specific time
      - seconds: 0
        minutes: 30
        hours: 7
        days_of_week: MON-FRI
        then:
          - switch.turn_on: alarm

      # Cron syntax
      - cron: "0 0 */2 * * *"   # Every 2 hours
        then:
          - script.execute: check_status

      # Sunrise/Sunset (requires sun component)
      - at: sunset
        then:
          - light.turn_on: porch_light

      - at: sunrise + 30min
        then:
          - light.turn_off: porch_light
```

### Cron Syntax

```
# Format: SEC MIN HOUR DAY MONTH DAY_OF_WEEK
#         0   0   *    *   *     *

# Examples:
"0 0 * * * *"      # Every hour
"0 */15 * * * *"   # Every 15 minutes
"0 0 8 * * MON-FRI"  # 8:00 AM weekdays
"0 30 22 * * *"    # 10:30 PM daily
```

### Sun Component

```yaml
sun:
  latitude: 59.3293    # Your latitude (or use !secret latitude)
  longitude: 18.0686   # Your longitude (or use !secret longitude)

sensor:
  - platform: sun
    type: elevation
    name: "Sun Elevation"
  - platform: sun
    type: azimuth
    name: "Sun Azimuth"

# Use in automations
time:
  - platform: homeassistant
    on_time:
      - at: sunset
        then:
          - light.turn_on: outdoor_lights
```

---

## Best Practices

1. **Use scripts** for reusable action sequences
2. **Use globals** sparingly - prefer component state
3. **Add timeouts** to wait_until to prevent hangs
4. **Log important events** for debugging
5. **Use meaningful IDs** for components
6. **Test automations** thoroughly before deployment
7. **Avoid on_loop** unless absolutely necessary (performance)
8. **Use conditions** before expensive actions
