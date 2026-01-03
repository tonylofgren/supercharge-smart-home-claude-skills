# Node Types in Node-RED

Understanding the different categories of nodes.

## Node Categories

### Input Nodes

Generate or receive messages.

| Node | Purpose |
|------|---------|
| `inject` | Manual/scheduled trigger |
| `http in` | HTTP endpoint |
| `mqtt in` | MQTT subscriber |
| `websocket in` | WebSocket receiver |
| `trigger-state` | HA state change (recommended) |
| `events:state` | HA state events |
| `poll-state` | HA periodic state check |

### Output Nodes

Send messages out of Node-RED.

| Node | Purpose |
|------|---------|
| `debug` | Display in sidebar |
| `http response` | HTTP reply |
| `mqtt out` | MQTT publisher |
| `api-call-service` | HA service calls |
| `fire-event` | HA custom events |

### Function Nodes

Transform or process messages.

| Node | Purpose |
|------|---------|
| `function` | JavaScript code |
| `change` | Set/delete properties |
| `switch` | Route messages |
| `template` | Mustache templates |
| `json` | Parse/stringify JSON |

### Config Nodes

Shared configuration (not visible in flow).

| Node | Purpose |
|------|---------|
| `server` | HA connection |
| `mqtt-broker` | MQTT connection |
| `http proxy` | Proxy settings |
| `tls-config` | TLS certificates |

---

## Input Nodes

### inject

Manual button or scheduled trigger.

```json
{
  "type": "inject",
  "repeat": "3600",
  "crontab": "0 8 * * *",
  "once": true,
  "onceDelay": 0.1,
  "payload": "trigger",
  "payloadType": "str"
}
```

Payload types:
- `str` - String
- `num` - Number
- `bool` - Boolean
- `json` - JSON object
- `date` - Timestamp
- `flow` - Flow context
- `global` - Global context
- `env` - Environment variable

### http in

Create HTTP endpoints.

```json
{
  "type": "http in",
  "method": "post",
  "url": "/api/trigger",
  "upload": false
}
```

Methods: `get`, `post`, `put`, `delete`, `patch`

### mqtt in

Subscribe to MQTT topics.

```json
{
  "type": "mqtt in",
  "topic": "home/+/temperature",
  "qos": "0",
  "datatype": "json"
}
```

Wildcards:
- `+` - Single level
- `#` - Multi level

### websocket in

Receive WebSocket messages.

```json
{
  "type": "websocket in",
  "server": "ws-server-config",
  "path": "/ws"
}
```

---

## Output Nodes

### debug

Display messages in debug sidebar.

```json
{
  "type": "debug",
  "active": true,
  "tosidebar": true,
  "console": false,
  "complete": "payload",
  "tostatus": true,
  "statusType": "auto"
}
```

Output options:
- `msg.payload` - Just payload
- `complete msg object` - Everything
- Property path - Specific property

### http response

Reply to HTTP requests.

```json
{
  "type": "http response",
  "statusCode": "200"
}
```

Set in function node:
```javascript
msg.statusCode = 200;
msg.payload = { status: "ok" };
return msg;
```

### mqtt out

Publish MQTT messages.

```json
{
  "type": "mqtt out",
  "topic": "home/status",
  "qos": "0",
  "retain": "false"
}
```

Dynamic topic:
```javascript
msg.topic = `home/${room}/status`;
msg.payload = "active";
return msg;
```

---

## Function Nodes

### function

JavaScript processing.

```json
{
  "type": "function",
  "func": "msg.payload = msg.payload.toUpperCase();\nreturn msg;",
  "outputs": 1,
  "initialize": "",
  "finalize": ""
}
```

Lifecycle:
- `initialize` - Runs once on deploy
- `func` - Runs for each message
- `finalize` - Runs on redeploy/close

### change

Modify message properties without code.

```json
{
  "type": "change",
  "rules": [
    { "t": "set", "p": "topic", "pt": "msg", "to": "temperature", "tot": "str" },
    { "t": "delete", "p": "data", "pt": "msg" },
    { "t": "move", "p": "payload.temp", "pt": "msg", "to": "temperature", "tot": "msg" }
  ]
}
```

Operations:
- `set` - Set value
- `change` - Find/replace
- `delete` - Remove property
- `move` - Rename property

### switch

Route messages based on rules.

```json
{
  "type": "switch",
  "property": "payload",
  "rules": [
    { "t": "lt", "v": "10", "vt": "num" },
    { "t": "btwn", "v": "10", "vt": "num", "v2": "20", "v2t": "num" },
    { "t": "gt", "v": "20", "vt": "num" },
    { "t": "else" }
  ],
  "checkall": "true"
}
```

Rule types:
- `eq` - Equal
- `neq` - Not equal
- `lt` - Less than
- `lte` - Less than or equal
- `gt` - Greater than
- `gte` - Greater than or equal
- `btwn` - Between
- `cont` - Contains
- `regex` - Matches regex
- `istype` - Type check
- `empty` - Is empty
- `null` - Is null
- `nnull` - Not null
- `else` - Otherwise

### template

Mustache templating.

```json
{
  "type": "template",
  "template": "Temperature is {{payload}}°C",
  "output": "str"
}
```

Syntax:
- `{{property}}` - Insert value
- `{{#array}}...{{/array}}` - Loop
- `{{^value}}...{{/value}}` - If not
- `{{{html}}}` - No escape

### json

Parse or stringify JSON.

```json
{
  "type": "json",
  "action": "obj",
  "property": "payload"
}
```

Actions:
- `obj` - String → Object
- `str` - Object → String
- `` (empty) - Toggle

---

## Flow Control

### delay

Pause or rate limit.

```json
{
  "type": "delay",
  "pauseType": "delay",
  "timeout": "5",
  "timeoutUnits": "seconds"
}
```

Pause types:
- `delay` - Fixed delay
- `delayv` - Variable (from msg.delay)
- `rate` - Rate limit
- `timed` - Release on schedule
- `random` - Random delay

### trigger

Timer with reset capability.

```json
{
  "type": "trigger",
  "op1": "on",
  "op2": "off",
  "duration": "5",
  "extend": true,
  "units": "min"
}
```

Key setting: `extend: true` resets timer on new message.

### split

Break array/string into messages.

```json
{
  "type": "split",
  "splt": "\\n",
  "arraySplt": 1
}
```

### join

Combine messages.

```json
{
  "type": "join",
  "mode": "custom",
  "count": "10",
  "build": "array"
}
```

Build types:
- `array` - Array of payloads
- `object` - Object with topics as keys
- `string` - Concatenated string
- `buffer` - Binary buffer
- `merged` - Merged object

### batch

Group messages.

```json
{
  "type": "batch",
  "mode": "count",
  "count": "5"
}
```

Modes:
- `count` - Every N messages
- `interval` - Every N time units
- `concat` - Until topic changes

---

## Context Storage Nodes

### link in / link out

Connect flows without wires.

```json
{
  "type": "link in",
  "links": ["link-out-id"]
}
```

Can link across tabs.

### subflow

Reusable flow component.

Properties:
- Name and category
- Environment variables
- Input/output count
- Icon and color

---

## Utility Nodes

### comment

Documentation in flow.

```json
{
  "type": "comment",
  "info": "Markdown description here"
}
```

### catch

Handle errors.

```json
{
  "type": "catch",
  "scope": ["node-id-1", "node-id-2"],
  "uncaught": false
}
```

Scope options:
- Specific nodes
- All nodes in flow
- Uncaught only

### status

Monitor node status.

```json
{
  "type": "status",
  "scope": ["node-id-1"]
}
```

### complete

Trigger when node completes.

```json
{
  "type": "complete",
  "scope": ["node-id-1"]
}
```

---

## Home Assistant Node Types

### Trigger Nodes

| Node | When to Use |
|------|-------------|
| `trigger-state` | State changes (recommended) |
| `events:state` | All state events |
| `device` | Device triggers |
| `time` | Time-based |
| `zone` | Location-based |
| `tag` | NFC tags |
| `sentence` | Voice commands |
| `webhook` | External webhooks |

### Action Nodes

| Node | When to Use |
|------|-------------|
| `api-call-service` | Call HA services |
| `fire-event` | Fire custom events |
| `api` | Direct HA API calls |

### State Nodes

| Node | When to Use |
|------|-------------|
| `api-current-state` | Get single entity state |
| `get-entities` | Query multiple entities |
| `get-history` | Historical data |
| `poll-state` | Periodic state check |
| `wait-until` | Wait for state condition |
| `render-template` | Evaluate HA template |

### Entity Nodes

| Node | Creates |
|------|---------|
| `entity` | Generic entity |
| `sensor` | Sensor entity |
| `binary-sensor` | Binary sensor |
| `switch` | Switch entity |
| `button` | Button entity |
| `number` | Number input |
| `select` | Select input |
| `text` | Text input |
| `time` | Time input |

---

## Node Status

Nodes can show status below them.

### In Function Node

```javascript
node.status({ fill: "green", shape: "dot", text: "active" });
node.status({ fill: "yellow", shape: "ring", text: "waiting" });
node.status({ fill: "red", shape: "dot", text: "error" });
node.status({});  // Clear status
```

### Fill Colors

- `red` - Error
- `yellow` - Warning
- `green` - OK
- `blue` - Info
- `grey` - Inactive

### Shapes

- `dot` - Filled circle
- `ring` - Empty circle

---

## Node Properties

### Common Properties

| Property | Purpose |
|----------|---------|
| `id` | Unique identifier |
| `type` | Node type |
| `name` | Display name |
| `z` | Parent flow ID |
| `x`, `y` | Position |
| `wires` | Output connections |

### Wire Format

```json
{
  "wires": [
    ["node-id-1", "node-id-2"],  // Output 1 connections
    ["node-id-3"]                 // Output 2 connections
  ]
}
```

---

## Quick Reference

### Node Selection by Use Case

| Use Case | Recommended Nodes |
|----------|-------------------|
| State change | `trigger-state` |
| Scheduled | `inject` with crontab |
| Transform data | `function` or `change` |
| Route messages | `switch` |
| Call HA service | `api-call-service` |
| Debug | `debug` with status |
| Wait | `delay` or `wait-until` |
| Timer with reset | `trigger` with `extend` |
| Error handling | `catch` |

### Node Palette Categories

| Category | Purpose |
|----------|---------|
| Common | inject, debug, function, template |
| Network | http, mqtt, websocket |
| Sequence | split, join, sort, batch |
| Parser | json, xml, csv, html |
| Storage | file, watch |
| Home Assistant | All HA-specific nodes |

