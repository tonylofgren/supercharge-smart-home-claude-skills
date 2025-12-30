# Shelly Integration

Complete guide for integrating Shelly devices with Home Assistant.

---

## Overview

Shelly devices are popular WiFi-based smart home devices known for:

- **Local API** - No cloud required
- **Quality Hardware** - Reliable, certified
- **Compact Size** - Fits in electrical boxes
- **Power Monitoring** - Built into most devices
- **Easy Setup** - Works out of the box with HA

### Integration Methods

| Method | Best For |
|--------|----------|
| **Native Integration** | Most users, simplest setup |
| **MQTT** | Advanced users, complex automations |
| **CoAP/CoIoT** | Legacy Gen1 devices |

---

## Native Shelly Integration

### Auto-Discovery

Shelly devices are automatically discovered via mDNS:

1. Connect Shelly to your network
2. Go to **Settings > Devices & Services**
3. Shelly appears in **Discovered** section
4. Click **Configure** to add

### Manual Setup

If not discovered:

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Shelly**
3. Enter device IP address
4. Configure authentication if needed

### Configuration

```yaml
# No YAML needed - configured via UI

# Optional: Push update interval
shelly:
  coap_timeout: 30  # Gen1 devices
```

---

## Gen1 vs Gen2+ Devices

### Gen1 Devices

- Uses CoAP/CoIoT protocol
- Older firmware (pre-2022)
- Examples: Shelly 1, Shelly 2.5, Shelly Dimmer

### Gen2+ Devices (Plus/Pro)

- Uses RPC/WebSocket
- Modern firmware
- Examples: Shelly Plus 1, Shelly Pro 4PM, Shelly Plus 2PM

### Feature Comparison

| Feature | Gen1 | Gen2+ |
|---------|------|-------|
| **Protocol** | CoAP | RPC |
| **Scripting** | No | Yes (JS) |
| **BLE Support** | Limited | Yes |
| **Bluetooth Gateway** | No | Yes |
| **Virtual Components** | No | Yes |

---

## Device Types

### Relays (Shelly 1, Plus 1, Pro 1)

```yaml
# Single channel relay
# Creates: switch.shelly_1_switch_0

automation:
  - alias: "Garage light timer"
    trigger:
      - platform: state
        entity_id: switch.shelly_garage_switch_0
        to: "on"
    action:
      - delay: "00:15:00"
      - service: switch.turn_off
        target:
          entity_id: switch.shelly_garage_switch_0
```

### Multi-Channel Relays (Shelly 2.5, Plus 2PM, Pro 4PM)

```yaml
# Multiple channels
# Creates: switch.shelly_2_switch_0, switch.shelly_2_switch_1

automation:
  - alias: "All lights off"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.shelly_switch_0
            - switch.shelly_switch_1
```

### Dimmers (Shelly Dimmer, Plus Dimmer)

```yaml
# Dimmer creates light entity
# light.shelly_dimmer_0

automation:
  - alias: "Evening dimming"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.shelly_dimmer_0
        data:
          brightness_pct: 40
          transition: 30
```

### RGBW Controllers (Shelly RGBW2)

```yaml
# Creates light entity with color support
# light.shelly_rgbw2_0

automation:
  - alias: "Colorful evening"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.shelly_rgbw2_0
        data:
          rgb_color: [255, 147, 41]  # Warm orange
          brightness_pct: 80
```

### Energy Meters (Shelly EM, 3EM, Pro 3EM)

```yaml
# Creates sensor entities:
# sensor.shelly_em_channel_1_power
# sensor.shelly_em_channel_1_energy

# Monitor solar production
automation:
  - alias: "High solar production alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.shelly_em_channel_1_power
        above: 3000
    action:
      - service: notify.mobile_app
        data:
          message: "Solar producing {{ states('sensor.shelly_em_channel_1_power') }}W"
```

### Temperature & Humidity (Shelly H&T)

```yaml
# Battery-powered sensor
# sensor.shelly_ht_temperature
# sensor.shelly_ht_humidity
# sensor.shelly_ht_battery

automation:
  - alias: "Temperature alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.shelly_ht_temperature
        above: 28
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.living_room
        data:
          hvac_mode: cool
```

### Motion Sensors (Shelly Motion)

```yaml
# Battery-powered motion sensor
# binary_sensor.shelly_motion_motion

automation:
  - alias: "Motion-activated light"
    trigger:
      - platform: state
        entity_id: binary_sensor.shelly_motion_motion
        to: "on"
    condition:
      - condition: numeric_state
        entity_id: sensor.shelly_motion_lux
        below: 50
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
```

### Covers/Shutters (Shelly 2.5 in Roller Mode)

```yaml
# Shelly 2.5 configured as roller shutter
# cover.shelly_roller

automation:
  - alias: "Open blinds at sunrise"
    trigger:
      - platform: sun
        event: sunrise
        offset: "00:30:00"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.shelly_roller

# Position control
automation:
  - alias: "Afternoon shade"
    trigger:
      - platform: time
        at: "14:00:00"
    action:
      - service: cover.set_cover_position
        target:
          entity_id: cover.shelly_roller
        data:
          position: 50  # 50% open
```

---

## Button Events

Shelly devices expose button/input events as device triggers.

### Button Press Types

| Event | Description |
|-------|-------------|
| `single` | Single press |
| `double` | Double press |
| `triple` | Triple press |
| `long` | Long press |

### Button Automation

```yaml
automation:
  - alias: "Shelly button scenes"
    trigger:
      - platform: device
        domain: shelly
        device_id: abc123...
        type: single
        subtype: button1
        id: single
      - platform: device
        domain: shelly
        device_id: abc123...
        type: double
        subtype: button1
        id: double
      - platform: device
        domain: shelly
        device_id: abc123...
        type: long
        subtype: button1
        id: long
    action:
      - choose:
          - conditions:
              - condition: trigger
                id: single
            sequence:
              - service: light.toggle
                target:
                  entity_id: light.living_room
          - conditions:
              - condition: trigger
                id: double
            sequence:
              - service: scene.turn_on
                target:
                  entity_id: scene.movie_mode
          - conditions:
              - condition: trigger
                id: long
            sequence:
              - service: light.turn_off
                target:
                  entity_id: all
```

---

## Power Monitoring

Most Shelly devices include power monitoring.

### Available Sensors

```yaml
# For Shelly Plus 1PM:
sensor.shelly_plus_1pm_power       # Current power (W)
sensor.shelly_plus_1pm_energy      # Total energy (kWh)
sensor.shelly_plus_1pm_voltage     # Voltage (V)
sensor.shelly_plus_1pm_current     # Current (A)
```

### Power Monitoring Automations

```yaml
# Appliance state detection
automation:
  - alias: "Washing machine finished"
    trigger:
      - platform: numeric_state
        entity_id: sensor.shelly_washer_power
        below: 5
        for: "00:02:00"
    condition:
      - condition: state
        entity_id: input_boolean.washer_running
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Washing machine finished!"
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.washer_running

# Power threshold alert
automation:
  - alias: "High power consumption"
    trigger:
      - platform: numeric_state
        entity_id: sensor.shelly_main_power
        above: 3000
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          message: "High power consumption: {{ states('sensor.shelly_main_power') }}W"
```

---

## MQTT Mode

For advanced control, configure Shelly for MQTT.

### Enable MQTT on Shelly

In Shelly web UI:
1. Go to **Internet & Security** > **MQTT**
2. Enable MQTT
3. Enter broker details:
   - Server: `192.168.1.100:1883`
   - User/Password
4. Save and reboot

### MQTT Topics

```yaml
# Gen1 topic structure
shellies/<device-id>/relay/0
shellies/<device-id>/relay/0/command

# Gen2 topic structure (configurable)
<topic-prefix>/status/switch:0
<topic-prefix>/command/switch:0
```

### MQTT Automation

```yaml
# Direct MQTT control
automation:
  - alias: "MQTT switch control"
    trigger:
      - platform: state
        entity_id: input_boolean.garage_light
    action:
      - service: mqtt.publish
        data:
          topic: "shellies/shelly1-123456/relay/0/command"
          payload: "{{ 'on' if trigger.to_state.state == 'on' else 'off' }}"
```

---

## Scripting (Gen2+ Only)

Gen2 devices support JavaScript scripting.

### Example Script: Presence Timeout

```javascript
// Auto-off after 30 minutes of no motion
let timeout = 30 * 60 * 1000;
let timer = null;

Shelly.addEventHandler(function(e) {
  if (e.component === "input:0") {
    if (e.info.state) {
      // Motion detected
      Shelly.call("Switch.Set", {id: 0, on: true});
      if (timer) Timer.clear(timer);
      timer = Timer.set(timeout, false, function() {
        Shelly.call("Switch.Set", {id: 0, on: false});
      });
    }
  }
});
```

### Managing Scripts

1. Access Shelly web UI
2. Go to **Scripts**
3. Create/edit scripts
4. Enable script to run on boot

---

## Firmware Updates

### Via Home Assistant

1. Go to device page in HA
2. Check **Firmware** sensor
3. Use **Update** entity to upgrade

### Via Shelly Web UI

1. Access device web interface
2. Go to **Settings** > **Firmware**
3. Click **Update**

### Via Shelly Cloud

1. Open Shelly app
2. Select device
3. Check for updates

---

## Troubleshooting

### Device Not Discovered

1. **Check network connectivity** - ping device IP
2. **Verify same subnet** - Shelly must be on same network
3. **Check firewall** - mDNS (5353) must be allowed
4. **Manually add** by IP address

### Connection Issues

```yaml
# Check device connectivity
# Access Shelly web UI: http://192.168.1.xxx

# If using CoAP (Gen1), check timeout
shelly:
  coap_timeout: 60  # Increase if needed
```

### Button Events Not Working

1. **Check device configuration** - Button mode must be "detached" or "momentary"
2. **Verify firmware** - Update to latest
3. **Check automation triggers** - Use correct event type

### Power Values Wrong

1. **Calibrate device** - Some require calibration
2. **Check load type** - Inductive loads may read differently
3. **Verify wiring** - Current sensor must be on correct wire

---

## Best Practices

### Network Setup

```yaml
# 1. Use static IP or DHCP reservations
# 2. Keep Shelly on main network (not IoT VLAN if using mDNS discovery)
# 3. Ensure mDNS traffic allowed between HA and Shelly subnet
```

### Device Configuration

```yaml
# 1. Set meaningful device names in Shelly web UI
# 2. Configure button type (momentary/toggle/edge)
# 3. Enable power-on state if needed
# 4. Set max power limit for safety
```

### Reliability

```yaml
# 1. Keep firmware updated
# 2. Monitor device availability
# 3. Use appropriate Shelly for load type
# 4. Don't exceed rated power
```

---

## Reference

### Useful Links

- [Shelly Integration Docs](https://www.home-assistant.io/integrations/shelly/)
- [Shelly Knowledge Base](https://kb.shelly.cloud/)
- [Shelly API Reference](https://shelly-api-docs.shelly.cloud/)
- [Shelly Scripting](https://shelly-api-docs.shelly.cloud/gen2/Scripts/)

### Device Comparison

| Device | Channels | Power Monitor | Max Load |
|--------|----------|---------------|----------|
| Shelly 1 | 1 | No | 16A |
| Shelly 1PM | 1 | Yes | 16A |
| Shelly Plus 1 | 1 | No | 16A |
| Shelly Plus 1PM | 1 | Yes | 16A |
| Shelly 2.5 | 2 | Yes | 10A each |
| Shelly Plus 2PM | 2 | Yes | 10A each |
| Shelly Pro 4PM | 4 | Yes | 16A each |
| Shelly Dimmer 2 | 1 | Yes | 200W |
| Shelly Plus Dimmer | 1 | Yes | 200W |
