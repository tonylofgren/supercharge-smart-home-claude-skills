# Node Types Reference

## Table of Contents
- [Node Categories](#node-categories)
- [Input Nodes](#input-nodes)
- [Output Nodes](#output-nodes)
- [Function Nodes](#function-nodes)
- [Flow Control Nodes](#flow-control-nodes)
- [Configuration Nodes](#configuration-nodes)
- [Storage Nodes](#storage-nodes)
- [Network Nodes](#network-nodes)
- [Parser Nodes](#parser-nodes)

---

## Node Categories

### By Function

| Category | Purpose | Examples |
|----------|---------|----------|
| **Input** | Receive data/events | Inject, HTTP In, MQTT In |
| **Output** | Send data/display | Debug, HTTP Response |
| **Processing** | Transform data | Function, Change, Switch |
| **Flow Control** | Route/delay messages | Switch, Delay, Split/Join |
| **Config** | Shared configuration | Server connections |
| **Storage** | Persist data | File, Context |
| **Network** | External communication | HTTP, MQTT, WebSocket |
| **Parser** | Data format conversion | JSON, CSV, XML |

### By Port Configuration

```
Input Only:         Processing:         Output Only:
┌─────────○        ○─────────○         ○─────────┐
│ Inject  │        │ Function │        │  Debug  │
└─────────┘        └──────────┘        └─────────┘
```

---

## Input Nodes

Input nodes have no input port - they generate or receive messages from external sources.

### inject

Manually or automatically trigger a flow.

```javascript
// Configuration
{
  "payload": "timestamp",    // payload type
  "payloadType": "date",     // date, str, num, bool, json, etc.
  "topic": "",
  "repeat": "",              // Interval in seconds
  "crontab": "",             // Cron expression
  "once": false,             // Trigger on deploy
  "onceDelay": 0.1
}
```

**Payload Types:**
| Type | Description |
|------|-------------|
| `date` | Current timestamp (ms) |
| `str` | String value |
| `num` | Number value |
| `bool` | Boolean value |
| `json` | JSON object |
| `flow` | Flow context variable |
| `global` | Global context variable |
| `env` | Environment variable |

**Cron Examples:**
```
0 8 * * *      # Daily at 8:00 AM
*/5 * * * *    # Every 5 minutes
0 0 * * 0      # Weekly on Sunday midnight
0 9-17 * * 1-5 # Weekdays 9 AM - 5 PM, hourly
```

### http in

Create HTTP endpoints.

```javascript
// Configuration
{
  "url": "/api/webhook",
  "method": "post",    // get, post, put, delete, patch
  "upload": false,     // Accept file uploads
  "swaggerDoc": ""     // API documentation
}

// Output message
msg = {
  payload: { /* request body */ },
  req: {
    params: {},        // URL parameters
    query: {},         // Query string
    body: {},          // POST body
    headers: {},       // HTTP headers
    cookies: {}        // Cookies
  },
  res: { /* response object */ }
}
```

### mqtt in

Subscribe to MQTT topics.

```javascript
// Configuration
{
  "topic": "home/+/temperature",  // + single level, # multi level
  "qos": "2",
  "datatype": "auto",  // auto, utf8, buffer, json
  "broker": "mqtt-broker-config"
}
```

### websocket in

Receive WebSocket messages.

```javascript
// Configuration
{
  "path": "/ws/updates",
  "wholemsg": "false"  // true = entire msg, false = payload only
}
```

---

## Output Nodes

Output nodes have no output port - they send data or display results.

### debug

Display messages in the debug sidebar.

```javascript
// Configuration
{
  "active": true,
  "tosidebar": true,    // Show in debug panel
  "console": false,     // Log to Node-RED console
  "tostatus": false,    // Show in node status
  "complete": "payload" // What to show: "payload", "true" (full msg), or JSONata
}
```

**Debug Tips:**
- Use `complete: "true"` to see entire message
- Use `tostatus: true` to see values without opening sidebar
- Use JSONata expressions for complex objects

### http response

Send HTTP responses (pair with http in).

```javascript
// Function node before http response
msg.statusCode = 200;
msg.headers = {
  "Content-Type": "application/json",
  "X-Custom-Header": "value"
};
msg.payload = { success: true, data: result };
return msg;
```

### mqtt out

Publish to MQTT topics.

```javascript
// Configuration
{
  "topic": "home/living/light/set",
  "qos": "2",
  "retain": "false"
}

// Dynamic topic via message
msg.topic = "home/bedroom/light/set";
msg.payload = "ON";
```

---

## Function Nodes

### function

Execute custom JavaScript code.

```javascript
// Setup tab (runs once on deploy)
// Initialize variables, load modules
const moment = global.get('moment');
context.set('counter', 0);

// On Message tab (runs for each message)
const count = context.get('counter') || 0;
context.set('counter', count + 1);

msg.payload = {
  original: msg.payload,
  count: count + 1,
  timestamp: Date.now()
};

return msg;

// On Stop tab (runs on redeploy)
// Cleanup resources
```

**Available Objects:**
| Object | Description |
|--------|-------------|
| `msg` | Current message |
| `node` | Current node (for status, warn, error) |
| `context` | Node context |
| `flow` | Flow context |
| `global` | Global context |
| `env` | Environment variables |
| `RED` | Node-RED API |

**Function Patterns:**
```javascript
// Multiple outputs
return [msg, null];          // Send to output 1
return [null, msg];          // Send to output 2
return [[msg1, msg2], null]; // Multiple to output 1

// Drop message
return null;

// Async operation
node.send(msg);
return null; // Don't auto-send

// Clone message
const newMsg = RED.util.cloneMessage(msg);

// Log messages
node.log("Info message");
node.warn("Warning message");
node.error("Error message", msg); // Triggers catch node

// Set status
node.status({fill:"green", shape:"dot", text:"OK"});
```

### change

Modify message properties without code.

```javascript
// Configuration - Rules array
[
  // Set a property
  {"t": "set", "p": "payload", "pt": "msg", "to": "Hello", "tot": "str"},

  // Change a property
  {"t": "change", "p": "payload", "pt": "msg",
   "from": "old", "fromt": "str", "to": "new", "tot": "str"},

  // Move a property
  {"t": "move", "p": "payload", "pt": "msg", "to": "data", "tot": "msg"},

  // Delete a property
  {"t": "delete", "p": "temp", "pt": "msg"}
]
```

**Property Types (pt/tot):**
- `msg` - Message property
- `flow` - Flow context
- `global` - Global context
- `str` - String
- `num` - Number
- `bool` - Boolean
- `json` - JSON
- `jsonata` - JSONata expression
- `env` - Environment variable

### template

Generate text using Mustache templates.

```javascript
// Template
"Hello {{payload.name}}!
Your temperature is {{payload.temp}}°C.
{{#payload.warning}}
WARNING: Temperature is high!
{{/payload.warning}}"

// Input
msg.payload = { name: "User", temp: 25, warning: false };

// Output
msg.payload = "Hello User!\nYour temperature is 25°C.\n"
```

---

## Flow Control Nodes

### switch

Route messages based on conditions.

```javascript
// Configuration
{
  "property": "payload",      // Property to evaluate
  "propertyType": "msg",
  "rules": [
    {"t": "eq", "v": "on", "vt": "str"},     // equals
    {"t": "neq", "v": "off", "vt": "str"},   // not equals
    {"t": "lt", "v": "10", "vt": "num"},     // less than
    {"t": "lte", "v": "10", "vt": "num"},    // less than or equal
    {"t": "gt", "v": "10", "vt": "num"},     // greater than
    {"t": "gte", "v": "10", "vt": "num"},    // greater than or equal
    {"t": "btwn", "v": "1", "v2": "10"},     // between
    {"t": "cont", "v": "error"},             // contains
    {"t": "regex", "v": "^test"},            // regex match
    {"t": "true"},                            // is true
    {"t": "false"},                           // is false
    {"t": "null"},                            // is null
    {"t": "nnull"},                           // is not null
    {"t": "istype", "v": "string"},          // type check
    {"t": "else"}                             // otherwise
  ],
  "checkall": "true",    // Check all rules vs stop at first match
  "repair": false        // Repair sequences
}
```

### delay

Add delays or rate limiting.

```javascript
// Delay mode
{
  "pauseType": "delay",
  "timeout": "5",
  "timeoutUnits": "seconds"
}

// Rate limit mode
{
  "pauseType": "rate",
  "rate": "1",
  "rateUnits": "second",
  "drop": true  // Drop messages exceeding rate
}

// Queue all mode
{
  "pauseType": "queue",
  "timeout": "1",
  "timeoutUnits": "seconds"
}
```

### trigger

Output messages at intervals or on trigger.

```javascript
// Configuration
{
  "send": "1",              // Send this initially
  "reset": "",              // Reset trigger on this value
  "duration": "250",        // Then wait this long
  "extend": false,          // Extend timer on new message
  "units": "ms",
  "outputType": "msg",
  "output2Type": "payl",
  "output2": "0"           // Send this after duration
}
```

### split

Split arrays or strings into individual messages.

```javascript
// Input
msg.payload = ["a", "b", "c"];

// Output (3 messages)
msg.payload = "a"; msg.parts = {index: 0, count: 3};
msg.payload = "b"; msg.parts = {index: 1, count: 3};
msg.payload = "c"; msg.parts = {index: 2, count: 3};
```

### join

Combine messages into arrays or objects.

```javascript
// Configuration - Modes
{
  "mode": "auto",      // auto, custom, reduce
  "build": "array",    // array, string, buffer, object
  "count": "",         // Number of messages to join
  "timeout": "",       // Timeout in seconds
  "propertyType": "msg",
  "property": "payload"
}

// Auto mode - reverses split
// Custom mode - manual configuration
// Reduce mode - accumulate with expression
```

### sort

Sort message sequences.

```javascript
// Configuration
{
  "target": "payload",
  "targetType": "msg",
  "msgKey": "payload",
  "msgKeyType": "elem",
  "order": "ascending"
}
```

### batch

Create message batches.

```javascript
// Configuration
{
  "mode": "count",     // count, interval, concat
  "count": 10,         // Messages per batch
  "interval": "",      // Interval mode: seconds
  "overlap": 0,        // Sliding window overlap
  "allowEmptySequence": false
}
```

---

## Configuration Nodes

Configuration nodes don't appear in flows - they store shared settings.

### Common Config Nodes

| Node | Purpose |
|------|---------|
| `mqtt-broker` | MQTT server connection |
| `http-proxy` | HTTP proxy settings |
| `tls-config` | TLS/SSL certificates |
| `server` | Home Assistant connection |

### Accessing Config Nodes

```javascript
// In function node
const configNode = RED.nodes.getNode("config-node-id");
if (configNode) {
  const setting = configNode.someSetting;
}
```

---

## Storage Nodes

### file

Read/write files.

```javascript
// Write file
{
  "filename": "/data/output.txt",
  "appendNewline": true,
  "overwriteFile": "true"  // true, false, delete
}

// Read file
{
  "filename": "/data/input.txt",
  "format": "utf8",        // utf8, lines, stream
  "sendError": false
}
```

### file in

Watch files for changes.

```javascript
// Watch mode
{
  "filename": "/data/config.json",
  "format": "utf8"
}
```

---

## Network Nodes

### http request

Make HTTP requests.

```javascript
// Configuration
{
  "method": "GET",
  "url": "https://api.example.com/data",
  "tls": "",
  "persist": false,
  "proxy": "",
  "ret": "obj",           // txt, bin, obj (JSON)
  "authType": "basic"     // basic, digest, bearer
}

// Dynamic configuration via message
msg.url = "https://api.example.com/users/" + msg.userId;
msg.method = "POST";
msg.headers = { "Authorization": "Bearer " + token };
msg.payload = { name: "John" };
```

### tcp in / tcp out

Raw TCP communication.

### udp in / udp out

UDP packet communication.

---

## Parser Nodes

### json

Parse/stringify JSON.

```javascript
// String to Object
msg.payload = '{"name":"John"}';
// Output: msg.payload = { name: "John" }

// Object to String
msg.payload = { name: "John" };
// Output: msg.payload = '{"name":"John"}'
```

### xml

Parse/generate XML.

```javascript
// XML to Object
msg.payload = '<person><name>John</name></person>';
// Output: msg.payload = { person: { name: "John" } }
```

### csv

Parse/generate CSV.

```javascript
// Configuration
{
  "sep": ",",
  "hdrin": true,    // First row is header
  "hdrout": "all",  // Include header in output
  "multi": "one"    // one message per row
}
```

### yaml

Parse/generate YAML.

---

## Node Status Reference

Common status indicators:

```javascript
// Connected/OK
node.status({fill:"green", shape:"dot", text:"connected"});

// Disconnected/Error
node.status({fill:"red", shape:"ring", text:"disconnected"});

// Processing
node.status({fill:"yellow", shape:"ring", text:"processing"});

// Idle
node.status({fill:"grey", shape:"dot", text:"idle"});

// With data
node.status({fill:"blue", shape:"dot", text:`${count} items`});

// Clear status
node.status({});
```

---

## Related References

- [Core Concepts](core-concepts.md) - Flows, wires, messages
- [Message Handling](message-handling.md) - Working with msg object
- [Function Nodes](function-nodes.md) - JavaScript in Node-RED
- [HA Trigger Nodes](ha-trigger-nodes.md) - Home Assistant specific
