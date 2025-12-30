# ESPHome Sensor Reference

## Table of Contents
- [Common Sensor Options](#common-sensor-options)
- [Environmental Sensors](#environmental-sensors)
- [Air Quality Sensors](#air-quality-sensors)
- [Power & Energy Sensors](#power--energy-sensors)
- [Distance & Presence Sensors](#distance--presence-sensors)
- [Light Sensors](#light-sensors)
- [Wireless/BLE Sensors](#wirelessble-sensors)
- [Template & Computed Sensors](#template--computed-sensors)
- [System Sensors](#system-sensors)

---

## Common Sensor Options

All sensors share these base options:

```yaml
sensor:
  - platform: <platform_name>
    name: "Sensor Name"              # Required: HA entity name
    id: sensor_id                    # Optional: Internal ID for references
    unit_of_measurement: "unit"      # Optional: Override unit
    accuracy_decimals: 2             # Optional: Decimal places
    device_class: temperature        # Optional: HA device class
    state_class: measurement         # Optional: measurement|total|total_increasing
    icon: "mdi:thermometer"          # Optional: MDI icon
    entity_category: diagnostic      # Optional: diagnostic|config
    update_interval: 60s             # Optional: Read frequency
    filters:                         # Optional: Value transformations
      - multiply: 0.001
      - offset: -10
      - lambda: return x * 2;
```

### Common Filters

```yaml
filters:
  - offset: 2.0                      # Add constant
  - multiply: 1.2                    # Multiply by factor
  - calibrate_linear:                # Linear calibration
      - 0.0 -> 0.0
      - 100.0 -> 102.5
  - median:                          # Median of last N values
      window_size: 5
      send_every: 5
  - sliding_window_moving_average:   # Moving average
      window_size: 15
      send_every: 15
  - exponential_moving_average:      # EMA filter
      alpha: 0.1
      send_every: 15
  - throttle: 1min                   # Max one update per period
  - delta: 0.5                       # Only send if changed by >= value
  - clamp:                           # Limit range
      min_value: 0
      max_value: 100
  - lambda: return x > 0 ? x : 0;    # Custom logic
```

---

## Environmental Sensors

### DHT (DHT11, DHT22, AM2302)
Temperature and humidity sensor.

```yaml
sensor:
  - platform: dht
    pin: GPIO4
    model: DHT22  # DHT11, DHT22, AM2302, RHT03, SI7021
    temperature:
      name: "Temperature"
      accuracy_decimals: 1
    humidity:
      name: "Humidity"
    update_interval: 30s
```

### BME280 / BMP280 (I2C)
Temperature, humidity, pressure sensor.

```yaml
i2c:
  sda: GPIO21
  scl: GPIO22

sensor:
  - platform: bme280_i2c
    address: 0x76  # or 0x77
    temperature:
      name: "Temperature"
      oversampling: 16x
    pressure:
      name: "Pressure"
    humidity:
      name: "Humidity"
    update_interval: 60s
```

### BME680 (I2C)
Air quality sensor with temperature, humidity, pressure, gas resistance.

```yaml
sensor:
  - platform: bme680
    address: 0x77
    temperature:
      name: "Temperature"
    pressure:
      name: "Pressure"
    humidity:
      name: "Humidity"
    gas_resistance:
      name: "Gas Resistance"
    update_interval: 60s
```

### SHT3X-D / SHT4X (I2C)
High-precision temperature and humidity.

```yaml
sensor:
  - platform: sht3xd
    address: 0x44
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 60s

  # SHT4X variant
  - platform: sht4x
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    precision: High  # Low, Medium, High
```

### AHT10 / AHT20 (I2C)
Budget temperature and humidity sensor.

```yaml
sensor:
  - platform: aht10
    variant: AHT20  # AHT10 or AHT20
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 60s
```

### Dallas DS18B20 (1-Wire)
Waterproof temperature sensor.

```yaml
one_wire:
  - platform: gpio
    pin: GPIO4

sensor:
  - platform: dallas_temp
    address: 0x1234567890ABCDEF  # Use dallas_temp scan to find
    name: "Water Temperature"
    resolution: 12  # 9-12 bits
```

### NTC Thermistor (Analog)
Temperature from resistance.

```yaml
sensor:
  - platform: ntc
    sensor: resistance_sensor
    calibration:
      b_constant: 3950
      reference_temperature: 25C
      reference_resistance: 10kOhm
    name: "NTC Temperature"

  - platform: resistance
    id: resistance_sensor
    sensor: adc_sensor
    configuration: DOWNSTREAM
    resistor: 10kOhm

  - platform: adc
    id: adc_sensor
    pin: GPIO34
    attenuation: 11db
```

---

## Air Quality Sensors

### SCD30 / SCD40 / SCD41 (CO2)
NDIR CO2 sensor with temperature and humidity.

```yaml
sensor:
  - platform: scd4x
    co2:
      name: "CO2"
    temperature:
      name: "Temperature"
    humidity:
      name: "Humidity"
    update_interval: 30s
```

### MH-Z19 (CO2)
NDIR CO2 sensor via UART.

```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 9600

sensor:
  - platform: mhz19
    co2:
      name: "CO2"
    temperature:
      name: "MH-Z19 Temperature"
    update_interval: 60s
    automatic_baseline_calibration: false
```

### SGP30 / SGP40 (VOC)
VOC and eCO2 sensor.

```yaml
sensor:
  - platform: sgp30
    eco2:
      name: "eCO2"
    tvoc:
      name: "TVOC"
    compensation:
      temperature_source: temp_sensor
      humidity_source: humidity_sensor
```

### PMSX003 (Particulate Matter)
PM1.0, PM2.5, PM10 sensor.

```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 9600

sensor:
  - platform: pmsx003
    type: PMSX003
    pm_1_0:
      name: "PM 1.0"
    pm_2_5:
      name: "PM 2.5"
    pm_10_0:
      name: "PM 10.0"
```

### SDS011 (Particulate Matter)
PM2.5, PM10 sensor.

```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 9600

sensor:
  - platform: sds011
    pm_2_5:
      name: "PM 2.5"
    pm_10_0:
      name: "PM 10.0"
    update_interval: 5min
```

### SPS30 (Particulate Matter)
High-precision PM sensor via I2C or UART.

```yaml
sensor:
  - platform: sps30
    pm_1_0:
      name: "PM 1.0"
    pm_2_5:
      name: "PM 2.5"
    pm_4_0:
      name: "PM 4.0"
    pm_10_0:
      name: "PM 10.0"
    pmc_0_5:
      name: "PMC 0.5"
    pm_size:
      name: "PM Size"
```

---

## Power & Energy Sensors

### ADC (Analog to Digital)
Read analog voltage.

```yaml
sensor:
  - platform: adc
    pin: GPIO34
    name: "Voltage"
    attenuation: 12db  # 0db, 2.5db, 6db, 11db, 12db, auto
    update_interval: 1s
    filters:
      - multiply: 3.3  # Voltage divider compensation
```

### Pulse Meter
High-resolution pulse counting for energy meters.

```yaml
sensor:
  - platform: pulse_meter
    pin: GPIO5
    name: "Power"
    unit_of_measurement: "W"
    device_class: power
    state_class: measurement
    internal_filter: 20ms
    filters:
      - multiply: 60  # 1000 pulses/kWh
    total:
      name: "Total Energy"
      unit_of_measurement: "kWh"
      device_class: energy
      state_class: total_increasing
      filters:
        - multiply: 0.001  # Convert to kWh
```

### Pulse Counter
Count pulses in fixed intervals.

```yaml
sensor:
  - platform: pulse_counter
    pin: GPIO5
    name: "Pulse Rate"
    unit_of_measurement: "pulses/min"
    count_mode:
      rising_edge: INCREMENT
      falling_edge: DISABLE
    internal_filter: 13us
```

### INA219 / INA226 / INA3221 (I2C Power Monitor)
Current, voltage, power measurement.

```yaml
sensor:
  - platform: ina219
    address: 0x40
    shunt_resistance: 0.1 ohm
    current:
      name: "Current"
    power:
      name: "Power"
    bus_voltage:
      name: "Bus Voltage"
    shunt_voltage:
      name: "Shunt Voltage"
    max_current: 3.2A
    max_voltage: 26V
```

### HLW8012 / CSE7766 / BL0942
AC power monitoring chips (common in Sonoff POW).

```yaml
sensor:
  - platform: hlw8012
    sel_pin: GPIO12
    cf_pin: GPIO5
    cf1_pin: GPIO14
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    energy:
      name: "Energy"
    current_resistor: 0.001 ohm
    voltage_divider: 2351
```

### PZEM-004T v3
AC power monitoring via Modbus.

```yaml
uart:
  rx_pin: GPIO16
  tx_pin: GPIO17
  baud_rate: 9600

sensor:
  - platform: pzemac
    current:
      name: "Current"
    voltage:
      name: "Voltage"
    power:
      name: "Power"
    frequency:
      name: "Frequency"
    power_factor:
      name: "Power Factor"
    energy:
      name: "Energy"
```

### ADE7953 (Shelly power chip)
Dual channel power monitoring.

```yaml
sensor:
  - platform: ade7953_i2c
    irq_pin: GPIO16
    voltage:
      name: "Voltage"
    current_a:
      name: "Current A"
    current_b:
      name: "Current B"
    power_a:
      name: "Power A"
    power_b:
      name: "Power B"
    energy_a:
      name: "Energy A"
    energy_b:
      name: "Energy B"
```

---

## Distance & Presence Sensors

### Ultrasonic (HC-SR04, JSN-SR04T)
Distance measurement.

```yaml
sensor:
  - platform: ultrasonic
    trigger_pin: GPIO12
    echo_pin: GPIO13
    name: "Distance"
    timeout: 3m
    update_interval: 1s
    filters:
      - filter_out: nan
```

### VL53L0X / VL53L1X (I2C Laser)
Time-of-flight distance sensor.

```yaml
sensor:
  - platform: vl53l0x
    address: 0x29
    name: "Distance"
    update_interval: 500ms
    long_range: true
    # For VL53L1X:
    # timing_budget: 200ms  # Accuracy vs speed
```

### LD2410 (mmWave Radar Presence)
Human presence detection via UART.

```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 256000

ld2410:
  id: ld2410_radar

binary_sensor:
  - platform: ld2410
    has_target:
      name: "Presence"
    has_moving_target:
      name: "Moving Target"
    has_still_target:
      name: "Still Target"

sensor:
  - platform: ld2410
    moving_distance:
      name: "Moving Distance"
    still_distance:
      name: "Still Distance"
    detection_distance:
      name: "Detection Distance"
```

### LD2450 (mmWave Radar Multi-target)
Multi-target tracking radar.

```yaml
uart:
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 256000

ld2450:
  id: ld2450_radar
  throttle: 1000ms

sensor:
  - platform: ld2450
    target_count:
      name: "Target Count"
    target_1:
      x:
        name: "Target 1 X"
      y:
        name: "Target 1 Y"
      speed:
        name: "Target 1 Speed"
      resolution:
        name: "Target 1 Resolution"
```

### PIR (Passive Infrared)
Motion detection (see binary_sensors).

---

## Light Sensors

### BH1750 (I2C Lux Sensor)
Ambient light sensor.

```yaml
sensor:
  - platform: bh1750
    address: 0x23
    name: "Illuminance"
    update_interval: 5s
    resolution: 1.0  # 0.5, 1.0, 4.0
```

### TSL2561 / TSL2591 (I2C Lux Sensor)
High-dynamic range light sensor.

```yaml
sensor:
  - platform: tsl2561
    address: 0x39
    name: "Illuminance"
    gain: 1x  # 1x, 16x
    integration_time: 402ms  # 14ms, 101ms, 402ms
```

### VEML7700 (I2C Lux Sensor)
High accuracy ambient light sensor.

```yaml
sensor:
  - platform: veml7700
    address: 0x10
    ambient_light:
      name: "Ambient Light"
    full_spectrum:
      name: "Full Spectrum"
    infrared:
      name: "Infrared"
```

### TCS34725 (I2C Color Sensor)
RGB color sensor.

```yaml
sensor:
  - platform: tcs34725
    address: 0x29
    red_channel:
      name: "Red"
    green_channel:
      name: "Green"
    blue_channel:
      name: "Blue"
    clear_channel:
      name: "Clear"
    illuminance:
      name: "Illuminance"
    color_temperature:
      name: "Color Temperature"
    integration_time: 700ms
    gain: 60x
```

---

## Wireless/BLE Sensors

### Xiaomi Mijia (BLE)
Temperature and humidity beacons.

```yaml
esp32_ble_tracker:

sensor:
  - platform: xiaomi_lywsdcgq
    mac_address: "XX:XX:XX:XX:XX:XX"
    temperature:
      name: "Xiaomi Temperature"
    humidity:
      name: "Xiaomi Humidity"
    battery_level:
      name: "Xiaomi Battery"
```

### RuuviTag (BLE)
Environmental sensor beacon.

```yaml
esp32_ble_tracker:

sensor:
  - platform: ruuvitag
    mac_address: "XX:XX:XX:XX:XX:XX"
    temperature:
      name: "RuuviTag Temperature"
    humidity:
      name: "RuuviTag Humidity"
    pressure:
      name: "RuuviTag Pressure"
    acceleration_x:
      name: "RuuviTag Acceleration X"
    battery_voltage:
      name: "RuuviTag Battery"
```

### Inkbird IBS-TH1/TH2 (BLE)
Temperature and humidity.

```yaml
esp32_ble_tracker:

sensor:
  - platform: inkbird_ibsth1_mini
    mac_address: "XX:XX:XX:XX:XX:XX"
    temperature:
      name: "Inkbird Temperature"
    humidity:
      name: "Inkbird Humidity"
    battery_level:
      name: "Inkbird Battery"
```

### ATC MiThermometer (BLE)
Custom firmware for Xiaomi sensors.

```yaml
esp32_ble_tracker:

sensor:
  - platform: atc_mithermometer
    mac_address: "XX:XX:XX:XX:XX:XX"
    temperature:
      name: "ATC Temperature"
    humidity:
      name: "ATC Humidity"
    battery_level:
      name: "ATC Battery"
    battery_voltage:
      name: "ATC Battery Voltage"
```

---

## Template & Computed Sensors

### Template Sensor
Computed values from other sensors.

```yaml
sensor:
  - platform: template
    name: "Dew Point"
    id: dew_point
    unit_of_measurement: "C"
    device_class: temperature
    lambda: |-
      float temp = id(temperature_sensor).state;
      float hum = id(humidity_sensor).state;
      float a = 17.27;
      float b = 237.7;
      float alpha = ((a * temp) / (b + temp)) + log(hum / 100.0);
      return (b * alpha) / (a - alpha);
    update_interval: 60s
```

### Copy Sensor
Transform another sensor's value.

```yaml
sensor:
  - platform: copy
    source_id: raw_temperature
    name: "Calibrated Temperature"
    filters:
      - offset: -2.5
      - multiply: 1.05
```

### Combination Sensor
Combine multiple sensors.

```yaml
sensor:
  - platform: combination
    type: mean  # mean, median, min, max, sum, range
    name: "Average Temperature"
    sources:
      - source: temp1
      - source: temp2
      - source: temp3
```

### MQTT Subscribe
Read values from MQTT.

```yaml
sensor:
  - platform: mqtt_subscribe
    name: "External Temperature"
    topic: sensors/external/temperature
    qos: 1
    accuracy_decimals: 1
```

---

## System Sensors

### WiFi Signal
Connection strength.

```yaml
sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s

  # Percentage version
  - platform: copy
    source_id: wifi_signal_db
    name: "WiFi Signal %"
    filters:
      - lambda: return min(max(2 * (x + 100.0), 0.0), 100.0);
    unit_of_measurement: "%"
```

### Uptime
Device uptime.

```yaml
sensor:
  - platform: uptime
    name: "Uptime"

text_sensor:
  - platform: uptime
    name: "Uptime Human Readable"
```

### Internal Temperature (ESP32)
Chip temperature.

```yaml
sensor:
  - platform: internal_temperature
    name: "ESP32 Temperature"
```

### Debug Sensors
Memory and loop time.

```yaml
debug:
  update_interval: 5s

sensor:
  - platform: debug
    free:
      name: "Free Heap"
    loop_time:
      name: "Loop Time"
```

---

## Quick Reference: Device Classes

| Device Class | Unit | Description |
|-------------|------|-------------|
| temperature | C, F | Temperature |
| humidity | % | Relative humidity |
| pressure | hPa, mbar | Atmospheric pressure |
| illuminance | lx | Light level |
| battery | % | Battery level |
| power | W | Power consumption |
| energy | kWh, Wh | Energy usage |
| voltage | V | Voltage |
| current | A | Current |
| signal_strength | dBm | Signal strength |
| distance | m, cm | Distance |
| pm25 | ug/m3 | PM2.5 |
| pm10 | ug/m3 | PM10 |
| co2 | ppm | CO2 concentration |
| carbon_monoxide | ppm | CO concentration |
| volatile_organic_compounds | ppb | VOC level |

---

## Quick Reference: State Classes

| State Class | Use Case |
|------------|----------|
| measurement | Instantaneous value (temperature, power) |
| total | Cumulative value that can reset (rain today) |
| total_increasing | Always increasing (energy, gas usage) |
