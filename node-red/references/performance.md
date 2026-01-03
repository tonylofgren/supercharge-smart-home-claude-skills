# Performance Optimization in Node-RED

Best practices for efficient flows.

## Common Performance Issues

### 1. Excessive Polling

**Problem:** Polling entities too frequently.

```json
{
  "type": "poll-state",
  "updateInterval": 1,
  "updateIntervalUnits": "seconds"
}
```

**Solution:** Use event-based triggers when possible:

```
// Instead of polling every second
[poll-state every 1s] ──> [process]

// Use state change trigger
[trigger-state] ──> [process]
```

When polling is necessary, use appropriate intervals:
- Fast changes (power): 10-30 seconds
- Slow changes (temperature): 1-5 minutes
- Rarely changes: 5-15 minutes

### 2. Heavy Function Nodes

**Problem:** Complex calculations in function nodes.

**Solutions:**

1. **Cache expensive operations:**
```javascript
// Check if cached result is still valid
const cached = flow.get('expensiveResult');
const cacheTime = flow.get('cacheTime') || 0;

if (cached && Date.now() - cacheTime < 60000) {
  msg.payload = cached;
  return msg;
}

// Calculate only when needed
const result = expensiveCalculation();
flow.set('expensiveResult', result);
flow.set('cacheTime', Date.now());
msg.payload = result;
return msg;
```

2. **Limit iterations:**
```javascript
// BAD: Process everything
Object.keys(states).forEach(...)

// GOOD: Filter first, then process
Object.keys(states)
  .filter(id => id.startsWith("sensor."))
  .slice(0, 100)  // Limit if large
  .forEach(...)
```

### 3. Unbounded Context Growth

**Problem:** Arrays that grow without limit.

```javascript
// BAD: Never shrinks
history.push(newValue);
flow.set('history', history);
```

**Solution:** Always cap collection sizes:

```javascript
// GOOD: Capped size
history.push(newValue);
if (history.length > 100) {
  history = history.slice(-100);
}
flow.set('history', history);
```

### 4. Rapid-Fire Triggers

**Problem:** Many messages in short time.

**Solutions:**

1. **Debounce:**
```javascript
const lastTime = context.get('lastTime') || 0;
const now = Date.now();
if (now - lastTime < 1000) return null;
context.set('lastTime', now);
return msg;
```

2. **Rate limit node:**
```json
{
  "type": "delay",
  "pauseType": "rate",
  "rate": "1",
  "rateUnits": "second"
}
```

3. **Throttle in trigger node:**
Use `outputs: 2` and filter frequent events.

## Memory Optimization

### Monitor Memory Usage

```javascript
// In function node
const used = process.memoryUsage();
node.warn(`Memory: ${Math.round(used.heapUsed / 1024 / 1024)}MB`);
```

### Clean Up Patterns

**Periodic cleanup:**
```
[inject every hour] ──> [cleanup function] ──> [debug]
```

```javascript
// Cleanup function
const data = flow.get('data') || {};
const cutoff = Date.now() - (24 * 60 * 60 * 1000); // 24 hours

let cleaned = 0;
Object.keys(data).forEach(key => {
  if (data[key].timestamp < cutoff) {
    delete data[key];
    cleaned++;
  }
});

flow.set('data', data);
msg.payload = `Cleaned ${cleaned} entries`;
return msg;
```

### Efficient Data Structures

**Instead of array for lookups:**
```javascript
// BAD: O(n) lookup
const found = array.find(item => item.id === searchId);

// GOOD: O(1) lookup
const map = { [item.id]: item, ... };
const found = map[searchId];
```

## Flow Organization

### Split Large Flows

Instead of one giant flow:
```
[many nodes on one tab]
```

Use multiple tabs with link nodes:
```
Tab 1: Triggers ──> [link out]

Tab 2: [link in] ──> Processing ──> [link out]

Tab 3: [link in] ──> Actions
```

### Use Subflows

Extract repeated patterns:

```
// Instead of copying 10 nodes everywhere
[repeated nodes] [repeated nodes] [repeated nodes]

// Create subflow and reuse
[subflow] [subflow] [subflow]
```

### Disable Unused Flows

Right-click on tab → Disable

Disabled flows don't consume resources.

## Debug Node Impact

### Disable When Not Needed

Debug nodes consume resources even when sidebar is closed.

```json
{
  "type": "debug",
  "active": false  // Disable when not debugging
}
```

### Limit Output

```json
{
  "type": "debug",
  "complete": "payload",  // Not complete msg object
  "targetType": "msg"
}
```

### Use Status Instead

For monitoring without debug overhead:

```javascript
node.status({
  fill: "green",
  shape: "dot",
  text: `Last: ${new Date().toLocaleTimeString()}`
});
```

## Async Best Practices

### Avoid Blocking

```javascript
// BAD: Blocking loop
for (let i = 0; i < 1000000; i++) {
  // Heavy computation
}

// GOOD: Break into chunks
async function processChunks() {
  for (let i = 0; i < items.length; i += 100) {
    const chunk = items.slice(i, i + 100);
    await processChunk(chunk);
    // Allow other events to process
    await new Promise(resolve => setImmediate(resolve));
  }
}
```

### Use Built-in Nodes

HTTP requests, delays, and file operations should use built-in nodes rather than function node implementations.

```
// GOOD: Use http request node
[http request] ──> [process]

// BAD: axios in function node
[function with axios]
```

## Monitoring Performance

### Flow Timing

Add timing to critical paths:

```javascript
// Start timer
msg._startTime = Date.now();
return msg;
```

```javascript
// End timer
const elapsed = Date.now() - msg._startTime;
if (elapsed > 100) {
  node.warn(`Slow execution: ${elapsed}ms`);
}
return msg;
```

### Node-RED Performance Dashboard

Install `node-red-contrib-actionflows` or similar for flow monitoring.

### External Monitoring

Use InfluxDB + Grafana to track:
- Message throughput
- Response times
- Error rates
- Memory usage

## Hardware Considerations

### Raspberry Pi Optimization

1. Use `localfilesystem` context storage sparingly (SD wear)
2. Reduce logging verbosity
3. Disable unused Node-RED nodes
4. Consider external MQTT broker

### Docker Optimization

1. Allocate sufficient memory
2. Use volume mounts for persistent data
3. Configure Node.js memory limits:
   ```
   NODE_OPTIONS="--max-old-space-size=512"
   ```

## Checklist

Before deploying:

- [ ] Removed or disabled debug nodes
- [ ] Appropriate polling intervals
- [ ] Context data capped
- [ ] No infinite loops possible
- [ ] Rate limiting on triggers
- [ ] Large flows split into tabs
- [ ] Repeated patterns in subflows
- [ ] Expensive operations cached
