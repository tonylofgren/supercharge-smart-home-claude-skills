# Context Storage in Node-RED

## Table of Contents
- [Overview](#overview)
- [Context Scopes](#context-scopes)
- [Basic Operations](#basic-operations)
- [Async Context](#async-context)
- [Context Stores](#context-stores)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)

---

## Overview

Context provides a way to store data that persists between messages. Unlike messages that flow through once, context data stays available for future use.

### Why Use Context?

| Use Case | Example |
|----------|---------|
| **State Tracking** | Remember last motion time |
| **Counters** | Count events over time |
| **Caching** | Store API responses |
| **Configuration** | Runtime settings |
| **Cross-Flow Data** | Share data between tabs |

### Context vs Messages

| Feature | Messages | Context |
|---------|----------|---------|
| Lifetime | Single flow execution | Persistent |
| Scope | Current flow path | Node/Flow/Global |
| Size | Should be small | Can be larger |
| Access | Sequential | Any time |

---

## Context Scopes

### Node Context

Available only to the specific node that created it.

```javascript
// In function node
context.set("counter", 0);
const count = context.get("counter");

// Shorthand
const count = context.counter;  // Get
context.counter = 5;            // Set (not recommended)
```

### Flow Context

Available to all nodes on the same flow (tab).

```javascript
// In function node
flow.set("lastMotion", Date.now());
const lastMotion = flow.get("lastMotion");

// Access from any node on same tab
const sharedData = flow.get("sharedData");
```

### Global Context

Available to all nodes across all flows.

```javascript
// In function node
global.set("homeMode", "away");
const mode = global.get("homeMode");

// Access from any node anywhere
const globalConfig = global.get("config");
```

### Scope Comparison

```
┌─────────────────────────────────────────────────────────┐
│                    GLOBAL CONTEXT                        │
│  global.set("key", value)                               │
│  Available everywhere                                    │
├───────────────────────┬─────────────────────────────────┤
│      FLOW 1          │         FLOW 2                   │
│  flow.set()          │     flow.set()                   │
│  ┌─────────────────┐ │  ┌─────────────────┐            │
│  │ Node A          │ │  │ Node C          │            │
│  │ context.set()   │ │  │ context.set()   │            │
│  └─────────────────┘ │  └─────────────────┘            │
│  ┌─────────────────┐ │  ┌─────────────────┐            │
│  │ Node B          │ │  │ Node D          │            │
│  │ context.set()   │ │  │ context.set()   │            │
│  └─────────────────┘ │  └─────────────────┘            │
└───────────────────────┴─────────────────────────────────┘
```

---

## Basic Operations

### Set Values

```javascript
// Set single value
context.set("count", 0);
flow.set("lastUpdate", Date.now());
global.set("homeMode", "home");

// Set object
flow.set("sensor", {
  temperature: 22.5,
  humidity: 45,
  timestamp: Date.now()
});

// Set array
context.set("history", [1, 2, 3, 4, 5]);

// Set nested path
flow.set("config.lighting.brightness", 80);
```

### Get Values

```javascript
// Get value
const count = context.get("count");
const mode = global.get("homeMode");

// Get with default
const count = context.get("count") || 0;
const mode = global.get("homeMode") ?? "away";

// Get nested path
const brightness = flow.get("config.lighting.brightness");

// Get all keys
const keys = context.keys();  // Returns array of key names
```

### Update Values

```javascript
// Increment counter
const count = context.get("count") || 0;
context.set("count", count + 1);

// Update object property
const sensor = flow.get("sensor") || {};
sensor.temperature = msg.payload;
sensor.timestamp = Date.now();
flow.set("sensor", sensor);

// Append to array
const history = context.get("history") || [];
history.push(msg.payload);
if (history.length > 100) history.shift();  // Limit size
context.set("history", history);
```

### Delete Values

```javascript
// Remove single key
context.set("tempData", undefined);

// Clear all context
const keys = context.keys();
keys.forEach(key => context.set(key, undefined));
```

---

## Async Context

When using file-based storage, context operations are async.

### Callback Style

```javascript
// Get with callback
context.get("key", function(err, value) {
  if (err) {
    node.error(err);
    return;
  }
  msg.payload = value;
  node.send(msg);
});

// Set with callback
context.set("key", value, function(err) {
  if (err) {
    node.error(err);
    return;
  }
  node.send(msg);
});
```

### Promise Style (Node-RED 2.0+)

```javascript
// Async get
const value = await context.get("key");
msg.payload = value;
return msg;

// Async set
await context.set("key", value);
return msg;

// Multiple operations
const [val1, val2] = await Promise.all([
  context.get("key1"),
  context.get("key2")
]);
```

---

## Context Stores

### Memory Store (Default)

- Fast access
- Lost on restart
- Good for temporary data

```javascript
// Implicit memory store
context.set("key", value);
flow.set("key", value);
global.set("key", value);
```

### File Store

- Persists across restarts
- Slower access
- Good for important state

```javascript
// Explicit file store
context.set("key", value, "file");
flow.set("key", value, "file");
global.set("key", value, "file");

// Get from file store
const value = context.get("key", "file");
```

### Configuring Stores

In `settings.js`:

```javascript
contextStorage: {
  default: "memoryOnly",
  memoryOnly: { module: 'memory' },
  file: { module: 'localfilesystem' }
}
```

### Store Selection

```javascript
// Store to memory (fast, temporary)
flow.set("cache", data);

// Store to file (slower, persistent)
flow.set("config", data, "file");

// Get from specific store
const config = flow.get("config", "file");
```

---

## Common Patterns

### Counter with Reset

```javascript
// Increment counter
const count = (context.get("count") || 0) + 1;
context.set("count", count);
msg.payload = count;

// Reset if requested
if (msg.reset) {
  context.set("count", 0);
  msg.payload = 0;
}
return msg;
```

### Rate Limiting

```javascript
// Track last execution time
const lastRun = context.get("lastRun") || 0;
const now = Date.now();
const minInterval = 5000;  // 5 seconds

if (now - lastRun < minInterval) {
  return null;  // Drop message, too soon
}

context.set("lastRun", now);
return msg;
```

### Debounce

```javascript
// Cancel pending timeout if exists
const timeout = context.get("timeout");
if (timeout) {
  clearTimeout(timeout);
}

// Set new timeout
const newTimeout = setTimeout(() => {
  context.set("timeout", null);
  node.send(msg);
}, 500);

context.set("timeout", newTimeout);
return null;  // Don't send immediately
```

### State Machine

```javascript
const STATES = {
  IDLE: "idle",
  ARMING: "arming",
  ARMED: "armed",
  TRIGGERED: "triggered"
};

// Get current state
let state = flow.get("alarmState") || STATES.IDLE;
const event = msg.payload.event;

// State transitions
const transitions = {
  idle: { arm: "arming" },
  arming: { complete: "armed", cancel: "idle" },
  armed: { trigger: "triggered", disarm: "idle" },
  triggered: { disarm: "idle" }
};

// Process transition
if (transitions[state] && transitions[state][event]) {
  state = transitions[state][event];
  flow.set("alarmState", state);
  msg.payload = { state, event };
  return msg;
}

return null;  // Invalid transition
```

### Caching with TTL

```javascript
const CACHE_TTL = 60000;  // 1 minute

// Check cache
const cached = flow.get("apiCache");
if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
  msg.payload = cached.data;
  msg.fromCache = true;
  return msg;
}

// Fetch fresh data (would be async in practice)
const freshData = msg.payload;

// Update cache
flow.set("apiCache", {
  data: freshData,
  timestamp: Date.now()
});

msg.fromCache = false;
return msg;
```

### Rolling Average

```javascript
const MAX_SAMPLES = 10;

// Get history
const history = context.get("history") || [];

// Add new value
history.push(msg.payload);

// Limit size
while (history.length > MAX_SAMPLES) {
  history.shift();
}

// Calculate average
const average = history.reduce((a, b) => a + b, 0) / history.length;

// Store updated history
context.set("history", history);

msg.payload = {
  current: msg.payload,
  average: average,
  samples: history.length
};
return msg;
```

### Last N Values

```javascript
const MAX_VALUES = 100;

// Get history
const values = flow.get("sensorHistory") || [];

// Add new entry
values.push({
  value: msg.payload,
  timestamp: Date.now(),
  entity: msg.topic
});

// Trim old values
while (values.length > MAX_VALUES) {
  values.shift();
}

// Save
flow.set("sensorHistory", values);

return msg;
```

### Presence Tracking

```javascript
// Track which entities are home
const presence = global.get("presence") || {};
const entity = msg.data.entity_id;
const state = msg.payload;

// Update presence
if (entity.startsWith("person.")) {
  const person = entity.replace("person.", "");
  presence[person] = state === "home";
  global.set("presence", presence);
}

// Check if anyone home
const anyoneHome = Object.values(presence).some(v => v);
msg.anyoneHome = anyoneHome;
msg.presence = presence;

return msg;
```

---

## Best Practices

### 1. Initialize with Defaults

```javascript
// Always provide defaults
const count = context.get("count") ?? 0;
const config = flow.get("config") || { brightness: 100 };
```

### 2. Clean Up Old Data

```javascript
// Periodically clean old entries
const data = flow.get("eventLog") || [];
const oneHourAgo = Date.now() - 3600000;
const cleaned = data.filter(e => e.timestamp > oneHourAgo);
flow.set("eventLog", cleaned);
```

### 3. Use Descriptive Keys

```javascript
// Good - descriptive keys
flow.set("lighting.livingRoom.lastMotion", Date.now());
global.set("homeAssistant.connection.status", "connected");

// Bad - unclear keys
flow.set("lm", Date.now());
global.set("s", "c");
```

### 4. Limit Context Size

```javascript
// Don't store unlimited data
const MAX_ENTRIES = 1000;
const entries = context.get("log") || [];

if (entries.length >= MAX_ENTRIES) {
  entries.splice(0, entries.length - MAX_ENTRIES + 1);
}

entries.push(newEntry);
context.set("log", entries);
```

### 5. Use File Store for Important Data

```javascript
// Temporary cache - memory is fine
flow.set("apiCache", data);

// Important state - use file
flow.set("alarmState", state, "file");
global.set("userSettings", settings, "file");
```

### 6. Document Context Usage

```javascript
/**
 * Context variables used:
 *
 * flow.motionTimeout - Timeout ID for motion delay
 * flow.lastMotionTime - Timestamp of last motion
 * flow.lightsManuallyControlled - Boolean flag
 *
 * global.homeMode - Current home mode (home/away/night)
 */
```

### 7. Avoid Context in Hot Paths

```javascript
// Bad - reading context every message
const config = flow.get("config");  // Every message!

// Better - cache locally if config rarely changes
let cachedConfig = null;

// On deploy or periodic refresh
cachedConfig = flow.get("config");

// On message - use cached value
const config = cachedConfig;
```

---

## Related References

- [Core Concepts](core-concepts.md) - Flows, nodes, messages
- [Function Nodes](function-nodes.md) - JavaScript in Node-RED
- [State Machines](state-machines.md) - Complex state management
- [Performance](performance.md) - Optimization tips
