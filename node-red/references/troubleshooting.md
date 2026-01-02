# Node-RED Troubleshooting

## Table of Contents
- [Connection Issues](#connection-issues)
- [Node Errors](#node-errors)
- [Message Problems](#message-problems)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)
- [Debug Techniques](#debug-techniques)
- [Recovery Procedures](#recovery-procedures)

---

## Connection Issues

### "No connection to Home Assistant"

**Symptoms:**
- Red "disconnected" status on nodes
- Service calls fail
- Entity autocomplete empty

**Solutions:**

1. **Check HA is running:**
   ```bash
   # HA addon
   ha core check
   ha core info

   # External
   curl http://homeassistant.local:8123/api/
   ```

2. **Verify URL configuration:**
   ```javascript
   // Addon
   { "addon": true }  // URL auto-configured

   // External - correct format
   { "host": "http://192.168.1.100", "port": "8123" }
   // NOT: https:// (unless using SSL)
   // NOT: Missing http://
   ```

3. **Regenerate access token:**
   - Profile → Long-Lived Access Tokens
   - Delete old token
   - Create new token
   - Update Node-RED server config

4. **Check network:**
   ```bash
   # From Node-RED container/host
   ping homeassistant.local
   curl -H "Authorization: Bearer TOKEN" \
        http://homeassistant.local:8123/api/
   ```

### Connection Drops Frequently

**Solutions:**

1. **Enable heartbeat:**
   ```javascript
   {
     "heartbeat": true,
     "heartbeatInterval": 30
   }
   ```

2. **Increase connection delay:**
   ```javascript
   {
     "connectionDelay": true
   }
   ```

3. **Check HA logs:**
   ```
   Settings → System → Logs
   Filter by: websocket
   ```

### "Authentication Failed"

**Causes:**
- Expired token
- Token from non-admin account
- Whitespace in token field
- Wrong token copied

**Fix:**
1. Create NEW token from administrator account
2. Copy ENTIRE token (no extra spaces)
3. Paste directly, don't edit

---

## Node Errors

### "Entity could not be found in cache"

**Solutions:**

1. **Clear autocomplete cache:**
   - Server config → Uncheck "Cache Autocomplete Results"
   - Deploy
   - Recheck and deploy again

2. **Wait for HA to fully load:**
   ```javascript
   // Add delay after HA restart
   { "connectionDelay": true }
   ```

3. **Check entity ID spelling:**
   - Use Developer Tools → States
   - Copy exact entity_id

### "Service not found"

**Causes:**
- Typo in service name
- Integration not loaded
- Service renamed in HA update

**Solutions:**
```javascript
// Correct format
"action": "light.turn_on"     // ✓
"action": "lights.turn_on"    // ✗ (wrong domain)
"action": "light.turnOn"      // ✗ (wrong format)

// Check available services
// Developer Tools → Services
```

### Node Shows Red Status

**Check:**
1. Node configuration complete?
2. Required config nodes exist?
3. Server connection active?

**Fix:**
1. Double-click node
2. Review all required fields
3. Check for missing config nodes

---

## Message Problems

### "Cannot read property 'x' of undefined"

**Cause:** Accessing property that doesn't exist

**Fix:**
```javascript
// BAD
const value = msg.payload.data.value;

// GOOD - safe access
const value = msg.payload?.data?.value;

// GOOD - with default
const value = msg.payload?.data?.value ?? "default";
```

### Message Not Arriving

**Debug steps:**

1. **Add debug nodes:**
   ```
   Trigger → [Debug] → Next Node → [Debug] → Action
   ```

2. **Check wire connections:**
   - Click on wire to verify connection
   - Remove and reconnect wire

3. **Check conditional logic:**
   - Switch nodes dropping messages?
   - Function returning null?

### Wrong Message Content

**Use debug node to inspect:**
```javascript
// Debug node settings
{
  "complete": "true",  // Show FULL message
  "tosidebar": true
}
```

**Common issues:**
```javascript
// Payload overwritten
msg.payload = "new";  // Replaces existing

// Whole message replaced
msg = { payload: "x" };  // Loses _msgid!

// Correct approach
msg.newField = "value";  // Adds field
return msg;              // Keeps everything
```

---

## Performance Issues

### Slow Response

**Causes & Solutions:**

1. **Too many nodes:**
   - Consolidate function nodes
   - Use subflows
   - Remove unused nodes

2. **Heavy processing in function:**
   ```javascript
   // BAD - blocking loop
   for (let i = 0; i < 1000000; i++) { }

   // GOOD - async processing
   setImmediate(() => {
     // Heavy work
     node.send(msg);
   });
   return null;
   ```

3. **Frequent polling:**
   ```javascript
   // BAD - poll every second
   { "updateInterval": 1 }

   // GOOD - use state triggers instead
   // Or poll less frequently
   { "updateInterval": 60 }
   ```

### High Memory Usage

**Solutions:**

1. **Clean context regularly:**
   ```javascript
   // Limit stored data
   const MAX_ENTRIES = 100;
   const history = flow.get("history") || [];
   while (history.length > MAX_ENTRIES) {
     history.shift();
   }
   ```

2. **Clear debug messages:**
   - Click trash icon in debug sidebar
   - Disable debug nodes in production

3. **Reduce message size:**
   ```javascript
   // Remove large data before passing
   delete msg.rawData;
   delete msg.debug;
   return msg;
   ```

### CPU Spikes

**Check for:**
- Infinite loops
- Rapid message generation
- Complex regex patterns

**Fix:**
```javascript
// Add rate limiting
const lastRun = context.get("lastRun") || 0;
if (Date.now() - lastRun < 1000) {
  return null;  // Skip if < 1 second
}
context.set("lastRun", Date.now());
```

---

## Common Error Messages

### Error Reference Table

| Error | Cause | Solution |
|-------|-------|----------|
| `ECONNREFUSED` | HA not running/accessible | Check HA status, network |
| `ETIMEDOUT` | Network timeout | Check firewall, routing |
| `401 Unauthorized` | Bad token | Regenerate token |
| `404 Not Found` | Wrong URL/service | Verify configuration |
| `Heap out of memory` | Memory leak | Restart, fix leaks |
| `Maximum call stack` | Infinite recursion | Fix loop in code |

### Reading Error Messages

```javascript
// Error object structure
{
  "message": "Something went wrong",
  "source": {
    "id": "node_id",
    "type": "function",
    "name": "My Function"
  }
}

// In Catch node
msg.error.message   // Error text
msg.error.source.id // Node that failed
```

---

## Debug Techniques

### Strategic Debug Nodes

```
            ┌───[Debug A]
Trigger ────┤
            └───▶ Process ────┬───[Debug B]
                              │
                              └───▶ Action ────[Debug C]
```

### Debug Output Types

```javascript
// Show payload only
{ "complete": "payload" }

// Show full message
{ "complete": "true" }

// Show specific property
{ "complete": "data.entity_id" }

// Show in node status
{ "tostatus": true, "tosidebar": false }
```

### Console Logging

```javascript
// In function nodes
node.log("Info message");      // Info level
node.warn("Warning message");  // Warning level
node.error("Error message");   // Error level

// With data
node.warn(`Processing: ${JSON.stringify(msg.payload)}`);
```

### Flow Injection Testing

```javascript
// Use inject node with test data
{
  "payload": {
    "entity_id": "light.test",
    "state": "on"
  }
}
```

### Checking Context

```javascript
// Debug context values
msg.context = {
  node: context.keys().map(k => ({ [k]: context.get(k) })),
  flow: flow.keys().map(k => ({ [k]: flow.get(k) })),
  global: global.keys().slice(0, 10)  // First 10
};
return msg;
```

---

## Recovery Procedures

### Reset Node-RED

**Addon:**
```
Settings → Add-ons → Node-RED → Restart
```

**Docker:**
```bash
docker restart node-red
```

**Service:**
```bash
sudo systemctl restart nodered
```

### Clear Context

```javascript
// In function node - clear all
const keys = flow.keys();
keys.forEach(key => flow.set(key, undefined));
node.warn("Flow context cleared");
```

### Restore from Backup

1. Export flows before changes
2. If broken, Menu → Import → Paste backup
3. Deploy

### Safe Mode

If flows won't load:

1. Stop Node-RED
2. Backup `flows.json`
3. Create empty `flows.json`: `[]`
4. Start Node-RED
5. Import flows carefully

### Factory Reset

**Addon:**
```
Settings → Add-ons → Node-RED → Reset to defaults
```

**Manual:**
```bash
cd ~/.node-red
rm flows.json flows_cred.json
# Restart Node-RED
```

---

## Troubleshooting Checklist

### Before Asking for Help

- [ ] Check Node-RED logs
- [ ] Check Home Assistant logs
- [ ] Add debug nodes
- [ ] Verify server connection (green status)
- [ ] Test with minimal flow
- [ ] Search community forums
- [ ] Check recent changes

### Information to Gather

```
1. Node-RED version
2. HA version
3. node-red-contrib-home-assistant-websocket version
4. Error message (exact text)
5. Flow export (sanitized)
6. Debug node output
7. Steps to reproduce
```

---

## Related References

- [Troubleshooting Flowcharts](troubleshooting-flowcharts.md) - Visual guides
- [HA Setup](ha-setup.md) - Connection configuration
- [Error Handling](error-handling.md) - Building resilient flows
- [Node Reference](node-reference.md) - All HA nodes
