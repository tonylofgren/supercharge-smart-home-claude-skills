# Node-RED Troubleshooting Guide

Common issues and solutions.

## Connection Issues

### Node shows "disconnected" or "connecting..."

**Symptoms:**
- HA nodes show red status
- "connecting..." message that never completes
- Flows not triggering

**Diagnosis:**
1. Check Node-RED debug sidebar for errors
2. Verify HA is accessible: `curl http://your-ha:8123`
3. Check access token validity in HA → Profile → Tokens

**Solutions:**

| Cause | Fix |
|-------|-----|
| Wrong Base URL | Addon: `http://supervisor/core`, External: `http://ip:8123` |
| Invalid token | Generate new Long-Lived Access Token |
| Network issue | Check firewall, DNS, routing |
| HA restarting | Wait for HA to fully start |
| SSL mismatch | Match http/https to HA config |

### WebSocket errors in logs

```
WebSocket connection to 'ws://...' failed
```

**Fixes:**
- Check if HA allows WebSocket connections
- Verify no proxy is blocking WebSocket upgrade
- Try both `ws://` and `wss://` protocols

## Trigger Issues

### Events not firing

**Symptoms:**
- Flow never triggers
- Debug shows no messages

**Diagnosis:**
1. Check entity exists: Developer Tools → States
2. Verify entity is actually changing
3. Check node filter configuration

**Common Mistakes:**

| Issue | Fix |
|-------|-----|
| Wrong entity_id | Copy exact ID from Developer Tools |
| Filter too strict | Remove constraints temporarily |
| State not changing | Entity might be "unavailable" |
| `entityIdType: "list"` | Use `regex` instead (no list type!) |

### Trigger fires multiple times

**Cause:** Multiple state updates for single action

**Fix:** Add debounce logic:
```javascript
// Function node
const lastTrigger = flow.get('lastTrigger') || 0;
const now = Date.now();

if (now - lastTrigger < 1000) { // 1 second debounce
  return null;
}

flow.set('lastTrigger', now);
return msg;
```

### Trigger fires on restart

**Cause:** `outputInitially: true` setting

**Fix:** Set `outputInitially: false` or filter initial message:
```javascript
// Function node
if (msg.data?.old_state === undefined) {
  return null; // Skip initial state
}
return msg;
```

## Service Call Issues

### Service call does nothing

**Symptoms:**
- No error, but action doesn't happen
- Node shows "done" status

**Diagnosis:**
1. Check Developer Tools → Services
2. Try calling service manually
3. Check service parameters

**Common Mistakes:**

| Issue | Fix |
|-------|-----|
| Wrong domain/service | Check docs for current service names |
| entity_id not in array | Use `["light.room"]` not `"light.room"` |
| Wrong data format | Verify JSON structure |
| dataType mismatch | `json` for static, `msg` for dynamic |

### "Service not found" error

**Causes:**
- Integration not loaded
- Typo in service name
- Service renamed in HA update

**Fix:** Check available services in Developer Tools → Services

### Dynamic service calls not working

**Problem:**
```json
{
  "dataType": "json",
  "data": "{{ msg.payload }}"
}
```

**Fix:** Use `dataType: "msg"` for dynamic payloads:
```json
{
  "dataType": "msg",
  "data": ""
}
```

With function node setting `msg.payload`:
```javascript
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.room"] },
  data: { brightness_pct: 80 }
};
return msg;
```

## Entity Node Issues

### Entity nodes show "Error"

**Cause:** Missing node-red integration in HA

**Fix:**
1. Install HACS
2. Install "Node-RED Companion" integration
3. Add integration in HA Settings
4. Restart both HA and Node-RED

### Entity not appearing in HA

**Causes:**
- Entity config not properly set
- Node not deployed after creation
- Integration not connected

**Fix:**
1. Check Entity Config node is properly configured
2. Verify unique_id is set
3. Deploy and check HA Developer Tools → States

## Function Node Issues

### "ReferenceError: X is not defined"

**Common missing objects:**

| Error | Solution |
|-------|----------|
| `global is not defined` | Use `global.get()` not just `global` |
| `require is not defined` | Configure in settings.js functionGlobalContext |
| `env is not defined` | Only available in subflows |

### Async code not working

**Wrong:**
```javascript
const data = await fetchData(); // This fails
msg.payload = data;
return msg;
```

**Correct:**
```javascript
async function run() {
  const data = await fetchData();
  msg.payload = data;
  node.send(msg);
  node.done();
}
run();
return null;
```

### External library not available

**Fix:** Add to settings.js:
```javascript
functionGlobalContext: {
  moment: require('moment'),
  lodash: require('lodash')
}
```

Then restart Node-RED and access via:
```javascript
const moment = global.get('moment');
```

## Context Issues

### Context not persisting

**Cause:** Using memory storage (default)

**Fix:** Configure file-based storage in settings.js:
```javascript
contextStorage: {
  default: { module: "localfilesystem" }
}
```

### Context lost on restart

**Cause:** Memory storage doesn't persist

**Fix:** Same as above - use localfilesystem

### Context not sharing between tabs

| Scope | Use |
|-------|-----|
| `context.get/set()` | Node only |
| `flow.get/set()` | Tab only |
| `global.get/set()` | All flows |

## Performance Issues

### Flows running slowly

**Causes:**
- Too many nodes
- Expensive function node operations
- Polling too frequently

**Fixes:**
1. Reduce polling frequency
2. Optimize function node code
3. Use rate limiting
4. Split complex flows

### High CPU usage

**Diagnosis:**
1. Check for infinite loops
2. Look for rapid-fire triggers
3. Monitor debug output volume

**Fix:** Add rate limiting:
```json
{
  "type": "delay",
  "pauseType": "rate",
  "rate": "1",
  "rateUnits": "second"
}
```

### Memory leaks

**Cause:** Accumulating data in context

**Fix:** Limit stored data:
```javascript
let history = flow.get('history') || [];
history.push(newItem);
if (history.length > 100) {
  history = history.slice(-100);
}
flow.set('history', history);
```

## Debugging Tips

### Enable debug output

1. Add debug node after problem node
2. Set to "complete msg object"
3. Check sidebar for output

### Check HA connection status

In Node-RED, check:
- Server node status in sidebar
- Deploy to reconnect if needed

### View HA WebSocket messages

In HA, enable debug logging:
```yaml
logger:
  default: info
  logs:
    homeassistant.components.websocket_api: debug
```

### Trace message flow

Use debug nodes at each step:
```
[trigger] → [debug1] → [function] → [debug2] → [action]
```

### Export flow for sharing

When asking for help:
1. Select problematic nodes
2. Menu → Export → Clipboard
3. Share JSON (remove credentials!)

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "Entity not found" | Entity ID typo | Check Developer Tools |
| "Call service error" | Bad service params | Verify in Developer Tools |
| "WebSocket closed" | Connection lost | Check network/HA status |
| "Unauthorized" | Token invalid | Generate new token |
| "Template error" | Invalid Jinja2 | Test in Developer Tools |
| "State unavailable" | Entity offline | Check device connectivity |
