# Home Assistant Trigger Nodes

## Table of Contents
- [Overview](#overview)
- [Trigger: state](#trigger-state)
- [Events: state](#events-state)
- [Events: all](#events-all)
- [Device Node](#device-node)
- [Time Node](#time-node)
- [Zone Node](#zone-node)
- [Events: calendar](#events-calendar)
- [Choosing the Right Trigger](#choosing-the-right-trigger)

---

## Overview

Trigger nodes start flows when something happens in Home Assistant. They have no input ports - they generate messages based on events.

### Quick Reference

| Node | Use When |
|------|----------|
| **Trigger: state** | Complex state conditions |
| **Events: state** | Simple state changes |
| **Events: all** | Any HA event type |
| **Device** | Device-specific triggers |
| **Time** | Scheduled automation |
| **Zone** | Location-based triggers |
| **Events: calendar** | Calendar events |

---

## Trigger: state

The most versatile state trigger with conditional outputs.

### Basic Configuration

```javascript
{
  "entityId": "binary_sensor.motion_living",
  "entityIdType": "exact",  // exact, substring, regex
  "outputOnConnect": false,
  "enableInput": false
}
```

### Entity ID Types

| Type | Pattern | Matches |
|------|---------|---------|
| `exact` | `light.kitchen` | Only light.kitchen |
| `substring` | `kitchen` | Any entity with "kitchen" |
| `regex` | `^light\..*_room$` | light.living_room, light.bed_room |

### Conditional Outputs

Configure outputs based on conditions:

```javascript
// Output 1: Motion detected (state = on)
{
  "outputProperties": [
    {"property": "payload", "value": "", "valueType": "entityState"}
  ],
  "comparator": "is",
  "value": "on",
  "valueType": "str"
}

// Output 2: Motion cleared (state = off)
{
  "comparator": "is",
  "value": "off",
  "valueType": "str"
}
```

### Output Message

```javascript
msg = {
  payload: "on",              // Current state
  topic: "binary_sensor.motion_living",
  data: {
    entity_id: "binary_sensor.motion_living",
    new_state: {
      state: "on",
      attributes: {
        device_class: "motion",
        friendly_name: "Living Room Motion"
      },
      last_changed: "2024-01-15T10:30:00.000Z",
      last_updated: "2024-01-15T10:30:00.000Z"
    },
    old_state: {
      state: "off",
      attributes: { /* ... */ },
      last_changed: "2024-01-15T10:25:00.000Z"
    }
  }
};
```

### Advanced Options

| Option | Description |
|--------|-------------|
| **Output on Connect** | Send current state on deploy |
| **Enable Input** | Accept external triggers |
| **Expose to HA** | Create switch entity to enable/disable |
| **State Type** | Cast state to specific type |

### Testing with Input

```javascript
// Send to trigger input to simulate state change
msg = {
  entity_id: "binary_sensor.motion",
  new_state: { state: "on" },
  old_state: { state: "off" }
};
```

### Comparators

| Comparator | Description | Example |
|------------|-------------|---------|
| `is` | Equals | state is "on" |
| `is_not` | Not equals | state is_not "unavailable" |
| `lt` | Less than | temperature < 20 |
| `lte` | Less than or equal | brightness <= 50 |
| `gt` | Greater than | humidity > 60 |
| `gte` | Greater than or equal | power >= 100 |
| `includes` | Contains string | state includes "error" |
| `does_not_include` | Doesn't contain | state does_not_include "ok" |
| `starts_with` | Starts with | state starts_with "play" |
| `in_group` | Entity in group | entity in_group "lights" |
| `jsonata` | JSONata expression | Custom condition |

---

## Events: state

Simpler state change listener without conditional outputs.

### Configuration

```javascript
{
  "entityId": "sensor.temperature",
  "entityIdType": "exact",
  "outputOnConnect": false,
  "stateFilter": "",          // Optional: filter states
  "outputProperties": [
    {"property": "payload", "valueType": "entityState"},
    {"property": "data", "valueType": "eventData"}
  ]
}
```

### State Filter

Only trigger on specific states:

```javascript
// Single state
"stateFilter": "on"

// Multiple states (JSONata)
"stateFilter": "$contains(['on', 'home'], payload)"

// Numeric comparison
"stateFilter": "$number(payload) > 25"
```

### Output Properties

| Value Type | Description |
|------------|-------------|
| `entityState` | Just the state value |
| `entityStateChanged` | Boolean if state changed |
| `eventData` | Full event object |
| `triggerId` | Entity ID |
| `config` | Node configuration |

---

## Events: all

Subscribe to any Home Assistant event.

### Configuration

```javascript
{
  "eventType": "call_service",  // Empty = all events
  "outputProperties": [
    {"property": "payload", "valueType": "eventData"},
    {"property": "event_type", "valueType": "eventType"}
  ]
}
```

### Common Event Types

| Event Type | When Fired |
|------------|------------|
| `state_changed` | Entity state changes |
| `call_service` | Service called |
| `automation_triggered` | Automation runs |
| `script_started` | Script starts |
| `homeassistant_start` | HA starts |
| `homeassistant_stop` | HA stops |
| `service_registered` | New service available |
| `component_loaded` | Integration loaded |

### Filtering Events

Use Switch node after Events: all:

```javascript
// Switch node rules
[
  {"t": "eq", "v": "state_changed", "vt": "str"},
  {"t": "eq", "v": "call_service", "vt": "str"}
]
```

### Output Message

```javascript
// call_service event
msg = {
  payload: {
    event_type: "call_service",
    data: {
      domain: "light",
      service: "turn_on",
      service_data: {
        entity_id: "light.living_room",
        brightness: 255
      }
    },
    origin: "LOCAL",
    time_fired: "2024-01-15T10:30:00.000Z"
  },
  event_type: "call_service"
};
```

---

## Device Node

Trigger based on device-specific events (buttons, remotes).

### Configuration

```javascript
{
  "deviceId": "abc123def456",
  "triggerType": "action",
  "trigger": "button_short_press"
}
```

### Finding Device ID

1. Edit Device node
2. Click "Device" dropdown
3. Search for device name
4. Select from list

### Common Trigger Types

| Trigger | Description |
|---------|-------------|
| `button_short_press` | Quick button press |
| `button_long_press` | Held button |
| `button_double_press` | Double tap |
| `turned_on` | Device turned on |
| `turned_off` | Device turned off |

### Output Message

```javascript
msg = {
  payload: {
    event_type: "device_event",
    device_id: "abc123def456",
    type: "button_short_press",
    subtype: "button_1"
  }
};
```

---

## Time Node

Schedule-based triggers.

### Configuration

```javascript
{
  "entityId": "input_datetime.alarm_time",  // Or fixed time
  "offset": 0,
  "offsetUnits": "minutes",
  "randomOffset": false,
  "repeatDaily": true
}
```

### Time Sources

| Source | Description |
|--------|-------------|
| Entity | input_datetime entity |
| Fixed | Specific time |
| Sun events | sunrise/sunset |

### Sun Events

```javascript
// Trigger at sunset
{
  "entityId": "sun.sun",
  "event": "sunset",
  "offset": -30,          // 30 minutes before
  "offsetUnits": "minutes"
}
```

### Output Message

```javascript
msg = {
  payload: {
    event: "sunset",
    time: "2024-01-15T17:30:00.000Z"
  }
};
```

---

## Zone Node

Trigger when entities enter/exit zones.

### Configuration

```javascript
{
  "entityId": "person.john",
  "zoneId": "zone.home",
  "event": "enter"  // enter, leave, enter_leave
}
```

### Events

| Event | Triggers When |
|-------|---------------|
| `enter` | Entity enters zone |
| `leave` | Entity leaves zone |
| `enter_leave` | Either enter or leave |

### Output Message

```javascript
msg = {
  payload: {
    entity_id: "person.john",
    zone: "zone.home",
    event: "enter",
    new_state: "home",
    old_state: "away"
  }
};
```

---

## Events: calendar

Trigger on calendar events.

### Configuration

```javascript
{
  "entityId": "calendar.family",
  "eventType": "start"  // start, end
}
```

### Output Message

```javascript
msg = {
  payload: {
    event_type: "start",
    summary: "Family Dinner",
    description: "Dinner at restaurant",
    start: "2024-01-15T18:00:00.000Z",
    end: "2024-01-15T20:00:00.000Z",
    location: "Restaurant Name"
  }
};
```

---

## Choosing the Right Trigger

### Decision Tree

```
Need to monitor state changes?
├── Yes → Simple trigger on any change?
│         ├── Yes → Events: state
│         └── No → Need conditions? → Trigger: state
│
├── Need time-based trigger?
│   └── Yes → Time node
│
├── Need location trigger?
│   └── Yes → Zone node
│
├── Device button/remote?
│   └── Yes → Device node
│
├── Calendar event?
│   └── Yes → Events: calendar
│
└── Other HA events (services, automations)?
    └── Yes → Events: all
```

### Performance Comparison

| Node | Resource Usage | Best For |
|------|----------------|----------|
| Trigger: state | Medium | Complex conditions |
| Events: state | Low | Simple changes |
| Events: all | High | Debugging, any event |
| Device | Low | Physical buttons |
| Time | Low | Schedules |
| Zone | Low | Presence |

### Common Patterns

**Motion Light:**
```
Trigger: state (motion sensor)
└── Condition: state = on
    └── Call Service: light.turn_on
```

**Presence Automation:**
```
Zone node (person entity)
└── Enter home → Enable heating
└── Leave home → Disable heating
```

**Scheduled Task:**
```
Time node (daily at 8:00)
└── Call Service: notify
```

---

## Related References

- [HA Setup](ha-setup.md) - Connection configuration
- [HA Action Nodes](ha-action-nodes.md) - Executing services
- [HA State Nodes](ha-state-nodes.md) - Getting state
- [Automation Patterns](automation-patterns.md) - Common recipes
