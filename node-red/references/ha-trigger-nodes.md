# Home Assistant Trigger Nodes

Detailed reference for all trigger nodes in node-red-contrib-home-assistant-websocket.

## trigger-state

The most commonly used trigger node. Fires when entity state changes match conditions.

### Basic Configuration

```json
{
  "type": "trigger-state",
  "entityId": "binary_sensor.motion",
  "entityIdType": "exact",
  "constraints": [],
  "outputs": 2,
  "outputInitially": false,
  "stateType": "str"
}
```

### entityIdType Options

| Type | Description | Example |
|------|-------------|---------|
| `exact` | Match exact entity_id | `light.living_room` |
| `substring` | Match if contains | `living_room` |
| `regex` | Regular expression | `light\\.living_.*` |

**IMPORTANT:** There is NO `list` type! Use `regex` for multiple entities:

```json
"entityId": "binary_sensor\\.motion_(living|bed|hall)",
"entityIdType": "regex"
```

### Constraints

Filter state changes with conditions:

```json
"constraints": [
  {
    "targetType": "this_entity",
    "propertyType": "current_state",
    "comparatorType": "is",
    "comparatorValue": "on"
  },
  {
    "targetType": "this_entity",
    "propertyType": "previous_state",
    "comparatorType": "is_not",
    "comparatorValue": "unavailable"
  }
]
```

#### targetType Options

| Value | Description |
|-------|-------------|
| `this_entity` | The entity that triggered the node |
| `entity_id` | A specific other entity |

#### propertyType Options

| Value | Description |
|-------|-------------|
| `current_state` | New state value |
| `previous_state` | Old state value |
| `attribute` | Entity attribute (specify property) |

#### comparatorType Options

| Value | Description |
|-------|-------------|
| `is` | Equals |
| `is_not` | Not equals |
| `lt` | Less than (numeric) |
| `lte` | Less than or equal |
| `gt` | Greater than |
| `gte` | Greater than or equal |
| `starts_with` | String starts with |
| `ends_with` | String ends with |
| `in` | Value in list |
| `not_in` | Value not in list |
| `includes` | Array includes value |
| `does_not_include` | Array doesn't include |
| `is_jsonata` | JSONata expression |
| `is_regex` | Regex match |

### Outputs

- `outputs: 1` - All state changes to output 1
- `outputs: 2` - Matched constraints to output 1, unmatched to output 2

### Output Message

```javascript
{
  payload: "on",  // New state
  topic: "binary_sensor.motion",
  data: {
    entity_id: "binary_sensor.motion",
    new_state: {
      state: "on",
      attributes: { device_class: "motion" },
      last_changed: "2024-01-01T12:00:00Z",
      last_updated: "2024-01-01T12:00:00Z"
    },
    old_state: {
      state: "off",
      attributes: { device_class: "motion" },
      last_changed: "2024-01-01T11:55:00Z"
    }
  }
}
```

### Custom Output Properties

Control what goes into the message:

```json
"outputProperties": [
  {
    "property": "payload",
    "propertyType": "msg",
    "value": "",
    "valueType": "entityState"
  },
  {
    "property": "data",
    "propertyType": "msg",
    "value": "",
    "valueType": "eventData"
  }
]
```

#### valueType Options

| Value | Result |
|-------|--------|
| `entityState` | Just the state string |
| `entity` | Full entity object |
| `eventData` | New and old state objects |
| `triggerId` | Entity ID that triggered |

### Examples

#### Motion Sensor ON

```json
{
  "type": "trigger-state",
  "entityId": "binary_sensor.motion_living_room",
  "entityIdType": "exact",
  "constraints": [
    {
      "targetType": "this_entity",
      "propertyType": "current_state",
      "comparatorType": "is",
      "comparatorValue": "on"
    }
  ]
}
```

#### Temperature Above Threshold

```json
{
  "type": "trigger-state",
  "entityId": "sensor.temperature",
  "entityIdType": "exact",
  "constraints": [
    {
      "targetType": "this_entity",
      "propertyType": "current_state",
      "comparatorType": "gt",
      "comparatorValue": "25"
    }
  ],
  "stateType": "num"
}
```

#### Any Light Turned On

```json
{
  "type": "trigger-state",
  "entityId": "light\\..+",
  "entityIdType": "regex",
  "constraints": [
    {
      "targetType": "this_entity",
      "propertyType": "current_state",
      "comparatorType": "is",
      "comparatorValue": "on"
    },
    {
      "targetType": "this_entity",
      "propertyType": "previous_state",
      "comparatorType": "is",
      "comparatorValue": "off"
    }
  ]
}
```

---

## events-state (server-state-changed)

Simpler state change listener. Less configuration options.

**Note:** UI name is "Events: state" but JSON type is `server-state-changed`.

### Basic Configuration

```json
{
  "type": "server-state-changed",
  "entityidfilter": "light.living_room",
  "entityidfiltertype": "exact",
  "outputinitially": false,
  "stateType": "str",
  "ifState": "",
  "ifStateType": "str",
  "ifStateOperator": "is"
}
```

### When to Use trigger-state vs events-state

| Use Case | Recommended Node |
|----------|------------------|
| Simple state monitoring | events-state |
| Complex conditions | trigger-state |
| Multiple constraints | trigger-state |
| Attribute checks | trigger-state |
| Just need state changes | events-state |

---

## events-all

Listen to any Home Assistant event.

### Configuration

```json
{
  "type": "server-events",
  "event_type": "call_service",
  "exposeAsEntityConfig": "",
  "waitForRunning": true
}
```

### Common Event Types

| Event | Description |
|-------|-------------|
| `call_service` | Service was called |
| `state_changed` | Entity state changed |
| `automation_triggered` | Automation fired |
| `script_started` | Script began execution |
| `homeassistant_start` | HA started |
| `homeassistant_stop` | HA stopping |
| `component_loaded` | Integration loaded |

### Output Message

```javascript
{
  payload: {
    event_type: "call_service",
    data: {
      domain: "light",
      service: "turn_on",
      service_data: { entity_id: "light.room" }
    },
    origin: "LOCAL",
    time_fired: "2024-01-01T12:00:00Z"
  }
}
```

---

## ha-time

Time-based triggers.

### Configuration

```json
{
  "type": "ha-time",
  "entityId": "input_datetime.morning_alarm",
  "property": "",
  "offset": 0,
  "offsetUnits": "minutes",
  "randomOffset": false,
  "repeatDaily": true
}
```

### Trigger Types

1. **Entity-based**: Trigger at time from input_datetime entity
2. **Fixed time**: Use property field for time string

### Offset Options

- Positive: Trigger after the time
- Negative: Trigger before the time
- Random: Add randomness within offset range

### Example: Sunrise Offset

```json
{
  "type": "ha-time",
  "entityId": "sensor.sun_next_rising",
  "offset": -30,
  "offsetUnits": "minutes"
}
```

---

## ha-zone

Trigger when entities enter or leave zones.

### Configuration

```json
{
  "type": "ha-zone",
  "entities": ["person.john", "person.jane"],
  "zones": ["zone.home", "zone.work"],
  "event": "enter",
  "outputs": 2
}
```

### Event Options

| Value | Description |
|-------|-------------|
| `enter` | Entity entered zone |
| `leave` | Entity left zone |
| `enter_leave` | Both events |

### Output Message

```javascript
{
  payload: {
    entity_id: "person.john",
    event: "enter",
    zone: "zone.home",
    from_zone: "zone.work"
  }
}
```

---

## ha-device

Device automations (button presses, device triggers).

### Configuration

```json
{
  "type": "ha-device",
  "exposeAsEntityConfig": "",
  "deviceId": "device_id_here",
  "deviceType": "trigger",
  "event": {},
  "capabilities": [],
  "outputProperties": []
}
```

### Common Device Triggers

- Button press (single, double, long)
- Motion detected
- Door opened/closed
- Device connected/disconnected

---

## ha-tag

NFC tag scans.

### Configuration

```json
{
  "type": "ha-tag",
  "tags": ["tag_id_1", "tag_id_2"],
  "devices": []
}
```

### Output Message

```javascript
{
  payload: {
    tag_id: "tag_id_1",
    device_id: "scanner_device_id"
  }
}
```

---

## ha-webhook

HTTP webhook triggers.

### Configuration

```json
{
  "type": "ha-webhook",
  "webhookId": "my_webhook_id",
  "exposeAsEntityConfig": "",
  "outputProperties": []
}
```

### Webhook URL

After deploying, webhook is available at:
```
https://your-ha.com/api/webhook/my_webhook_id
```

### Output Message

```javascript
{
  payload: {
    query: { param1: "value1" },
    body: { data: "from_post" },
    headers: { "content-type": "application/json" }
  }
}
```

---

## ha-sentence

Voice command triggers (Assist integration).

### Configuration

```json
{
  "type": "ha-sentence",
  "sentences": [
    "turn on the {room} lights",
    "set {room} brightness to {level}"
  ],
  "exposeAsEntityConfig": "",
  "outputProperties": []
}
```

### Slots

Use `{name}` for variable parts that will be captured:

```json
"sentences": ["play {artist} music", "play music by {artist}"]
```

### Output Message

```javascript
{
  payload: {
    sentence: "play Beatles music",
    slots: {
      artist: "Beatles"
    }
  }
}
```

---

## events-calendar

Calendar event triggers.

### Configuration

```json
{
  "type": "ha-events-calendar",
  "entityId": "calendar.home",
  "eventType": "start",
  "offset": 0,
  "offsetUnits": "minutes"
}
```

### Event Types

| Value | Description |
|-------|-------------|
| `start` | Calendar event starts |
| `end` | Calendar event ends |

### Output Message

```javascript
{
  payload: {
    summary: "Meeting",
    description: "Team standup",
    start: "2024-01-01T09:00:00",
    end: "2024-01-01T09:30:00",
    location: "Conference Room"
  }
}
```
