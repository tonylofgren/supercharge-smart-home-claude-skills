# EV Charging Integration Reference

> Smart EV charging with Home Assistant for 2024/2025

## Overview

Home Assistant enables intelligent EV charging through integration with popular chargers, dynamic pricing, solar surplus utilization, and multi-vehicle support. This guide covers everything from basic setup to advanced optimization strategies.

### Key Features

- **Charger Integration** - Support for major EV charger brands
- **Smart Charging** - Spot price and solar-aware scheduling
- **Load Balancing** - Prevent grid overload
- **Multi-Vehicle** - Manage multiple EVs and users
- **Cost Tracking** - Monitor and optimize charging costs
- **V2G Readiness** - Bidirectional charging preparation

---

## Supported EV Charger Integrations

### Easee

```yaml
# Via HACS or built-in integration
# Settings → Devices & Services → Add Integration → Easee

# Entities created:
# - sensor.easee_power (current power draw)
# - sensor.easee_session_energy (session energy)
# - sensor.easee_lifetime_energy (total energy)
# - binary_sensor.easee_cable_locked
# - switch.easee_enabled (enable/disable charger)
# - number.easee_max_charger_limit (amperage)

# Service calls
service: easee.set_charger_dynamic_limit
data:
  charger_id: "EH000000"
  current: 16  # Amperes

service: easee.action_command
data:
  charger_id: "EH000000"
  action_command: pause  # or resume, stop, start
```

### Wallbox

```yaml
# Via HACS: Wallbox integration
# Settings → Devices & Services → Add Integration → Wallbox

# Entities:
# - sensor.wallbox_charging_power
# - sensor.wallbox_added_energy
# - sensor.wallbox_charging_speed
# - switch.wallbox_pause_resume
# - number.wallbox_max_charging_current

# Service calls
service: wallbox.set_max_charging_current
data:
  charging_current: 32
  station: 12345

service: wallbox.pause_charging
data:
  station: 12345
```

### Tesla Wall Connector

```yaml
# Via Tesla integration (vehicle + wall connector)
# Gen 3 Wall Connector with WiFi

# Configuration
tesla_wall_connector:
  host: 192.168.1.100

# Entities:
# - sensor.tesla_wall_connector_power
# - sensor.tesla_wall_connector_energy
# - switch.tesla_wall_connector_charging
```

### Zaptec

```yaml
# Via HACS: Zaptec integration
# Settings → Devices & Services → Add Integration → Zaptec

# Entities:
# - sensor.zaptec_charger_power
# - sensor.zaptec_total_energy
# - binary_sensor.zaptec_is_charging
# - switch.zaptec_charger

# Service calls
service: zaptec.authorize_charging
data:
  charger_id: "ZAP000000"

service: zaptec.set_available_current
data:
  charger_id: "ZAP000000"
  available_current: 16
```

### OpenEVSE

```yaml
# Via HACS: OpenEVSE integration
# Local API access

# Configuration
openevse:
  host: 192.168.1.100

# Entities:
# - sensor.openevse_power
# - sensor.openevse_session_energy
# - sensor.openevse_total_energy
# - switch.openevse_charging
# - number.openevse_max_current

# Set charging current via service
service: openevse.set_current
data:
  current: 24
```

### Generic OCPP

```yaml
# Via HACS: OCPP integration
# Supports OCPP 1.6 compatible chargers

# Configuration in HA:
# Settings → Devices & Services → Add Integration → OCPP

ocpp:
  host: 0.0.0.0
  port: 9000
  ssl: false
  websocket_ping_interval: 30
  skip_schema_validation: false

# Entities vary by charger capabilities
```

### Charge Point (via REST)

```yaml
# Custom integration via REST sensors
rest:
  - resource: https://api.chargepoint.com/station/status
    headers:
      Authorization: "Bearer TOKEN"
    scan_interval: 60
    sensor:
      - name: "ChargePoint Status"
        value_template: "{{ value_json.status }}"
      - name: "ChargePoint Power"
        value_template: "{{ value_json.power_kw }}"
        unit_of_measurement: "kW"
```

---

## Basic Automations

### Start/Stop Charging

```yaml
# Start charging at specific time
automation:
  - id: ev_start_charging_scheduled
    alias: "EV - Start Scheduled Charging"
    trigger:
      - platform: time
        at: "23:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
      - condition: numeric_state
        entity_id: sensor.ev_battery_level
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger

# Stop at target SoC
automation:
  - id: ev_stop_at_target
    alias: "EV - Stop at Target SoC"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ev_battery_level
        above: 80
    condition:
      - condition: state
        entity_id: switch.ev_charger
        state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.ev_charger
      - service: notify.mobile_app
        data:
          title: "EV Charging"
          message: "Charging complete! Battery at {{ states('sensor.ev_battery_level') }}%"
```

### Manual Charging Control

```yaml
# Script for easy control
script:
  ev_start_charging:
    alias: "Start EV Charging"
    sequence:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
      - service: notify.mobile_app
        data:
          message: "EV charging started"

  ev_stop_charging:
    alias: "Stop EV Charging"
    sequence:
      - service: switch.turn_off
        target:
          entity_id: switch.ev_charger
      - service: notify.mobile_app
        data:
          message: >
            EV charging stopped.
            Added {{ states('sensor.ev_session_energy') }} kWh
```

### Connection Notifications

```yaml
automation:
  - id: ev_connected_notification
    alias: "EV - Connected Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.ev_connected
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "EV Connected"
          message: >
            Battery: {{ states('sensor.ev_battery_level') }}%
            {{ 'Charging will start at cheap price' if is_state('input_boolean.ev_smart_charging', 'on') else 'Manual charging mode' }}
          data:
            actions:
              - action: "START_CHARGING"
                title: "Start Now"
              - action: "SMART_CHARGE"
                title: "Smart Charge"
```

---

## Smart Charging Patterns

### Spot Price Optimization

```yaml
# Helper entities
input_number:
  ev_price_threshold:
    name: "EV Price Threshold"
    min: 0
    max: 2
    step: 0.05
    unit_of_measurement: "SEK/kWh"
    initial: 0.5

input_datetime:
  ev_departure_time:
    name: "EV Departure Time"
    has_date: false
    has_time: true

input_number:
  ev_target_soc:
    name: "EV Target SoC"
    min: 50
    max: 100
    step: 5
    unit_of_measurement: "%"
    initial: 80

# Price-based charging automation
automation:
  - id: ev_cheap_price_charging
    alias: "EV - Charge at Cheap Price"
    trigger:
      - platform: state
        entity_id: sensor.nordpool_kwh_se3_sek_3_10_025
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
      - condition: state
        entity_id: input_boolean.ev_smart_charging
        state: "on"
      - condition: numeric_state
        entity_id: sensor.ev_battery_level
        below: input_number.ev_target_soc
    action:
      - choose:
          # Start charging if cheap
          - conditions:
              - condition: template
                value_template: >
                  {{ states('sensor.nordpool_kwh_se3_sek_3_10_025') | float <
                     states('input_number.ev_price_threshold') | float }}
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.ev_charger
          # Stop if expensive
          - conditions:
              - condition: template
                value_template: >
                  {{ states('sensor.nordpool_kwh_se3_sek_3_10_025') | float >
                     states('input_number.ev_price_threshold') | float * 1.5 }}
            sequence:
              - service: switch.turn_off
                target:
                  entity_id: switch.ev_charger

# Find cheapest hours for target charge
template:
  - sensor:
      - name: "EV Cheapest Charging Hours"
        state: >
          {% set prices = state_attr('sensor.nordpool_kwh_se3_sek_3_10_025', 'raw_today') %}
          {% set current_soc = states('sensor.ev_battery_level') | float(50) %}
          {% set target_soc = states('input_number.ev_target_soc') | float(80) %}
          {% set battery_capacity = 64 %}  {# kWh - adjust for your EV #}
          {% set charge_power = 11 %}  {# kW - your charger power #}

          {% set energy_needed = (target_soc - current_soc) / 100 * battery_capacity %}
          {% set hours_needed = (energy_needed / charge_power) | round(0, 'ceil') %}

          {% if prices and hours_needed > 0 %}
            {% set sorted_prices = prices | sort(attribute='value') %}
            {% set cheapest = sorted_prices[:hours_needed] %}
            {{ cheapest | map(attribute='start') | list }}
          {% else %}
            []
          {% endif %}
```

### Solar Surplus Charging

```yaml
# Helpers
input_number:
  ev_min_solar_surplus:
    name: "Minimum Solar Surplus for Charging"
    min: 1
    max: 10
    step: 0.5
    unit_of_measurement: "kW"
    initial: 3

input_boolean:
  ev_solar_only_charging:
    name: "Solar Only Charging Mode"

# Calculate surplus
template:
  - sensor:
      - name: "Solar Surplus"
        unit_of_measurement: "kW"
        device_class: power
        state: >
          {% set solar = states('sensor.solar_production') | float(0) %}
          {% set consumption = states('sensor.home_consumption') | float(0) %}
          {% set ev = states('sensor.ev_charger_power') | float(0) %}
          {{ ((solar - consumption + ev) / 1000) | round(2) }}

# Solar surplus automation
automation:
  - id: ev_solar_surplus_charging
    alias: "EV - Solar Surplus Charging"
    mode: restart
    trigger:
      - platform: state
        entity_id: sensor.solar_surplus
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
      - condition: state
        entity_id: input_boolean.ev_solar_only_charging
        state: "on"
      - condition: sun
        after: sunrise
        before: sunset
    action:
      - choose:
          # Enough surplus - charge
          - conditions:
              - condition: numeric_state
                entity_id: sensor.solar_surplus
                above: input_number.ev_min_solar_surplus
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.ev_charger
              # Adjust charging current based on surplus
              - service: number.set_value
                target:
                  entity_id: number.ev_charger_current
                data:
                  value: >
                    {% set surplus = states('sensor.solar_surplus') | float %}
                    {% set voltage = 230 %}
                    {% set phases = 3 %}
                    {% set amps = (surplus * 1000) / (voltage * phases) %}
                    {{ [32, [6, amps | int] | max] | min }}
          # Not enough surplus - stop
          - conditions:
              - condition: numeric_state
                entity_id: sensor.solar_surplus
                below: 2
            sequence:
              - delay:
                  minutes: 5  # Debounce cloud passing
              - condition: numeric_state
                entity_id: sensor.solar_surplus
                below: 2
              - service: switch.turn_off
                target:
                  entity_id: switch.ev_charger
```

### Departure Time Scheduling

```yaml
# Calculate optimal charging schedule
template:
  - sensor:
      - name: "EV Charging Schedule"
        state: >
          {% set departure = today_at(states('input_datetime.ev_departure_time')) %}
          {% set current_soc = states('sensor.ev_battery_level') | float(50) %}
          {% set target_soc = states('input_number.ev_target_soc') | float(80) %}
          {% set battery_kwh = 64 %}
          {% set charge_rate = 11 %}  {# kW #}

          {% set energy_needed = (target_soc - current_soc) / 100 * battery_kwh %}
          {% set hours_needed = (energy_needed / charge_rate) %}
          {% set start_time = departure - timedelta(hours=hours_needed) %}

          {% if start_time > now() %}
            Start: {{ start_time.strftime('%H:%M') }}
          {% else %}
            Start immediately
          {% endif %}
        attributes:
          hours_needed: >
            {% set current_soc = states('sensor.ev_battery_level') | float(50) %}
            {% set target_soc = states('input_number.ev_target_soc') | float(80) %}
            {% set battery_kwh = 64 %}
            {% set charge_rate = 11 %}
            {{ ((target_soc - current_soc) / 100 * battery_kwh / charge_rate) | round(1) }}
          estimated_cost: >
            {% set hours = this.attributes.hours_needed | float(0) %}
            {% set rate = 11 %}  {# kW #}
            {% set price = states('sensor.electricity_price') | float(1) %}
            {{ (hours * rate * price) | round(2) }}

# Automation to start at calculated time
automation:
  - id: ev_departure_schedule
    alias: "EV - Departure Time Charging"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
      - condition: state
        entity_id: input_boolean.ev_smart_charging
        state: "on"
      - condition: template
        value_template: >
          {% set departure = today_at(states('input_datetime.ev_departure_time')) %}
          {% set hours_needed = state_attr('sensor.ev_charging_schedule', 'hours_needed') | float(0) %}
          {% set start_time = departure - timedelta(hours=hours_needed) %}
          {{ start_time <= now() < departure }}
      - condition: numeric_state
        entity_id: sensor.ev_battery_level
        below: input_number.ev_target_soc
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

### Grid Load Balancing

```yaml
# Prevent grid overload with dynamic charging
template:
  - sensor:
      - name: "Available Charging Power"
        unit_of_measurement: "kW"
        device_class: power
        state: >
          {% set main_fuse = 25 %}  {# Amperes #}
          {% set phases = 3 %}
          {% set voltage = 230 %}
          {% set max_power = main_fuse * phases * voltage / 1000 %}

          {% set home_consumption = states('sensor.home_power') | float(0) / 1000 %}
          {% set ev_power = states('sensor.ev_charger_power') | float(0) / 1000 %}

          {% set available = max_power - home_consumption + ev_power %}
          {{ [0, available - 1] | max | round(1) }}  {# 1kW safety margin #}

# Dynamic current adjustment
automation:
  - id: ev_load_balancing
    alias: "EV - Load Balancing"
    mode: restart
    trigger:
      - platform: state
        entity_id: sensor.available_charging_power
    condition:
      - condition: state
        entity_id: switch.ev_charger
        state: "on"
    action:
      - variables:
          available_kw: "{{ states('sensor.available_charging_power') | float(0) }}"
          available_amps: "{{ (available_kw * 1000 / (230 * 3)) | int }}"
          target_amps: "{{ [32, [6, available_amps] | max] | min }}"
      - choose:
          # Enough power - adjust current
          - conditions:
              - condition: template
                value_template: "{{ available_amps >= 6 }}"
            sequence:
              - service: number.set_value
                target:
                  entity_id: number.ev_charger_current
                data:
                  value: "{{ target_amps }}"
          # Not enough power - pause charging
        default:
          - service: switch.turn_off
            target:
              entity_id: switch.ev_charger
          - service: notify.mobile_app
            data:
              title: "EV Charging Paused"
              message: "High home consumption - charging paused"
```

---

## Multi-Vehicle Support

### Vehicle Detection

```yaml
# Detect which vehicle is connected based on charging characteristics
template:
  - sensor:
      - name: "Connected Vehicle"
        state: >
          {% set power = states('sensor.ev_charger_power') | float(0) %}
          {% set current = states('sensor.ev_charger_current') | float(0) %}

          {# Each vehicle has different max charging rate #}
          {% if power > 10000 %}
            Tesla Model 3
          {% elif power > 7000 %}
            VW ID.4
          {% elif power > 3000 %}
            Peugeot e-208
          {% elif current > 0 %}
            Unknown Vehicle
          {% else %}
            None
          {% endif %}

# Or use RFID/NFC tags for identification
automation:
  - id: ev_rfid_identification
    alias: "EV - RFID Vehicle ID"
    trigger:
      - platform: tag
        tag_id: "vehicle_1_tag_id"
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.connected_vehicle
        data:
          option: "Tesla Model 3"
```

### Per-Vehicle Settings

```yaml
# Vehicle profiles
input_select:
  connected_vehicle:
    name: "Connected Vehicle"
    options:
      - Tesla Model 3
      - VW ID.4
      - Peugeot e-208
      - Unknown

# Vehicle-specific settings via template
template:
  - sensor:
      - name: "Vehicle Battery Capacity"
        unit_of_measurement: "kWh"
        state: >
          {% set vehicle = states('input_select.connected_vehicle') %}
          {% set capacities = {
            'Tesla Model 3': 60,
            'VW ID.4': 77,
            'Peugeot e-208': 50,
            'Unknown': 50
          } %}
          {{ capacities.get(vehicle, 50) }}

      - name: "Vehicle Max Charge Rate"
        unit_of_measurement: "kW"
        state: >
          {% set vehicle = states('input_select.connected_vehicle') %}
          {% set rates = {
            'Tesla Model 3': 11,
            'VW ID.4': 11,
            'Peugeot e-208': 7.4,
            'Unknown': 7.4
          } %}
          {{ rates.get(vehicle, 7.4) }}
```

### User-Based Preferences

```yaml
# Different users have different needs
input_select:
  ev_active_user:
    name: "Active EV User"
    options:
      - John
      - Jane
      - Guest

# User-specific automations
automation:
  - id: ev_user_john_preferences
    alias: "EV - John's Charging Preferences"
    trigger:
      - platform: state
        entity_id: input_select.ev_active_user
        to: "John"
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
    action:
      # John wants 80% by 7:00 AM
      - service: input_number.set_value
        target:
          entity_id: input_number.ev_target_soc
        data:
          value: 80
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.ev_departure_time
        data:
          time: "07:00:00"

  - id: ev_user_jane_preferences
    alias: "EV - Jane's Charging Preferences"
    trigger:
      - platform: state
        entity_id: input_select.ev_active_user
        to: "Jane"
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
    action:
      # Jane only wants solar charging to 100%
      - service: input_number.set_value
        target:
          entity_id: input_number.ev_target_soc
        data:
          value: 100
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.ev_solar_only_charging
```

### Charging Queue (Multiple Chargers)

```yaml
# For multiple chargers with limited power
input_select:
  ev_charging_queue:
    name: "Charging Priority Queue"
    options:
      - Charger 1
      - Charger 2
      - Both

automation:
  - id: ev_queue_management
    alias: "EV - Queue Management"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.charger_1_connected
          - binary_sensor.charger_2_connected
    action:
      - choose:
          # Both connected - alternate or priority
          - conditions:
              - condition: state
                entity_id: binary_sensor.charger_1_connected
                state: "on"
              - condition: state
                entity_id: binary_sensor.charger_2_connected
                state: "on"
            sequence:
              # Charge the one with lower SoC first
              - if:
                  - condition: template
                    value_template: >
                      {{ states('sensor.charger_1_soc') | float <
                         states('sensor.charger_2_soc') | float }}
                then:
                  - service: switch.turn_on
                    target:
                      entity_id: switch.charger_1
                  - service: switch.turn_off
                    target:
                      entity_id: switch.charger_2
                else:
                  - service: switch.turn_on
                    target:
                      entity_id: switch.charger_2
                  - service: switch.turn_off
                    target:
                      entity_id: switch.charger_1
```

---

## V2G Readiness

### Bidirectional Charging Concepts

```yaml
# V2G (Vehicle-to-Grid) allows discharging EV to home/grid
# Currently limited hardware support (Wallbox Quasar, etc.)

# Monitor for future V2G capability
template:
  - binary_sensor:
      - name: "V2G Profitable"
        state: >
          {% set sell_price = states('sensor.electricity_sell_price') | float(0) %}
          {% set buy_price = states('sensor.electricity_buy_price') | float(0) %}
          {% set battery_degradation_cost = 0.05 %}  {# EUR/kWh estimate #}
          {% set efficiency_loss = 0.15 %}  {# 15% round-trip loss #}

          {% set profit_margin = sell_price - buy_price * (1 + efficiency_loss) - battery_degradation_cost %}
          {{ profit_margin > 0.10 }}  {# Minimum 0.10 EUR/kWh profit #}

# Future V2G automation template
automation:
  - id: v2g_discharge_to_home
    alias: "V2G - Discharge to Home"
    trigger:
      - platform: state
        entity_id: binary_sensor.v2g_profitable
        to: "on"
    condition:
      - condition: state
        entity_id: binary_sensor.ev_connected
        state: "on"
      - condition: numeric_state
        entity_id: sensor.ev_battery_level
        above: 50  # Keep minimum SoC
      - condition: state
        entity_id: input_boolean.v2g_enabled
        state: "on"
    action:
      # Set charger to discharge mode (future API)
      - service: ev_charger.set_mode
        data:
          mode: discharge
          power: 5000  # 5kW discharge rate
```

### Grid Services Patterns

```yaml
# Frequency regulation readiness
template:
  - sensor:
      - name: "EV Grid Service Availability"
        state: >
          {% set soc = states('sensor.ev_battery_level') | float(0) %}
          {% set connected = is_state('binary_sensor.ev_connected', 'on') %}
          {% set min_soc = 30 %}
          {% set max_soc = 90 %}

          {% if not connected %}
            Unavailable
          {% elif soc < min_soc %}
            Below minimum
          {% elif soc > max_soc %}
            Above maximum
          {% else %}
            Available
          {% endif %}
        attributes:
          discharge_capacity: >
            {% set soc = states('sensor.ev_battery_level') | float(0) %}
            {% set min_soc = 30 %}
            {% set capacity = 64 %}  {# kWh #}
            {{ ((soc - min_soc) / 100 * capacity) | round(1) }}
          charge_capacity: >
            {% set soc = states('sensor.ev_battery_level') | float(0) %}
            {% set max_soc = 90 %}
            {% set capacity = 64 %}
            {{ ((max_soc - soc) / 100 * capacity) | round(1) }}
```

---

## Energy Dashboard Integration

### Charging Statistics

```yaml
# Track daily/monthly charging
utility_meter:
  ev_daily_energy:
    source: sensor.ev_charger_energy
    cycle: daily

  ev_monthly_energy:
    source: sensor.ev_charger_energy
    cycle: monthly

  ev_yearly_energy:
    source: sensor.ev_charger_energy
    cycle: yearly
```

### Cost Tracking

```yaml
template:
  - sensor:
      # Session cost
      - name: "EV Session Cost"
        unit_of_measurement: "SEK"
        device_class: monetary
        state: >
          {% set energy = states('sensor.ev_session_energy') | float(0) %}
          {% set avg_price = state_attr('sensor.nordpool', 'average') | float(1) %}
          {{ (energy * avg_price) | round(2) }}

      # Daily cost
      - name: "EV Daily Cost"
        unit_of_measurement: "SEK"
        device_class: monetary
        state: >
          {% set energy = states('sensor.ev_daily_energy') | float(0) %}
          {% set avg_price = state_attr('sensor.nordpool', 'average') | float(1) %}
          {{ (energy * avg_price) | round(2) }}

      # Monthly cost
      - name: "EV Monthly Cost"
        unit_of_measurement: "SEK"
        device_class: monetary
        state: >
          {% set energy = states('sensor.ev_monthly_energy') | float(0) %}
          {% set avg_price = state_attr('sensor.nordpool', 'average') | float(1) %}
          {{ (energy * avg_price) | round(2) }}

      # Cost per km (efficiency tracking)
      - name: "EV Cost per km"
        unit_of_measurement: "SEK/km"
        state: >
          {% set efficiency = 0.18 %}  {# kWh/km - adjust for your EV #}
          {% set price = states('sensor.electricity_price') | float(1) %}
          {{ (efficiency * price) | round(2) }}
```

### Dashboard Card

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: EV Charging
    subtitle: >
      {{ states('input_select.connected_vehicle') }}
      {% if is_state('binary_sensor.ev_connected', 'on') %}
        connected
      {% else %}
        not connected
      {% endif %}

  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.ev_battery_level
        name: Battery
        icon: mdi:battery-charging

      - type: custom:mushroom-entity-card
        entity: sensor.ev_charger_power
        name: Power
        icon: mdi:flash

  - type: custom:mushroom-entity-card
    entity: sensor.ev_session_cost
    name: Session Cost
    icon: mdi:currency-usd

  - type: entities
    entities:
      - entity: input_datetime.ev_departure_time
        name: Departure
      - entity: input_number.ev_target_soc
        name: Target SoC
      - entity: input_boolean.ev_smart_charging
        name: Smart Charging
      - entity: input_boolean.ev_solar_only_charging
        name: Solar Only
```

---

## Troubleshooting

### Charger Not Responding

```yaml
# Check connectivity
# 1. Verify charger is online
# 2. Check cloud service status (if applicable)
# 3. Test local API/MQTT connection

# Restart automation on error
automation:
  - id: ev_charger_watchdog
    alias: "EV - Charger Watchdog"
    trigger:
      - platform: state
        entity_id: switch.ev_charger
        to: "unavailable"
        for:
          minutes: 5
    action:
      - service: homeassistant.reload_config_entry
        data:
          entry_id: "charger_config_entry_id"
      - service: notify.mobile_app
        data:
          title: "EV Charger"
          message: "Charger went unavailable - attempting reconnection"
```

### Charging Doesn't Start

```yaml
# Common issues:
# 1. Vehicle not properly connected
# 2. Charging lock engaged
# 3. Vehicle schedule overriding HA
# 4. Grid fault protection

# Debug template
template:
  - sensor:
      - name: "EV Charging Debug"
        state: >
          {% set connected = is_state('binary_sensor.ev_connected', 'on') %}
          {% set enabled = is_state('switch.ev_charger_enabled', 'on') %}
          {% set power = states('sensor.ev_charger_power') | float(0) %}
          {% set fault = is_state('binary_sensor.ev_charger_fault', 'on') %}

          {% if fault %}
            Charger Fault
          {% elif not connected %}
            Not Connected
          {% elif not enabled %}
            Charger Disabled
          {% elif power == 0 %}
            Ready but not charging
          {% else %}
            Charging {{ power }}W
          {% endif %}
```

---

## Best Practices

### Battery Health

```yaml
# Limit daily charging to 80% for battery longevity
# Only charge to 100% before long trips

input_number:
  ev_daily_max_soc:
    name: "Daily Max SoC"
    min: 50
    max: 80
    initial: 80

  ev_trip_max_soc:
    name: "Trip Max SoC"
    min: 80
    max: 100
    initial: 100

# Use daily limit normally
# Switch to trip limit when needed
```

### Notification Strategy

```yaml
# Key notifications only
automation:
  - id: ev_important_notifications
    alias: "EV - Important Notifications"
    trigger:
      - platform: state
        entity_id: sensor.ev_battery_level
    action:
      - choose:
          # Target reached
          - conditions:
              - condition: template
                value_template: >
                  {{ trigger.to_state.state | float >=
                     states('input_number.ev_target_soc') | float }}
            sequence:
              - service: notify.mobile_app
                data:
                  title: "EV Ready"
                  message: "Battery at {{ states('sensor.ev_battery_level') }}%"

# Avoid notification spam during charging
```

---

## Related References

- [Energy Optimization](automations.md#energy-optimization) - Energy automation patterns
- [Nordpool Integration](integrations-common.md#nordpool) - Spot price integration
- [Dashboards](dashboards.md) - Dashboard configuration
- [Templates](jinja2-templates.md) - Template syntax
