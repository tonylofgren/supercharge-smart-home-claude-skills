# ESPHome Troubleshooting Guide

## Table of Contents
- [Compilation Errors](#compilation-errors)
- [WiFi Issues](#wifi-issues)
- [OTA Update Problems](#ota-update-problems)
- [Sensor Issues](#sensor-issues)
- [API/Home Assistant Connection](#apihome-assistant-connection)
- [Memory Issues](#memory-issues)
- [Boot Loops](#boot-loops)
- [GPIO Issues](#gpio-issues)

---

## Compilation Errors

### "Unknown board" Error

```
Error: Unknown board 'xxx'
```

**Solution:** Check board name in platformio boards list or use generic:

```yaml
# ESP8266
esp8266:
  board: esp01_1m      # 1MB flash
  board: esp8285       # For integrated antenna
  board: nodemcuv2     # NodeMCU
  board: d1_mini       # Wemos D1 Mini

# ESP32
esp32:
  board: esp32dev      # Generic ESP32
  board: nodemcu-32s   # NodeMCU-32S
  board: esp32-s3-devkitc-1  # ESP32-S3
  board: esp32-c3-devkitm-1  # ESP32-C3
```

### "GPIO not available" Error

```
Error: GPIOxx is not available on this board
```

**Solution:** Check pin restrictions for your chip:

| Chip | Restricted Pins |
|------|-----------------|
| ESP8266 | GPIO6-11 (flash), GPIO16 (no PWM) |
| ESP32 | GPIO6-11 (flash), GPIO34-39 (input only) |
| ESP32-S3 | GPIO26-32 (PSRAM on some boards) |

### "Multiple definitions" Error

```
Error: Multiple definitions of 'id_xxx'
```

**Solution:** Ensure unique IDs across all components:

```yaml
sensor:
  - platform: dht
    id: temp_sensor_1    # Must be unique
  - platform: dallas
    id: temp_sensor_2    # Different ID
```

### Framework Conflicts

```
Error: Component xxx requires framework arduino/esp-idf
```

**Solution:** Specify compatible framework:

```yaml
esp32:
  board: esp32dev
  framework:
    type: arduino       # or esp-idf
    version: recommended
```

---

## WiFi Issues

### Device Not Connecting

**Check credentials:**
```yaml
wifi:
  ssid: "MyNetwork"        # Exact name, case-sensitive
  password: "MyPassword"   # Check for typos

  # Enable debug logging
  output_power: 20dB       # Increase if needed
```

**Add fallback AP:**
```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${device_name}-fallback"
    password: "fallback123"

captive_portal:
```

### Frequent Disconnections

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  fast_connect: true       # Faster reconnection
  power_save_mode: none    # Disable power saving

  # Manual IP for faster connection
  manual_ip:
    static_ip: 192.168.1.100
    gateway: 192.168.1.1
    subnet: 255.255.255.0
```

### Hidden Network

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true       # Required for hidden networks
```

### Multi-Network Setup

```yaml
wifi:
  networks:
    - ssid: "PrimaryNetwork"
      password: "password1"
      priority: 2          # Higher = preferred
    - ssid: "BackupNetwork"
      password: "password2"
      priority: 1
  ap:
    ssid: "${device_name}-fallback"
```

### Check WiFi Signal

```yaml
sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s

# Signal strength guidelines:
# > -50 dBm: Excellent
# -50 to -60 dBm: Good
# -60 to -70 dBm: Fair
# < -70 dBm: Poor
```

---

## OTA Update Problems

### "Waiting for result" Timeout

**Causes:**
1. Large firmware size
2. Network issues
3. Flash memory issues

**Solutions:**

```yaml
# Increase timeout
ota:
  platform: esphome
  safe_mode: true

# Reduce firmware size
logger:
  level: WARN              # Less verbose logging

# Use minimal font
font:
  - file: "gfonts://Roboto"
    size: 14
    glyphs: '0123456789.:-'  # Only needed characters
```

### "Bad magic byte" Error

Device not in flash mode or wrong serial settings.

**Solution:** Hold GPIO0 LOW during power-on, or use safe mode:

```yaml
button:
  - platform: safe_mode
    name: "Safe Mode Boot"
```

### OTA Upload Fails Mid-way

```yaml
# Use HTTP OTA for larger updates
ota:
  - platform: esphome
  - platform: http_request
    id: ota_http

# Ensure enough free heap
debug:
sensor:
  - platform: debug
    free:
      name: "Free Heap"
```

### Safe Mode Recovery

Device boots into safe mode after 10 failed boots. Connect to fallback AP and upload working firmware.

---

## Sensor Issues

### NaN (Not a Number) Values

```yaml
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Temperature"
      filters:
        - filter_out: nan     # Ignore invalid readings
```

**Common causes:**
- Wrong pin
- Missing pull-up resistor
- Bad wiring
- Wrong sensor model

### Sensor Always Returns 0

**Check:**
1. Correct GPIO pin
2. Power supply (3.3V vs 5V)
3. Sensor model setting
4. I2C address

```yaml
# Scan I2C bus
i2c:
  scan: true              # Shows found addresses in log
```

### Unstable/Noisy Readings

```yaml
sensor:
  - platform: adc
    filters:
      - sliding_window_moving_average:
          window_size: 10
          send_every: 5
      - delta: 1.0          # Only report changes > 1.0
```

### Wrong Values

```yaml
sensor:
  - platform: adc
    filters:
      - calibrate_linear:
          - 0.0 -> 0.0      # Measured -> Actual
          - 3.3 -> 100.0
```

### Dallas/OneWire Not Found

```yaml
one_wire:
  - platform: gpio
    pin: GPIO4

# Scan for addresses
logger:
  level: DEBUG
# Look for "Found sensors: 0x..." in log
```

---

## API/Home Assistant Connection

### "Unknown" in HA

Device appears but entities show "unknown".

**Solution:** Wait for first update or check update_interval:

```yaml
sensor:
  - platform: dht
    update_interval: 30s    # Reduce if too slow
```

### "Can't connect" Error

```yaml
api:
  encryption:
    key: "YOUR_32_BYTE_KEY"   # Must match HA config
  reboot_timeout: 15min       # Increase if HA restarts often
```

### Entities Not Appearing

```yaml
# Check internal flag
sensor:
  - platform: template
    name: "My Sensor"
    internal: false           # Must be false to appear in HA
```

### API Disconnects Frequently

```yaml
api:
  reboot_timeout: 0s          # Disable reboot on disconnect

# Or increase timeout
api:
  reboot_timeout: 1h
```

### Encryption Key Mismatch

Delete and re-add device in HA after changing encryption key.

---

## Memory Issues

### "Out of memory" Crash

```yaml
# Check memory usage
debug:
sensor:
  - platform: debug
    free:
      name: "Free Heap"
    block:
      name: "Max Block"
```

**Solutions:**

```yaml
# Reduce logging
logger:
  level: WARN

# Use less fonts/images
font:
  - file: "gfonts://Roboto"
    glyphs: '0123456789.:-'   # Minimal glyphs

# Disable unused features
web_server:
  local: true                  # Reduces memory

# For ESP8266: Use ESP-IDF on ESP32
esp32:
  framework:
    type: esp-idf             # More efficient memory
```

### PSRAM Usage (ESP32-S3/WROVER)

```yaml
esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_SPIRAM: y
      CONFIG_SPIRAM_USE_MALLOC: y
```

---

## Boot Loops

### Constant Rebooting

**Check:**
1. Power supply (minimum 500mA for ESP32, 300mA for ESP8266)
2. GPIO0 not grounded
3. No short circuits

```yaml
# Enable safe mode
esphome:
  on_boot:
    priority: 600
    then:
      - logger.log: "Boot successful"

button:
  - platform: safe_mode
    name: "Safe Mode"
```

### Watchdog Reset

```yaml
# Avoid blocking operations
interval:
  - interval: 100ms           # Instead of delay in on_loop
    then:
      - lambda: |-
          // Non-blocking code
```

### Brown-out Detection

```yaml
# ESP32 only - disable if false triggers
esp32:
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_ESP32_BROWNOUT_DET: n
```

---

## GPIO Issues

### Strapping Pin Warnings

```yaml
# ESP32 strapping pins: GPIO0, 2, 5, 12, 15
# These affect boot mode - use with caution

output:
  - platform: gpio
    pin:
      number: GPIO12
      ignore_strapping_warning: true   # Suppress warning
```

### Pin Conflicts

```yaml
# Check for conflicts:
# - I2C uses 2 pins
# - SPI uses 4 pins
# - UART uses 2 pins
# - OneWire uses 1 pin

# Debug pin usage
logger:
  level: DEBUG
```

### Input Not Working

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO5
      mode:
        input: true
        pullup: true          # Enable internal pullup
      inverted: true          # Invert if needed
```

### Output Not Working

```yaml
# Check pin capabilities
# ESP8266 GPIO16: No PWM
# ESP32 GPIO34-39: Input only

output:
  - platform: gpio
    pin: GPIO12
    id: output1

# Test with LED
switch:
  - platform: output
    output: output1
    name: "Test Output"
```

---

## Diagnostic Commands

### Enable Verbose Logging

```yaml
logger:
  level: VERBOSE
  logs:
    component: DEBUG
    wifi: DEBUG
    api: DEBUG
```

### Serial Monitor

```bash
# ESPHome
esphome logs device.yaml

# Or with screen/minicom
screen /dev/ttyUSB0 115200
```

### Web Server Debug

```yaml
web_server:
  port: 80
  local: true
# Access http://device-ip for live status
```

### Debug Component

```yaml
debug:
  update_interval: 5s

sensor:
  - platform: debug
    free:
      name: "Free Heap"
    block:
      name: "Max Block"
    loop_time:
      name: "Loop Time"

text_sensor:
  - platform: debug
    device:
      name: "Device Info"
    reset_reason:
      name: "Reset Reason"
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Component xxx took too long` | Blocking code | Use async patterns |
| `Invalid config` | YAML syntax error | Check indentation |
| `GPIO conflict` | Same pin used twice | Use unique pins |
| `Address already in use` | Port conflict | Change API/web port |
| `Checksum invalid` | Flash corruption | Reflash device |
| `Not enough space` | Firmware too large | Reduce features |
