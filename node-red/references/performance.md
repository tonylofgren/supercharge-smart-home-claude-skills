# Performance Optimization

Optimizing Node-RED flows for speed and efficiency.

---

## Message Flow Optimization

### Minimize Nodes

```
// Inefficient: Many nodes for simple logic
[Trigger] → [Change] → [Function] → [Change] → [Service]

// Better: Combine in single function
[Trigger] → [Function] → [Service]
```

### Use Native Nodes

Native nodes are faster than function nodes:

| Instead of Function | Use Native Node |
|---------------------|-----------------|
| `msg.payload = x` | Change node |
| `if (x) return msg` | Switch node |
| `setTimeout()` | Delay node |
| Multiple outputs | Switch node |

### Parallel vs Sequential

```
// Parallel: Independent operations
[Trigger] → [Service A]
         → [Service B]
         → [Service C]

// Sequential: Only when necessary
[Trigger] → [Service A] → [Service B] → [Service C]
```

---

## Reducing Load

### Debouncing

Prevent rapid-fire messages:

```javascript
const DEBOUNCE_MS = 500;
const timeout = context.get("timeout");

if (timeout) clearTimeout(timeout);

context.set("timeout", setTimeout(() => {
    context.set("timeout", null);
    node.send(msg);
}, DEBOUNCE_MS));

return null;
```

### Throttling

Limit message frequency:

```javascript
const MIN_INTERVAL = 1000;  // 1 second
const lastSent = context.get("lastSent") || 0;

if (Date.now() - lastSent < MIN_INTERVAL) {
    return null;  // Drop message
}

context.set("lastSent", Date.now());
return msg;
```

### Rate Limiting with Queue

```javascript
const MAX_PER_MINUTE = 10;
const timestamps = context.get("timestamps") || [];

// Remove old timestamps
const oneMinuteAgo = Date.now() - 60000;
const recent = timestamps.filter(t => t > oneMinuteAgo);

if (recent.length >= MAX_PER_MINUTE) {
    node.warn("Rate limit exceeded");
    return null;
}

recent.push(Date.now());
context.set("timestamps", recent);
return msg;
```

---

## Caching

### Cache HA States

```javascript
// Cache states to avoid repeated global lookups
const CACHE_TTL = 5000;  // 5 seconds
let cache = context.get("stateCache");

if (!cache || Date.now() - cache.time > CACHE_TTL) {
    cache = {
        states: global.get("homeassistant").homeAssistant.states,
        time: Date.now()
    };
    context.set("stateCache", cache);
}

const lightState = cache.states["light.room"]?.state;
```

### Cache Expensive Calculations

```javascript
// Cache computed values
const cacheKey = JSON.stringify(msg.payload);
let cache = context.get("calcCache") || {};

if (cache[cacheKey] && Date.now() - cache[cacheKey].time < 60000) {
    msg.result = cache[cacheKey].value;
    return msg;
}

// Expensive calculation
const result = expensiveCalculation(msg.payload);

cache[cacheKey] = { value: result, time: Date.now() };
context.set("calcCache", cache);

msg.result = result;
return msg;
```

---

## Polling Optimization

### Reduce Poll Frequency

| Data Type | Recommended Interval |
|-----------|---------------------|
| Temperature | 60-300 seconds |
| Motion state | Event-based, not polling |
| Energy readings | 10-60 seconds |
| Weather | 600-1800 seconds |

### Use Events Instead of Polling

```
// Bad: Poll State every 5 seconds
[Inject 5s] → [Get State] → [Compare] → [Action]

// Good: Event-driven
[Trigger: state] → [Action]
```

### Batch API Calls

```javascript
// Bad: Multiple individual calls
for (const entity of entities) {
    callService(entity);
}

// Good: Single call with array
msg.payload = {
    action: "light.turn_off",
    target: { entity_id: entities }
};
```

---

## Memory Management

### Clear Unused Context

```javascript
// Clean up old data periodically
const data = context.get("history") || [];
const oneHourAgo = Date.now() - 3600000;

const cleaned = data.filter(item => item.time > oneHourAgo);
context.set("history", cleaned);
```

### Limit Array Sizes

```javascript
const MAX_HISTORY = 100;
const history = context.get("history") || [];

history.push(newItem);
while (history.length > MAX_HISTORY) {
    history.shift();
}

context.set("history", history);
```

### Clear Timeouts

```javascript
// In On Stop tab
const timeout = context.get("timeout");
if (timeout) clearTimeout(timeout);

const interval = context.get("interval");
if (interval) clearInterval(interval);
```

---

## Flow Organization for Performance

### Split Heavy Flows

```
// Instead of one massive flow:
Flow: All Automations (100+ nodes)

// Split into focused flows:
Flow: Lighting Automations
Flow: Climate Control
Flow: Security
Flow: Notifications
```

### Disable Unused Flows

- Right-click flow tab → Disable
- Disabled flows don't process messages

### Use Link Nodes Wisely

```
// Link nodes add minimal overhead
// Good for organization without performance penalty

[Light Trigger] → [Link Out: lights]

[Link In: lights] → [Common Processing] → [Service]
```

---

## Trigger Optimization

### Filter Early

```javascript
// Filter immediately after trigger
// Before expensive processing

const entityId = msg.data.entity_id;

// Skip unwanted entities
if (!entityId.startsWith("light.")) {
    return null;
}

// Skip unavailable states
if (msg.payload === "unavailable") {
    return null;
}

// Continue with filtered message
return msg;
```

### Use Constraints

Configure trigger nodes with constraints:

```
Entity ID: light.living_room
State: is: on
```

Better than triggering on all state changes and filtering in function.

---

## Debug Mode Performance

### Disable Debug Nodes in Production

- Debug nodes consume resources even when sidebar closed
- Disable or remove debug nodes for production
- Use conditional debugging:

```javascript
const DEBUG = flow.get("debugMode") || false;

if (DEBUG) {
    node.warn(JSON.stringify(msg.payload));
}
```

### Status Updates

```javascript
// Limit status update frequency
const lastStatus = context.get("lastStatus") || 0;

if (Date.now() - lastStatus > 1000) {  // Max once per second
    node.status({fill: "green", shape: "dot", text: msg.payload});
    context.set("lastStatus", Date.now());
}
```

---

## Benchmarking

### Measure Execution Time

```javascript
const start = Date.now();

// ... processing ...

const duration = Date.now() - start;
if (duration > 100) {  // Log if > 100ms
    node.warn(`Processing took ${duration}ms`);
}
```

### Track Message Throughput

```javascript
// Count messages per minute
let count = context.get("msgCount") || 0;
let lastReset = context.get("lastReset") || Date.now();

count++;

if (Date.now() - lastReset > 60000) {
    node.status({text: `${count} msg/min`});
    count = 0;
    lastReset = Date.now();
}

context.set("msgCount", count);
context.set("lastReset", lastReset);
```

---

## Common Performance Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| High CPU | Too many triggers | Filter, debounce |
| Memory growth | Unbounded arrays | Limit size, cleanup |
| Slow response | Blocking operations | Use async patterns |
| Delayed actions | Long chains | Parallelize |
| Browser lag | Too many debug msgs | Disable debug nodes |

---

## Performance Checklist

- [ ] Use native nodes where possible
- [ ] Filter messages early in flow
- [ ] Debounce/throttle rapid events
- [ ] Cache expensive lookups
- [ ] Limit history/array sizes
- [ ] Clean up timeouts on stop
- [ ] Use events over polling
- [ ] Batch API calls
- [ ] Disable debug in production
- [ ] Split large flows
