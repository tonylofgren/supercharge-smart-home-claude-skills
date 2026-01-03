# Message Handling in Node-RED

Understanding the msg object and data flow.

## The msg Object

Every message in Node-RED is a JavaScript object.

### Standard Properties

| Property | Type | Purpose |
|----------|------|---------|
| `msg.payload` | any | Primary data |
| `msg.topic` | string | Message category/routing |
| `msg._msgid` | string | Unique message ID (auto) |

### Home Assistant Properties

After trigger nodes:

| Property | Purpose |
|----------|---------|
| `msg.payload` | New state value |
| `msg.data.entity_id` | Entity that triggered |
| `msg.data.new_state` | Full new state object |
| `msg.data.old_state` | Previous state object |
| `msg.data.event_type` | Type of event |

---

## Payload Patterns

### Simple Values

```javascript
msg.payload = "hello";        // String
msg.payload = 42;             // Number
msg.payload = true;           // Boolean
msg.payload = ["a", "b"];     // Array
msg.payload = { key: "val" }; // Object
```

### State Object

```javascript
msg.data.new_state = {
  entity_id: "light.living_room",
  state: "on",
  attributes: {
    brightness: 255,
    friendly_name: "Living Room"
  },
  last_changed: "2024-01-01T12:00:00Z",
  last_updated: "2024-01-01T12:00:00Z"
};
```

### Accessing Nested Data

```javascript
// Safe access
const brightness = msg.data?.new_state?.attributes?.brightness;

// With default
const brightness = msg.data?.new_state?.attributes?.brightness ?? 255;

// Check before use
if (msg.data && msg.data.new_state) {
  const state = msg.data.new_state.state;
}
```

---

## Transforming Messages

### Basic Transform

```javascript
// Input: msg.payload = "23.5"
msg.payload = parseFloat(msg.payload);
msg.unit = "°C";
return msg;
// Output: msg.payload = 23.5, msg.unit = "°C"
```

### Restructure

```javascript
// Input: msg.data.new_state.attributes.temperature = 23.5
const temp = msg.data.new_state.attributes.temperature;
const humidity = msg.data.new_state.attributes.humidity;

msg.payload = {
  temperature: temp,
  humidity: humidity,
  timestamp: Date.now()
};

return msg;
```

### Extract from Array

```javascript
// Input: msg.payload = [{temp: 20}, {temp: 22}, {temp: 21}]
const temps = msg.payload.map(item => item.temp);
const average = temps.reduce((a, b) => a + b, 0) / temps.length;

msg.payload = {
  values: temps,
  average: Math.round(average * 10) / 10
};

return msg;
```

---

## Multiple Outputs

### Function Node with Multiple Outputs

Configure function node with N outputs:

```javascript
// 2 outputs: [output1, output2]

if (msg.payload > 25) {
  return [msg, null];  // Send to output 1 only
} else {
  return [null, msg];  // Send to output 2 only
}
```

### Send to Both

```javascript
return [msg, msg];  // Clone to both outputs
```

### Different Messages

```javascript
const msg1 = { payload: "high", topic: "alert" };
const msg2 = { payload: "normal", topic: "log" };

return [msg1, msg2];
```

### Array for Multiple Messages on One Output

```javascript
// Send 3 messages on output 1
const messages = [
  { payload: "first" },
  { payload: "second" },
  { payload: "third" }
];

return [messages];
```

---

## Message Cloning

### Why Cloning Matters

```javascript
// BAD - both outputs share same object
const msg1 = msg;
const msg2 = msg;
msg1.payload = "changed";  // Also changes msg2!

// GOOD - clone for independence
const msg2 = RED.util.cloneMessage(msg);
msg2.payload = "different";
```

### Deep Clone

```javascript
// For complex objects
const clone = JSON.parse(JSON.stringify(msg.payload));
```

### Selective Clone

```javascript
// Clone only what you need
const newMsg = {
  payload: { ...msg.payload },
  topic: msg.topic
};
```

---

## Message Routing

### Switch Node

Routes messages based on property values.

Configuration:
```json
{
  "type": "switch",
  "property": "payload",
  "rules": [
    { "t": "eq", "v": "on" },
    { "t": "eq", "v": "off" },
    { "t": "else" }
  ]
}
```

### Route by Topic

```json
{
  "property": "topic",
  "rules": [
    { "t": "eq", "v": "temperature" },
    { "t": "eq", "v": "humidity" }
  ]
}
```

### Route by Entity Domain

```javascript
// In function node
const entityId = msg.data.entity_id;
const domain = entityId.split('.')[0];

switch (domain) {
  case 'light':
    return [msg, null, null];
  case 'switch':
    return [null, msg, null];
  default:
    return [null, null, msg];
}
```

---

## Message Aggregation

### Join Node

Combine multiple messages into one.

Modes:
- **Automatic** - Wait for msg.parts
- **Manual** - Specify count
- **Reduce** - Custom reduction

### Manual Join

Wait for 3 messages, output array:

```json
{
  "type": "join",
  "mode": "custom",
  "count": "3",
  "build": "array"
}
```

### Join by Topic

```json
{
  "type": "join",
  "mode": "custom",
  "build": "object",
  "propertyType": "msg",
  "property": "topic"
}
```

### Reduce Pattern

```javascript
// Collect temperatures, output average
{
  "mode": "reduce",
  "reduceExp": "$A + payload",
  "reduceInit": "0",
  "reduceFixup": "$A / count"
}
```

---

## Split Node

Break array into individual messages.

### Basic Split

Input: `[1, 2, 3]`
Output: Three messages with `payload` 1, 2, 3

### Split Object

Input: `{a: 1, b: 2}`
Output: Two messages:
- `{payload: 1, topic: "a"}`
- `{payload: 2, topic: "b"}`

### Split with Parts

Messages include `msg.parts`:
```javascript
msg.parts = {
  id: "unique-id",
  index: 0,
  count: 3,
  type: "array"
};
```

---

## Message Enrichment

### Add Context Data

```javascript
const states = global.get("homeassistant").homeAssistant.states;

// Enrich with related entity data
msg.room = {
  temperature: parseFloat(states["sensor.living_room_temperature"]?.state),
  humidity: parseFloat(states["sensor.living_room_humidity"]?.state),
  lux: parseFloat(states["sensor.living_room_lux"]?.state)
};

return msg;
```

### Add Timestamps

```javascript
msg.receivedAt = Date.now();
msg.formattedTime = new Date().toISOString();
return msg;
```

### Add Metadata

```javascript
msg.meta = {
  source: "motion-sensor",
  area: "living_room",
  processed: true,
  version: "1.0"
};
return msg;
```

---

## Topic Usage

### Set Topic for Routing

```javascript
msg.topic = msg.data.entity_id.split('.')[0];
// "light.living_room" → topic = "light"
return msg;
```

### Topic as Key

```javascript
// Store by topic
const key = msg.topic;
const data = flow.get('dataStore') || {};
data[key] = msg.payload;
flow.set('dataStore', data);
```

### Hierarchical Topics

```javascript
msg.topic = "home/living_room/motion";

// Parse hierarchy
const parts = msg.topic.split('/');
const location = parts[0];  // "home"
const room = parts[1];      // "living_room"
const sensor = parts[2];    // "motion"
```

---

## Error Messages

### Standard Error Format

```javascript
msg.error = {
  message: "Failed to process",
  source: {
    id: node.id,
    type: "function",
    name: node.name
  }
};
```

### Throwing Errors

```javascript
// Catchable error
node.error("Something went wrong", msg);
return null;

// Or throw
throw new Error("Critical failure");
```

### Error in Catch Node

```javascript
// After catch node
node.warn(`Error from ${msg.error.source.name}: ${msg.error.message}`);
```

---

## Complete Message

### Before Change

Preserve original message:

```javascript
const original = RED.util.cloneMessage(msg);
msg._original = original;

// Later, restore if needed
msg = msg._original;
```

### Complete msg Object

Typical Home Assistant trigger message:

```javascript
{
  _msgid: "abc123",
  topic: "",
  payload: "on",
  data: {
    entity_id: "binary_sensor.motion",
    old_state: {
      state: "off",
      attributes: { ... },
      last_changed: "...",
      last_updated: "..."
    },
    new_state: {
      state: "on",
      attributes: {
        device_class: "motion",
        friendly_name: "Living Room Motion"
      },
      last_changed: "...",
      last_updated: "..."
    }
  }
}
```

---

## JSONata Expressions

Alternative to function nodes for transformations.

### In Change Node

Set `msg.payload` using JSONata:

```jsonata
payload.temperature & "°C"
```

### Complex Transformations

```jsonata
{
  "temp": data.new_state.attributes.temperature,
  "unit": "celsius",
  "timestamp": $now()
}
```

### Filtering

```jsonata
payload[temperature > 20]
```

### Aggregation

```jsonata
$average(payload.values)
```

---

## Best Practices

### 1. Don't Mutate Shared References

```javascript
// BAD
msg.payload.value = 10;  // Mutates original

// GOOD
msg.payload = { ...msg.payload, value: 10 };
```

### 2. Check Before Access

```javascript
// BAD
const temp = msg.data.new_state.attributes.temperature;

// GOOD
const temp = msg.data?.new_state?.attributes?.temperature ?? 0;
```

### 3. Clean Up Temporary Properties

```javascript
// Add temp property
msg._processing = true;

// ...do work...

// Clean up before output
delete msg._processing;
return msg;
```

### 4. Consistent Payload Types

Pick a format and stick to it:

```javascript
// Always output same structure
msg.payload = {
  value: parseFloat(msg.payload) || 0,
  unit: "°C",
  timestamp: Date.now()
};
```

### 5. Document Message Shape

```javascript
/*
 * Expected input:
 *   msg.payload = { entity_id: string, action: "on"|"off" }
 *
 * Output:
 *   msg.payload = { action: string, target: {...}, data: {...} }
 */
```

---

## Quick Reference

### Common Transformations

| From | To | Code |
|------|----|------|
| String → Number | `"23.5"` → `23.5` | `parseFloat(msg.payload)` |
| Number → String | `23.5` → `"23.5"` | `String(msg.payload)` |
| Array → First | `[1,2,3]` → `1` | `msg.payload[0]` |
| Object → Value | `{a:1}` → `1` | `msg.payload.a` |
| Extract | deep.nested.val | `msg.data?.new_state?.state` |

### Output Patterns

| Pattern | Return |
|---------|--------|
| Single output | `return msg;` |
| Stop message | `return null;` |
| Output 1 only | `return [msg, null];` |
| Output 2 only | `return [null, msg];` |
| Both outputs | `return [msg, msg];` |
| Multiple on 1 | `return [[m1, m2, m3]];` |

