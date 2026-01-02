# ESP Board Pinout Reference

Quick reference for common ESP board pinouts with ASCII diagrams.

## ESP32 DevKit V1 (30-pin)

```
                    ┌──────────────┐
                    │    USB-C     │
                    └──────────────┘
            EN   [ ]              [ ] GPIO23  (MOSI)
            GPIO36 (VP/ADC0) [ ]  [ ] GPIO22  (SCL)
            GPIO39 (VN/ADC3) [ ]  [ ] GPIO1   (TX)
            GPIO34 (ADC6)  [ ]    [ ] GPIO3   (RX)
            GPIO35 (ADC7)  [ ]    [ ] GPIO21  (SDA)
            GPIO32 (ADC4)  [ ]    [ ] GND
            GPIO33 (ADC5)  [ ]    [ ] GPIO19  (MISO)
            GPIO25 (DAC1)  [ ]    [ ] GPIO18  (SCK)
            GPIO26 (DAC2)  [ ]    [ ] GPIO5   ⚠️ Strapping
            GPIO27        [ ]     [ ] GPIO17  (TX2)
            GPIO14        [ ]     [ ] GPIO16  (RX2)
            GPIO12 ⚠️     [ ]     [ ] GPIO4
            GND          [ ]      [ ] GPIO0   ⚠️ Boot
            GPIO13       [ ]      [ ] GPIO2   ⚠️ Boot LED
            GPIO9  (⚡ Flash) [ ]  [ ] GPIO15  ⚠️ Strapping
            GPIO10 (⚡ Flash) [ ]  [ ] GPIO8   (⚡ Flash)
            GPIO11 (⚡ Flash) [ ]  [ ] GPIO7   (⚡ Flash)
            VIN (5V)     [ ]      [ ] GPIO6   (⚡ Flash)
            GND          [ ]      [ ] 3V3
                    ┌──────────────┐
                    │   ▪▪▪▪▪▪▪▪   │
                    └──────────────┘
```

**Legend:**
- ⚠️ Strapping pin (use with caution)
- ⚡ Flash pins (DO NOT USE)
- ADCx = Analog input capable
- DACx = Analog output capable

---

## ESP32-S3 DevKit (44-pin)

```
                    ┌──────────────┐
                    │    USB-C     │
                    └──────────────┘
            3V3    [ ]              [ ] GND
            3V3    [ ]              [ ] GPIO43 (TX)
            RST    [ ]              [ ] GPIO44 (RX)
            GPIO4  [ ]              [ ] GPIO1
            GPIO5  [ ]              [ ] GPIO2
            GPIO6  [ ]              [ ] GPIO42
            GPIO7  [ ]              [ ] GPIO41
            GPIO15 [ ]              [ ] GPIO40
            GPIO16 [ ]              [ ] GPIO39
            GPIO17 [ ]              [ ] GPIO38  (RGB LED)
            GPIO18 [ ]              [ ] GPIO37
            GPIO8  (SDA) [ ]        [ ] GPIO36
            GPIO9  (SCL) [ ]        [ ] GPIO35
            GPIO10 [ ]              [ ] GPIO0   ⚠️ Boot
            GPIO11 [ ]              [ ] GPIO45  ⚠️ Strapping
            GPIO12 [ ]              [ ] GPIO46  ⚠️ Strapping
            GPIO13 [ ]              [ ] GPIO47
            GPIO14 [ ]              [ ] GPIO48
            5V     [ ]              [ ] GND
                    └──────────────┘
```

**S3 Special Features:**
- USB OTG on GPIO19/20
- Camera interface support
- Vector extensions for ML

---

## ESP32-C3 Mini (13-pin per side)

```
                    ┌────────┐
                    │ USB-C  │
                    └────────┘
            GPIO0  ⚠️ [ ]     [ ] GPIO10
            GPIO1     [ ]     [ ] GPIO9  (Boot)  ⚠️
            GPIO2     [ ]     [ ] GPIO8  (Strapping) ⚠️
            GPIO3     [ ]     [ ] GPIO7
            GPIO4  (SDA) [ ]  [ ] GPIO6  (SCL)
            GPIO5     [ ]     [ ] GPIO5
            5V        [ ]     [ ] 3V3
            GND       [ ]     [ ] GND
                    └────────┘
```

**C3 Features:**
- WiFi + BLE 5.0
- RISC-V core
- USB CDC (no separate UART chip)

---

## D1 Mini (ESP8266)

```
                    ┌────────┐
                    │ USB    │
                    └────────┘
            RST    [ ]        [ ] TX  (GPIO1)
            A0     [ ]        [ ] RX  (GPIO3)
            D0     [ ] GPIO16 [ ] D1  (GPIO5/SCL)
            D5     [ ] GPIO14 [ ] D2  (GPIO4/SDA)
            D6     [ ] GPIO12 [ ] D3  (GPIO0)  ⚠️ Boot
            D7     [ ] GPIO13 [ ] D4  (GPIO2)  ⚠️ Boot/LED
            D8     [ ] GPIO15 [ ] GND          ⚠️ Boot
            3V3    [ ]        [ ] 5V
                    └────────┘
```

**D1 Mini Pin Mapping:**
| Label | GPIO | Function |
|-------|------|----------|
| D0 | 16 | Wake from deep sleep |
| D1 | 5 | SCL (I2C) |
| D2 | 4 | SDA (I2C) |
| D3 | 0 | Boot mode ⚠️ |
| D4 | 2 | Boot/LED ⚠️ |
| D5 | 14 | SCK (SPI) |
| D6 | 12 | MISO (SPI) |
| D7 | 13 | MOSI (SPI) |
| D8 | 15 | Boot (must be LOW) ⚠️ |
| A0 | ADC | Analog input (0-1V) |

---

## Strapping Pins Reference

### ESP32

| GPIO | Function | Boot Requirement |
|------|----------|------------------|
| 0 | Boot mode | HIGH = normal boot, LOW = download mode |
| 2 | Boot mode | Must be LOW or floating at boot |
| 5 | SDIO timing | Affects SDIO slave timing |
| 12 | MTDI | HIGH = 1.8V flash, LOW = 3.3V flash |
| 15 | MTDO | HIGH = debug output enabled |

**Safe to use after boot:** GPIO0, 2, 5, 15 (with pull-up/down)
**Avoid:** GPIO12 (can cause boot failure if wrong state)

### ESP32-S3

| GPIO | Function |
|------|----------|
| 0 | Boot mode |
| 45 | VDD_SPI voltage |
| 46 | Boot mode / ROM log |

### ESP32-C3

| GPIO | Function |
|------|----------|
| 2 | Strapping |
| 8 | Strapping (ROM log) |
| 9 | Boot mode |

### ESP8266

| GPIO | Boot Requirement |
|------|------------------|
| 0 | HIGH = normal, LOW = flash mode |
| 2 | Must be HIGH at boot |
| 15 | Must be LOW at boot |

---

## ADC Capable Pins

### ESP32
- ADC1: GPIO32-39 (can use with WiFi)
- ADC2: GPIO0, 2, 4, 12-15, 25-27 (NOT usable with WiFi!)

### ESP32-S3
- ADC1: GPIO1-10
- ADC2: GPIO11-20

### ESP32-C3
- ADC1: GPIO0-4
- ADC2: GPIO5 (limited when WiFi active)

### ESP8266
- A0 only (0-1V range, use voltage divider for 3.3V)

---

## PWM / LEDC Capable Pins

### ESP32
All GPIOs except input-only (34-39) support PWM via LEDC.

### ESP32-S3
All GPIOs support PWM.

### ESP32-C3
All GPIOs support PWM.

### ESP8266
All GPIOs except GPIO16 support PWM (software PWM).

---

## Touch Capable Pins (ESP32 only)

| Touch Pad | GPIO |
|-----------|------|
| T0 | GPIO4 |
| T1 | GPIO0 |
| T2 | GPIO2 |
| T3 | GPIO15 |
| T4 | GPIO13 |
| T5 | GPIO12 |
| T6 | GPIO14 |
| T7 | GPIO27 |
| T8 | GPIO33 |
| T9 | GPIO32 |

---

## Quick Reference Table

| Feature | ESP32 | ESP32-S3 | ESP32-C3 | ESP8266 |
|---------|-------|----------|----------|---------|
| GPIO Count | 34 | 45 | 22 | 17 |
| ADC Channels | 18 | 20 | 6 | 1 |
| DAC | 2 | 0 | 0 | 0 |
| Touch | 10 | 14 | 0 | 0 |
| I2C | 2 | 2 | 1 | 1 (SW) |
| SPI | 4 | 4 | 3 | 2 |
| UART | 3 | 3 | 2 | 2 |
| PWM | 16 ch | 8 ch | 6 ch | SW |
| Flash Pins | 6-11 | Internal | Internal | 6-11 |
