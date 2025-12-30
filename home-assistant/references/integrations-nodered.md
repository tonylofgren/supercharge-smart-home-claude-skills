# Home Assistant Node-RED Integration Reference

## Table of Contents
- [Core Concepts](#core-concepts)
- [Installation and Setup](#installation-and-setup)
- [Entity Nodes](#entity-nodes)
- [Service Nodes](#service-nodes)
- [Event Nodes](#event-nodes)
- [Webhook Integration](#webhook-integration)
- [WebSocket API](#websocket-api)
- [Automation Examples](#automation-examples)
- [Node-RED vs HA Automations](#node-red-vs-ha-automations)
- [Advanced Patterns](#advanced-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

Node-RED is a flow-based programming tool that can integrate deeply with Home Assistant for complex automation logic.

### Key Terms

| Term | Description |
|------|-------------|
| **Flow** | A visual program connecting nodes |
| **Node** | A single processing unit |
| **Wire** | Connection between nodes |
| **msg** | Message object passed between nodes |
| **payload** | Primary data in message |
| **context** | Stored data (flow/global) |

### Integration Methods

| Method | Use Case | Best For |
|--------|----------|----------|
| **HA Addon** | Supervised installations | Easiest setup |
| **WebSocket API** | Any setup | Direct API access |
| **Webhooks** | External triggers | Third-party integration |
| **MQTT** | Lightweight messaging | IoT devices |

### Message Structure

```javascript
// Standard Node-RED message
{
  "_msgid": "abc123",
  "payload": "value",
  "topic": "optional/topic"
}

// Home Assistant entity message
{
  "payload": {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {
      "brightness": 255,
      "friendly_name": "Living Room"
    },
    "last_changed": "2024-01-15T10:30:00+00:00",
    "last_updated": "2024-01-15T10:30:05+00:00"
  },
  "data": { /* original HA data */ },
  "topic": "light.living_room"
}
```

---

## Installation and Setup

### Home Assistant Addon (Recommended)

```yaml
# No configuration.yaml changes needed
# Install via Supervisor > Add-on Store > Node-RED
```

**Addon Configuration:**
```yaml
# Node-RED addon options
credential_secret: your-secret-key
theme: dark
system_packages: []
npm_packages:
  - node-red-contrib-home-assistant-websocket
init_commands: []
```

### External Node-RED Instance

```yaml
# configuration.yaml
# Enable API access for external Node-RED

api:

http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.100  # Node-RED server IP
```

### Long-Lived Access Token

1. Go to Profile (bottom left)
2. Scroll to Long-Lived Access Tokens
3. Create Token
4. Copy and save securely

### Node-RED Configuration

```javascript
// Home Assistant server configuration in Node-RED
{
  "name": "Home Assistant",
  "version": 2,
  "addon": true,  // or false for external
  "rejectUnauthorizedCerts": true,
  "ha_boolean": "y|yes|true|on|home|open",
  "connectionDelay": true,
  "cacheJson": true,
  "heartbeat": false,
  "heartbeatInterval": 30,
  "areaRegistry": true,
  "deviceRegistry": true,
  "entityRegistry": true,
  "statusSeparator": ":",
  "statusYear": "hidden",
  "statusMonth": "short",
  "statusDay": "numeric",
  "statusHourCycle": "h23",
  "enableGlobalContextStore": true
}
```

---

## Entity Nodes

### State Changed Node

Triggers when an entity state changes.

```javascript
// Node configuration
{
  "entityId": "light.living_room",
  "entityIdType": "exact",  // exact, substring, regex
  "outputOnConnect": false,
  "stateType": "str",
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
}
```

**Example Flow: Motion Light**
```json
[
  {
    "id": "motion_trigger",
    "type": "server-state-changed",
    "entityId": "binary_sensor.motion_living",
    "outputOnConnect": false,
    "wires": [["motion_check"]]
  },
  {
    "id": "motion_check",
    "type": "switch",
    "property": "payload",
    "rules": [
      {"t": "eq", "v": "on"}
    ],
    "wires": [["light_on"]]
  },
  {
    "id": "light_on",
    "type": "api-call-service",
    "server": "ha_server",
    "service": "light.turn_on",
    "entityId": "light.living_room",
    "wires": [[]]
  }
]
```

### Get Entities Node

Retrieve entity states based on criteria.

```javascript
// Get all lights that are on
{
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
  "outputType": "array",
  "outputEmptyResults": false,
  "outputLocationType": "msg",
  "outputLocation": "payload"
}

// Output: Array of matching entities
[
  {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {...}
  },
  {
    "entity_id": "light.bedroom",
    "state": "on",
    "attributes": {...}
  }
]
```

### Current State Node

Get current state of a single entity.

```javascript
// Configuration
{
  "entityId": "sensor.temperature",
  "blockInputOverrides": false,
  "outputProperties": [
    {
      "property": "payload",
      "propertyType": "msg",
      "value": "",
      "valueType": "entityState"
    },
    {
      "property": "attributes",
      "propertyType": "msg",
      "value": "",
      "valueType": "entityAttributes"
    }
  ]
}

// Output message
{
  "payload": "22.5",
  "attributes": {
    "unit_of_measurement": "°C",
    "friendly_name": "Temperature"
  },
  "data": {...}
}
```

### Poll State Node

Periodically check entity state.

```javascript
// Configuration
{
  "entityId": "sensor.power_consumption",
  "updateInterval": 60,  // seconds
  "updateIntervalType": "num",
  "outputOnChanged": true,
  "outputProperties": [
    {
      "property": "payload",
      "value": "",
      "valueType": "entityState"
    }
  ]
}
```

---

## Service Nodes

### Call Service Node

Call any Home Assistant service.

```javascript
// Basic configuration
{
  "server": "ha_server",
  "version": 5,
  "service": "light.turn_on",
  "entityId": "light.living_room",
  "data": {
    "brightness": 255,
    "color_temp": 300
  }
}
```

**Dynamic Service Calls:**
```javascript
// Function node before service call
msg.payload = {
  service: "light.turn_on",
  target: {
    entity_id: "light.living_room"
  },
  data: {
    brightness: msg.brightness || 255
  }
};
return msg;
```

**Service call with templates:**
```javascript
// Using mustache templates
{
  "service": "light.turn_on",
  "entityId": "{{payload.entity_id}}",
  "data": {
    "brightness": "{{payload.brightness}}"
  }
}
```

### Fire Event Node

Fire custom events in Home Assistant.

```javascript
// Configuration
{
  "event": "custom_event",
  "data": {
    "source": "node_red",
    "value": "{{payload}}"
  }
}
```

**Listen in HA Automation:**
```yaml
# Home Assistant automation
automation:
  - alias: "Handle Node-RED Event"
    trigger:
      - platform: event
        event_type: custom_event
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.source == 'node_red' }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Event received: {{ trigger.event.data.value }}"
```

---

## Event Nodes

### Events: All Node

Subscribe to all Home Assistant events.

```javascript
// Configuration
{
  "eventType": "",  // Empty = all events
  "exposeToHomeAssistant": false,
  "outputProperties": [
    {
      "property": "payload",
      "value": "",
      "valueType": "eventData"
    },
    {
      "property": "topic",
      "value": "$outputData('eventData').event_type",
      "valueType": "jsonata"
    }
  ]
}
```

**Filter Specific Events:**
```javascript
// Switch node after events:all
{
  "property": "topic",
  "rules": [
    {"t": "eq", "v": "call_service"},
    {"t": "eq", "v": "state_changed"},
    {"t": "eq", "v": "automation_triggered"}
  ]
}
```

### Events: State Node

Optimized state change listener.

```javascript
// Configuration
{
  "entityIdType": "regex",
  "entityId": "^light\\.",  // All lights
  "outputOnConnect": false,
  "stateFilter": "",
  "outputProperties": [
    {
      "property": "payload",
      "valueType": "entityState"
    },
    {
      "property": "previous_state",
      "value": "$outputData('eventData').old_state.state",
      "valueType": "jsonata"
    }
  ]
}
```

### Device Trigger Node

Listen to device-specific triggers.

```javascript
// Configuration
{
  "deviceId": "abcd1234",
  "triggers": [
    {
      "type": "turned_on",
      "subtype": "button_1"
    }
  ]
}
```

---

## Webhook Integration

### Setting Up Webhooks in Node-RED

```javascript
// HTTP In node configuration
{
  "name": "HA Webhook",
  "url": "/ha-webhook",
  "method": "post",
  "upload": false
}
```

**Complete Webhook Flow:**
```json
[
  {
    "id": "webhook_in",
    "type": "http in",
    "url": "/ha-webhook",
    "method": "post",
    "wires": [["process_webhook"]]
  },
  {
    "id": "process_webhook",
    "type": "function",
    "func": "// Process incoming webhook\nconst action = msg.payload.action;\nconst data = msg.payload.data;\n\n// Validate\nif (!action) {\n  msg.statusCode = 400;\n  msg.payload = {error: 'Missing action'};\n  return [null, msg];\n}\n\nmsg.action = action;\nmsg.data = data;\nreturn [msg, null];",
    "outputs": 2,
    "wires": [["ha_service"], ["http_response"]]
  },
  {
    "id": "ha_service",
    "type": "api-call-service",
    "service": "{{action}}",
    "wires": [["http_response"]]
  },
  {
    "id": "http_response",
    "type": "http response",
    "statusCode": "200",
    "wires": []
  }
]
```

### Calling Node-RED from Home Assistant

```yaml
# Home Assistant automation calling Node-RED webhook
automation:
  - alias: "Trigger Node-RED Flow"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    action:
      - service: rest_command.node_red_webhook
        data:
          action: motion_detected
          location: living_room

rest_command:
  node_red_webhook:
    url: "http://localhost:1880/ha-webhook"
    method: POST
    content_type: "application/json"
    payload: '{"action": "{{ action }}", "data": {"location": "{{ location }}"}}'
```

### Webhook Security

```javascript
// Validate webhook secret
const secret = env.get("WEBHOOK_SECRET");
const providedSecret = msg.req.headers['x-webhook-secret'];

if (providedSecret !== secret) {
  msg.statusCode = 401;
  msg.payload = {error: "Unauthorized"};
  return [null, msg];  // Send to error output
}
return [msg, null];  // Continue processing
```

---

## WebSocket API

### Direct WebSocket Connection

```javascript
// Function node: Connect to HA WebSocket
const WebSocket = global.get('ws');
const ws = new WebSocket('ws://homeassistant.local:8123/api/websocket');

ws.on('open', function() {
  // Authenticate
  ws.send(JSON.stringify({
    type: "auth",
    access_token: env.get("HA_TOKEN")
  }));
});

ws.on('message', function(data) {
  const msg = JSON.parse(data);
  node.send({payload: msg});
});

context.set('ws', ws);
```

### WebSocket Commands

```javascript
// Subscribe to state changes
{
  "id": 1,
  "type": "subscribe_events",
  "event_type": "state_changed"
}

// Call service
{
  "id": 2,
  "type": "call_service",
  "domain": "light",
  "service": "turn_on",
  "target": {
    "entity_id": "light.living_room"
  },
  "service_data": {
    "brightness": 255
  }
}

// Get states
{
  "id": 3,
  "type": "get_states"
}

// Get config
{
  "id": 4,
  "type": "get_config"
}

// Get services
{
  "id": 5,
  "type": "get_services"
}
```

---

## Automation Examples

### Advanced Motion Lighting

```json
[
  {
    "id": "motion_input",
    "type": "server-state-changed",
    "entityId": "binary_sensor.motion_living",
    "wires": [["motion_switch"]]
  },
  {
    "id": "motion_switch",
    "type": "switch",
    "property": "payload",
    "rules": [
      {"t": "eq", "v": "on"},
      {"t": "eq", "v": "off"}
    ],
    "wires": [["check_conditions"], ["start_timer"]]
  },
  {
    "id": "check_conditions",
    "type": "api-current-state",
    "entityId": "sun.sun",
    "outputProperties": [
      {"property": "sun_state", "value": "", "valueType": "entityState"}
    ],
    "wires": [["sun_check"]]
  },
  {
    "id": "sun_check",
    "type": "switch",
    "property": "sun_state",
    "rules": [
      {"t": "eq", "v": "below_horizon"}
    ],
    "wires": [["get_brightness"]]
  },
  {
    "id": "get_brightness",
    "type": "function",
    "func": "const hour = new Date().getHours();\nlet brightness;\n\nif (hour >= 22 || hour < 6) {\n  brightness = 50;  // Night mode\n} else {\n  brightness = 255; // Full brightness\n}\n\nmsg.payload = {\n  brightness: brightness\n};\nreturn msg;",
    "wires": [["turn_on_light"]]
  },
  {
    "id": "turn_on_light",
    "type": "api-call-service",
    "service": "light.turn_on",
    "entityId": "light.living_room",
    "data": "{\"brightness\": {{payload.brightness}}}",
    "wires": [[]]
  },
  {
    "id": "start_timer",
    "type": "trigger",
    "duration": "300",
    "units": "s",
    "reset": true,
    "wires": [["turn_off_light"]]
  },
  {
    "id": "turn_off_light",
    "type": "api-call-service",
    "service": "light.turn_off",
    "entityId": "light.living_room",
    "wires": [[]]
  }
]
```

### Notification Router

```javascript
// Function node: Route notifications based on presence
const presenceStates = flow.get('presence') || {};
const message = msg.payload.message;
const priority = msg.payload.priority || 'normal';

let targets = [];

// Check who's home
if (presenceStates.john === 'home') {
  targets.push('mobile_app_john_phone');
}
if (presenceStates.jane === 'home') {
  targets.push('mobile_app_jane_phone');
}

// High priority = notify everyone
if (priority === 'high') {
  targets = ['mobile_app_john_phone', 'mobile_app_jane_phone'];
}

// No one home = use speakers
if (targets.length === 0) {
  msg.useAnnouncement = true;
  return [null, msg];
}

// Send to each target
const messages = targets.map(target => ({
  payload: {
    service: 'notify.' + target,
    data: {
      message: message,
      title: msg.payload.title || 'Home Assistant'
    }
  }
}));

return [messages];
```

### State Machine Pattern

```javascript
// Function node: Manage complex state
const states = {
  IDLE: 'idle',
  ARMING: 'arming',
  ARMED: 'armed',
  TRIGGERED: 'triggered'
};

let currentState = flow.get('alarm_state') || states.IDLE;
const event = msg.payload.event;

// State transitions
const transitions = {
  [states.IDLE]: {
    'arm': states.ARMING
  },
  [states.ARMING]: {
    'armed': states.ARMED,
    'cancel': states.IDLE
  },
  [states.ARMED]: {
    'trigger': states.TRIGGERED,
    'disarm': states.IDLE
  },
  [states.TRIGGERED]: {
    'disarm': states.IDLE,
    'timeout': states.IDLE
  }
};

// Process transition
if (transitions[currentState] && transitions[currentState][event]) {
  const newState = transitions[currentState][event];
  flow.set('alarm_state', newState);

  msg.payload = {
    previous: currentState,
    current: newState,
    event: event
  };
  return msg;
}

// Invalid transition
node.warn(`Invalid transition: ${currentState} -> ${event}`);
return null;
```

---

## Node-RED vs HA Automations

### When to Use Node-RED

| Scenario | Why Node-RED |
|----------|--------------|
| Complex logic | Visual debugging, easier branching |
| Multiple conditions | Switch nodes, function nodes |
| External API calls | HTTP request nodes |
| Data transformation | Function nodes with full JavaScript |
| Rate limiting | Delay/throttle nodes |
| State machines | Flow context, complex state |
| Debugging | Debug nodes, visual flow |

### When to Use HA Automations

| Scenario | Why HA Automations |
|----------|-------------------|
| Simple triggers | Single trigger, single action |
| Device triggers | Native device support |
| Blueprints | Reusable, shareable |
| Native integrations | Deep HA integration |
| Traces | Built-in automation traces |
| Backups | Part of HA config backup |

### Hybrid Approach

```yaml
# Home Assistant handles triggers, Node-RED handles logic
automation:
  - alias: "Motion Detected - Forward to Node-RED"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_living
        to: "on"
    action:
      - service: rest_command.node_red
        data:
          endpoint: motion
          entity: "{{ trigger.entity_id }}"

  - alias: "Complex Automation via Node-RED"
    trigger:
      - platform: event
        event_type: node_red_action
    action:
      - service: "{{ trigger.event.data.service }}"
        target:
          entity_id: "{{ trigger.event.data.entity_id }}"
        data: "{{ trigger.event.data.service_data }}"
```

---

## Advanced Patterns

### Subflows for Reusability

```json
{
  "id": "subflow:notification_handler",
  "type": "subflow",
  "name": "Notification Handler",
  "info": "Routes notifications based on priority and presence",
  "in": [
    {
      "x": 50,
      "y": 30,
      "wires": [{"id": "process_notification"}]
    }
  ],
  "out": [
    {
      "x": 350,
      "y": 30,
      "wires": [{"id": "output", "port": 0}]
    }
  ],
  "env": [
    {
      "name": "DEFAULT_PRIORITY",
      "type": "str",
      "value": "normal"
    }
  ]
}
```

### Context Store for State

```javascript
// Global context: Shared across all flows
global.set('home_mode', 'away');
const mode = global.get('home_mode');

// Flow context: Shared within flow
flow.set('last_motion', Date.now());
const lastMotion = flow.get('last_motion');

// Node context: Per-node storage
context.set('counter', (context.get('counter') || 0) + 1);

// Persistent storage (survives restarts)
flow.set('important_data', value, 'file');
const data = flow.get('important_data', 'file');
```

### Rate Limiting

```javascript
// Delay node configuration for rate limiting
{
  "pauseType": "rate",
  "rate": "1",
  "rateUnits": "minute",
  "drop": true  // Drop messages exceeding rate
}
```

**Debounce Pattern:**
```javascript
// Function node for debouncing
const DEBOUNCE_MS = 5000;
const key = msg.payload.entity_id;
const lastTrigger = context.get(key) || 0;
const now = Date.now();

if (now - lastTrigger < DEBOUNCE_MS) {
  return null;  // Ignore rapid triggers
}

context.set(key, now);
return msg;
```

### Error Handling

```javascript
// Catch node + error handling
try {
  // Process logic
  const result = processData(msg.payload);
  msg.payload = result;
  return [msg, null];  // Success output
} catch (error) {
  msg.error = error.message;
  msg.originalPayload = msg.payload;
  return [null, msg];  // Error output
}
```

**Recovery Pattern:**
```json
[
  {
    "id": "main_flow",
    "type": "function",
    "wires": [["success_handler"], ["error_handler"]]
  },
  {
    "id": "error_handler",
    "type": "function",
    "func": "// Log error\nnode.error(msg.error, msg);\n\n// Retry logic\nconst retries = msg.retries || 0;\nif (retries < 3) {\n  msg.retries = retries + 1;\n  return msg;\n}\n\n// Max retries exceeded\nreturn null;",
    "wires": [["retry_delay"]]
  },
  {
    "id": "retry_delay",
    "type": "delay",
    "timeout": "5",
    "timeoutUnits": "seconds",
    "wires": [["main_flow"]]
  }
]
```

### Environment Variables

```javascript
// Access environment variables
const token = env.get("HA_ACCESS_TOKEN");
const baseUrl = env.get("HA_BASE_URL");

// Set in settings.js or addon config
process.env.HA_ACCESS_TOKEN = "your_token";
```

---

## Best Practices

### Flow Organization

```
Home Automation/
├── Lighting/
│   ├── Motion Lights
│   ├── Schedule Lights
│   └── Scene Manager
├── Climate/
│   ├── Temperature Control
│   └── Fan Automation
├── Security/
│   ├── Door Alerts
│   └── Camera Motion
├── Notifications/
│   └── Notification Router
└── Utilities/
    ├── State Cache
    └── Error Handler
```

### Naming Conventions

```javascript
// Node naming
"[Room] Action - Detail"
"Living Room Light - Motion On"
"Kitchen Fan - Temperature Trigger"

// Flow naming
"Domain - Feature"
"Lighting - Motion Automation"
"Climate - AC Schedule"
```

### Performance Tips

| Tip | Implementation |
|-----|----------------|
| Filter early | Use state filters in trigger nodes |
| Cache states | Store frequently accessed states in context |
| Limit polling | Use event-based nodes over poll state |
| Batch operations | Group related service calls |
| Clean context | Periodically clear old context data |

```javascript
// Cache example
const CACHE_TTL = 60000;  // 1 minute
const cached = flow.get('entity_cache') || {};
const now = Date.now();

if (!cached[entityId] || now - cached[entityId].timestamp > CACHE_TTL) {
  // Fetch fresh state
  cached[entityId] = {
    state: await getState(entityId),
    timestamp: now
  };
  flow.set('entity_cache', cached);
}

msg.payload = cached[entityId].state;
```

### Documentation

```javascript
// Add comments to function nodes
/**
 * Process motion events for living room
 *
 * Inputs:
 *   msg.payload - Motion sensor state (on/off)
 *   msg.data - Full event data
 *
 * Outputs:
 *   [0] - Motion detected, proceed with lighting
 *   [1] - No motion, start off timer
 */
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection lost | Token expired | Generate new long-lived token |
| No state updates | Event filter | Check entity ID patterns |
| Service not called | Wrong format | Use JSONata for dynamic data |
| Slow response | Too many nodes | Optimize flow, filter early |
| Memory issues | Context buildup | Clear old context data |

### Debug Techniques

```javascript
// Debug node: Show complete message
{
  "active": true,
  "tosidebar": true,
  "console": false,
  "complete": "true",  // Show entire msg object
  "targetType": "full"
}

// Conditional debug
if (env.get("DEBUG_MODE") === "true") {
  node.warn(JSON.stringify(msg.payload, null, 2));
}
```

### Connection Issues

```javascript
// Check connection status
const serverNode = RED.nodes.getNode("ha_server_id");
if (serverNode && serverNode.websocket) {
  const state = serverNode.websocket.readyState;
  // 0: CONNECTING, 1: OPEN, 2: CLOSING, 3: CLOSED
  node.status({
    fill: state === 1 ? "green" : "red",
    shape: "dot",
    text: state === 1 ? "Connected" : "Disconnected"
  });
}
```

### Log Analysis

```bash
# Node-RED logs (addon)
ha logs -f addon_a0d7b954_nodered

# Node-RED logs (external)
journalctl -u nodered -f

# Home Assistant logs for API calls
tail -f /config/home-assistant.log | grep "node_red\|websocket"
```

### State Synchronization

```javascript
// Force state refresh
msg.payload = {
  type: "get_states"
};
// Send to WebSocket API node

// Handle stale cache
const lastUpdate = flow.get('last_state_update') || 0;
if (Date.now() - lastUpdate > 300000) {  // 5 minutes
  // Trigger full state refresh
  flow.set('last_state_update', Date.now());
  // ... refresh logic
}
```

### Common Errors

```javascript
// "Cannot read property 'state' of undefined"
// Entity doesn't exist or not loaded yet
const state = msg.payload?.state ?? "unknown";

// "Invalid service call"
// Check service exists
{
  "domain": "light",      // Not "lights"
  "service": "turn_on",   // Not "turnOn"
  "target": {
    "entity_id": "light.living_room"  // Full entity_id
  }
}

// "Authentication failed"
// Token issues
// 1. Check token hasn't expired
// 2. Verify token has sufficient permissions
// 3. Check for whitespace in token string
```

---

## Integration Checklist

```markdown
## Node-RED Setup Checklist

### Installation
- [ ] Node-RED installed (addon or external)
- [ ] node-red-contrib-home-assistant-websocket installed
- [ ] Long-lived access token generated
- [ ] Server connection configured and connected

### Configuration
- [ ] Entity registry enabled
- [ ] Device registry enabled (if using device triggers)
- [ ] Global context store enabled
- [ ] Credential secret set

### Security
- [ ] HTTPS enabled (production)
- [ ] Authentication enabled
- [ ] Webhook secrets configured
- [ ] Token stored securely

### Organization
- [ ] Flows organized by domain
- [ ] Naming conventions established
- [ ] Debug flows disabled in production
- [ ] Backup schedule configured
```

