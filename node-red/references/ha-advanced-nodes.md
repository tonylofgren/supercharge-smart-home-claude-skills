# Advanced Home Assistant Nodes

Webhook, Tag, Sentence, Render Template, and other specialized nodes.

## Webhook Node

Receive external HTTP requests.

### Basic Configuration

```json
{
  "type": "webhook",
  "webhookId": "my_custom_webhook",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

### Setup in Home Assistant

1. Configure webhook ID in node
2. Deploy flow
3. Access URL: `https://your-ha.com/api/webhook/my_custom_webhook`

### Output Message

```javascript
msg = {
  payload: {
    // POST body or query params
  },
  headers: {
    // HTTP headers
  },
  params: {
    // URL parameters
  }
};
```

### Authentication

Options:
- None (open)
- Basic authentication
- Custom header validation

### Example: IFTTT Integration

```json
{
  "webhookId": "ifttt_trigger",
  "method": "POST"
}
```

Function node to process:
```javascript
const event = msg.payload.event;
const value = msg.payload.value1;

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness_pct: parseInt(value) || 100 }
};

return msg;
```

---

## Tag Node

Trigger on NFC tag scans.

### Configuration

```json
{
  "type": "tag",
  "tag": "",
  "device": "",
  "exposeAsEntityConfig": ""
}
```

### Filter Options

| Field | Purpose |
|-------|---------|
| Tag ID | Specific tag only |
| Device | Specific scanner only |
| (empty) | All tag scans |

### Output Message

```javascript
msg = {
  payload: {
    tag_id: "unique-tag-id",
    device_id: "scanner-device-id"
  },
  data: {
    event: { /* full event data */ }
  }
};
```

### Example: Tag-Based Scenes

```javascript
const tagId = msg.payload.tag_id;

const tagScenes = {
  "tag-123": "scene.morning",
  "tag-456": "scene.evening",
  "tag-789": "scene.movie"
};

const scene = tagScenes[tagId];
if (scene) {
  msg.payload = {
    action: "scene.turn_on",
    target: { entity_id: [scene] }
  };
  return msg;
}

node.warn(`Unknown tag: ${tagId}`);
return null;
```

---

## Sentence Node

Trigger on voice commands (Assist).

### Configuration

```json
{
  "type": "sentence",
  "sentences": [
    "turn on [the] lights",
    "set lights to {brightness} percent"
  ]
}
```

### Sentence Syntax

| Pattern | Matches |
|---------|---------|
| `word` | Exact word |
| `[optional]` | Optional word |
| `(a|b|c)` | One of choices |
| `{slot}` | Capture value |

### Examples

```
turn on [the] (living room|kitchen) lights
set temperature to {temp} degrees
play {playlist} on {speaker}
```

### Output Message

```javascript
msg = {
  payload: {
    // Captured slot values
    brightness: "80",
    room: "living room"
  }
};
```

### Example: Voice Light Control

Sentence: `set {room} lights to {brightness} percent`

Function node:
```javascript
const room = msg.payload.room;
const brightness = parseInt(msg.payload.brightness);

const roomEntities = {
  "living room": "light.living_room",
  "kitchen": "light.kitchen",
  "bedroom": "light.bedroom"
};

const entity = roomEntities[room.toLowerCase()];
if (entity) {
  msg.payload = {
    action: "light.turn_on",
    target: { entity_id: [entity] },
    data: { brightness_pct: brightness }
  };
  return msg;
}

return null;
```

---

## Render Template Node

Evaluate Home Assistant templates.

### Configuration

```json
{
  "type": "render-template",
  "template": "{{ states('sensor.temperature') }}",
  "templateLocation": "payload",
  "templateLocationType": "msg"
}
```

### Template Sources

| Source | Use Case |
|--------|----------|
| Fixed template | Static template string |
| msg property | Dynamic template |

### Common Templates

**Current state:**
```jinja
{{ states('light.living_room') }}
```

**With attributes:**
```jinja
{{ state_attr('light.living_room', 'brightness') }}
```

**Conditional:**
```jinja
{% if is_state('binary_sensor.motion', 'on') %}
  Motion detected
{% else %}
  No motion
{% endif %}
```

**Time-based:**
```jinja
{% if now().hour >= 22 or now().hour < 6 %}
  Night mode
{% else %}
  Day mode
{% endif %}
```

**Entity count:**
```jinja
{{ states.light | selectattr('state', 'eq', 'on') | list | count }}
```

### Output

Template result in configured location (default: `msg.payload`).

### Example: Dynamic Notification

Template:
```jinja
{{ states.binary_sensor
   | selectattr('state', 'eq', 'on')
   | selectattr('attributes.device_class', 'eq', 'door')
   | map(attribute='attributes.friendly_name')
   | list | join(', ') }}
```

Result: "Front Door, Back Door"

---

## API Node

Direct Home Assistant REST API calls.

### Configuration

```json
{
  "type": "api",
  "protocol": "http",
  "method": "get",
  "path": "/api/states/light.living_room",
  "data": ""
}
```

### Common Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/` | API check |
| GET | `/api/states` | All entity states |
| GET | `/api/states/{entity_id}` | Single entity |
| POST | `/api/states/{entity_id}` | Set state |
| POST | `/api/services/{domain}/{service}` | Call service |
| GET | `/api/history/period` | History data |

### Dynamic Paths

Use `msg.apiPath`:
```javascript
msg.apiPath = `/api/states/${msg.entityId}`;
return msg;
```

### Example: Bulk State Query

```javascript
// Before API node
msg.apiPath = "/api/states";
return msg;

// After API node
const lights = msg.payload
  .filter(e => e.entity_id.startsWith('light.'))
  .filter(e => e.state === 'on');

msg.payload = lights;
return msg;
```

---

## Fire Event Node

Fire custom events in Home Assistant.

### Configuration

```json
{
  "type": "fire-event",
  "event": "custom_event",
  "eventType": "str",
  "data": "{\"key\": \"value\"}"
}
```

### Event Types

**Custom events:**
```
nodered_motion_detected
custom_notification_request
app_data_update
```

### Event Data

Static:
```json
{
  "source": "node-red",
  "room": "living_room"
}
```

Dynamic from msg:
```javascript
msg.event = "motion_detected";
msg.eventData = {
  room: msg.room,
  timestamp: Date.now()
};
return msg;
```

### Listening in HA

```yaml
automation:
  - alias: "Handle custom event"
    trigger:
      - platform: event
        event_type: nodered_motion_detected
    action:
      - service: notify.mobile_app
        data:
          message: "Motion in {{ trigger.event.data.room }}"
```

---

## Events: All Node

Listen to all Home Assistant events.

### Configuration

```json
{
  "type": "events-all",
  "eventType": "",
  "eventTypeType": "str"
}
```

### Filter by Event Type

Common event types:
- `state_changed` - Entity state changes
- `call_service` - Service calls
- `automation_triggered` - Automation triggers
- `script_started` - Script execution
- `homeassistant_start` - HA startup
- `component_loaded` - Component load

### Output Message

```javascript
msg = {
  payload: { /* event data */ },
  topic: "state_changed",
  event_type: "state_changed",
  data: { /* full event */ }
};
```

### Example: Log All Service Calls

```javascript
if (msg.event_type === "call_service") {
  const domain = msg.payload.domain;
  const service = msg.payload.service;
  const target = msg.payload.service_data?.entity_id;

  node.log(`Service: ${domain}.${service} → ${target}`);
}

return null; // Don't pass through
```

---

## Events: Calendar Node

Trigger on calendar events.

### Configuration

```json
{
  "type": "events-calendar",
  "entityId": "calendar.family",
  "eventType": "start"
}
```

### Event Types

| Type | Triggers |
|------|----------|
| `start` | Event starts |
| `end` | Event ends |

### Output Message

```javascript
msg = {
  payload: {
    summary: "Meeting",
    description: "...",
    location: "Office",
    start: "2024-01-15T10:00:00",
    end: "2024-01-15T11:00:00"
  }
};
```

### Example: Meeting Reminder

```javascript
const event = msg.payload;
const summary = event.summary;
const startTime = new Date(event.start);

// Only for meetings starting in next 15 minutes
const now = Date.now();
const diff = startTime.getTime() - now;
const minutes = Math.round(diff / 60000);

if (minutes > 0 && minutes <= 15) {
  msg.payload = {
    action: "notify.mobile_app_phone",
    data: {
      title: "Upcoming Meeting",
      message: `${summary} starts in ${minutes} minutes`
    }
  };
  return msg;
}

return null;
```

---

## Wait Until Node

Pause flow until condition is met.

### Configuration

```json
{
  "type": "wait-until",
  "entityId": "binary_sensor.motion",
  "entityIdType": "exact",
  "property": "state",
  "comparator": "is",
  "value": "off",
  "timeout": "30",
  "timeoutUnits": "seconds"
}
```

### Outputs

| Output | When |
|--------|------|
| 1 | Condition met |
| 2 | Timeout reached |

### Timeout Options

- Seconds, minutes, hours
- msg property for dynamic timeout

### Example: Motion Timeout

```
[motion on] → [turn on light] → [wait until: motion off, 5 min] → [turn off]
                                           ↓
                                      [output 2: timeout]
                                           ↓
                                      [turn off anyway]
```

---

## Zone Node

Trigger on zone enter/leave.

### Configuration

```json
{
  "type": "zone",
  "entities": ["person.john", "person.jane"],
  "zone": "zone.home",
  "event": "enter"
}
```

### Event Types

| Event | Triggers |
|-------|----------|
| `enter` | Entity enters zone |
| `leave` | Entity leaves zone |

### Output Message

```javascript
msg = {
  payload: "enter", // or "leave"
  data: {
    entity_id: "person.john",
    new_state: { /* person state */ },
    old_state: { /* previous state */ }
  }
};
```

### Example: Arrival Actions

```javascript
const person = msg.data.entity_id;
const event = msg.payload;

if (event === "enter") {
  // Person arrived home
  msg.payload = {
    action: "light.turn_on",
    target: { entity_id: ["light.entryway"] }
  };
  return msg;
}

return null;
```

---

## Time Node

Trigger at specific times.

### Configuration

```json
{
  "type": "time",
  "crontab": "0 7 * * 1-5",
  "entityId": "",
  "property": ""
}
```

### Crontab Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun-Sat)
│ │ │ │ │
* * * * *
```

### Examples

| Schedule | Crontab |
|----------|---------|
| Every day 7 AM | `0 7 * * *` |
| Weekdays 7 AM | `0 7 * * 1-5` |
| Every hour | `0 * * * *` |
| Every 15 min | `*/15 * * * *` |
| First of month | `0 0 1 * *` |

### Entity-Based Time

Use HA input_datetime:
```json
{
  "entityId": "input_datetime.alarm_time",
  "property": ""
}
```

---

## Quick Reference

### Node Selection

| Use Case | Node |
|----------|------|
| External HTTP trigger | Webhook |
| NFC tag scan | Tag |
| Voice command | Sentence |
| Evaluate HA template | Render Template |
| Direct API access | API |
| Fire HA event | Fire Event |
| Listen all events | Events: All |
| Calendar events | Events: Calendar |
| Wait for state | Wait Until |
| Location trigger | Zone |
| Time-based trigger | Time |

### Common Patterns

**Webhook + Validation:**
```
[Webhook] → [Function: validate] → [Action]
                    ↓
               [HTTP Response: error]
```

**Time + Condition:**
```
[Time: 7 AM] → [Current State: is_weekday] → [Action]
```

**Zone + Presence:**
```
[Zone: leave] → [Get Entities: persons home] → [Switch: count=0] → [Away mode]
```

