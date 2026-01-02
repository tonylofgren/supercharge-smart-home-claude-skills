# Home Assistant State Nodes

## Table of Contents
- [Overview](#overview)
- [Current State Node](#current-state-node)
- [Get Entities Node](#get-entities-node)
- [Get History Node](#get-history-node)
- [Poll State Node](#poll-state-node)
- [Wait Until Node](#wait-until-node)
- [Render Template Node](#render-template-node)

---

## Overview

State nodes read information from Home Assistant without triggering on changes - they're used inline in flows to get current values.

### Quick Reference

| Node | Use When |
|------|----------|
| **Current State** | Get single entity state |
| **Get Entities** | Query multiple entities |
| **Get History** | Historical state data |
| **Poll State** | Periodic state checks |
| **Wait Until** | Pause until condition |
| **Render Template** | Evaluate HA templates |

---

## Current State Node

Get the current state of a single entity.

### Configuration

```javascript
{
  "entityId": "sensor.temperature",
  "blockInputOverrides": false,
  "outputProperties": [
    {"property": "payload", "valueType": "entityState"},
    {"property": "data", "valueType": "entity"}
  ],
  "ifState": "",
  "ifStateType": "str",
  "ifStateOperator": "is",
  "timeout": 0
}
```

### Output Properties

| Value Type | Description | Example Output |
|------------|-------------|----------------|
| `entityState` | State value only | `"22.5"` |
| `entity` | Full entity object | `{entity_id, state, attributes...}` |
| `entityId` | Entity ID | `"sensor.temperature"` |
| `config` | Node configuration | Config object |

### Output Message

```javascript
msg = {
  payload: "22.5",  // entityState
  data: {
    entity_id: "sensor.temperature",
    state: "22.5",
    attributes: {
      unit_of_measurement: "°C",
      friendly_name: "Temperature",
      device_class: "temperature"
    },
    last_changed: "2024-01-15T10:30:00.000Z",
    last_updated: "2024-01-15T10:30:05.000Z"
  }
};
```

### Conditional Output

Route based on state:

```javascript
// Configuration
{
  "ifState": "on",
  "ifStateOperator": "is",
  "halt_if_state": "on",  // Stop if state is "on"
}

// Output 1: State matches condition
// Output 2: State doesn't match
```

### Dynamic Entity ID

```javascript
// Function node before Current State
msg.payload = {
  entity_id: `sensor.${msg.room}_temperature`
};
// Uncheck "Block input overrides" in node config
```

---

## Get Entities Node

Query entities based on criteria.

### Configuration

```javascript
{
  "rules": [
    {
      "property": "entity_id",
      "logic": "starts_with",
      "value": "light.",
      "valueType": "str"
    },
    {
      "property": "state",
      "logic": "is",
      "value": "on",
      "valueType": "str"
    }
  ],
  "outputType": "array",
  "outputEmptyResults": false,
  "outputLocationType": "msg",
  "outputLocation": "payload"
}
```

### Rule Logic

| Logic | Description | Example |
|-------|-------------|---------|
| `is` | Equals | state is "on" |
| `is_not` | Not equals | state is_not "unavailable" |
| `lt` | Less than | brightness < 50 |
| `lte` | Less or equal | ≤ |
| `gt` | Greater than | temperature > 25 |
| `gte` | Greater or equal | ≥ |
| `starts_with` | Starts with | entity_id starts_with "light." |
| `in_group` | In HA group | entity in_group "lights" |
| `jsonata` | JSONata expression | Custom logic |

### Rule Properties

| Property | Description |
|----------|-------------|
| `entity_id` | Entity identifier |
| `state` | Current state |
| `attributes` | Entity attributes |
| `attributes.{name}` | Specific attribute |
| `last_changed` | Last state change |
| `last_updated` | Last update time |

### Output Types

```javascript
// Array (default)
"outputType": "array"
// Output: [{entity1}, {entity2}, ...]

// Count
"outputType": "count"
// Output: 5

// Split (one message per entity)
"outputType": "split"
// Output: Multiple messages

// Random
"outputType": "random"
// Output: One random matching entity
```

### Example: Get All Lights On

```javascript
// Configuration
{
  "rules": [
    {"property": "entity_id", "logic": "starts_with", "value": "light."},
    {"property": "state", "logic": "is", "value": "on"}
  ],
  "outputType": "array"
}

// Output
msg.payload = [
  {
    entity_id: "light.living_room",
    state: "on",
    attributes: { brightness: 255 }
  },
  {
    entity_id: "light.kitchen",
    state: "on",
    attributes: { brightness: 128 }
  }
];
```

### Example: Count Open Windows

```javascript
// Configuration
{
  "rules": [
    {"property": "entity_id", "logic": "starts_with", "value": "binary_sensor.window_"},
    {"property": "state", "logic": "is", "value": "on"}
  ],
  "outputType": "count"
}

// Output
msg.payload = 3;  // 3 windows open
```

---

## Get History Node

Retrieve historical state data.

### Configuration

```javascript
{
  "entityId": "sensor.temperature",
  "startDate": "",  // Empty = relative
  "endDate": "",
  "relativeTime": "24",
  "relativeTimeUnits": "hours",
  "flatten": true
}
```

### Time Options

| Option | Description |
|--------|-------------|
| `startDate` | Specific start date |
| `endDate` | Specific end date |
| `relativeTime` | Hours/days back |
| `relativeTimeUnits` | hours, days, minutes |

### Output (Flattened)

```javascript
msg.payload = [
  {
    entity_id: "sensor.temperature",
    state: "22.5",
    last_changed: "2024-01-14T12:00:00.000Z"
  },
  {
    entity_id: "sensor.temperature",
    state: "23.0",
    last_changed: "2024-01-14T14:00:00.000Z"
  },
  // ... more entries
];
```

### Processing History

```javascript
// Function node: Calculate average
const values = msg.payload
  .map(entry => parseFloat(entry.state))
  .filter(val => !isNaN(val));

const average = values.reduce((a, b) => a + b, 0) / values.length;

msg.payload = {
  average: average.toFixed(1),
  min: Math.min(...values),
  max: Math.max(...values),
  samples: values.length
};
return msg;
```

---

## Poll State Node

Periodically check entity state.

### Configuration

```javascript
{
  "entityId": "sensor.power",
  "updateInterval": 60,
  "updateIntervalType": "num",
  "updateIntervalUnits": "seconds",
  "outputOnChanged": true,
  "outputInitially": false
}
```

### Options

| Option | Description |
|--------|-------------|
| `updateInterval` | Seconds between polls |
| `outputOnChanged` | Only output if changed |
| `outputInitially` | Output on deploy |

### Use Cases

```
When to use Poll State:
✓ Monitoring entities that don't fire events
✓ Rate-limiting state checks
✓ Periodic reports

When NOT to use:
✗ Real-time state changes (use Trigger: state)
✗ Fast updates needed (events are faster)
```

---

## Wait Until Node

Pause flow until condition is met.

### Configuration

```javascript
{
  "entityId": "binary_sensor.door",
  "entityIdType": "exact",
  "property": "state",
  "comparator": "is",
  "value": "off",
  "timeout": 60,
  "timeoutUnits": "seconds",
  "checkCurrentState": true
}
```

### Behavior

1. Check current state (if enabled)
2. If condition met, continue immediately
3. If not, wait for state change
4. Timeout if condition not met in time

### Outputs

| Output | When |
|--------|------|
| Output 1 | Condition met |
| Output 2 | Timeout |

### Example: Wait for Door to Close

```javascript
// Configuration
{
  "entityId": "binary_sensor.front_door",
  "comparator": "is",
  "value": "off",  // Door closed
  "timeout": 300,
  "timeoutUnits": "seconds"
}

// Output 1: Door closed within 5 minutes
// Output 2: Timeout - door still open
```

---

## Render Template Node

Evaluate Home Assistant Jinja2 templates.

### Configuration

```javascript
{
  "template": "{{ states('sensor.temperature') | float + 5 }}",
  "resultsLocation": "payload",
  "resultsLocationType": "msg"
}
```

### Common Templates

```jinja2
{# Get state #}
{{ states('sensor.temperature') }}

{# With conversion #}
{{ states('sensor.temperature') | float }}

{# Check state #}
{{ is_state('binary_sensor.motion', 'on') }}

{# State attributes #}
{{ state_attr('climate.hvac', 'temperature') }}

{# Time-based #}
{{ now().hour }}
{{ now().strftime('%Y-%m-%d') }}

{# Conditional #}
{% if is_state('sun.sun', 'below_horizon') %}dark{% else %}light{% endif %}

{# List all on lights #}
{{ states.light | selectattr('state', 'eq', 'on') | map(attribute='entity_id') | list }}
```

### Dynamic Templates

```javascript
// Via message
msg.template = `{{ states('sensor.${msg.room}_temperature') }}`;
```

---

## Combining State Nodes

### Pattern: Check Before Action

```
┌─────────┐    ┌───────────────┐    ┌──────────┐    ┌──────────┐
│ Trigger │───▶│ Current State │───▶│  Switch  │───▶│  Action  │
│         │    │ (sun.sun)     │    │(is below)│    │(light on)│
└─────────┘    └───────────────┘    └──────────┘    └──────────┘
```

### Pattern: Aggregate State

```
┌─────────┐    ┌───────────────┐    ┌──────────┐
│ Trigger │───▶│ Get Entities  │───▶│ Function │───▶ Summary
│         │    │ (all windows) │    │(count)   │
└─────────┘    └───────────────┘    └──────────┘
```

### Pattern: Historical Analysis

```
┌─────────┐    ┌───────────────┐    ┌──────────┐
│  Time   │───▶│  Get History  │───▶│ Function │───▶ Report
│ (daily) │    │  (24 hours)   │    │(average) │
└─────────┘    └───────────────┘    └──────────┘
```

---

## Related References

- [HA Setup](ha-setup.md) - Connection configuration
- [HA Trigger Nodes](ha-trigger-nodes.md) - Event triggers
- [HA Action Nodes](ha-action-nodes.md) - Service calls
- [JSONata](jsonata.md) - Expression language
