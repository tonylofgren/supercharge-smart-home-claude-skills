# ESP Board Reference

Complete reference for ESP32 and ESP8266 boards supported by ESPHome.

---

## Table of Contents

- [Board Selection Guide](#board-selection-guide)
- [ESP32 Family](#esp32-family)
  - [ESP32 (Original)](#esp32-original)
  - [ESP32-S2](#esp32-s2)
  - [ESP32-S3](#esp32-s3)
  - [ESP32-C3](#esp32-c3)
  - [ESP32-C6](#esp32-c6)
  - [ESP32-H2](#esp32-h2)
- [ESP8266 Family](#esp8266-family)
  - [ESP-01 / ESP-01S](#esp-01--esp-01s)
  - [ESP-12E/F (NodeMCU)](#esp-12ef-nodemcu)
  - [Wemos D1 Mini](#wemos-d1-mini)
  - [ESP8285](#esp8285)
- [Pin Reference Tables](#pin-reference-tables)
- [Board Comparison Table](#board-comparison-table)
- [Common Development Boards](#common-development-boards)
- [Framework Selection](#framework-selection)

---

## Board Selection Guide

### Quick Decision Tree

**Do you need Bluetooth?**
- BLE only: ESP32, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2
- Bluetooth Classic: ESP32 only
- No Bluetooth needed: Any chip including ESP8266

**Do you need voice assistant capability?**
- Yes: ESP32-S3 (best), ESP32 with PSRAM (limited)

**Do you need Thread/Zigbee/Matter?**
- Yes: ESP32-C6 or ESP32-H2

**Is this a battery-powered device?**
- Yes: ESP32-C3 (lowest power), ESP8266 with deep sleep

**Budget project with simple sensors?**
- Yes: ESP8266 or ESP32-C3

**Converting a commercial device (Shelly/Sonoff)?**
- See [device-guides.md](device-guides.md)

### Feature Requirements Matrix

| Requirement | Recommended Chip |
|-------------|------------------|
| General IoT | ESP32 |
| Voice assistant | ESP32-S3 |
| BLE proxy/tracker | ESP32, ESP32-C3 |
| Thread/Matter device | ESP32-C6 |
| Zigbee coordinator | ESP32-H2 |
| Battery sensor | ESP32-C3 |
| Simple relay/switch | ESP8266 |
| Display with touch | ESP32-S3 |
| Camera project | ESP32-S3 |
| USB device | ESP32-S2, ESP32-S3 |
| Legacy/budget | ESP8266 |

### Quick Board ID Mapping

Use this table to quickly find the correct `board:` ID for ESPHome configs based on what users typically say:

| User Says | Chip | Board ID |
|-----------|------|----------|
| ESP32 / generic | ESP32 | `esp32dev` |
| NodeMCU-32S | ESP32 | `nodemcu-32s` |
| ESP32-S3 | ESP32-S3 | `esp32-s3-devkitc-1` |
| ESP32-C3 | ESP32-C3 | `esp32-c3-devkitm-1` |
| ESP32-C6 | ESP32-C6 | `esp32-c6-devkitc-1` |
| ESP32-H2 | ESP32-H2 | `esp32-h2-devkitm-1` |
| NodeMCU / ESP8266 | ESP8266 | `nodemcuv2` |
| D1 Mini / Wemos | ESP8266 | `d1_mini` |
| ESP-01 | ESP8266 | `esp01_1m` |
| Sonoff Basic/Mini | ESP8285 | `esp8285` |
| Shelly 1/1PM/2.5 | ESP8266 | `esp01_1m` |
| Shelly Plus | ESP32 | `esp32doit-devkit-v1` |

**See detailed board sections below for complete specifications and additional board IDs.**

---

## ESP32 Family

### ESP32 (Original)

The most common and versatile ESP32 variant. Dual-core with WiFi and Bluetooth.

**Specifications:**
- Cores: 2 (Xtensa LX6)
- Clock: 240 MHz
- RAM: 520 KB SRAM
- Flash: 4-16 MB (external)
- WiFi: 802.11 b/g/n
- Bluetooth: Classic + BLE 4.2
- GPIOs: 34 (GPIO0-39)
- ADC: 18 channels (12-bit)
- DAC: 2 channels (8-bit)
- Touch: 10 capacitive touch pins

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| Generic DevKit | `esp32dev` | Most common, use as default |
| NodeMCU-32S | `nodemcu-32s` | NodeMCU form factor |
| LOLIN32 | `lolin32` | Wemos D1 Mini form factor |
| ESP-WROVER-KIT | `esp-wrover-kit` | With PSRAM and display |
| Adafruit HUZZAH32 | `featheresp32` | Feather form factor |
| TTGO T-Display | `ttgo-t1` | Built-in TFT display |
| M5Stack Core | `m5stack-core-esp32` | With display and buttons |

**Pin Categories:**

| Category | Pins | Notes |
|----------|------|-------|
| Input Only | GPIO34, 35, 36, 39 | No pullup, no output |
| Strapping | GPIO0, 2, 5, 12, 15 | Affect boot mode |
| Flash (NEVER USE) | GPIO6-11 | Internal flash |
| Touch Capable | GPIO0, 2, 4, 12-15, 27, 32, 33 | Capacitive touch |
| DAC Output | GPIO25, 26 | Analog output |
| ADC1 (WiFi safe) | GPIO32-39 | Works with WiFi |
| ADC2 (WiFi conflict) | GPIO0, 2, 4, 12-15, 25-27 | Unavailable when WiFi active |

**Safe GPIO Recommendations:**
- Best for outputs: GPIO16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
- Best for inputs: GPIO16, 17, 18, 19, 21, 22, 23, 34, 35, 36, 39
- I2C default: SDA=GPIO21, SCL=GPIO22
- SPI default: MOSI=GPIO23, MISO=GPIO19, CLK=GPIO18, CS=GPIO5

**Example Configuration:**

```yaml
esp32:
  board: esp32dev
  framework:
    type: arduino
```

**Best For:** General IoT, BLE proxy, displays, most projects

---

### ESP32-S2

Single-core with native USB. No Bluetooth support.

**Specifications:**
- Cores: 1 (Xtensa LX7)
- Clock: 240 MHz
- RAM: 320 KB SRAM
- Flash: 4 MB+ (external)
- WiFi: 802.11 b/g/n
- Bluetooth: None
- GPIOs: 43
- ADC: 20 channels
- DAC: 2 channels
- Touch: 14 capacitive touch pins
- USB: Native USB OTG

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-S2-Saola-1 | `esp32-s2-saola-1` | Standard dev board |
| LOLIN S2 Mini | `lolin_s2_mini` | Compact form factor |
| Adafruit Feather S2 | `adafruit_feather_esp32s2` | Feather form factor |
| Unexpected Maker TinyS2 | `um_tinys2` | Ultra compact |

**Example Configuration:**

```yaml
esp32:
  board: esp32-s2-saola-1
  framework:
    type: arduino
```

**Best For:** USB devices, projects not needing Bluetooth

---

### ESP32-S3

Dual-core with AI acceleration. Best for voice assistants and cameras.

**Specifications:**
- Cores: 2 (Xtensa LX7)
- Clock: 240 MHz
- RAM: 512 KB SRAM + optional 8MB PSRAM
- Flash: 8-16 MB
- WiFi: 802.11 b/g/n
- Bluetooth: BLE 5.0
- GPIOs: 45
- ADC: 20 channels
- Touch: 14 capacitive touch pins
- USB: Native USB OTG
- Special: Vector instructions for AI/ML

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-S3-DevKitC-1 | `esp32-s3-devkitc-1` | Standard dev board |
| Seeed XIAO ESP32S3 | `seeed_xiao_esp32s3` | Tiny form factor |
| ESP32-S3-BOX | `esp32s3box` | Voice assistant dev kit |
| Adafruit Feather S3 | `adafruit_feather_esp32s3` | Feather form factor |
| M5Stack AtomS3 | `m5stack-atoms3` | Ultra compact |
| LILYGO T-Display S3 | `lilygo-t-display-s3` | Built-in display |

**Example Configuration:**

```yaml
esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf  # Recommended for S3
```

**Voice Assistant Configuration:**

```yaml
esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_ESP32S3_DEFAULT_CPU_FREQ_240: "y"
      CONFIG_ESP32S3_SPIRAM_SUPPORT: "y"

psram:
  mode: octal
  speed: 80MHz
```

**Best For:** Voice assistants, cameras, AI edge, displays with touch

---

### ESP32-C3

RISC-V single-core. Low power and compact.

**Specifications:**
- Cores: 1 (RISC-V)
- Clock: 160 MHz
- RAM: 400 KB SRAM
- Flash: 4 MB
- WiFi: 802.11 b/g/n
- Bluetooth: BLE 5.0
- GPIOs: 22
- ADC: 6 channels

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-C3-DevKitM-1 | `esp32-c3-devkitm-1` | Standard dev board |
| Seeed XIAO ESP32C3 | `seeed_xiao_esp32c3` | Tiny form factor |
| ESP32-C3-MINI-1 | `esp32-c3-devkitc-02` | Module-based |
| LOLIN C3 Mini | `lolin_c3_mini` | D1 Mini form factor |
| Adafruit QT Py C3 | `adafruit_qtpy_esp32c3` | STEMMA QT connector |

**Pin Notes:**
- GPIO0-10: General purpose (some have boot functions)
- GPIO11-17: Not available on most modules (internal flash)
- GPIO18-21: Safe to use

**Example Configuration:**

```yaml
esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: arduino
```

**Best For:** Battery devices, simple sensors, BLE beacons, compact projects

---

### ESP32-C6

WiFi 6 with Thread/Zigbee support. Matter-ready.

**Specifications:**
- Cores: 1 (RISC-V) + 1 low-power core
- Clock: 160 MHz
- RAM: 512 KB SRAM
- Flash: 4 MB
- WiFi: 802.11ax (WiFi 6)
- Bluetooth: BLE 5.0
- 802.15.4: Thread, Zigbee
- GPIOs: 30
- ADC: 7 channels

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-C6-DevKitC-1 | `esp32-c6-devkitc-1` | Standard dev board |
| Seeed XIAO ESP32C6 | `seeed_xiao_esp32c6` | Tiny form factor |

**Example Configuration:**

```yaml
esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf
```

**Best For:** Matter devices, Thread border router, WiFi 6 projects

---

### ESP32-H2

Thread/Zigbee only. No WiFi.

**Specifications:**
- Cores: 1 (RISC-V)
- Clock: 96 MHz
- RAM: 320 KB SRAM
- Flash: 4 MB
- WiFi: None
- Bluetooth: BLE 5.0
- 802.15.4: Thread, Zigbee
- GPIOs: 25

**Common Board IDs:**

| Board | ID | Notes |
|-------|-----|-------|
| ESP32-H2-DevKitM-1 | `esp32-h2-devkitm-1` | Standard dev board |

**Example Configuration:**

```yaml
esp32:
  board: esp32-h2-devkitm-1
  framework:
    type: esp-idf
```

**Best For:** Thread endpoints, Zigbee devices, low-power sensors

---

## ESP8266 Family

### ESP-01 / ESP-01S

Minimal module with limited GPIOs.

**Specifications:**
- Clock: 80 MHz
- RAM: 80 KB
- Flash: 512 KB (ESP-01) or 1 MB (ESP-01S)
- WiFi: 802.11 b/g/n
- GPIOs: 4 usable (GPIO0, 1, 2, 3)
- ADC: None accessible

**Board IDs:**
- `esp01` - 512KB flash
- `esp01_1m` - 1MB flash (most common now)

**Available Pins:**
- GPIO0: Boot mode (use with caution)
- GPIO1: TX (Serial)
- GPIO2: Must be HIGH at boot
- GPIO3: RX (Serial)

**Example Configuration:**

```yaml
esp8266:
  board: esp01_1m
  restore_from_flash: true
```

**Best For:** Simple relay modules, single-sensor projects

---

### ESP-12E/F (NodeMCU)

Most common ESP8266 module. Full GPIO access.

**Specifications:**
- Clock: 80/160 MHz
- RAM: 80 KB
- Flash: 4 MB
- WiFi: 802.11 b/g/n
- GPIOs: 11 usable
- ADC: 1 channel (A0, 0-1V)

**Board IDs:**
- `nodemcuv2` - NodeMCU v2 (CH340 USB)
- `esp12e` - Generic ESP-12E module

**Pin Categories:**

| Category | Pins | Notes |
|----------|------|-------|
| Safe for general use | GPIO4, 5, 12, 13, 14 | Best choices |
| Boot sensitive | GPIO0, 2, 15 | Strapping pins |
| Serial | GPIO1 (TX), GPIO3 (RX) | Avoid if using serial |
| Flash (NEVER USE) | GPIO6-11 | Internal flash |
| No PWM | GPIO16 | Wake from deep sleep only |
| ADC | A0 | 0-1V input range |

**D-pin to GPIO mapping (NodeMCU):**

| D-Pin | GPIO | Notes |
|-------|------|-------|
| D0 | GPIO16 | No PWM, wake pin |
| D1 | GPIO5 | Safe, I2C SCL |
| D2 | GPIO4 | Safe, I2C SDA |
| D3 | GPIO0 | Boot pin, has pullup |
| D4 | GPIO2 | Boot pin, has pullup, LED |
| D5 | GPIO14 | Safe, SPI CLK |
| D6 | GPIO12 | Safe, SPI MISO |
| D7 | GPIO13 | Safe, SPI MOSI |
| D8 | GPIO15 | Boot pin, has pulldown |
| RX | GPIO3 | Serial RX |
| TX | GPIO1 | Serial TX |

**Example Configuration:**

```yaml
esp8266:
  board: nodemcuv2
```

**Best For:** DIY projects, learning, prototyping

---

### Wemos D1 Mini

Compact ESP8266 board with shield ecosystem.

**Specifications:**
- Same as ESP-12E/F
- Compact form factor
- 4MB flash
- CH340 USB chip

**Board IDs:**
- `d1_mini` - Standard D1 Mini
- `d1_mini_pro` - With external antenna connector
- `d1_mini_lite` - 1MB flash variant

**Example Configuration:**

```yaml
esp8266:
  board: d1_mini
```

**Best For:** Compact projects, shield-based designs

---

### ESP8285

ESP8266 with built-in 1MB flash. Used in commercial devices.

**Specifications:**
- Same as ESP8266
- 1MB internal flash
- No external flash chip

**Board IDs:**
- `esp8285` - Generic ESP8285

**Common Devices Using ESP8285:**
- Sonoff Basic, Mini, RF
- Many Tuya devices
- Some Shelly devices

**Example Configuration:**

```yaml
esp8266:
  board: esp8285
```

**Best For:** Flashing commercial devices (Sonoff, Tuya)

---

## Pin Reference Tables

### ESP32 Complete Pin Reference

| GPIO | Input | Output | ADC | Touch | Notes |
|------|-------|--------|-----|-------|-------|
| 0 | Yes | Yes | ADC2 | Yes | Strapping, boot button |
| 1 | Yes | Yes | - | - | TX0 (Serial) |
| 2 | Yes | Yes | ADC2 | Yes | Strapping, onboard LED |
| 3 | Yes | Yes | - | - | RX0 (Serial) |
| 4 | Yes | Yes | ADC2 | Yes | Safe |
| 5 | Yes | Yes | - | - | Strapping, VSPI CS |
| 6-11 | - | - | - | - | FLASH - Never use |
| 12 | Yes | Yes | ADC2 | Yes | Strapping (MTDI) |
| 13 | Yes | Yes | ADC2 | Yes | Safe |
| 14 | Yes | Yes | ADC2 | Yes | Safe |
| 15 | Yes | Yes | ADC2 | Yes | Strapping (MTDO) |
| 16 | Yes | Yes | - | - | Safe |
| 17 | Yes | Yes | - | - | Safe |
| 18 | Yes | Yes | - | - | VSPI CLK |
| 19 | Yes | Yes | - | - | VSPI MISO |
| 21 | Yes | Yes | - | - | I2C SDA |
| 22 | Yes | Yes | - | - | I2C SCL |
| 23 | Yes | Yes | - | - | VSPI MOSI |
| 25 | Yes | Yes | ADC2 | - | DAC1 |
| 26 | Yes | Yes | ADC2 | - | DAC2 |
| 27 | Yes | Yes | ADC2 | Yes | Safe |
| 32 | Yes | Yes | ADC1 | Yes | Safe |
| 33 | Yes | Yes | ADC1 | Yes | Safe |
| 34 | Input only | No | ADC1 | - | Input only |
| 35 | Input only | No | ADC1 | - | Input only |
| 36 | Input only | No | ADC1 | - | VP, input only |
| 39 | Input only | No | ADC1 | - | VN, input only |

### ESP8266 Complete Pin Reference

| GPIO | Input | Output | PWM | Notes |
|------|-------|--------|-----|-------|
| 0 | Yes | Yes | Yes | Boot, has internal pullup |
| 1 | Yes | Yes | Yes | TX, avoid if using serial |
| 2 | Yes | Yes | Yes | Boot, has internal pullup |
| 3 | Yes | Yes | Yes | RX, avoid if using serial |
| 4 | Yes | Yes | Yes | Safe, I2C SDA |
| 5 | Yes | Yes | Yes | Safe, I2C SCL |
| 6-11 | - | - | - | FLASH - Never use |
| 12 | Yes | Yes | Yes | Safe, SPI MISO |
| 13 | Yes | Yes | Yes | Safe, SPI MOSI |
| 14 | Yes | Yes | Yes | Safe, SPI CLK |
| 15 | Yes | Yes | Yes | Boot, has internal pulldown |
| 16 | Yes | Yes | No | Wake from deep sleep, no PWM |
| A0 | ADC | No | No | 0-1V input range |

---

## Board Comparison Table

| Chip | Cores | MHz | RAM | Flash | WiFi | BLE | USB | Thread | Price |
|------|-------|-----|-----|-------|------|-----|-----|--------|-------|
| ESP32 | 2 | 240 | 520KB | 4MB+ | Yes | 4.2 | No | No | $$ |
| ESP32-S2 | 1 | 240 | 320KB | 4MB+ | Yes | No | OTG | No | $ |
| ESP32-S3 | 2 | 240 | 512KB | 8MB+ | Yes | 5.0 | OTG | No | $$$ |
| ESP32-C3 | 1 | 160 | 400KB | 4MB | Yes | 5.0 | CDC | No | $ |
| ESP32-C6 | 1 | 160 | 512KB | 4MB | WiFi 6 | 5.0 | CDC | Yes | $$ |
| ESP32-H2 | 1 | 96 | 320KB | 4MB | No | 5.0 | CDC | Yes | $ |
| ESP8266 | 1 | 80 | 80KB | 1-4MB | Yes | No | No | No | $ |

### Use Case Recommendations

| Use Case | Best Choice | Alternative |
|----------|-------------|-------------|
| General IoT | ESP32 | ESP32-C3 |
| Voice Assistant | ESP32-S3 | - |
| BLE Proxy | ESP32 | ESP32-C3 |
| Battery Sensor | ESP32-C3 | ESP8266 |
| Display Project | ESP32-S3 | ESP32 |
| Camera | ESP32-S3 | ESP32-CAM |
| Thread/Matter | ESP32-C6 | ESP32-H2 |
| Zigbee Device | ESP32-H2 | ESP32-C6 |
| Budget/Simple | ESP8266 | ESP32-C3 |
| Commercial Device | ESP8285 | - |

---

## Common Development Boards

### ESP32 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32 DevKit V1 | `esp32dev` | Standard, most common |
| NodeMCU-32S | `nodemcu-32s` | NodeMCU form factor |
| LOLIN D32 | `lolin_d32` | Battery connector |
| LOLIN D32 Pro | `lolin_d32_pro` | SD card, battery |
| ESP-WROVER-KIT | `esp-wrover-kit` | PSRAM, display |
| TTGO T-Display | `ttgo-t1` | Built-in 1.14" TFT |
| M5Stack Core | `m5stack-core-esp32` | Display, buttons, speaker |
| M5Stack Atom | `m5stack-atom` | Ultra compact |
| Adafruit HUZZAH32 | `featheresp32` | Feather form factor |
| SparkFun Thing | `esp32thing` | Battery charging |

### ESP32-S3 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32-S3-DevKitC-1 | `esp32-s3-devkitc-1` | Standard |
| Seeed XIAO S3 | `seeed_xiao_esp32s3` | Tiny, camera |
| ESP32-S3-BOX | `esp32s3box` | Voice assistant kit |
| LILYGO T-Display S3 | `lilygo-t-display-s3` | Built-in display |
| M5Stack AtomS3 | `m5stack-atoms3` | Tiny with display |
| Adafruit Feather S3 | `adafruit_feather_esp32s3` | Feather form |

### ESP32-C3 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32-C3-DevKitM-1 | `esp32-c3-devkitm-1` | Standard |
| Seeed XIAO C3 | `seeed_xiao_esp32c3` | Tiny |
| LOLIN C3 Mini | `lolin_c3_mini` | D1 Mini form |
| Adafruit QT Py C3 | `adafruit_qtpy_esp32c3` | STEMMA QT |
| ESP32-C3-MINI-1 | `esp32-c3-devkitc-02` | Module-based |

### ESP32-C6/H2 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| ESP32-C6-DevKitC-1 | `esp32-c6-devkitc-1` | WiFi 6, Thread |
| Seeed XIAO C6 | `seeed_xiao_esp32c6` | Tiny |
| ESP32-H2-DevKitM-1 | `esp32-h2-devkitm-1` | Thread/Zigbee only |

### ESP8266 Development Boards

| Board Name | Board ID | Features |
|------------|----------|----------|
| NodeMCU v2 | `nodemcuv2` | Most common |
| NodeMCU v3 | `nodemcuv2` | Same as v2 |
| Wemos D1 Mini | `d1_mini` | Compact |
| D1 Mini Pro | `d1_mini_pro` | External antenna |
| ESP-01S | `esp01_1m` | Minimal, 1MB |
| ESP-12E Module | `esp12e` | Just module |

---

## Framework Selection

ESPHome supports two frameworks for ESP32:

### Arduino Framework (Default)

```yaml
esp32:
  board: esp32dev
  framework:
    type: arduino
```

**Pros:**
- Faster compile times
- More community examples
- Simpler

**Best for:** Most projects, beginners

### ESP-IDF Framework

```yaml
esp32:
  board: esp32dev
  framework:
    type: esp-idf
```

**Pros:**
- Full feature access
- Better for voice assistant
- Required for some S3/C6/H2 features

**Best for:** Voice assistants, advanced projects, ESP32-S3/C6/H2

### ESP8266 Framework

ESP8266 only supports Arduino framework:

```yaml
esp8266:
  board: nodemcuv2
```

---

## Related Documentation

- [device-guides.md](device-guides.md) - Converting commercial devices
- [troubleshooting.md](troubleshooting.md) - Common hardware issues
- [power-management.md](power-management.md) - Deep sleep and battery
