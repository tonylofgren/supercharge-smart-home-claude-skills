# MQTT Integration

Using MQTT with Node-RED and Home Assistant.

---

## Overview

MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol. Node-RED can:
- Receive MQTT messages (subscribe)
- Send MQTT messages (publish)
- Bridge between MQTT and Home Assistant

---

## MQTT Nodes

### mqtt in (Subscribe)

Receives messages from MQTT broker.

| Setting | Description |
|---------|-------------|
| Server | MQTT broker connection |
| Topic | Topic to subscribe (supports wildcards) |
| QoS | Quality of Service (0, 1, or 2) |
| Output | auto, string, buffer, JSON, base64 |

### mqtt out (Publish)

Sends messages to MQTT broker.

| Setting | Description |
|---------|-------------|
| Server | MQTT broker connection |
| Topic | Topic to publish to |
| QoS | Quality of Service |
| Retain | Keep last message on broker |

---

## Broker Configuration

### Add MQTT Broker

1. Drag mqtt in node to workspace
2. Double-click to configure
3. Click pencil icon next to Server
4. Configure broker:

```
Server: 192.168.1.100
Port: 1883
Client ID: nodered-client

# If authentication required:
Username: mqtt_user
Password: ****
```

### Mosquitto (Common Broker)

```yaml
# /etc/mosquitto/mosquitto.conf
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

---

## Topic Patterns

### Wildcards

| Pattern | Matches |
|---------|---------|
| `home/+/temperature` | `home/living/temperature`, `home/bedroom/temperature` |
| `home/#` | All topics under `home/` |
| `+/+/state` | `zigbee/switch1/state`, `mqtt/sensor2/state` |

### Home Assistant MQTT Topics

```
# Default discovery prefix
homeassistant/<component>/<object_id>/config

# State topics
homeassistant/sensor/temperature_1/state

# Command topics
homeassistant/switch/relay_1/set
```

---

## Common Patterns

### Subscribe and Process

```
[mqtt in] --> [JSON parse] --> [Function] --> [HA Service]
```

```javascript
// Function: Process MQTT payload
const data = msg.payload;

if (data.temperature > 25) {
    msg.payload = {
        action: "climate.set_temperature",
        target: { entity_id: ["climate.ac"] },
        data: { temperature: 22 }
    };
    return msg;
}
return null;
```

### Publish from Home Assistant

```
[HA Trigger] --> [Function] --> [mqtt out]
```

```javascript
// Function: Format for MQTT
msg.topic = "sensors/" + msg.data.entity_id.replace(".", "/");
msg.payload = {
    state: msg.payload,
    attributes: msg.data.new_state.attributes,
    timestamp: Date.now()
};
return msg;
```

### Bidirectional Bridge

```
// HA to MQTT
[HA State Change] --> [Format] --> [mqtt out: device/state]

// MQTT to HA
[mqtt in: device/command] --> [Parse] --> [HA Service]
```

---

## MQTT Discovery

### Create HA Entity via MQTT

```javascript
// Publish to discovery topic
msg.topic = "homeassistant/sensor/nodered_temp/config";
msg.payload = {
    name: "Node-RED Temperature",
    state_topic: "nodered/sensor/temperature/state",
    unit_of_measurement: "°C",
    device_class: "temperature",
    unique_id: "nodered_temp_001",
    device: {
        identifiers: ["nodered_sensors"],
        name: "Node-RED Sensors",
        manufacturer: "Node-RED"
    }
};
msg.retain = true;
return msg;
```

### Update Entity State

```javascript
msg.topic = "nodered/sensor/temperature/state";
msg.payload = "23.5";
return msg;
```

### Remove Discovery Entity

```javascript
// Publish empty payload to remove
msg.topic = "homeassistant/sensor/nodered_temp/config";
msg.payload = "";
msg.retain = true;
return msg;
```

---

## Zigbee2MQTT Integration

### Subscribe to Device

```
Topic: zigbee2mqtt/living_room_sensor
Output: JSON object
```

### Message Format

```json
{
    "temperature": 23.5,
    "humidity": 45,
    "battery": 85,
    "linkquality": 120
}
```

### Control Zigbee Device

```javascript
// Turn on Zigbee light
msg.topic = "zigbee2mqtt/living_room_light/set";
msg.payload = {
    state: "ON",
    brightness: 200,
    color_temp: 350
};
return msg;
```

### Process Zigbee Events

```javascript
// From mqtt in subscribed to zigbee2mqtt/#
const topic = msg.topic;
const device = topic.split('/')[1];

// Skip bridge messages
if (device === 'bridge') return null;

// Process device update
if (msg.payload.occupancy === true) {
    // Motion detected
    msg.payload = {
        action: "light.turn_on",
        target: { entity_id: ["light." + device + "_light"] }
    };
    return msg;
}
return null;
```

---

## Tasmota Integration

### Subscribe to Tasmota Device

```
Topic: tele/device_name/SENSOR
```

### Tasmota Message Format

```json
{
    "Time": "2024-01-15T10:30:00",
    "ENERGY": {
        "Power": 150,
        "Voltage": 230,
        "Current": 0.65
    }
}
```

### Control Tasmota

```javascript
// Turn on
msg.topic = "cmnd/device_name/POWER";
msg.payload = "ON";
return msg;

// Set dimmer
msg.topic = "cmnd/device_name/Dimmer";
msg.payload = "50";
return msg;
```

---

## QoS Levels

| QoS | Guarantee | Use Case |
|-----|-----------|----------|
| 0 | At most once | Sensor readings, frequent updates |
| 1 | At least once | Commands, important events |
| 2 | Exactly once | Critical operations (rarely needed) |

### Set QoS

```javascript
msg.qos = 1;  // Ensure delivery
msg.retain = false;  // Don't retain
return msg;
```

---

## Retained Messages

### When to Use Retain

- Device configuration (discovery)
- Last known state
- Static values

### When NOT to Use Retain

- Commands
- Temporary events
- Time-sensitive data

```javascript
// Publish retained
msg.retain = true;
msg.payload = {
    online: true,
    version: "1.0.0"
};
return msg;
```

---

## Error Handling

### Connection Status

```javascript
// Check MQTT connection
const connected = global.get("mqttConnected");

if (!connected) {
    node.warn("MQTT not connected");
    // Queue message or handle offline
}
```

### Handle Disconnection

Use Status node to monitor mqtt nodes:

```javascript
// Status node watching mqtt in node
if (msg.status.text === "disconnected") {
    // Alert or attempt recovery
    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "MQTT Disconnected",
            message: "Check broker status"
        }
    };
    return msg;
}
```

---

## Performance Tips

### Batch Messages

```javascript
// Collect messages and publish periodically
let buffer = context.get("buffer") || [];
buffer.push(msg.payload);

if (buffer.length >= 10 || /* time elapsed */) {
    msg.topic = "batch/data";
    msg.payload = buffer;
    context.set("buffer", []);
    return msg;
}

context.set("buffer", buffer);
return null;
```

### Filter Duplicates

```javascript
const lastValue = context.get("lastValue");
if (JSON.stringify(msg.payload) === JSON.stringify(lastValue)) {
    return null;  // Skip duplicate
}
context.set("lastValue", msg.payload);
return msg;
```

### Use Appropriate QoS

- QoS 0 for frequent sensor data
- QoS 1 for commands
- Avoid QoS 2 (rarely necessary, adds overhead)

---

## Debugging MQTT

### MQTT Explorer

Use MQTT Explorer tool to:
- View all topics
- Monitor messages
- Publish test messages
- Check retained messages

### Debug Flow

```
[mqtt in: #] --> [Debug node]
```

Subscribe to `#` temporarily to see all messages.

### Log Messages

```javascript
node.warn(`MQTT: ${msg.topic} = ${JSON.stringify(msg.payload)}`);
```
