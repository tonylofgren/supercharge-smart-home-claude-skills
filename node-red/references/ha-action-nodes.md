# Home Assistant Action Nodes

Detailed reference for action/output nodes.

## api-call-service

The primary node for controlling Home Assistant entities.

### Static Configuration

Use when service call is always the same:

```json
{
  "type": "api-call-service",
  "domain": "light",
  "service": "turn_on",
  "areaId": [],
  "deviceId": [],
  "entityId": ["light.living_room", "light.bedroom"],
  "data": "{\"brightness_pct\": 80, \"color_temp\": 300}",
  "dataType": "json",
  "mergeContext": "",
  "mustacheAltTags": false,
  "outputProperties": [],
  "queue": "none"
}
```

### Dynamic via Message

Use when service call varies based on input:

```json
{
  "type": "api-call-service",
  "domain": "",
  "service": "",
  "data": "",
  "dataType": "msg"
}
```

With function node before:

```javascript
msg.payload = {
  action: "light.turn_on",
  target: {
    entity_id: ["light.living_room"]
  },
  data: {
    brightness_pct: msg.brightness || 100
  }
};
return msg;
```

### Target Types

```javascript
// By entity
target: { entity_id: ["light.room1", "light.room2"] }

// By area
target: { area_id: ["living_room", "bedroom"] }

// By device
target: { device_id: ["device_abc123"] }

// Combined
target: {
  entity_id: ["light.specific"],
  area_id: ["living_room"]
}
```

### Queue Options

| Value | Description |
|-------|-------------|
| `none` | No queuing, execute immediately |
| `first` | Queue if busy, process first |
| `last` | Queue if busy, process latest |
| `all` | Queue all requests |

### Common Service Calls

#### Lights

```javascript
// Turn on with brightness
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.room"] },
  data: { brightness_pct: 80 }
};

// Turn on with color
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.room"] },
  data: { rgb_color: [255, 0, 0] }
};

// Turn on with color temperature
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.room"] },
  data: { color_temp_kelvin: 4000 }
};

// Toggle
msg.payload = {
  action: "light.toggle",
  target: { entity_id: ["light.room"] }
};

// Turn off with transition
msg.payload = {
  action: "light.turn_off",
  target: { entity_id: ["light.room"] },
  data: { transition: 5 }
};
```

#### Climate

```javascript
// Set temperature
msg.payload = {
  action: "climate.set_temperature",
  target: { entity_id: ["climate.thermostat"] },
  data: { temperature: 22 }
};

// Set HVAC mode
msg.payload = {
  action: "climate.set_hvac_mode",
  target: { entity_id: ["climate.thermostat"] },
  data: { hvac_mode: "heat" }
};

// Set preset
msg.payload = {
  action: "climate.set_preset_mode",
  target: { entity_id: ["climate.thermostat"] },
  data: { preset_mode: "away" }
};
```

#### Media Player

```javascript
// Play/Pause
msg.payload = {
  action: "media_player.media_play_pause",
  target: { entity_id: ["media_player.living_room"] }
};

// Set volume
msg.payload = {
  action: "media_player.volume_set",
  target: { entity_id: ["media_player.living_room"] },
  data: { volume_level: 0.5 }
};

// Play media
msg.payload = {
  action: "media_player.play_media",
  target: { entity_id: ["media_player.living_room"] },
  data: {
    media_content_type: "music",
    media_content_id: "spotify:playlist:abc123"
  }
};
```

#### Notifications

```javascript
// Mobile app notification
msg.payload = {
  action: "notify.mobile_app_phone",
  data: {
    title: "Alert",
    message: "Motion detected",
    data: {
      priority: "high"
    }
  }
};

// Persistent notification
msg.payload = {
  action: "notify.persistent_notification",
  data: {
    title: "Reminder",
    message: "Check the front door"
  }
};

// Actionable notification
msg.payload = {
  action: "notify.mobile_app_phone",
  data: {
    title: "Door Open",
    message: "Front door has been open for 5 minutes",
    data: {
      actions: [
        { action: "DISMISS", title: "Dismiss" },
        { action: "LOCK", title: "Lock Door" }
      ]
    }
  }
};
```

#### Covers

```javascript
// Open/Close
msg.payload = {
  action: "cover.open_cover",
  target: { entity_id: ["cover.garage"] }
};

// Set position
msg.payload = {
  action: "cover.set_cover_position",
  target: { entity_id: ["cover.blinds"] },
  data: { position: 50 }
};
```

#### Scenes and Scripts

```javascript
// Activate scene
msg.payload = {
  action: "scene.turn_on",
  target: { entity_id: ["scene.movie_time"] }
};

// Run script
msg.payload = {
  action: "script.turn_on",
  target: { entity_id: ["script.welcome_home"] }
};

// Run script with variables
msg.payload = {
  action: "script.announcement",
  data: {
    variables: {
      message: "Dinner is ready"
    }
  }
};
```

#### Locks

```javascript
// Lock
msg.payload = {
  action: "lock.lock",
  target: { entity_id: ["lock.front_door"] }
};

// Unlock (some locks support code)
msg.payload = {
  action: "lock.unlock",
  target: { entity_id: ["lock.front_door"] },
  data: { code: "1234" }
};
```

---

## ha-fire-event

Fire custom events on the Home Assistant event bus.

### Configuration

```json
{
  "type": "ha-fire-event",
  "event": "my_custom_event",
  "data": "{\"key\": \"value\"}",
  "dataType": "json"
}
```

### Dynamic Event

```javascript
msg.payload = {
  event_type: "node_red_automation",
  event_data: {
    source: "motion_flow",
    triggered_by: msg.data.entity_id
  }
};
```

### Use Cases

- Trigger HA automations from Node-RED
- Create custom integration points
- Logging and debugging
- Cross-system notifications

---

## ha-api

Direct access to Home Assistant's WebSocket and HTTP APIs.

### Configuration

```json
{
  "type": "ha-api",
  "protocol": "websocket",
  "method": "get",
  "path": "",
  "data": "",
  "dataType": "json",
  "outputProperties": []
}
```

### Protocol Options

| Protocol | Use Case |
|----------|----------|
| `websocket` | Real-time, persistent connection |
| `http` | RESTful API calls |

### Common API Calls

#### Get All States (WebSocket)

```json
{
  "protocol": "websocket",
  "method": "get",
  "path": "states"
}
```

#### Get Specific State (HTTP)

```json
{
  "protocol": "http",
  "method": "get",
  "path": "states/sensor.temperature"
}
```

#### Get History

```json
{
  "protocol": "http",
  "method": "get",
  "path": "history/period/2024-01-01T00:00:00Z?filter_entity_id=sensor.temperature"
}
```

#### Get Logbook

```json
{
  "protocol": "http",
  "method": "get",
  "path": "logbook/2024-01-01T00:00:00Z"
}
```

---

## api-render-template

Render Jinja2 templates.

### Configuration

```json
{
  "type": "api-render-template",
  "template": "{{ states('sensor.temperature') }}°C",
  "resultsLocation": "payload",
  "resultsLocationType": "msg"
}
```

### Template Examples

#### Entity State

```jinja2
{{ states('sensor.temperature') }}
```

#### Entity Attribute

```jinja2
{{ state_attr('climate.thermostat', 'current_temperature') }}
```

#### Conditional

```jinja2
{% if is_state('sun.sun', 'above_horizon') %}
  Daytime
{% else %}
  Nighttime
{% endif %}
```

#### Looping

```jinja2
{% set lights = states.light | selectattr('state', 'eq', 'on') | list %}
Lights on: {{ lights | length }}
{% for light in lights %}
  - {{ light.name }}
{% endfor %}
```

#### Time Formatting

```jinja2
{{ now().strftime('%H:%M') }}
{{ as_timestamp(states.sensor.last_motion.last_changed) | timestamp_custom('%H:%M') }}
```

### Dynamic Template

Pass template in message:

```javascript
msg.template = `
  Temperature: {{ states('sensor.temperature') }}°C
  Humidity: {{ states('sensor.humidity') }}%
`;
```

With node configured to use `msg.template`.

---

## Output Message Handling

### Checking Service Call Success

```javascript
// After api-call-service
if (msg.payload && !msg.payload.error) {
  node.status({fill:"green", shape:"dot", text:"success"});
} else {
  node.status({fill:"red", shape:"dot", text:"failed"});
}
```

### Getting Service Response

Some services return data:

```json
"outputProperties": [
  {
    "property": "response",
    "propertyType": "msg",
    "value": "",
    "valueType": "results"
  }
]
```

Then access via `msg.response`.
