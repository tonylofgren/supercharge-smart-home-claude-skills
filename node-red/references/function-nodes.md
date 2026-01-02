# Function Nodes

Writing JavaScript in Node-RED function nodes.

---

## Basic Structure

```javascript
// Function node receives msg object
// Must return msg (or array) to pass downstream

// Simple passthrough
return msg;

// Stop the flow
return null;

// Multiple outputs (wire to different nodes)
return [msg1, msg2, msg3];
```

---

## Available Objects

### msg - The Message Object

```javascript
// Common properties
msg.payload      // Primary data
msg.topic        // Message category/routing
msg._msgid       // Unique message ID

// Home Assistant specific
msg.data.entity_id
msg.data.new_state
msg.data.old_state
```

### node - Node Instance

```javascript
// Send messages asynchronously
node.send(msg);
node.send([msg1, msg2]);  // Multiple outputs

// Logging
node.log("Info message");
node.warn("Warning message");
node.error("Error message", msg);  // Include msg for catch node

// Status indicator
node.status({fill:"green", shape:"dot", text:"OK"});
node.status({fill:"red", shape:"ring", text:"Error"});
node.status({});  // Clear status
```

### context - Node Context

```javascript
// Persistent within this node instance
context.set("key", value);
const val = context.get("key");
context.set("key", value, "file");  // Persistent across restarts
```

### flow - Flow Context

```javascript
// Shared across nodes in same flow (tab)
flow.set("key", value);
const val = flow.get("key");
```

### global - Global Context

```javascript
// Shared across all flows
global.set("key", value);
const val = global.get("key");

// Access Home Assistant states
const ha = global.get("homeassistant");
const state = ha.homeAssistant.states["light.living_room"]?.state;
```

### env - Environment Variables

```javascript
// Access environment variables
const value = env.get("MY_VAR");
```

---

## Common Patterns

### Conditional Routing

```javascript
// Route to different outputs based on condition
if (msg.payload > 100) {
    return [msg, null];  // Output 1
} else {
    return [null, msg];  // Output 2
}
```

### Rate Limiting

```javascript
const MIN_INTERVAL = 5000;  // 5 seconds
const lastRun = context.get("lastRun") || 0;

if (Date.now() - lastRun < MIN_INTERVAL) {
    return null;  // Drop message
}

context.set("lastRun", Date.now());
return msg;
```

### Debouncing

```javascript
// Only output after messages stop for 500ms
const timeout = context.get("timeout");
if (timeout) clearTimeout(timeout);

context.set("timeout", setTimeout(() => {
    context.set("timeout", null);
    node.send(msg);
}, 500));

return null;
```

### State Tracking

```javascript
const previousState = context.get("state");
const currentState = msg.payload;

if (previousState !== currentState) {
    context.set("state", currentState);
    msg.changed = true;
    msg.previousState = previousState;
    return msg;
}

return null;  // No change
```

### Counting

```javascript
const count = (context.get("count") || 0) + 1;
context.set("count", count);
msg.count = count;
return msg;
```

### Rolling Average

```javascript
const MAX_SAMPLES = 10;
const history = context.get("history") || [];

history.push(parseFloat(msg.payload));
while (history.length > MAX_SAMPLES) {
    history.shift();
}

context.set("history", history);
msg.average = history.reduce((a, b) => a + b, 0) / history.length;
return msg;
```

---

## Working with Home Assistant

### Get Entity State

```javascript
const ha = global.get("homeassistant");
const states = ha.homeAssistant.states;

// Get state
const lightState = states["light.living_room"]?.state;

// Get attribute
const brightness = states["light.living_room"]?.attributes?.brightness;

// Check if entity exists
if (!states["sensor.temperature"]) {
    node.warn("Entity not found");
    return null;
}
```

### Build Service Call

```javascript
msg.payload = {
    action: "light.turn_on",
    target: {
        entity_id: ["light.living_room"]
    },
    data: {
        brightness_pct: 80,
        transition: 2
    }
};
return msg;
```

### Dynamic Entity Selection

```javascript
// Get all lights that are on
const ha = global.get("homeassistant").homeAssistant.states;
const onLights = Object.keys(ha)
    .filter(id => id.startsWith("light."))
    .filter(id => ha[id].state === "on");

msg.payload = {
    action: "light.turn_off",
    target: { entity_id: onLights }
};
return msg;
```

---

## Async Operations

### Using Promises

```javascript
// Function node with outputs: 1
// On Start: leave empty
// On Message:

const fetchData = async () => {
    try {
        const response = await fetch("https://api.example.com/data");
        const data = await response.json();
        msg.payload = data;
        node.send(msg);
    } catch (error) {
        node.error("Fetch failed: " + error.message, msg);
    }
};

fetchData();
return null;  // Don't return msg synchronously
```

### setTimeout / setInterval

```javascript
// Delayed execution
setTimeout(() => {
    node.send(msg);
}, 5000);

return null;

// Periodic execution (use inject node instead when possible)
const interval = context.get("interval");
if (!interval) {
    context.set("interval", setInterval(() => {
        node.send({ payload: Date.now() });
    }, 60000));
}
```

---

## Setup and Cleanup

### On Start Tab

```javascript
// Runs once when flow is deployed
// Good for initialization

context.set("initialized", true);
context.set("startTime", Date.now());
```

### On Stop Tab

```javascript
// Runs when flow is stopped/redeployed
// Good for cleanup

const interval = context.get("interval");
if (interval) {
    clearInterval(interval);
}

const timeout = context.get("timeout");
if (timeout) {
    clearTimeout(timeout);
}
```

---

## Error Handling

### Try-Catch

```javascript
try {
    const data = JSON.parse(msg.payload);
    msg.payload = data.value;
    return msg;
} catch (error) {
    node.error("Parse error: " + error.message, msg);
    return null;
}
```

### Validation

```javascript
// Validate required fields
if (!msg.payload) {
    node.warn("Missing payload");
    return null;
}

if (typeof msg.payload !== "number") {
    node.error("Payload must be a number", msg);
    return null;
}

if (msg.payload < 0 || msg.payload > 100) {
    node.warn("Value out of range: " + msg.payload);
    msg.payload = Math.max(0, Math.min(100, msg.payload));
}

return msg;
```

---

## External Modules

### Built-in Modules

```javascript
// Available without configuration
const util = require("util");
const os = require("os");
```

### Custom Modules

Edit `settings.js` to add modules:

```javascript
functionGlobalContext: {
    moment: require("moment"),
    lodash: require("lodash")
}
```

Then in function node:

```javascript
const moment = global.get("moment");
const _ = global.get("lodash");

msg.formatted = moment().format("YYYY-MM-DD HH:mm");
msg.unique = _.uniq(msg.payload);
```

---

## Best Practices

### Keep Functions Focused

```javascript
// Good: Single responsibility
const temperature = parseFloat(msg.payload);
msg.payload = (temperature * 9/5) + 32;  // C to F
return msg;

// Bad: Too many responsibilities
// (parsing, validation, conversion, formatting, logging)
```

### Use Meaningful Status

```javascript
// Show what the node is doing
node.status({
    fill: "green",
    shape: "dot",
    text: `${msg.payload}°C at ${new Date().toLocaleTimeString()}`
});
```

### Handle Edge Cases

```javascript
// Safe property access
const value = msg.payload?.data?.value ?? "default";

// Handle empty arrays
const items = msg.payload || [];
if (items.length === 0) {
    node.status({fill: "yellow", shape: "ring", text: "No items"});
    return null;
}
```

### Document Complex Logic

```javascript
/**
 * Calculate heating demand based on:
 * - Current temperature vs target
 * - Rate of temperature change
 * - Outside temperature
 */
const demand = calculateDemand(current, target, outside);
```

---

## Performance Tips

1. **Avoid heavy computation** in function nodes
2. **Cache expensive lookups** in context
3. **Use built-in nodes** when possible (faster)
4. **Limit state access** - batch reads when possible
5. **Clear timeouts** in On Stop to prevent memory leaks

---

## Debugging

### Console Output

```javascript
// Shows in Node-RED debug sidebar when connected to debug node
node.warn("Variable value: " + JSON.stringify(variable));

// More detailed logging
console.log("Debug info:", {
    payload: msg.payload,
    topic: msg.topic,
    timestamp: Date.now()
});
```

### Status Indicators

```javascript
// Visual feedback on node
node.status({fill: "blue", shape: "dot", text: "Processing..."});

// After operation
node.status({fill: "green", shape: "dot", text: "Done"});

// On error
node.status({fill: "red", shape: "ring", text: "Failed"});
```
