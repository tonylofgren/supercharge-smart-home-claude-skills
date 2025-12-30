# Device Classes and Units Reference

> Complete mapping of device classes to valid units for Home Assistant 2024/2025

## Overview

Device classes define what type of data a sensor represents. Starting with Home Assistant 2024.2, strict validation requires matching device classes with appropriate units of measurement. This guide provides complete mappings and validation rules.

---

## Sensor Device Classes

### Temperature

```yaml
device_class: temperature
state_class: measurement
valid_units:
  - "°C"    # Celsius (preferred SI)
  - "°F"    # Fahrenheit
  - "K"     # Kelvin
```

Example template sensor:
```yaml
template:
  - sensor:
      - name: "Average Temperature"
        device_class: temperature
        unit_of_measurement: "°C"
        state_class: measurement
        state: >
          {{ states('sensor.temp_1') | float(0) +
             states('sensor.temp_2') | float(0) / 2 | round(1) }}
```

### Humidity

```yaml
device_class: humidity
state_class: measurement
valid_units:
  - "%"     # Percentage (only valid unit)
```

### Pressure

```yaml
device_class: pressure
state_class: measurement
valid_units:
  - "Pa"    # Pascal
  - "hPa"   # Hectopascal (preferred for weather)
  - "kPa"   # Kilopascal
  - "bar"   # Bar
  - "mbar"  # Millibar
  - "mmHg"  # Millimeters of mercury
  - "inHg"  # Inches of mercury
  - "psi"   # Pounds per square inch
  - "cbar"  # Centibar
```

### Power

```yaml
device_class: power
state_class: measurement
valid_units:
  - "W"     # Watt (preferred)
  - "kW"    # Kilowatt
  - "MW"    # Megawatt
  - "BTU/h" # BTU per hour
```

### Energy

```yaml
device_class: energy
state_class: total_increasing  # Important: use total_increasing for meters
valid_units:
  - "Wh"    # Watt-hour
  - "kWh"   # Kilowatt-hour (preferred)
  - "MWh"   # Megawatt-hour
  - "GWh"   # Gigawatt-hour
  - "GJ"    # Gigajoule
  - "MJ"    # Megajoule
```

### Voltage

```yaml
device_class: voltage
state_class: measurement
valid_units:
  - "V"     # Volt (preferred)
  - "mV"    # Millivolt
  - "µV"    # Microvolt
```

### Current

```yaml
device_class: current
state_class: measurement
valid_units:
  - "A"     # Ampere (preferred)
  - "mA"    # Milliampere
```

### Frequency

```yaml
device_class: frequency
state_class: measurement
valid_units:
  - "Hz"    # Hertz (preferred)
  - "kHz"   # Kilohertz
  - "MHz"   # Megahertz
  - "GHz"   # Gigahertz
```

### Battery

```yaml
device_class: battery
state_class: measurement
valid_units:
  - "%"     # Percentage (only valid unit)
```

### Illuminance

```yaml
device_class: illuminance
state_class: measurement
valid_units:
  - "lx"    # Lux (preferred)
  - "lm"    # Lumen
```

### Signal Strength

```yaml
device_class: signal_strength
state_class: measurement
valid_units:
  - "dB"    # Decibel
  - "dBm"   # Decibel-milliwatts (preferred for WiFi)
```

### Distance

```yaml
device_class: distance
state_class: measurement
valid_units:
  - "km"    # Kilometer
  - "m"     # Meter (preferred)
  - "cm"    # Centimeter
  - "mm"    # Millimeter
  - "mi"    # Mile
  - "yd"    # Yard
  - "ft"    # Foot
  - "in"    # Inch
```

### Speed

```yaml
device_class: speed
state_class: measurement
valid_units:
  - "m/s"   # Meters per second (preferred SI)
  - "km/h"  # Kilometers per hour
  - "mph"   # Miles per hour
  - "kn"    # Knots
  - "ft/s"  # Feet per second
  - "mm/d"  # Millimeters per day (precipitation)
  - "in/d"  # Inches per day
  - "in/h"  # Inches per hour
```

### Volume

```yaml
device_class: volume
state_class: measurement  # or total_increasing for meters
valid_units:
  - "L"     # Liter (preferred)
  - "mL"    # Milliliter
  - "m³"    # Cubic meter
  - "ft³"   # Cubic foot
  - "gal"   # Gallon (US)
  - "fl. oz." # Fluid ounce
  - "CCF"   # Centum cubic feet
```

### Volume Flow Rate

```yaml
device_class: volume_flow_rate
state_class: measurement
valid_units:
  - "L/min"   # Liters per minute
  - "L/h"     # Liters per hour
  - "m³/h"    # Cubic meters per hour
  - "ft³/min" # Cubic feet per minute
  - "gal/min" # Gallons per minute
```

### Weight / Mass

```yaml
device_class: weight
state_class: measurement
valid_units:
  - "kg"    # Kilogram (preferred)
  - "g"     # Gram
  - "mg"    # Milligram
  - "µg"    # Microgram
  - "lb"    # Pound
  - "oz"    # Ounce
  - "st"    # Stone
```

### Gas

```yaml
device_class: gas
state_class: total_increasing
valid_units:
  - "m³"    # Cubic meter (preferred)
  - "ft³"   # Cubic foot
  - "CCF"   # Centum cubic feet
```

### Water

```yaml
device_class: water
state_class: total_increasing
valid_units:
  - "L"     # Liter (preferred)
  - "m³"    # Cubic meter
  - "gal"   # Gallon
  - "ft³"   # Cubic foot
  - "CCF"   # Centum cubic feet
```

### Carbon Dioxide (CO2)

```yaml
device_class: carbon_dioxide
state_class: measurement
valid_units:
  - "ppm"   # Parts per million (only valid unit)
```

### Carbon Monoxide (CO)

```yaml
device_class: carbon_monoxide
state_class: measurement
valid_units:
  - "ppm"   # Parts per million (only valid unit)
```

### Volatile Organic Compounds

```yaml
device_class: volatile_organic_compounds
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (preferred)
  - "mg/m³" # Milligrams per cubic meter
  - "ppm"   # Parts per million
  - "ppb"   # Parts per billion
```

### PM1

```yaml
device_class: pm1
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (only valid unit)
```

### PM2.5

```yaml
device_class: pm25
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (only valid unit)
```

### PM10

```yaml
device_class: pm10
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (only valid unit)
```

### AQI (Air Quality Index)

```yaml
device_class: aqi
state_class: measurement
valid_units:
  - null    # No unit (dimensionless index)
```

### Nitrogen Dioxide

```yaml
device_class: nitrogen_dioxide
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (only valid unit)
```

### Ozone

```yaml
device_class: ozone
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (only valid unit)
```

### Sulphur Dioxide

```yaml
device_class: sulphur_dioxide
state_class: measurement
valid_units:
  - "µg/m³" # Micrograms per cubic meter (only valid unit)
```

### Sound Pressure

```yaml
device_class: sound_pressure
state_class: measurement
valid_units:
  - "dB"    # Decibel
  - "dBA"   # A-weighted decibel (preferred for environmental)
```

### Duration

```yaml
device_class: duration
state_class: measurement  # or total_increasing
valid_units:
  - "d"     # Days
  - "h"     # Hours
  - "min"   # Minutes
  - "s"     # Seconds
  - "ms"    # Milliseconds
```

### Monetary

```yaml
device_class: monetary
state_class: total  # or total_increasing
valid_units:
  # Any valid ISO 4217 currency code
  - "USD"   # US Dollar
  - "EUR"   # Euro
  - "GBP"   # British Pound
  - "SEK"   # Swedish Krona
  - "NOK"   # Norwegian Krone
  - "DKK"   # Danish Krone
  # etc.
```

### Data Size

```yaml
device_class: data_size
state_class: measurement  # or total_increasing
valid_units:
  - "bit"   # Bit
  - "kbit"  # Kilobit
  - "Mbit"  # Megabit
  - "Gbit"  # Gigabit
  - "B"     # Byte
  - "kB"    # Kilobyte
  - "MB"    # Megabyte
  - "GB"    # Gigabyte
  - "TB"    # Terabyte
  - "PB"    # Petabyte
  - "EB"    # Exabyte
  - "ZB"    # Zettabyte
  - "YB"    # Yottabyte
  - "KiB"   # Kibibyte
  - "MiB"   # Mebibyte
  - "GiB"   # Gibibyte
  - "TiB"   # Tebibyte
  - "PiB"   # Pebibyte
  - "EiB"   # Exbibyte
  - "ZiB"   # Zebibyte
  - "YiB"   # Yobibyte
```

### Data Rate

```yaml
device_class: data_rate
state_class: measurement
valid_units:
  - "bit/s"   # Bits per second
  - "kbit/s"  # Kilobits per second
  - "Mbit/s"  # Megabits per second
  - "Gbit/s"  # Gigabits per second
  - "B/s"     # Bytes per second
  - "kB/s"    # Kilobytes per second
  - "MB/s"    # Megabytes per second
  - "GB/s"    # Gigabytes per second
  - "KiB/s"   # Kibibytes per second
  - "MiB/s"   # Mebibytes per second
  - "GiB/s"   # Gibibytes per second
```

### Precipitation

```yaml
device_class: precipitation
state_class: measurement
valid_units:
  - "mm"    # Millimeter (preferred)
  - "cm"    # Centimeter
  - "in"    # Inch
```

### Precipitation Intensity

```yaml
device_class: precipitation_intensity
state_class: measurement
valid_units:
  - "mm/h"  # Millimeters per hour (preferred)
  - "mm/d"  # Millimeters per day
  - "in/h"  # Inches per hour
  - "in/d"  # Inches per day
```

### Wind Speed

```yaml
device_class: wind_speed
state_class: measurement
valid_units:
  - "m/s"   # Meters per second (preferred SI)
  - "km/h"  # Kilometers per hour
  - "mph"   # Miles per hour
  - "kn"    # Knots
  - "ft/s"  # Feet per second
  - "Beaufort" # Beaufort scale
```

### Irradiance

```yaml
device_class: irradiance
state_class: measurement
valid_units:
  - "W/m²"  # Watts per square meter (preferred)
  - "BTU/(h⋅ft²)" # BTU per hour per square foot
```

### pH

```yaml
device_class: ph
state_class: measurement
valid_units:
  - null    # No unit (dimensionless)
```

### Power Factor

```yaml
device_class: power_factor
state_class: measurement
valid_units:
  - "%"     # Percentage
  - null    # Dimensionless (0-1)
```

### Reactive Power

```yaml
device_class: reactive_power
state_class: measurement
valid_units:
  - "var"   # Volt-ampere reactive (preferred)
```

### Apparent Power

```yaml
device_class: apparent_power
state_class: measurement
valid_units:
  - "VA"    # Volt-ampere (preferred)
```

---

## Binary Sensor Device Classes

Binary sensors have device classes but no units:

```yaml
device_class:
  - battery         # Low battery
  - battery_charging # Charging status
  - carbon_monoxide # CO detected
  - cold            # Cold detected
  - connectivity    # Connected/disconnected
  - door            # Door open/closed
  - garage_door     # Garage door open/closed
  - gas             # Gas detected
  - heat            # Heat detected
  - light           # Light detected
  - lock            # Locked/unlocked
  - moisture        # Moisture detected
  - motion          # Motion detected
  - moving          # Moving/not moving
  - occupancy       # Occupied/not occupied
  - opening         # Opening detected
  - plug            # Plugged in/unplugged
  - power           # Power on/off
  - presence        # Present/not present
  - problem         # Problem detected
  - running         # Running/not running
  - safety          # Safe/unsafe
  - smoke           # Smoke detected
  - sound           # Sound detected
  - tamper          # Tampering detected
  - update          # Update available
  - vibration       # Vibration detected
  - window          # Window open/closed
```

---

## State Classes

State classes define how the sensor state should be interpreted:

| State Class | Description | Use Case |
|-------------|-------------|----------|
| `measurement` | Instantaneous value | Temperature, power, humidity |
| `total` | Statistically accumulated value | Total energy, total runtime |
| `total_increasing` | Monotonically increasing total | Meter readings, counters |

### Choosing State Class

```yaml
# Instantaneous measurement
template:
  - sensor:
      - name: "Current Power"
        device_class: power
        state_class: measurement  # Current reading
        unit_of_measurement: "W"
        state: "{{ states('sensor.power') }}"

# Meter reading (always increases)
template:
  - sensor:
      - name: "Energy Meter"
        device_class: energy
        state_class: total_increasing  # Cumulative meter
        unit_of_measurement: "kWh"
        state: "{{ states('sensor.energy_meter') }}"

# Accumulated total (can reset)
template:
  - sensor:
      - name: "Daily Energy"
        device_class: energy
        state_class: total  # Can reset at midnight
        unit_of_measurement: "kWh"
        state: "{{ states('sensor.daily_energy') }}"
```

---

## Validation Rules (2024.2+)

### Strict Validation

Starting with Home Assistant 2024.2, sensors with device classes must use valid units:

```yaml
# VALID - matching device_class and unit
template:
  - sensor:
      - name: "Temperature"
        device_class: temperature
        unit_of_measurement: "°C"
        state: "{{ states('sensor.temp') }}"

# INVALID - mismatched unit (will show warning)
template:
  - sensor:
      - name: "Temperature"
        device_class: temperature
        unit_of_measurement: "degrees"  # Wrong! Use °C, °F, or K
        state: "{{ states('sensor.temp') }}"
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid unit` | Unit doesn't match device_class | Use valid unit from mapping |
| `Missing state_class` | Energy integration requires state_class | Add `state_class: total_increasing` |
| `Invalid device_class` | Typo or deprecated class | Check valid device classes |

### Error Examples and Fixes

```yaml
# Error: "sensor.power has device_class power but has wrong unit kWh"
# Fix: kWh is for energy, not power
- name: "Power Usage"
  device_class: power
  unit_of_measurement: "W"  # Correct: Watts for power
  state: "{{ states('sensor.power') }}"

# Error: "sensor.energy missing state_class for energy dashboard"
# Fix: Energy sensors need state_class
- name: "Energy Usage"
  device_class: energy
  state_class: total_increasing  # Required for energy dashboard
  unit_of_measurement: "kWh"
  state: "{{ states('sensor.energy') }}"

# Error: "sensor.temp has invalid unit 'deg'"
# Fix: Use proper unit symbol
- name: "Temperature"
  device_class: temperature
  unit_of_measurement: "°C"  # Not "deg" or "degrees"
  state: "{{ states('sensor.temp') }}"
```

---

## Template Sensor Best Practices

### Complete Template Sensor

```yaml
template:
  - sensor:
      - name: "Living Room Temperature Average"
        unique_id: living_room_temp_avg
        device_class: temperature
        state_class: measurement
        unit_of_measurement: "°C"
        icon: mdi:thermometer
        availability: >
          {{ states('sensor.temp_1') not in ['unknown', 'unavailable'] and
             states('sensor.temp_2') not in ['unknown', 'unavailable'] }}
        state: >
          {% set t1 = states('sensor.temp_1') | float(0) %}
          {% set t2 = states('sensor.temp_2') | float(0) %}
          {{ ((t1 + t2) / 2) | round(1) }}
        attributes:
          sensors:
            - sensor.temp_1
            - sensor.temp_2
          last_updated: "{{ now().isoformat() }}"
```

### Without Device Class

If your sensor doesn't fit a standard device class, omit it:

```yaml
template:
  - sensor:
      - name: "Automation Run Count"
        unique_id: automation_run_count
        # No device_class - custom sensor type
        state_class: total_increasing
        unit_of_measurement: "runs"
        icon: mdi:counter
        state: "{{ states('counter.automation_runs') }}"
```

### Multiple Sensors with Shared Config

```yaml
template:
  - sensor:
      # Temperature sensors
      - name: "Kitchen Temperature"
        unique_id: kitchen_temp
        device_class: temperature
        state_class: measurement
        unit_of_measurement: "°C"
        state: "{{ states('sensor.kitchen_temp_raw') | float(0) | round(1) }}"

      - name: "Bedroom Temperature"
        unique_id: bedroom_temp
        device_class: temperature
        state_class: measurement
        unit_of_measurement: "°C"
        state: "{{ states('sensor.bedroom_temp_raw') | float(0) | round(1) }}"

      # Power sensors
      - name: "Total Power"
        unique_id: total_power
        device_class: power
        state_class: measurement
        unit_of_measurement: "W"
        state: >
          {{ states('sensor.circuit_1') | float(0) +
             states('sensor.circuit_2') | float(0) +
             states('sensor.circuit_3') | float(0) }}
```

---

## Icon and Display Patterns

### Automatic Icons

Home Assistant sets default icons based on device_class:

| Device Class | Default Icon |
|-------------|--------------|
| temperature | mdi:thermometer |
| humidity | mdi:water-percent |
| battery | mdi:battery |
| power | mdi:flash |
| energy | mdi:lightning-bolt |
| illuminance | mdi:brightness-5 |
| pressure | mdi:gauge |
| motion | mdi:motion-sensor |
| door | mdi:door |
| window | mdi:window-closed |

### Custom Icons with Template

```yaml
template:
  - sensor:
      - name: "Battery Level"
        device_class: battery
        unit_of_measurement: "%"
        state: "{{ states('sensor.battery') }}"
        icon: >
          {% set level = states('sensor.battery') | int(0) %}
          {% if level > 90 %}
            mdi:battery
          {% elif level > 70 %}
            mdi:battery-80
          {% elif level > 50 %}
            mdi:battery-60
          {% elif level > 30 %}
            mdi:battery-40
          {% elif level > 10 %}
            mdi:battery-20
          {% else %}
            mdi:battery-alert
          {% endif %}
```

### Unit Conversion in Templates

```yaml
template:
  - sensor:
      # Convert Fahrenheit to Celsius
      - name: "Temperature Celsius"
        device_class: temperature
        unit_of_measurement: "°C"
        state: >
          {% set f = states('sensor.temp_fahrenheit') | float(32) %}
          {{ ((f - 32) * 5/9) | round(1) }}

      # Convert kW to W
      - name: "Power Watts"
        device_class: power
        unit_of_measurement: "W"
        state: >
          {{ states('sensor.power_kw') | float(0) * 1000 | round(0) }}

      # Convert cubic meters to liters
      - name: "Water Liters"
        device_class: water
        state_class: total_increasing
        unit_of_measurement: "L"
        state: >
          {{ states('sensor.water_m3') | float(0) * 1000 | round(0) }}
```

---

## Quick Reference Table

| Device Class | Common Units | State Class | Example Entity |
|-------------|--------------|-------------|----------------|
| temperature | °C, °F | measurement | sensor.outdoor_temp |
| humidity | % | measurement | sensor.humidity |
| pressure | hPa, mbar | measurement | sensor.pressure |
| power | W, kW | measurement | sensor.power |
| energy | kWh, Wh | total_increasing | sensor.energy_meter |
| voltage | V, mV | measurement | sensor.voltage |
| current | A, mA | measurement | sensor.current |
| battery | % | measurement | sensor.battery |
| illuminance | lx | measurement | sensor.light_level |
| carbon_dioxide | ppm | measurement | sensor.co2 |
| pm25 | µg/m³ | measurement | sensor.pm25 |
| gas | m³ | total_increasing | sensor.gas_meter |
| water | L, m³ | total_increasing | sensor.water_meter |
| monetary | EUR, USD | total | sensor.cost |

---

## Migration from Legacy Units

### Common Migrations

```yaml
# Old (deprecated)
unit_of_measurement: "degrees"
# New
unit_of_measurement: "°C"

# Old
unit_of_measurement: "percent"
# New
unit_of_measurement: "%"

# Old
unit_of_measurement: "watts"
# New
unit_of_measurement: "W"

# Old
unit_of_measurement: "kwh"
# New
unit_of_measurement: "kWh"

# Old
unit_of_measurement: "lux"
# New
unit_of_measurement: "lx"
```

---

## Resources

- [Home Assistant Sensor Documentation](https://www.home-assistant.io/integrations/sensor/)
- [Device Class Reference](https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes)
- [State Classes](https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes)
- [Unit Conversion](https://www.home-assistant.io/integrations/sensor/#unit-conversion)
