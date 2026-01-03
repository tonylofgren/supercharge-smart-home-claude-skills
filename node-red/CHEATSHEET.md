# Node-RED Cheatsheet

Quick reference for common patterns.

## Node Type Names

| UI Name | JSON Type |
|---------|-----------|
| Trigger: state | `trigger-state` |
| Events: state | `server-state-changed` |
| Current State | `api-current-state` |
| Call Service | `api-call-service` |
| Get Entities | `ha-get-entities` |

## Entity ID Filtering

```javascript
// ✓ Valid types
"entityIdType": "exact"      // single entity
"entityIdType": "substring"  // contains text
"entityIdType": "regex"      // pattern match

// ✗ Invalid
"entityIdType": "list"       // DOES NOT EXIST!
```

**Multiple entities with regex:**
```javascript
"entityId": "binary_sensor\\.motion_(living|bed)room",
"entityIdType": "regex"
```

## Service Calls

**Static (in node config):**
```json
{
  "type": "api-call-service",
  "domain": "light",
  "service": "turn_on",
  "entityId": ["light.room"],
  "data": "{\"brightness_pct\": 80}",
  "dataType": "json"
}
```

**Dynamic (via msg):**
```json
{
  "type": "api-call-service",
  "dataType": "msg"
}
```
```javascript
// Function node before
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.room"] },
  data: { brightness_pct: 80 }
};
return msg;
```

## Context Storage

```javascript
// Node context (this node only)
context.get('key');
context.set('key', value);

// Flow context (same tab)
flow.get('key');
flow.set('key', value);

// Global context (all flows)
global.get('key');
global.set('key', value);

// Home Assistant states
const states = global.get("homeassistant").homeAssistant.states;
const temp = states["sensor.temperature"].state;
```

## Function Node Outputs

```javascript
// Single output
return msg;
return null;  // stop message

// Multiple outputs (configured in node)
return [msg, null];     // output 1 only
return [null, msg];     // output 2 only
return [msg, msg];      // both outputs

// Multiple messages to one output
return [[msg1, msg2, msg3]];
```

## Async Function Pattern

```javascript
async function run() {
  try {
    const result = await someAsyncOp();
    msg.payload = result;
    node.send(msg);
  } catch (e) {
    node.error(e.message, msg);
  }
  node.done();
}
run();
return null;  // IMPORTANT!
```

## Timer with Auto-Reset

```json
{
  "type": "trigger",
  "op1type": "nul",
  "op2": "timeout",
  "op2type": "str",
  "duration": "5",
  "extend": true,
  "units": "min"
}
```

`extend: true` = reset timer on each input

## Debounce Pattern

```javascript
const lastTime = context.get('lastTime') || 0;
const now = Date.now();
if (now - lastTime < 1000) return null; // 1s debounce
context.set('lastTime', now);
return msg;
```

## Rate Limiting

```javascript
const history = context.get('history') || [];
const now = Date.now();
const windowMs = 60000; // 1 minute
const filtered = history.filter(t => now - t < windowMs);
if (filtered.length >= 10) return null; // max 10/min
filtered.push(now);
context.set('history', filtered);
return msg;
```

## Error Handling

```javascript
// In function node
try {
  // risky code
} catch (e) {
  node.error(e.message, msg);
  return null;
}

// Catch node: msg.error.message, msg.error.source.id
```

## Status Display

```javascript
node.status({fill:"green", shape:"dot", text:"active"});
node.status({fill:"red", shape:"ring", text:"error"});
node.status({});  // clear
```

## Environment Variables (Subflows)

```javascript
const timeout = env.get('TIMEOUT') || 5000;
const entityId = env.get('ENTITY_ID');
```

## Get All Entities of Type

```javascript
const states = global.get("homeassistant").homeAssistant.states;

const lightsOn = Object.keys(states)
  .filter(id => id.startsWith("light."))
  .filter(id => states[id].state === "on");

const temps = Object.entries(states)
  .filter(([id]) => id.startsWith("sensor.") &&
          states[id].attributes.device_class === "temperature")
  .map(([id, s]) => ({id, temp: parseFloat(s.state)}));
```

## Check Time of Day

```javascript
const hour = new Date().getHours();
const isNight = hour >= 22 || hour < 6;
const isMorning = hour >= 6 && hour < 9;
const isDay = hour >= 9 && hour < 18;
const isEvening = hour >= 18 && hour < 22;
```

## Check Workday

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const isWorkday = states["binary_sensor.workday"]?.state === "on";
```

## Presence Check

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const anyoneHome = Object.keys(states)
  .filter(id => id.startsWith("person."))
  .some(id => states[id].state === "home");
```

## Flow Best Practices

1. **Name all nodes**
2. **Use comment nodes**
3. **Group related nodes**
4. **Handle errors with catch nodes**
5. **Test with debug nodes**
6. **Don't store unlimited history**
7. **Use extend:true for timers**
8. **Leave server field empty in exported flows**
