# Statistics & Long-Term Data

Complete guide for working with statistics, long-term data, and historical analysis in Home Assistant.

---

## Overview

Home Assistant provides several ways to track and analyze historical data:

| Feature | Purpose | Data Retention |
|---------|---------|----------------|
| **Recorder** | Short-term event history | Days/weeks |
| **Long-term Statistics** | Aggregated hourly data | Unlimited |
| **History Stats** | Duration-based tracking | Real-time calculation |
| **Statistics Sensor** | Value-based calculations | Configurable |

---

## Long-Term Statistics

### How It Works

- Data sampled every 5 minutes
- Aggregated to hourly statistics (mean, min, max, sum)
- Stored indefinitely (separate from recorder database)
- Powers the Energy Dashboard

### Compatible Sensors

Sensors must have `state_class` attribute:

```yaml
# state_class options:
# - measurement: Current value (temperature, humidity)
# - total: Cumulative value that can reset (energy meter)
# - total_increasing: Only increases (gas meter)

# Example sensor with state_class
template:
  - sensor:
      - name: "Room Temperature"
        device_class: temperature
        state_class: measurement  # Enables long-term statistics
        unit_of_measurement: "°C"
        state: "{{ states('sensor.temperature_raw') }}"
```

### Viewing Statistics

1. **Developer Tools > Statistics** - View all tracked statistics
2. **History tab** - Long-term graph view
3. **Energy Dashboard** - Energy-specific statistics

### Fixing Statistics Issues

```yaml
# Developer Tools > Statistics shows issues:
# - "Entity no longer available"
# - "Unit changed"
# - "State class changed"

# Fix via service call:
service: recorder.clear_statistics
data:
  statistic_ids:
    - sensor.problematic_sensor
```

---

## History Stats Sensor

Track how long something has been in a specific state.

### Basic Configuration

```yaml
sensor:
  - platform: history_stats
    name: TV On Today
    entity_id: media_player.living_room_tv
    state: "on"
    type: time
    start: "{{ today_at() }}"
    end: "{{ now() }}"
```

### Type Options

```yaml
# time - Duration in hours
sensor:
  - platform: history_stats
    name: "Heating Hours Today"
    entity_id: climate.living_room
    state: "heat"
    type: time
    start: "{{ today_at() }}"
    end: "{{ now() }}"

# count - Number of state changes
sensor:
  - platform: history_stats
    name: "Door Opens Today"
    entity_id: binary_sensor.front_door
    state: "on"
    type: count
    start: "{{ today_at() }}"
    end: "{{ now() }}"

# ratio - Percentage of time in state
sensor:
  - platform: history_stats
    name: "Motion Ratio Today"
    entity_id: binary_sensor.motion
    state: "on"
    type: ratio
    start: "{{ today_at() }}"
    end: "{{ now() }}"
```

### Common Time Periods

```yaml
sensor:
  # Today (midnight to now)
  - platform: history_stats
    name: "Lights On Today"
    entity_id: light.living_room
    state: "on"
    type: time
    start: "{{ today_at() }}"
    end: "{{ now() }}"

  # Yesterday (full day)
  - platform: history_stats
    name: "Lights On Yesterday"
    entity_id: light.living_room
    state: "on"
    type: time
    start: "{{ today_at() - timedelta(days=1) }}"
    end: "{{ today_at() }}"

  # This week (Monday to now)
  - platform: history_stats
    name: "Lights On This Week"
    entity_id: light.living_room
    state: "on"
    type: time
    start: "{{ today_at() - timedelta(days=now().weekday()) }}"
    end: "{{ now() }}"

  # This month (1st to now)
  - platform: history_stats
    name: "Lights On This Month"
    entity_id: light.living_room
    state: "on"
    type: time
    start: "{{ today_at().replace(day=1) }}"
    end: "{{ now() }}"

  # Last 24 hours (rolling)
  - platform: history_stats
    name: "Lights On Last 24h"
    entity_id: light.living_room
    state: "on"
    type: time
    start: "{{ now() - timedelta(hours=24) }}"
    end: "{{ now() }}"

  # Last 7 days (rolling)
  - platform: history_stats
    name: "Lights On Last Week"
    entity_id: light.living_room
    state: "on"
    type: time
    start: "{{ now() - timedelta(days=7) }}"
    end: "{{ now() }}"
```

### Multiple States

```yaml
sensor:
  # Track multiple states
  - platform: history_stats
    name: "TV Active Time"
    entity_id: media_player.tv
    state:
      - "on"
      - "playing"
      - "paused"
    type: time
    start: "{{ today_at() }}"
    end: "{{ now() }}"
```

---

## Statistics Sensor

Perform statistical calculations on sensor data.

### Basic Configuration

```yaml
sensor:
  - platform: statistics
    name: "Temperature Statistics"
    entity_id: sensor.outdoor_temperature
    state_characteristic: mean
    max_age:
      hours: 24
```

### Available Characteristics

```yaml
# Central tendency
state_characteristic: mean           # Average value
state_characteristic: median         # Middle value

# Extremes
state_characteristic: value_max      # Maximum value
state_characteristic: value_min      # Minimum value

# Spread
state_characteristic: standard_deviation
state_characteristic: variance

# Range
state_characteristic: change         # Difference between newest and oldest
state_characteristic: change_rate    # Change per time unit

# Count
state_characteristic: count          # Number of samples
state_characteristic: datetime_newest  # Time of newest sample
state_characteristic: datetime_oldest  # Time of oldest sample

# Quantiles
state_characteristic: quantiles      # Returns list
```

### Example Configurations

```yaml
sensor:
  # Average temperature over 24 hours
  - platform: statistics
    name: "Average Temperature (24h)"
    entity_id: sensor.outdoor_temperature
    state_characteristic: mean
    max_age:
      hours: 24

  # Maximum temperature today
  - platform: statistics
    name: "Max Temperature Today"
    entity_id: sensor.outdoor_temperature
    state_characteristic: value_max
    max_age:
      hours: 24

  # Temperature change rate
  - platform: statistics
    name: "Temperature Change Rate"
    entity_id: sensor.outdoor_temperature
    state_characteristic: change_rate
    max_age:
      hours: 1

  # Sample count (for debugging)
  - platform: statistics
    name: "Temperature Sample Count"
    entity_id: sensor.outdoor_temperature
    state_characteristic: count
    max_age:
      hours: 24
```

### Sample-Based vs Time-Based

```yaml
sensor:
  # Time-based: Include samples from last N hours
  - platform: statistics
    name: "Temp Stats (Time)"
    entity_id: sensor.temperature
    state_characteristic: mean
    max_age:
      hours: 24

  # Sample-based: Use last N samples
  - platform: statistics
    name: "Temp Stats (Samples)"
    entity_id: sensor.temperature
    state_characteristic: mean
    sampling_size: 100
```

---

## Template-Based Statistics

### Rolling Average

```yaml
template:
  - sensor:
      - name: "Temperature Rolling Average"
        unit_of_measurement: "°C"
        device_class: temperature
        state: >
          {% set temps = state_attr('sensor.temperature_statistics', 'buffer') %}
          {% if temps %}
            {{ (temps | sum / temps | length) | round(1) }}
          {% else %}
            {{ states('sensor.outdoor_temperature') }}
          {% endif %}
```

### Daily Min/Max

```yaml
template:
  - sensor:
      - name: "Today's High"
        unit_of_measurement: "°C"
        device_class: temperature
        state: "{{ states('sensor.max_temperature_today') }}"

      - name: "Today's Low"
        unit_of_measurement: "°C"
        device_class: temperature
        state: "{{ states('sensor.min_temperature_today') }}"
```

### Comparison to Yesterday

```yaml
template:
  - sensor:
      - name: "Temperature vs Yesterday"
        unit_of_measurement: "°C"
        state: >
          {% set today = states('sensor.outdoor_temperature') | float(0) %}
          {% set yesterday = states('sensor.yesterday_temperature') | float(0) %}
          {{ (today - yesterday) | round(1) }}
```

---

## Automations with Statistics

### Alert on Unusual Values

```yaml
automation:
  - alias: "Temperature Anomaly Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: sensor.temperature_mean_24h
        value_template: >
          {{ float(trigger.to_state.state, 0) -
             float(states('sensor.temperature_mean_24h'), 0) > 10 }}
    action:
      - service: notify.mobile_app
        data:
          message: >
            Temperature {{ states('sensor.outdoor_temperature') }}°C is
            {{ (states('sensor.outdoor_temperature') | float -
               states('sensor.temperature_mean_24h') | float) | round(1) }}°C
            above 24h average
```

### Usage Threshold Alerts

```yaml
automation:
  - alias: "Excessive TV Usage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tv_on_today
        above: 8  # More than 8 hours
    action:
      - service: notify.mobile_app
        data:
          message: "TV has been on for {{ states('sensor.tv_on_today') | round(1) }} hours today"
```

### Weekly Summary

```yaml
automation:
  - alias: "Weekly Usage Summary"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Weekly Summary"
          message: >
            This week:
            - Heating: {{ states('sensor.heating_hours_week') | round(1) }}h
            - TV: {{ states('sensor.tv_hours_week') | round(1) }}h
            - Motion events: {{ states('sensor.motion_count_week') }}
```

---

## Dashboard Cards

### Statistics Overview

```yaml
type: entities
title: Statistics
entities:
  - entity: sensor.temperature_mean_24h
    name: Avg Temp (24h)
  - entity: sensor.temperature_max_today
    name: High Today
  - entity: sensor.temperature_min_today
    name: Low Today
  - type: divider
  - entity: sensor.tv_on_today
    name: TV Time Today
  - entity: sensor.heating_hours_today
    name: Heating Today
```

### History Stats Card

```yaml
type: glance
title: Today's Activity
entities:
  - entity: sensor.tv_on_today
    name: TV
  - entity: sensor.heating_hours_today
    name: Heating
  - entity: sensor.motion_count_today
    name: Motion Events
  - entity: sensor.door_opens_today
    name: Door Opens
```

### Statistics Graph

```yaml
type: statistics-graph
title: Temperature Statistics
entities:
  - entity: sensor.outdoor_temperature
period:
  calendar:
    period: day
stat_types:
  - mean
  - min
  - max
```

### ApexCharts (HACS)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Temperature History
graph_span: 7d
series:
  - entity: sensor.outdoor_temperature
    type: line
    statistics:
      type: mean
      period: hour
  - entity: sensor.outdoor_temperature
    type: area
    opacity: 0.3
    statistics:
      type: min
      period: hour
  - entity: sensor.outdoor_temperature
    type: area
    opacity: 0.3
    statistics:
      type: max
      period: hour
```

---

## Recorder Configuration

### Optimizing for Statistics

```yaml
# configuration.yaml
recorder:
  # Keep detailed history for X days
  purge_keep_days: 10

  # Commit to database every X seconds
  commit_interval: 1

  # Exclude entities from history (not statistics!)
  exclude:
    domains:
      - automation
      - script
      - updater
    entity_globs:
      - sensor.weather_*_forecast
    entities:
      - sensor.last_boot
```

### Database Size Management

```yaml
recorder:
  # Aggressive purging for small installations
  purge_keep_days: 5

  # Or exclude more entities
  exclude:
    domains:
      - media_player
      - camera
      - automation
```

---

## Template Functions for Statistics

### Time Calculations

```yaml
template:
  - sensor:
      - name: "Hours Since Last Motion"
        state: >
          {% set last = states.binary_sensor.motion.last_changed %}
          {% if last %}
            {{ ((now() - last).total_seconds() / 3600) | round(1) }}
          {% else %}
            unknown
          {% endif %}
        unit_of_measurement: "h"

      - name: "Minutes Since Door Open"
        state: >
          {% set last = states.binary_sensor.door.last_changed %}
          {% if last and is_state('binary_sensor.door', 'off') %}
            {{ ((now() - last).total_seconds() / 60) | round(0) }}
          {% else %}
            0
          {% endif %}
        unit_of_measurement: "min"
```

### State Duration

```yaml
template:
  - sensor:
      - name: "Current State Duration"
        state: >
          {% set changed = states.climate.living_room.last_changed %}
          {% if changed %}
            {% set duration = now() - changed %}
            {% set hours = (duration.total_seconds() // 3600) | int %}
            {% set minutes = ((duration.total_seconds() % 3600) // 60) | int %}
            {{ hours }}h {{ minutes }}m
          {% else %}
            unknown
          {% endif %}
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Statistics not recording | Check sensor has `state_class` attribute |
| History stats shows 0 | Verify entity_id and state values match |
| Database growing large | Reduce `purge_keep_days`, exclude more entities |
| Old data missing | Long-term stats separate from recorder history |

### Validate Statistics Configuration

```yaml
# Check in Developer Tools > Statistics
# Look for:
# - "Entities with issues"
# - Unit mismatches
# - Missing state_class
```

### Debug Logging

```yaml
logger:
  default: warning
  logs:
    homeassistant.components.history_stats: debug
    homeassistant.components.statistics: debug
    homeassistant.components.recorder: debug
```

---

## Best Practices

### state_class Selection

```yaml
# measurement - Instantaneous values
# Good for: temperature, humidity, power
state_class: measurement

# total_increasing - Cumulative, only increases
# Good for: energy meters, gas meters
state_class: total_increasing

# total - Cumulative, can reset
# Good for: daily counters, resettable meters
state_class: total
```

### History Stats Tips

```yaml
# 1. Use consistent state values
state: "on"  # Not "On" or "ON"

# 2. Test time templates in Developer Tools
# 3. Consider time zones
# 4. Don't track high-frequency sensors
```

### Performance Considerations

```yaml
# Avoid:
# - Too many history_stats sensors
# - Very long time periods
# - High-frequency source sensors

# Better:
# - Use long-term statistics for long periods
# - Limit history_stats to last 24-48 hours
# - Use statistics sensor for calculations
```

---

## Reference

### Useful Links

- [Recorder Documentation](https://www.home-assistant.io/integrations/recorder/)
- [History Stats](https://www.home-assistant.io/integrations/history_stats/)
- [Statistics Sensor](https://www.home-assistant.io/integrations/statistics/)
- [Long-term Statistics](https://developers.home-assistant.io/docs/core/entity/sensor/#long-term-statistics)

### State Class Reference

| state_class | Use Case | Example |
|-------------|----------|---------|
| `measurement` | Instantaneous | Temperature, humidity |
| `total` | Cumulative (resets) | Daily energy |
| `total_increasing` | Cumulative (no reset) | Total gas used |
