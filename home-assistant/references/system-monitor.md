# System Monitor Integration

Complete guide for monitoring Home Assistant system health - CPU, memory, disk, and network.

---

## Overview

The System Monitor integration provides sensors for tracking the health and performance of your Home Assistant host system.

### Available Metrics

| Category | Sensors |
|----------|---------|
| **Processor** | CPU usage, load averages |
| **Memory** | RAM usage, swap usage |
| **Disk** | Disk usage, I/O stats |
| **Network** | Throughput, packets |
| **System** | Last boot, process count |

---

## Installation

### Via UI (Recommended)

1. Go to **Settings > Devices & Services**
2. Click **Add Integration**
3. Search for **System Monitor**
4. Select sensors to monitor
5. Configure update interval

### Via YAML

```yaml
# configuration.yaml
sensor:
  - platform: systemmonitor
    resources:
      # Processor
      - type: processor_use
      - type: processor_temperature
      - type: load_1m
      - type: load_5m
      - type: load_15m

      # Memory
      - type: memory_use_percent
      - type: memory_use
      - type: memory_free
      - type: swap_use_percent
      - type: swap_use
      - type: swap_free

      # Disk
      - type: disk_use_percent
        arg: /
      - type: disk_use
        arg: /
      - type: disk_free
        arg: /
      - type: disk_use_percent
        arg: /home

      # Network
      - type: network_in
        arg: eth0
      - type: network_out
        arg: eth0
      - type: throughput_network_in
        arg: eth0
      - type: throughput_network_out
        arg: eth0
      - type: packets_in
        arg: eth0
      - type: packets_out
        arg: eth0
      - type: ipv4_address
        arg: eth0
      - type: ipv6_address
        arg: eth0

      # System
      - type: last_boot
      - type: process
        arg: Home Assistant
```

---

## Sensor Types

### Processor Sensors

```yaml
# CPU Usage (percentage)
sensor:
  - platform: systemmonitor
    resources:
      - type: processor_use      # Overall CPU usage %

      # CPU temperature (if available)
      - type: processor_temperature

      # Load averages (Unix systems)
      - type: load_1m           # 1 minute average
      - type: load_5m           # 5 minute average
      - type: load_15m          # 15 minute average
```

### Memory Sensors

```yaml
sensor:
  - platform: systemmonitor
    resources:
      # RAM
      - type: memory_use_percent  # % of RAM used
      - type: memory_use          # Bytes used
      - type: memory_free         # Bytes free

      # Swap
      - type: swap_use_percent    # % of swap used
      - type: swap_use            # Bytes used
      - type: swap_free           # Bytes free
```

### Disk Sensors

```yaml
sensor:
  - platform: systemmonitor
    resources:
      # Root filesystem
      - type: disk_use_percent
        arg: /                    # Path to monitor
      - type: disk_use
        arg: /
      - type: disk_free
        arg: /

      # Additional partitions
      - type: disk_use_percent
        arg: /media/storage
      - type: disk_use_percent
        arg: /mnt/backup
```

### Network Sensors

```yaml
sensor:
  - platform: systemmonitor
    resources:
      # Cumulative data transfer (since boot)
      - type: network_in
        arg: eth0               # Interface name
      - type: network_out
        arg: eth0

      # Current throughput (bytes/sec)
      - type: throughput_network_in
        arg: eth0
      - type: throughput_network_out
        arg: eth0

      # Packet counts
      - type: packets_in
        arg: eth0
      - type: packets_out
        arg: eth0

      # IP addresses
      - type: ipv4_address
        arg: eth0
      - type: ipv6_address
        arg: eth0
```

### System Sensors

```yaml
sensor:
  - platform: systemmonitor
    resources:
      # Boot time
      - type: last_boot

      # Process monitoring
      - type: process
        arg: Home Assistant      # Process name
      - type: process
        arg: mosquitto
      - type: process
        arg: nginx
```

---

## Finding Interface Names

### Linux/Raspberry Pi

```bash
# List network interfaces
ip link show

# Or
ifconfig -a

# Common names:
# eth0 - Wired ethernet
# wlan0 - WiFi
# enp0s3 - Newer naming (ethernet)
# wlp2s0 - Newer naming (WiFi)
```

### Home Assistant OS

```bash
# Via SSH add-on or console
ha network info
```

---

## Automations

### High CPU Alert

```yaml
automation:
  - alias: "High CPU Usage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.processor_use
        above: 80
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ High CPU Usage"
          message: "CPU usage at {{ states('sensor.processor_use') }}% for 5 minutes"
```

### Low Disk Space Alert

```yaml
automation:
  - alias: "Low Disk Space Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.disk_use_percent
        above: 85
    action:
      - service: notify.mobile_app
        data:
          title: "💾 Low Disk Space"
          message: "Disk usage at {{ states('sensor.disk_use_percent') }}%"
      - service: persistent_notification.create
        data:
          title: "Low Disk Space Warning"
          message: "Disk is {{ states('sensor.disk_use_percent') }}% full. Consider cleanup."
```

### High Memory Usage

```yaml
automation:
  - alias: "High Memory Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.memory_use_percent
        above: 90
        for: "00:10:00"
    action:
      - service: notify.mobile_app
        data:
          title: "🧠 High Memory Usage"
          message: "Memory at {{ states('sensor.memory_use_percent') }}%"
```

### System Reboot Notification

```yaml
automation:
  - alias: "System Rebooted"
    trigger:
      - platform: state
        entity_id: sensor.last_boot
    condition:
      - condition: template
        value_template: "{{ trigger.from_state.state != 'unknown' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "🔄 System Rebooted"
          message: "Home Assistant host rebooted at {{ states('sensor.last_boot') }}"
```

### Uptime Tracking

```yaml
template:
  - sensor:
      - name: "System Uptime"
        state: >
          {% set boot = as_timestamp(states('sensor.last_boot')) %}
          {% set now_ts = as_timestamp(now()) %}
          {% set uptime = now_ts - boot %}
          {% set days = (uptime // 86400) | int %}
          {% set hours = ((uptime % 86400) // 3600) | int %}
          {% set minutes = ((uptime % 3600) // 60) | int %}
          {{ days }}d {{ hours }}h {{ minutes }}m
        icon: mdi:clock-outline
```

---

## Dashboard Cards

### System Overview Card

```yaml
type: entities
title: System Health
entities:
  - entity: sensor.processor_use
    name: CPU Usage
  - entity: sensor.memory_use_percent
    name: Memory Usage
  - entity: sensor.disk_use_percent
    name: Disk Usage
  - entity: sensor.swap_use_percent
    name: Swap Usage
  - type: divider
  - entity: sensor.system_uptime
    name: Uptime
  - entity: sensor.last_boot
    name: Last Boot
```

### Gauge Cards

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.processor_use
    name: CPU
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 60
      red: 80

  - type: gauge
    entity: sensor.memory_use_percent
    name: Memory
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 70
      red: 90

  - type: gauge
    entity: sensor.disk_use_percent
    name: Disk
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 70
      red: 85
```

### Network Statistics Card

```yaml
type: entities
title: Network
entities:
  - entity: sensor.network_throughput_in_eth0
    name: Download Speed
  - entity: sensor.network_throughput_out_eth0
    name: Upload Speed
  - type: divider
  - entity: sensor.network_in_eth0
    name: Total Downloaded
  - entity: sensor.network_out_eth0
    name: Total Uploaded
  - type: divider
  - entity: sensor.ipv4_address_eth0
    name: IP Address
```

### History Graph

```yaml
type: history-graph
title: System Load (24h)
hours_to_show: 24
entities:
  - entity: sensor.processor_use
    name: CPU
  - entity: sensor.memory_use_percent
    name: Memory
  - entity: sensor.load_5m
    name: Load (5m)
```

---

## Template Sensors

### Disk Space Free (Human Readable)

```yaml
template:
  - sensor:
      - name: "Disk Free Formatted"
        state: >
          {% set free = states('sensor.disk_free') | float(0) %}
          {% if free > 1073741824 %}
            {{ (free / 1073741824) | round(1) }} GB
          {% elif free > 1048576 %}
            {{ (free / 1048576) | round(1) }} MB
          {% else %}
            {{ (free / 1024) | round(1) }} KB
          {% endif %}
```

### Network Speed (Formatted)

```yaml
template:
  - sensor:
      - name: "Download Speed"
        state: >
          {% set speed = states('sensor.network_throughput_in_eth0') | float(0) %}
          {% if speed > 1048576 %}
            {{ (speed / 1048576) | round(2) }} MB/s
          {% elif speed > 1024 %}
            {{ (speed / 1024) | round(2) }} KB/s
          {% else %}
            {{ speed | round(0) }} B/s
          {% endif %}
        icon: mdi:download
```

### CPU Temperature Status

```yaml
template:
  - sensor:
      - name: "CPU Temperature Status"
        state: >
          {% set temp = states('sensor.processor_temperature') | float(0) %}
          {% if temp < 50 %}
            Normal
          {% elif temp < 70 %}
            Warm
          {% elif temp < 80 %}
            Hot
          {% else %}
            Critical
          {% endif %}
        icon: >
          {% set temp = states('sensor.processor_temperature') | float(0) %}
          {% if temp < 50 %}
            mdi:thermometer-low
          {% elif temp < 70 %}
            mdi:thermometer
          {% else %}
            mdi:thermometer-high
          {% endif %}
```

---

## Integration with Other Sensors

### Raspberry Pi Specific

```yaml
# Combine with Raspberry Pi Power Supply Checker
# and Raspberry Pi OS sensors

sensor:
  - platform: systemmonitor
    resources:
      - type: processor_use
      - type: processor_temperature
      - type: memory_use_percent
      - type: disk_use_percent
        arg: /

  # Additional Pi sensors via command line
  - platform: command_line
    name: "GPU Temperature"
    command: "vcgencmd measure_temp"
    value_template: "{{ value.split('=')[1].split(\"'\")[0] }}"
    unit_of_measurement: "°C"
```

### Docker Container Monitoring

```yaml
# If running in Docker, monitor container stats
sensor:
  - platform: systemmonitor
    resources:
      - type: processor_use
      - type: memory_use_percent

# For detailed container monitoring, use:
# - cAdvisor integration
# - Docker Monitor (HACS)
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Sensors unavailable | Check sensor type supported on your OS |
| Network sensors missing | Verify interface name with `ip link` |
| Disk sensors wrong | Check mount point path |
| Temperature unavailable | May not be exposed by hardware |

### Check Available Resources

```yaml
# Not all sensors available on all systems:
# - processor_temperature: Needs hardware support
# - load_*: Unix/Linux only
# - Some network stats: OS dependent
```

### Debug Logging

```yaml
logger:
  default: warning
  logs:
    homeassistant.components.systemmonitor: debug
```

---

## Best Practices

### Update Interval

```yaml
# Default scan interval: 1 minute
# Adjust via integration options if needed

# For high-frequency monitoring, consider
# dedicated monitoring tools (Prometheus, Grafana)
```

### Resource Selection

```yaml
# Don't monitor everything - select what matters:
# ✅ processor_use - Essential
# ✅ memory_use_percent - Essential
# ✅ disk_use_percent (/) - Essential
# ⚠️ Network throughput - Only if needed
# ⚠️ Load averages - Only on Linux
```

### Alert Thresholds

```yaml
# Recommended alert thresholds:
# CPU: > 80% for 5+ minutes
# Memory: > 90% for 10+ minutes
# Disk: > 85% (act before 95%)
# Swap: > 50% (indicates memory pressure)
```

---

## Reference

### Useful Links

- [System Monitor Documentation](https://www.home-assistant.io/integrations/systemmonitor/)
- [Home Assistant Analytics](https://analytics.home-assistant.io/)

### Sensor Units

| Sensor Type | Unit |
|-------------|------|
| `processor_use` | % |
| `processor_temperature` | °C |
| `load_*` | processes |
| `memory_*_percent` | % |
| `memory_*` | bytes |
| `disk_*_percent` | % |
| `disk_*` | bytes |
| `network_*` | bytes |
| `throughput_*` | bytes/sec |
| `packets_*` | packets |
