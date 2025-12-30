# ESPHome Buttons and Inputs Reference

Guide to Button, Number, Select, and Text components for Home Assistant interaction.

## Table of Contents

- [Button Component](#button-component)
- [Number Component](#number-component)
- [Select Component](#select-component)
- [Text Component](#text-component)
- [Text Sensor Component](#text-sensor-component)
- [Tuya Integration](#tuya-integration)

---

## Button Component

Buttons appear in Home Assistant as pressable entities. They trigger actions when pressed.

### Restart Button

```yaml
button:
  - platform: restart
    name: "Restart Device"
    entity_category: config
```

### Safe Mode Button

```yaml
button:
  - platform: safe_mode
    name: "Restart (Safe Mode)"
    entity_category: config
```

### Shutdown Button (ESP32)

```yaml
button:
  - platform: shutdown
    name: "Shutdown"
    entity_category: config
```

### Factory Reset Button

```yaml
button:
  - platform: factory_reset
    name: "Factory Reset"
    entity_category: config
```

### Template Button

```yaml
button:
  - platform: template
    name: "Run Script"
    on_press:
      - script.execute: my_script

  - platform: template
    name: "Toggle Relay"
    on_press:
      - switch.toggle: relay

  - platform: template
    name: "Play Sound"
    on_press:
      - rtttl.play: "beep:d=4,o=5,b=100:c"
```

### Wake on LAN Button

```yaml
button:
  - platform: wake_on_lan
    name: "Wake PC"
    target_mac_address: AA:BB:CC:DD:EE:FF
```

### Output Button

```yaml
output:
  - platform: gpio
    pin: GPIO12
    id: relay_output

button:
  - platform: output
    name: "Pulse Relay"
    output: relay_output
    duration: 500ms
```

---

## Number Component

Numbers appear as sliders or input boxes in Home Assistant.

### Template Number

```yaml
number:
  - platform: template
    name: "Target Temperature"
    id: target_temp
    min_value: 15
    max_value: 30
    step: 0.5
    unit_of_measurement: "°C"
    optimistic: true
    restore_value: true
    initial_value: 21
    on_value:
      - logger.log:
          format: "Target temperature set to %.1f"
          args: ['x']
```

### Number with Lambda

```yaml
number:
  - platform: template
    name: "LED Brightness"
    id: led_brightness
    min_value: 0
    max_value: 100
    step: 1
    unit_of_measurement: "%"
    lambda: |-
      return id(led_pwm).get_level() * 100;
    set_action:
      - output.set_level:
          id: led_pwm
          level: !lambda "return x / 100.0;"
```

### Calibration Number

```yaml
number:
  - platform: template
    name: "Temperature Offset"
    id: temp_offset
    min_value: -5
    max_value: 5
    step: 0.1
    unit_of_measurement: "°C"
    optimistic: true
    restore_value: true
    initial_value: 0
    entity_category: config

sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Temperature"
      filters:
        - lambda: return x + id(temp_offset).state;
```

### Slider for Fan Speed

```yaml
number:
  - platform: template
    name: "Fan Speed"
    id: fan_speed
    min_value: 0
    max_value: 100
    step: 10
    unit_of_measurement: "%"
    optimistic: true
    on_value:
      - output.set_level:
          id: fan_output
          level: !lambda "return x / 100.0;"
```

### Mode Selection

```yaml
number:
  - platform: template
    name: "Mode"
    id: mode
    min_value: 1
    max_value: 3
    step: 1
    mode: box
    optimistic: true
```

---

## Select Component

Selects appear as dropdown menus in Home Assistant.

### Template Select

```yaml
select:
  - platform: template
    name: "Operating Mode"
    id: mode_select
    options:
      - "Off"
      - "Auto"
      - "Manual"
      - "Schedule"
    initial_option: "Auto"
    optimistic: true
    on_value:
      - logger.log:
          format: "Mode changed to %s"
          args: ['x.c_str()']
```

### Mode with Actions

```yaml
select:
  - platform: template
    name: "Fan Mode"
    id: fan_mode
    options:
      - "Off"
      - "Low"
      - "Medium"
      - "High"
      - "Auto"
    optimistic: true
    set_action:
      - lambda: |-
          if (x == "Off") {
            id(fan_speed).publish_state(0);
          } else if (x == "Low") {
            id(fan_speed).publish_state(30);
          } else if (x == "Medium") {
            id(fan_speed).publish_state(60);
          } else if (x == "High") {
            id(fan_speed).publish_state(100);
          }
```

### Effect Selector

```yaml
select:
  - platform: template
    name: "LED Effect"
    id: led_effect
    options:
      - "None"
      - "Rainbow"
      - "Pulse"
      - "Strobe"
      - "Color Wipe"
    optimistic: true
    on_value:
      - if:
          condition:
            lambda: 'return x == "None";'
          then:
            - light.turn_on:
                id: led_strip
                effect: "None"
      - if:
          condition:
            lambda: 'return x == "Rainbow";'
          then:
            - light.turn_on:
                id: led_strip
                effect: "Rainbow"
      # ... etc
```

### Scene Selector

```yaml
select:
  - platform: template
    name: "Scene"
    id: scene_select
    options:
      - "Day"
      - "Night"
      - "Movie"
      - "Party"
    optimistic: true
    on_value:
      - script.execute:
          id: apply_scene
          scene: !lambda "return x;"

script:
  - id: apply_scene
    parameters:
      scene: string
    then:
      - lambda: |-
          if (scene == "Day") {
            auto call = id(led_strip).turn_on();
            call.set_brightness(1.0);
            call.set_rgb(1.0, 1.0, 1.0);
            call.perform();
          } else if (scene == "Night") {
            auto call = id(led_strip).turn_on();
            call.set_brightness(0.2);
            call.set_rgb(1.0, 0.5, 0.0);
            call.perform();
          }
          // ...
```

---

## Text Component

Text components allow string input from Home Assistant.

### Template Text

```yaml
text:
  - platform: template
    name: "Device Name"
    id: device_name
    mode: text
    optimistic: true
    restore_value: true
    initial_value: "My Device"
    on_value:
      - logger.log:
          format: "Device name: %s"
          args: ['x.c_str()']
```

### Text Modes

```yaml
text:
  # Regular text input
  - platform: template
    name: "Message"
    mode: text
    optimistic: true

  # Password input (masked)
  - platform: template
    name: "Password"
    mode: password
    optimistic: true
```

### Display Message

```yaml
text:
  - platform: template
    name: "Display Message"
    id: display_message
    mode: text
    optimistic: true
    on_value:
      - display.page.show: message_page
      - component.update: oled_display

display:
  - platform: ssd1306_i2c
    id: oled_display
    pages:
      - id: message_page
        lambda: |-
          it.print(0, 0, id(font), id(display_message).state.c_str());
```

---

## Text Sensor Component

Text sensors display string values (read-only) in Home Assistant.

### Template Text Sensor

```yaml
text_sensor:
  - platform: template
    name: "Status"
    id: status_text
    update_interval: never  # Manual updates only

binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_press:
      - text_sensor.template.publish:
          id: status_text
          state: "Active"
    on_release:
      - text_sensor.template.publish:
          id: status_text
          state: "Idle"
```

### WiFi Info

```yaml
text_sensor:
  - platform: wifi_info
    ip_address:
      name: "IP Address"
    ssid:
      name: "Connected SSID"
    bssid:
      name: "Connected BSSID"
    mac_address:
      name: "MAC Address"
```

### Version Info

```yaml
text_sensor:
  - platform: version
    name: "ESPHome Version"
    hide_timestamp: true
```

### Last Boot Time

```yaml
time:
  - platform: sntp
    id: sntp_time

text_sensor:
  - platform: template
    name: "Last Boot"
    id: last_boot
    update_interval: never

esphome:
  on_boot:
    priority: -100
    then:
      - text_sensor.template.publish:
          id: last_boot
          state: !lambda |-
            char str[25];
            time_t now = id(sntp_time).now().timestamp;
            strftime(str, sizeof(str), "%Y-%m-%d %H:%M:%S", localtime(&now));
            return str;
```

### Formatted Sensor Values

```yaml
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      id: temp
    humidity:
      id: hum

text_sensor:
  - platform: template
    name: "Environment"
    lambda: |-
      char buf[50];
      snprintf(buf, sizeof(buf), "%.1f°C / %.1f%%",
               id(temp).state, id(hum).state);
      return std::string(buf);
    update_interval: 30s
```

---

## Tuya Integration

Tuya devices often use these components for configuration.

### Tuya Number

```yaml
tuya:

number:
  - platform: tuya
    name: "Temperature Setpoint"
    number_datapoint: 2
    min_value: 15
    max_value: 35
    step: 1
    unit_of_measurement: "°C"
```

### Tuya Select

```yaml
select:
  - platform: tuya
    name: "Mode"
    enum_datapoint: 4
    options:
      0: "Manual"
      1: "Schedule"
      2: "Away"
```

### Tuya Text

```yaml
text:
  - platform: tuya
    name: "Device Name"
    sensor_datapoint: 10
```

---

## Complete Examples

### Thermostat Controls

```yaml
number:
  - platform: template
    name: "Target Temperature"
    id: target_temp
    min_value: 15
    max_value: 30
    step: 0.5
    unit_of_measurement: "°C"
    optimistic: true
    restore_value: true
    initial_value: 21

select:
  - platform: template
    name: "Thermostat Mode"
    id: thermo_mode
    options:
      - "Off"
      - "Heat"
      - "Cool"
      - "Auto"
    optimistic: true
    restore_value: true
    initial_option: "Off"

button:
  - platform: template
    name: "Reset to Defaults"
    on_press:
      - number.set:
          id: target_temp
          value: 21
      - select.set:
          id: thermo_mode
          option: "Off"
```

### Display Configuration

```yaml
number:
  - platform: template
    name: "Display Brightness"
    id: display_brightness
    min_value: 0
    max_value: 100
    step: 10
    unit_of_measurement: "%"
    optimistic: true
    restore_value: true
    initial_value: 80
    entity_category: config

  - platform: template
    name: "Page Rotation Interval"
    id: page_interval
    min_value: 5
    max_value: 60
    step: 5
    unit_of_measurement: "s"
    optimistic: true
    restore_value: true
    initial_value: 10
    entity_category: config

select:
  - platform: template
    name: "Display Page"
    id: current_page
    options:
      - "Temperature"
      - "Humidity"
      - "Time"
      - "Status"
    optimistic: true
    on_value:
      - lambda: |-
          if (x == "Temperature") {
            id(oled).show_page(id(temp_page));
          } else if (x == "Humidity") {
            id(oled).show_page(id(hum_page));
          }
          // ...
```

### LED Strip Controller

```yaml
number:
  - platform: template
    name: "LED Count"
    id: led_count
    min_value: 1
    max_value: 300
    step: 1
    optimistic: true
    restore_value: true
    initial_value: 60
    entity_category: config

  - platform: template
    name: "Effect Speed"
    id: effect_speed
    min_value: 1
    max_value: 100
    step: 1
    unit_of_measurement: "%"
    optimistic: true
    initial_value: 50

select:
  - platform: template
    name: "Color Preset"
    id: color_preset
    options:
      - "Warm White"
      - "Cool White"
      - "Red"
      - "Green"
      - "Blue"
      - "Purple"
      - "Custom"
    optimistic: true
    on_value:
      - lambda: |-
          auto call = id(led_strip).turn_on();
          if (x == "Warm White") {
            call.set_rgb(1.0, 0.8, 0.6);
          } else if (x == "Cool White") {
            call.set_rgb(0.9, 0.95, 1.0);
          } else if (x == "Red") {
            call.set_rgb(1.0, 0.0, 0.0);
          }
          // ...
          call.perform();

button:
  - platform: template
    name: "All LEDs Off"
    on_press:
      - light.turn_off: led_strip
```
