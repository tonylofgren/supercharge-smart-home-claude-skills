# Context Storage in Node-RED

Store and share data between nodes and flows.

## Context Scopes

### Node Context

Private to a single node instance.

```javascript
// Store
context.set('count', 0);
context.set('lastValue', msg.payload);

// Retrieve
const count = context.get('count') || 0;
const lastValue = context.get('lastValue');

// Store multiple
context.set(['key1', 'key2'], ['value1', 'value2']);

// Retrieve multiple
const [val1, val2] = context.get(['key1', 'key2']);
```

**Use cases:**
- Per-node counters
- Last message tracking
- Node-specific state

### Flow Context

Shared between all nodes in the same flow (tab).

```javascript
// Store
flow.set('motionActive', true);
flow.set('lastMotionTime', Date.now());

// Retrieve
const active = flow.get('motionActive');
const lastTime = flow.get('lastMotionTime');
```

**Use cases:**
- Flow-wide state
- Shared configuration
- Cross-node communication within tab

### Global Context

Shared across all flows in Node-RED.

```javascript
// Store
global.set('homeMode', 'away');
global.set('systemStartTime', Date.now());

// Retrieve
const mode = global.get('homeMode');
```

**Use cases:**
- Application-wide settings
- Cross-flow state
- System-level data

## Special Global: Home Assistant States

When connected to Home Assistant, all entity states are available:

```javascript
// Get all states
const states = global.get("homeassistant").homeAssistant.states;

// Access specific entity
const light = states["light.living_room"];
const temp = states["sensor.temperature"];

// Entity structure
{
  entity_id: "sensor.temperature",
  state: "23.5",
  attributes: {
    unit_of_measurement: "°C",
    device_class: "temperature",
    friendly_name: "Living Room Temperature"
  },
  last_changed: "2024-01-01T12:00:00Z",
  last_updated: "2024-01-01T12:00:00Z"
}
```

### Common HA State Patterns

```javascript
const states = global.get("homeassistant").homeAssistant.states;

// All lights
const lights = Object.keys(states)
  .filter(id => id.startsWith("light."));

// Lights that are on
const lightsOn = Object.keys(states)
  .filter(id => id.startsWith("light."))
  .filter(id => states[id].state === "on");

// All people
const people = Object.entries(states)
  .filter(([id]) => id.startsWith("person."))
  .map(([id, entity]) => ({
    id,
    name: entity.attributes.friendly_name,
    location: entity.state
  }));

// Anyone home?
const anyoneHome = Object.keys(states)
  .filter(id => id.startsWith("person."))
  .some(id => states[id].state === "home");

// Temperature sensors
const temps = Object.entries(states)
  .filter(([id, entity]) =>
    entity.attributes?.device_class === "temperature" &&
    entity.state !== "unavailable"
  )
  .map(([id, entity]) => ({
    id,
    name: entity.attributes.friendly_name,
    temp: parseFloat(entity.state)
  }));
```

## Persistence

By default, context is lost when Node-RED restarts.

### Configure File-Based Storage

In `settings.js`:

```javascript
contextStorage: {
  default: {
    module: "localfilesystem"
  }
}
```

### Multiple Stores

```javascript
contextStorage: {
  default: {
    module: "memory"
  },
  persistent: {
    module: "localfilesystem"
  }
}
```

Use specific store:

```javascript
// Store to persistent
flow.set('important', value, 'persistent');

// Retrieve from persistent
const value = flow.get('important', 'persistent');
```

## Async Context Access

For large data or persistent storage:

```javascript
// Async get
flow.get('key', 'persistent', function(err, value) {
  if (err) {
    node.error(err);
    return;
  }
  msg.payload = value;
  node.send(msg);
});

// Async set
flow.set('key', value, 'persistent', function(err) {
  if (err) {
    node.error(err);
    return;
  }
  node.send(msg);
});

// Don't return msg synchronously when using async
return null;
```

## Data Patterns

### Counter

```javascript
let count = context.get('count') || 0;
count++;
context.set('count', count);
msg.count = count;
return msg;
```

### Rate Limiting

```javascript
const maxPerMinute = 10;
let timestamps = context.get('timestamps') || [];
const now = Date.now();
const oneMinuteAgo = now - 60000;

// Remove old timestamps
timestamps = timestamps.filter(t => t > oneMinuteAgo);

if (timestamps.length >= maxPerMinute) {
  // Rate limited
  return null;
}

timestamps.push(now);
context.set('timestamps', timestamps);
return msg;
```

### Debounce

```javascript
const debounceMs = 1000;
const lastTime = context.get('lastTime') || 0;
const now = Date.now();

if (now - lastTime < debounceMs) {
  return null;
}

context.set('lastTime', now);
return msg;
```

### Running Average

```javascript
const windowSize = 10;
let values = context.get('values') || [];

values.push(parseFloat(msg.payload));
if (values.length > windowSize) {
  values = values.slice(-windowSize);
}

context.set('values', values);

const average = values.reduce((a, b) => a + b, 0) / values.length;
msg.average = Math.round(average * 100) / 100;
return msg;
```

### State History

```javascript
const maxHistory = 50;
let history = flow.get('history') || [];

history.push({
  timestamp: Date.now(),
  value: msg.payload,
  entity: msg.topic
});

if (history.length > maxHistory) {
  history = history.slice(-maxHistory);
}

flow.set('history', history);
```

### Caching

```javascript
const cacheKey = msg.topic;
const cacheTTL = 60000; // 1 minute
const cache = flow.get('cache') || {};

// Check cache
if (cache[cacheKey] && Date.now() - cache[cacheKey].time < cacheTTL) {
  msg.payload = cache[cacheKey].value;
  msg.cached = true;
  return msg;
}

// Cache miss - fetch and store
// ... fetch data ...

cache[cacheKey] = {
  value: fetchedValue,
  time: Date.now()
};
flow.set('cache', cache);

msg.payload = fetchedValue;
msg.cached = false;
return msg;
```

## Memory Management

### Limit Array Sizes

```javascript
// BAD: Unlimited growth
history.push(newItem);

// GOOD: Capped size
history.push(newItem);
if (history.length > 100) {
  history = history.slice(-100);
}
```

### Clean Up Old Data

```javascript
// Remove entries older than 24 hours
const cutoff = Date.now() - (24 * 60 * 60 * 1000);
let data = flow.get('timestampedData') || {};

Object.keys(data).forEach(key => {
  if (data[key].timestamp < cutoff) {
    delete data[key];
  }
});

flow.set('timestampedData', data);
```

### Clear Context

```javascript
// Clear specific key
context.set('key', undefined);

// Clear all node context
context.keys().forEach(key => context.set(key, undefined));

// Clear flow context (careful!)
flow.keys().forEach(key => flow.set(key, undefined));
```

## Viewing Context

### In Node-RED Sidebar

1. Open Context Data sidebar tab
2. Click Refresh to see current values
3. Expand nodes/flows to see values

### In Function Node

```javascript
// Debug: show all context keys
node.warn("Node context: " + JSON.stringify(context.keys()));
node.warn("Flow context: " + JSON.stringify(flow.keys()));
node.warn("Global context: " + JSON.stringify(global.keys()));
```

## Best Practices

1. **Initialize with defaults**: `context.get('key') || defaultValue`
2. **Use appropriate scope**: Don't use global when flow works
3. **Clean up old data**: Prevent memory leaks
4. **Use meaningful key names**: Not `x`, `temp`, but `lastMotionTimestamp`
5. **Document context usage**: Comment what each key stores
6. **Consider persistence**: Use localfilesystem for important data
7. **Handle missing data**: Always check if value exists
8. **Avoid large objects**: Keep stored data reasonably sized
