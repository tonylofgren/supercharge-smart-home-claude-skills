# Node-RED Home Assistant Nodes Reference

Complete reference for node-red-contrib-home-assistant-websocket v0.65+

## Node Type Quick Reference

| Category | Node Name | Type (for JSON) | Purpose |
|----------|-----------|-----------------|---------|
| **Trigger** | Trigger: state | `trigger-state` | State change with conditions |
| **Trigger** | Events: state | `events-state` | Simple state change events |
| **Trigger** | Events: all | `events-all` | Listen to any HA event |
| **Trigger** | Events: calendar | `events-calendar` | Calendar event start/end |
| **Trigger** | Device | `ha-device` | Device automations |
| **Trigger** | Time | `ha-time` | Date/time triggers |
| **Trigger** | Zone | `ha-zone` | Enter/exit zones |
| **Trigger** | Tag | `ha-tag` | NFC/barcode scans |
| **Trigger** | Sentence | `ha-sentence` | Voice commands (Assist) |
| **Trigger** | Webhook | `ha-webhook` | HTTP webhook triggers |
| **State** | Current State | `api-current-state` | Get entity state |
| **State** | Get Entities | `ha-get-entities` | Query multiple entities |
| **State** | Get History | `api-get-history` | Historical data |
| **State** | Poll State | `poll-state` | Periodic state polling |
| **State** | Wait Until | `ha-wait-until` | Wait for condition |
| **Action** | Action | `api-call-service` | Call HA services |
| **Action** | Fire Event | `ha-fire-event` | Fire custom events |
| **Action** | API | `ha-api` | Raw API access |
| **Action** | Render Template | `api-render-template` | Jinja2 templates |
| **Entity** | Sensor | `ha-sensor` | Create sensor |
| **Entity** | Binary Sensor | `ha-binary-sensor` | Create binary sensor |
| **Entity** | Switch | `ha-switch` | Create switch |
| **Entity** | Button | `ha-button` | Create button |
| **Entity** | Number | `ha-number` | Create number |
| **Entity** | Select | `ha-select` | Create dropdown |
| **Entity** | Text | `ha-text` | Create text input |
| **Entity** | Time Entity | `ha-time-entity` | Create time |
| **Entity** | Entity | `ha-entity` | Generic entity |
| **Entity** | Update Config | `ha-entity-config` | Update entity |
| **Config** | Server Config | `server` | HA connection |
| **Config** | Device Config | `ha-device-config` | Device settings |
| **Config** | Entity Config | `ha-entity-config` | Entity settings |

## Trigger Nodes

### trigger-state

Advanced state change trigger with conditions.

```json
{
  "type": "trigger-state",
  "entityId": "binary_sensor.motion",
  "entityIdType": "exact",
  "constraints": [
    {
      "targetType": "this_entity",
      "propertyType": "current_state",
      "comparatorType": "is",
      "comparatorValue": "on"
    }
  ],
  "outputs": 2,
  "outputProperties": [
    {
      "property": "payload",
      "propertyType": "msg",
      "value": "",
      "valueType": "entityState"
    }
  ]
}
```

**Key Properties:**
- `entityIdType`: `exact`, `substring`, `regex` (NO `list` type!)
- `outputs`: 1 (all) or 2 (matched/unmatched)
- `constraints`: Array of conditions

### events-state

Simple state change listener.

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

**Note:** Despite the UI name "Events: state", the node type in JSON is `server-state-changed`.

### ha-time

Time-based triggers.

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

### ha-zone

Zone enter/exit detection.

```json
{
  "type": "ha-zone",
  "entities": ["person.john"],
  "zones": ["zone.home"],
  "event": "enter",
  "outputs": 2
}
```

**event options:** `enter`, `leave`, `enter_leave`

## State Nodes

### api-current-state

Get current state of ONE entity.

```json
{
  "type": "api-current-state",
  "entity_id": "sensor.temperature",
  "stateType": "str",
  "blockInputOverrides": false
}
```

**IMPORTANT:** Only accepts single entity_id, not patterns!

### ha-get-entities

Query multiple entities.

```json
{
  "type": "ha-get-entities",
  "rules": [
    {
      "property": "entity_id",
      "logic": "starts_with",
      "value": "light."
    },
    {
      "property": "state",
      "logic": "is",
      "value": "on"
    }
  ],
  "outputType": "array"
}
```

**rule.logic options:** `is`, `is_not`, `lt`, `lte`, `gt`, `gte`, `starts_with`, `ends_with`, `in`, `includes`, `contains`, `does_not_contain`, `in_group`, `jsonata`, `regex`

### poll-state

Periodic state polling.

```json
{
  "type": "poll-state",
  "entity_id": "sensor.power",
  "updateInterval": 60,
  "updateIntervalUnits": "seconds",
  "outputInitially": true,
  "stateType": "num"
}
```

### ha-wait-until

Wait for condition or timeout.

```json
{
  "type": "ha-wait-until",
  "entityId": "binary_sensor.door",
  "entityIdType": "exact",
  "property": "state",
  "comparator": "is",
  "value": "off",
  "valueType": "str",
  "timeout": 30,
  "timeoutUnits": "seconds",
  "checkCurrentState": true,
  "blockInputOverrides": false
}
```

## Action Nodes

### api-call-service

Call Home Assistant services.

```json
{
  "type": "api-call-service",
  "domain": "light",
  "service": "turn_on",
  "entityId": ["light.living_room"],
  "data": "{\"brightness_pct\": 80}",
  "dataType": "json"
}
```

**Dynamic via msg:**
```json
{
  "type": "api-call-service",
  "domain": "",
  "service": "",
  "data": "",
  "dataType": "msg"
}
```

With function node:
```javascript
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness_pct: 80 }
};
return msg;
```

### ha-fire-event

Fire events on HA event bus.

```json
{
  "type": "ha-fire-event",
  "event": "custom_event",
  "data": "{\"key\": \"value\"}",
  "dataType": "json"
}
```

### api-render-template

Render Jinja2 templates.

```json
{
  "type": "api-render-template",
  "template": "{{ states('sensor.temperature') }}°C",
  "resultsLocation": "payload",
  "resultsLocationType": "msg"
}
```

## Entity Nodes

**IMPORTANT:** Entity nodes require the `node-red` integration in Home Assistant (HACS). This is separate from the websocket connection!

### ha-sensor

Create sensor entity.

```json
{
  "type": "ha-sensor",
  "entityConfig": "entity_config_node_id",
  "state": "msg.payload",
  "stateType": "msg",
  "attributes": [],
  "resend": true,
  "outputLocation": "payload",
  "outputLocationType": "msg"
}
```

### ha-binary-sensor

Create binary sensor.

```json
{
  "type": "ha-binary-sensor",
  "entityConfig": "entity_config_node_id",
  "state": "msg.payload",
  "stateType": "msg",
  "attributes": []
}
```

### ha-switch

Create controllable switch.

```json
{
  "type": "ha-switch",
  "entityConfig": "entity_config_node_id",
  "enableInput": true,
  "outputOnStateChange": true
}
```

## Output Message Structure

Most nodes output messages with this structure:

```javascript
{
  payload: "on",                    // Entity state
  data: {
    entity_id: "light.living_room",
    state: "on",
    attributes: { brightness: 255 },
    last_changed: "2024-01-01T12:00:00Z",
    last_updated: "2024-01-01T12:00:00Z"
  },
  topic: "light.living_room"
}
```

For `trigger-state` and `events-state`:
```javascript
{
  payload: "on",
  data: {
    entity_id: "light.living_room",
    new_state: { /* full state object */ },
    old_state: { /* previous state */ }
  }
}
```

## Accessing Home Assistant States in Function Nodes

```javascript
// Get all states
const states = global.get("homeassistant").homeAssistant.states;

// Get specific entity
const temp = states["sensor.temperature"];

// Check state
if (temp.state === "unavailable") {
  return null;
}

msg.payload = parseFloat(temp.state);
return msg;
```
