# Node-RED Home Assistant Node Reference

Quick reference for all 31 nodes in node-red-contrib-home-assistant-websocket.

---

## Config Nodes

### Server Config
Connection settings for Home Assistant.

| Setting | Description |
|---------|-------------|
| `addon` | Enable for HA addon install |
| `host` | HA URL (external only) |
| `accessToken` | Long-lived access token |

### Entity Config
Shared entity settings for entity nodes.

| Setting | Description |
|---------|-------------|
| `name` | Entity name in HA |
| `deviceConfig` | Parent device grouping |
| `unique_id` | Unique identifier |

### Device Config
Device grouping for entity nodes.

| Setting | Description |
|---------|-------------|
| `name` | Device name |
| `manufacturer` | Device manufacturer |
| `model` | Device model |

---

## Trigger Nodes

### Trigger: state
Advanced state change trigger with conditions.

```javascript
// Output
msg = {
  payload: "on",                    // State value
  topic: "entity_id",
  data: { new_state, old_state }
};
```

| Setting | Description |
|---------|-------------|
| `entityId` | Entity to monitor |
| `entityIdType` | exact/substring/regex |
| `conditions` | Filter conditions |
| `outputs` | Custom conditional outputs |

### Events: state
Simple state change listener.

```javascript
// Output
msg = {
  payload: "on",
  data: { entity_id, new_state, old_state }
};
```

### Events: all
Listen to any HA event.

```javascript
// Output
msg = {
  payload: { event_type, data, origin, time_fired }
};
```

| Setting | Description |
|---------|-------------|
| `eventType` | Filter by type (empty = all) |

### Events: calendar
Trigger on calendar events.

```javascript
// Output
msg = {
  payload: { summary, start, end, location }
};
```

### Device
Device-specific triggers (buttons, remotes).

```javascript
// Output
msg = {
  payload: { device_id, type, subtype }
};
```

### Time
Schedule-based triggers.

| Setting | Description |
|---------|-------------|
| `entityId` | input_datetime or sun.sun |
| `offset` | Minutes before/after |
| `repeatDaily` | Repeat every day |

### Zone
Location-based triggers.

```javascript
// Output
msg = {
  payload: { entity_id, zone, event }  // event: enter/leave
};
```

### Webhook
HTTP webhook receiver.

```javascript
// Output
msg = {
  payload: { /* request body */ },
  headers: { /* HTTP headers */ }
};
```

### Tag
NFC tag scanner trigger.

```javascript
// Output
msg = {
  payload: { tag_id, device_id, user_id }
};
```

### Sentence
Voice command trigger.

```javascript
// Output
msg = {
  payload: { /* slot values */ },
  sentence: "original sentence"
};
```

---

## Action Nodes

### Action (Call Service)
Execute HA services.

```javascript
// Input
msg = {
  payload: {
    action: "light.turn_on",
    target: { entity_id: ["light.room"] },
    data: { brightness: 255 }
  }
};
```

| Setting | Description |
|---------|-------------|
| `action` | Service to call |
| `target` | Entity/area/device IDs |
| `data` | Service data |
| `queue` | Offline handling |

### Fire Event
Trigger custom events.

```javascript
// Configuration
{
  "event": "custom_event",
  "data": { "source": "node_red" }
}
```

### API
Direct WebSocket/HTTP API access.

| Setting | Description |
|---------|-------------|
| `protocol` | websocket/http |
| `method` | get/post |
| `path` | API endpoint |

---

## State Nodes

### Current State
Get single entity state.

```javascript
// Output
msg = {
  payload: "22.5",               // State value
  data: { entity_id, state, attributes }
};
```

| Setting | Description |
|---------|-------------|
| `entityId` | Entity to query |
| `ifState` | Conditional routing |
| `halt_if` | Stop if condition met |

### Get Entities
Query multiple entities.

```javascript
// Output (array mode)
msg = {
  payload: [
    { entity_id, state, attributes },
    // ...
  ]
};
```

| Setting | Description |
|---------|-------------|
| `rules` | Filter criteria |
| `outputType` | array/count/split/random |

### Get History
Historical state data.

```javascript
// Output
msg = {
  payload: [
    { entity_id, state, last_changed },
    // ...
  ]
};
```

| Setting | Description |
|---------|-------------|
| `entityId` | Entity to query |
| `relativeTime` | Hours/days back |
| `flatten` | Flatten results |

### Poll State
Periodic state polling.

| Setting | Description |
|---------|-------------|
| `entityId` | Entity to poll |
| `updateInterval` | Seconds between polls |
| `outputOnChanged` | Only output on change |

### Wait Until
Pause until condition.

| Setting | Description |
|---------|-------------|
| `entityId` | Entity to monitor |
| `comparator` | Condition to meet |
| `timeout` | Max wait time |

### Render Template
Evaluate Jinja2 templates.

```javascript
// Input
msg.template = "{{ states('sensor.temp') }}";

// Output
msg.payload = "22.5";
```

---

## Entity Nodes

**Requires:** Node-RED Custom Integration in HA

### Sensor
Create sensor entities.

```javascript
// Input
msg = {
  payload: {
    state: 22.5,
    attributes: { unit: "°C" }
  }
};
```

| Setting | Description |
|---------|-------------|
| `device_class` | temperature/humidity/etc |
| `unit_of_measurement` | Unit string |

### Binary Sensor
Create on/off sensors.

```javascript
// Input
msg.payload = true;  // or "on"/"off"
```

| Setting | Description |
|---------|-------------|
| `device_class` | motion/door/window/etc |

### Switch
Create controllable switches.

```javascript
// Input (set state)
msg.payload = { state: "on" };

// Output (when toggled from HA)
msg.payload = { state: "on", old_state: "off" };
```

### Button
Create pressable buttons.

```javascript
// Output (when pressed in HA)
msg.payload = { button_pressed: true };
```

### Number
Create numeric inputs.

```javascript
// Input
msg.payload = { state: 22.5 };

// Output (when changed in HA)
msg.payload = { state: 23, old_state: 22.5 };
```

| Setting | Description |
|---------|-------------|
| `min` | Minimum value |
| `max` | Maximum value |
| `step` | Increment |
| `mode` | slider/box |

### Select
Create dropdown selections.

```javascript
// Input
msg.payload = { state: "Option1" };
```

| Setting | Description |
|---------|-------------|
| `options` | Array of options |

### Text
Create text inputs.

```javascript
// Input
msg.payload = { state: "Hello" };
```

| Setting | Description |
|---------|-------------|
| `min` | Min length |
| `max` | Max length |
| `pattern` | Regex validation |

### Time (Entity)
Create time pickers.

```javascript
// Input
msg.payload = { state: "07:30:00" };
```

### Update Config
Dynamically update entity settings.

```javascript
// Input
msg.payload = {
  icon: "mdi:thermometer-high"
};
```

---

## Quick Lookup

### By Use Case

| Task | Node |
|------|------|
| Monitor state changes | Trigger: state |
| Call a service | Action |
| Get current state | Current State |
| Query entities | Get Entities |
| Schedule automation | Time |
| Track location | Zone |
| Handle voice | Sentence |
| Receive webhooks | Webhook |
| Create sensors in HA | Sensor |
| Create switches in HA | Switch |

### Node Categories

**Triggers (start flows):**
Trigger: state, Events: state, Events: all, Events: calendar, Device, Time, Zone, Webhook, Tag, Sentence

**Actions (execute commands):**
Action, Fire Event, API

**State (read data):**
Current State, Get Entities, Get History, Poll State, Wait Until, Render Template

**Entity (create in HA):**
Sensor, Binary Sensor, Switch, Button, Number, Select, Text, Time, Update Config

**Config (shared settings):**
Server Config, Entity Config, Device Config

---

## Related References

- [HA Trigger Nodes](ha-trigger-nodes.md) - Detailed trigger docs
- [HA Action Nodes](ha-action-nodes.md) - Detailed action docs
- [HA State Nodes](ha-state-nodes.md) - Detailed state docs
- [HA Entity Nodes](ha-entity-nodes.md) - Detailed entity docs
