# Home Assistant Template Sensors Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Template Sensor Structure](#template-sensor-structure)
- [State Templates](#state-templates)
- [Availability Templates](#availability-templates)
- [Attribute Templates](#attribute-templates)
- [Unit and Device Class](#unit-and-device-class)
- [Binary Template Sensors](#binary-template-sensors)
- [Trigger-Based Templates](#trigger-based-templates)
- [Using 'this' Variable](#using-this-variable)
- [Template Numbers and Selects](#template-numbers-and-selects)
- [Performance Optimization](#performance-optimization)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Template sensors create derived entities from other entity states using Jinja2 templates. They're useful for calculations, aggregations, and transformations.

### Key Terms

| Term | Description |
|------|-------------|
| **Template Sensor** | Sensor with state derived from template |
| **Trigger-Based** | Updates only on specific triggers |
| **State Class** | For statistics (measurement, total, etc.) |
| **Device Class** | Semantic type (temperature, power, etc.) |

### Template Sensor Types

| Type | Use Case |
|------|----------|
| `sensor` | Numeric or text values |
| `binary_sensor` | On/off states |
| `number` | Controllable numeric values |
| `select` | Controllable option lists |
| `button` | Trigger actions |

### File Location

```yaml
# Modern format (recommended)
# configuration.yaml
template:
  - sensor:
      - name: "My Sensor"
        state: "{{ ... }}"

# Or in separate file
template: !include templates.yaml
```

---

## Template Sensor Structure

### Minimal Sensor

```yaml
template:
  - sensor:
      - name: "Temperature Average"
        state: >
          {{ ((states('sensor.temp_1') | float) +
              (states('sensor.temp_2') | float)) / 2 | round(1) }}
```

### Complete Sensor

```yaml
template:
  - sensor:
      - name: "Daily Energy Cost"
        unique_id: daily_energy_cost
        unit_of_measurement: "SEK"
        device_class: monetary
        state_class: total
        icon: mdi:currency-usd
        state: >
          {{ (states('sensor.daily_energy') | float(0) *
              states('sensor.electricity_price') | float(0)) | round(2) }}
        availability: >
          {{ states('sensor.daily_energy') not in ['unknown', 'unavailable'] and
             states('sensor.electricity_price') not in ['unknown', 'unavailable'] }}
        attributes:
          energy_kwh: "{{ states('sensor.daily_energy') }}"
          price_per_kwh: "{{ states('sensor.electricity_price') }}"
          last_updated: "{{ now().isoformat() }}"
```

### Sensor Options

| Option | Required | Description |
|--------|----------|-------------|
| `name` | Yes | Friendly name |
| `unique_id` | No | Unique identifier for entity registry |
| `state` | Yes | Template for state value |
| `unit_of_measurement` | No | Unit label |
| `device_class` | No | Semantic type |
| `state_class` | No | For statistics |
| `icon` | No | Icon template or static |
| `picture` | No | Entity picture URL |
| `availability` | No | Template returning true/false |
| `attributes` | No | Additional attributes |

---

## State Templates

### Basic State

```yaml
template:
  - sensor:
      - name: "Outside Temperature"
        state: "{{ states('sensor.weather_temperature') }}"
```

### Calculations

```yaml
template:
  - sensor:
      # Average
      - name: "Average Temperature"
        unit_of_measurement: "°C"
        state: >
          {% set sensors = [
            states('sensor.temp_living') | float(0),
            states('sensor.temp_bedroom') | float(0),
            states('sensor.temp_kitchen') | float(0)
          ] %}
          {{ (sensors | sum / sensors | count) | round(1) }}

      # Min/Max
      - name: "Max Temperature"
        unit_of_measurement: "°C"
        state: >
          {{ [states('sensor.temp_1') | float,
              states('sensor.temp_2') | float,
              states('sensor.temp_3') | float] | max | round(1) }}

      # Conversion
      - name: "Power in kW"
        unit_of_measurement: "kW"
        state: "{{ (states('sensor.power_w') | float / 1000) | round(2) }}"
```

### Conditional States

```yaml
template:
  - sensor:
      - name: "HVAC Status"
        state: >
          {% set hvac = states('climate.thermostat') %}
          {% set action = state_attr('climate.thermostat', 'hvac_action') %}
          {% if hvac == 'off' %}
            Off
          {% elif action == 'heating' %}
            Heating
          {% elif action == 'cooling' %}
            Cooling
          {% else %}
            Idle
          {% endif %}
```

### Text States

```yaml
template:
  - sensor:
      - name: "Greeting"
        state: >
          {% set hour = now().hour %}
          {% if hour < 12 %}
            Good morning
          {% elif hour < 18 %}
            Good afternoon
          {% else %}
            Good evening
          {% endif %}

      - name: "Laundry Status"
        state: >
          {% set power = states('sensor.washer_power') | float(0) %}
          {% if power > 10 %}
            Running
          {% elif power > 1 %}
            Finishing
          {% else %}
            Idle
          {% endif %}
```

### Count Entities

```yaml
template:
  - sensor:
      - name: "Lights On"
        unit_of_measurement: "lights"
        state: >
          {{ states.light | selectattr('state', 'eq', 'on') | list | count }}

      - name: "Open Doors"
        state: >
          {{ states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'door')
             | selectattr('state', 'eq', 'on')
             | list | count }}

      - name: "Low Battery Devices"
        state: >
          {{ states.sensor
             | selectattr('attributes.device_class', 'eq', 'battery')
             | selectattr('state', 'lt', '20')
             | list | count }}
```

### Time-Based States

```yaml
template:
  - sensor:
      - name: "Time Since Last Motion"
        unit_of_measurement: "min"
        state: >
          {% set last = states.binary_sensor.motion.last_changed %}
          {{ ((now() - last).total_seconds() / 60) | round(0) }}

      - name: "Days Until Event"
        unit_of_measurement: "days"
        state: >
          {% set event_date = strptime('2024-12-25', '%Y-%m-%d') %}
          {{ ((event_date - now()).days) }}
```

---

## Availability Templates

### Basic Availability

```yaml
template:
  - sensor:
      - name: "Temperature Difference"
        state: >
          {{ (states('sensor.outdoor_temp') | float -
              states('sensor.indoor_temp') | float) | round(1) }}
        availability: >
          {{ states('sensor.outdoor_temp') not in ['unknown', 'unavailable'] and
             states('sensor.indoor_temp') not in ['unknown', 'unavailable'] }}
```

### With Numeric Validation

```yaml
template:
  - sensor:
      - name: "Power Cost"
        state: >
          {{ (states('sensor.power') | float * 0.15) | round(2) }}
        availability: >
          {{ states('sensor.power') | is_number }}
```

### Multiple Dependencies

```yaml
template:
  - sensor:
      - name: "Combined Sensor"
        state: >
          {{ states('sensor.a') | float + states('sensor.b') | float }}
        availability: >
          {% set sensors = ['sensor.a', 'sensor.b', 'sensor.c'] %}
          {{ sensors | map('states') | reject('in', ['unknown', 'unavailable']) | list | count == sensors | count }}
```

---

## Attribute Templates

### Static Attributes

```yaml
template:
  - sensor:
      - name: "Energy Cost"
        state: "{{ states('sensor.energy') | float * 0.12 }}"
        attributes:
          rate: "0.12"
          currency: "SEK"
```

### Dynamic Attributes

```yaml
template:
  - sensor:
      - name: "Climate Summary"
        state: "{{ states('climate.thermostat') }}"
        attributes:
          current_temp: "{{ state_attr('climate.thermostat', 'current_temperature') }}"
          target_temp: "{{ state_attr('climate.thermostat', 'temperature') }}"
          hvac_action: "{{ state_attr('climate.thermostat', 'hvac_action') }}"
          last_changed: "{{ states.climate.thermostat.last_changed.isoformat() }}"
```

### List Attributes

```yaml
template:
  - sensor:
      - name: "Lights Summary"
        state: "{{ states.light | selectattr('state', 'eq', 'on') | list | count }}"
        attributes:
          lights_on: >
            {{ states.light
               | selectattr('state', 'eq', 'on')
               | map(attribute='entity_id')
               | list }}
          lights_off: >
            {{ states.light
               | selectattr('state', 'eq', 'off')
               | map(attribute='entity_id')
               | list }}
```

---

## Unit and Device Class

### Device Classes

```yaml
template:
  - sensor:
      # Temperature
      - name: "Average Temperature"
        device_class: temperature
        unit_of_measurement: "°C"
        state: "{{ ... }}"

      # Power
      - name: "Total Power"
        device_class: power
        unit_of_measurement: "W"
        state: "{{ ... }}"

      # Energy
      - name: "Daily Energy"
        device_class: energy
        unit_of_measurement: "kWh"
        state_class: total_increasing
        state: "{{ ... }}"

      # Battery
      - name: "Average Battery"
        device_class: battery
        unit_of_measurement: "%"
        state: "{{ ... }}"

      # Monetary
      - name: "Energy Cost"
        device_class: monetary
        unit_of_measurement: "SEK"
        state: "{{ ... }}"
```

### State Classes

| State Class | Use Case |
|-------------|----------|
| `measurement` | Current value (temperature, power) |
| `total` | Cumulative value that can reset |
| `total_increasing` | Always increasing (energy meter) |

```yaml
template:
  - sensor:
      # Current measurement
      - name: "Current Power"
        device_class: power
        state_class: measurement
        unit_of_measurement: "W"
        state: "{{ states('sensor.power') }}"

      # Total that increases
      - name: "Total Energy"
        device_class: energy
        state_class: total_increasing
        unit_of_measurement: "kWh"
        state: "{{ states('sensor.energy_meter') }}"
```

### Dynamic Icons

```yaml
template:
  - sensor:
      - name: "Battery Status"
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

---

## Binary Template Sensors

### Basic Binary Sensor

```yaml
template:
  - binary_sensor:
      - name: "Someone Home"
        state: "{{ states('group.family') == 'home' }}"
```

### With Device Class

```yaml
template:
  - binary_sensor:
      # Motion
      - name: "Any Motion"
        device_class: motion
        state: >
          {{ states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'motion')
             | selectattr('state', 'eq', 'on')
             | list | count > 0 }}

      # Door
      - name: "Any Door Open"
        device_class: door
        state: >
          {{ is_state('binary_sensor.front_door', 'on') or
             is_state('binary_sensor.back_door', 'on') }}

      # Problem
      - name: "System Problem"
        device_class: problem
        state: >
          {{ states.sensor
             | selectattr('state', 'in', ['unknown', 'unavailable'])
             | list | count > 5 }}

      # Occupancy
      - name: "Room Occupied"
        device_class: occupancy
        state: >
          {{ is_state('binary_sensor.motion', 'on') or
             as_timestamp(now()) - as_timestamp(states.binary_sensor.motion.last_changed) < 600 }}
```

### Threshold Binary Sensor

```yaml
template:
  - binary_sensor:
      - name: "High Temperature"
        device_class: heat
        state: "{{ states('sensor.temperature') | float > 28 }}"

      - name: "Low Battery"
        device_class: battery
        state: "{{ states('sensor.battery') | float < 20 }}"
```

### Delay Off

```yaml
template:
  - binary_sensor:
      - name: "Motion with Delay"
        device_class: motion
        state: "{{ is_state('binary_sensor.motion', 'on') }}"
        delay_off:
          minutes: 5
```

---

## Trigger-Based Templates

Trigger-based templates only update when specified triggers fire, improving performance.

### Basic Trigger-Based

```yaml
template:
  - trigger:
      - platform: time_pattern
        minutes: "/5"
    sensor:
      - name: "Slow Update Sensor"
        state: "{{ states('sensor.data') }}"
```

### State Change Trigger

```yaml
template:
  - trigger:
      - platform: state
        entity_id: sensor.power
    sensor:
      - name: "Power Moving Average"
        unit_of_measurement: "W"
        state: >
          {% set current = trigger.to_state.state | float(0) %}
          {% set previous = this.state | float(0) %}
          {{ ((previous * 0.9) + (current * 0.1)) | round(1) }}
```

### Multiple Triggers

```yaml
template:
  - trigger:
      - platform: state
        entity_id:
          - sensor.temp_1
          - sensor.temp_2
          - sensor.temp_3
      - platform: time_pattern
        hours: "*"
    sensor:
      - name: "Temperature Summary"
        state: >
          {{ [states('sensor.temp_1') | float,
              states('sensor.temp_2') | float,
              states('sensor.temp_3') | float] | average | round(1) }}
```

### Trigger Variables

```yaml
template:
  - trigger:
      - platform: state
        entity_id: sensor.energy
    sensor:
      - name: "Energy Consumption Rate"
        unit_of_measurement: "W"
        state: >
          {% set current = trigger.to_state.state | float(0) %}
          {% set previous = trigger.from_state.state | float(0) %}
          {% set time_diff = (trigger.to_state.last_updated - trigger.from_state.last_updated).total_seconds() %}
          {% if time_diff > 0 %}
            {{ ((current - previous) / time_diff * 3600000) | round(0) }}
          {% else %}
            {{ this.state | default(0) }}
          {% endif %}
```

### With Action

```yaml
template:
  - trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: input_number.set_value
        target:
          entity_id: input_number.daily_energy_start
        data:
          value: "{{ states('sensor.energy_meter') }}"
    sensor:
      - name: "Daily Energy"
        unit_of_measurement: "kWh"
        state: >
          {{ (states('sensor.energy_meter') | float -
              states('input_number.daily_energy_start') | float) | round(2) }}
```

---

## Using 'this' Variable

The `this` variable references the current template entity.

### Access Previous State

```yaml
template:
  - sensor:
      - name: "Smoothed Value"
        state: >
          {% set current = states('sensor.noisy') | float(0) %}
          {% set previous = this.state | float(0) %}
          {{ ((previous * 0.8) + (current * 0.2)) | round(2) }}
```

### Access Previous Attributes

```yaml
template:
  - trigger:
      - platform: state
        entity_id: sensor.power
    sensor:
      - name: "Power Statistics"
        state: "{{ trigger.to_state.state }}"
        attributes:
          min: >
            {% set current = trigger.to_state.state | float %}
            {% set prev_min = this.attributes.get('min', current) | float %}
            {{ [current, prev_min] | min }}
          max: >
            {% set current = trigger.to_state.state | float %}
            {% set prev_max = this.attributes.get('max', current) | float %}
            {{ [current, prev_max] | max }}
          samples: >
            {{ (this.attributes.get('samples', 0) | int) + 1 }}
```

### Keep Running Total

```yaml
template:
  - trigger:
      - platform: state
        entity_id: binary_sensor.door
        to: "on"
    sensor:
      - name: "Door Open Count"
        state: >
          {{ (this.state | int(0)) + 1 }}
```

---

## Template Numbers and Selects

### Template Number

```yaml
template:
  - number:
      - name: "Brightness Override"
        unique_id: brightness_override
        min: 0
        max: 100
        step: 5
        unit_of_measurement: "%"
        state: "{{ states('input_number.brightness') }}"
        set_value:
          - service: input_number.set_value
            target:
              entity_id: input_number.brightness
            data:
              value: "{{ value }}"
```

### Template Select

```yaml
template:
  - select:
      - name: "Home Mode"
        unique_id: home_mode_select
        state: "{{ states('input_select.mode') }}"
        options: "{{ state_attr('input_select.mode', 'options') }}"
        select_option:
          - service: input_select.select_option
            target:
              entity_id: input_select.mode
            data:
              option: "{{ option }}"
```

### Template Button

```yaml
template:
  - button:
      - name: "Reset Counter"
        unique_id: reset_counter_button
        press:
          - service: counter.reset
            target:
              entity_id: counter.my_counter
```

---

## Performance Optimization

### Use Trigger-Based for Heavy Templates

```yaml
# Bad: Updates on every state change in HA
template:
  - sensor:
      - name: "Complex Calculation"
        state: >
          {% for sensor in states.sensor %}
            ...complex logic...
          {% endfor %}

# Good: Only updates when needed
template:
  - trigger:
      - platform: time_pattern
        minutes: "/5"
    sensor:
      - name: "Complex Calculation"
        state: >
          {% for sensor in states.sensor %}
            ...complex logic...
          {% endfor %}
```

### Limit Entity Queries

```yaml
# Bad: Multiple calls for same entity
template:
  - sensor:
      - name: "Climate Info"
        state: "{{ states('climate.thermostat') }}"
        attributes:
          temp: "{{ state_attr('climate.thermostat', 'current_temperature') }}"
          target: "{{ state_attr('climate.thermostat', 'temperature') }}"
          mode: "{{ states('climate.thermostat') }}"

# Better: Use variables
template:
  - sensor:
      - name: "Climate Info"
        state: >
          {% set climate = states.climate.thermostat %}
          {{ climate.state }}
        attributes:
          temp: >
            {% set climate = states.climate.thermostat %}
            {{ climate.attributes.current_temperature }}
```

### Avoid Unnecessary Updates

```yaml
# Add availability to prevent errors
template:
  - sensor:
      - name: "Safe Sensor"
        state: "{{ states('sensor.data') | float * 2 }}"
        availability: "{{ states('sensor.data') | is_number }}"
```

---

## Advanced List Transformations

### selectattr and rejectattr

Filter entities by their attributes.

```yaml
template:
  - sensor:
      # Count lights that are on
      - name: "Lights On Count"
        state: >
          {{ states.light
             | selectattr('state', 'eq', 'on')
             | list | length }}

      # Get names of lights that are on
      - name: "Lights On List"
        state: >
          {{ states.light
             | selectattr('state', 'eq', 'on')
             | map(attribute='name')
             | list | join(', ') }}

      # Filter by attribute value
      - name: "Bright Lights Count"
        state: >
          {{ states.light
             | selectattr('state', 'eq', 'on')
             | selectattr('attributes.brightness', 'defined')
             | selectattr('attributes.brightness', 'gt', 128)
             | list | length }}

      # Reject unavailable entities
      - name: "Available Sensors"
        state: >
          {{ states.sensor
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | list | length }}
```

### map and Transformations

Transform lists of values.

```yaml
template:
  - sensor:
      # Extract specific attribute
      - name: "All Temperatures"
        state: >
          {{ states.sensor
             | selectattr('attributes.device_class', 'eq', 'temperature')
             | map(attribute='state')
             | map('float', 0)
             | list }}

      # Calculate average of multiple sensors
      - name: "Average Temperature"
        unit_of_measurement: "°C"
        state: >
          {% set temps = states.sensor
             | selectattr('attributes.device_class', 'eq', 'temperature')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | map(attribute='state')
             | map('float')
             | list %}
          {{ (temps | sum / temps | length) | round(1) if temps else 'unknown' }}

      # Get entity IDs matching pattern
      - name: "Motion Sensors List"
        state: >
          {{ states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'motion')
             | map(attribute='entity_id')
             | list | join(', ') }}
```

### sort and Filtering

Sort and limit results.

```yaml
template:
  - sensor:
      # Get highest power consumer
      - name: "Highest Power Device"
        state: >
          {% set devices = states.sensor
             | selectattr('attributes.device_class', 'eq', 'power')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | sort(attribute='state', reverse=true)
             | list %}
          {{ devices[0].name if devices else 'None' }}

      # Top 3 power consumers
      - name: "Top Power Consumers"
        state: >
          {% set devices = states.sensor
             | selectattr('attributes.device_class', 'eq', 'power')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | sort(attribute='state', reverse=true)
             | map(attribute='name')
             | list %}
          {{ devices[:3] | join(', ') }}

      # Recently changed entities
      - name: "Recently Changed"
        state: >
          {% set cutoff = now() - timedelta(minutes=5) %}
          {{ states
             | selectattr('last_changed', 'gt', cutoff)
             | map(attribute='entity_id')
             | list | length }}
```

### groupby Operations

Group entities by attributes.

```yaml
template:
  - sensor:
      # Count entities by area
      - name: "Entities Per Area"
        state: >
          {% set by_area = states.light
             | groupby('area_id')
             | list %}
          {{ by_area | length }} areas

      # Entities grouped by domain
      - name: "Domain Summary"
        state: >
          {% for domain in states | map(attribute='domain') | unique | list %}
            {{ domain }}: {{ states[domain] | list | length }}
          {% endfor %}
```

### Complex Aggregations

```yaml
template:
  - sensor:
      # Sum of all power sensors
      - name: "Total Power Consumption"
        unit_of_measurement: "W"
        device_class: power
        state: >
          {{ states.sensor
             | selectattr('attributes.device_class', 'eq', 'power')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | map(attribute='state')
             | map('float', 0)
             | sum | round(0) }}

      # Count entities in specific states
      - name: "Security Summary"
        state: >
          {% set doors = states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'door')
             | selectattr('state', 'eq', 'on')
             | list | length %}
          {% set windows = states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'window')
             | selectattr('state', 'eq', 'on')
             | list | length %}
          {% set motion = states.binary_sensor
             | selectattr('attributes.device_class', 'eq', 'motion')
             | selectattr('state', 'eq', 'on')
             | list | length %}
          {{ doors }} doors, {{ windows }} windows, {{ motion }} motion

      # Battery levels below threshold
      - name: "Low Batteries"
        state: >
          {% set low = states.sensor
             | selectattr('attributes.device_class', 'eq', 'battery')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | selectattr('state', 'lt', '20')
             | map(attribute='name')
             | list %}
          {{ low | join(', ') if low else 'All OK' }}
```

### Working with JSON and Attributes

```yaml
template:
  - sensor:
      # Extract nested attribute
      - name: "Weather Forecast High"
        unit_of_measurement: "°C"
        state: >
          {% set forecast = state_attr('weather.home', 'forecast') %}
          {{ forecast[0].temperature if forecast else 'unknown' }}

      # Process JSON attribute
      - name: "Device Count from JSON"
        state: >
          {% set data = state_attr('sensor.api_response', 'devices') %}
          {{ data | length if data else 0 }}

      # Complex attribute extraction
      - name: "Active Notifications"
        state: >
          {% set notifs = states.persistent_notification | list %}
          {{ notifs | length }}
        attributes:
          titles: >
            {{ states.persistent_notification
               | map(attribute='attributes.title')
               | list }}
```

### Performance Tips for List Operations

```yaml
# GOOD: Filter early, process less data
template:
  - sensor:
      - name: "Efficient Temperature Avg"
        state: >
          {% set temps = states.sensor
             | selectattr('entity_id', 'search', 'temperature')
             | rejectattr('state', 'in', ['unknown', 'unavailable'])
             | map(attribute='state')
             | map('float', 0)
             | list %}
          {{ (temps | sum / temps | length) | round(1) if temps else 0 }}

# BAD: Processing all entities then filtering
# Avoid iterating all of states without filtering

# GOOD: Use trigger-based for expensive operations
template:
  - trigger:
      - platform: time_pattern
        minutes: "/5"
    sensor:
      - name: "Periodic Expensive Calculation"
        state: >
          {{ expensive_calculation_here }}
```

---

## Common Patterns

### Sun Position Based Brightness

```yaml
template:
  - sensor:
      - name: "Recommended Brightness"
        unit_of_measurement: "%"
        state: >
          {% set elevation = state_attr('sun.sun', 'elevation') | float %}
          {% if elevation < 0 %}
            20
          {% elif elevation < 10 %}
            50
          {% elif elevation < 30 %}
            80
          {% else %}
            100
          {% endif %}
```

### Washer/Dryer Status

```yaml
template:
  - sensor:
      - name: "Washer Status"
        state: >
          {% set power = states('sensor.washer_power') | float(0) %}
          {% if power > 50 %}
            Washing
          {% elif power > 5 %}
            Finishing
          {% else %}
            Idle
          {% endif %}
        icon: >
          {% set power = states('sensor.washer_power') | float(0) %}
          {% if power > 5 %}
            mdi:washing-machine
          {% else %}
            mdi:washing-machine-off
          {% endif %}
```

### Room Temperature Status

```yaml
template:
  - sensor:
      - name: "Living Room Climate"
        state: >
          {% set temp = states('sensor.living_room_temperature') | float %}
          {% set humidity = states('sensor.living_room_humidity') | float %}
          {% if temp < 18 %}
            Cold
          {% elif temp > 26 %}
            Hot
          {% elif humidity > 70 %}
            Humid
          {% elif humidity < 30 %}
            Dry
          {% else %}
            Comfortable
          {% endif %}
        attributes:
          temperature: "{{ states('sensor.living_room_temperature') }}"
          humidity: "{{ states('sensor.living_room_humidity') }}"
          comfort_index: >
            {% set temp = states('sensor.living_room_temperature') | float %}
            {% set humidity = states('sensor.living_room_humidity') | float %}
            {{ (temp * 0.5 + humidity * 0.5) | round(0) }}
```

### Next Scheduled Event

```yaml
template:
  - sensor:
      - name: "Next Calendar Event"
        state: >
          {% set event = state_attr('calendar.family', 'message') %}
          {{ event if event else 'No upcoming events' }}
        attributes:
          start_time: "{{ state_attr('calendar.family', 'start_time') }}"
          location: "{{ state_attr('calendar.family', 'location') }}"
```

---

## Best Practices

### Use Unique IDs

```yaml
template:
  - sensor:
      - name: "My Sensor"
        unique_id: my_custom_sensor  # Enables UI customization
        state: "{{ ... }}"
```

### Provide Defaults

```yaml
template:
  - sensor:
      - name: "Safe Calculation"
        state: >
          {{ (states('sensor.value') | float(0) * 2) | round(2) }}
        # float(0) provides default if unavailable
```

### Use Proper Device/State Classes

```yaml
template:
  - sensor:
      - name: "Energy Sensor"
        device_class: energy
        state_class: total_increasing  # Required for energy dashboard
        unit_of_measurement: "kWh"
        state: "{{ ... }}"
```

### Add Availability

```yaml
template:
  - sensor:
      - name: "Derived Value"
        state: "{{ ... }}"
        availability: >
          {{ states('sensor.source') not in ['unknown', 'unavailable'] }}
```

### Document Complex Templates

```yaml
template:
  - sensor:
      # Calculate daily energy cost based on:
      # - Current energy price from Nordpool
      # - Daily energy consumption from utility meter
      # Updates every 5 minutes to reduce load
      - name: "Daily Energy Cost"
        state: >
          {# Get current values #}
          {% set energy = states('sensor.daily_energy') | float(0) %}
          {% set price = states('sensor.nordpool') | float(0) %}
          {# Calculate and round to 2 decimals #}
          {{ (energy * price) | round(2) }}
```

---

## Troubleshooting

### Sensor Shows Unknown

| Cause | Solution |
|-------|----------|
| Source entity unavailable | Add availability template |
| Template error | Check Developer Tools > Template |
| Missing default | Use `| float(0)` or `| default('')` |

### Debug Templates

```yaml
# Test in Developer Tools > Template
{% set value = states('sensor.test') %}
Value: {{ value }}
Is number: {{ value | is_number }}
As float: {{ value | float('error') }}
```

### Common Errors

```yaml
# Error: 'None' has no attribute
# Fix: Check entity exists
state: >
  {% if states('sensor.test') %}
    {{ states('sensor.test') | float }}
  {% else %}
    0
  {% endif %}

# Error: Invalid template
# Fix: Quote template properly
state: "{{ states('sensor.test') }}"  # Correct
state: {{ states('sensor.test') }}    # Wrong - missing quotes

# Error: Float conversion failed
# Fix: Provide default
state: "{{ states('sensor.test') | float(0) }}"
```

### Reload Templates

```yaml
# Developer Tools > YAML > Reload Template Entities

# Or via service
service: homeassistant.reload_config_entry
data:
  entry_id: <template_config_entry_id>
```
