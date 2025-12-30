# ESPHome Home Assistant Integration

## Table of Contents
- [API Configuration](#api-configuration)
- [Reading HA Entities](#reading-ha-entities)
- [Custom Services](#custom-services)
- [Sending Events](#sending-events)
- [Time Synchronization](#time-synchronization)
- [Input Components](#input-components)
- [Device Triggers](#device-triggers)
- [Bluetooth Proxy](#bluetooth-proxy)
- [Voice Assistant](#voice-assistant)

---

## API Configuration

### Basic Setup

```yaml
api:
  encryption:
    key: "base64-encoded-32-byte-key"  # Generate with: openssl rand -base64 32
```

### Full Options

```yaml
api:
  encryption:
    key: !secret api_encryption_key

  password: !secret api_password           # Legacy, use encryption instead

  port: 6053                               # Default port

  reboot_timeout: 15min                    # Reboot if no client for this duration
                                           # Set to 0s to disable

  services:                                # Custom services (see below)
    - service: my_service
      then:
        - switch.turn_on: relay

  on_client_connected:
    then:
      - logger.log: "HA connected"

  on_client_disconnected:
    then:
      - logger.log: "HA disconnected"
```

### Generate Encryption Key

```bash
# Linux/Mac
openssl rand -base64 32

# Or use Python
python3 -c "import secrets; import base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

---

## Reading HA Entities

### Sensors from Home Assistant

```yaml
sensor:
  - platform: homeassistant
    id: outdoor_temp
    entity_id: sensor.outdoor_temperature
    name: "Outdoor Temperature"

  - platform: homeassistant
    id: electricity_price
    entity_id: sensor.nordpool_kwh_se3_sek_3_10_025
    attribute: current_price    # Read specific attribute
```

### Binary Sensors from Home Assistant

```yaml
binary_sensor:
  - platform: homeassistant
    id: vacation_mode
    entity_id: input_boolean.vacation_mode
    name: "Vacation Mode"
    on_state:
      then:
        - if:
            condition:
              binary_sensor.is_on: vacation_mode
            then:
              - climate.control:
                  id: thermostat
                  mode: "OFF"
```

### Text Sensors from Home Assistant

```yaml
text_sensor:
  - platform: homeassistant
    id: current_user
    entity_id: sensor.current_user
    name: "Current User"

  - platform: homeassistant
    id: weather_condition
    entity_id: weather.home
    attribute: condition
```

### Using HA Values in Lambdas

```yaml
sensor:
  - platform: template
    name: "Adjusted Temperature"
    lambda: |-
      if (id(outdoor_temp).has_state()) {
        return id(indoor_temp).state - (id(outdoor_temp).state * 0.1);
      }
      return id(indoor_temp).state;
```

---

## Custom Services

### Basic Service

```yaml
api:
  services:
    - service: reset_filter_timer
      then:
        - globals.set:
            id: filter_hours
            value: '0'
        - logger.log: "Filter timer reset"
```

### Service with Parameters

```yaml
api:
  services:
    - service: set_brightness
      variables:
        level: int              # int, float, bool, string
      then:
        - light.turn_on:
            id: led
            brightness: !lambda return level / 100.0;

    - service: play_rtttl
      variables:
        song_str: string
      then:
        - rtttl.play:
            rtttl: !lambda return song_str;

    - service: set_target_temperature
      variables:
        temp: float
      then:
        - climate.control:
            id: thermostat
            target_temperature: !lambda return temp;
```

### Calling Services from HA

```yaml
# In Home Assistant automation/script:
service: esphome.device_name_set_brightness
data:
  level: 75

service: esphome.device_name_play_rtttl
data:
  song_str: "TakeOnMe:d=4,o=4,b=160:8f#5,8f#5,8f#5,8d5,8p,8b,8p,8e5"
```

---

## Sending Events

### Fire Event to HA

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_press:
      - homeassistant.event:
          event: esphome.button_pressed
          data:
            device: "${device_name}"
            button: "main"

    on_multi_click:
      - timing:
          - ON for at most 1s
          - OFF for at most 1s
          - ON for at most 1s
        then:
          - homeassistant.event:
              event: esphome.button_double_pressed
              data:
                device: "${device_name}"
```

### Dynamic Event Data

```yaml
on_press:
  - homeassistant.event:
      event: esphome.sensor_alert
      data:
        temperature: !lambda return to_string(id(temp).state);
        humidity: !lambda return to_string(id(humidity).state);
        timestamp: !lambda |-
          auto time = id(ha_time).now();
          return time.strftime("%Y-%m-%d %H:%M:%S");
```

### Using Events in HA

```yaml
# Home Assistant automation trigger:
trigger:
  - platform: event
    event_type: esphome.button_pressed
    event_data:
      device: "living_room_switch"
      button: "main"
```

---

## Time Synchronization

### Basic Time Sync

```yaml
time:
  - platform: homeassistant
    id: ha_time
```

### With Timezone

```yaml
time:
  - platform: homeassistant
    id: ha_time
    timezone: Europe/Stockholm

    on_time_sync:
      then:
        - logger.log: "Time synchronized with HA"

    on_time:
      - seconds: 0
        minutes: 0
        hours: 8
        then:
          - script.execute: morning_routine
```

### Using Time in Lambdas

```yaml
lambda: |-
  auto time = id(ha_time).now();
  if (!time.is_valid())
    return {};

  // Access components
  int hour = time.hour;         // 0-23
  int minute = time.minute;     // 0-59
  int second = time.second;     // 0-59
  int day = time.day_of_week;   // 1=Sunday, 7=Saturday
  int day_of_month = time.day_of_month;  // 1-31
  int month = time.month;       // 1-12
  int year = time.year;         // e.g., 2024

  // Format as string
  std::string formatted = time.strftime("%H:%M:%S");

  // Check time ranges
  bool is_daytime = hour >= 8 && hour < 22;
  bool is_weekend = day == 1 || day == 7;
```

---

## Input Components

### Number Input

```yaml
number:
  - platform: template
    name: "Target Temperature"
    id: target_temp
    min_value: 15
    max_value: 30
    step: 0.5
    initial_value: 21
    restore_value: true
    optimistic: true
    unit_of_measurement: "C"
    device_class: temperature
    on_value:
      then:
        - climate.control:
            id: thermostat
            target_temperature: !lambda return x;
```

### Select Input

```yaml
select:
  - platform: template
    name: "Operation Mode"
    id: operation_mode
    options:
      - "Auto"
      - "Manual"
      - "Away"
    initial_option: "Auto"
    restore_value: true
    optimistic: true
    on_value:
      then:
        - logger.log:
            format: "Mode changed to: %s"
            args: ['x.c_str()']
```

### Text Input

```yaml
text:
  - platform: template
    name: "Device Name"
    id: custom_name
    mode: text              # text, password
    min_length: 1
    max_length: 32
    initial_value: "My Device"
    restore_value: true
    optimistic: true
```

### Button

```yaml
button:
  - platform: template
    name: "Reset Counter"
    on_press:
      - globals.set:
          id: counter
          value: '0'

  - platform: restart
    name: "Restart Device"

  - platform: safe_mode
    name: "Safe Mode Boot"

  - platform: factory_reset
    name: "Factory Reset"
```

### Switch (HA Controllable)

```yaml
switch:
  - platform: template
    name: "Night Mode"
    id: night_mode
    restore_mode: RESTORE_DEFAULT_OFF
    optimistic: true
    on_turn_on:
      - light.turn_off: main_light
      - light.turn_on:
          id: night_light
          brightness: 10%
    on_turn_off:
      - light.turn_off: night_light
```

---

## Device Triggers

ESPHome can create device triggers that appear in HA's device page.

### Automation Triggers

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    name: "Button"
    device_class: None
    on_press:
      - homeassistant.event:
          event: esphome.button_pressed
```

### In HA Device Automation

These show up under Device > Automations:
- `esphome.button_pressed` event triggers
- Binary sensor state changes
- Sensor value changes

---

## Bluetooth Proxy

Enable Bluetooth device support in Home Assistant.

```yaml
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: true

bluetooth_proxy:
  active: true              # Allows HA to connect to BLE devices
```

### Passive Only (Lower Power)

```yaml
esp32_ble_tracker:

bluetooth_proxy:
  active: false             # Only forward advertisements
```

---

## Voice Assistant

Enable voice assistant features.

### Basic Voice Assistant

```yaml
voice_assistant:
  microphone: mic
  speaker: speaker
  noise_suppression_level: 2
  auto_gain: 31dBFS
  volume_multiplier: 2.0

  on_listening:
    - light.turn_on:
        id: led
        effect: "Listening"

  on_stt_end:
    - light.turn_on:
        id: led
        effect: "Processing"

  on_tts_start:
    - light.turn_on:
        id: led
        effect: "Speaking"

  on_end:
    - light.turn_off: led

  on_error:
    - light.turn_on:
        id: led
        red: 100%
        green: 0%
        blue: 0%
```

### Wake Word Detection

```yaml
micro_wake_word:
  models:
    - model: okay_nabu

  on_wake_word_detected:
    - voice_assistant.start:

voice_assistant:
  microphone: mic
  speaker: speaker
```

### Media Player Integration

```yaml
media_player:
  - platform: i2s_audio
    id: media_out
    name: "Media Player"
    dac_type: external
    i2s_dout_pin: GPIO22
    mode: stereo
```

---

## Entity Configuration

### Entity Categories

```yaml
sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    entity_category: diagnostic    # Hidden from main UI

  - platform: uptime
    name: "Uptime"
    entity_category: diagnostic

switch:
  - platform: restart
    name: "Restart"
    entity_category: config        # Shows in device config
```

### Disabled by Default

```yaml
sensor:
  - platform: debug
    free:
      name: "Free Heap"
      disabled_by_default: true    # User must enable in HA
```

### Internal Only

```yaml
sensor:
  - platform: adc
    id: battery_voltage
    internal: true                 # Not exposed to HA at all
```

---

## Best Practices

1. **Use encryption** - Always set `api.encryption.key`
2. **Set reboot_timeout** - Prevents devices being stuck offline
3. **Use entity_category** - Keep diagnostic sensors organized
4. **Cache HA sensor values** - Check `has_state()` before using
5. **Handle disconnects** - Add fallback behavior when HA unavailable
6. **Minimize HA sensors** - Polling HA adds load; cache locally
7. **Use events** for buttons - More flexible than binary sensors
8. **Name services clearly** - They show up as `esphome.device_name_service`
