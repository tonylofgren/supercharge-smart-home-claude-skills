# Home Assistant Entity Nodes

## Table of Contents
- [Overview](#overview)
- [Sensor Node](#sensor-node)
- [Binary Sensor Node](#binary-sensor-node)
- [Switch Node](#switch-node)
- [Button Node](#button-node)
- [Number Node](#number-node)
- [Select Node](#select-node)
- [Text Node](#text-node)
- [Time Node](#time-node)
- [Update Config Node](#update-config-node)

---

## Overview

Entity nodes create entities in Home Assistant that are controlled from Node-RED. This allows you to expose Node-RED data as sensors, switches, and other entities visible in Home Assistant.

### Requirements

**IMPORTANT:** Entity nodes require the [Node-RED Custom Integration](https://github.com/zachowj/hass-node-red) (hass-node-red) to be installed in Home Assistant.

### Installation

1. Install via HACS or manually
2. Restart Home Assistant
3. Add integration: Settings → Integrations → Add → Node-RED

### Quick Reference

| Node | Creates | Example Use |
|------|---------|-------------|
| **Sensor** | sensor.* | Calculated values |
| **Binary Sensor** | binary_sensor.* | On/off states |
| **Switch** | switch.* | Controllable toggle |
| **Button** | button.* | Triggerable action |
| **Number** | number.* | Adjustable value |
| **Select** | select.* | Dropdown options |
| **Text** | text.* | Text input |
| **Time** | time.* | Time picker |

---

## Sensor Node

Creates a sensor entity reporting any value.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Calculated Temperature",
    "device_class": "temperature",
    "unit_of_measurement": "°C",
    "icon": "mdi:thermometer"
  },
  "state": "",
  "stateType": "msg",
  "attributes": [],
  "inputOverride": "allow"
}
```

### Device Classes

| Class | Unit Options |
|-------|--------------|
| `temperature` | °C, °F, K |
| `humidity` | % |
| `power` | W, kW |
| `energy` | Wh, kWh |
| `voltage` | V |
| `current` | A |
| `pressure` | Pa, hPa, mbar |
| `battery` | % |
| `illuminance` | lx |

### Setting State

```javascript
// From message payload
msg.payload = {
  state: 22.5
};

// With attributes
msg.payload = {
  state: 22.5,
  attributes: {
    source: "calculated",
    last_update: new Date().toISOString()
  }
};
```

### Example: Average Temperature

```javascript
// Function node calculating average
const temps = msg.payload; // Array of temperatures
const avg = temps.reduce((a, b) => a + b, 0) / temps.length;

msg.payload = {
  state: avg.toFixed(1),
  attributes: {
    samples: temps.length,
    min: Math.min(...temps),
    max: Math.max(...temps)
  }
};
return msg;
```

---

## Binary Sensor Node

Creates an on/off sensor.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Room Occupied",
    "device_class": "occupancy",
    "icon": "mdi:account-check"
  },
  "state": "",
  "stateType": "msg",
  "attributes": []
}
```

### Device Classes

| Class | On Means | Example |
|-------|----------|---------|
| `occupancy` | Occupied | Room presence |
| `motion` | Motion detected | Motion sensor |
| `door` | Door open | Entry sensor |
| `window` | Window open | Window sensor |
| `moisture` | Wet | Water leak |
| `smoke` | Smoke detected | Fire alarm |
| `connectivity` | Connected | Network device |
| `problem` | Problem exists | Error state |
| `running` | Running | Appliance |

### Setting State

```javascript
// Boolean
msg.payload = true;  // on
msg.payload = false; // off

// String
msg.payload = "on";
msg.payload = "off";

// With object
msg.payload = {
  state: true,
  attributes: {
    last_triggered: new Date().toISOString(),
    source: "multiple_sensors"
  }
};
```

---

## Switch Node

Creates a controllable switch entity.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Automation Enable",
    "icon": "mdi:toggle-switch"
  },
  "state": "",
  "stateType": "msg",
  "outputOnStateChange": true
}
```

### Behavior

- **Input:** Set switch state from Node-RED
- **Output:** Triggered when switch toggled from HA

### Two-Way Control

```javascript
// Set state from Node-RED
msg.payload = {
  state: "on"  // or "off"
};

// Output when toggled from HA
msg = {
  payload: {
    state: "on",
    old_state: "off"
  }
};
```

### Example: Automation Toggle

```
┌──────────────┐
│ Switch Node  │───▶ [To automation logic]
│ "Auto Mode"  │
└──────────────┘
       │
       │ (from HA toggle)
       ▼
┌──────────────┐
│ Switch Node  │───▶ [Flow continues or stops]
│   Output     │
└──────────────┘
```

---

## Button Node

Creates a pressable button entity.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Run Cleanup",
    "icon": "mdi:broom"
  },
  "outputOnStateChange": true
}
```

### Behavior

- **No state** - Buttons don't have persistent state
- **Output:** Message sent when button pressed in HA

### Output Message

```javascript
msg = {
  payload: {
    button_pressed: true,
    timestamp: "2024-01-15T10:30:00.000Z"
  }
};
```

### Example: Manual Trigger

```
┌──────────────┐
│ Button Node  │───▶ [Run cleanup routine]
│ "Run Cleanup"│
└──────────────┘
       │
       │ (pressed in HA)
       ▼
[Cleanup flow triggered]
```

---

## Number Node

Creates an adjustable numeric input.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Target Temperature",
    "min": 16,
    "max": 28,
    "step": 0.5,
    "mode": "slider",  // slider or box
    "unit_of_measurement": "°C",
    "icon": "mdi:thermometer"
  },
  "state": "",
  "stateType": "msg",
  "outputOnStateChange": true
}
```

### Options

| Option | Description |
|--------|-------------|
| `min` | Minimum value |
| `max` | Maximum value |
| `step` | Increment amount |
| `mode` | slider or box |

### Setting/Getting Value

```javascript
// Set from Node-RED
msg.payload = {
  state: 22.5
};

// Output when changed in HA
msg = {
  payload: {
    state: 23.0,
    old_state: 22.5
  }
};
```

---

## Select Node

Creates a dropdown selection entity.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Home Mode",
    "options": ["Home", "Away", "Night", "Guest"],
    "icon": "mdi:home-variant"
  },
  "state": "",
  "stateType": "msg",
  "outputOnStateChange": true
}
```

### Setting/Getting Value

```javascript
// Set from Node-RED
msg.payload = {
  state: "Away"
};

// Output when changed in HA
msg = {
  payload: {
    state: "Night",
    old_state: "Away"
  }
};
```

### Dynamic Options

```javascript
// Update options via Update Config node
msg.payload = {
  options: ["Option1", "Option2", "Option3"]
};
```

---

## Text Node

Creates a text input entity.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Status Message",
    "min": 0,
    "max": 255,
    "pattern": "",  // Regex pattern
    "mode": "text", // text or password
    "icon": "mdi:text"
  },
  "state": "",
  "stateType": "msg",
  "outputOnStateChange": true
}
```

### Options

| Option | Description |
|--------|-------------|
| `min` | Minimum length |
| `max` | Maximum length |
| `pattern` | Regex validation |
| `mode` | text or password |

### Example: Custom Message

```javascript
// Set from Node-RED
msg.payload = {
  state: "System operational"
};

// Use in notification
msg.payload = `Status: ${flow.get('status_message')}`;
```

---

## Time Node

Creates a time picker entity.

### Configuration

```javascript
{
  "entityConfig": {
    "name": "Alarm Time",
    "icon": "mdi:alarm"
  },
  "state": "",
  "stateType": "msg",
  "outputOnStateChange": true
}
```

### Time Format

```javascript
// Set time (HH:MM:SS)
msg.payload = {
  state: "07:30:00"
};

// Output includes
msg = {
  payload: {
    state: "07:30:00",
    hour: 7,
    minute: 30,
    second: 0
  }
};
```

---

## Update Config Node

Dynamically update entity configuration.

### Configuration

```javascript
{
  "entityConfigNode": "entity_config_id",
  "property": "attributes",  // What to update
  "value": "",
  "valueType": "msg"
}
```

### Update Options

| Property | Description |
|----------|-------------|
| `name` | Entity name |
| `icon` | MDI icon |
| `unit_of_measurement` | Unit |
| `options` | Select options |
| `min`, `max` | Number limits |

### Example: Dynamic Icon

```javascript
// Change icon based on state
const state = msg.payload;
msg.payload = {
  icon: state > 25 ? "mdi:thermometer-high" : "mdi:thermometer-low"
};
```

---

## Entity Config Node

Shared configuration for entity nodes.

### Configuration

```javascript
{
  "name": "My Entity",
  "deviceConfig": "device_id",  // Optional device grouping
  "entityId": "sensor.custom_id",  // Optional custom ID
  "unique_id": "unique_id_string"
}
```

### Device Grouping

Group entities under a device:

```javascript
// Device config
{
  "name": "Node-RED Sensors",
  "manufacturer": "Node-RED",
  "model": "Virtual Sensors"
}
```

---

## Best Practices

### 1. Use Appropriate Device Class

```javascript
// Good - helps HA display correctly
{
  "device_class": "temperature",
  "unit_of_measurement": "°C"
}

// Bad - generic sensor
{
  "device_class": null
}
```

### 2. Set Icons

```javascript
// Use MDI icons
{
  "icon": "mdi:thermometer"
}
// Browse: https://pictogrammers.com/library/mdi/
```

### 3. Update Attributes Separately

```javascript
// Efficient: Only update state
msg.payload = 22.5;

// When needed: Update with attributes
msg.payload = {
  state: 22.5,
  attributes: { source: "calculated" }
};
```

### 4. Handle Unavailable State

```javascript
// Set to unavailable
msg.payload = {
  state: null
};

// Check before sending
if (value === undefined) {
  msg.payload = { state: null };
} else {
  msg.payload = { state: value };
}
```

---

## Related References

- [HA Setup](ha-setup.md) - Connection and integration
- [HA State Nodes](ha-state-nodes.md) - Reading entities
- [HA Action Nodes](ha-action-nodes.md) - Controlling entities
- [Automation Patterns](automation-patterns.md) - Using entities
