# Node-RED Automation Patterns

Common automation patterns for Home Assistant.

## Motion-Activated Light

The most common automation pattern.

### Simple Version

```
[trigger-state] → [api-call-service]
  motion on         light on
```

```json
[
  {
    "type": "trigger-state",
    "entityId": "binary_sensor.motion_living_room",
    "entityIdType": "exact",
    "constraints": [
      {
        "targetType": "this_entity",
        "propertyType": "current_state",
        "comparatorType": "is",
        "comparatorValue": "on"
      }
    ],
    "outputs": 2
  },
  {
    "type": "api-call-service",
    "domain": "light",
    "service": "turn_on",
    "entityId": ["light.living_room"]
  }
]
```

### With Auto-Off Timer

Use trigger node with `extend: true` to reset timer on each motion event.

```
[trigger-state] → [trigger(extend)] → [api-call-service]
  motion on         5 min timer        light off
```

```json
{
  "type": "trigger",
  "op1type": "nul",
  "op2": "off",
  "op2type": "str",
  "duration": "5",
  "extend": true,
  "units": "min"
}
```

**Key:** `extend: true` resets the timer on each new input. Do NOT create separate reset nodes!

### With Day/Night Brightness

```
[trigger-state] → [function] → [api-call-service]
  motion            brightness       light on
                    calculation
```

```javascript
// Function node: Calculate brightness based on time
const hour = new Date().getHours();
let brightness;

if (hour >= 22 || hour < 6) {
  brightness = 20;  // Night mode
} else if (hour >= 6 && hour < 9) {
  brightness = 60;  // Morning
} else {
  brightness = 100; // Day
}

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness_pct: brightness }
};
return msg;
```

### With Manual Override

Detect manual control and disable automation temporarily.

```javascript
// Function node: Check if manually controlled
const context = flow.get('manualOverride') || {};
const entityId = msg.data.entity_id;

// If light was turned on/off manually (not by this automation)
if (msg.data.context?.user_id) {
  context[entityId] = {
    active: true,
    until: Date.now() + (30 * 60 * 1000) // 30 min override
  };
  flow.set('manualOverride', context);
  return null; // Don't trigger automation
}

// Check if override is still active
if (context[entityId]?.active && Date.now() < context[entityId].until) {
  return null;
}

return msg;
```

## Presence Detection

### Basic Home/Away

```
[trigger-state] → [function] → [api-call-service]
  person entity       check all        set mode
                      persons
```

```javascript
// Function node: Check all persons
const states = global.get("homeassistant").homeAssistant.states;

const people = Object.keys(states)
  .filter(id => id.startsWith("person."));

const anyoneHome = people.some(id => states[id].state === "home");

if (anyoneHome) {
  msg.payload = { action: "input_boolean.turn_on", target: { entity_id: "input_boolean.someone_home" } };
} else {
  msg.payload = { action: "input_boolean.turn_off", target: { entity_id: "input_boolean.someone_home" } };
}

return msg;
```

### First Home / Last Leave

```javascript
// Function node: Detect first arrival or last departure
const states = global.get("homeassistant").homeAssistant.states;
const person = msg.data.entity_id;
const newState = msg.payload;
const oldState = msg.data.old_state?.state;

const otherPeople = Object.keys(states)
  .filter(id => id.startsWith("person.") && id !== person);

const othersHome = otherPeople.some(id => states[id].state === "home");

if (newState === "home" && oldState !== "home" && !othersHome) {
  // First person arriving
  msg.event = "first_home";
  return [msg, null];
} else if (newState !== "home" && oldState === "home" && !othersHome) {
  // Last person leaving
  msg.event = "last_leave";
  return [null, msg];
}

return [null, null];
```

## Schedule-Based Automation

### Time-Based Actions

Use `ha-time` node with entity or fixed time:

```json
{
  "type": "ha-time",
  "entityId": "input_datetime.morning_routine",
  "offset": 0,
  "repeatDaily": true
}
```

Or use inject node for fixed times:
```json
{
  "type": "inject",
  "repeat": "",
  "crontab": "0 7 * * 1-5",
  "topic": "weekday_morning"
}
```

### Workday Check

```javascript
// Function node: Check if today is a workday
const states = global.get("homeassistant").homeAssistant.states;
const workday = states["binary_sensor.workday"]?.state;

if (workday !== "on") {
  return null; // Skip on non-workdays
}

return msg;
```

## Notification Patterns

### Smart Notification Router

Route notifications based on presence and time.

```javascript
// Function node: Route notification
const states = global.get("homeassistant").homeAssistant.states;
const hour = new Date().getHours();

const title = msg.payload.title || "Notification";
const message = msg.payload.message;
const priority = msg.payload.priority || "normal";

// Get people who are home
const peopleHome = Object.keys(states)
  .filter(id => id.startsWith("person.") && states[id].state === "home")
  .map(id => id.replace("person.", ""));

// Night mode: only critical notifications
if (hour >= 23 || hour < 7) {
  if (priority !== "critical") {
    return null;
  }
}

// Build notification targets
const targets = [];

if (peopleHome.includes("john")) {
  targets.push("mobile_app_john_phone");
}
if (peopleHome.includes("jane")) {
  targets.push("mobile_app_jane_phone");
}

// If no one home, notify everyone
if (targets.length === 0) {
  targets.push("mobile_app_john_phone", "mobile_app_jane_phone");
}

msg.payload = {
  action: "notify.notify",
  data: {
    message: message,
    title: title,
    target: targets
  }
};

return msg;
```

### Actionable Notifications

```javascript
// Function node: Create actionable notification
msg.payload = {
  action: "notify.mobile_app_phone",
  data: {
    message: "Motion detected at front door",
    title: "Security Alert",
    data: {
      actions: [
        {
          action: "DISMISS",
          title: "Dismiss"
        },
        {
          action: "VIEW_CAMERA",
          title: "View Camera"
        },
        {
          action: "TURN_ON_LIGHTS",
          title: "Turn On Lights"
        }
      ],
      image: "/api/camera_proxy/camera.front_door"
    }
  }
};
return msg;
```

## Appliance Monitoring

### Power-Based State Detection

Detect washing machine states based on power consumption.

```javascript
// Function node: Detect appliance state
const power = parseFloat(msg.payload);
const currentState = flow.get('applianceState') || 'idle';

let newState = currentState;

if (power < 5) {
  if (currentState === 'running') {
    newState = 'finished';
  } else {
    newState = 'idle';
  }
} else if (power > 10) {
  newState = 'running';
}

if (newState !== currentState) {
  flow.set('applianceState', newState);
  msg.state = newState;
  msg.previousState = currentState;

  if (newState === 'finished') {
    return [msg, msg]; // Output 1: state change, Output 2: notification
  }
  return [msg, null];
}

return [null, null];
```

## Security Patterns

### Door/Window Monitoring

```javascript
// Function node: Check all security sensors
const states = global.get("homeassistant").homeAssistant.states;

const securitySensors = Object.keys(states)
  .filter(id => id.match(/^binary_sensor\.(door|window)_/))
  .filter(id => states[id].state === "on"); // on = open

if (securitySensors.length > 0) {
  msg.payload = {
    open: true,
    sensors: securitySensors,
    message: `Open: ${securitySensors.map(s => states[s].attributes.friendly_name).join(", ")}`
  };
  return msg;
}

msg.payload = { open: false, sensors: [] };
return msg;
```

### Alarm Integration

```javascript
// Function node: Handle alarm state changes
const newState = msg.payload;
const oldState = msg.data.old_state?.state;

const transitions = {
  'disarmed_to_armed_home': () => ({
    action: "script.arm_home_routine",
    message: "Alarm armed (Home mode)"
  }),
  'disarmed_to_armed_away': () => ({
    action: "script.arm_away_routine",
    message: "Alarm armed (Away mode)"
  }),
  'armed_to_triggered': () => ({
    action: "script.alarm_triggered",
    message: "ALARM TRIGGERED!",
    priority: "critical"
  })
};

const transition = `${oldState}_to_${newState}`;
const handler = transitions[transition];

if (handler) {
  const result = handler();
  msg.payload = result;
  return msg;
}

return null;
```

## Climate Control

### Temperature-Based Heating

```javascript
// Function node: Smart thermostat logic
const states = global.get("homeassistant").homeAssistant.states;

const currentTemp = parseFloat(states["sensor.living_room_temperature"]?.state);
const targetTemp = parseFloat(states["input_number.target_temperature"]?.state);
const outsideTemp = parseFloat(states["sensor.outside_temperature"]?.state);
const heatingState = states["climate.living_room"]?.state;

const hysteresis = 0.5;

if (isNaN(currentTemp) || isNaN(targetTemp)) {
  return null;
}

let action = null;

if (currentTemp < targetTemp - hysteresis && heatingState !== "heat") {
  action = { action: "climate.set_hvac_mode", target: { entity_id: "climate.living_room" }, data: { hvac_mode: "heat" } };
} else if (currentTemp > targetTemp + hysteresis && heatingState === "heat") {
  action = { action: "climate.set_hvac_mode", target: { entity_id: "climate.living_room" }, data: { hvac_mode: "off" } };
}

if (action) {
  msg.payload = action;
  return msg;
}

return null;
```

## Flow Organization Tips

1. **Group related nodes** using the Group feature (Ctrl+Shift+G)
2. **Use comment nodes** to explain complex logic
3. **Name your nodes** descriptively
4. **Use link nodes** to connect between tabs
5. **Create subflows** for reusable patterns
6. **Use flow context** for state that persists across messages
7. **Use global context** for data shared between flows
