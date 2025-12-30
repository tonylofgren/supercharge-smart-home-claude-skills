# ESPHome Templates

Ready-to-use ESPHome configuration templates for common use cases.

---

## Base Templates

### base-esp32.yaml
Basic ESP32 starter template with:
- WiFi connectivity
- Home Assistant API
- OTA updates
- Logger
- Restart button

**Use for:** Starting any ESP32 project

### base-esp8266.yaml
Basic ESP8266 starter template with:
- WiFi connectivity
- Home Assistant API
- OTA updates
- Logger
- Restart button

**Use for:** Starting any ESP8266 project

---

## Battery-Powered Devices

### battery-sensor.yaml
Battery-powered sensor with deep sleep optimization:
- DHT22 temperature/humidity sensor
- Battery voltage monitoring
- Deep sleep between readings (configurable interval)
- Wake on external trigger option

**Use for:** Remote sensors, outdoor monitoring, low-power applications

**Power consumption:** <100µA in deep sleep

---

## Bluetooth & Presence

### ble-presence.yaml
Bluetooth Low Energy presence detection:
- BLE tracker for presence detection
- iBeacon support
- Xiaomi Mi Flora plant sensor integration
- RSSI-based distance estimation

**Use for:** Room presence, BLE sensor gateway, plant monitoring

---

## Displays

### display-oled.yaml
SSD1306 OLED display (128x64):
- I2C or SPI configuration
- Time, date, WiFi status
- Sensor readings display
- Custom pages with navigation

**Use for:** Information displays, sensor dashboards

---

## Automation & Control

### garage-door.yaml
Garage door controller with:
- Relay control for door opener
- Reed switch for open/closed status
- Safety timeout
- Cover component for Home Assistant

**Use for:** Garage door automation, gate control

### thermostat.yaml
Smart thermostat with PID control:
- Temperature sensor input
- Heating/cooling relay output
- PID controller for precise temperature
- Home Assistant climate integration

**Use for:** Room heating, underfloor heating, HVAC control

---

## IR & RF

### ir-remote-hub.yaml
Infrared transmitter and receiver:
- IR receiver for capturing codes
- IR transmitter for replay
- Multiple remote support
- Learning mode

**Use for:** Universal remote, AC control, TV automation

---

## Lighting

### led-matrix-clock.yaml
MAX7219 LED matrix clock:
- 4x8x8 LED matrix modules
- NTP time sync
- Multiple display modes
- Brightness control

**Use for:** Desk clocks, status displays

### led-strip-effects.yaml
WS2812B LED strip with effects:
- Addressable RGB LED control
- Built-in effects (rainbow, strobe, etc.)
- Custom color patterns
- Home Assistant light integration

**Use for:** Ambient lighting, decorative LEDs, notification lights

---

## Multi-Sensor Nodes

### sensor-multi.yaml
Multi-sensor combination:
- BME280 (temperature, humidity, pressure)
- BH1750 (light level)
- WiFi signal monitoring
- All I2C sensors

**Use for:** Environmental monitoring, weather stations

---

## Device Conversions

### shelly-1pm.yaml
Shelly 1PM power monitoring relay:
- Power measurement (HLW8012)
- Relay control
- Button input
- Calibrated power/voltage/current

**Use for:** Converting Shelly 1PM to ESPHome

### sonoff-basic.yaml
Sonoff Basic relay switch:
- Relay control
- Button with toggle/hold actions
- LED status indicator
- Safe mode button

**Use for:** Converting Sonoff Basic to ESPHome

---

## Networking

### mqtt-gateway.yaml
MQTT gateway (no Home Assistant):
- MQTT broker connection
- Topic-based control
- JSON payloads
- Standalone operation

**Use for:** Non-Home Assistant setups, custom MQTT integrations

### web-dashboard.yaml
Built-in web server dashboard:
- Web interface on device IP
- Control switches and view sensors
- No Home Assistant required
- Optional authentication

**Use for:** Standalone devices, debugging, quick access

---

## Touch & Input

### touch-panel.yaml
ESP32 capacitive touch panel:
- Multiple touch pads
- Touch binary sensors
- Threshold calibration
- Multi-touch support

**Use for:** Touch buttons, capacitive sensors, custom interfaces

---

## Voice & Audio

### voice-assistant.yaml
ESP32-S3 voice assistant:
- Wake word detection
- Voice commands
- Speaker output
- Home Assistant integration

**Use for:** DIY voice assistants, smart speakers

**Requirements:** ESP32-S3 with PSRAM, microphone, speaker

---

## How to Use Templates

1. **Copy template** to your ESPHome config directory
2. **Rename** to match your device (e.g., `living-room-sensor.yaml`)
3. **Update** device name and friendly name
4. **Modify** GPIO pins to match your hardware
5. **Add secrets** to ESPHome `secrets.yaml`
6. **Flash** to your device

### Example:

```bash
cp base-esp32.yaml my-device.yaml
# Edit my-device.yaml with your pins and settings
esphome run my-device.yaml
```

---

## Customization Tips

### Changing GPIO Pins

All templates use GPIO pins that work on most boards. Update pin numbers to match your wiring:

```yaml
# Before
pin: GPIO4

# After (your hardware)
pin: GPIO21
```

### Adding Components

Combine patterns from multiple templates:

1. Start with base template
2. Add sensor sections from sensor-multi.yaml
3. Add display from display-oled.yaml
4. Merge and test

### Board Compatibility

Most templates work on both ESP32 and ESP8266 with pin adjustments:

- **ESP32-only features:** Bluetooth, touch sensors, DAC, RMT LED strips
- **ESP8266 limitations:** No BLE, fewer PWM channels, some pins are input-only

See [../references/boards.md](../references/boards.md) for pin compatibility.

---

## Contributing

Have a useful template? Create a pull request with:
- Working YAML configuration
- Clear comments
- Description of use case
- Required hardware list
