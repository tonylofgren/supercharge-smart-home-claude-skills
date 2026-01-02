# Subflows in Node-RED

## Table of Contents
- [Overview](#overview)
- [Creating Subflows](#creating-subflows)
- [Subflow Properties](#subflow-properties)
- [Environment Variables](#environment-variables)
- [Subflow Status](#subflow-status)
- [Common Subflow Patterns](#common-subflow-patterns)
- [Best Practices](#best-practices)

---

## Overview

A **Subflow** is a collection of nodes that are collapsed into a single reusable node. Think of it as a custom node created from existing nodes.

### Benefits

| Benefit | Description |
|---------|-------------|
| **Reusability** | Use same logic in multiple places |
| **Maintainability** | Update once, affects all instances |
| **Readability** | Hide complex logic behind simple node |
| **Organization** | Clean up cluttered flows |

### Subflow vs Copy-Paste

| Feature | Subflow | Copy-Paste |
|---------|---------|------------|
| Updates | All instances at once | Each copy separately |
| Customization | Via properties/env | Edit each copy |
| Complexity | Hidden inside | Visible in flow |
| Reuse | Easy, from palette | Manual duplication |

---

## Creating Subflows

### From Scratch

1. **Menu** → **Subflows** → **Create Subflow**
2. Name the subflow
3. Add nodes inside
4. Configure inputs/outputs
5. Subflow appears in palette

### From Selection

1. Select nodes to convert
2. **Menu** → **Subflows** → **Selection to Subflow**
3. Adjust inputs/outputs as needed

### Subflow Template

```
┌─────────────────────────────────────────────────────────┐
│                    Subflow: My Logic                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ○ Input    ┌──────────┐    ┌──────────┐    Output ○    │
│  ─────────▶│  Node A  │───▶│  Node B  │───▶             │
│             └──────────┘    └──────────┘                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Adding Inputs/Outputs

**Inputs:**
- Maximum 1 input per subflow
- Click "Add Input" in subflow editor
- Position the input connector

**Outputs:**
- Multiple outputs supported
- Click "Add Output" for each
- Number outputs like function nodes

```javascript
// Subflow with 2 outputs
// Output 1: Success
// Output 2: Error
```

---

## Subflow Properties

### Instance Properties

Properties that can be customized per instance of the subflow.

**Defining Properties:**

1. Edit subflow
2. Click "Edit Properties"
3. Add property definitions

```javascript
// Property definition example
{
  "name": "threshold",
  "type": "num",
  "value": "50",      // Default value
  "ui": {
    "label": {
      "en-US": "Threshold"
    },
    "type": "input",
    "opts": {
      "types": ["num", "flow", "global"]
    }
  }
}
```

### Property Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | String | "hello" |
| `num` | Number | 42 |
| `bool` | Boolean | true/false |
| `json` | JSON object | {"key": "value"} |
| `flow` | Flow context | Flow variable |
| `global` | Global context | Global variable |
| `env` | Environment var | Process env |

### Using Properties in Subflow

Access via environment variables:

```javascript
// In function node inside subflow
const threshold = env.get("threshold");
const entityId = env.get("entityId");

if (msg.payload > threshold) {
  // Process
}
```

---

## Environment Variables

### Subflow Environment

Each subflow instance has its own environment scope.

**Defining in Subflow:**

```javascript
// Edit Subflow Properties → Environment Variables
[
  {
    "name": "ENTITY_ID",
    "value": "sensor.default",
    "type": "str"
  },
  {
    "name": "TIMEOUT",
    "value": "5000",
    "type": "num"
  }
]
```

**Accessing in Nodes:**

```javascript
// Function node
const entity = env.get("ENTITY_ID");
const timeout = env.get("TIMEOUT");

// Change node - use ${ENV_VAR} syntax
// Set msg.entity to ${ENTITY_ID}

// Template node
// Entity: {{env.ENTITY_ID}}
```

### Override Per Instance

1. Double-click subflow instance
2. Modify environment variables
3. Each instance can have different values

```
Instance 1:               Instance 2:
ENTITY_ID: sensor.temp1   ENTITY_ID: sensor.temp2
TIMEOUT: 5000             TIMEOUT: 10000
```

### Default Values

```javascript
// In function node - with fallback
const entity = env.get("ENTITY_ID") || "sensor.default";
const timeout = parseInt(env.get("TIMEOUT") || "5000", 10);
```

---

## Subflow Status

### Setting Status

Subflows can display status like regular nodes:

```javascript
// In function node inside subflow
node.status({fill:"green", shape:"dot", text:"connected"});
node.status({fill:"red", shape:"ring", text:"error"});
node.status({});  // Clear
```

### Status Node (in Subflow)

Use the "Status" node to output status changes:

```
┌─────────────────────────────────────────────────────────┐
│ Subflow                                                  │
│                                                          │
│  ○ Input → [Process] → Output ○                         │
│                ↓                                         │
│           [Status] → (subflow status output)             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Dynamic Status from Properties

```javascript
// Show entity name in status
const entity = env.get("ENTITY_ID");
node.status({fill:"blue", shape:"dot", text:entity});
```

---

## Common Subflow Patterns

### Debounce Subflow

Prevent rapid repeated triggers.

```
Environment Variables:
- DELAY_MS: 500 (default)

Nodes:
┌────────┐    ┌────────────┐    ┌────────┐
│ Input  │───▶│  Trigger   │───▶│ Output │
│        │    │ (delay)    │    │        │
└────────┘    └────────────┘    └────────┘
```

```javascript
// Trigger node config
{
  "duration": "${DELAY_MS}",
  "extend": true,  // Reset timer on new message
  "units": "ms"
}
```

### Notification Router Subflow

Smart notification routing.

```
Environment Variables:
- DEFAULT_SERVICE: notify.mobile_app
- PRIORITY_SERVICE: notify.urgent

Nodes:
Input → Switch (priority) → [High] → Priority Service
                         → [Normal] → Default Service
```

### Rate Limiter Subflow

Limit message frequency.

```
Environment Variables:
- MAX_PER_MINUTE: 10
- DROP_EXCESS: true

Logic:
- Track message count in context
- Reset count every minute
- Either drop or queue excess messages
```

### Entity State Cache Subflow

Cache entity states for quick access.

```
Environment Variables:
- ENTITY_PATTERN: "sensor.*"
- CACHE_TTL: 60000

Logic:
- Listen for state changes
- Cache in flow context
- Serve from cache on request
```

### Retry with Backoff Subflow

Retry failed operations.

```
Environment Variables:
- MAX_RETRIES: 3
- INITIAL_DELAY: 1000
- BACKOFF_MULTIPLIER: 2

Logic:
- On error, wait and retry
- Increase delay exponentially
- Give up after max retries
```

### Example: Motion Light Subflow

```
Environment Variables:
- MOTION_SENSOR: binary_sensor.motion_living
- LIGHT_ENTITY: light.living_room
- OFF_DELAY: 300 (seconds)
- BRIGHTNESS: 100

Flow:
Motion Sensor Change → Check if On → Turn On Light
                                          ↓
                    ←── Delay ←── Start Timer
                    ↓
              Turn Off Light
```

---

## Best Practices

### 1. Name Clearly

```
Good Names:
- "Motion Light Controller"
- "Notification Router"
- "Rate Limiter (per minute)"

Bad Names:
- "Subflow 1"
- "My Logic"
- "Handler"
```

### 2. Document Properties

```javascript
// In subflow description/info
/**
 * Motion Light Controller
 *
 * Properties:
 *   MOTION_SENSOR - Entity ID of motion sensor
 *   LIGHT_ENTITY - Entity ID of light to control
 *   OFF_DELAY - Seconds before turning off (default: 300)
 *
 * Input:
 *   Any message triggers evaluation
 *
 * Outputs:
 *   1: Light turned on
 *   2: Light turned off
 */
```

### 3. Provide Defaults

```javascript
// Always have sensible defaults
const delay = parseInt(env.get("OFF_DELAY") || "300", 10);
const brightness = parseInt(env.get("BRIGHTNESS") || "100", 10);
```

### 4. Validate Properties

```javascript
// Check required properties
const entityId = env.get("ENTITY_ID");
if (!entityId) {
  node.error("ENTITY_ID is required");
  node.status({fill:"red", shape:"ring", text:"missing config"});
  return null;
}
```

### 5. Use Status Effectively

```javascript
// Show current state
const count = context.get("count") || 0;
node.status({
  fill: count > 0 ? "green" : "grey",
  shape: "dot",
  text: `${count} processed`
});
```

### 6. Handle Errors Gracefully

```javascript
// Catch errors inside subflow
try {
  // Processing logic
} catch (err) {
  node.error(err.message, msg);
  node.status({fill:"red", shape:"ring", text:"error"});
  return [null, msg];  // Error output
}
```

### 7. Keep Subflows Focused

```
Good: One clear purpose
- "Debounce" - just debouncing
- "Format Notification" - just formatting

Bad: Too many responsibilities
- "Process Everything" - unclear purpose
- "Do All The Things" - hard to maintain
```

### 8. Version Control Subflows

Export subflows separately for version control:

```javascript
// Menu → Export → Selected Nodes
// Save as: subflow-debounce.json
```

---

## Subflow JSON Structure

```javascript
{
  "id": "subflow:abc123",
  "type": "subflow",
  "name": "Debounce",
  "info": "Debounce rapid events",
  "category": "utility",
  "in": [
    {"x": 50, "y": 30, "wires": [{"id": "node1"}]}
  ],
  "out": [
    {"x": 350, "y": 30, "wires": [{"id": "node2", "port": 0}]}
  ],
  "env": [
    {"name": "DELAY_MS", "type": "num", "value": "500"}
  ],
  "color": "#DDAA99"
}
```

---

## Related References

- [Core Concepts](core-concepts.md) - Flows, nodes overview
- [Node Types](node-types.md) - Available nodes
- [Context Storage](context-storage.md) - Storing state
- [Automation Patterns](automation-patterns.md) - Common patterns
