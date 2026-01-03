# MQTT Integration

MQTT with Node-RED and Home Assistant.

## Overview

```
[Device] ←MQTT→ [Broker] ←MQTT→ [Node-RED]
                   ↓
              [Home Assistant]
```

### When to Use MQTT

| Use Case | Best For |
|----------|----------|
| ESPHome devices | Direct device control |
| Zigbee2MQTT | Zigbee device integration |
| Custom sensors | Arduino, ESP32 projects |
| Cross-system | Multiple home automation systems |
| High frequency | Fast sensor updates |

---

## MQTT Broker Setup

### Mosquitto (Recommended)

Home Assistant Add-on:

```yaml
# Add-on configuration
logins:
  - username: nodered
    password: secure-password
  - username: homeassistant
    password: another-password
anonymous: false
```

### Connection Settings

| Setting | Value |
|---------|-------|
| Host | `homeassistant.local` or `core-mosquitto` |
| Port | 1883 (plain) or 8883 (TLS) |
| Protocol | MQTT 3.1.1 or 5.0 |

---

## Node-RED MQTT Nodes

### MQTT In

Subscribe to topics:

```json
{
  "type": "mqtt in",
  "topic": "zigbee2mqtt/living_room_motion",
  "qos": "0",
  "datatype": "json",
  "broker": "mqtt_broker_config"
}
```

### MQTT Out

Publish messages:

```json
{
  "type": "mqtt out",
  "topic": "zigbee2mqtt/living_room_light/set",
  "qos": "0",
  "retain": "false",
  "broker": "mqtt_broker_config"
}
```

### Broker Configuration

```json
{
  "type": "mqtt-broker",
  "name": "Mosquitto",
  "broker": "homeassistant.local",
  "port": "1883",
  "clientid": "nodered",
  "autoConnect": true,
  "usetls": false,
  "credentials": {
    "user": "nodered",
    "password": ""
  }
}
```

---

## Zigbee2MQTT Integration

### Device State Topics

```
zigbee2mqtt/[friendly_name]          # Device state
zigbee2mqtt/[friendly_name]/set      # Control device
zigbee2mqtt/[friendly_name]/get      # Request state
zigbee2mqtt/bridge/state             # Bridge status
zigbee2mqtt/bridge/logging           # Debug logs
```

### Subscribe to Motion Sensor

```json
{
  "type": "mqtt in",
  "topic": "zigbee2mqtt/living_room_motion"
}
```

Payload example:

```json
{
  "occupancy": true,
  "battery": 95,
  "linkquality": 120,
  "voltage": 3100
}
```

### Control Light

```javascript
msg.topic = "zigbee2mqtt/living_room_light/set";
msg.payload = {
  state: "ON",
  brightness: 200,
  color_temp: 350
};
return msg;
```

### Request Device State

```javascript
msg.topic = "zigbee2mqtt/living_room_light/get";
msg.payload = {
  state: ""
};
return msg;
```

---

## Common Patterns

### Motion → Light

```
[mqtt in: motion] → [function: check] → [mqtt out: light/set]
```

Function node:

```javascript
if (msg.payload.occupancy === true) {
  msg.topic = "zigbee2mqtt/living_room_light/set";
  msg.payload = { state: "ON", brightness: 254 };
  return msg;
}
return null;
```

### Temperature Monitoring

```javascript
// mqtt in: zigbee2mqtt/+/temperature
const device = msg.topic.split('/')[1];
const temp = msg.payload.temperature;

// Store in flow context
let temps = flow.get('temperatures') || {};
temps[device] = {
  value: temp,
  time: Date.now()
};
flow.set('temperatures', temps);

// Alert if too high
if (temp > 30) {
  msg.alert = `${device}: ${temp}°C`;
  return [msg, msg];  // Output 1: store, Output 2: alert
}

return [msg, null];
```

### Wildcard Subscriptions

```
zigbee2mqtt/+/temperature     # Any device, temperature only
zigbee2mqtt/#                 # All zigbee2mqtt messages
sensor/+/state                # Any sensor state
```

### Topic Parsing

```javascript
// Topic: zigbee2mqtt/living_room_motion
const parts = msg.topic.split('/');
const system = parts[0];      // "zigbee2mqtt"
const device = parts[1];      // "living_room_motion"
const action = parts[2];      // undefined (or "set", "get")

msg.device = device;
return msg;
```

---

## MQTT + Home Assistant

### HA MQTT Discovery

Automatic entity creation:

```javascript
// Create a sensor in HA via MQTT
msg.topic = "homeassistant/sensor/my_sensor/config";
msg.payload = {
  name: "Custom Sensor",
  state_topic: "custom/sensor/state",
  unit_of_measurement: "°C",
  device_class: "temperature",
  unique_id: "custom_temp_001",
  device: {
    identifiers: ["custom_device_001"],
    name: "Custom Device",
    manufacturer: "DIY"
  }
};
msg.retain = true;
return msg;
```

### Discovery Topics

```
homeassistant/[component]/[node_id]/[object_id]/config
```

Components: `sensor`, `binary_sensor`, `switch`, `light`, `climate`, etc.

### Bridge Mode

When to use MQTT vs HA WebSocket:

| Feature | MQTT | HA WebSocket |
|---------|------|--------------|
| Direct device control | ✅ Faster | Via HA |
| Device state | Real-time | Polling or events |
| HA entity integration | Manual | Native |
| Zigbee2MQTT | Direct | Via HA entities |
| Discovery | Supported | N/A |

---

## QoS Levels

| Level | Name | Guarantee |
|-------|------|-----------|
| 0 | At most once | Fire and forget |
| 1 | At least once | Delivered, maybe duplicates |
| 2 | Exactly once | Delivered once only |

### When to Use

| Use Case | QoS |
|----------|-----|
| Sensor updates | 0 |
| Light commands | 1 |
| Critical alerts | 2 |
| Logging | 0 |

---

## Retained Messages

### What is Retain?

Broker stores last message on topic. New subscribers receive it immediately.

### When to Retain

| Topic Type | Retain? |
|------------|---------|
| Device state | Yes |
| Commands | No |
| Events | No |
| Configuration | Yes |

### Clear Retained Message

```javascript
msg.topic = "zigbee2mqtt/device/state";
msg.payload = "";  // Empty payload
msg.retain = true;
return msg;
```

---

## Last Will and Testament (LWT)

### Broker Configuration

```json
{
  "type": "mqtt-broker",
  "willTopic": "nodered/status",
  "willPayload": "offline",
  "willQos": "1",
  "willRetain": true
}
```

### Birth Message

On connect, publish online status:

```
[inject: on start] → [mqtt out: nodered/status, payload: "online"]
```

### Monitor Connection

```javascript
// Subscribe to nodered/status
if (msg.payload === "offline") {
  // Node-RED disconnected, alert!
  msg.alert = "Node-RED is offline";
  return msg;
}
return null;
```

---

## Performance Tuning

### Connection Keepalive

```json
{
  "type": "mqtt-broker",
  "keepalive": "60"
}
```

### Reconnect Behavior

```json
{
  "reconnectPeriod": 5000,
  "connectTimeout": 30000
}
```

### Message Rate Limiting

```javascript
const key = msg.topic;
const lastTime = context.get(`lastMsg_${key}`) || 0;
const now = Date.now();
const minInterval = 100; // ms

if (now - lastTime < minInterval) {
  return null; // Drop message
}

context.set(`lastMsg_${key}`, now);
return msg;
```

---

## Debugging MQTT

### MQTT Explorer

Desktop tool to browse topics:
- Windows/Mac/Linux
- Topic tree view
- Publish/subscribe
- History

### Command Line

```bash
# Subscribe to all
mosquitto_sub -h localhost -t '#' -v

# Subscribe to specific
mosquitto_sub -h localhost -t 'zigbee2mqtt/+' -v

# Publish
mosquitto_pub -h localhost -t 'test/topic' -m 'hello'
```

### Node-RED Debug

```
[mqtt in: #] → [debug: complete msg object]
```

---

## Security

### TLS Connection

```json
{
  "type": "mqtt-broker",
  "usetls": true,
  "tls": "mqtt_tls_config"
}
```

TLS Config:

```json
{
  "type": "tls-config",
  "cert": "",
  "key": "",
  "ca": "/path/to/ca.crt",
  "verifyservercert": true
}
```

### Access Control

Mosquitto ACL:

```
# Allow nodered to publish/subscribe to zigbee2mqtt
user nodered
topic readwrite zigbee2mqtt/#
topic readwrite homeassistant/#
```

---

## Troubleshooting

### Connection Issues

| Problem | Check |
|---------|-------|
| Can't connect | Broker running? Firewall? |
| Auth failed | Username/password correct? |
| TLS errors | Certificate paths? CA trusted? |
| Reconnecting | Network stability? Keepalive? |

### Message Issues

| Problem | Check |
|---------|-------|
| No messages | Topic correct? QoS? |
| Old data | Retained message? |
| Duplicates | QoS 1 with slow network? |
| JSON errors | `datatype: json` set? |

### Debug Flow

```
[mqtt in: topic] → [debug: msg.payload]
                 → [debug: msg.topic]
                 → [debug: typeof msg.payload]
```

---

## Quick Reference

### Node Types

| Node | Purpose |
|------|---------|
| `mqtt in` | Subscribe to topic |
| `mqtt out` | Publish to topic |
| `mqtt-broker` | Broker connection config |

### Message Properties

| Property | Purpose |
|----------|---------|
| `msg.topic` | MQTT topic |
| `msg.payload` | Message content |
| `msg.qos` | Quality of service |
| `msg.retain` | Retain flag |

### Common Topics

| Topic Pattern | Purpose |
|---------------|---------|
| `zigbee2mqtt/+` | All Z2M devices |
| `zigbee2mqtt/bridge/#` | Z2M bridge info |
| `homeassistant/+/+/config` | HA discovery |
| `nodered/status` | Node-RED online status |

