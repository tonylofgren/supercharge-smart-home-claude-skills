# Home Assistant Action Nodes

## Table of Contents
- [Overview](#overview)
- [Action Node](#action-node)
- [Fire Event Node](#fire-event-node)
- [API Node](#api-node)
- [Common Service Calls](#common-service-calls)
- [Dynamic Service Calls](#dynamic-service-calls)
- [Error Handling](#error-handling)

---

## Overview

Action nodes execute commands in Home Assistant - turning on lights, sending notifications, controlling devices.

### Quick Reference

| Node | Use When |
|------|----------|
| **Action** | Call any HA service |
| **Fire Event** | Trigger custom events |
| **API** | Direct WebSocket/HTTP API |

---

## Action Node

The primary node for calling Home Assistant services (formerly "Call Service").

### Basic Configuration

```javascript
{
  "action": "light.turn_on",
  "target": {
    "entity_id": ["light.living_room"]
  },
  "data": {
    "brightness_pct": 100
  }
}
```

### Configuration Options

| Option | Description |
|--------|-------------|
| **Action** | Service to call (domain.service) |
| **Target** | Entity/area/device IDs |
| **Data** | Service-specific parameters |
| **Queue** | Handle disconnection |
| **Merge Context** | Include context variables |

### Target Types

```javascript
// Single entity
"target": {
  "entity_id": ["light.living_room"]
}

// Multiple entities
"target": {
  "entity_id": ["light.living_room", "light.bedroom"]
}

// Area
"target": {
  "area_id": ["living_room"]
}

// Device
"target": {
  "device_id": ["abc123def456"]
}

// Floor
"target": {
  "floor_id": ["first_floor"]
}

// Label
"target": {
  "label_id": ["outdoor_lights"]
}

// Combined
"target": {
  "entity_id": ["light.kitchen"],
  "area_id": ["living_room"]
}
```

### Data Field

```javascript
// Light service data
"data": {
  "brightness_pct": 75,
  "color_temp": 350,
  "transition": 2
}

// Notification data
"data": {
  "message": "Hello World",
  "title": "Alert",
  "data": {
    "priority": "high"
  }
}

// Script data
"data": {
  "variables": {
    "target_light": "light.bedroom"
  }
}
```

### Templates (Mustache)

Use `{{property}}` for dynamic values:

```javascript
// Entity from message
"target": {
  "entity_id": ["{{payload.entity_id}}"]
}

// Dynamic brightness
"data": {
  "brightness_pct": "{{payload.brightness}}"
}

// Conditional color
"data": {
  "rgb_color": "{{payload.color}}"
}
```

### Output Message

```javascript
msg = {
  payload: {
    // Service response (if any)
  },
  data: {
    action: "light.turn_on",
    target: { entity_id: ["light.living_room"] },
    data: { brightness_pct: 100 }
  }
};
```

### Queue Options

| Option | Behavior |
|--------|----------|
| `none` | Drop if disconnected |
| `first` | Queue first message only |
| `all` | Queue all messages |
| `last` | Queue only most recent |

---

## Fire Event Node

Trigger custom events on the Home Assistant event bus.

### Configuration

```javascript
{
  "event": "custom_node_red_event",
  "data": {
    "source": "node_red",
    "action": "motion_detected",
    "room": "living_room"
  }
}
```

### Dynamic Event Data

```javascript
// Use message payload
"data": {
  "triggered_by": "{{topic}}",
  "value": "{{payload}}"
}

// Via function node
msg.payload = {
  event: "custom_event",
  data: {
    temperature: msg.payload.temp,
    timestamp: Date.now()
  }
};
```

### Listening in Home Assistant

```yaml
# automation.yaml
automation:
  - alias: "Handle Node-RED Event"
    trigger:
      - platform: event
        event_type: custom_node_red_event
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.room == 'living_room' }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Event from Node-RED: {{ trigger.event.data.action }}"
```

---

## API Node

Direct access to Home Assistant's WebSocket and HTTP APIs.

### WebSocket API

```javascript
// Configuration
{
  "protocol": "websocket",
  "method": "get",
  "path": "states",  // API endpoint
  "data": {}
}
```

### Common WebSocket Methods

| Method | Path | Description |
|--------|------|-------------|
| `get` | `states` | Get all entity states |
| `get` | `config` | Get HA configuration |
| `get` | `services` | Get available services |
| `post` | `services/{domain}/{service}` | Call service |

### HTTP API

```javascript
// Configuration
{
  "protocol": "http",
  "method": "GET",
  "path": "/api/states",
  "data": {}
}
```

### HTTP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/` | API status |
| `GET` | `/api/states` | All states |
| `GET` | `/api/states/{entity_id}` | Single entity |
| `POST` | `/api/services/{domain}/{service}` | Call service |
| `GET` | `/api/history/period` | History data |

### Render Template

```javascript
// Use API node to render templates
{
  "protocol": "websocket",
  "method": "post",
  "path": "template",
  "data": {
    "template": "{{ states('sensor.temperature') | float }}"
  }
}
```

---

## Common Service Calls

### Lights

```javascript
// Turn on with brightness
{
  "action": "light.turn_on",
  "target": {"entity_id": ["light.living_room"]},
  "data": {
    "brightness_pct": 75,
    "transition": 2
  }
}

// Set color
{
  "action": "light.turn_on",
  "target": {"entity_id": ["light.rgb_strip"]},
  "data": {
    "rgb_color": [255, 100, 50]
  }
}

// Toggle
{
  "action": "light.toggle",
  "target": {"entity_id": ["light.kitchen"]}
}
```

### Switches & Covers

```javascript
// Switch
{
  "action": "switch.turn_on",
  "target": {"entity_id": ["switch.fan"]}
}

// Cover
{
  "action": "cover.set_cover_position",
  "target": {"entity_id": ["cover.blinds"]},
  "data": {"position": 50}
}
```

### Climate

```javascript
// Set temperature
{
  "action": "climate.set_temperature",
  "target": {"entity_id": ["climate.hvac"]},
  "data": {
    "temperature": 22,
    "hvac_mode": "heat"
  }
}

// Set preset
{
  "action": "climate.set_preset_mode",
  "target": {"entity_id": ["climate.hvac"]},
  "data": {"preset_mode": "away"}
}
```

### Notifications

```javascript
// Mobile notification
{
  "action": "notify.mobile_app_phone",
  "data": {
    "message": "Motion detected!",
    "title": "Security Alert",
    "data": {
      "priority": "high",
      "ttl": 0,
      "image": "/local/camera_snapshot.jpg"
    }
  }
}

// Persistent notification
{
  "action": "persistent_notification.create",
  "data": {
    "message": "System alert",
    "title": "Warning",
    "notification_id": "system_alert"
  }
}
```

### Media Player

```javascript
// Play media
{
  "action": "media_player.play_media",
  "target": {"entity_id": ["media_player.speaker"]},
  "data": {
    "media_content_id": "http://example.com/audio.mp3",
    "media_content_type": "music"
  }
}

// TTS
{
  "action": "tts.speak",
  "target": {"entity_id": ["media_player.speaker"]},
  "data": {
    "message": "Hello World"
  }
}

// Volume
{
  "action": "media_player.volume_set",
  "target": {"entity_id": ["media_player.speaker"]},
  "data": {"volume_level": 0.5}
}
```

### Scripts & Scenes

```javascript
// Run script
{
  "action": "script.turn_on",
  "target": {"entity_id": ["script.morning_routine"]},
  "data": {
    "variables": {
      "brightness": 80
    }
  }
}

// Activate scene
{
  "action": "scene.turn_on",
  "target": {"entity_id": ["scene.movie_night"]},
  "data": {"transition": 5}
}
```

### Input Helpers

```javascript
// Input boolean
{
  "action": "input_boolean.turn_on",
  "target": {"entity_id": ["input_boolean.vacation_mode"]}
}

// Input number
{
  "action": "input_number.set_value",
  "target": {"entity_id": ["input_number.target_temp"]},
  "data": {"value": 22}
}

// Input select
{
  "action": "input_select.select_option",
  "target": {"entity_id": ["input_select.home_mode"]},
  "data": {"option": "Away"}
}

// Input text
{
  "action": "input_text.set_value",
  "target": {"entity_id": ["input_text.message"]},
  "data": {"value": "Hello"}
}
```

---

## Dynamic Service Calls

### From Function Node

```javascript
// Build service call dynamically
const brightness = msg.payload.bright ? 100 : 50;
const entity = `light.${msg.payload.room}`;

msg.payload = {
  action: "light.turn_on",
  target: {
    entity_id: [entity]
  },
  data: {
    brightness_pct: brightness,
    transition: 1
  }
};
return msg;
```

### Override Configuration

```javascript
// Input message overrides node config
msg.payload = {
  action: "light.turn_on",
  target: {
    entity_id: ["light.override_entity"]
  },
  data: {
    brightness_pct: 50
  }
};
```

### Batch Service Calls

```javascript
// Call multiple services
const rooms = ["living_room", "bedroom", "kitchen"];
const messages = rooms.map(room => ({
  payload: {
    action: "light.turn_off",
    target: {
      entity_id: [`light.${room}`]
    }
  }
}));
return [messages];
```

---

## Error Handling

### Check Service Response

```javascript
// Function node after Action
if (msg.payload && msg.payload.error) {
  node.error("Service call failed: " + msg.payload.error);
  return [null, msg];  // Error output
}
return [msg, null];  // Success output
```

### Handle Disconnection

```javascript
// Use queue for important actions
{
  "queue": "last"  // Keep most recent if disconnected
}
```

### Retry Pattern

```javascript
// Retry on failure
const maxRetries = 3;
const retries = msg.retries || 0;

if (retries < maxRetries) {
  msg.retries = retries + 1;
  // Wait and retry
  setTimeout(() => node.send(msg), 1000 * retries);
  return null;
}

// Max retries exceeded
node.error("Service call failed after " + maxRetries + " retries");
return null;
```

---

## Related References

- [HA Setup](ha-setup.md) - Connection configuration
- [HA Trigger Nodes](ha-trigger-nodes.md) - Event triggers
- [HA State Nodes](ha-state-nodes.md) - Reading state
- [Automation Patterns](automation-patterns.md) - Common recipes
