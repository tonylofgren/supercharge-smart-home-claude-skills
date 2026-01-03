# Home Assistant Entity Nodes

Create entities in Home Assistant from Node-RED.

## IMPORTANT: Prerequisites

Entity nodes require the **Node-RED Companion** integration in Home Assistant.

### Installation

1. Install HACS (if not already installed)
2. In HACS, search for "Node-RED"
3. Install "Node-RED Companion" integration
4. Restart Home Assistant
5. Go to Settings → Devices & Services
6. Click "Add Integration"
7. Search for "Node-RED"
8. Complete setup

**Without this integration, entity nodes will show errors!**

## Common Configuration

All entity nodes share these config properties:

### Entity Config Node

Create a config node with:

```json
{
  "type": "ha-entity-config",
  "server": "server_node_id",
  "deviceConfig": "",
  "name": "Node-RED Sensor",
  "version": 6,
  "entityType": "sensor",
  "haConfig": [
    { "property": "name", "value": "My Sensor" },
    { "property": "device_class", "value": "temperature" },
    { "property": "unit_of_measurement", "value": "°C" }
  ],
  "resend": false
}
```

### Available haConfig Properties

| Property | Description | Example |
|----------|-------------|---------|
| `name` | Friendly name | `"Living Room Temperature"` |
| `device_class` | HA device class | `"temperature"`, `"motion"` |
| `unit_of_measurement` | Unit | `"°C"`, `"%"`, `"W"` |
| `icon` | MDI icon | `"mdi:thermometer"` |
| `entity_category` | Category | `"diagnostic"`, `"config"` |

---

## ha-sensor

Create sensor entities.

### Configuration

```json
{
  "type": "ha-sensor",
  "entityConfig": "entity_config_node_id",
  "state": "payload",
  "stateType": "msg",
  "attributes": [],
  "inputOverride": "allow",
  "resend": true,
  "outputLocation": "payload",
  "outputLocationType": "msg"
}
```

### Setting State

**From message payload:**
```javascript
msg.payload = 23.5;
return msg;
```

**With attributes:**
```javascript
msg.payload = {
  state: 23.5,
  attributes: {
    last_reading: new Date().toISOString(),
    trend: "rising"
  }
};
return msg;
```

### Device Classes

| Class | Description | Units |
|-------|-------------|-------|
| `apparent_power` | Apparent power | VA |
| `battery` | Battery level | % |
| `carbon_dioxide` | CO2 | ppm |
| `carbon_monoxide` | CO | ppm |
| `current` | Current | A |
| `energy` | Energy | kWh, Wh |
| `frequency` | Frequency | Hz |
| `gas` | Gas | m³, ft³ |
| `humidity` | Humidity | % |
| `illuminance` | Light level | lx |
| `power` | Power | W, kW |
| `power_factor` | Power factor | % |
| `pressure` | Pressure | hPa, mbar |
| `signal_strength` | Signal | dB, dBm |
| `temperature` | Temperature | °C, °F |
| `voltage` | Voltage | V |
| `water` | Water usage | L, gal, m³, ft³ |

### Example: Temperature Sensor

Entity config:
```json
{
  "haConfig": [
    { "property": "name", "value": "Calculated Average Temperature" },
    { "property": "device_class", "value": "temperature" },
    { "property": "unit_of_measurement", "value": "°C" },
    { "property": "state_class", "value": "measurement" }
  ]
}
```

Function node:
```javascript
const states = global.get("homeassistant").homeAssistant.states;
const temps = Object.entries(states)
  .filter(([id, e]) => e.attributes?.device_class === "temperature")
  .map(([id, e]) => parseFloat(e.state))
  .filter(t => !isNaN(t));

const avg = temps.reduce((a, b) => a + b, 0) / temps.length;
msg.payload = Math.round(avg * 10) / 10;
return msg;
```

---

## ha-binary-sensor

Create binary (on/off) sensors.

### Configuration

```json
{
  "type": "ha-binary-sensor",
  "entityConfig": "entity_config_node_id",
  "state": "payload",
  "stateType": "msg",
  "attributes": [],
  "resend": false,
  "inputOverride": "allow",
  "outputLocation": "payload",
  "outputLocationType": "msg"
}
```

### Setting State

**Boolean:**
```javascript
msg.payload = true;  // on
msg.payload = false; // off
return msg;
```

**String:**
```javascript
msg.payload = "on";
msg.payload = "off";
return msg;
```

### Device Classes

| Class | On Meaning | Off Meaning |
|-------|------------|-------------|
| `battery` | Low | Normal |
| `battery_charging` | Charging | Not charging |
| `cold` | Cold | Normal |
| `connectivity` | Connected | Disconnected |
| `door` | Open | Closed |
| `garage_door` | Open | Closed |
| `gas` | Detected | Clear |
| `heat` | Hot | Normal |
| `light` | Light | No light |
| `lock` | Unlocked | Locked |
| `moisture` | Wet | Dry |
| `motion` | Motion | No motion |
| `occupancy` | Occupied | Clear |
| `opening` | Open | Closed |
| `plug` | Plugged in | Unplugged |
| `power` | Powered | No power |
| `presence` | Present | Away |
| `problem` | Problem | OK |
| `running` | Running | Not running |
| `safety` | Unsafe | Safe |
| `smoke` | Detected | Clear |
| `sound` | Sound | Silence |
| `vibration` | Detected | Clear |
| `window` | Open | Closed |

### Example: Custom Motion Sensor

Combine multiple sensors:

```javascript
const states = global.get("homeassistant").homeAssistant.states;

const motionSensors = [
  "binary_sensor.motion_living_room",
  "binary_sensor.motion_hallway"
];

const anyMotion = motionSensors.some(id =>
  states[id]?.state === "on"
);

msg.payload = anyMotion;
return msg;
```

---

## ha-switch

Create controllable switches.

### Configuration

```json
{
  "type": "ha-switch",
  "entityConfig": "entity_config_node_id",
  "enableInput": true,
  "outputOnStateChange": true,
  "outputPayload": "state",
  "outputPayloadType": "habool"
}
```

### Behavior

- **Input messages**: Set switch state
- **HA control**: Triggered when switch is toggled in HA
- **Output**: Sent when state changes

### Setting State

```javascript
msg.payload = true;   // Turn on
msg.payload = false;  // Turn off
msg.payload = "on";   // Turn on
msg.payload = "off";  // Turn off
return msg;
```

### Receiving State Changes

When the switch is toggled in HA:

```javascript
// msg.payload is true or false
if (msg.payload === true) {
  // Switch was turned on in HA
} else {
  // Switch was turned off in HA
}
```

### Example: Automation Enable Switch

```javascript
// React to switch state change
const automationEnabled = msg.payload;

if (automationEnabled) {
  node.status({fill:"green", shape:"dot", text:"enabled"});
} else {
  node.status({fill:"grey", shape:"ring", text:"disabled"});
}

msg.enabled = automationEnabled;
return msg;
```

---

## ha-button

Create button entities that trigger flows.

### Configuration

```json
{
  "type": "ha-button",
  "entityConfig": "entity_config_node_id",
  "outputProperties": [
    {
      "property": "payload",
      "propertyType": "msg",
      "value": "pressed",
      "valueType": "str"
    }
  ]
}
```

### Usage

When the button is pressed in HA, the node outputs a message.

```javascript
// Function node after button
if (msg.payload === "pressed") {
  // Button was pressed
  msg.payload = {
    action: "script.my_script",
    target: {}
  };
  return msg;
}
```

### Example: Manual Trigger Button

Entity config:
```json
{
  "haConfig": [
    { "property": "name", "value": "Run Cleanup Script" },
    { "property": "icon", "value": "mdi:broom" }
  ]
}
```

---

## ha-number

Create number input entities.

### Configuration

```json
{
  "type": "ha-number",
  "entityConfig": "entity_config_node_id",
  "mode": "slider",
  "minValue": 0,
  "maxValue": 100,
  "step": 1,
  "state": "payload",
  "stateType": "msg",
  "enableInput": true,
  "outputOnStateChange": true
}
```

### Mode Options

| Mode | Description |
|------|-------------|
| `slider` | Slider control |
| `box` | Number input box |

### Setting Value

```javascript
msg.payload = 75;
return msg;
```

### Receiving Changes

When value is changed in HA:

```javascript
const newValue = msg.payload;
// Use the new value
```

### Example: Brightness Override

```javascript
// Use number value as brightness
msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness_pct: msg.payload }
};
return msg;
```

---

## ha-select

Create dropdown selection entities.

### Configuration

```json
{
  "type": "ha-select",
  "entityConfig": "entity_config_node_id",
  "options": ["Option 1", "Option 2", "Option 3"],
  "state": "payload",
  "stateType": "msg",
  "enableInput": true,
  "outputOnStateChange": true
}
```

### Setting Selection

```javascript
msg.payload = "Option 2";
return msg;
```

### Receiving Selection

```javascript
const selected = msg.payload;

switch (selected) {
  case "Option 1":
    // Handle option 1
    break;
  case "Option 2":
    // Handle option 2
    break;
}
```

### Example: Mode Selector

Options: `["Home", "Away", "Night", "Vacation"]`

```javascript
const mode = msg.payload;

const modeActions = {
  "Home": "script.home_mode",
  "Away": "script.away_mode",
  "Night": "script.night_mode",
  "Vacation": "script.vacation_mode"
};

msg.payload = {
  action: modeActions[mode],
  target: {}
};
return msg;
```

---

## ha-text

Create text input entities.

### Configuration

```json
{
  "type": "ha-text",
  "entityConfig": "entity_config_node_id",
  "mode": "text",
  "minLength": 0,
  "maxLength": 255,
  "pattern": "",
  "state": "payload",
  "stateType": "msg",
  "enableInput": true,
  "outputOnStateChange": true
}
```

### Mode Options

| Mode | Description |
|------|-------------|
| `text` | Regular text input |
| `password` | Hidden text |

### Example: Custom Message Input

```javascript
// User entered text
const customMessage = msg.payload;

msg.payload = {
  action: "notify.mobile_app_phone",
  data: {
    title: "Custom Alert",
    message: customMessage
  }
};
return msg;
```

---

## Common Patterns

### Update on Interval

Poll and update entity:

```
[inject every 1 min] ──> [function: calculate] ──> [ha-sensor]
```

### React to Entity

```
                                    ┌──> [action 1]
[ha-switch] ──> [switch node] ──┼──> [action 2]
                                    └──> [action 3]
```

### Expose Node-RED State

Create sensor from flow context:

```javascript
msg.payload = {
  state: flow.get('currentState'),
  attributes: {
    last_updated: new Date().toISOString(),
    source: "Node-RED"
  }
};
return msg;
```
