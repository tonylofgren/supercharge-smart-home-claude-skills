# Weather Integration

Complete guide for weather integrations and weather-based automations in Home Assistant.

---

## Overview

Home Assistant supports multiple weather data sources:

| Integration | Coverage | Key Features |
|-------------|----------|--------------|
| **Met.no** | Global | Default, free, reliable |
| **OpenWeatherMap** | Global | Detailed forecasts, alerts |
| **AccuWeather** | Global | Hourly forecasts |
| **SMHI** | Sweden | Local Swedish forecasts |
| **Met Office** | UK | Official UK weather |
| **Environment Canada** | Canada | Alerts, radar |
| **NWS** | USA | National Weather Service |

---

## Met.no Integration

The default weather integration in Home Assistant.

### Setup

1. Go to **Settings > Devices & Services**
2. Click **Add Integration**
3. Search for **Meteorologisk institutt (Met.no)**
4. Configure location (uses HA location by default)

### Configuration Options

```yaml
# Optional: Different location
# Configure via UI with custom coordinates

# Entities created:
# weather.forecast_home
# - Attributes: temperature, humidity, wind_speed, etc.
```

### Entities Created

```yaml
# Main weather entity
weather.forecast_home

# Attributes available:
# - temperature
# - humidity
# - pressure
# - wind_bearing
# - wind_speed
# - visibility
# - forecast (list of future conditions)
```

---

## OpenWeatherMap Integration

### Setup

1. Get API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Go to **Settings > Devices & Services**
3. Click **Add Integration** > **OpenWeatherMap**
4. Enter API key and location

### Configuration Options

```yaml
# Modes available:
# - onecall_daily: Daily forecasts (free)
# - onecall_hourly: Hourly forecasts (free)
# - freedaily: Basic daily (deprecated)

# Additional sensors:
# - UV index
# - Visibility
# - Pressure tendency
# - Cloud coverage
```

### Sensors Created

```yaml
# Weather entity
weather.openweathermap

# Individual sensors (if enabled):
sensor.openweathermap_temperature
sensor.openweathermap_humidity
sensor.openweathermap_pressure
sensor.openweathermap_wind_speed
sensor.openweathermap_wind_bearing
sensor.openweathermap_clouds
sensor.openweathermap_rain
sensor.openweathermap_snow
sensor.openweathermap_uv_index
sensor.openweathermap_dew_point
sensor.openweathermap_feels_like
sensor.openweathermap_forecast_condition
```

---

## Using Weather Data

### Accessing Current Conditions

```yaml
# Current temperature
{{ states('weather.home') }}  # Returns condition: sunny, cloudy, etc.
{{ state_attr('weather.home', 'temperature') }}

# All current attributes
{{ state_attr('weather.home', 'temperature') }}
{{ state_attr('weather.home', 'humidity') }}
{{ state_attr('weather.home', 'pressure') }}
{{ state_attr('weather.home', 'wind_speed') }}
{{ state_attr('weather.home', 'wind_bearing') }}
```

### Accessing Forecasts (2024.x+ Method)

```yaml
# Use weather.get_forecasts service (action in automations)
action:
  - service: weather.get_forecasts
    target:
      entity_id: weather.home
    data:
      type: daily  # or "hourly" or "twice_daily"
    response_variable: forecast

  - service: notify.mobile_app
    data:
      message: >
        Tomorrow: {{ forecast['weather.home'].forecast[0].condition }}
        High: {{ forecast['weather.home'].forecast[0].temperature }}°C
```

### Template Sensor for Forecast

```yaml
template:
  - trigger:
      - platform: time_pattern
        hours: /1  # Update every hour
    action:
      - service: weather.get_forecasts
        target:
          entity_id: weather.home
        data:
          type: daily
        response_variable: forecast
    sensor:
      - name: "Tomorrow High"
        unit_of_measurement: "°C"
        device_class: temperature
        state: >
          {{ forecast['weather.home'].forecast[0].temperature }}

      - name: "Tomorrow Low"
        unit_of_measurement: "°C"
        device_class: temperature
        state: >
          {{ forecast['weather.home'].forecast[0].templow }}

      - name: "Tomorrow Condition"
        state: >
          {{ forecast['weather.home'].forecast[0].condition }}

      - name: "Rain Expected Tomorrow"
        state: >
          {% set precip = forecast['weather.home'].forecast[0].precipitation | float(0) %}
          {{ 'Yes' if precip > 0 else 'No' }}
```

---

## Weather-Based Automations

### Rain Protection

```yaml
automation:
  - alias: "Close Windows Before Rain"
    trigger:
      - platform: time_pattern
        minutes: /30
    action:
      - service: weather.get_forecasts
        target:
          entity_id: weather.home
        data:
          type: hourly
        response_variable: forecast
      - if:
          - condition: template
            value_template: >
              {% set next_hours = forecast['weather.home'].forecast[:6] %}
              {{ next_hours | selectattr('precipitation', 'gt', 0) | list | count > 0 }}
        then:
          - service: cover.close_cover
            target:
              entity_id: cover.awning
          - service: notify.mobile_app
            data:
              message: "Rain expected in next 6 hours - closing awning"

automation:
  - alias: "Alert if Windows Open and Rain Coming"
    trigger:
      - platform: state
        entity_id: weather.home
        to:
          - rainy
          - pouring
    condition:
      - condition: state
        entity_id: group.windows
        state: "on"  # Windows open
    action:
      - service: notify.mobile_app
        data:
          title: "🌧️ Close Windows!"
          message: "Rain starting and windows are open"
          data:
            priority: high
```

### Temperature-Based Heating

```yaml
automation:
  - alias: "Pre-Heat Before Cold Weather"
    trigger:
      - platform: time
        at: "05:00:00"
    action:
      - service: weather.get_forecasts
        target:
          entity_id: weather.home
        data:
          type: hourly
        response_variable: forecast
      - if:
          - condition: template
            value_template: >
              {{ forecast['weather.home'].forecast[0].temperature < 5 }}
        then:
          - service: climate.set_temperature
            target:
              entity_id: climate.living_room
            data:
              temperature: 22
              hvac_mode: heat
```

### Frost Warning

```yaml
automation:
  - alias: "Frost Warning"
    trigger:
      - platform: time
        at: "18:00:00"
    action:
      - service: weather.get_forecasts
        target:
          entity_id: weather.home
        data:
          type: hourly
        response_variable: forecast
      - if:
          - condition: template
            value_template: >
              {% set overnight = forecast['weather.home'].forecast[:12] %}
              {{ overnight | selectattr('temperature', 'lt', 2) | list | count > 0 }}
        then:
          - service: notify.mobile_app
            data:
              title: "❄️ Frost Warning"
              message: "Freezing temperatures expected tonight"
```

### Sun-Based Blinds

```yaml
automation:
  - alias: "Close Blinds on Hot Sunny Day"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 25
    condition:
      - condition: state
        entity_id: weather.home
        state: "sunny"
      - condition: sun
        after: sunrise
        after_offset: "02:00:00"
        before: sunset
        before_offset: "-02:00:00"
    action:
      - service: cover.set_cover_position
        target:
          entity_id:
            - cover.south_windows
            - cover.west_windows
        data:
          position: 30
```

### Wind Protection

```yaml
automation:
  - alias: "Retract Awning on High Wind"
    trigger:
      - platform: numeric_state
        entity_id: sensor.wind_speed
        above: 30  # km/h
    action:
      - service: cover.close_cover
        target:
          entity_id: cover.awning
      - service: notify.mobile_app
        data:
          message: "Awning retracted due to high wind ({{ states('sensor.wind_speed') }} km/h)"
```

---

## Template Sensors

### Weather Condition Icons

```yaml
template:
  - sensor:
      - name: "Weather Icon"
        state: >
          {% set condition = states('weather.home') %}
          {% set icons = {
            'clear-night': 'mdi:weather-night',
            'cloudy': 'mdi:weather-cloudy',
            'fog': 'mdi:weather-fog',
            'hail': 'mdi:weather-hail',
            'lightning': 'mdi:weather-lightning',
            'lightning-rainy': 'mdi:weather-lightning-rainy',
            'partlycloudy': 'mdi:weather-partly-cloudy',
            'pouring': 'mdi:weather-pouring',
            'rainy': 'mdi:weather-rainy',
            'snowy': 'mdi:weather-snowy',
            'snowy-rainy': 'mdi:weather-snowy-rainy',
            'sunny': 'mdi:weather-sunny',
            'windy': 'mdi:weather-windy',
            'windy-variant': 'mdi:weather-windy-variant',
            'exceptional': 'mdi:alert-circle'
          } %}
          {{ icons.get(condition, 'mdi:weather-cloudy') }}
```

### Feels Like Temperature

```yaml
template:
  - sensor:
      - name: "Feels Like Temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state: >
          {% set t = state_attr('weather.home', 'temperature') | float %}
          {% set h = state_attr('weather.home', 'humidity') | float %}
          {% set w = state_attr('weather.home', 'wind_speed') | float %}
          {% if t > 27 and h > 40 %}
            {# Heat index calculation #}
            {% set hi = -8.785 + 1.611*t + 2.339*h - 0.146*t*h %}
            {{ hi | round(1) }}
          {% elif t < 10 and w > 5 %}
            {# Wind chill calculation #}
            {% set wc = 13.12 + 0.6215*t - 11.37*(w**0.16) + 0.3965*t*(w**0.16) %}
            {{ wc | round(1) }}
          {% else %}
            {{ t | round(1) }}
          {% endif %}
```

### Weather Summary

```yaml
template:
  - sensor:
      - name: "Weather Summary"
        state: >
          {% set temp = state_attr('weather.home', 'temperature') %}
          {% set condition = states('weather.home') %}
          {% set wind = state_attr('weather.home', 'wind_speed') %}
          {{ condition | capitalize }}, {{ temp }}°C
          {% if wind > 20 %}(Windy){% endif %}
```

### Precipitation Probability

```yaml
template:
  - trigger:
      - platform: time_pattern
        hours: /1
    action:
      - service: weather.get_forecasts
        target:
          entity_id: weather.home
        data:
          type: hourly
        response_variable: forecast
    sensor:
      - name: "Rain Probability Next Hour"
        unit_of_measurement: "%"
        state: >
          {% set next = forecast['weather.home'].forecast[0] %}
          {{ next.precipitation_probability | default(0) }}
```

---

## Dashboard Cards

### Weather Forecast Card

```yaml
type: weather-forecast
entity: weather.home
show_forecast: true
forecast_type: daily
```

### Custom Weather Card (HACS)

```yaml
# Using custom:weather-card
type: custom:weather-card
entity: weather.home
details: true
forecast: true
hourly_forecast: true
```

### Glance Weather Card

```yaml
type: glance
title: Current Weather
entities:
  - entity: weather.home
    name: Condition
  - entity: sensor.outdoor_temperature
    name: Temperature
  - entity: sensor.outdoor_humidity
    name: Humidity
  - entity: sensor.wind_speed
    name: Wind
```

### Conditional Weather Alert

```yaml
type: conditional
conditions:
  - entity: weather.home
    state_not: sunny
    state_not: clear-night
    state_not: partlycloudy
card:
  type: markdown
  content: >
    ⚠️ **Weather Alert**

    Current: {{ states('weather.home') | capitalize }}

    Temperature: {{ state_attr('weather.home', 'temperature') }}°C
```

---

## Advanced Patterns

### Multi-Source Weather

```yaml
# Combine multiple weather sources
template:
  - sensor:
      - name: "Best Temperature Estimate"
        unit_of_measurement: "°C"
        device_class: temperature
        state: >
          {% set sources = [
            states('sensor.openweathermap_temperature'),
            state_attr('weather.home', 'temperature'),
            states('sensor.outdoor_sensor_temperature')
          ] | map('float', default=none) | reject('none') | list %}
          {% if sources %}
            {{ (sources | sum / sources | length) | round(1) }}
          {% else %}
            unavailable
          {% endif %}
```

### Weather Trend

```yaml
template:
  - sensor:
      - name: "Temperature Trend"
        state: >
          {% set current = state_attr('weather.home', 'temperature') | float %}
          {% set previous = states('sensor.temperature_1h_ago') | float %}
          {% set diff = current - previous %}
          {% if diff > 1 %}
            Rising
          {% elif diff < -1 %}
            Falling
          {% else %}
            Stable
          {% endif %}
        icon: >
          {% set current = state_attr('weather.home', 'temperature') | float %}
          {% set previous = states('sensor.temperature_1h_ago') | float %}
          {% set diff = current - previous %}
          {% if diff > 1 %}
            mdi:trending-up
          {% elif diff < -1 %}
            mdi:trending-down
          {% else %}
            mdi:trending-neutral
          {% endif %}
```

### Seasonal Adjustments

```yaml
template:
  - binary_sensor:
      - name: "Heating Season"
        state: >
          {% set month = now().month %}
          {{ month >= 10 or month <= 4 }}

      - name: "Cooling Season"
        state: >
          {% set month = now().month %}
          {{ month >= 5 and month <= 9 }}

automation:
  - alias: "Seasonal Temperature Adjustment"
    trigger:
      - platform: state
        entity_id: binary_sensor.heating_season
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.living_room
        data:
          preset_mode: >
            {{ 'home' if is_state('binary_sensor.heating_season', 'on') else 'eco' }}
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Forecast not updating | Check API limits, wait for next update cycle |
| Wrong location | Verify coordinates in integration settings |
| Missing attributes | Some integrations don't provide all attributes |
| Stale data | Check integration logs, verify internet connection |

### API Rate Limits

```yaml
# OpenWeatherMap free tier: 1000 calls/day
# Met.no: No hard limit, but be reasonable

# Reduce API calls:
# - Don't poll forecast every minute
# - Use trigger-based template sensors
# - Cache forecast data
```

### Debug Logging

```yaml
logger:
  default: warning
  logs:
    homeassistant.components.met: debug
    homeassistant.components.openweathermap: debug
```

---

## Reference

### Useful Links

- [Weather Integration](https://www.home-assistant.io/integrations/weather/)
- [Met.no Integration](https://www.home-assistant.io/integrations/met/)
- [OpenWeatherMap](https://www.home-assistant.io/integrations/openweathermap/)

### Weather Conditions

| Condition | Description |
|-----------|-------------|
| `clear-night` | Clear sky at night |
| `cloudy` | Overcast |
| `fog` | Foggy |
| `hail` | Hail |
| `lightning` | Lightning only |
| `lightning-rainy` | Thunderstorm |
| `partlycloudy` | Partly cloudy |
| `pouring` | Heavy rain |
| `rainy` | Rain |
| `snowy` | Snow |
| `snowy-rainy` | Sleet |
| `sunny` | Clear sky |
| `windy` | Windy |
| `windy-variant` | Windy with clouds |
| `exceptional` | Unusual conditions |
