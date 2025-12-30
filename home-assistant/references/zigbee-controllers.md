# Zigbee Controllers - Complete Reference

Reference for Zigbee button controllers and remotes in Home Assistant.

## ZHA vs Zigbee2MQTT

| Feature | ZHA | Zigbee2MQTT |
|---------|-----|-------------|
| Integration | Native HA | MQTT bridge |
| Configuration | GUI | YAML + Web UI |
| Device support | Good | Excellent |
| Custom quirks | Via Python | Via JS converters |
| Event format | `zha_event` | MQTT message |

---

## IKEA Controllers

### TRADFRI Remote (E1524/E1810)

5-button remote with dimming ring.

#### ZHA Events

```yaml
automation:
  trigger:
    - platform: event
      event_type: zha_event
      event_data:
        device_id: "abc123"
        command: "toggle"  # Center button
    - platform: event
      event_type: zha_event
      event_data:
        device_id: "abc123"
        command: "step_with_on_off"
        args: [0, 43, 5]  # Brightness up
    - platform: event
      event_type: zha_event
      event_data:
        device_id: "abc123"
        command: "step"
        args: [1, 43, 5]  # Brightness down
```

**Button Commands:**
- Center: `toggle`
- Brightness up: `step_with_on_off` (args[0]=0)
- Brightness down: `step` (args[0]=1)
- Left arrow: `press` (args[0]=257)
- Right arrow: `press` (args[0]=256)
- Hold: `hold` (args[0]=3329/3328)
- Release: `release`

#### Zigbee2MQTT Events

```yaml
automation:
  trigger:
    - platform: mqtt
      topic: "zigbee2mqtt/ikea_remote/action"
      payload: "toggle"
```

**Actions:**
- `toggle`, `brightness_up_click`, `brightness_down_click`
- `arrow_left_click`, `arrow_right_click`
- `brightness_up_hold`, `brightness_down_hold`
- `brightness_up_release`, `brightness_down_release`

---

### TRADFRI On/Off Switch (E1743)

2-button switch.

#### ZHA Events

```yaml
trigger:
  - platform: event
    event_type: zha_event
    event_data:
      device_id: "abc123"
      command: "on"  # Top button
  - platform: event
    event_type: zha_event
    event_data:
      device_id: "abc123"
      command: "off"  # Bottom button
```

**Commands:**
- Top press: `on`
- Bottom press: `off`
- Top hold: `move_with_on_off`
- Bottom hold: `move`
- Release: `stop`

#### Zigbee2MQTT

**Actions:** `on`, `off`, `brightness_move_up`, `brightness_move_down`, `brightness_stop`

---

### TRADFRI Shortcut Button (E1812)

Single button.

#### ZHA Events

```yaml
trigger:
  - platform: event
    event_type: zha_event
    event_data:
      device_id: "abc123"
      command: "on"  # Short press
  - platform: event
    event_type: zha_event
    event_data:
      device_id: "abc123"
      command: "move_with_on_off"  # Long press
```

#### Zigbee2MQTT

**Actions:** `on`, `off`, `brightness_move_up`, `brightness_stop`

---

### STYRBAR Remote (E2001/E2002)

4-button remote.

#### Zigbee2MQTT Actions

- `on`, `off`
- `brightness_move_up`, `brightness_move_down`, `brightness_stop`
- `arrow_left_click`, `arrow_right_click`
- `arrow_left_hold`, `arrow_right_hold`, `arrow_left_release`, `arrow_right_release`

---

### RODRET Dimmer (E2201)

2-button dimmer.

#### Zigbee2MQTT Actions

- `on`, `off`
- `brightness_move_up`, `brightness_move_down`, `brightness_stop`

---

### SOMRIG Shortcut Button (E2213)

2-button device.

#### Zigbee2MQTT Actions

- `1_short_release`, `1_long_press`, `1_double_press`
- `2_short_release`, `2_long_press`, `2_double_press`

---

## Philips Hue Controllers

### Hue Dimmer Switch (RWL020/RWL021)

4-button remote.

#### ZHA Events

```yaml
trigger:
  - platform: event
    event_type: zha_event
    event_data:
      device_id: "abc123"
      command: "on_press"
```

**Commands:**
- `on_press`, `on_hold`, `on_short_release`, `on_long_release`
- `off_press`, `off_hold`, `off_short_release`, `off_long_release`
- `up_press`, `up_hold`, `up_short_release`, `up_long_release`
- `down_press`, `down_hold`, `down_short_release`, `down_long_release`

#### Zigbee2MQTT Actions

- `on_press`, `on_hold`, `on_hold_release`
- `off_press`, `off_hold`, `off_hold_release`
- `up_press`, `up_hold`, `up_hold_release`
- `down_press`, `down_hold`, `down_hold_release`

---

### Hue Smart Button

Single button with multiple presses.

#### Zigbee2MQTT Actions

- `on_press`, `on_hold`, `on_hold_release`
- `off_press`, `off_hold`, `off_hold_release`

---

## Aqara Controllers

### Aqara Mini Switch (WXKG11LM)

Single button with gesture support.

#### ZHA Events

```yaml
trigger:
  - platform: event
    event_type: zha_event
    event_data:
      device_id: "abc123"
      command: "single"
```

**Commands:** `single`, `double`, `triple`, `quadruple`, `hold`, `release`

#### Zigbee2MQTT Actions

`single`, `double`, `triple`, `quadruple`, `hold`, `release`

---

### Aqara Opple Switch (6-button)

#### Zigbee2MQTT Actions

- `button_1_single`, `button_1_double`, `button_1_triple`, `button_1_hold`
- (Same pattern for buttons 2-6)

---

### Aqara Cube (MFKZQ01LM)

Gesture-based controller.

#### Zigbee2MQTT Actions

- `shake`, `throw`, `wakeup`, `fall`
- `tap`, `slide`, `flip180`, `flip90`
- `rotate_left`, `rotate_right`

---

## Sonoff Controllers

### SNZB-01 Button

Single button.

#### ZHA Events

**Commands:** `toggle`, `on`, `off` (single, double, long)

#### Zigbee2MQTT Actions

`single`, `double`, `long`

---

## Tuya Controllers

### Tuya 4-Button Scene Switch

#### Zigbee2MQTT Actions

- `1_single`, `1_double`, `1_hold`
- (Same for buttons 2-4)

---

## Blueprint Pattern for Controllers

### Universal Controller Blueprint

```yaml
blueprint:
  name: Universal Zigbee Controller
  domain: automation
  input:
    controller:
      name: Controller Device
      selector:
        device:
          integration: zha

    button_1_single:
      name: Button 1 Single Press
      default: []
      selector:
        action:

    button_1_double:
      name: Button 1 Double Press
      default: []
      selector:
        action:

    button_1_hold:
      name: Button 1 Hold
      default: []
      selector:
        action:

mode: single
max_exceeded: silent

trigger:
  - platform: event
    event_type: zha_event
    event_data:
      device_id: !input controller

action:
  - variables:
      command: "{{ trigger.event.data.command }}"
      args: "{{ trigger.event.data.args }}"

  - choose:
      - conditions: "{{ command == 'on' }}"
        sequence: !input button_1_single
      - conditions: "{{ command == 'off' }}"
        sequence: !input button_1_double
```

---

## Zigbee Groups

### Creating Groups in ZHA

1. Configuration → Devices → Select Zigbee device
2. Click "Add to Group"
3. Create or select existing group

### Groups in Zigbee2MQTT

```yaml
# configuration.yaml (Zigbee2MQTT)
groups:
  living_room_lights:
    friendly_name: "Living Room Lights"
    devices:
      - '0x00158d0001234567'
      - '0x00158d0009876543'
```

### Binding Controllers to Groups

ZHA:
1. Select controller device
2. Click "Bind to Device" or "Bind to Group"
3. Select target

Zigbee2MQTT:
```yaml
# In device settings
bind:
  - target: living_room_lights
    clusters:
      - genOnOff
      - genLevelCtrl
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Button not responding | Re-pair device, check battery |
| Delayed response | Check mesh, add routers |
| Wrong events | Check device quirks/converter |
| Missing double-click | Some devices need firmware update |

### Debug Events

ZHA:
```yaml
# In Developer Tools → Events
# Listen to: zha_event
```

Zigbee2MQTT:
```yaml
# Monitor MQTT topic
# zigbee2mqtt/<device_name>/action
```

### Force Re-interview

ZHA: Remove and re-pair device

Zigbee2MQTT:
```yaml
# Publish to zigbee2mqtt/bridge/request/device/interview
{"id": "0x00158d0001234567"}
```
