# ESPHome Remote Control Reference

Complete reference for IR and RF remote transmitters, receivers, and protocols.

## Table of Contents
- [Remote Transmitter](#remote-transmitter)
- [Remote Receiver](#remote-receiver)
- [IR Protocols](#ir-protocols)
- [RF 433MHz](#rf-433mhz)
- [RF CC1101](#rf-cc1101)
- [Actions and Triggers](#actions-and-triggers)
- [Learning Unknown Codes](#learning-unknown-codes)

---

## Remote Transmitter

### IR LED Setup
```yaml
remote_transmitter:
  pin: GPIO5
  carrier_duty_percent: 50%  # Standard for most IR
```

### IR with Transistor Driver
```yaml
# Use when IR LED needs more current
remote_transmitter:
  pin:
    number: GPIO5
    inverted: true  # Common for transistor circuits
  carrier_duty_percent: 50%
```

### Multiple Transmitters
```yaml
remote_transmitter:
  - id: ir_tx
    pin: GPIO5
    carrier_duty_percent: 50%
  - id: rf_tx
    pin: GPIO4
    carrier_duty_percent: 100%  # No carrier for RF
```

---

## Remote Receiver

### IR Receiver (TSOP38238, VS1838B)
```yaml
remote_receiver:
  pin:
    number: GPIO14
    inverted: true
    mode:
      input: true
      pullup: true
  dump: all  # Log all received codes
```

### RF 433MHz Receiver
```yaml
remote_receiver:
  pin: GPIO4
  dump: all
  filter: 200us
  idle: 10ms
  buffer_size: 2kb
```

### Receiver Options
| Option | Type | Description |
|--------|------|-------------|
| `dump` | list | Protocols to log (all, raw, nec, etc.) |
| `filter` | time | Minimum pulse length |
| `idle` | time | Gap before considering complete |
| `buffer_size` | size | Buffer for long codes |
| `tolerance` | percent | Timing tolerance (25%) |

### Dump Specific Protocols
```yaml
remote_receiver:
  pin: GPIO14
  dump:
    - nec
    - samsung
    - lg
    - sony
```

---

## IR Protocols

### NEC (Most TVs, generic remotes)
```yaml
# Transmit
on_...:
  - remote_transmitter.transmit_nec:
      address: 0x4040
      command: 0x12

# Receive trigger
binary_sensor:
  - platform: remote_receiver
    name: "NEC Button"
    nec:
      address: 0x4040
      command: 0x12
```

### Samsung
```yaml
# Transmit
on_...:
  - remote_transmitter.transmit_samsung:
      data: 0xE0E040BF

# Alternative format
  - remote_transmitter.transmit_samsung:
      address: 0x07
      command: 0x02

# Receive
binary_sensor:
  - platform: remote_receiver
    name: "Samsung Button"
    samsung:
      data: 0xE0E040BF
```

### Samsung36
```yaml
on_...:
  - remote_transmitter.transmit_samsung36:
      address: 0x0400
      command: 0x000E00FF
```

### LG
```yaml
# Transmit
on_...:
  - remote_transmitter.transmit_lg:
      data: 0x20DF10EF
      nbits: 32

# Receive
binary_sensor:
  - platform: remote_receiver
    name: "LG Button"
    lg:
      data: 0x20DF10EF
```

### Sony
```yaml
# Transmit (12, 15, or 20 bit)
on_...:
  - remote_transmitter.transmit_sony:
      data: 0xA90
      nbits: 12

# Receive
binary_sensor:
  - platform: remote_receiver
    name: "Sony Button"
    sony:
      data: 0xA90
      nbits: 12
```

### Panasonic
```yaml
# Transmit
on_...:
  - remote_transmitter.transmit_panasonic:
      address: 0x4004
      command: 0x100BCBD

# Receive
binary_sensor:
  - platform: remote_receiver
    name: "Panasonic Button"
    panasonic:
      address: 0x4004
      command: 0x100BCBD
```

### JVC
```yaml
on_...:
  - remote_transmitter.transmit_jvc:
      data: 0x5583
```

### RC5 (Philips)
```yaml
on_...:
  - remote_transmitter.transmit_rc5:
      address: 0x05
      command: 0x10
```

### RC6 (MCE remotes)
```yaml
on_...:
  - remote_transmitter.transmit_rc6:
      address: 0x00
      command: 0x0C
```

### Pioneer
```yaml
on_...:
  - remote_transmitter.transmit_pioneer:
      rc_code_1: 0xA55A
      rc_code_2: 0xA55A
      repeat: 2
```

### Pronto
```yaml
# For raw/hex codes from Pronto format
on_...:
  - remote_transmitter.transmit_pronto:
      data: "0000 006D 0022 0003 00A9 00A8..."
```

### Raw
```yaml
# Direct timing control
on_...:
  - remote_transmitter.transmit_raw:
      carrier_frequency: 38000Hz
      code: [4500, -4500, 560, -1690, 560, -560, ...]
```

---

## RF 433MHz

### RC Switch (Common 433MHz)
```yaml
# Type A: 10-bit DIP switch
on_...:
  - remote_transmitter.transmit_rc_switch_type_a:
      group: "11001"
      device: "01000"
      state: true

# Type B: Address/Channel
  - remote_transmitter.transmit_rc_switch_type_b:
      address: 3
      channel: 2
      state: true

# Type C: Family/Device
  - remote_transmitter.transmit_rc_switch_type_c:
      family: "a"
      group: 1
      device: 2
      state: true

# Type D: Group/Device
  - remote_transmitter.transmit_rc_switch_type_d:
      group: "a"
      device: 1
      state: true
```

### RC Switch Raw
```yaml
on_...:
  - remote_transmitter.transmit_rc_switch_raw:
      code: "101010100010001010100011"
      protocol: 1
```

### RC Switch Protocols
| Protocol | Pulse Length | Sync |
|----------|--------------|------|
| 1 | 350µs | 31 |
| 2 | 650µs | 10 |
| 3 | 100µs | 71 |
| 4 | 380µs | 6 |
| 5 | 500µs | 23 |

### Receive RC Switch
```yaml
binary_sensor:
  - platform: remote_receiver
    name: "RF Button"
    rc_switch_raw:
      code: "101010100010001010100011"
      protocol: 1
```

---

## RF CC1101

Sub-GHz transceiver for 315/433/868/915 MHz.

### CC1101 Setup
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

cc1101:
  - id: rf_transceiver
    cs_pin: GPIO5
    gdo0: GPIO4
    gdo2: GPIO2
    bandwidth: 200kHz
    frequency: 433920000  # 433.92 MHz
```

### CC1101 Transmit
```yaml
remote_transmitter:
  - platform: cc1101
    id: rf_tx
    cc1101_id: rf_transceiver
    carrier_duty_percent: 100%
```

### CC1101 Receive
```yaml
remote_receiver:
  - platform: cc1101
    cc1101_id: rf_transceiver
    dump: raw
```

---

## Actions and Triggers

### Button Actions
```yaml
button:
  - platform: template
    name: "TV Power"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x4040
          command: 0x12

  - platform: template
    name: "TV Volume Up"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x4040
          command: 0x13
```

### Repeat Transmission
```yaml
on_...:
  - remote_transmitter.transmit_nec:
      address: 0x4040
      command: 0x12
      repeat:
        times: 3
        wait_time: 50ms
```

### Binary Sensor Triggers
```yaml
binary_sensor:
  - platform: remote_receiver
    name: "Power Button"
    nec:
      address: 0x4040
      command: 0x12
    on_press:
      - light.toggle: my_light

  - platform: remote_receiver
    name: "Volume Up"
    nec:
      address: 0x4040
      command: 0x13
    on_press:
      - light.dim_relative:
          id: my_light
          relative_brightness: 10%
```

### On Raw Receive
```yaml
remote_receiver:
  pin: GPIO14
  on_raw:
    then:
      - lambda: |-
          ESP_LOGD("ir", "Received raw IR: %d pulses", x.size());
```

### On Specific Protocol
```yaml
remote_receiver:
  pin: GPIO14
  on_nec:
    then:
      - lambda: |-
          ESP_LOGD("ir", "NEC: addr=0x%04X cmd=0x%04X", x.address, x.command);

  on_samsung:
    then:
      - lambda: |-
          ESP_LOGD("ir", "Samsung: 0x%08X", x.data);
```

---

## Learning Unknown Codes

### Step 1: Enable Dump
```yaml
remote_receiver:
  pin:
    number: GPIO14
    inverted: true
    mode: INPUT_PULLUP
  dump: all
```

### Step 2: Read Logs
```
[D][remote.nec:049]: Received NEC: address=0x4040, command=0x12
```

### Step 3: Create Button
```yaml
button:
  - platform: template
    name: "Learned Button"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x4040
          command: 0x12
```

### Raw Code Learning
When protocol is unknown, use raw codes:

```yaml
# Log shows:
# [D][remote.raw:049]: Received Raw: 9000, -4500, 560, -1690, 560, -560...

# Use in transmit:
button:
  - platform: template
    name: "Raw Button"
    on_press:
      - remote_transmitter.transmit_raw:
          carrier_frequency: 38kHz
          code: [9000, -4500, 560, -1690, 560, -560]
```

---

## Common Patterns

### IR Remote Hub
```yaml
substitutions:
  device_name: "ir-hub"

esphome:
  name: ${device_name}

esp32:
  board: esp32dev

remote_transmitter:
  pin: GPIO5
  carrier_duty_percent: 50%

remote_receiver:
  pin:
    number: GPIO14
    inverted: true
    mode: INPUT_PULLUP
  dump: all

# TV Controls
button:
  - platform: template
    name: "TV Power"
    icon: "mdi:power"
    on_press:
      - remote_transmitter.transmit_samsung:
          data: 0xE0E040BF

  - platform: template
    name: "TV Volume Up"
    icon: "mdi:volume-plus"
    on_press:
      - remote_transmitter.transmit_samsung:
          data: 0xE0E0E01F

  - platform: template
    name: "TV Volume Down"
    icon: "mdi:volume-minus"
    on_press:
      - remote_transmitter.transmit_samsung:
          data: 0xE0E0D02F

  - platform: template
    name: "TV Mute"
    icon: "mdi:volume-mute"
    on_press:
      - remote_transmitter.transmit_samsung:
          data: 0xE0E0F00F
```

### RF Light Switches
```yaml
button:
  - platform: template
    name: "Living Room On"
    on_press:
      - remote_transmitter.transmit_rc_switch_type_a:
          group: "11001"
          device: "10000"
          state: true

  - platform: template
    name: "Living Room Off"
    on_press:
      - remote_transmitter.transmit_rc_switch_type_a:
          group: "11001"
          device: "10000"
          state: false
```

### AC Control via IR
```yaml
# See climate.md for IR climate platforms
climate:
  - platform: coolix
    name: "AC"
```

### Learn and Store Multiple Codes
```yaml
# Use Home Assistant to store learned codes and trigger via service
api:
  services:
    - service: send_raw_ir
      variables:
        code: int[]
      then:
        - remote_transmitter.transmit_raw:
            code: !lambda "return code;"
```

### RF Doorbell Trigger
```yaml
binary_sensor:
  - platform: remote_receiver
    name: "Doorbell"
    rc_switch_raw:
      code: "001100110011"
      protocol: 1
    on_press:
      - homeassistant.service:
          service: notify.mobile_app
          data:
            message: "Someone at the door!"
```

### RF Garage Door
```yaml
cover:
  - platform: template
    name: "Garage Door"
    open_action:
      - remote_transmitter.transmit_rc_switch_raw:
          code: "101010101010"
          protocol: 1
    close_action:
      - remote_transmitter.transmit_rc_switch_raw:
          code: "101010101010"  # Same code for toggle
          protocol: 1
    stop_action:
      - remote_transmitter.transmit_rc_switch_raw:
          code: "101010101010"
          protocol: 1
```

### Retransmit Received Code
```yaml
globals:
  - id: last_ir_code
    type: uint32_t
    initial_value: "0"

remote_receiver:
  pin: GPIO14
  on_nec:
    - lambda: |-
        id(last_ir_code) = (x.address << 16) | x.command;

button:
  - platform: template
    name: "Retransmit Last"
    on_press:
      - remote_transmitter.transmit_nec:
          address: !lambda "return id(last_ir_code) >> 16;"
          command: !lambda "return id(last_ir_code) & 0xFFFF;"
```

### IR Blaster with Web Interface
```yaml
web_server:
  port: 80

button:
  - platform: template
    name: "Device 1 Power"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x1234
          command: 0x56
```

---

## Troubleshooting

### IR Not Working
1. Check polarity of IR LED
2. Verify carrier frequency (usually 38kHz)
3. Add transistor if LED needs more current
4. Check receiver distance and angle

### RF Not Working
1. Check antenna length (17.3cm for 433MHz)
2. Verify protocol and timing
3. Try different buffer sizes
4. Check for interference

### Codes Not Matching
1. Use `tolerance: 35%` for looser matching
2. Compare raw codes for timing differences
3. Some remotes vary codes slightly each press
