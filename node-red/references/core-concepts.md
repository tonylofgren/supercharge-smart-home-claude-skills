# Node-RED Core Concepts

## Table of Contents
- [What is Node-RED](#what-is-node-red)
- [Flows](#flows)
- [Nodes](#nodes)
- [Wires](#wires)
- [Messages](#messages)
- [Workspace Organization](#workspace-organization)
- [Deploy Modes](#deploy-modes)
- [Editor Overview](#editor-overview)

---

## What is Node-RED

Node-RED is a flow-based programming tool that provides a visual editor for wiring together hardware devices, APIs, and online services. It runs on Node.js and uses a browser-based editor.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Visual Programming** | Drag-and-drop nodes, connect with wires |
| **Event-Driven** | Flows triggered by events (messages) |
| **Node.js Based** | Full JavaScript/npm ecosystem available |
| **Extensible** | Thousands of community nodes available |
| **JSON Export** | Flows stored as JSON for version control |

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Node-RED Runtime                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Flow 1    │  │   Flow 2    │  │   Flow 3    │     │
│  │  (Tab 1)    │  │  (Tab 2)    │  │  (Tab 3)    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  Context Store │ Credential Store │ Settings            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │      Node.js Runtime     │
              └─────────────────────────┘
```

---

## Flows

A **Flow** is the basic unit of organization in Node-RED. Each flow corresponds to a tab in the editor.

### Flow Structure

```javascript
// A flow is an array of node objects
[
  {
    "id": "flow1",
    "type": "tab",
    "label": "Motion Lights",
    "disabled": false,
    "info": "Handles motion-triggered lighting"
  },
  {
    "id": "node1",
    "type": "trigger-state",
    "z": "flow1",  // Parent flow ID
    "name": "Motion Sensor",
    // ... node configuration
  }
]
```

### Flow Properties

| Property | Description |
|----------|-------------|
| `id` | Unique identifier |
| `type` | Always "tab" for flows |
| `label` | Display name in editor |
| `disabled` | If true, flow won't execute |
| `info` | Documentation/notes |

### Flow Organization Best Practices

```
Home Automation/
├── Lighting/           # Tab: All lighting automations
│   ├── Motion lights
│   ├── Schedule lights
│   └── Scene manager
├── Climate/            # Tab: HVAC control
│   ├── Temperature
│   └── Humidity
├── Security/           # Tab: Alarms and alerts
│   ├── Door sensors
│   └── Motion alerts
└── Utilities/          # Tab: Helper flows
    ├── Notification hub
    └── Error handler
```

---

## Nodes

A **Node** is the basic building block of Node-RED. Each node has a specific purpose and can receive, process, and send messages.

### Node Anatomy

```
┌─────────────────────────────────────┐
│  ○ Input    [  Node Name  ]  Output ○
│   Port          Body          Port   │
└─────────────────────────────────────┘
```

### Node Types

| Type | Input Ports | Output Ports | Examples |
|------|-------------|--------------|----------|
| **Input** | 0 | 1+ | Inject, HTTP In, MQTT In |
| **Output** | 1 | 0 | Debug, HTTP Response |
| **Processing** | 1 | 1+ | Function, Switch, Change |
| **Config** | - | - | Server, Credentials |

### Node Properties

```javascript
{
  "id": "abc123",           // Unique ID
  "type": "function",       // Node type
  "z": "flow1",             // Parent flow
  "name": "Process Data",   // Display name
  "func": "return msg;",    // Type-specific config
  "outputs": 1,             // Number of outputs
  "wires": [["xyz789"]],    // Connected nodes
  "x": 300,                 // X position
  "y": 200                  // Y position
}
```

### Common Node Categories

**Core Nodes:**
- `inject` - Manually trigger flows
- `debug` - Display messages in sidebar
- `function` - Custom JavaScript code
- `change` - Modify message properties
- `switch` - Route messages conditionally
- `delay` - Pause or rate-limit messages

**Network Nodes:**
- `http in/out` - HTTP endpoints
- `websocket` - WebSocket connections
- `mqtt in/out` - MQTT messaging
- `tcp/udp` - Raw socket communication

**Home Assistant Nodes:**
- `trigger-state` - State change triggers
- `call-service` - Execute HA services
- `current-state` - Get entity state
- See `ha-*.md` references for full list

---

## Wires

**Wires** connect nodes together and define the path messages travel through a flow.

### Wire Characteristics

- **Unidirectional** - Messages flow in one direction
- **One-to-Many** - One output can connect to multiple inputs
- **No Loops** - Wires cannot create direct cycles (use Link nodes)

### Wire Visualization

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Trigger │────▶│ Process │────▶│ Action  │
└─────────┘     └─────────┘     └─────────┘
                    │
                    │ (split)
                    ▼
               ┌─────────┐
               │  Debug  │
               └─────────┘
```

### Wire JSON Structure

```javascript
{
  "id": "node1",
  "wires": [
    ["node2", "node3"],  // Output 1 → node2 AND node3
    ["node4"]            // Output 2 → node4
  ]
}
```

### Link Nodes

For connecting distant parts of a flow or creating loops:

```
┌──────────┐                    ┌──────────┐
│ Link Out │ ═══════════════════│ Link In  │
│  (loop)  │                    │  (loop)  │
└──────────┘                    └──────────┘
```

---

## Messages

**Messages** are JavaScript objects that flow between nodes. The message object is typically named `msg`.

### Message Structure

```javascript
msg = {
  _msgid: "abc123def456",  // Auto-generated unique ID
  payload: "Hello World",   // Primary data
  topic: "sensors/temp",    // Optional topic/category
  // ... any other properties
};
```

### Standard Properties

| Property | Description | Usage |
|----------|-------------|-------|
| `_msgid` | Unique message ID | Auto-generated, don't modify |
| `payload` | Primary message data | Main data being processed |
| `topic` | Message category | Routing, filtering |
| `req` / `res` | HTTP request/response | HTTP In/Out nodes |
| `error` | Error information | Catch node output |

### Message Flow Example

```javascript
// Inject node output
msg = { payload: 1609459200000, topic: "" }

// After Change node (set payload to timestamp)
msg = { payload: "2021-01-01T00:00:00.000Z", topic: "" }

// After Function node (format for notification)
msg = {
  payload: "Current time: 2021-01-01T00:00:00.000Z",
  topic: "notification"
}
```

### Preserving Message Properties

```javascript
// GOOD - preserve existing properties
msg.payload = "new value";
return msg;

// BAD - loses all other properties
msg = { payload: "new value" };
return msg;

// BETTER - clone if needed
const newMsg = RED.util.cloneMessage(msg);
newMsg.payload = "new value";
return newMsg;
```

### Multiple Outputs

```javascript
// Function node with 2 outputs
// Output 1: Even numbers, Output 2: Odd numbers
if (msg.payload % 2 === 0) {
  return [msg, null];  // Send to output 1 only
} else {
  return [null, msg];  // Send to output 2 only
}

// Send to both outputs
return [msg, msg];

// Send multiple messages to output 1
return [[msg1, msg2], null];
```

### Dropping Messages

```javascript
// Drop message (don't continue flow)
return null;

// Conditional drop
if (msg.payload < 0) {
  return null;  // Ignore negative values
}
return msg;
```

---

## Workspace Organization

### Tabs (Flows)

Organize by:
- **Domain** - Lighting, Climate, Security
- **Room** - Living Room, Bedroom, Kitchen
- **Device Type** - Sensors, Switches, Lights

### Groups

Visual grouping within a flow:

```
┌─────────────────────────────────────┐
│ Motion Detection                     │
│ ┌────────┐  ┌────────┐  ┌────────┐ │
│ │Trigger │─▶│ Check  │─▶│ Action │ │
│ └────────┘  └────────┘  └────────┘ │
└─────────────────────────────────────┘
```

### Comments

Add comment nodes or use node info:
- Explain complex logic
- Document expected inputs/outputs
- Note dependencies

### Color Coding

Use node colors to indicate:
- **Red** - Critical/Alert flows
- **Green** - Working/Active
- **Yellow** - Under development
- **Gray** - Disabled/Legacy

---

## Deploy Modes

### Full Deploy

Restarts all flows. Use when:
- Changing configuration nodes
- Adding new flows
- After Node-RED restart

### Modified Flows

Only restarts changed flows. Use for:
- Most development work
- Faster iteration
- Preserves state in unchanged flows

### Modified Nodes

Only restarts individual changed nodes. Use for:
- Minor tweaks
- Testing single nodes
- Minimal disruption

### Recommended Settings

```
Settings > User Settings > Deploy
├── ☑ Confirm deploy when workspace has undeployed changes
├── ☐ Automatically confirm on close
└── Deploy Type: Modified Flows (default)
```

---

## Editor Overview

### Panels

```
┌─────────────────────────────────────────────────────────┐
│  Menu Bar                                               │
├─────────┬───────────────────────────────┬───────────────┤
│         │                               │               │
│ Palette │       Workspace               │   Sidebar     │
│         │       (Flow Editor)           │   - Info      │
│ (Nodes) │                               │   - Debug     │
│         │                               │   - Config    │
│         │                               │               │
├─────────┴───────────────────────────────┴───────────────┤
│  Status Bar                                             │
└─────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Deploy |
| `Ctrl+E` | Export nodes |
| `Ctrl+I` | Import nodes |
| `Ctrl+Space` | Open search |
| `Ctrl+.` | Toggle sidebar |
| `Delete` | Delete selected |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |

### Debug Sidebar

The debug sidebar shows output from debug nodes:

```javascript
// Debug node settings
{
  "active": true,           // Enabled
  "tosidebar": true,        // Show in sidebar
  "console": false,         // Log to console
  "tostatus": false,        // Show in node status
  "complete": "payload",    // What to display
  // "complete": "true" for entire msg object
}
```

### Node Status

Nodes can display status beneath them:

```javascript
// In a function node
node.status({fill:"green", shape:"dot", text:"connected"});
node.status({fill:"red", shape:"ring", text:"error"});
node.status({});  // Clear status
```

Status shapes:
- `dot` - Filled circle
- `ring` - Hollow circle

Status colors:
- `red`, `green`, `yellow`, `blue`, `grey`

---

## Best Practices Summary

1. **Organize flows by domain** - Keep related automations together
2. **Name nodes descriptively** - "Living Room Motion" not "trigger-state"
3. **Use debug nodes liberally** - Especially during development
4. **Comment complex logic** - Future you will thank present you
5. **Use subflows for reuse** - Don't repeat yourself
6. **Handle errors** - Add Catch nodes to every flow
7. **Test incrementally** - Use inject nodes to test portions
8. **Version control flows** - Export JSON regularly

---

## Related References

- [Node Types](node-types.md) - Detailed node categories
- [Message Handling](message-handling.md) - Working with messages
- [Context Storage](context-storage.md) - Storing persistent data
- [Subflows](subflows.md) - Creating reusable components
