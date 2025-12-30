# ESPHome Popular Devices Reference

Configurations for popular community devices and DIY projects.

## Table of Contents
- [Air Quality Monitors](#air-quality-monitors)
- [Smart Lighting](#smart-lighting)
- [Smart Plugs](#smart-plugs)
- [Display Projects](#display-projects)
- [Sensor Modifications](#sensor-modifications)
- [Voice Assistants](#voice-assistants)

---

## Air Quality Monitors

### AirGradient DIY

Popular open-source air quality monitor with PM2.5 and CO2.

```yaml
# AirGradient ONE or DIY Pro
substitutions:
  device_name: "airgradient"
  friendly_name: "AirGradient"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: d1_mini

# I2C for SHT sensor
i2c:
  sda: GPIO4
  scl: GPIO5

# UART for PM sensor (PMS5003)
uart:
  - id: uart_pm
    rx_pin: GPIO2
    baud_rate: 9600

  # UART for CO2 sensor (Senseair S8)
  - id: uart_co2
    rx_pin: GPIO14
    tx_pin: GPIO12
    baud_rate: 9600

sensor:
  # PM2.5 sensor
  - platform: pmsx003
    type: PMSX003
    uart_id: uart_pm
    pm_2_5:
      name: "PM2.5"
      filters:
        - sliding_window_moving_average:
            window_size: 10
            send_every: 10

  # CO2 sensor
  - platform: senseair
    uart_id: uart_co2
    co2:
      name: "CO2"
      filters:
        - sliding_window_moving_average:
            window_size: 5
            send_every: 5

  # Temperature and humidity
  - platform: sht3xd
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 60s
```

### AirGradient with Display

```yaml
# Add SSD1306 OLED display
i2c:
  sda: GPIO4
  scl: GPIO5

font:
  - file: "gfonts://Roboto"
    id: font_small
    size: 10
  - file: "gfonts://Roboto"
    id: font_large
    size: 24

display:
  - platform: ssd1306_i2c
    model: "SH1106 128x64"
    address: 0x3C
    lambda: |-
      it.printf(0, 0, id(font_small), "CO2: %.0f ppm", id(co2_sensor).state);
      it.printf(0, 12, id(font_small), "PM2.5: %.0f ug/m3", id(pm25_sensor).state);
      it.printf(0, 24, id(font_small), "%.1f°C  %.0f%%",
                id(temp_sensor).state, id(humidity_sensor).state);
```

---

## Smart Lighting

### Yeelight Ceiling Light

Control MBBC4 / MXCZ02YL ceiling lights via UART.

```yaml
# Yeelight Ceiling Light ESP replacement
substitutions:
  device_name: "yeelight-ceiling"
  friendly_name: "Ceiling Light"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev

# Control via PWM outputs
output:
  - platform: ledc
    pin: GPIO19
    id: output_warm
    frequency: 1000Hz

  - platform: ledc
    pin: GPIO21
    id: output_cold
    frequency: 1000Hz

  - platform: ledc
    pin: GPIO23
    id: output_nightlight
    frequency: 1000Hz

light:
  - platform: cwww
    name: "Ceiling Light"
    cold_white: output_cold
    warm_white: output_warm
    cold_white_color_temperature: 6500K
    warm_white_color_temperature: 2700K
    constant_brightness: true

  - platform: monochromatic
    name: "Night Light"
    output: output_nightlight
```

### Xiaomi Bedside Lamp v2

```yaml
# Xiaomi Bedside Lamp 2 (MJCTD02YL)
esphome:
  name: bedside-lamp
  friendly_name: "Bedside Lamp"

esp32:
  board: esp32dev

# RGB + White LED outputs
output:
  - platform: ledc
    pin: GPIO19
    id: output_red
  - platform: ledc
    pin: GPIO21
    id: output_green
  - platform: ledc
    pin: GPIO22
    id: output_blue
  - platform: ledc
    pin: GPIO23
    id: output_white

light:
  - platform: rgbw
    name: "Bedside Lamp"
    red: output_red
    green: output_green
    blue: output_blue
    white: output_white
    effects:
      - random:
      - strobe:

# Touch button
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO12
      mode: INPUT_PULLUP
    name: "Touch Button"
    on_click:
      - light.toggle: bedside_lamp
    on_double_click:
      - light.turn_on:
          id: bedside_lamp
          brightness: 100%
          white: 100%

# Rotary encoder for brightness
sensor:
  - platform: rotary_encoder
    pin_a: GPIO26
    pin_b: GPIO27
    name: "Brightness Control"
    on_clockwise:
      - light.dim_relative:
          id: bedside_lamp
          relative_brightness: 5%
    on_anticlockwise:
      - light.dim_relative:
          id: bedside_lamp
          relative_brightness: -5%
```

### WS2812 LED Strip Controller

```yaml
# Universal LED strip controller
substitutions:
  num_leds: "60"

esphome:
  name: led-strip
  friendly_name: "LED Strip"

esp32:
  board: esp32dev

light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: ${num_leds}
    rmt_channel: 0
    chipset: WS2812
    rgb_order: GRB
    name: "LED Strip"
    effects:
      - addressable_rainbow:
          name: "Rainbow"
          speed: 10
          width: 50
      - addressable_color_wipe:
          name: "Color Wipe"
          colors:
            - red: 100%
              green: 0%
              blue: 0%
              num_leds: 1
            - red: 0%
              green: 0%
              blue: 0%
              num_leds: 1
      - addressable_scan:
          name: "Knight Rider"
          move_interval: 50ms
          scan_width: 5
      - addressable_twinkle:
          name: "Twinkle"
          twinkle_probability: 5%
      - addressable_fireworks:
          name: "Fireworks"
```

---

## Smart Plugs

### Athom Smart Plug

Pre-flashed ESPHome plugs with power monitoring.

```yaml
# Athom Plug V2 (BL0937 power monitoring)
substitutions:
  device_name: "athom-plug"
  friendly_name: "Smart Plug"

  # Calibration values (adjust per device)
  current_res: "0.001"
  voltage_div: "770"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp8285
  restore_from_flash: true

# Status LED
status_led:
  pin:
    number: GPIO13
    inverted: true

# Relay
switch:
  - platform: gpio
    pin: GPIO14
    name: "Switch"
    id: relay
    restore_mode: RESTORE_DEFAULT_OFF
    on_turn_on:
      - light.turn_on: led
    on_turn_off:
      - light.turn_off: led

# LED indicator
output:
  - platform: gpio
    pin: GPIO16
    inverted: true
    id: led_output

light:
  - platform: binary
    output: led_output
    id: led
    internal: true

# Physical button
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

# Power monitoring (BL0937)
sensor:
  - platform: hlw8012
    model: BL0937
    sel_pin:
      number: GPIO12
      inverted: true
    cf_pin: GPIO04
    cf1_pin: GPIO05
    current_resistor: ${current_res}
    voltage_divider: ${voltage_div}
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"
    update_interval: 10s
```

### Gosund/Tuya Smart Plug

```yaml
# Gosund SP111 / Tuya variant
substitutions:
  device_name: "gosund-plug"
  friendly_name: "Gosund Plug"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: esp8285

switch:
  - platform: gpio
    pin: GPIO14
    name: "Switch"
    id: relay
    restore_mode: RESTORE_DEFAULT_OFF

# LED (active low)
output:
  - platform: gpio
    pin:
      number: GPIO1
      inverted: true
    id: led_red
  - platform: gpio
    pin:
      number: GPIO13
      inverted: true
    id: led_blue

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO3
      inverted: true
    name: "Button"
    on_press:
      - switch.toggle: relay

# Power monitoring (CSE7766)
uart:
  rx_pin: GPIO12
  baud_rate: 4800

sensor:
  - platform: cse7766
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"
    update_interval: 10s
```

---

## Display Projects

### E-ink Weather Display

Inspired by Weatherman Dashboard project.

```yaml
# E-ink Weather Dashboard
substitutions:
  device_name: "weather-display"
  friendly_name: "Weather Display"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev

# SPI for e-paper
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23

# Fonts
font:
  - file: "gfonts://Roboto"
    id: font_small
    size: 14
  - file: "gfonts://Roboto"
    id: font_medium
    size: 24
  - file: "gfonts://Roboto"
    id: font_large
    size: 48
  - file: "gfonts://Material+Symbols+Outlined"
    id: icon_font
    size: 48
    glyphs: ["\U0000e81a", "\U0000e2bd", "\U0000f070"]  # thermostat, water_drop, cloudy

# Weather data from Home Assistant
sensor:
  - platform: homeassistant
    entity_id: sensor.outside_temperature
    id: outside_temp
    internal: true

  - platform: homeassistant
    entity_id: sensor.outside_humidity
    id: outside_humidity
    internal: true

text_sensor:
  - platform: homeassistant
    entity_id: weather.home
    id: weather_condition
    internal: true

# E-paper display (Waveshare 4.2")
display:
  - platform: waveshare_epaper
    cs_pin: GPIO5
    dc_pin: GPIO17
    busy_pin: GPIO4
    reset_pin: GPIO16
    model: 4.20in
    update_interval: 300s  # Update every 5 minutes
    full_update_every: 12  # Full refresh every hour
    lambda: |-
      // Current temperature large
      it.printf(20, 20, id(font_large), "%.0f°C", id(outside_temp).state);

      // Humidity
      it.printf(20, 80, id(font_medium), "%.0f%%", id(outside_humidity).state);

      // Weather icon
      auto weather = id(weather_condition).state;
      if (weather == "sunny" || weather == "clear-night") {
        it.printf(250, 20, id(icon_font), "\U0000e81a");
      } else if (weather == "rainy") {
        it.printf(250, 20, id(icon_font), "\U0000e2bd");
      } else {
        it.printf(250, 20, id(icon_font), "\U0000f070");
      }

      // Last update time
      it.strftime(20, 110, id(font_small), "Updated: %H:%M", id(ha_time).now());

time:
  - platform: homeassistant
    id: ha_time
```

### LILYGO T-Display

Popular compact display board with ST7789.

```yaml
# LILYGO T-Display (ST7789 1.14")
substitutions:
  device_name: "t-display"
  friendly_name: "T-Display"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev
  framework:
    type: arduino

# SPI for display
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO19

# Backlight control
output:
  - platform: ledc
    pin: GPIO4
    id: backlight_output

light:
  - platform: monochromatic
    output: backlight_output
    name: "Backlight"
    id: backlight
    restore_mode: ALWAYS_ON

# Display
display:
  - platform: st7789v
    model: TTGO_TDisplay_135x240
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO23
    rotation: 90
    lambda: |-
      it.fill(Color::BLACK);
      it.print(10, 10, id(font_medium), Color::WHITE, "Hello!");

font:
  - file: "gfonts://Roboto"
    id: font_medium
    size: 20

# Built-in buttons
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      inverted: true
    name: "Button 1"

  - platform: gpio
    pin:
      number: GPIO35
      inverted: true
    name: "Button 2"

# Battery voltage (via ADC)
sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery Voltage"
    attenuation: 11db
    filters:
      - multiply: 2.0  # Voltage divider
    update_interval: 60s
```

### Nextion Display Panel

Wall-mounted touch panel.

```yaml
# Nextion Touch Panel
substitutions:
  device_name: "nextion-panel"
  friendly_name: "Wall Panel"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp32:
  board: esp32dev

uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 115200

display:
  - platform: nextion
    id: nextion_display
    update_interval: 5s
    lambda: |-
      // Update temperature
      it.set_component_text_printf("temp", "%.1f°C", id(temperature).state);
      // Update humidity
      it.set_component_text_printf("humidity", "%.0f%%", id(humidity).state);

sensor:
  - platform: homeassistant
    entity_id: sensor.living_room_temperature
    id: temperature
    on_value:
      - lambda: |-
          id(nextion_display).set_component_text_printf("temp", "%.1f", x);

  - platform: homeassistant
    entity_id: sensor.living_room_humidity
    id: humidity

# Touch events from Nextion
binary_sensor:
  - platform: nextion
    page_id: 0
    component_id: 2
    name: "Light Button"
    on_press:
      - homeassistant.service:
          service: light.toggle
          data:
            entity_id: light.living_room
```

---

## Sensor Modifications

### IKEA VINDRIKTNING Mod

Add WiFi to IKEA's PM2.5 sensor.

```yaml
# IKEA VINDRIKTNING with ESP8266
substitutions:
  device_name: "vindriktning"
  friendly_name: "VINDRIKTNING"

esphome:
  name: ${device_name}
  friendly_name: ${friendly_name}

esp8266:
  board: d1_mini

# Read PM1006 sensor via UART
uart:
  rx_pin: GPIO4  # D2
  baud_rate: 9600

sensor:
  - platform: pm1006
    pm_2_5:
      name: "PM2.5"
      filters:
        - sliding_window_moving_average:
            window_size: 10
            send_every: 10
```

### VINDRIKTNING with Additional Sensors

```yaml
# Enhanced VINDRIKTNING
# Add SCD40 for CO2 and BME280 for temp/humidity

i2c:
  sda: GPIO5  # D1
  scl: GPIO14 # D5

uart:
  rx_pin: GPIO4
  baud_rate: 9600

sensor:
  # Original PM sensor
  - platform: pm1006
    pm_2_5:
      name: "PM2.5"

  # CO2 sensor (SCD40)
  - platform: scd4x
    co2:
      name: "CO2"
    temperature:
      name: "Temperature"
      id: scd_temp
    humidity:
      name: "Humidity"
      id: scd_hum
    update_interval: 60s

  # Alternative: BME280
  - platform: bme280_i2c
    address: 0x76
    temperature:
      name: "Temperature"
      oversampling: 16x
    humidity:
      name: "Humidity"
    pressure:
      name: "Pressure"
    update_interval: 60s
```

### Xiaomi Mi Flora Plant Sensor (BLE)

```yaml
# Read Xiaomi Mi Flora via BLE
esphome:
  name: plant-monitor
  friendly_name: "Plant Monitor"

esp32:
  board: esp32dev

esp32_ble_tracker:

sensor:
  - platform: xiaomi_hhccjcy01
    mac_address: "C4:7C:8D:XX:XX:XX"
    temperature:
      name: "Plant Temperature"
    moisture:
      name: "Soil Moisture"
    illuminance:
      name: "Plant Light"
    conductivity:
      name: "Soil Conductivity"
    battery_level:
      name: "Plant Sensor Battery"
```

### Xiaomi Mijia Temperature/Humidity (BLE)

```yaml
# Xiaomi Mijia LYWSD03MMC (with ATC firmware)
esp32_ble_tracker:

sensor:
  - platform: atc_mithermometer
    mac_address: "A4:C1:38:XX:XX:XX"
    temperature:
      name: "Room Temperature"
    humidity:
      name: "Room Humidity"
    battery_level:
      name: "Sensor Battery"
    battery_voltage:
      name: "Sensor Voltage"
```

---

## Voice Assistants

### ESP32-S3-BOX Voice Assistant

```yaml
# ESP32-S3-BOX Voice Assistant
esphome:
  name: voice-assistant
  friendly_name: "Voice Assistant"

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz

# Microphone (I2S)
i2s_audio:
  - id: i2s_in
    i2s_lrclk_pin: GPIO45
    i2s_bclk_pin: GPIO17
  - id: i2s_out
    i2s_lrclk_pin: GPIO46
    i2s_bclk_pin: GPIO9

microphone:
  - platform: i2s_audio
    id: box_mic
    adc_type: external
    i2s_din_pin: GPIO16
    i2s_audio_id: i2s_in
    pdm: true

speaker:
  - platform: i2s_audio
    id: box_speaker
    dac_type: external
    i2s_dout_pin: GPIO15
    i2s_audio_id: i2s_out
    mode: mono

voice_assistant:
  microphone: box_mic
  speaker: box_speaker
  use_wake_word: true
  noise_suppression_level: 2
  auto_gain: 31dBFS
  volume_multiplier: 2.0
  on_wake_word_detected:
    - light.turn_on:
        id: led_ring
        effect: "pulse"
  on_listening:
    - light.turn_on:
        id: led_ring
        brightness: 100%
        red: 0%
        green: 100%
        blue: 0%
  on_tts_end:
    - light.turn_off: led_ring
  on_error:
    - light.turn_on:
        id: led_ring
        brightness: 100%
        red: 100%
        green: 0%
        blue: 0%
    - delay: 1s
    - light.turn_off: led_ring

# Wake word
micro_wake_word:
  model: okay_nabu
  on_wake_word_detected:
    - voice_assistant.start:
```

### M5Stack ATOM Echo

Compact voice assistant.

```yaml
# M5Stack ATOM Echo
esphome:
  name: atom-echo
  friendly_name: "ATOM Echo"

esp32:
  board: m5stack-atom
  framework:
    type: esp-idf

# I2S Audio
i2s_audio:
  i2s_lrclk_pin: GPIO33
  i2s_bclk_pin: GPIO19

microphone:
  - platform: i2s_audio
    id: atom_mic
    adc_type: external
    i2s_din_pin: GPIO23
    pdm: true

speaker:
  - platform: i2s_audio
    id: atom_speaker
    dac_type: external
    i2s_dout_pin: GPIO22
    mode: mono

voice_assistant:
  microphone: atom_mic
  speaker: atom_speaker
  use_wake_word: false  # Push-to-talk

# Button for push-to-talk
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO39
      inverted: true
    name: "Button"
    on_press:
      - voice_assistant.start:
    on_release:
      - voice_assistant.stop:

# Status LED
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO27
    num_leds: 1
    rmt_channel: 0
    chipset: SK6812
    rgb_order: GRB
    id: status_led
    name: "Status LED"
```

---

## Best Practices for Community Devices

### Finding GPIO Pins

```yaml
# Use templates to test pins
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "GPIO0"
  - platform: gpio
    pin: GPIO2
    name: "GPIO2"
  # Add more GPIOs to discover wiring
```

### Calibrating Power Monitoring

```yaml
# Calibrate BL0937/HLW8012
sensor:
  - platform: hlw8012
    # 1. Measure with known load (e.g., 100W bulb)
    # 2. Compare reported vs actual
    # 3. Adjust these values:
    current_resistor: 0.001  # Typical for most devices
    voltage_divider: 770     # Adjust if voltage is wrong
```

### Safe Flash Settings

```yaml
# Preserve flash on power loss
esp8266:
  board: esp8285
  restore_from_flash: true

preferences:
  flash_write_interval: 5min
```

### Template for Unknown Devices

```yaml
# Discovery template for unknown devices
substitutions:
  device_name: "unknown-device"

esphome:
  name: ${device_name}

esp8266:
  board: esp8285

# Enable all logging
logger:
  level: VERBOSE

# Test all GPIOs as inputs
binary_sensor:
  - platform: gpio
    pin: GPIO0
    name: "GPIO0"
  - platform: gpio
    pin: GPIO2
    name: "GPIO2"
  - platform: gpio
    pin: GPIO4
    name: "GPIO4"
  - platform: gpio
    pin: GPIO5
    name: "GPIO5"
  - platform: gpio
    pin: GPIO12
    name: "GPIO12"
  - platform: gpio
    pin: GPIO13
    name: "GPIO13"
  - platform: gpio
    pin: GPIO14
    name: "GPIO14"
  - platform: gpio
    pin: GPIO16
    name: "GPIO16"

# Test GPIOs as outputs (one at a time!)
# switch:
#   - platform: gpio
#     pin: GPIO12
#     name: "Test GPIO12"
```

