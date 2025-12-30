# ESPHome Displays Reference

Complete reference for display platforms, graphics, fonts, and LVGL.

## Table of Contents
- [Display Basics](#display-basics)
- [OLED Displays](#oled-displays)
- [TFT Displays](#tft-displays)
- [E-Paper/E-Ink](#e-paper-e-ink)
- [LED Matrix](#led-matrix)
- [Segment Displays](#segment-displays)
- [Nextion HMI](#nextion-hmi)
- [Fonts and Graphics](#fonts-and-graphics)
- [LVGL Framework](#lvgl-framework)

---

## Display Basics

All displays use a common rendering system with lambda functions.

### Display Lambda
```yaml
display:
  - platform: ...
    lambda: |-
      it.print(0, 0, id(font), "Hello World");
```

### Common Drawing Methods
```cpp
// Text
it.print(x, y, font, "text");
it.print(x, y, font, TextAlign::CENTER, "centered");
it.printf(x, y, font, "Value: %.1f", sensor_value);

// Shapes
it.line(x1, y1, x2, y2);
it.rectangle(x, y, width, height);
it.filled_rectangle(x, y, width, height);
it.circle(x, y, radius);
it.filled_circle(x, y, radius);

// Images
it.image(x, y, id(my_image));

// Colors (for color displays)
it.print(x, y, font, Color(255, 0, 0), "Red text");
it.filled_rectangle(0, 0, 100, 50, Color(0, 255, 0));
```

### Text Alignment
```cpp
TextAlign::TOP_LEFT      // Default
TextAlign::TOP_CENTER
TextAlign::TOP_RIGHT
TextAlign::CENTER_LEFT
TextAlign::CENTER        // Both axes
TextAlign::CENTER_RIGHT
TextAlign::BOTTOM_LEFT
TextAlign::BOTTOM_CENTER
TextAlign::BOTTOM_RIGHT
TextAlign::BASELINE_LEFT
TextAlign::BASELINE_CENTER
TextAlign::BASELINE_RIGHT
```

---

## OLED Displays

### SSD1306 (I2C)
Most common 0.96" and 1.3" OLED.

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

font:
  - file: "gfonts://Roboto"
    id: roboto
    size: 14

display:
  - platform: ssd1306_i2c
    model: "SSD1306 128x64"
    address: 0x3C
    lambda: |-
      it.print(0, 0, id(roboto), "Hello!");
```

### SSD1306 Models
| Model | Resolution |
|-------|------------|
| SSD1306 128x64 | 128x64 |
| SSD1306 128x32 | 128x32 |
| SSD1306 96x16 | 96x16 |
| SSD1306 64x48 | 64x48 |
| SH1106 128x64 | 128x64 |
| SH1107 128x64 | 128x64 |

### SSD1306 (SPI)
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23

display:
  - platform: ssd1306_spi
    model: "SSD1306 128x64"
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO17
    lambda: |-
      it.print(0, 0, id(font), "SPI OLED");
```

### SSD1327 (Grayscale OLED)
```yaml
display:
  - platform: ssd1327_i2c
    model: "SSD1327 128x128"
    address: 0x3C
    lambda: |-
      // Supports 16 grayscale levels
      it.print(0, 0, id(font), "Grayscale");
```

### SSD1322 (256x64 OLED)
```yaml
display:
  - platform: ssd1322_spi
    model: "SSD1322 256x64"
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO17
```

### SSD1351 (Color OLED)
```yaml
display:
  - platform: ssd1351_spi
    model: "SSD1351 128x128"
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO17
    lambda: |-
      it.filled_rectangle(0, 0, 64, 64, Color(255, 0, 0));
```

---

## TFT Displays

### ILI9xxx Family
Covers ILI9341, ILI9342, ILI9481, ILI9486, ILI9488.

```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

display:
  - platform: ili9xxx
    model: ILI9341
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO17
    dimensions:
      width: 320
      height: 240
    lambda: |-
      it.fill(Color::BLACK);
      it.print(10, 10, id(font), Color::WHITE, "ILI9341");
```

### ILI9xxx Models
| Model | Resolution | Notes |
|-------|------------|-------|
| ILI9341 | 320x240 | Most common |
| ILI9342 | 320x240 | Landscape |
| ILI9481 | 480x320 | 3.5" |
| ILI9486 | 480x320 | 3.5" |
| ILI9488 | 480x320 | 3.5" |
| ST7789V | 240x320 | Common |
| ST7735 | 128x160 | Small |

### ST7789V
```yaml
display:
  - platform: st7789v
    model: TTGO_TDisplay_135x240
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO23
    backlight_pin: GPIO4
    lambda: |-
      it.print(0, 0, id(font), "ST7789V");
```

### ST7735
```yaml
display:
  - platform: st7735
    model: INITR_18BLACKTAB
    cs_pin: GPIO5
    dc_pin: GPIO16
    reset_pin: GPIO17
    lambda: |-
      it.print(0, 0, id(font), "ST7735");
```

### Rotation
```yaml
display:
  - platform: ili9xxx
    model: ILI9341
    rotation: 90  # 0, 90, 180, 270
    # ...
```

### Backlight Control
```yaml
output:
  - platform: ledc
    id: backlight_pwm
    pin: GPIO4

light:
  - platform: monochromatic
    name: "Display Backlight"
    output: backlight_pwm
    restore_mode: ALWAYS_ON
```

---

## E-Paper / E-Ink

### Waveshare E-Paper
```yaml
spi:
  clk_pin: GPIO13
  mosi_pin: GPIO14

display:
  - platform: waveshare_epaper
    model: 2.90inv2
    cs_pin: GPIO15
    dc_pin: GPIO27
    busy_pin: GPIO25
    reset_pin: GPIO26
    full_update_every: 30
    lambda: |-
      it.print(0, 0, id(font), "E-Paper");
```

### Waveshare Models
| Model | Resolution | Colors |
|-------|------------|--------|
| 1.54in | 200x200 | B/W |
| 2.13in | 250x122 | B/W |
| 2.90in | 296x128 | B/W |
| 2.90inv2 | 296x128 | B/W faster |
| 4.20in | 400x300 | B/W |
| 7.50in | 800x480 | B/W |
| 2.13in-ttgo | 250x122 | TTGO T5 |
| 2.90in-b | 296x128 | B/W/Red |
| 4.20in-bv2 | 400x300 | B/W/Red |

### Partial Update
```yaml
display:
  - platform: waveshare_epaper
    model: 2.90inv2
    full_update_every: 30  # Full refresh every 30 updates
    # Partial updates for other refreshes
```

### Inkplate
```yaml
display:
  - platform: inkplate6
    greyscale: true
    partial_updating: true
    update_interval: 60s
    lambda: |-
      it.print(10, 10, id(font), "Inkplate");
```

---

## LED Matrix

### MAX7219 (7-segment & dot matrix)
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23

display:
  - platform: max7219digit
    cs_pin: GPIO5
    num_chips: 4
    intensity: 8
    lambda: |-
      it.print(0, 0, id(font), "1234");
```

### MAX7219 Scroll Text
```yaml
display:
  - platform: max7219digit
    cs_pin: GPIO5
    num_chips: 4
    scroll_enable: true
    scroll_mode: CONTINUOUS
    scroll_speed: 100ms
    scroll_delay: 2
    lambda: |-
      it.print(0, 0, id(font), "SCROLLING TEXT");
```

### HUB75 RGB Matrix
```yaml
display:
  - platform: hub75_matrix
    width: 64
    height: 32
    chain_length: 1
    i2sspeed: HZ_10M

    R1_pin: GPIO25
    G1_pin: GPIO26
    B1_pin: GPIO27
    R2_pin: GPIO14
    G2_pin: GPIO12
    B2_pin: GPIO13
    A_pin: GPIO23
    B_pin: GPIO19
    C_pin: GPIO5
    D_pin: GPIO17
    E_pin: GPIO32
    LAT_pin: GPIO4
    OE_pin: GPIO15
    CLK_pin: GPIO16

    lambda: |-
      it.filled_rectangle(0, 0, 32, 32, Color(255, 0, 0));
```

### TM1637 (4-digit 7-segment)
```yaml
display:
  - platform: tm1637
    clk_pin: GPIO5
    dio_pin: GPIO4
    intensity: 7
    lambda: |-
      it.print("12:34");
```

### TM1638 (8-digit with buttons)
```yaml
display:
  - platform: tm1638
    clk_pin: GPIO5
    dio_pin: GPIO4
    stb_pin: GPIO15
    intensity: 7
    lambda: |-
      it.print("HELLO   ");
```

---

## Segment Displays

### LCD Character Display (HD44780)
```yaml
# I2C backpack (PCF8574)
i2c:
  sda: GPIO21
  scl: GPIO22

display:
  - platform: lcd_pcf8574
    dimensions: 16x2
    address: 0x27
    lambda: |-
      it.print(0, 0, "Line 1");
      it.print(0, 1, "Line 2");
```

### LCD Direct GPIO
```yaml
display:
  - platform: lcd_gpio
    dimensions: 20x4
    data_pins:
      - GPIO5
      - GPIO4
      - GPIO14
      - GPIO12
    enable_pin: GPIO13
    rs_pin: GPIO15
    lambda: |-
      it.print("Hello LCD");
```

---

## Nextion HMI

### Basic Setup
```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 9600

display:
  - platform: nextion
    id: nextion_display
    update_interval: 5s
    lambda: |-
      it.set_component_text("t0", "Hello");
      it.set_component_value("n0", 42);
```

### Nextion Components
```yaml
# Text sensor from Nextion
text_sensor:
  - platform: nextion
    nextion_id: nextion_display
    name: "Nextion Text"
    component_name: t0

# Number from Nextion
sensor:
  - platform: nextion
    nextion_id: nextion_display
    name: "Nextion Value"
    component_name: n0

# Binary sensor (button touch)
binary_sensor:
  - platform: nextion
    page_id: 0
    component_id: 1
    name: "Button"
```

### Nextion Touch Events
```yaml
binary_sensor:
  - platform: nextion
    page_id: 0
    component_id: 2
    name: "Touch Button"
    on_press:
      - light.toggle: my_light
```

### Upload TFT File
```yaml
display:
  - platform: nextion
    id: nextion_display
    tft_url: "http://192.168.1.100/display.tft"
```

---

## Fonts and Graphics

### Google Fonts
```yaml
font:
  - file: "gfonts://Roboto"
    id: roboto_small
    size: 12
  - file: "gfonts://Roboto"
    id: roboto_medium
    size: 20
  - file: "gfonts://Roboto@700"  # Bold
    id: roboto_bold
    size: 24
```

### Local Fonts
```yaml
font:
  - file: "fonts/arial.ttf"
    id: arial
    size: 16
```

### Glyphs (Special Characters)
```yaml
font:
  - file: "gfonts://Roboto"
    id: roboto
    size: 16
    glyphs: "0123456789:.-°C%"  # Only include needed chars
```

### Material Design Icons
```yaml
font:
  - file: "gfonts://Material+Symbols+Outlined"
    id: icons
    size: 24
    glyphs: [
      "\U0000E88A",  # home
      "\U0000E8B8",  # settings
      "\U0000E8B5",  # power
    ]
```

### Images
```yaml
image:
  - file: "images/logo.png"
    id: logo
    resize: 64x64
    type: RGB24  # or BINARY, GRAYSCALE, RGB565

display:
  lambda: |-
    it.image(0, 0, id(logo));
```

### Animated GIF
```yaml
animation:
  - file: "images/loading.gif"
    id: loading_anim
    resize: 32x32

display:
  lambda: |-
    id(loading_anim).next_frame();
    it.image(0, 0, id(loading_anim));
```

### QR Code
```yaml
qr_code:
  - id: wifi_qr
    value: "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;"

display:
  lambda: |-
    it.qr_code(0, 0, id(wifi_qr), Color::BLACK, 2);
```

### Graph
```yaml
graph:
  - id: temp_graph
    sensor: temp_sensor
    duration: 1h
    width: 100
    height: 50
    x_grid: 10min
    y_grid: 5

display:
  lambda: |-
    it.graph(10, 10, id(temp_graph));
```

---

## LVGL Framework

Light and Versatile Graphics Library for advanced UIs.

### Basic Setup
```yaml
lvgl:
  displays:
    - display_id: my_display
  touchscreens:
    - touchscreen_id: my_touchscreen

display:
  - platform: ili9xxx
    id: my_display
    model: ILI9341
    # ... pins
```

### LVGL Widgets

#### Label
```yaml
lvgl:
  pages:
    - id: main_page
      widgets:
        - label:
            id: temp_label
            text: "Temperature"
            align: CENTER
            text_font: montserrat_20
```

#### Button
```yaml
lvgl:
  pages:
    - id: main_page
      widgets:
        - button:
            id: my_button
            x: 10
            y: 100
            width: 100
            height: 40
            widgets:
              - label:
                  text: "Click Me"
            on_click:
              - logger.log: "Button clicked!"
```

#### Slider
```yaml
lvgl:
  pages:
    - id: main_page
      widgets:
        - slider:
            id: brightness_slider
            x: 10
            y: 150
            width: 200
            min_value: 0
            max_value: 255
            on_value:
              - output.set_level:
                  id: led_output
                  level: !lambda "return x / 255.0;"
```

#### Arc (Gauge)
```yaml
lvgl:
  pages:
    - id: main_page
      widgets:
        - arc:
            id: temp_arc
            x: 100
            y: 100
            width: 150
            height: 150
            min_value: 0
            max_value: 40
            value: !lambda "return id(temp_sensor).state;"
```

#### Switch
```yaml
lvgl:
  pages:
    - id: main_page
      widgets:
        - switch:
            id: light_switch
            x: 10
            y: 200
            on_click:
              - switch.toggle: my_relay
```

### LVGL Styles
```yaml
lvgl:
  style_definitions:
    - id: style_btn
      bg_color: 0x2196F3
      radius: 8
      text_color: 0xFFFFFF

  pages:
    - widgets:
        - button:
            styles: style_btn
```

### LVGL Pages & Navigation
```yaml
lvgl:
  pages:
    - id: page_home
      widgets:
        - label:
            text: "Home"
        - button:
            widgets:
              - label:
                  text: "Settings"
            on_click:
              - lvgl.page.show: page_settings

    - id: page_settings
      widgets:
        - label:
            text: "Settings"
        - button:
            widgets:
              - label:
                  text: "Back"
            on_click:
              - lvgl.page.show: page_home
```

### LVGL Update from Sensor
```yaml
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      id: room_temp
      on_value:
        - lvgl.label.update:
            id: temp_label
            text: !lambda |-
              static char buf[16];
              snprintf(buf, sizeof(buf), "%.1f°C", x);
              return buf;
```

### LVGL with Touchscreen
```yaml
touchscreen:
  - platform: xpt2046
    id: my_touch
    cs_pin: GPIO33
    interrupt_pin: GPIO36
    calibration:
      x_min: 230
      x_max: 3860
      y_min: 300
      y_max: 3860

lvgl:
  touchscreens:
    - touchscreen_id: my_touch
```

---

## Common Patterns

### Clock Display
```yaml
time:
  - platform: homeassistant
    id: ha_time

display:
  lambda: |-
    it.strftime(64, 32, id(font_large), TextAlign::CENTER,
                "%H:%M", id(ha_time).now());
```

### Sensor Dashboard
```yaml
display:
  lambda: |-
    it.printf(0, 0, id(font), "Temp: %.1f°C", id(temp).state);
    it.printf(0, 20, id(font), "Humidity: %.0f%%", id(hum).state);
    it.printf(0, 40, id(font), "CO2: %.0f ppm", id(co2).state);
```

### Status Icons
```yaml
display:
  lambda: |-
    // WiFi status icon
    if (WiFi.isConnected()) {
      it.image(100, 0, id(wifi_icon));
    } else {
      it.image(100, 0, id(wifi_off_icon));
    }
```

### Page Switching
```yaml
globals:
  - id: display_page
    type: int
    initial_value: "0"

binary_sensor:
  - platform: gpio
    pin: GPIO0
    on_click:
      - lambda: |-
          id(display_page) = (id(display_page) + 1) % 3;

display:
  lambda: |-
    switch (id(display_page)) {
      case 0:
        it.print(0, 0, id(font), "Page 1");
        break;
      case 1:
        it.print(0, 0, id(font), "Page 2");
        break;
      case 2:
        it.print(0, 0, id(font), "Page 3");
        break;
    }
```

### Screen Timeout
```yaml
globals:
  - id: screen_on
    type: bool
    initial_value: "true"
  - id: last_activity
    type: uint32_t
    initial_value: "0"

interval:
  - interval: 1s
    then:
      - lambda: |-
          if (millis() - id(last_activity) > 60000) {
            id(screen_on) = false;
          }

binary_sensor:
  - platform: gpio
    pin: GPIO0
    on_press:
      - lambda: |-
          id(screen_on) = true;
          id(last_activity) = millis();

display:
  lambda: |-
    if (!id(screen_on)) {
      it.fill(Color::BLACK);
      return;
    }
    // Normal display code...
```
