# Utility Meter Integration

Complete guide for tracking energy, water, gas, and other utility consumption in Home Assistant.

---

## Overview

The Utility Meter integration creates sensors that track consumption over defined periods (daily, weekly, monthly) and supports multiple tariffs for cost calculations.

### Key Features

- **Cycle Tracking** - Daily, weekly, monthly, quarterly, yearly
- **Tariff Support** - Peak/off-peak, multiple rate tiers
- **Reset Options** - Automatic or manual reset
- **Statistics** - Long-term statistics compatible
- **No External Dependencies** - Pure Home Assistant solution

---

## Basic Configuration

### Simple Daily Meter

```yaml
# configuration.yaml
utility_meter:
  daily_energy:
    source: sensor.smart_meter_energy
    cycle: daily

  monthly_energy:
    source: sensor.smart_meter_energy
    cycle: monthly
```

### All Cycle Options

```yaml
utility_meter:
  # Quarter-hourly (15 min)
  energy_quarter_hourly:
    source: sensor.energy
    cycle: quarter-hourly

  # Hourly
  energy_hourly:
    source: sensor.energy
    cycle: hourly

  # Daily (resets at midnight)
  energy_daily:
    source: sensor.energy
    cycle: daily

  # Weekly (resets Monday)
  energy_weekly:
    source: sensor.energy
    cycle: weekly

  # Monthly (resets 1st of month)
  energy_monthly:
    source: sensor.energy
    cycle: monthly

  # Bimonthly (every 2 months)
  energy_bimonthly:
    source: sensor.energy
    cycle: bimonthly

  # Quarterly (every 3 months)
  energy_quarterly:
    source: sensor.energy
    cycle: quarterly

  # Yearly (resets Jan 1)
  energy_yearly:
    source: sensor.energy
    cycle: yearly
```

---

## Tariff Support

Track consumption across different rate periods.

### Two-Tariff Setup (Peak/Off-Peak)

```yaml
utility_meter:
  daily_energy:
    source: sensor.smart_meter_energy
    cycle: daily
    tariffs:
      - peak
      - offpeak

  monthly_energy:
    source: sensor.smart_meter_energy
    cycle: monthly
    tariffs:
      - peak
      - offpeak
```

### Entities Created

```yaml
# For the above configuration:
sensor.daily_energy_peak       # Peak consumption
sensor.daily_energy_offpeak    # Off-peak consumption
select.daily_energy            # Tariff selector

sensor.monthly_energy_peak
sensor.monthly_energy_offpeak
select.monthly_energy
```

### Tariff Switching Automation

```yaml
automation:
  - alias: "Energy Tariff - Peak Hours"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: select.select_option
        target:
          entity_id:
            - select.daily_energy
            - select.monthly_energy
        data:
          option: peak

  - alias: "Energy Tariff - Off-Peak Hours"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: select.select_option
        target:
          entity_id:
            - select.daily_energy
            - select.monthly_energy
        data:
          option: offpeak

  - alias: "Energy Tariff - Weekend Off-Peak"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: time
        weekday:
          - sat
          - sun
    action:
      - service: select.select_option
        target:
          entity_id:
            - select.daily_energy
            - select.monthly_energy
        data:
          option: offpeak
```

### Three-Tier Tariff (Time of Use)

```yaml
utility_meter:
  energy_tou:
    source: sensor.smart_meter_energy
    cycle: monthly
    tariffs:
      - peak      # Most expensive
      - shoulder  # Mid-price
      - offpeak   # Cheapest

# Automation for three tiers
automation:
  - alias: "TOU - Peak"
    trigger:
      - platform: time
        at: "14:00:00"  # 2 PM - 8 PM
    condition:
      - condition: time
        weekday: [mon, tue, wed, thu, fri]
    action:
      - service: select.select_option
        target:
          entity_id: select.energy_tou
        data:
          option: peak

  - alias: "TOU - Shoulder"
    trigger:
      - platform: time
        at:
          - "07:00:00"  # 7 AM - 2 PM
          - "20:00:00"  # 8 PM - 10 PM
    condition:
      - condition: time
        weekday: [mon, tue, wed, thu, fri]
    action:
      - service: select.select_option
        target:
          entity_id: select.energy_tou
        data:
          option: shoulder

  - alias: "TOU - Off-Peak"
    trigger:
      - platform: time
        at: "22:00:00"  # 10 PM - 7 AM
    action:
      - service: select.select_option
        target:
          entity_id: select.energy_tou
        data:
          option: offpeak
```

---

## Custom Reset Times

### Monthly Reset on Billing Date

```yaml
utility_meter:
  monthly_energy_billing:
    source: sensor.smart_meter_energy
    cycle: monthly
    offset:
      days: 14  # Reset on 15th of each month
```

### Weekly Reset on Different Day

```yaml
utility_meter:
  weekly_energy:
    source: sensor.smart_meter_energy
    cycle: weekly
    offset:
      days: 6  # Reset on Sunday (0=Mon, 6=Sun)
```

### Daily Reset at Different Time

```yaml
utility_meter:
  daily_energy:
    source: sensor.smart_meter_energy
    cycle: daily
    offset:
      hours: 6  # Reset at 6 AM instead of midnight
```

---

## Cost Calculation

### Template Sensor for Cost

```yaml
template:
  - sensor:
      - name: "Daily Energy Cost"
        unit_of_measurement: "€"
        device_class: monetary
        state: >
          {% set peak = states('sensor.daily_energy_peak') | float(0) %}
          {% set offpeak = states('sensor.daily_energy_offpeak') | float(0) %}
          {% set peak_rate = 0.25 %}
          {% set offpeak_rate = 0.12 %}
          {{ ((peak * peak_rate) + (offpeak * offpeak_rate)) | round(2) }}

      - name: "Monthly Energy Cost"
        unit_of_measurement: "€"
        device_class: monetary
        state: >
          {% set peak = states('sensor.monthly_energy_peak') | float(0) %}
          {% set offpeak = states('sensor.monthly_energy_offpeak') | float(0) %}
          {% set peak_rate = 0.25 %}
          {% set offpeak_rate = 0.12 %}
          {{ ((peak * peak_rate) + (offpeak * offpeak_rate)) | round(2) }}
```

### Dynamic Pricing (Spot Price)

```yaml
template:
  - sensor:
      - name: "Hourly Energy Cost"
        unit_of_measurement: "€"
        device_class: monetary
        state: >
          {% set consumption = states('sensor.hourly_energy') | float(0) %}
          {% set spot_price = states('sensor.nordpool_kwh_se3_sek_3_10_025') | float(0) %}
          {{ (consumption * spot_price) | round(2) }}
```

---

## Multiple Utility Types

### Water Meter

```yaml
utility_meter:
  daily_water:
    source: sensor.water_meter_total
    cycle: daily

  monthly_water:
    source: sensor.water_meter_total
    cycle: monthly
```

### Gas Meter

```yaml
utility_meter:
  daily_gas:
    source: sensor.gas_meter_total
    cycle: daily
    tariffs:
      - standard
      - winter  # Higher rate in winter

  monthly_gas:
    source: sensor.gas_meter_total
    cycle: monthly
```

### Per-Room Energy Tracking

```yaml
utility_meter:
  # Living room
  living_room_daily:
    source: sensor.living_room_plug_energy
    cycle: daily

  living_room_monthly:
    source: sensor.living_room_plug_energy
    cycle: monthly

  # Kitchen
  kitchen_daily:
    source: sensor.kitchen_plug_energy
    cycle: daily

  kitchen_monthly:
    source: sensor.kitchen_plug_energy
    cycle: monthly

  # Office
  office_daily:
    source: sensor.office_plug_energy
    cycle: daily

  office_monthly:
    source: sensor.office_plug_energy
    cycle: monthly
```

---

## Integration with Energy Dashboard

### Source Sensor Requirements

For Energy Dashboard compatibility:
- `device_class: energy`
- `state_class: total_increasing` or `total`
- Unit: `kWh`, `MWh`, `Wh`, or `GJ`

```yaml
# Example source sensor (template)
template:
  - sensor:
      - name: "Total Energy"
        device_class: energy
        state_class: total_increasing
        unit_of_measurement: "kWh"
        state: "{{ states('sensor.smart_meter_energy') }}"
```

### Utility Meter in Energy Dashboard

1. Go to **Settings > Dashboards > Energy**
2. Add utility meter sensors as individual devices
3. Configure cost tracking per tariff

---

## Services

### Manual Reset

```yaml
# Reset specific utility meter
service: utility_meter.reset
target:
  entity_id: sensor.daily_energy

# Reset with automation
automation:
  - alias: "Reset Energy Meter Manually"
    trigger:
      - platform: state
        entity_id: input_button.reset_energy
    action:
      - service: utility_meter.reset
        target:
          entity_id: sensor.daily_energy
```

### Calibrate Meter

```yaml
# Adjust meter value (e.g., after replacing source sensor)
service: utility_meter.calibrate
target:
  entity_id: sensor.monthly_energy
data:
  value: 150.5
```

---

## Automations

### Daily Report

```yaml
automation:
  - alias: "Daily Energy Report"
    trigger:
      - platform: time
        at: "23:55:00"
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Daily Energy Report"
          message: >
            Today: {{ states('sensor.daily_energy') | round(2) }} kWh
            Peak: {{ states('sensor.daily_energy_peak') | round(2) }} kWh
            Off-Peak: {{ states('sensor.daily_energy_offpeak') | round(2) }} kWh
            Cost: €{{ states('sensor.daily_energy_cost') }}
```

### Monthly Summary

```yaml
automation:
  - alias: "Monthly Energy Summary"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: template
        value_template: "{{ now().day == 1 }}"
    action:
      - service: notify.mobile_app
        data:
          title: "📊 Monthly Energy Summary"
          message: >
            Last month total: {{ states('sensor.monthly_energy') | round(2) }} kWh
            Estimated cost: €{{ states('sensor.monthly_energy_cost') }}
```

### High Consumption Alert

```yaml
automation:
  - alias: "High Daily Consumption Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.daily_energy
        above: 30  # kWh threshold
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ High Energy Consumption"
          message: "Daily consumption exceeded 30 kWh ({{ states('sensor.daily_energy') }} kWh)"
```

### Compare to Yesterday

```yaml
template:
  - sensor:
      - name: "Energy vs Yesterday"
        state: >
          {% set today = states('sensor.daily_energy') | float(0) %}
          {% set yesterday = state_attr('sensor.daily_energy', 'last_period') | float(0) %}
          {% if yesterday > 0 %}
            {{ ((today - yesterday) / yesterday * 100) | round(1) }}
          {% else %}
            0
          {% endif %}
        unit_of_measurement: "%"
```

---

## Dashboard Cards

### Energy Overview Card

```yaml
type: entities
title: Energy Consumption
entities:
  - entity: sensor.daily_energy
    name: Today
  - entity: sensor.weekly_energy
    name: This Week
  - entity: sensor.monthly_energy
    name: This Month
  - type: divider
  - entity: sensor.daily_energy_peak
    name: Peak (Today)
  - entity: sensor.daily_energy_offpeak
    name: Off-Peak (Today)
  - type: divider
  - entity: sensor.daily_energy_cost
    name: Cost Today
  - entity: sensor.monthly_energy_cost
    name: Cost This Month
```

### Tariff Selector Card

```yaml
type: entities
title: Energy Tariff
entities:
  - entity: select.daily_energy
    name: Current Tariff
  - type: section
    label: Today's Usage
  - entity: sensor.daily_energy_peak
  - entity: sensor.daily_energy_offpeak
```

### History Graph

```yaml
type: history-graph
title: Daily Energy History
hours_to_show: 168  # 7 days
entities:
  - entity: sensor.daily_energy
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Meter not updating | Verify source sensor is updating |
| Negative values | Source sensor may not be `total_increasing` |
| Reset not working | Check entity_id is correct |
| Wrong values after restart | Ensure source has `state_class` |

### Source Sensor Requirements

```yaml
# Good source sensor characteristics:
# - state_class: total_increasing (preferred) or total
# - Only increases (never decreases)
# - Doesn't reset unexpectedly
# - Has proper device_class

# Check your source sensor:
# Developer Tools > States > Find sensor
# Verify state_class attribute
```

### Debug Logging

```yaml
logger:
  default: warning
  logs:
    homeassistant.components.utility_meter: debug
```

---

## Best Practices

### Source Sensor Selection

```yaml
# Use sensors with:
# ✅ state_class: total_increasing
# ✅ Consistent updates
# ✅ Energy device_class
# ✅ kWh unit

# Avoid:
# ❌ Sensors that reset randomly
# ❌ Power sensors (W) - need energy (kWh)
# ❌ Sensors with missing data
```

### Tariff Automation

```yaml
# Best practices:
# 1. Use exact times for tariff switches
# 2. Handle holidays separately
# 3. Consider DST transitions
# 4. Test tariff switching thoroughly
```

### Backup Strategy

```yaml
# Utility meters store state in database
# Ensure:
# 1. Regular backups
# 2. Test restore procedures
# 3. Document calibration values
```

---

## Reference

### Useful Links

- [Utility Meter Documentation](https://www.home-assistant.io/integrations/utility_meter/)
- [Energy Dashboard](https://www.home-assistant.io/docs/energy/)
- [Template Sensors](https://www.home-assistant.io/integrations/template/)

### Cycle Summary

| Cycle | Reset Time |
|-------|------------|
| `quarter-hourly` | Every 15 minutes |
| `hourly` | Every hour |
| `daily` | Midnight |
| `weekly` | Monday midnight |
| `monthly` | 1st of month |
| `bimonthly` | Every 2 months |
| `quarterly` | Jan, Apr, Jul, Oct |
| `yearly` | January 1st |
