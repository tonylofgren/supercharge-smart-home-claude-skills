# Message Handling in Node-RED

## Table of Contents
- [Message Structure](#message-structure)
- [Working with Payload](#working-with-payload)
- [Message Properties](#message-properties)
- [Message Routing](#message-routing)
- [Cloning Messages](#cloning-messages)
- [Multiple Outputs](#multiple-outputs)
- [Async Message Handling](#async-message-handling)
- [Best Practices](#best-practices)

---

## Message Structure

Every message in Node-RED is a JavaScript object, conventionally named `msg`.

### Standard Message

```javascript
msg = {
  _msgid: "abc123.456789",   // Auto-generated, unique per message
  payload: "Hello World",     // Primary data
  topic: "sensors/temp"       // Optional categorization
};
```

### Home Assistant Message

```javascript
// From Trigger: state node
msg = {
  _msgid: "def456.789012",
  payload: "on",                      // Current state value
  topic: "binary_sensor.motion",      // Entity ID
  data: {
    entity_id: "binary_sensor.motion_living",
    new_state: {
      state: "on",
      attributes: {
        friendly_name: "Living Room Motion",
        device_class: "motion"
      },
      last_changed: "2024-01-15T10:30:00.000Z",
      last_updated: "2024-01-15T10:30:00.000Z"
    },
    old_state: {
      state: "off",
      attributes: { /* ... */ }
    }
  }
};
```

---

## Working with Payload

### Reading Payload

```javascript
// Simple value
const value = msg.payload;

// Nested object
const temp = msg.payload.temperature;
const name = msg.payload.sensor?.name;  // Optional chaining

// Array
const first = msg.payload[0];
const last = msg.payload[msg.payload.length - 1];
```

### Setting Payload

```javascript
// Replace payload
msg.payload = "new value";

// Modify object payload
msg.payload.processed = true;
msg.payload.timestamp = Date.now();

// Transform payload
msg.payload = msg.payload.toUpperCase();
msg.payload = parseInt(msg.payload, 10);
msg.payload = JSON.parse(msg.payload);
```

### Payload Types

| Type | Example | Notes |
|------|---------|-------|
| String | `"hello"` | Most common |
| Number | `42`, `3.14` | Numeric operations |
| Boolean | `true`, `false` | Conditionals |
| Object | `{a: 1}` | Complex data |
| Array | `[1, 2, 3]` | Lists of items |
| Buffer | `Buffer.from()` | Binary data |
| null | `null` | No value |
| undefined | `undefined` | Property doesn't exist |

---

## Message Properties

### Common Properties

| Property | Description | Set By |
|----------|-------------|--------|
| `_msgid` | Unique message ID | System |
| `payload` | Primary data | Most nodes |
| `topic` | Message category | Various |
| `parts` | Sequence information | Split node |
| `complete` | Sequence complete flag | Join node |
| `error` | Error details | Catch node |
| `req` | HTTP request | HTTP In |
| `res` | HTTP response | HTTP In |
| `statusCode` | HTTP status code | HTTP Response |
| `headers` | HTTP headers | HTTP nodes |
| `cookies` | HTTP cookies | HTTP In |

### Custom Properties

```javascript
// Add custom properties
msg.customField = "value";
msg.metadata = {
  source: "sensor",
  timestamp: Date.now()
};

// Preserve custom properties
// GOOD - keeps existing properties
msg.payload = "new";
return msg;

// BAD - loses custom properties
msg = { payload: "new" };
return msg;
```

### Accessing Nested Properties

```javascript
// Dot notation
const value = msg.payload.data.value;

// Bracket notation (for dynamic keys)
const key = "temperature";
const value = msg.payload[key];

// Safe access with optional chaining
const value = msg.data?.entity?.state;

// With default value
const value = msg.payload?.value ?? "default";
```

---

## Message Routing

### Using Switch Node

```javascript
// Route by payload value
// Property: msg.payload
// Rules:
[
  {"t": "eq", "v": "on"},      // → Output 1
  {"t": "eq", "v": "off"},     // → Output 2
  {"t": "else"}                 // → Output 3
]
```

### Using Topic

```javascript
// Route by topic
// Property: msg.topic
// Rules:
[
  {"t": "eq", "v": "sensors/temperature"},
  {"t": "eq", "v": "sensors/humidity"},
  {"t": "cont", "v": "error"}
]
```

### Function Node Routing

```javascript
// Route to different outputs based on condition
if (msg.payload > 100) {
  return [msg, null];  // Output 1: High value
} else {
  return [null, msg];  // Output 2: Normal value
}

// Route to multiple outputs
if (msg.payload.type === "alert") {
  return [msg, msg];  // Both outputs
}
return [msg, null];   // Output 1 only
```

### Link Nodes for Complex Routing

```
┌─────────────────┐     ┌─────────────────┐
│   Link Out      │═════│    Link In      │
│   "to-alerts"   │     │  "from-alerts"  │
└─────────────────┘     └─────────────────┘
```

```javascript
// Link nodes connect by name across flows
// Useful for:
// - Cross-tab connections
// - Centralized error handling
// - Notification hubs
```

---

## Cloning Messages

### Why Clone?

When sending a message to multiple outputs, Node-RED passes the same object reference. Modifying it in one branch affects all branches.

### RED.util.cloneMessage()

```javascript
// Clone entire message
const newMsg = RED.util.cloneMessage(msg);
newMsg.payload = "modified";
return [msg, newMsg];  // Original and modified
```

### Manual Cloning

```javascript
// Shallow clone payload
msg.payload = { ...msg.payload, newField: "value" };

// Deep clone payload
msg.payload = JSON.parse(JSON.stringify(msg.payload));

// Clone specific properties
const newMsg = {
  _msgid: msg._msgid,
  payload: { ...msg.payload },
  topic: msg.topic
};
```

### Clone Patterns

```javascript
// Create multiple messages from one
const messages = msg.payload.items.map(item => ({
  _msgid: RED.util.generateId(),
  payload: item,
  topic: msg.topic
}));
return [messages];  // Array of messages to output 1

// Clone and modify
const alertMsg = RED.util.cloneMessage(msg);
alertMsg.topic = "alerts";
alertMsg.payload = {
  type: "warning",
  original: msg.payload
};
node.send([msg, alertMsg]);  // Both original and alert
```

---

## Multiple Outputs

### Configuring Outputs

Function nodes can have multiple outputs (configure in node settings).

```javascript
// 2-output function node
// Output 1: Success
// Output 2: Error

try {
  const result = processData(msg.payload);
  msg.payload = result;
  return [msg, null];  // Success output
} catch (err) {
  msg.error = err.message;
  return [null, msg];  // Error output
}
```

### Output Patterns

```javascript
// Send to output 1 only
return [msg, null];
return [msg];  // Implicit null for remaining outputs

// Send to output 2 only
return [null, msg];

// Send to both outputs
return [msg, msg];

// Send to output 1, with clone to output 2
const clone = RED.util.cloneMessage(msg);
return [msg, clone];

// Send different messages to each output
return [successMsg, errorMsg];

// Send multiple messages to output 1
return [[msg1, msg2, msg3], null];

// Drop message (no output)
return null;
```

### Conditional Multi-Output

```javascript
// Route based on value
const outputs = [null, null, null];  // 3 outputs
const value = msg.payload.priority;

if (value === "high") {
  outputs[0] = msg;
} else if (value === "medium") {
  outputs[1] = msg;
} else {
  outputs[2] = msg;
}

return outputs;
```

---

## Async Message Handling

### Using node.send()

For async operations, use `node.send()` instead of returning.

```javascript
// Async with callback
someAsyncFunction(msg.payload, (err, result) => {
  if (err) {
    msg.error = err;
    node.send([null, msg]);
  } else {
    msg.payload = result;
    node.send([msg, null]);
  }
});
return null;  // Don't auto-send

// Async with Promise
fetchData(msg.payload)
  .then(result => {
    msg.payload = result;
    node.send(msg);
  })
  .catch(err => {
    msg.error = err.message;
    node.error(err.message, msg);
  });
return null;

// Async with async/await
(async () => {
  try {
    const result = await fetchData(msg.payload);
    msg.payload = result;
    node.send(msg);
  } catch (err) {
    node.error(err.message, msg);
  }
})();
return null;
```

### node.done()

Signal completion for proper flow tracking:

```javascript
// With done callback
someAsyncOperation()
  .then(result => {
    msg.payload = result;
    node.send(msg);
    node.done();  // Signal completion
  })
  .catch(err => {
    node.error(err, msg);
    node.done();  // Even on error
  });
return null;
```

---

## Best Practices

### 1. Preserve Message Structure

```javascript
// GOOD - modify only what's needed
msg.payload = "new value";
msg.processed = true;
return msg;

// BAD - loses _msgid and other properties
return { payload: "new value" };
```

### 2. Use Debug Nodes

```javascript
// During development, add debug nodes
// Set to show complete message object
// Remove or disable for production
```

### 3. Validate Input

```javascript
// Check payload exists and is expected type
if (!msg.payload) {
  node.warn("No payload received");
  return null;
}

if (typeof msg.payload !== "object") {
  node.warn("Expected object payload");
  return null;
}
```

### 4. Handle Undefined

```javascript
// Safe property access
const value = msg.payload?.nested?.value ?? "default";

// Check before use
if (msg.data && msg.data.entity_id) {
  // Process
}
```

### 5. Document Expected Format

```javascript
/**
 * Expected input:
 *   msg.payload.temperature: number
 *   msg.payload.humidity: number
 *   msg.topic: string (sensor ID)
 *
 * Output:
 *   msg.payload: { average: number, status: string }
 */
```

### 6. Clean Up Large Messages

```javascript
// Remove large/temporary data before passing on
delete msg.rawData;
delete msg.debug;
return msg;
```

### 7. Use Consistent Naming

```javascript
// Consistent property names across flows
msg.payload.entityId     // Not entity_id mixed with entityId
msg.payload.timestamp    // Consistent naming
msg.payload.value        // Clear purpose
```

---

## Related References

- [Core Concepts](core-concepts.md) - Flows, nodes, wires
- [Node Types](node-types.md) - Available nodes
- [Function Nodes](function-nodes.md) - JavaScript details
- [Context Storage](context-storage.md) - Persistent storage
