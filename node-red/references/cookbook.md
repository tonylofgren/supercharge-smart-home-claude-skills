# Node-RED Cookbook

Ready-to-use recipes for common automations.

## Motion-Activated Lighting

### Basic Motion Light

```javascript
// Trigger: trigger-state on binary_sensor.motion
// Action: api-call-service

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] }
};
return msg;
```

### Motion Light with Timeout

Use trigger node with `extend: true`:

```json
{
  "type": "trigger",
  "op1type": "nul",
  "op2": "off",
  "duration": "5",
  "extend": true,
  "units": "min"
}
```

### Motion Light with Brightness by Time

```javascript
const hour = new Date().getHours();
let brightness;

if (hour >= 22 || hour < 6) {
  brightness = 20;
} else if (hour >= 6 && hour < 9) {
  brightness = 60;
} else {
  brightness = 100;
}

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness_pct: brightness }
};
return msg;
```

### Motion Light with Lux Check

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const lux = parseFloat(states["sensor.living_room_lux"]?.state);

// Only turn on if dark enough
if (lux > 50) {
  return null;
}

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] }
};
return msg;
```

---

## Presence Detection

### First Home Detection

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const person = msg.data.entity_id;
const newState = msg.payload;
const oldState = msg.data.old_state?.state;

// Only on arrival
if (newState !== "home" || oldState === "home") {
  return null;
}

// Check if first to arrive
const otherPeople = Object.keys(states)
  .filter(id => id.startsWith("person.") && id !== person);

const othersHome = otherPeople.some(id => states[id].state === "home");

if (!othersHome) {
  // First person arriving
  msg.event = "first_home";
  msg.person = person;
  return msg;
}

return null;
```

### Last Leave Detection

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const person = msg.data.entity_id;
const newState = msg.payload;
const oldState = msg.data.old_state?.state;

// Only on departure
if (newState === "home" || oldState !== "home") {
  return null;
}

// Check if last to leave
const otherPeople = Object.keys(states)
  .filter(id => id.startsWith("person.") && id !== person);

const othersHome = otherPeople.some(id => states[id].state === "home");

if (!othersHome) {
  // Last person leaving
  msg.event = "last_leave";
  msg.person = person;
  return msg;
}

return null;
```

### Anyone Home Check

```javascript
const states = global.get("homeassistant").homeAssistant.states;

const anyoneHome = Object.keys(states)
  .filter(id => id.startsWith("person."))
  .some(id => states[id].state === "home");

msg.payload = anyoneHome;
return msg;
```

---

## Climate Control

### Temperature-Based Heating

```javascript
const states = global.get("homeassistant").homeAssistant.states;

const currentTemp = parseFloat(states["sensor.living_room_temperature"]?.state);
const targetTemp = parseFloat(states["input_number.target_temperature"]?.state);
const heatingOn = states["climate.thermostat"]?.state === "heat";

const hysteresis = 0.5;

if (isNaN(currentTemp) || isNaN(targetTemp)) {
  return null;
}

if (currentTemp < targetTemp - hysteresis && !heatingOn) {
  msg.payload = {
    action: "climate.set_hvac_mode",
    target: { entity_id: ["climate.thermostat"] },
    data: { hvac_mode: "heat" }
  };
  return msg;
}

if (currentTemp > targetTemp + hysteresis && heatingOn) {
  msg.payload = {
    action: "climate.set_hvac_mode",
    target: { entity_id: ["climate.thermostat"] },
    data: { hvac_mode: "off" }
  };
  return msg;
}

return null;
```

### Window Open Detection

```javascript
const states = global.get("homeassistant").homeAssistant.states;

// Check if any windows are open
const windowsOpen = Object.keys(states)
  .filter(id => id.match(/binary_sensor\.window_/))
  .some(id => states[id].state === "on");

if (windowsOpen) {
  // Turn off heating
  msg.payload = {
    action: "climate.set_hvac_mode",
    target: { entity_id: ["climate.thermostat"] },
    data: { hvac_mode: "off" }
  };
  return msg;
}

return null;
```

---

## Notifications

### Smart Notification Router

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const hour = new Date().getHours();

const title = msg.title || "Notification";
const message = msg.message || msg.payload;
const priority = msg.priority || "normal";

// Quiet hours: 23:00 - 07:00
if (hour >= 23 || hour < 7) {
  if (priority !== "critical") {
    return null;
  }
}

// Find people who are home
const targets = [];
if (states["person.john"]?.state === "home") {
  targets.push("mobile_app_john_phone");
}
if (states["person.jane"]?.state === "home") {
  targets.push("mobile_app_jane_phone");
}

// If no one home, notify everyone
if (targets.length === 0) {
  targets.push("mobile_app_john_phone", "mobile_app_jane_phone");
}

// Send to each target
const messages = targets.map(target => ({
  action: `notify.${target}`,
  data: {
    title: title,
    message: message,
    data: { priority: priority === "critical" ? "high" : "normal" }
  }
}));

msg.payload = messages[0];
if (messages.length > 1) {
  msg.payload2 = messages[1];
}
return msg;
```

### Actionable Notification

```javascript
msg.payload = {
  action: "notify.mobile_app_phone",
  data: {
    title: msg.title || "Action Required",
    message: msg.message,
    data: {
      actions: [
        { action: "CONFIRM", title: "Confirm" },
        { action: "DENY", title: "Deny" },
        { action: "SNOOZE", title: "Remind Later" }
      ]
    }
  }
};
return msg;
```

---

## Security

### Door Left Open Alert

```javascript
// Function after trigger-state on door sensor
const entityId = msg.data.entity_id;
const friendlyName = msg.data.new_state.attributes.friendly_name;

// Store open time
flow.set(`doorOpen_${entityId}`, Date.now());

msg.payload = {
  entityId: entityId,
  name: friendlyName,
  message: `${friendlyName} has been open for 5 minutes`
};

return msg;
```

### All Doors/Windows Status

```javascript
const states = global.get("homeassistant").homeAssistant.states;

const openings = Object.entries(states)
  .filter(([id]) => id.match(/binary_sensor\.(door|window)_/))
  .filter(([id, entity]) => entity.state === "on")
  .map(([id, entity]) => ({
    id: id,
    name: entity.attributes.friendly_name,
    type: id.includes("door") ? "door" : "window"
  }));

if (openings.length > 0) {
  msg.payload = {
    open: true,
    count: openings.length,
    items: openings,
    message: `Open: ${openings.map(o => o.name).join(", ")}`
  };
} else {
  msg.payload = {
    open: false,
    count: 0,
    items: [],
    message: "All doors and windows are closed"
  };
}

return msg;
```

---

## Energy Monitoring

### Appliance State Detection

```javascript
const power = parseFloat(msg.payload);
const currentState = flow.get('applianceState') || 'idle';

let newState = currentState;

if (power < 5) {
  newState = currentState === 'running' ? 'finished' : 'idle';
} else if (power > 10) {
  newState = 'running';
}

if (newState !== currentState) {
  flow.set('applianceState', newState);
  msg.state = newState;
  msg.previousState = currentState;
  return msg;
}

return null;
```

### Daily Energy Cost

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const energyToday = parseFloat(states["sensor.energy_today"]?.state);
const pricePerKwh = 1.50; // SEK

const cost = Math.round(energyToday * pricePerKwh * 100) / 100;

msg.payload = {
  energy: energyToday,
  cost: cost,
  message: `Today's energy: ${energyToday} kWh (${cost} kr)`
};

return msg;
```

---

## Media Control

### Toggle Play/Pause

```javascript
msg.payload = {
  action: "media_player.media_play_pause",
  target: { entity_id: [msg.mediaPlayer || "media_player.living_room"] }
};
return msg;
```

### Volume Control

```javascript
const direction = msg.payload; // "up" or "down"
const states = global.get("homeassistant").homeAssistant.states;
const player = "media_player.living_room";
const currentVolume = states[player]?.attributes?.volume_level || 0.5;

let newVolume;
if (direction === "up") {
  newVolume = Math.min(1, currentVolume + 0.1);
} else {
  newVolume = Math.max(0, currentVolume - 0.1);
}

msg.payload = {
  action: "media_player.volume_set",
  target: { entity_id: [player] },
  data: { volume_level: newVolume }
};
return msg;
```

---

## Utility Functions

### Calculate Average

```javascript
const values = msg.payload; // Array of numbers
const valid = values.filter(v => !isNaN(v));

if (valid.length === 0) {
  return null;
}

const average = valid.reduce((a, b) => a + b, 0) / valid.length;
msg.payload = Math.round(average * 100) / 100;
return msg;
```

### Format Duration

```javascript
function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

msg.formatted = formatDuration(msg.payload);
return msg;
```

### Check Time Range

```javascript
function isInTimeRange(startHour, endHour) {
  const now = new Date().getHours();

  if (startHour < endHour) {
    return now >= startHour && now < endHour;
  } else {
    // Spans midnight
    return now >= startHour || now < endHour;
  }
}

// Examples
msg.isNightTime = isInTimeRange(22, 6);
msg.isMorning = isInTimeRange(6, 9);
msg.isWorkHours = isInTimeRange(9, 17);
return msg;
```

### Debounce

```javascript
const debounceMs = 1000;
const key = msg.topic || 'default';
const lastTime = context.get(`last_${key}`) || 0;
const now = Date.now();

if (now - lastTime < debounceMs) {
  return null;
}

context.set(`last_${key}`, now);
return msg;
```

### Rate Limit

```javascript
const maxPerMinute = 10;
let timestamps = context.get('timestamps') || [];
const now = Date.now();
const oneMinuteAgo = now - 60000;

timestamps = timestamps.filter(t => t > oneMinuteAgo);

if (timestamps.length >= maxPerMinute) {
  return null;
}

timestamps.push(now);
context.set('timestamps', timestamps);
return msg;
```

---

## Template Flows

### Input → Process → Output

```
[trigger] ──> [validate] ──> [transform] ──> [action] ──> [debug]
                  │
                  └──> [error handler]
```

### Multiple Actions from One Trigger

```
           ┌──> [action 1]
[trigger] ─┼──> [action 2]
           └──> [action 3]
```

### Conditional Routing

```
           ┌──> [if true] ──> [action A]
[trigger] ─┤
           └──> [if false] ──> [action B]
```

### Error Handling

```
[action] ──────────> [next step]
    │
    └──> [catch] ──> [retry logic] ──> [back to action]
              │
              └──> [notify on failure]
```
