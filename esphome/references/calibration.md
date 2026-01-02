# Sensor Calibration Guide

Step-by-step calibration procedures for common ESPHome sensors.

## CT Clamp Calibration (SCT-013)

Current transformers require calibration for accurate power readings.

### Equipment Needed
- Known load (e.g., incandescent bulb with known wattage)
- Multimeter (optional, for verification)
- Kill-A-Watt or similar power meter (optional)

### Calibration Steps

```yaml
sensor:
  - platform: ct_clamp
    pin: GPIO36
    name: "Power Meter"
    update_interval: 1s
    filters:
      # Step 1: Start with theoretical calibration factor
      # SCT-013-030 (30A/1V): calibration = 30
      # SCT-013-050 (50A/1V): calibration = 50
      # SCT-013-100 (100A/1V): calibration = 100
      - calibrate_linear:
          - 0.0 -> 0.0
          - 0.033 -> 1.0  # Adjust based on measurements
```

### Calibration Procedure

1. **Determine theoretical factor:**
   ```
   SCT-013-030: 30A max, 1V output
   At 30A: output = 1V RMS = 1.414V peak
   ADC reading at 30A ≈ 0.033 (normalized)
   ```

2. **Connect known load** (e.g., 100W incandescent bulb)
   ```
   100W at 230V = 0.435A
   Expected reading: 100W
   ```

3. **Read raw sensor value** (with `update_interval: 1s`):
   ```yaml
   sensor:
     - platform: ct_clamp
       pin: GPIO36
       name: "CT Raw"
       update_interval: 1s
       # No filters - read raw value
   ```

4. **Calculate correction factor:**
   ```
   correction = actual_power / displayed_power
   If showing 85W for a 100W load: correction = 100/85 = 1.176
   ```

5. **Apply calibration:**
   ```yaml
   filters:
     - multiply: 1.176  # Your correction factor
     - lambda: return x * 230.0;  # Voltage (for power in Watts)
   ```

### Common SCT-013 Variants

| Model | Max Current | Output | Burden Resistor |
|-------|-------------|--------|-----------------|
| SCT-013-000 | 100A | 50mA | Need external (22Ω for 1V) |
| SCT-013-005 | 5A | 1V | Built-in |
| SCT-013-010 | 10A | 1V | Built-in |
| SCT-013-015 | 15A | 1V | Built-in |
| SCT-013-020 | 20A | 1V | Built-in |
| SCT-013-025 | 25A | 1V | Built-in |
| SCT-013-030 | 30A | 1V | Built-in |
| SCT-013-050 | 50A | 1V | Built-in |
| SCT-013-100 | 100A | 1V | Built-in |

---

## Soil Moisture Sensor Calibration

Capacitive soil moisture sensors need wet/dry calibration.

### Calibration Steps

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Soil Moisture"
    update_interval: 60s
    unit_of_measurement: "%"
    filters:
      # Calibration values (measure these!)
      - calibrate_linear:
          - 2.8 -> 0.0    # Dry air value
          - 1.2 -> 100.0  # In water value
      - clamp:
          min_value: 0
          max_value: 100
```

### Procedure

1. **Measure dry value:**
   - Hold sensor in dry air
   - Record ADC voltage (e.g., 2.8V)

2. **Measure wet value:**
   - Place sensor in glass of water (up to marked line only!)
   - Record ADC voltage (e.g., 1.2V)

3. **Apply calibration:**
   - Dry value → 0%
   - Wet value → 100%

### Tips
- Never submerge electronics portion
- Capacitive sensors last longer than resistive
- Different soil types may need recalibration
- Temperature affects readings

---

## Load Cell / Weight Sensor Calibration (HX711)

Precise weight measurement requires careful calibration.

### Configuration

```yaml
sensor:
  - platform: hx711
    name: "Weight"
    dout_pin: GPIO16
    clk_pin: GPIO4
    gain: 128
    update_interval: 1s
    unit_of_measurement: "kg"
    filters:
      - calibrate_linear:
          - -287000 -> 0      # Tare (empty scale)
          - -150000 -> 5.0    # Known weight point
      - sliding_window_moving_average:
          window_size: 5
          send_every: 1
```

### Calibration Procedure

1. **Read raw values:**
   ```yaml
   sensor:
     - platform: hx711
       name: "Weight Raw"
       dout_pin: GPIO16
       clk_pin: GPIO4
       gain: 128
       update_interval: 1s
       # No filters - raw value
   ```

2. **Record empty scale value** (tare):
   - Place nothing on scale
   - Record raw value (e.g., -287000)

3. **Record known weight value:**
   - Place known weight (e.g., 5kg dumbbell)
   - Record raw value (e.g., -150000)

4. **Calculate and apply:**
   ```yaml
   filters:
     - calibrate_linear:
         - -287000 -> 0.0   # Empty
         - -150000 -> 5.0   # 5kg reference
   ```

### Multi-Point Calibration

For better accuracy across the range:

```yaml
filters:
  - calibrate_polynomial:
      degree: 2
      datapoints:
        - -287000 -> 0.0
        - -218500 -> 2.5
        - -150000 -> 5.0
        - -81500 -> 7.5
        - -13000 -> 10.0
```

### Load Cell Wiring (4-wire)

| Wire Color | Connection |
|------------|------------|
| Red | E+ (Excitation+) |
| Black | E- (Excitation-) |
| White | A- (Signal-) |
| Green | A+ (Signal+) |

Some variations exist - check your cell's datasheet.

---

## Temperature Sensor Offset Calibration

### NTC Thermistor

```yaml
sensor:
  - platform: ntc
    sensor: temp_resistance
    name: "Temperature"
    calibration:
      b_constant: 3950
      reference_temperature: 25°C
      reference_resistance: 10kOhm
    filters:
      - offset: -1.5  # Calibration offset in °C

  - platform: resistance
    id: temp_resistance
    sensor: temp_adc
    configuration: DOWNSTREAM
    resistor: 10kOhm

  - platform: adc
    id: temp_adc
    pin: GPIO34
    attenuation: 11db
```

### Dallas DS18B20

```yaml
sensor:
  - platform: dallas_temp
    address: 0x1234567890ABCDEF
    name: "Temperature"
    filters:
      - offset: -0.8  # Measured offset
```

### Calibration Method

1. **Reference measurement:**
   - Use calibrated thermometer or ice bath (0°C) / boiling water (100°C adjusted for altitude)

2. **Record offset:**
   ```
   offset = reference_temp - sensor_temp
   If sensor shows 21.5°C and reference is 20.0°C:
   offset = 20.0 - 21.5 = -1.5
   ```

3. **Apply filter:**
   ```yaml
   filters:
     - offset: -1.5
   ```

---

## ADC Voltage Divider Calculation

For measuring voltages above 3.3V (ESP32 ADC max).

### Voltage Divider Formula

```
         Vin
          |
         [R1]
          |──── Vout (to GPIO)
         [R2]
          |
         GND

Vout = Vin × (R2 / (R1 + R2))
```

### Common Configurations

**12V Battery Monitoring:**
```
R1 = 100kΩ, R2 = 27kΩ
Vout = 12V × (27k / 127k) = 2.55V ✓ (under 3.3V)
```

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Battery Voltage"
    attenuation: 11db
    filters:
      - multiply: 4.704  # (R1 + R2) / R2 = 127/27
```

**24V System:**
```
R1 = 100kΩ, R2 = 15kΩ
Vout = 24V × (15k / 115k) = 3.13V ✓
```

```yaml
filters:
  - multiply: 7.667  # 115/15
```

### ESP32 ADC Attenuation

| Attenuation | Voltage Range | Accuracy |
|-------------|---------------|----------|
| 0db | 0 - 1.1V | Best |
| 2.5db | 0 - 1.5V | Good |
| 6db | 0 - 2.2V | OK |
| 11db | 0 - 3.3V | Lower |

Use lowest attenuation that covers your range.

---

## Ultrasonic Distance Calibration

For tank level or distance measurement with HC-SR04.

```yaml
sensor:
  - platform: ultrasonic
    trigger_pin: GPIO5
    echo_pin: GPIO18
    name: "Tank Level"
    update_interval: 60s
    filters:
      # Convert distance to percentage
      - lambda: |-
          // Tank dimensions (in meters)
          const float empty_distance = 1.5;  // Sensor to bottom
          const float full_distance = 0.1;   // Sensor to full level

          // Calculate percentage
          float level = (empty_distance - x) / (empty_distance - full_distance) * 100.0;
          return clamp(level, 0.0f, 100.0f);
    unit_of_measurement: "%"
```

### Calibration

1. **Measure empty distance** (sensor to bottom of empty tank)
2. **Measure full distance** (sensor to water surface when full)
3. **Temperature compensation** (optional, sound speed varies):
   ```yaml
   # Speed of sound: ~331 + 0.6 × temperature (m/s)
   - lambda: |-
       float temp = id(temperature_sensor).state;
       float speed_factor = (331.0 + 0.6 * temp) / 343.0;
       return x * speed_factor;
   ```

---

## Filter Reference

Common filters for sensor calibration:

```yaml
filters:
  # Linear offset
  - offset: 1.5

  # Multiplication factor
  - multiply: 0.95

  # Two-point linear calibration
  - calibrate_linear:
      - 0.0 -> 0.0
      - 1.0 -> 100.0

  # Multi-point polynomial
  - calibrate_polynomial:
      degree: 2
      datapoints:
        - 0.0 -> 0.0
        - 0.5 -> 45.0
        - 1.0 -> 100.0

  # Clamp to range
  - clamp:
      min_value: 0
      max_value: 100

  # Moving average (smoothing)
  - sliding_window_moving_average:
      window_size: 10
      send_every: 1

  # Exponential smoothing
  - exponential_moving_average:
      alpha: 0.1
      send_every: 1

  # Delta filter (only send on change)
  - delta: 0.5

  # Throttle updates
  - throttle: 10s

  # Heartbeat (send at interval even if unchanged)
  - heartbeat: 60s

  # Lambda for custom logic
  - lambda: return x * 1.05 + 0.2;
```

---

## See Also

- [sensors.md](sensors.md) - Sensor platform reference
- [troubleshooting-flowcharts.md](troubleshooting-flowcharts.md) - Debug sensor issues
- [pinouts.md](pinouts.md) - ADC-capable pins
