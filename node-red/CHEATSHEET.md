# Node-RED Cheatsheet

Quick reference for common Node-RED patterns with Home Assistant.

---

## Message Structure

```javascript
msg = {
  _msgid: "unique-id",
  payload: "primary data",
  topic: "category",
  data: { /* extra info */ }
};
```

## Home Assistant State Message

```javascript
msg = {
  payload: "on",                    // State value
  topic: "entity_id",
  data: {
    entity_id: "light.room",
    new_state: { state, attributes },
    old_state: { state, attributes }
  }
};
```

---

## Common Patterns

### Check State Before Action

```javascript
// Get sun state
msg.isNight = msg.sunState === "below_horizon";
if (msg.isNight) {
  // Only at night
}
```

### Safe Property Access

```javascript
const value = msg.payload?.data?.value ?? "default";
```

### Multiple Outputs

```javascript
// Output 1: condition true, Output 2: condition false
if (msg.payload > 10) {
  return [msg, null];
}
return [null, msg];
```

### Drop Message

```javascript
return null;  // Stop flow
```

---

## Context Storage

### Node Context (this node only)

```javascript
context.set("key", value);
const val = context.get("key");
```

### Flow Context (same tab)

```javascript
flow.set("key", value);
const val = flow.get("key");
```

### Global Context (everywhere)

```javascript
global.set("key", value);
const val = global.get("key");
```

### Persistent Storage

```javascript
flow.set("key", value, "file");
```

---

## Service Calls

### Light On

```javascript
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.room"] },
  data: { brightness_pct: 100 }
};
```

### Notification

```javascript
msg.payload = {
  action: "notify.mobile_app",
  data: {
    message: "Alert!",
    title: "Home"
  }
};
```

### Climate

```javascript
msg.payload = {
  action: "climate.set_temperature",
  target: { entity_id: ["climate.hvac"] },
  data: { temperature: 22 }
};
```

---

## Function Node Templates

### Rate Limiter

```javascript
const MIN_INTERVAL = 5000;
const lastRun = context.get("lastRun") || 0;
if (Date.now() - lastRun < MIN_INTERVAL) return null;
context.set("lastRun", Date.now());
return msg;
```

### Debounce

```javascript
const timeout = context.get("timeout");
if (timeout) clearTimeout(timeout);
context.set("timeout", setTimeout(() => {
  context.set("timeout", null);
  node.send(msg);
}, 500));
return null;
```

### Counter

```javascript
const count = (context.get("count") || 0) + 1;
context.set("count", count);
msg.count = count;
return msg;
```

### Rolling Average

```javascript
const MAX = 10;
const history = context.get("history") || [];
history.push(msg.payload);
while (history.length > MAX) history.shift();
context.set("history", history);
msg.average = history.reduce((a,b) => a+b, 0) / history.length;
return msg;
```

---

## Switch Node Comparators

| Comparator | Usage |
|------------|-------|
| `is` | Equals |
| `is not` | Not equals |
| `<` / `<=` | Less than |
| `>` / `>=` | Greater than |
| `between` | In range |
| `contains` | String contains |
| `matches regex` | Pattern match |
| `is true` | Boolean true |
| `is null` | Null check |
| `otherwise` | Default case |

---

## Time-Based Logic

### Current Hour

```javascript
const hour = new Date().getHours();
const isDay = hour >= 6 && hour < 22;
```

### Day of Week

```javascript
const day = new Date().getDay();
const isWeekend = day === 0 || day === 6;
```

### Minutes Since

```javascript
const lastEvent = flow.get("lastEvent") || 0;
const minutes = (Date.now() - lastEvent) / 60000;
```

---

## Debug Tips

```javascript
// Log to sidebar
node.warn(msg.payload);

// Log object
node.warn(JSON.stringify(msg.payload, null, 2));

// Node status
node.status({fill:"green", shape:"dot", text:"OK"});
```

---

## Home Assistant Helpers

### Get Entity State

```javascript
const state = global.get("homeassistant")
  .homeAssistant.states["sensor.temp"]?.state;
```

### Check If Home

```javascript
const isHome = global.get("homeassistant")
  .homeAssistant.states["person.john"]?.state === "home";
```

### Get Attribute

```javascript
const brightness = global.get("homeassistant")
  .homeAssistant.states["light.room"]?.attributes.brightness;
```

---

## Mustache Templates (in nodes)

```
{{payload}}              - Message payload
{{payload.entity_id}}    - Nested property
{{flow.myVar}}           - Flow context
{{global.setting}}       - Global context
{{env.MY_VAR}}           - Environment variable
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+D` | Deploy |
| `Ctrl+E` | Export |
| `Ctrl+I` | Import |
| `Ctrl+Space` | Search |
| `Delete` | Delete selected |
| `Ctrl+Z` | Undo |

---

## Quick Troubleshooting

| Issue | Check |
|-------|-------|
| No connection | Server config, token |
| Entity not found | Spelling, cache |
| Service fails | Service name format |
| Message lost | Debug nodes, switch logic |
| Slow | Polling interval, loops |

---

## Related Files

- [SKILL.md](SKILL.md) - Full skill reference
- [references/](references/) - Detailed documentation
- [templates/](templates/) - Ready-to-use flows
