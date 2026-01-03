# Error Handling in Node-RED

Handle errors gracefully.

## Catch Node

The primary error handling mechanism.

### Basic Setup

```
[nodes that may error] ──> ...
         │
         └──> [catch] ──> [error handler]
```

### Configuration

```json
{
  "type": "catch",
  "scope": ["node_id_1", "node_id_2"],
  "uncaught": false
}
```

### Scope Options

| Setting | Description |
|---------|-------------|
| `scope: ["id1", "id2"]` | Catch from specific nodes |
| `scope: null` | Catch from all nodes in flow |
| `uncaught: true` | Catch uncaught errors (not already caught) |

### Error Message Properties

```javascript
msg.error = {
  message: "Error text here",
  source: {
    id: "node_id",
    type: "api-call-service",
    name: "Turn On Light",
    count: 1  // How many times error has occurred
  }
};

// Original message is preserved
msg.payload // Still available
msg.topic   // Still available
```

## Throwing Errors

### From Function Node

```javascript
// Method 1: node.error() - catchable
node.error("Something went wrong", msg);
return null;

// Method 2: throw - catchable
throw new Error("Something went wrong");

// Method 3: Return null to stop message (no error)
if (!msg.payload) {
  node.warn("No payload, stopping");
  return null;
}
```

### Error Severity

```javascript
// Debug info (not shown to user)
node.log("Processing started");

// Warning (yellow in sidebar)
node.warn("Unexpected value, using default");

// Error (red, catchable)
node.error("Failed to process", msg);
```

## Retry Pattern

### Simple Retry

```
[action] ──error──> [catch] ──> [delay] ──> [action]
                       │
                       └──> [check retry count]
```

### With Exponential Backoff

```javascript
// Initialize retry state
if (!msg._retryCount) {
  msg._retryCount = 0;
  msg._maxRetries = 3;
}

msg._retryCount++;

if (msg._retryCount > msg._maxRetries) {
  // All retries failed
  node.error("Max retries exceeded", msg);
  return null;
}

// Calculate exponential delay: 1s, 2s, 4s
const delay = Math.pow(2, msg._retryCount - 1) * 1000;
msg._delay = delay;

node.status({
  fill: "yellow",
  shape: "ring",
  text: `retry ${msg._retryCount}/${msg._maxRetries}`
});

return msg;
```

### Delay Node Configuration

For variable delay:
```json
{
  "type": "delay",
  "pauseType": "delayv",
  "timeout": "5",
  "timeoutUnits": "seconds"
}
```

Reads delay from `msg.delay` in milliseconds.

## Error Notification

### Send Alert on Error

```javascript
// In catch handler
msg.payload = {
  action: "notify.mobile_app_phone",
  data: {
    title: "Node-RED Error",
    message: `${msg.error.source.name}: ${msg.error.message}`,
    data: {
      priority: "high"
    }
  }
};
return msg;
```

### Log to File

```javascript
// In catch handler
const fs = global.get('fs');
const logEntry = {
  timestamp: new Date().toISOString(),
  node: msg.error.source.name,
  type: msg.error.source.type,
  error: msg.error.message,
  payload: JSON.stringify(msg.payload)
};

// Append to log
msg.payload = JSON.stringify(logEntry) + "\n";
msg.filename = "/data/nodered-errors.log";
return msg;
```

## Validation Pattern

### Input Validation

```javascript
// Validate before processing
function validate(msg) {
  if (!msg.payload) {
    return { valid: false, error: "Missing payload" };
  }

  if (typeof msg.payload !== 'object') {
    return { valid: false, error: "Payload must be object" };
  }

  if (!msg.payload.entity_id) {
    return { valid: false, error: "Missing entity_id" };
  }

  return { valid: true };
}

const result = validate(msg);

if (!result.valid) {
  node.error(result.error, msg);
  return null;
}

return msg;
```

### State Validation

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const entityId = msg.payload.entity_id;

// Check entity exists
if (!states[entityId]) {
  node.error(`Entity not found: ${entityId}`, msg);
  return null;
}

// Check entity is available
if (states[entityId].state === "unavailable") {
  node.warn(`Entity unavailable: ${entityId}`);
  return null;
}

return msg;
```

## Fallback Pattern

### Primary/Secondary

```
           ┌──> [primary action] ──> [catch] ──> [fallback action]
[trigger] ─┤
           └──> [always action]
```

### In Function Node

```javascript
const states = global.get("homeassistant").homeAssistant.states;

// Primary: specific entity
let targetEntity = "light.living_room_main";

// Check if available
if (!states[targetEntity] || states[targetEntity].state === "unavailable") {
  // Fallback: alternative entity
  targetEntity = "light.living_room_secondary";

  if (!states[targetEntity] || states[targetEntity].state === "unavailable") {
    // Ultimate fallback: any light in area
    targetEntity = Object.keys(states)
      .filter(id => id.startsWith("light.living_room"))
      .find(id => states[id].state !== "unavailable");
  }
}

if (!targetEntity) {
  node.error("No available light found", msg);
  return null;
}

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: [targetEntity] }
};
return msg;
```

## Timeout Pattern

### With Timer

```javascript
// Set timeout
const timeoutMs = 30000;
const timeoutId = setTimeout(() => {
  node.error("Operation timed out", msg);
  node.done();
}, timeoutMs);

// Store timeout ID for cleanup
msg._timeoutId = timeoutId;

// Perform operation
try {
  await someAsyncOperation();
  clearTimeout(timeoutId);
  node.send(msg);
} catch (error) {
  clearTimeout(timeoutId);
  node.error(error.message, msg);
}

node.done();
return null;
```

### With Wait Until Node

```json
{
  "type": "ha-wait-until",
  "timeout": 30,
  "timeoutUnits": "seconds"
}
```

Output 2 triggers on timeout.

## Circuit Breaker Pattern

Prevent cascading failures:

```javascript
const maxFailures = 3;
const resetTime = 60000; // 1 minute

let state = flow.get('circuitState') || { failures: 0, open: false, openedAt: 0 };

// Check if circuit is open
if (state.open) {
  if (Date.now() - state.openedAt > resetTime) {
    // Try to close
    state.open = false;
    state.failures = 0;
  } else {
    // Still open, reject
    node.warn("Circuit breaker open");
    return null;
  }
}

// Process normally
try {
  // Your operation here
  state.failures = 0; // Reset on success
  flow.set('circuitState', state);
  return msg;
} catch (error) {
  state.failures++;

  if (state.failures >= maxFailures) {
    state.open = true;
    state.openedAt = Date.now();
    node.error("Circuit breaker opened", msg);
  }

  flow.set('circuitState', state);
  return null;
}
```

## Error Aggregation

Collect errors before alerting:

```javascript
// Add error to collection
let errors = flow.get('errorCollection') || [];
errors.push({
  time: Date.now(),
  source: msg.error.source.name,
  message: msg.error.message
});

// Keep last hour only
const oneHourAgo = Date.now() - (60 * 60 * 1000);
errors = errors.filter(e => e.time > oneHourAgo);

flow.set('errorCollection', errors);

// Alert if threshold exceeded
if (errors.length >= 5) {
  // Send aggregated alert
  msg.payload = {
    action: "notify.mobile_app_phone",
    data: {
      title: `${errors.length} Errors in Last Hour`,
      message: errors.map(e => e.source).join(", ")
    }
  };
  return msg;
}

return null; // Don't alert for single errors
```

## Best Practices

1. **Always handle errors** - Add catch nodes to critical flows
2. **Log errors** - For debugging and monitoring
3. **Retry appropriately** - Not everything should retry
4. **Validate inputs** - Fail fast with clear messages
5. **Set timeouts** - Prevent hung operations
6. **Notify selectively** - Don't spam on every error
7. **Preserve context** - Keep original message when catching
8. **Document error handling** - Comment complex patterns
