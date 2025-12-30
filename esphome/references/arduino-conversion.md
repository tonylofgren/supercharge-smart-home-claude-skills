# Arduino to ESPHome Conversion Guide

Complete guide for converting Arduino projects to ESPHome, including code from GitHub repositories.

## Table of Contents

- [Why Convert to ESPHome?](#why-convert-to-esphome)
- [Conceptual Differences](#conceptual-differences)
- [Converting from GitHub](#converting-from-github)
- [Function Mapping Reference](#function-mapping-reference)
- [Lambda and C++ Integration](#lambda-and-c-integration)
- [Communication Protocols](#communication-protocols)
- [Custom Components](#custom-components)
- [Migration Examples](#migration-examples)
- [Common Pitfalls](#common-pitfalls)

---

## Why Convert to ESPHome?

### Benefits of ESPHome

| Arduino | ESPHome |
|---------|---------|
| Imperative C++ code | Declarative YAML configuration |
| Manual WiFi/MQTT handling | Built-in WiFi, API, MQTT |
| Custom OTA implementation | OTA updates out of the box |
| Write code for every sensor | Pre-built components for 200+ sensors |
| Manual Home Assistant integration | Native HA integration |
| Compile and flash manually | Dashboard with web-based management |

### When to Convert

- Device primarily interfaces with Home Assistant
- Using standard sensors/actuators with ESPHome components
- Want simplified maintenance and updates
- Need reliable OTA and monitoring

### When to Keep Arduino

- Highly custom timing-critical code
- Complex state machines
- Unusual hardware with no ESPHome component
- Real-time processing requirements

---

## Conceptual Differences

### Core Architecture

| Arduino | ESPHome | Notes |
|---------|---------|-------|
| `setup()` | `on_boot:` trigger | Or component initialization |
| `loop()` | `interval:` component | Or triggers/automations |
| Global variables | `globals:` section | Persistent state |
| `#include` libraries | Components or `external_components:` | Built-in or custom |
| Classes | Lambda functions | Or custom components |

### Execution Model

**Arduino:** Sequential execution in loop()
```cpp
void loop() {
  readSensor();
  updateDisplay();
  checkButton();
  delay(100);
}
```

**ESPHome:** Event-driven with automatic scheduling
```yaml
sensor:
  - platform: dht
    update_interval: 10s  # Automatic polling

binary_sensor:
  - platform: gpio
    on_press:  # Event-driven
      - display.page.show_next: oled
```

### State Management

**Arduino:**
```cpp
int counter = 0;
bool ledState = false;
float lastTemp = 0.0;
```

**ESPHome:**
```yaml
globals:
  - id: counter
    type: int
    initial_value: '0'
  - id: led_state
    type: bool
    initial_value: 'false'
  - id: last_temp
    type: float
    initial_value: '0.0'
```

---

## Converting from GitHub

### Workflow for GitHub Projects

When given a GitHub URL like `https://github.com/user/arduino-project`:

1. **Analyze Repository Structure**
   - Look for `.ino`, `.cpp`, `.h` files
   - Check `platformio.ini` or library dependencies
   - Read `README.md` for hardware requirements

2. **Identify Hardware**
   - Board type (ESP8266, ESP32, Arduino)
   - Sensors (DHT, BME280, etc.)
   - Outputs (relays, LEDs, displays)
   - Communication (I2C, SPI, UART)

3. **Map to ESPHome Components**
   - Find equivalent ESPHome platforms
   - Identify what needs custom lambdas
   - Determine if external components exist

4. **Convert Custom Logic**
   - Simple logic → automations/triggers
   - Complex logic → lambda functions
   - Very complex → custom component

5. **Generate Configuration**
   - Create complete working YAML
   - Include all necessary components
   - Add proper secrets references

### Example: Analyzing a GitHub Project

**Repository:** `https://github.com/example/temp-logger`

**Files found:**
```
src/
  main.cpp       # Main Arduino code
  display.cpp    # OLED display handling
  display.h
lib/
  Adafruit_SSD1306/
  DHT/
platformio.ini   # Build configuration
```

**From main.cpp:**
```cpp
#include <DHT.h>
#include <Wire.h>
#include "display.h"

#define DHT_PIN 4
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);
```

**Analysis:**
- Uses DHT22 sensor on GPIO4
- SSD1306 OLED display (I2C)
- Standard libraries → ESPHome components exist

**ESPHome Equivalent:**
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "Temperature"
      id: temp
    humidity:
      name: "Humidity"
      id: humidity

display:
  - platform: ssd1306_i2c
    model: "SSD1306 128x64"
    lambda: |-
      it.printf(0, 0, id(font), "Temp: %.1f", id(temp).state);
```

---

## Function Mapping Reference

### Digital I/O

| Arduino | ESPHome | Notes |
|---------|---------|-------|
| `pinMode(pin, OUTPUT)` | `output:` component | Configured in YAML |
| `pinMode(pin, INPUT)` | `binary_sensor:` | With appropriate mode |
| `pinMode(pin, INPUT_PULLUP)` | `mode: INPUT_PULLUP` | In pin config |
| `digitalWrite(pin, HIGH)` | `- output.turn_on: id` | In lambda: `id(out).turn_on()` |
| `digitalWrite(pin, LOW)` | `- output.turn_off: id` | In lambda: `id(out).turn_off()` |
| `digitalRead(pin)` | `id(sensor).state` | Via binary_sensor |

**Arduino:**
```cpp
pinMode(LED_BUILTIN, OUTPUT);
digitalWrite(LED_BUILTIN, HIGH);
```

**ESPHome:**
```yaml
output:
  - platform: gpio
    pin: GPIO2
    id: led_output

# In automation
- output.turn_on: led_output

# In lambda
- lambda: id(led_output).turn_on();
```

### Analog I/O

| Arduino | ESPHome | Notes |
|---------|---------|-------|
| `analogRead(pin)` | `sensor: platform: adc` | ESP32 ADC pins |
| `analogWrite(pin, val)` | `output: platform: ledc` | PWM via LEDC |
| `analogReadResolution()` | `attenuation:` | Configure ADC range |

**Arduino:**
```cpp
int value = analogRead(A0);
analogWrite(LED_PIN, 128);
```

**ESPHome:**
```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Analog Value"
    attenuation: 11db

output:
  - platform: ledc
    pin: GPIO25
    id: pwm_output

# Set to 50%
- output.set_level:
    id: pwm_output
    level: 50%
```

### Timing Functions

| Arduino | ESPHome | Notes |
|---------|---------|-------|
| `delay(ms)` | `- delay: Xms` | In automations |
| `delayMicroseconds(us)` | Lambda with `delayMicroseconds()` | Use sparingly |
| `millis()` | `millis()` | Available in lambdas |
| `micros()` | `micros()` | Available in lambdas |

**Arduino:**
```cpp
delay(1000);
unsigned long start = millis();
```

**ESPHome:**
```yaml
# In automation
- delay: 1s

# In lambda
- lambda: |-
    unsigned long now = millis();
    ESP_LOGD("timing", "Millis: %lu", now);
```

### Serial/Logging

| Arduino | ESPHome | Notes |
|---------|---------|-------|
| `Serial.begin(baud)` | `logger:` | Automatic |
| `Serial.print()` | `ESP_LOGD()` | In lambdas |
| `Serial.println()` | `ESP_LOGI()` | Various levels |
| `Serial.available()` | `uart:` component | For device communication |

**Arduino:**
```cpp
Serial.begin(115200);
Serial.println("Hello World");
Serial.printf("Value: %d\n", value);
```

**ESPHome:**
```yaml
logger:
  level: DEBUG

# In lambda
- lambda: |-
    ESP_LOGD("custom", "Hello World");
    ESP_LOGD("custom", "Value: %d", some_value);
```

### Interrupts and Events

| Arduino | ESPHome | Notes |
|---------|---------|-------|
| `attachInterrupt()` | `on_press:`, `on_value:` | Event-based triggers |
| `detachInterrupt()` | Not needed | Managed automatically |
| ISR functions | Lambda in trigger | Don't block |

**Arduino:**
```cpp
attachInterrupt(digitalPinToInterrupt(2), buttonISR, FALLING);

void buttonISR() {
  buttonPressed = true;
}
```

**ESPHome:**
```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO2
      mode: INPUT_PULLUP
      inverted: true
    on_press:
      - switch.toggle: relay
      - logger.log: "Button pressed!"
```

### Common Libraries

| Arduino Library | ESPHome Component |
|-----------------|-------------------|
| `Wire.h` (I2C) | `i2c:` |
| `SPI.h` | `spi:` |
| `WiFi.h` | `wifi:` |
| `PubSubClient.h` (MQTT) | `mqtt:` |
| `DHT.h` | `sensor: platform: dht` |
| `Adafruit_BME280.h` | `sensor: platform: bme280` |
| `Adafruit_SSD1306.h` | `display: platform: ssd1306_i2c` |
| `FastLED.h` | `light: platform: esp32_rmt_led_strip` |
| `IRremote.h` | `remote_receiver:` / `remote_transmitter:` |
| `Servo.h` | `servo:` |
| `Stepper.h` | `stepper:` |

---

## Lambda and C++ Integration

### Basic Lambda Syntax

```yaml
sensor:
  - platform: template
    name: "Calculated Value"
    lambda: |-
      return id(temp).state * 1.8 + 32;  # Celsius to Fahrenheit
    update_interval: 10s
```

### Accessing Components

**Sensors:**
```yaml
lambda: |-
  float temp = id(temperature_sensor).state;
  if (isnan(temp)) {
    return 0.0;
  }
  return temp;
```

**Switches:**
```yaml
lambda: |-
  if (id(motion_sensor).state) {
    id(relay).turn_on();
  } else {
    id(relay).turn_off();
  }
```

**Lights:**
```yaml
lambda: |-
  auto call = id(led_strip).turn_on();
  call.set_rgb(1.0, 0.0, 0.0);  # Red
  call.set_brightness(0.5);
  call.perform();
```

### Using Globals

```yaml
globals:
  - id: counter
    type: int
    initial_value: '0'
  - id: values
    type: float[10]
    initial_value: '{0}'

# In lambda
lambda: |-
  id(counter) += 1;
  id(values)[id(counter) % 10] = id(sensor).state;
```

### Logging in Lambdas

```yaml
lambda: |-
  ESP_LOGD("custom", "Debug message");
  ESP_LOGI("custom", "Info: %s", "text");
  ESP_LOGW("custom", "Warning: value=%d", value);
  ESP_LOGE("custom", "Error occurred!");
```

### Multi-line Logic

```yaml
lambda: |-
  // Calculate average of last 5 readings
  static float readings[5] = {0};
  static int index = 0;

  readings[index] = id(sensor).state;
  index = (index + 1) % 5;

  float sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += readings[i];
  }

  return sum / 5.0;
```

---

## Communication Protocols

### I2C (Wire.h)

**Arduino:**
```cpp
#include <Wire.h>
Wire.begin(21, 22);
Wire.beginTransmission(0x68);
Wire.write(0x00);
Wire.endTransmission();
```

**ESPHome:**
```yaml
i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true

sensor:
  - platform: bme280_i2c
    address: 0x76
    temperature:
      name: "Temperature"
```

### SPI

**Arduino:**
```cpp
#include <SPI.h>
SPI.begin();
SPI.transfer(data);
```

**ESPHome:**
```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

# Used by SPI-based components
display:
  - platform: ili9341
    cs_pin: GPIO5
    dc_pin: GPIO16
```

### UART (Serial)

**Arduino:**
```cpp
Serial1.begin(9600);
Serial1.write("AT\r\n");
if (Serial1.available()) {
  char c = Serial1.read();
}
```

**ESPHome:**
```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 9600
  id: uart_bus

# For custom communication
- uart.write:
    id: uart_bus
    data: "AT\r\n"
```

---

## Custom Components

### When Lambdas Aren't Enough

Use custom components when:
- Need complex initialization
- Require multiple interacting parts
- Want to share code across projects
- Need to wrap an Arduino library

### Simple Custom Component

**File: `my_sensor.h`**
```cpp
#include "esphome.h"

class MySensor : public PollingComponent, public Sensor {
 public:
  MySensor() : PollingComponent(10000) {}  // 10s interval

  void setup() override {
    // Initialize hardware
  }

  void update() override {
    // Read sensor
    float value = analogRead(34) / 4095.0 * 3.3;
    publish_state(value);
  }
};
```

**YAML:**
```yaml
esphome:
  includes:
    - my_sensor.h

sensor:
  - platform: custom
    lambda: |-
      auto sensor = new MySensor();
      App.register_component(sensor);
      return {sensor};
    sensors:
      - name: "My Custom Sensor"
```

### External Components

For more complex components, use `external_components`:

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/user/esphome-component
    components: [my_component]

# Use the component
my_component:
  pin: GPIO4
```

---

## Migration Examples

### Example 1: Simple Blink

**Arduino:**
```cpp
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}
```

**ESPHome:**
```yaml
output:
  - platform: gpio
    pin: GPIO2
    id: led

interval:
  - interval: 2s
    then:
      - output.turn_on: led
      - delay: 1s
      - output.turn_off: led
```

### Example 2: Temperature Logger with Display

**Arduino (simplified):**
```cpp
#include <DHT.h>
#include <Adafruit_SSD1306.h>

DHT dht(4, DHT22);
Adafruit_SSD1306 display(128, 64, &Wire);

void setup() {
  dht.begin();
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  display.clearDisplay();
  display.setCursor(0, 0);
  display.printf("Temp: %.1f C", temp);
  display.setCursor(0, 20);
  display.printf("Hum: %.1f %%", hum);
  display.display();

  delay(2000);
}
```

**ESPHome:**
```yaml
# Generated by supercharge-esphome-skill v2.3.0
# https://github.com/tonylofgren/supercharge-smart-home-claude-skills

esphome:
  name: temp-logger
  friendly_name: Temperature Logger

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  platform: esphome

logger:

i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22
    temperature:
      name: "Temperature"
      id: temp
    humidity:
      name: "Humidity"
      id: humidity
    update_interval: 2s

font:
  - file: "gfonts://Roboto"
    id: font1
    size: 16

display:
  - platform: ssd1306_i2c
    model: "SSD1306 128x64"
    address: 0x3C
    lambda: |-
      it.printf(0, 0, id(font1), "Temp: %.1f C", id(temp).state);
      it.printf(0, 20, id(font1), "Hum: %.1f %%", id(humidity).state);
```

### Example 3: MQTT Relay Controller

**Arduino (simplified):**
```cpp
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  if (strcmp(topic, "home/relay/set") == 0) {
    if (payload[0] == '1') {
      digitalWrite(12, HIGH);
    } else {
      digitalWrite(12, LOW);
    }
    client.publish("home/relay/state", digitalRead(12) ? "1" : "0");
  }
}

void setup() {
  pinMode(12, OUTPUT);
  WiFi.begin("ssid", "password");
  client.setServer("mqtt.local", 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    client.connect("ESP32Client");
    client.subscribe("home/relay/set");
  }
  client.loop();
}
```

**ESPHome:**
```yaml
# Generated by supercharge-esphome-skill v2.3.0
# https://github.com/tonylofgren/supercharge-smart-home-claude-skills

esphome:
  name: mqtt-relay
  friendly_name: MQTT Relay

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

mqtt:
  broker: mqtt.local
  port: 1883

ota:
  platform: esphome

logger:

switch:
  - platform: gpio
    pin: GPIO12
    name: "Relay"
    id: relay
    command_topic: home/relay/set
    state_topic: home/relay/state
```

### Example 4: IR Remote Hub

**Arduino (simplified):**
```cpp
#include <IRremote.h>

IRrecv irrecv(15);
IRsend irsend(4);

void setup() {
  irrecv.enableIRIn();
}

void loop() {
  if (irrecv.decode()) {
    Serial.printf("Received: %08X\n", irrecv.decodedIRData.decodedRawData);
    irrecv.resume();
  }
}

void sendNEC(uint32_t code) {
  irsend.sendNEC(code, 32);
}
```

**ESPHome:**
```yaml
# Generated by supercharge-esphome-skill v2.3.0
# https://github.com/tonylofgren/supercharge-smart-home-claude-skills

esphome:
  name: ir-hub
  friendly_name: IR Hub

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

ota:
  platform: esphome

logger:

remote_receiver:
  pin: GPIO15
  dump: all

remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%

button:
  - platform: template
    name: "TV Power"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x04
          command: 0x08
```

---

## Common Pitfalls

### 1. Blocking Code

**Problem:** Using `delay()` in lambdas blocks the entire system.

**Arduino habit:**
```cpp
while (!sensor.ready()) {
  delay(10);
}
```

**ESPHome solution:**
```yaml
# Use interval or on_value triggers
interval:
  - interval: 10ms
    then:
      - if:
          condition:
            lambda: return id(sensor).state;
          then:
            - script.execute: process_data
```

### 2. Global State

**Problem:** Directly accessing globals without initialization.

**Wrong:**
```yaml
lambda: return values[counter];  # Undefined behavior
```

**Correct:**
```yaml
globals:
  - id: counter
    type: int
    initial_value: '0'
  - id: values
    type: float[10]
    initial_value: '{0}'

lambda: |-
  return id(values)[id(counter)];
```

### 3. Float Precision

**Problem:** Expecting Arduino float precision.

**ESPHome sensors use single-precision floats:**
```yaml
sensor:
  - platform: template
    accuracy_decimals: 2  # Control display precision
```

### 4. Pin Mapping

**Problem:** Using Arduino pin names instead of GPIO numbers.

**Wrong:** `pin: A0`
**Correct:** `pin: GPIO34` (for ESP32 ADC)

### 5. Timing Expectations

**Problem:** Expecting immediate updates.

ESPHome components have update intervals:
```yaml
sensor:
  - platform: dht
    update_interval: 10s  # Default, not instant

# For more responsive:
    update_interval: 1s
```

### 6. Library Compatibility

**Problem:** Not all Arduino libraries work in ESPHome.

Check:
- Is there an ESPHome component?
- Is there an external component?
- Can the library be wrapped in a custom component?

### 7. Memory Usage

**Problem:** Large arrays and strings.

ESPHome is more memory-constrained than typical Arduino setups:
```yaml
globals:
  - id: buffer
    type: char[256]  # Keep buffers small
```

### 8. Interrupt Handling

**Problem:** Complex interrupt logic.

ESPHome handles interrupts through triggers:
```yaml
binary_sensor:
  - platform: gpio
    pin: GPIO5
    on_press:
      # Don't put complex logic here
      - script.execute: handle_button
```

---

## Quick Reference Card

### Arduino → ESPHome Cheat Sheet

```
pinMode(X, OUTPUT)     → output: platform: gpio, pin: GPIOX
digitalWrite(X, HIGH)  → - output.turn_on: id
digitalWrite(X, LOW)   → - output.turn_off: id
digitalRead(X)         → id(binary_sensor).state
analogRead(X)          → id(adc_sensor).state
analogWrite(X, val)    → output.set_level: id, level: X%
delay(ms)              → - delay: Xms
millis()               → millis()  (in lambda)
Serial.print()         → ESP_LOGD("tag", "msg")
Wire.begin()           → i2c:
SPI.begin()            → spi:
attachInterrupt()      → on_press: / on_value:
```

### Conversion Checklist

- [ ] Identify board type (ESP32/ESP8266)
- [ ] List all sensors and actuators
- [ ] Map Arduino libraries to ESPHome components
- [ ] Convert setup() to component configuration
- [ ] Convert loop() to intervals/triggers
- [ ] Convert globals to `globals:` section
- [ ] Test compilation
- [ ] Verify functionality
- [ ] Add Home Assistant integration
