# Node-RED Core Concepts

Fundamental concepts for working with Node-RED.

## Flows, Nodes, and Wires

### Flow

A flow is a collection of connected nodes on a single tab. Each tab in Node-RED is a separate flow.

```
[Tab: Living Room Lights]
  ├── Motion trigger flow
  ├── Schedule-based flow
  └── Manual control flow
```

### Node

A node is a single unit of functionality. Nodes have:
- **Inputs**: Receive messages (0-1 inputs)
- **Outputs**: Send messages (0-n outputs)
- **Properties**: Configuration options
- **Status**: Visual indicator (dot + text)

### Wire

Wires connect nodes together. Messages flow through wires from output to input.

```
[node1] ──wire──> [node2] ──wire──> [node3]
```

## The Message Object

Every message in Node-RED is a JavaScript object called `msg`.

### Core Properties

| Property | Purpose | Example |
|----------|---------|---------|
| `msg.payload` | Main data | `"on"`, `42`, `{temp: 21}` |
| `msg.topic` | Message category | `"sensors/temperature"` |
| `msg._msgid` | Unique ID | `"abc123.456"` |

### Adding Custom Properties

```javascript
// In function node
msg.customField = "value";
msg.sensor = { name: "Living Room", type: "motion" };
return msg;
```

### Preserving Properties

When modifying `msg.payload`, other properties persist:

```javascript
// Input: { payload: "on", topic: "motion", sensor: "lr" }
msg.payload = { state: msg.payload, time: Date.now() };
return msg;
// Output: { payload: {state:"on",time:123}, topic: "motion", sensor: "lr" }
```

## Message Routing

### Single Output

```
[trigger] ──> [action]
```

Node passes message to single output.

### Multiple Outputs

```
           ┌──> [output 1]
[function] ┼──> [output 2]
           └──> [output 3]
```

In function node:
```javascript
// Send to specific outputs
return [msg, null, null];  // Output 1 only
return [null, msg, null];  // Output 2 only
return [msg, msg, null];   // Outputs 1 and 2
return [msg, msg, msg];    // All outputs
```

### Splitting Messages

```javascript
// Send multiple messages to single output
return [[msg1, msg2, msg3]];

// Send to multiple outputs with multiple messages each
return [[msg1, msg2], [msg3], null];
```

## Context: Storing Data

Node-RED has three context scopes for storing data:

### Node Context

Private to a single node instance.

```javascript
// In function node
context.set('count', 0);
const count = context.get('count');
```

### Flow Context

Shared between all nodes in the same flow (tab).

```javascript
flow.set('lastMotion', Date.now());
const lastMotion = flow.get('lastMotion');
```

### Global Context

Shared across all flows.

```javascript
global.set('homeMode', 'away');
const mode = global.get('homeMode');
```

### Special Global: Home Assistant States

When connected to HA, all states are available:

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const tempState = states["sensor.temperature"];
const temp = parseFloat(tempState.state);
const unit = tempState.attributes.unit_of_measurement;
```

### Persistent Context

By default, context is lost on restart. Enable persistence in settings.js:

```javascript
contextStorage: {
  default: { module: "localfilesystem" }
}
```

## Node Types

### Input Nodes

Start of a flow. No inputs, one or more outputs.

Examples: inject, trigger-state, events-state

```
[inject] ──>
[trigger-state] ──>
```

### Output Nodes

End of a flow. One input, no outputs.

Examples: debug, api-call-service, notify

```
──> [debug]
──> [api-call-service]
```

### Processing Nodes

Transform or route messages. Has both inputs and outputs.

Examples: function, switch, change

```
──> [function] ──>
──> [switch] ──>
```

### Config Nodes

Not visible on canvas. Provide shared configuration.

Examples: server, mqtt-broker, entity-config

## Subflows

Reusable node sequences that act as a single node.

### Creating a Subflow

1. Select nodes to include
2. Menu → Subflows → Selection to Subflow
3. Name the subflow

### Environment Variables

Subflows can have configurable properties:

```javascript
// In subflow function node
const threshold = env.get('THRESHOLD') || 50;
```

Set when using the subflow instance.

## Status Messages

Nodes can display status:

```javascript
// In function node
node.status({ fill: "green", shape: "dot", text: "active" });
node.status({ fill: "red", shape: "ring", text: "error" });
node.status({}); // Clear status
```

### Status Colors and Shapes

| Fill | Meaning |
|------|---------|
| green | Success/Active |
| yellow | Warning |
| red | Error |
| blue | Info |
| grey | Inactive |

| Shape | Meaning |
|-------|---------|
| dot | Filled circle |
| ring | Hollow circle |

## Error Handling

### Throwing Errors

```javascript
// In function node
if (!msg.payload) {
  node.error("No payload", msg);
  return null;
}
```

### Catching Errors

Use the `catch` node to handle errors:

```
[nodes] ──> ... ──> [catch] ──> [error handler]
```

Catch node provides:
- `msg.error.message` - Error text
- `msg.error.source.id` - Node ID that threw error
- `msg.error.source.type` - Node type

### Uncaught Errors

Configure catch node to handle all uncaught errors:

```json
{
  "type": "catch",
  "scope": null,
  "uncaught": true
}
```

## Async Operations

### Async Function Pattern

```javascript
async function process() {
  try {
    const result = await someAsyncOperation();
    msg.payload = result;
    node.send(msg);
  } catch (error) {
    node.error(error.message, msg);
  } finally {
    node.done();
  }
}

process();
return null; // Important: prevent sync output
```

### Key Points

- Use `node.send(msg)` for async output
- Use `node.done()` to signal completion
- Return `null` to prevent immediate output

## Flow Deployment

### Deploy Options

| Mode | Effect |
|------|--------|
| Full | Stops all, deploys all |
| Modified Flows | Only affected flows restart |
| Modified Nodes | Only changed nodes restart |

### When to Use Full Deploy

- After changing config nodes
- After changing subflows
- When experiencing issues

## Best Practices

1. **Name all nodes** - Makes debugging easier
2. **Use comment nodes** - Document complex logic
3. **Group related nodes** - Visual organization
4. **Limit function node size** - Extract to subflows
5. **Test incrementally** - Add debug nodes during development
6. **Use consistent naming** - `sensor_name` or `sensorName`, pick one
7. **Handle errors** - Add catch nodes to critical flows
8. **Clean up context** - Don't store unlimited history
