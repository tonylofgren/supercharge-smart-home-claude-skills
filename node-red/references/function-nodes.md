# Function Nodes in Node-RED

JavaScript programming inside Node-RED.

## Basic Syntax

```javascript
// msg is the incoming message
// msg.payload contains the main data

// Modify the message
msg.payload = msg.payload.toUpperCase();

// Return to send to next node
return msg;

// Return null to stop the message
return null;
```

## Multiple Outputs

Configure the function node with multiple outputs:

```javascript
// 2 outputs configured
if (msg.payload > 50) {
  return [msg, null]; // Send to output 1
} else {
  return [null, msg]; // Send to output 2
}
```

Send to all outputs:
```javascript
return [msg, msg]; // Clone to both outputs
```

## Multiple Messages

Send multiple messages to one output:
```javascript
const messages = [
  { payload: "first" },
  { payload: "second" },
  { payload: "third" }
];
return [messages]; // Array of messages to output 1
```

Send in sequence with delay:
```javascript
const items = msg.payload.items;
items.forEach((item, index) => {
  setTimeout(() => {
    node.send({ payload: item });
  }, index * 100);
});
node.done();
return null;
```

## Context Storage

### Node Context (Private to This Node)

```javascript
// Initialize on first run
let count = context.get('count') || 0;
count++;
context.set('count', count);
msg.count = count;
return msg;
```

### Flow Context (Shared in Tab)

```javascript
// Store state
flow.set('lastMotion', Date.now());
flow.set('motionCount', (flow.get('motionCount') || 0) + 1);

// Retrieve state
const lastMotion = flow.get('lastMotion');
```

### Global Context (Shared Everywhere)

```javascript
// Store global settings
global.set('homeMode', 'away');

// Access Home Assistant states (special global)
const states = global.get("homeassistant").homeAssistant.states;
const temp = states["sensor.temperature"].state;
```

## Accessing Home Assistant

### Get Entity State

```javascript
const states = global.get("homeassistant").homeAssistant.states;

// Single entity
const light = states["light.living_room"];
if (light) {
  msg.state = light.state;
  msg.brightness = light.attributes.brightness;
}

return msg;
```

### Find Entities by Pattern

```javascript
const states = global.get("homeassistant").homeAssistant.states;

// All lights that are on
const lightsOn = Object.keys(states)
  .filter(id => id.startsWith("light."))
  .filter(id => states[id].state === "on");

msg.lightsOn = lightsOn;
return msg;
```

### Check Person States

```javascript
const states = global.get("homeassistant").homeAssistant.states;

const people = Object.entries(states)
  .filter(([id]) => id.startsWith("person."))
  .map(([id, state]) => ({
    id,
    name: state.attributes.friendly_name,
    location: state.state
  }));

const anyoneHome = people.some(p => p.location === "home");
msg.people = people;
msg.anyoneHome = anyoneHome;
return msg;
```

## Environment Variables

### In Subflows Only

```javascript
// Access subflow environment variable
const threshold = env.get('THRESHOLD');
const entityId = env.get('ENTITY_ID');
```

### From System (via settings.js)

Configure in settings.js:
```javascript
functionGlobalContext: {
  env: process.env
}
```

Then access:
```javascript
const apiKey = global.get('env').WEATHER_API_KEY;
```

## Node Status

Show status under the node:

```javascript
// Show activity
node.status({ fill: "green", shape: "dot", text: "active" });

// Show warning
node.status({ fill: "yellow", shape: "ring", text: "waiting" });

// Show error
node.status({ fill: "red", shape: "dot", text: "error" });

// Clear status
node.status({});
```

With dynamic text:
```javascript
const count = context.get('count') || 0;
node.status({ fill: "blue", shape: "dot", text: `processed: ${count}` });
```

## Error Handling

### Throw Error

```javascript
if (!msg.payload) {
  node.error("Missing payload", msg);
  return null;
}
```

### Warn (Non-Fatal)

```javascript
node.warn("Unexpected value, using default");
```

### Log (Debug Only)

```javascript
node.log("Processing started");
```

### Try-Catch

```javascript
try {
  const data = JSON.parse(msg.payload);
  msg.payload = data;
  return msg;
} catch (error) {
  node.error(`Parse error: ${error.message}`, msg);
  return null;
}
```

## Async Operations

### Using Promises

```javascript
async function fetchData() {
  try {
    const response = await someAsyncOperation();
    msg.payload = response;
    node.send(msg);
  } catch (error) {
    node.error(error.message, msg);
  }
  node.done();
}

fetchData();
return null; // IMPORTANT: prevent sync output
```

### With Timeout

```javascript
async function fetchWithTimeout() {
  const timeout = 5000;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(msg.url, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    msg.payload = await response.json();
    node.send(msg);
  } catch (error) {
    if (error.name === 'AbortError') {
      node.error("Request timed out", msg);
    } else {
      node.error(error.message, msg);
    }
  }
  node.done();
}

fetchWithTimeout();
return null;
```

## External Libraries

### Configure in settings.js

```javascript
functionGlobalContext: {
  moment: require('moment'),
  lodash: require('lodash'),
  axios: require('axios')
}
```

### Use in Function Node

```javascript
const moment = global.get('moment');
const _ = global.get('lodash');

// Format date
const formatted = moment().format('YYYY-MM-DD HH:mm:ss');

// Use lodash
const value = _.get(msg, 'payload.nested.value', 'default');
```

**IMPORTANT:** Prefer built-in nodes over libraries when possible!
- HTTP requests → http request node
- JSON manipulation → change node + JSONata
- Delays → delay node

## Common Patterns

### Debounce

```javascript
const key = msg.topic || 'default';
const timeout = 1000; // 1 second

const lastTime = context.get(`lastTime_${key}`) || 0;
const now = Date.now();

if (now - lastTime < timeout) {
  return null; // Skip this message
}

context.set(`lastTime_${key}`, now);
return msg;
```

### Rate Limit

```javascript
const maxPerMinute = 10;
const windowMs = 60000;

let history = context.get('rateHistory') || [];
const now = Date.now();

// Remove old entries
history = history.filter(t => now - t < windowMs);

if (history.length >= maxPerMinute) {
  node.warn("Rate limit exceeded");
  return null;
}

history.push(now);
context.set('rateHistory', history);
return msg;
```

### State Machine

```javascript
const STATES = { IDLE: 'idle', ACTIVE: 'active', COOLDOWN: 'cooldown' };

let state = flow.get('machineState') || STATES.IDLE;
const event = msg.payload;

switch (state) {
  case STATES.IDLE:
    if (event === 'start') {
      state = STATES.ACTIVE;
    }
    break;
  case STATES.ACTIVE:
    if (event === 'stop') {
      state = STATES.COOLDOWN;
    }
    break;
  case STATES.COOLDOWN:
    if (event === 'reset') {
      state = STATES.IDLE;
    }
    break;
}

flow.set('machineState', state);
msg.state = state;
return msg;
```

### Moving Average

```javascript
const windowSize = 10;
let values = context.get('values') || [];

values.push(parseFloat(msg.payload));
if (values.length > windowSize) {
  values = values.slice(-windowSize);
}

context.set('values', values);

const average = values.reduce((a, b) => a + b, 0) / values.length;
msg.payload = Math.round(average * 100) / 100;
msg.sampleCount = values.length;
return msg;
```

## Setup and Finalization

### On Deploy (Setup)

Configure in "On Start" tab:
```javascript
// Runs when flow is deployed
context.set('count', 0);
flow.set('initialized', true);
node.log("Function initialized");
```

### On Close (Cleanup)

Configure in "On Stop" tab:
```javascript
// Runs when flow is stopped/redeployed
const count = context.get('count');
node.log(`Processed ${count} messages`);
```

## Performance Tips

1. **Avoid heavy computation** - Blocks the event loop
2. **Limit context writes** - Batch updates when possible
3. **Use built-in nodes** - They're optimized
4. **Clean up timers** - In the On Stop handler
5. **Limit history size** - Always cap arrays

```javascript
// BAD: Unlimited growth
history.push(newItem);

// GOOD: Capped size
history.push(newItem);
if (history.length > 100) {
  history = history.slice(-100);
}
```
