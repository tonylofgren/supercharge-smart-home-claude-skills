# Home Assistant Advanced Nodes

## Table of Contents
- [Overview](#overview)
- [Webhook Node](#webhook-node)
- [Tag Node](#tag-node)
- [Sentence Node](#sentence-node)
- [Render Template Node](#render-template-node)
- [Events: calendar Node](#events-calendar-node)

---

## Overview

Advanced nodes handle specialized integrations like webhooks, NFC tags, voice commands, and calendar events.

| Node | Use Case |
|------|----------|
| **Webhook** | External triggers |
| **Tag** | NFC tag scanning |
| **Sentence** | Voice commands |
| **Render Template** | Jinja2 processing |
| **Events: calendar** | Calendar automation |

---

## Webhook Node

Receive HTTP requests from external services or Home Assistant webhooks.

### Configuration

```javascript
{
  "webhookId": "my_custom_webhook",
  "outputProperties": [
    {"property": "payload", "valueType": "data"},
    {"property": "headers", "valueType": "headers"}
  ]
}
```

### Webhook URL

Access via:
```
https://your-ha-domain/api/webhook/my_custom_webhook
```

### Output Message

```javascript
msg = {
  payload: {
    // Request body data
    action: "trigger",
    room: "living_room"
  },
  headers: {
    "content-type": "application/json",
    "user-agent": "external-service"
  },
  params: {
    // URL query parameters
    key: "value"
  }
};
```

### Calling from External Service

```bash
# cURL example
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"action": "trigger", "room": "living_room"}' \
  https://your-ha-domain/api/webhook/my_custom_webhook
```

### Calling from Home Assistant

```yaml
# automation.yaml
automation:
  - alias: "Trigger Node-RED Webhook"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    action:
      - service: rest_command.node_red_webhook
        data:
          action: motion_detected
          location: "{{ trigger.entity_id }}"

# configuration.yaml
rest_command:
  node_red_webhook:
    url: "http://localhost:1880/api/webhook/my_webhook"
    method: POST
    content_type: "application/json"
    payload: '{"action": "{{ action }}", "location": "{{ location }}"}'
```

### Security

```javascript
// Validate webhook secret
if (msg.headers['x-webhook-secret'] !== env.get('WEBHOOK_SECRET')) {
  node.warn("Invalid webhook secret");
  return null;
}
return msg;
```

---

## Tag Node

Trigger flows when NFC tags are scanned.

### Configuration

```javascript
{
  "tags": ["tag_living_room", "tag_bedroom"],
  "devices": [],  // Optional: limit to specific devices
  "outputProperties": [
    {"property": "payload", "valueType": "complete"}
  ]
}
```

### Output Message

```javascript
msg = {
  payload: {
    tag_id: "tag_living_room",
    device_id: "mobile_app_phone",
    user_id: "user123"
  }
};
```

### Finding Tag IDs

1. Scan tag with HA Companion App
2. Check notification for tag ID
3. Or view in Developer Tools → Events

### Example: Room-Based Actions

```javascript
// Switch node after Tag
// Property: msg.payload.tag_id

// Rules:
[
  {"t": "eq", "v": "tag_living_room"},  // Output 1
  {"t": "eq", "v": "tag_bedroom"},      // Output 2
  {"t": "eq", "v": "tag_office"}        // Output 3
]
```

### Multi-Device Support

```javascript
// Different actions per device
const tag = msg.payload.tag_id;
const device = msg.payload.device_id;

if (device.includes("john")) {
  // John's phone
  msg.action = "personal_greeting";
} else {
  // Other devices
  msg.action = "general_action";
}
return msg;
```

---

## Sentence Node

Handle voice commands from Assist/voice assistants.

### Configuration

```javascript
{
  "sentences": [
    "turn on {area} lights",
    "set {room} temperature to {temp:number}"
  ],
  "outputProperties": [
    {"property": "payload", "valueType": "slots"},
    {"property": "sentence", "valueType": "sentence"}
  ]
}
```

### Sentence Syntax

```
# Basic pattern
"turn on the lights"

# Slot (variable)
"turn on {area} lights"
# Matches: "turn on living room lights"
# Slot value: area = "living room"

# Typed slot
"set temperature to {temp:number}"
# Extracts numeric value

# Optional words
"[please] turn on the lights"
# Matches with or without "please"

# Alternative words
"(turn|switch) on the lights"
# Matches "turn on" or "switch on"
```

### Output Message

```javascript
// Sentence: "set living room temperature to 22"
msg = {
  payload: {
    area: "living room",
    temp: 22
  },
  sentence: "set living room temperature to 22",
  response: null  // Set response text
};
```

### Response

```javascript
// Function node: Generate response
const room = msg.payload.room;
const temp = msg.payload.temp;

// Set response for voice assistant
msg.response = `Setting ${room} temperature to ${temp} degrees`;
return msg;
```

### Example: Voice Control

```
Sentences:
- "turn on {area} lights"
- "set {area} to {preset} mode"
- "what's the temperature in {area}"

Flow:
Sentence Node → Switch (by area) → Action Node
                                 ↓
                        Response with confirmation
```

---

## Render Template Node

Evaluate Home Assistant Jinja2 templates.

### Configuration

```javascript
{
  "template": "{{ states('sensor.temperature') }}",
  "resultsLocation": "payload",
  "resultsLocationType": "msg"
}
```

### Common Templates

```jinja2
{# Get state #}
{{ states('sensor.temperature') }}

{# State with default #}
{{ states('sensor.temperature') | default('unknown') }}

{# Numeric conversion #}
{{ states('sensor.temperature') | float }}
{{ states('sensor.temperature') | int }}

{# Check state #}
{{ is_state('binary_sensor.motion', 'on') }}
{{ is_state_attr('light.room', 'brightness', 255) }}

{# Get attribute #}
{{ state_attr('climate.hvac', 'current_temperature') }}

{# List comprehension #}
{{ states.light
   | selectattr('state', 'eq', 'on')
   | map(attribute='entity_id')
   | list }}

{# Count entities #}
{{ states.light
   | selectattr('state', 'eq', 'on')
   | list | count }}

{# Time functions #}
{{ now() }}
{{ utcnow() }}
{{ now().hour }}
{{ now().strftime('%Y-%m-%d %H:%M') }}

{# Time comparisons #}
{{ (now() - states.sensor.last_motion.last_changed).seconds }}
{{ as_timestamp(now()) - as_timestamp(states.sensor.last_motion.last_changed) }}

{# Area entities #}
{{ area_entities('living_room') }}
{{ area_devices('living_room') }}

{# Labels #}
{{ label_entities('outdoor') }}
```

### Dynamic Templates

```javascript
// Build template from message
msg.template = `{{ states('${msg.entityId}') }}`;

// Or use in template
msg.payload = {
  template: "{{ states('sensor.' + entity_prefix + '_temperature') }}",
  entity_prefix: msg.room
};
```

### Output

```javascript
// Template result is in msg.payload
msg.payload = "22.5";  // String by default

// Parse if needed
msg.payload = parseFloat(msg.payload);
```

---

## Events: calendar Node

Trigger on calendar events.

### Configuration

```javascript
{
  "entityId": "calendar.family",
  "eventType": "start",  // start, end
  "outputProperties": [
    {"property": "payload", "valueType": "eventData"}
  ]
}
```

### Event Types

| Type | Triggers When |
|------|---------------|
| `start` | Event begins |
| `end` | Event ends |

### Output Message

```javascript
msg = {
  payload: {
    summary: "Family Dinner",
    description: "Dinner at restaurant",
    location: "Restaurant Name",
    start: "2024-01-15T18:00:00.000Z",
    end: "2024-01-15T20:00:00.000Z",
    all_day: false
  }
};
```

### Example: Event-Based Automation

```javascript
// Function node after calendar trigger
const event = msg.payload;

// Check event type
if (event.summary.includes("Work")) {
  msg.mode = "work";
} else if (event.summary.includes("Vacation")) {
  msg.mode = "away";
}

return msg;
```

### Filtering Events

```javascript
// Only process certain events
const summary = msg.payload.summary.toLowerCase();

if (!summary.includes("automation") &&
    !summary.includes("trigger")) {
  return null;  // Ignore this event
}

return msg;
```

---

## Combining Advanced Nodes

### Webhook + Action Pattern

```
External Service
      │
      ▼
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Webhook    │───▶│   Validate   │───▶│   Action     │
│             │    │   Request    │    │   Node       │
└─────────────┘    └──────────────┘    └──────────────┘
```

### Voice + Confirmation Pattern

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Sentence   │───▶│   Process    │───▶│   Action     │
│   Node      │    │   Command    │    │   Node       │
└─────────────┘    └──────────────┘    └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   Response   │──▶ Voice feedback
                   └──────────────┘
```

### Tag + Context Pattern

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Tag Node   │───▶│  Check Time  │───▶│   Morning    │
│             │    │  of Day      │    │   Routine    │
└─────────────┘    └──────────────┘    │              │
                          │            └──────────────┘
                          │
                          └───────────▶┌──────────────┐
                                      │   Evening    │
                                      │   Routine    │
                                      └──────────────┘
```

---

## Related References

- [HA Setup](ha-setup.md) - Connection configuration
- [HA Trigger Nodes](ha-trigger-nodes.md) - State triggers
- [HA Action Nodes](ha-action-nodes.md) - Service calls
- [Automation Patterns](automation-patterns.md) - Common patterns
