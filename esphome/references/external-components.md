# ESPHome External Components Reference

Community-developed components not included in official ESPHome.

## Table of Contents
- [Using External Components](#using-external-components)
- [Smart Home Integration](#smart-home-integration)
- [Climate & HVAC](#climate--hvac)
- [Energy & Solar](#energy--solar)
- [Security Systems](#security-systems)
- [Specialty Devices](#specialty-devices)
- [Bluetooth & Network](#bluetooth--network)

---

## Using External Components

### Basic Syntax
```yaml
external_components:
  # From GitHub repository
  - source: github://username/repo@branch
    components: [component_name]

  # From GitHub PR (for testing)
  - source: github://pr#1234
    components: [my_component]

  # From local folder
  - source:
      type: local
      path: my_components
    components: [my_component]

  # Refresh interval (default: 1d)
  - source: github://user/repo
    refresh: 0s  # Always fetch latest
```

### Example with Multiple Sources
```yaml
external_components:
  - source: github://ssieb/esphome_components@main
    components: [opentherm]
  - source: github://oxan/esphome-stream-server
    components: [stream_server]
```

---

## Smart Home Integration

### Apple HomeKit
Connect ESPHome devices to Apple Home without a bridge.

```yaml
# Source: github://rednblkx/HAP-ESPHome
external_components:
  - source: github://rednblkx/HAP-ESPHome@main
    components: [homekit]

homekit:
  password: "111-22-333"

light:
  - platform: binary
    id: my_light
    name: "Light"
    output: light_output
    # Automatically exposed to HomeKit
```

### Nuki Smart Lock
Control Nuki locks via BLE.

```yaml
# Source: github://uriyacovy/ESPHome_nuki_lock
external_components:
  - source: github://uriyacovy/ESPHome_nuki_lock@main
    components: [nuki_lock]

esp32_ble_tracker:

nuki_lock:
  name: "Front Door"
  id: nuki_front
  # Pair via Nuki app first

lock:
  - platform: nuki_lock
    name: "Nuki Lock"
    nuki_lock_id: nuki_front
```

### Roomba Bridge
Control iRobot Roomba without cloud.

```yaml
# Source: github://mannkind/ESPHomeRoombaComponent
external_components:
  - source: github://mannkind/ESPHomeRoombaComponent@main
    components: [roomba]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 115200

roomba:
  id: my_roomba

vacuum:
  - platform: roomba
    name: "Roomba"
    roomba_id: my_roomba
```

### RatGDO Garage Door
Direct garage door opener control (Security+ 2.0).

```yaml
# Source: github://ratgdo/esphome-ratgdo
external_components:
  - source: github://ratgdo/esphome-ratgdo@main
    components: [ratgdo]

ratgdo:
  id: garage_ratgdo
  input_gdo_pin: GPIO4
  output_gdo_pin: GPIO5
  input_obst_pin: GPIO6

cover:
  - platform: ratgdo
    name: "Garage Door"
    ratgdo_id: garage_ratgdo

binary_sensor:
  - platform: ratgdo
    type: obstruction
    name: "Obstruction"
    ratgdo_id: garage_ratgdo
```

---

## Climate & HVAC

### OpenTherm Thermostat
Control OpenTherm boilers directly.

```yaml
# Source: github://arthurrump/esphome-opentherm
external_components:
  - source: github://arthurrump/esphome-opentherm@main
    components: [opentherm]

opentherm:
  in_pin: GPIO4
  out_pin: GPIO5

sensor:
  - platform: opentherm
    boiler_temperature:
      name: "Boiler Temperature"
    return_temperature:
      name: "Return Temperature"
    modulation:
      name: "Modulation"

climate:
  - platform: opentherm
    name: "OpenTherm"
```

### Mitsubishi Heat Pump
Control Mitsubishi via CN105 connector.

```yaml
# Source: github://geoffdavis/esphome-mitsubishiheatpump
external_components:
  - source: github://geoffdavis/esphome-mitsubishiheatpump@main
    components: [mitsubishi_heatpump]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 2400

climate:
  - platform: mitsubishi_heatpump
    name: "Heat Pump"
    horizontal_vane_select:
      name: "Horizontal Vane"
    vertical_vane_select:
      name: "Vertical Vane"
```

### Panasonic AC
Cloud-free Panasonic air conditioner control.

```yaml
# Source: github://DomiStyle/esphome-panasonic-ac
external_components:
  - source: github://DomiStyle/esphome-panasonic-ac@main
    components: [panasonic_ac]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 9600

climate:
  - platform: panasonic_ac
    name: "Panasonic AC"
    # CNT interface connection
```

### Samsung HVAC (NASA Protocol)
Control Samsung HVAC with NASA protocol.

```yaml
# Source: github://lanwin/esphome_samsung_ac
external_components:
  - source: github://lanwin/esphome_samsung_ac@main
    components: [samsung_ac]

uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
  parity: EVEN

samsung_ac:
  debug_log_messages: false

climate:
  - platform: samsung_ac
    name: "Samsung AC"
    unit: "00"
```

### Nibe Heat Pump
Modbus control for Nibe heat pumps.

```yaml
# Source: github://elupus/esphome-nibe
external_components:
  - source: github://elupus/esphome-nibe@main
    components: [nibe]

uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600

nibe:
  - id: nibe_hp

sensor:
  - platform: nibe
    nibe_id: nibe_hp
    address: 40004
    name: "Outdoor Temperature"
```

### Ecodan Heat Pump
Mitsubishi Ecodan heat pump control.

```yaml
# Source: github://fonske/esphome-ecodan
external_components:
  - source: github://fonske/esphome-ecodan@main
    components: [ecodan]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 2400

climate:
  - platform: ecodan
    name: "Ecodan"
```

---

## Energy & Solar

### Victron MPPT
Monitor Victron solar charge controllers via VE.Direct.

```yaml
# Source: github://KinDR007/VictronMPPT-ESPHOME
external_components:
  - source: github://KinDR007/VictronMPPT-ESPHOME@main
    components: [victron]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 19200

victron:
  id: victron_mppt

sensor:
  - platform: victron
    victron_id: victron_mppt
    panel_voltage:
      name: "PV Voltage"
    panel_power:
      name: "PV Power"
    battery_voltage:
      name: "Battery Voltage"
    battery_current:
      name: "Battery Current"
    yield_today:
      name: "Yield Today"
```

### JK-BMS
Monitor JK battery management systems.

```yaml
# Source: github://syssi/esphome-jk-bms
external_components:
  - source: github://syssi/esphome-jk-bms@main
    components: [jk_bms_ble]

esp32_ble_tracker:

jk_bms_ble:
  - id: jk_bms
    mac_address: "C8:47:8C:XX:XX:XX"

sensor:
  - platform: jk_bms_ble
    jk_bms_ble_id: jk_bms
    total_voltage:
      name: "Total Voltage"
    current:
      name: "Current"
    power:
      name: "Power"
    state_of_charge:
      name: "SoC"
    temperature_sensor_1:
      name: "Temp 1"
```

### PowMr Hybrid Inverter
Control PowMr/MPP Solar inverters via Modbus.

```yaml
# Source: github://odya/esphome-powmr-hybrid-inverter
external_components:
  - source: github://odya/esphome-powmr-hybrid-inverter@main
    components: [powmr_hybrid]

uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 2400
  parity: NONE

modbus:
  id: modbus_hub

powmr_hybrid:
  modbus_id: modbus_hub
  address: 0x01

sensor:
  - platform: powmr_hybrid
    pv_input_voltage:
      name: "PV Voltage"
    pv_input_power:
      name: "PV Power"
    battery_voltage:
      name: "Battery Voltage"
    output_load_percent:
      name: "Load"
```

### Pipsolar / Voltronic
RS232 control for Pipsolar inverters.

```yaml
# Source: github://syssi/esphome-pipsolar
external_components:
  - source: github://syssi/esphome-pipsolar@main
    components: [pipsolar]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 2400

pipsolar:
  id: inverter

sensor:
  - platform: pipsolar
    pipsolar_id: inverter
    grid_voltage:
      name: "Grid Voltage"
    pv_input_voltage:
      name: "PV Voltage"
    battery_voltage:
      name: "Battery Voltage"
```

### Deye Inverter
Monitor Deye/Sunsynk inverters.

```yaml
# Source: github://klatremis/esphome-for-deye
external_components:
  - source: github://klatremis/esphome-for-deye@main
    components: [deye]

uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600

modbus:
  id: modbus_hub

deye:
  modbus_id: modbus_hub
  address: 0x01

sensor:
  - platform: deye
    pv1_voltage:
      name: "PV1 Voltage"
    pv1_power:
      name: "PV1 Power"
    battery_voltage:
      name: "Battery Voltage"
```

---

## Security Systems

### DSC Keybus
Interface with DSC PowerSeries alarm panels.

```yaml
# Source: github://Dilbert66/esphome-dsckeybus
external_components:
  - source: github://Dilbert66/esphome-dsckeybus@main
    components: [dscKeybusInterface]

dscKeybusInterface:
  id: dsc_panel
  dscClockPin: GPIO18
  dscReadPin: GPIO19
  dscWritePin: GPIO21

binary_sensor:
  - platform: dscKeybusInterface
    zone: 1
    name: "Zone 1"
```

### Vista ECP (Honeywell/Ademco)
Control Honeywell Vista alarm systems.

```yaml
# Source: github://Dilbert66/esphome-vistaECP
external_components:
  - source: github://Dilbert66/esphome-vistaECP@main
    components: [vistaECP]

vistaECP:
  id: vista_panel
  rxPin: GPIO19
  txPin: GPIO18
  accessCode: "1234"

alarm_control_panel:
  - platform: vistaECP
    name: "Alarm Panel"
```

### Konnected Alarm
Interface for Konnected alarm boards.

```yaml
# Source: github://konnected-io/konnected-esphome
external_components:
  - source: github://konnected-io/konnected-esphome@main
    components: [konnected]

konnected:
  id: alarm_panel

binary_sensor:
  - platform: konnected
    zone: 1
    name: "Front Door"
    device_class: door
```

---

## Specialty Devices

### Philips Coffee Machine
Control Philips 2200/3200 series coffee machines.

```yaml
# Source: github://TillFleworken/ESPHome-Philips-Smart-Coffee
external_components:
  - source: github://TillFleworken/ESPHome-Philips-Smart-Coffee@main
    components: [philips_coffee_machine]

uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 115200

philips_coffee_machine:
  id: coffee
  display_uart: uart_bus
  mainboard_uart: uart_bus2

button:
  - platform: philips_coffee_machine
    philips_coffee_machine_id: coffee
    make_coffee:
      name: "Make Coffee"
```

### Tesla BLE
Communicate with Tesla vehicles via BLE.

```yaml
# Source: github://yoziru/esphome-tesla-ble
external_components:
  - source: github://yoziru/esphome-tesla-ble@main
    components: [tesla_ble_vehicle]

tesla_ble_vehicle:
  id: tesla
  vin: "5YJ3E1..."

lock:
  - platform: tesla_ble_vehicle
    name: "Tesla Lock"
    tesla_ble_vehicle_id: tesla
```

### iGrill BBQ Sensor
Read Weber iGrill temperature sensors.

```yaml
# Source: github://bendikwa/esphome-igrill
external_components:
  - source: github://bendikwa/esphome-igrill@main
    components: [igrill]

esp32_ble_tracker:

igrill:
  mac_address: "XX:XX:XX:XX:XX:XX"

sensor:
  - platform: igrill
    probe_1:
      name: "Probe 1"
    probe_2:
      name: "Probe 2"
```

### Xiaomi Air Purifier
Control Xiaomi air purifiers via UART.

```yaml
# Source: github://syssi/esphome-xiaomi-air-purifier
external_components:
  - source: github://syssi/esphome-xiaomi-air-purifier@main
    components: [xiaomi_miio]

uart:
  tx_pin: GPIO1
  rx_pin: GPIO3
  baud_rate: 115200

fan:
  - platform: xiaomi_miio
    name: "Air Purifier"

sensor:
  - platform: xiaomi_miio
    pm25:
      name: "PM2.5"
    temperature:
      name: "Temperature"
```

### DMX512 Lighting
Control DMX lighting fixtures.

```yaml
# Source: github://andyboeh/esphome-dmx512
external_components:
  - source: github://andyboeh/esphome-dmx512@main
    components: [dmx512]

dmx512:
  pin: GPIO5
  universe: 1
  num_channels: 512

output:
  - platform: dmx512
    channel: 1
    id: dmx_ch1
```

---

## Bluetooth & Network

### OpenHaystack (Apple Find My)
Make ESP32 trackable on Apple Find My network.

```yaml
# Source: github://MatthewBlam/openhaystack-esphome
external_components:
  - source: github://MatthewBlam/openhaystack-esphome@main
    components: [openhaystack]

openhaystack:
  # Generated public key from OpenHaystack app
  public_key: "base64-encoded-key"
```

### BLE Keyboard
Turn ESP32 into a Bluetooth keyboard.

```yaml
# Source: github://dmamontov/esphome-blekeyboard
external_components:
  - source: github://dmamontov/esphome-blekeyboard@main
    components: [ble_keyboard]

ble_keyboard:
  id: kb
  name: "ESP32 Keyboard"

button:
  - platform: template
    name: "Send Enter"
    on_press:
      - ble_keyboard.key:
          id: kb
          key: RETURN
```

### Stream Server (UART TCP Bridge)
Bridge UART to TCP for network access.

```yaml
# Source: github://oxan/esphome-stream-server
external_components:
  - source: github://oxan/esphome-stream-server@main
    components: [stream_server]

uart:
  id: my_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 115200

stream_server:
  uart_id: my_uart
  port: 1234
```

---

## Best Practices

### Version Pinning
```yaml
external_components:
  # Pin to specific commit for stability
  - source: github://user/repo@abc1234
    components: [component]

  # Or pin to release tag
  - source: github://user/repo@v1.2.3
    components: [component]
```

### Troubleshooting
```yaml
# Disable caching during development
external_components:
  - source: github://user/repo
    refresh: 0s  # Always fetch

# Enable verbose logging
logger:
  level: VERBOSE
```

### Component Conflicts
```yaml
# If components conflict, use component_sources
external_components:
  - source: github://user/repo
    components: [my_sensor]
    # Only import specific components
```
