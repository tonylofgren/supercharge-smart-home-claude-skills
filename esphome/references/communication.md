# ESPHome Communication Protocols Reference

Complete reference for communication buses and protocols.

## Table of Contents
- [I2C Bus](#i2c-bus)
- [SPI Bus](#spi-bus)
- [UART](#uart)
- [1-Wire](#1-wire)
- [CAN Bus](#can-bus)
- [Modbus](#modbus)

---

## I2C Bus

Two-wire serial bus for sensors and peripherals.

### Basic Setup
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true  # Scan for devices on boot
```

### ESP32 Default Pins
| Board | SDA | SCL |
|-------|-----|-----|
| ESP32 | GPIO21 | GPIO22 |
| ESP32-S2 | GPIO8 | GPIO9 |
| ESP32-S3 | GPIO8 | GPIO9 |
| ESP32-C3 | GPIO8 | GPIO9 |
| ESP8266 | GPIO4 | GPIO5 |

### Multiple I2C Buses
```yaml
i2c:
  - id: bus_a
    sda: GPIO21
    scl: GPIO22
  - id: bus_b
    sda: GPIO18
    scl: GPIO19

sensor:
  - platform: bme280_i2c
    i2c_id: bus_a
    address: 0x76
    # ...

  - platform: bme280_i2c
    i2c_id: bus_b
    address: 0x76
    # ...
```

### I2C Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sda` | pin | platform | Data pin |
| `scl` | pin | platform | Clock pin |
| `scan` | bool | false | Scan bus on startup |
| `frequency` | freq | 50kHz | Bus speed |

### Fast Mode (400kHz)
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22
  frequency: 400kHz
```

### I2C Scan Action
```yaml
button:
  - platform: template
    name: "I2C Scan"
    on_press:
      - lambda: |-
          Wire.begin();
          for (byte address = 1; address < 127; address++) {
            Wire.beginTransmission(address);
            if (Wire.endTransmission() == 0) {
              ESP_LOGI("i2c", "Device found at 0x%02X", address);
            }
          }
```

### Common I2C Addresses
| Device | Address |
|--------|---------|
| SSD1306 OLED | 0x3C or 0x3D |
| BME280/BMP280 | 0x76 or 0x77 |
| SHT3x | 0x44 or 0x45 |
| AHT10/20 | 0x38 |
| HTU21D | 0x40 |
| BH1750 | 0x23 or 0x5C |
| PCF8574 | 0x20-0x27 |
| PCA9685 | 0x40-0x7F |
| ADS1115 | 0x48-0x4B |

---

## SPI Bus

High-speed serial bus for displays, SD cards, and sensors.

### Basic Setup
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19
```

### ESP32 Default Pins
| Bus | CLK | MOSI | MISO |
|-----|-----|------|------|
| VSPI | GPIO18 | GPIO23 | GPIO19 |
| HSPI | GPIO14 | GPIO13 | GPIO12 |

### SPI Options
| Option | Type | Description |
|--------|------|-------------|
| `clk_pin` | pin | Clock pin (required) |
| `mosi_pin` | pin | Master Out Slave In |
| `miso_pin` | pin | Master In Slave Out |
| `interface` | string | hardware or any |

### Multiple SPI Buses
```yaml
spi:
  - id: spi_bus_1
    clk_pin: GPIO18
    mosi_pin: GPIO23
    miso_pin: GPIO19
  - id: spi_bus_2
    clk_pin: GPIO14
    mosi_pin: GPIO13
    miso_pin: GPIO12
```

### SPI Device Example
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

display:
  - platform: ili9xxx
    model: ILI9341
    spi_id: spi_bus_1
    cs_pin: GPIO5
    dc_pin: GPIO16
    # ...
```

---

## UART

Serial communication for sensors and devices.

### Basic Setup
```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
```

### UART Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `tx_pin` | pin | - | Transmit pin |
| `rx_pin` | pin | - | Receive pin |
| `baud_rate` | int | required | Baud rate |
| `data_bits` | int | 8 | Data bits |
| `parity` | string | NONE | NONE/EVEN/ODD |
| `stop_bits` | int | 1 | Stop bits |
| `rx_buffer_size` | int | 256 | RX buffer size |

### Multiple UARTs
```yaml
uart:
  - id: uart_sensor
    tx_pin: GPIO17
    rx_pin: GPIO16
    baud_rate: 9600
  - id: uart_debug
    tx_pin: GPIO1
    rx_pin: GPIO3
    baud_rate: 115200
```

### UART Debug (Log Raw Data)
```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
  debug:
    direction: BOTH
    dummy_receiver: false
    after:
      timeout: 100ms
    sequence:
      - lambda: |-
          UARTDebug::log_hex(direction, bytes, ' ');
```

### UART Write Actions
```yaml
on_...:
  # Write text
  - uart.write: "Hello\r\n"

  # Write bytes
  - uart.write: [0x55, 0xAA, 0x01]

  # Write with lambda
  - uart.write: !lambda |-
      return {0x55, 0xAA, (uint8_t)(value & 0xFF)};
```

### Read UART Data
```yaml
uart:
  id: my_uart
  # ...

interval:
  - interval: 100ms
    then:
      - lambda: |-
          while (id(my_uart).available()) {
            char c;
            id(my_uart).read_byte(&c);
            ESP_LOGD("uart", "Received: %c", c);
          }
```

### Custom UART Sensor
```yaml
uart:
  id: my_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600

sensor:
  - platform: custom
    lambda: |-
      auto my_sensor = new MyUartSensor(id(my_uart));
      App.register_component(my_sensor);
      return {my_sensor};
    sensors:
      - name: "Custom Sensor"
```

---

## 1-Wire

Single-wire bus for Dallas temperature sensors.

### Dallas Temperature Sensors
```yaml
one_wire:
  - platform: gpio
    pin: GPIO4

sensor:
  - platform: dallas_temp
    address: 0x1234567890ABCDEF
    name: "Temperature"
```

### Find Sensor Addresses
```yaml
# Enable logging, check logs for addresses
logger:
  level: DEBUG

one_wire:
  - platform: gpio
    pin: GPIO4
```

### Multiple Sensors
```yaml
one_wire:
  - platform: gpio
    pin: GPIO4

sensor:
  - platform: dallas_temp
    address: 0x1234567890ABCDEF
    name: "Sensor 1"
  - platform: dallas_temp
    address: 0xFEDCBA0987654321
    name: "Sensor 2"
```

### Use Index Instead of Address
```yaml
sensor:
  - platform: dallas_temp
    index: 0
    name: "First Sensor"
  - platform: dallas_temp
    index: 1
    name: "Second Sensor"
```

---

## CAN Bus

Controller Area Network for automotive and industrial use.

### ESP32 CAN (Built-in TWAI)
```yaml
canbus:
  - platform: esp32_can
    id: my_can
    tx_pin: GPIO5
    rx_pin: GPIO4
    can_id: 0x100
    bit_rate: 500kbps
```

### MCP2515 (SPI CAN Controller)
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

canbus:
  - platform: mcp2515
    id: my_can
    cs_pin: GPIO5
    can_id: 0x100
    bit_rate: 500kbps
    clock: 8MHZ  # Crystal frequency
```

### CAN Options
| Option | Type | Description |
|--------|------|-------------|
| `can_id` | int | Default CAN ID for sending |
| `bit_rate` | string | 125/250/500/1000kbps |
| `use_extended_id` | bool | Use 29-bit IDs |

### Send CAN Message
```yaml
on_...:
  - canbus.send:
      can_id: 0x123
      data: [0x01, 0x02, 0x03]

  # With lambda
  - canbus.send:
      can_id: 0x123
      data: !lambda |-
        return {0x01, (uint8_t)(value >> 8), (uint8_t)(value & 0xFF)};
```

### Receive CAN Messages
```yaml
canbus:
  - platform: esp32_can
    id: my_can
    tx_pin: GPIO5
    rx_pin: GPIO4
    can_id: 0x100
    bit_rate: 500kbps
    on_frame:
      - lambda: |-
          ESP_LOGD("can", "ID: 0x%03X, Data: %02X %02X %02X",
                   x.can_id, x.data[0], x.data[1], x.data[2]);
```

### CAN Binary Sensor Trigger
```yaml
binary_sensor:
  - platform: template
    name: "CAN Signal"
    id: can_signal

canbus:
  on_frame:
    - if:
        condition:
          lambda: "return x.can_id == 0x200 && x.data[0] == 0x01;"
        then:
          - binary_sensor.template.publish:
              id: can_signal
              state: true
```

### CAN Sensor (Parse Data)
```yaml
sensor:
  - platform: template
    id: can_value
    name: "CAN Value"

canbus:
  on_frame:
    - if:
        condition:
          lambda: "return x.can_id == 0x300;"
        then:
          - sensor.template.publish:
              id: can_value
              state: !lambda |-
                return (x.data[0] << 8) | x.data[1];
```

---

## Modbus

Industrial protocol for PLCs and sensors.

### Modbus Controller (Master)
```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
  parity: EVEN

modbus:
  id: modbus_hub

modbus_controller:
  - id: controller1
    address: 0x01
    modbus_id: modbus_hub
    update_interval: 5s
```

### Read Holding Registers
```yaml
sensor:
  - platform: modbus_controller
    modbus_controller_id: controller1
    name: "Temperature"
    register_type: holding
    address: 0x0000
    value_type: S_WORD  # Signed 16-bit
    unit_of_measurement: "°C"
    accuracy_decimals: 1
    filters:
      - multiply: 0.1
```

### Register Types
| Type | Description |
|------|-------------|
| `holding` | Read/Write registers (function 3/6/16) |
| `read` | Read-only input registers (function 4) |
| `coil` | Read/Write single bit (function 1/5) |
| `discrete_input` | Read-only single bit (function 2) |

### Value Types
| Type | Description |
|------|-------------|
| `U_WORD` | Unsigned 16-bit |
| `S_WORD` | Signed 16-bit |
| `U_DWORD` | Unsigned 32-bit |
| `S_DWORD` | Signed 32-bit |
| `U_DWORD_R` | 32-bit, reversed word order |
| `FP32` | 32-bit float |
| `FP32_R` | 32-bit float, reversed |

### Read Multiple Registers
```yaml
sensor:
  - platform: modbus_controller
    modbus_controller_id: controller1
    name: "Energy Total"
    register_type: holding
    address: 0x0048
    value_type: U_DWORD
    unit_of_measurement: "kWh"
    filters:
      - multiply: 0.01
```

### Write to Register
```yaml
number:
  - platform: modbus_controller
    modbus_controller_id: controller1
    name: "Setpoint"
    register_type: holding
    address: 0x0100
    value_type: U_WORD
    min_value: 0
    max_value: 100

switch:
  - platform: modbus_controller
    modbus_controller_id: controller1
    name: "Relay Output"
    register_type: coil
    address: 0x0000
```

### Custom Modbus Commands
```yaml
on_...:
  - modbus_controller.set_value:
      id: controller1
      address: 0x0100
      value: 50

  # Read manually
  - lambda: |-
      uint16_t result;
      id(controller1).read_holding_register(0x0000, &result, 1);
```

---

## Common Patterns

### I2C Level Shifter
```yaml
# Use for 5V I2C devices with 3.3V ESP32
i2c:
  sda: GPIO21
  scl: GPIO22
  frequency: 100kHz  # Lower frequency for level shifters
```

### UART RS485
```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600

# Control DE/RE pin for half-duplex
output:
  - platform: gpio
    id: rs485_dir
    pin: GPIO5

# Set direction before TX
on_...:
  - output.turn_on: rs485_dir
  - uart.write: [0x01, 0x03, 0x00, 0x00]
  - delay: 10ms
  - output.turn_off: rs485_dir
```

### Multi-Device SPI
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

# Each device needs own CS pin
display:
  - platform: ili9xxx
    cs_pin: GPIO5
    # ...

sensor:
  - platform: max6675
    cs_pin: GPIO15
    # ...
```

### Scan I2C on Button Press
```yaml
button:
  - platform: template
    name: "Scan I2C"
    on_press:
      - lambda: |-
          ESP_LOGI("i2c_scan", "Scanning I2C bus...");
          for (uint8_t addr = 1; addr < 127; addr++) {
            Wire.beginTransmission(addr);
            if (Wire.endTransmission() == 0) {
              ESP_LOGI("i2c_scan", "Found device at 0x%02X", addr);
            }
          }
          ESP_LOGI("i2c_scan", "Scan complete");
```

### UART Bridge (TCP)
```yaml
uart:
  id: my_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 115200

stream_server:
  uart_id: my_uart
  port: 1234
```

### Modbus Energy Meter
```yaml
modbus_controller:
  - id: sdm120
    address: 0x01
    modbus_id: modbus_hub
    update_interval: 5s

sensor:
  - platform: modbus_controller
    modbus_controller_id: sdm120
    name: "Voltage"
    register_type: read
    address: 0x0000
    value_type: FP32
    unit_of_measurement: "V"

  - platform: modbus_controller
    modbus_controller_id: sdm120
    name: "Current"
    register_type: read
    address: 0x0006
    value_type: FP32
    unit_of_measurement: "A"

  - platform: modbus_controller
    modbus_controller_id: sdm120
    name: "Power"
    register_type: read
    address: 0x000C
    value_type: FP32
    unit_of_measurement: "W"
```
