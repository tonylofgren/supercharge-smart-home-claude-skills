# Subflows in Node-RED

Create reusable node sequences.

## What is a Subflow?

A subflow is a collection of nodes packaged as a single reusable node. It appears in the palette like any other node.

**Use cases:**
- Debounce logic used in multiple places
- Standard notification formatting
- Common data transformations
- Retry patterns

## Creating a Subflow

### Method 1: From Selection

1. Select nodes to include
2. Menu → Subflows → Selection to Subflow
3. Name the subflow
4. Double-click the new subflow in palette to edit

### Method 2: Empty Subflow

1. Menu → Subflows → Create Subflow
2. Double-click to open editor
3. Add nodes inside

## Subflow Structure

```
┌─────────────────────────────────────────────┐
│  Subflow: Debounce                          │
│                                             │
│  [input] ──> [function] ──> [trigger] ──>   │
│     │                            │          │
│  (in 0)                      (out 0)        │
└─────────────────────────────────────────────┘
```

### Input Node

Connect external wires to subflow input. Access in function:
```javascript
// msg comes from whatever is connected to the subflow
msg.payload // incoming data
```

### Output Node

Connect internal wires to output. Multiple outputs supported:
```javascript
// Function with 2 outputs
return [successMsg, errorMsg];
```

## Environment Variables

### Defining Variables

1. Open subflow editor
2. Click "edit properties" (top right)
3. Add environment variables

Example properties:
```
Name: TIMEOUT
Type: number
Default: 5000
UI Label: Timeout (ms)
```

### Using in Function Nodes

```javascript
// Access environment variable
const timeout = env.get('TIMEOUT') || 5000;
const entityId = env.get('ENTITY_ID');

// Use in logic
if (env.get('DEBUG_MODE')) {
  node.warn(`Processing: ${msg.payload}`);
}
```

### Variable Types

| Type | Example | Notes |
|------|---------|-------|
| string | `"light.room"` | Default type |
| number | `5000` | Auto-parsed |
| boolean | `true` | Checkbox in UI |
| json | `{"a":1}` | Parsed to object |
| env | `${MY_VAR}` | From parent env |
| msg | `msg.payload` | From incoming message |
| flow | `flow.setting` | From flow context |
| global | `global.config` | From global context |

## Subflow Status

Show status on subflow instances:

```javascript
// In function node inside subflow
node.status({ fill: "green", shape: "dot", text: "active" });
```

This status appears on every instance of the subflow.

## Debounce Subflow Example

### Subflow Definition

Environment variables:
- `DEBOUNCE_MS`: number, default 1000
- `PASS_FIRST`: boolean, default false

Internal flow:
```
[input] ──> [function: Debounce Logic] ──> [output]
```

Function node:
```javascript
const debounceMs = env.get('DEBOUNCE_MS') || 1000;
const passFirst = env.get('PASS_FIRST') || false;

const key = msg.topic || 'default';
const contextKey = `debounce_${key}`;

const lastTime = context.get(contextKey);
const now = Date.now();

if (lastTime === undefined && passFirst) {
  // First message, pass through
  context.set(contextKey, now);
  return msg;
}

if (lastTime && (now - lastTime) < debounceMs) {
  // Within debounce window, block
  return null;
}

// Outside window or first message
context.set(contextKey, now);
return msg;
```

### Usage

```json
{
  "type": "subflow:debounce_subflow_id",
  "name": "Debounce Motion",
  "env": [
    { "name": "DEBOUNCE_MS", "value": "5000" },
    { "name": "PASS_FIRST", "value": "true" }
  ]
}
```

## Retry Subflow Example

### Environment Variables

- `MAX_RETRIES`: number, default 3
- `INITIAL_DELAY`: number, default 1000
- `BACKOFF_MULTIPLIER`: number, default 2

### Internal Flow

```
[input] ──> [function: Init] ──> [output 0: Try]
                                       │
[input 1: Error] ──> [function: Retry] ┴──> [delay] ──> [loop back to output 0]
                           │
                      [output 1: Failed]
```

Init function:
```javascript
msg._retryCount = 0;
msg._maxRetries = env.get('MAX_RETRIES') || 3;
msg._initialDelay = env.get('INITIAL_DELAY') || 1000;
msg._backoffMultiplier = env.get('BACKOFF_MULTIPLIER') || 2;
return msg;
```

Retry function:
```javascript
msg._retryCount = (msg._retryCount || 0) + 1;

if (msg._retryCount >= msg._maxRetries) {
  // Max retries reached
  msg.error = `Failed after ${msg._retryCount} attempts`;
  node.status({ fill: "red", shape: "dot", text: "failed" });
  return [null, msg]; // Output 1: Failed
}

// Calculate delay with exponential backoff
const delay = msg._initialDelay * Math.pow(msg._backoffMultiplier, msg._retryCount - 1);
msg._delay = delay;

node.status({
  fill: "yellow",
  shape: "ring",
  text: `retry ${msg._retryCount}/${msg._maxRetries}`
});

return [msg, null]; // Output 0: Retry
```

## Notification Subflow Example

### Environment Variables

- `NOTIFY_SERVICE`: string, default "notify.mobile_app"
- `DEFAULT_PRIORITY`: string, default "normal"
- `INCLUDE_TIMESTAMP`: boolean, default true

### Function Node

```javascript
const service = env.get('NOTIFY_SERVICE') || 'notify.mobile_app';
const defaultPriority = env.get('DEFAULT_PRIORITY') || 'normal';
const includeTimestamp = env.get('INCLUDE_TIMESTAMP');

const title = msg.title || 'Notification';
let message = msg.message || msg.payload;
const priority = msg.priority || defaultPriority;

if (includeTimestamp) {
  const time = new Date().toLocaleTimeString('sv-SE');
  message = `[${time}] ${message}`;
}

msg.payload = {
  action: service,
  data: {
    title: title,
    message: message,
    data: {
      priority: priority
    }
  }
};

return msg;
```

## Subflow Best Practices

### Do

- **Clear naming**: Describe what it does
- **Document variables**: Add descriptions
- **Set defaults**: Handle missing config
- **Show status**: Visual feedback
- **Handle errors**: Graceful failure

### Don't

- **Too many variables**: Keep it focused
- **Hard-coded values**: Use env vars
- **Complex branching**: Split into multiple subflows
- **Stateful without cleanup**: Clear context appropriately

## Subflow Instance Configuration

When placing a subflow, configure per-instance:

```json
{
  "type": "subflow:abc123",
  "name": "Motion Debounce",
  "env": [
    { "name": "DEBOUNCE_MS", "value": "3000" }
  ]
}
```

Each instance can have different settings.

## Nested Subflows

Subflows can contain other subflows, but:
- Avoid deep nesting (2 levels max)
- Consider performance
- Keep dependencies clear

## Exporting Subflows

### Export

1. Menu → Export → Select subflow tab
2. Download JSON

### Import

1. Menu → Import
2. Paste/upload JSON
3. Subflow appears in palette

### Sharing

When sharing subflows:
- Include documentation
- Test on clean Node-RED install
- List dependencies (external nodes)
- Provide example usage

## Subflow Template

```json
{
  "id": "subflow_template",
  "type": "subflow",
  "name": "My Subflow",
  "info": "Description of what this subflow does.\n\n## Usage\n\nExplain how to use it.\n\n## Variables\n\n- VAR1: Description",
  "category": "home assistant",
  "in": [{ "x": 50, "y": 50, "wires": [{"id": "node1"}] }],
  "out": [{ "x": 350, "y": 50, "wires": [{"id": "node2", "port": 0}] }],
  "env": [
    {
      "name": "TIMEOUT",
      "type": "num",
      "value": "5000",
      "ui": {
        "label": { "en-US": "Timeout (ms)" },
        "type": "spinner",
        "opts": { "min": 100, "max": 60000 }
      }
    }
  ],
  "color": "#87CEEB",
  "icon": "font-awesome/fa-clock-o"
}
```
