# ESPHome Lights Reference

Complete guide to lights: addressable LEDs, RGB strips, effects, and control.

## Table of Contents

- [Light Types Overview](#light-types-overview)
- [Binary Lights](#binary-lights)
- [Monochromatic Lights](#monochromatic-lights)
- [RGB Lights](#rgb-lights)
- [RGBW Lights](#rgbw-lights)
- [Color Temperature Lights](#color-temperature-lights)
- [Addressable LED Strips](#addressable-led-strips)
- [Light Effects](#light-effects)
- [Light Groups](#light-groups)
- [Partitions](#partitions)
- [Transitions and Gamma](#transitions-and-gamma)
- [Automation](#automation)
- [Complete Examples](#complete-examples)

---

## Light Types Overview

| Type | Channels | Use Case |
|------|----------|----------|
| Binary | On/Off | Simple LED, relay-controlled lights |
| Monochromatic | Brightness | Single color dimmable LED |
| RGB | Red, Green, Blue | Color mixing LED strips |
| RGBW | RGB + White | LED strips with dedicated white |
| RGBWW | RGB + Cold White + Warm White | Full color + tunable white |
| CWWW | Cold White + Warm White | Tunable white only |
| Addressable | Per-LED control | WS2812, SK6812, APA102 |

---

## Binary Lights

### Basic On/Off

```yaml
output:
  - platform: gpio
    pin: GPIO12
    id: light_output

light:
  - platform: binary
    name: "Light"
    output: light_output
```

### With Status LED

```yaml
light:
  - platform: status_led
    name: "Status LED"
    pin: GPIO2
```

---

## Monochromatic Lights

### PWM Dimming (ESP32)

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: led_output
    frequency: 1000Hz

light:
  - platform: monochromatic
    name: "Dimmable LED"
    output: led_output
    gamma_correct: 2.8
```

### PWM Dimming (ESP8266)

```yaml
output:
  - platform: esp8266_pwm
    pin: GPIO5
    id: led_output
    frequency: 1000Hz

light:
  - platform: monochromatic
    name: "Dimmable LED"
    output: led_output
```

### With Default State

```yaml
light:
  - platform: monochromatic
    name: "LED"
    output: led_output
    default_transition_length: 1s
    restore_mode: RESTORE_DEFAULT_ON
```

---

## RGB Lights

### Common Anode RGB LED

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: red
    inverted: true  # Common anode needs inverted
  - platform: ledc
    pin: GPIO26
    id: green
    inverted: true
  - platform: ledc
    pin: GPIO27
    id: blue
    inverted: true

light:
  - platform: rgb
    name: "RGB LED"
    red: red
    green: green
    blue: blue
```

### Common Cathode RGB LED

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: red
  - platform: ledc
    pin: GPIO26
    id: green
  - platform: ledc
    pin: GPIO27
    id: blue

light:
  - platform: rgb
    name: "RGB LED"
    red: red
    green: green
    blue: blue
```

---

## RGBW Lights

### RGB + Dedicated White

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: red
  - platform: ledc
    pin: GPIO26
    id: green
  - platform: ledc
    pin: GPIO27
    id: blue
  - platform: ledc
    pin: GPIO14
    id: white

light:
  - platform: rgbw
    name: "RGBW Light"
    red: red
    green: green
    blue: blue
    white: white
    color_interlock: true  # Prevents RGB+W simultaneously
```

### RGBWW (RGB + Cold + Warm White)

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: red
  - platform: ledc
    pin: GPIO26
    id: green
  - platform: ledc
    pin: GPIO27
    id: blue
  - platform: ledc
    pin: GPIO14
    id: cold_white
  - platform: ledc
    pin: GPIO12
    id: warm_white

light:
  - platform: rgbww
    name: "RGBWW Light"
    red: red
    green: green
    blue: blue
    cold_white: cold_white
    warm_white: warm_white
    cold_white_color_temperature: 6500 K
    warm_white_color_temperature: 2700 K
```

---

## Color Temperature Lights

### CWWW (Tunable White)

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: cold_white
  - platform: ledc
    pin: GPIO26
    id: warm_white

light:
  - platform: cwww
    name: "Tunable White"
    cold_white: cold_white
    warm_white: warm_white
    cold_white_color_temperature: 6500 K
    warm_white_color_temperature: 2700 K
    constant_brightness: true
```

---

## Addressable LED Strips

### ESP32 RMT (Recommended for ESP32)

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    rmt_channel: 0
    chipset: WS2812
    rgb_order: GRB
    name: "LED Strip"
```

### Supported Chipsets

| Chipset | Colors | Data | Clock |
|---------|--------|------|-------|
| WS2812 | RGB | Yes | No |
| WS2812B | RGB | Yes | No |
| WS2811 | RGB | Yes | No |
| SK6812 | RGBW | Yes | No |
| APA102 | RGB | Yes | Yes |
| SK9822 | RGB | Yes | Yes |

### WS2812B Configuration

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    rmt_channel: 0
    chipset: WS2812B
    rgb_order: GRB
    name: "WS2812B Strip"
```

### SK6812 (RGBW)

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    rmt_channel: 0
    chipset: SK6812
    rgb_order: GRB
    is_rgbw: true
    name: "SK6812 RGBW Strip"
```

### APA102/SK9822 (SPI)

```yaml
light:
  - platform: apa102
    data_pin: GPIO23
    clock_pin: GPIO18
    num_leds: 60
    name: "APA102 Strip"
```

### ESP8266 with NeoPixelBus

```yaml
light:
  - platform: neopixelbus
    type: GRB
    variant: WS2812
    pin: GPIO3  # RX pin recommended
    num_leds: 60
    name: "LED Strip"
```

### FastLED (Alternative)

```yaml
light:
  - platform: fastled_clockless
    chipset: WS2812B
    pin: GPIO25
    num_leds: 60
    rgb_order: GRB
    name: "FastLED Strip"
```

### Multiple RMT Channels

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    rmt_channel: 0
    chipset: WS2812
    name: "Strip 1"

  - platform: esp32_rmt_led_strip
    pin: GPIO26
    num_leds: 30
    rmt_channel: 1
    chipset: WS2812
    name: "Strip 2"
```

---

## Light Effects

### Built-in Effects

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    chipset: WS2812
    name: "LED Strip"
    effects:
      # Color effects
      - rainbow:
      - rainbow:
          name: "Fast Rainbow"
          speed: 20
          width: 50
      - color_wipe:
      - color_wipe:
          name: "Color Wipe"
          colors:
            - red: 100%
              green: 0%
              blue: 0%
              num_leds: 1
            - red: 0%
              green: 100%
              blue: 0%
              num_leds: 1

      # Pulse effects
      - pulse:
      - pulse:
          name: "Slow Pulse"
          transition_length: 2s
          update_interval: 2s
          min_brightness: 0%
          max_brightness: 100%

      # Strobe
      - strobe:
      - strobe:
          name: "Fast Strobe"
          colors:
            - state: true
              brightness: 100%
              duration: 50ms
            - state: false
              duration: 50ms

      # Random
      - random:
      - random:
          name: "Random Colors"
          transition_length: 2s
          update_interval: 3s

      # Flicker (candle)
      - flicker:
      - flicker:
          name: "Candle"
          alpha: 95%
          intensity: 2%

      # Scan/Knight Rider
      - scan:
          name: "Knight Rider"
          move_interval: 100ms
          scan_width: 3
```

### Addressable Effects

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    chipset: WS2812
    name: "LED Strip"
    effects:
      # Addressable rainbow
      - addressable_rainbow:
      - addressable_rainbow:
          name: "Rainbow Shift"
          speed: 10
          width: 50

      # Addressable color wipe
      - addressable_color_wipe:
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
          add_led_interval: 100ms
          reverse: false

      # Addressable scan
      - addressable_scan:
          name: "Scan"
          move_interval: 100ms
          scan_width: 5

      # Addressable twinkle
      - addressable_twinkle:
          name: "Twinkle"
          twinkle_probability: 5%
          progress_interval: 4ms

      # Addressable random twinkle
      - addressable_random_twinkle:
          name: "Random Twinkle"
          twinkle_probability: 5%
          progress_interval: 32ms

      # Addressable fireworks
      - addressable_fireworks:
          name: "Fireworks"
          update_interval: 32ms
          spark_probability: 10%
          use_random_color: false
          fade_out_rate: 120

      # Addressable flicker
      - addressable_flicker:
          name: "Flicker"
          update_interval: 16ms
          intensity: 5%
```

### Lambda Effects

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    chipset: WS2812
    name: "LED Strip"
    id: led_strip
    effects:
      - addressable_lambda:
          name: "Fire"
          update_interval: 15ms
          lambda: |-
            static uint8_t heat[60];
            // Fire2012 algorithm
            for (int i = 0; i < 60; i++) {
              heat[i] = qsub8(heat[i], random8(0, 55));
            }
            for (int k = 59; k >= 2; k--) {
              heat[k] = (heat[k-1] + heat[k-2] + heat[k-2]) / 3;
            }
            if (random8() < 120) {
              int y = random8(7);
              heat[y] = qadd8(heat[y], random8(160, 255));
            }
            for (int j = 0; j < 60; j++) {
              uint8_t t192 = heat[j] * 191 / 255;
              uint8_t heatramp = t192 & 0x3F;
              heatramp <<= 2;
              if (t192 & 0x80) {
                it[j] = Color(255, 255, heatramp);
              } else if (t192 & 0x40) {
                it[j] = Color(255, heatramp, 0);
              } else {
                it[j] = Color(heatramp, 0, 0);
              }
            }

      - addressable_lambda:
          name: "Breathing"
          update_interval: 16ms
          lambda: |-
            static uint16_t phase = 0;
            phase += 256;
            uint8_t brightness = (sin16(phase) + 32768) >> 8;
            Color color = Color(brightness, 0, brightness);
            it.all() = color;
```

---

## Light Groups

### Grouping Multiple Lights

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 30
    chipset: WS2812
    name: "Strip 1"
    id: strip1

  - platform: esp32_rmt_led_strip
    pin: GPIO26
    num_leds: 30
    chipset: WS2812
    name: "Strip 2"
    id: strip2

  - platform: group
    name: "All Strips"
    entities:
      - strip1
      - strip2
```

---

## Partitions

### Splitting a Strip

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 120
    chipset: WS2812
    id: led_strip_full
    internal: true

  - platform: partition
    name: "Section 1"
    segments:
      - id: led_strip_full
        from: 0
        to: 39

  - platform: partition
    name: "Section 2"
    segments:
      - id: led_strip_full
        from: 40
        to: 79

  - platform: partition
    name: "Section 3"
    segments:
      - id: led_strip_full
        from: 80
        to: 119
```

### Complex Partitions

```yaml
light:
  - platform: partition
    name: "Mixed Segment"
    segments:
      - id: strip1
        from: 0
        to: 29
      - id: strip2
        from: 0
        to: 29
        reversed: true
```

---

## Transitions and Gamma

### Default Transition

```yaml
light:
  - platform: monochromatic
    name: "LED"
    output: led_output
    default_transition_length: 500ms
```

### Gamma Correction

```yaml
light:
  - platform: monochromatic
    name: "LED"
    output: led_output
    gamma_correct: 2.8  # Default is 2.8

# For addressable strips
light:
  - platform: esp32_rmt_led_strip
    # ...
    correction:
      red: 100%
      green: 75%  # Reduce green intensity
      blue: 85%
```

### Restore Modes

```yaml
light:
  - platform: monochromatic
    name: "LED"
    output: led_output
    restore_mode: RESTORE_DEFAULT_OFF  # Options:
    # RESTORE_DEFAULT_OFF - Restore or default to off
    # RESTORE_DEFAULT_ON - Restore or default to on
    # RESTORE_INVERTED_DEFAULT_OFF - Restore inverted or off
    # RESTORE_INVERTED_DEFAULT_ON - Restore inverted or on
    # RESTORE_AND_OFF - Always restore, then turn off
    # RESTORE_AND_ON - Always restore, then turn on
    # ALWAYS_OFF - Always start off
    # ALWAYS_ON - Always start on
```

---

## Automation

### Turn On/Off Actions

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    chipset: WS2812
    name: "LED Strip"
    id: led_strip

binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_press:
      - light.turn_on:
          id: led_strip
          brightness: 80%
          red: 100%
          green: 50%
          blue: 0%
          transition_length: 1s
    on_release:
      - light.turn_off:
          id: led_strip
          transition_length: 2s
```

### Toggle with Effect

```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_click:
      - light.toggle:
          id: led_strip
          effect: "Rainbow"
```

### Color from Sensor

```yaml
sensor:
  - platform: dht
    temperature:
      id: temp
      on_value:
        - light.turn_on:
            id: led_strip
            red: !lambda |-
              return x > 25 ? 1.0 : 0.0;
            blue: !lambda |-
              return x < 20 ? 1.0 : 0.0;
            green: !lambda |-
              return (x >= 20 && x <= 25) ? 1.0 : 0.0;
```

### Addressable Set

```yaml
script:
  - id: set_led
    parameters:
      led_index: int
      r: int
      g: int
      b: int
    then:
      - lambda: |-
          id(led_strip)[led_index] = Color(r, g, b);
          id(led_strip).schedule_show();
```

---

## Complete Examples

### Smart Bulb

```yaml
output:
  - platform: ledc
    pin: GPIO25
    id: cold_white
  - platform: ledc
    pin: GPIO26
    id: warm_white

light:
  - platform: cwww
    name: "Smart Bulb"
    cold_white: cold_white
    warm_white: warm_white
    cold_white_color_temperature: 6500 K
    warm_white_color_temperature: 2700 K
    constant_brightness: true
    default_transition_length: 500ms
    restore_mode: RESTORE_DEFAULT_OFF
```

### Under Cabinet LED Strip

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 120
    chipset: WS2812
    rgb_order: GRB
    name: "Under Cabinet"
    id: cabinet_led
    default_transition_length: 500ms
    effects:
      - random:
      - strobe:
      - pulse:
      - addressable_rainbow:

binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_click:
      min_length: 50ms
      max_length: 500ms
      then:
        - light.toggle: cabinet_led
    on_click:
      min_length: 1s
      max_length: 5s
      then:
        - light.control:
            id: cabinet_led
            effect: "None"
            brightness: 100%
            red: 100%
            green: 100%
            blue: 100%
```

### Mood Lighting

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 60
    chipset: WS2812
    name: "Mood Light"
    id: mood_light
    effects:
      - addressable_lambda:
          name: "Sunset"
          update_interval: 50ms
          lambda: |-
            static float phase = 0;
            phase += 0.002;
            if (phase > 1) phase = 0;
            for (int i = 0; i < it.size(); i++) {
              float pos = float(i) / it.size();
              uint8_t r = 255;
              uint8_t g = 100 * (1 - pos);
              uint8_t b = 50 * pos;
              it[i] = Color(r, g, b);
            }

      - addressable_lambda:
          name: "Ocean"
          update_interval: 50ms
          lambda: |-
            static float phase = 0;
            phase += 0.02;
            for (int i = 0; i < it.size(); i++) {
              float wave = sin(phase + i * 0.1);
              uint8_t b = 128 + 127 * wave;
              uint8_t g = 50 + 50 * wave;
              it[i] = Color(0, g, b);
            }
```

### Status Indicator Strip

```yaml
light:
  - platform: esp32_rmt_led_strip
    pin: GPIO25
    num_leds: 8
    chipset: WS2812
    name: "Status LEDs"
    id: status_leds
    internal: true

script:
  - id: show_status
    parameters:
      status: int
    then:
      - lambda: |-
          Color color;
          switch(status) {
            case 0: color = Color(0, 255, 0); break;   // Green = OK
            case 1: color = Color(255, 165, 0); break; // Orange = Warning
            case 2: color = Color(255, 0, 0); break;   // Red = Error
            default: color = Color(0, 0, 255);         // Blue = Unknown
          }
          id(status_leds).all() = color;
          id(status_leds).schedule_show();
```
