# Automation Patterns

## Table of Contents
- [Motion Lighting](#motion-lighting)
- [Presence Detection](#presence-detection)
- [Time-Based Automation](#time-based-automation)
- [Notification Routing](#notification-routing)
- [Climate Control](#climate-control)
- [Security Patterns](#security-patterns)
- [Appliance Monitoring](#appliance-monitoring)

---

## Motion Lighting

### Basic Motion Light

```
Trigger: state        Switch            Action
(motion on)  ───────▶ (is on?) ───────▶ (light.turn_on)
```

```json
[
  {
    "type": "trigger-state",
    "entityId": "binary_sensor.motion_living",
    "wires": [["switch_on"]]
  },
  {
    "type": "switch",
    "property": "payload",
    "rules": [{"t": "eq", "v": "on"}],
    "wires": [["light_on"]]
  },
  {
    "type": "api-call-service",
    "action": "light.turn_on",
    "entityId": "light.living_room"
  }
]
```

### Motion Light with Timer

```
Motion On  ──▶ Light On
Motion Off ──▶ Start Timer ──▶ (5 min) ──▶ Light Off
```

```javascript
// Function node: Handle motion states
const motion = msg.payload;
const timeout = context.get("timeout");

if (motion === "on") {
  // Cancel any pending off timer
  if (timeout) clearTimeout(timeout);
  context.set("timeout", null);
  return [msg, null];  // Output 1: Turn on
}

// Motion off - start timer
if (timeout) clearTimeout(timeout);

const newTimeout = setTimeout(() => {
  context.set("timeout", null);
  node.send([null, {payload: "off"}]);  // Output 2: Turn off
}, 5 * 60 * 1000);

context.set("timeout", newTimeout);
return null;  // Don't send yet
```

### Motion Light with Day/Night

```javascript
// Check sun state before lighting
const isNight = msg.data.sun_state === "below_horizon";
const brightness = isNight ? 50 : 255;

msg.payload = {
  action: "light.turn_on",
  target: { entity_id: ["light.living_room"] },
  data: { brightness: brightness }
};
return msg;
```

### Motion Light with Manual Override

```javascript
// Track if light was manually controlled
const wasManual = flow.get("lightManuallyChanged") || false;
const motion = msg.payload;

if (wasManual) {
  // Check if override has expired (30 min)
  const overrideTime = flow.get("overrideTime") || 0;
  if (Date.now() - overrideTime > 30 * 60 * 1000) {
    flow.set("lightManuallyChanged", false);
  } else {
    return null;  // Ignore motion, manual override active
  }
}

// Process motion normally
return msg;
```

---

## Presence Detection

### Multi-Sensor Presence

```javascript
// Combine multiple motion sensors
const sensors = [
  "binary_sensor.motion_living",
  "binary_sensor.motion_kitchen",
  "binary_sensor.motion_hallway"
];

const sensorStates = sensors.map(id => {
  return global.get("homeassistant").homeAssistant.states[id]?.state;
});

const anyMotion = sensorStates.some(state => state === "on");
const allClear = sensorStates.every(state => state === "off");

msg.payload = {
  anyMotion,
  allClear,
  activeSensors: sensors.filter((_, i) => sensorStates[i] === "on")
};
return msg;
```

### Presence with Decay Timer

```javascript
// Room occupied if motion within last 10 minutes
const PRESENCE_TIMEOUT = 10 * 60 * 1000;

const lastMotion = flow.get("lastMotion") || {};
const now = Date.now();

// Update last motion time
if (msg.payload === "on") {
  lastMotion[msg.topic] = now;
  flow.set("lastMotion", lastMotion);
}

// Check all sensors for recent activity
const recentActivity = Object.values(lastMotion).some(
  time => now - time < PRESENCE_TIMEOUT
);

msg.occupied = recentActivity;
msg.lastActivity = Math.max(...Object.values(lastMotion));
return msg;
```

### Device-Based Presence

```javascript
// Track person entities
const people = [
  "person.john",
  "person.jane"
];

const peopleHome = people.filter(id => {
  const state = global.get("homeassistant").homeAssistant.states[id];
  return state?.state === "home";
});

msg.payload = {
  anyoneHome: peopleHome.length > 0,
  whoIsHome: peopleHome.map(p => p.replace("person.", "")),
  count: peopleHome.length
};
return msg;
```

---

## Time-Based Automation

### Schedule Pattern

```javascript
// Time-based routing
const hour = new Date().getHours();
let mode;

if (hour >= 6 && hour < 9) {
  mode = "morning";
} else if (hour >= 9 && hour < 17) {
  mode = "day";
} else if (hour >= 17 && hour < 22) {
  mode = "evening";
} else {
  mode = "night";
}

msg.timeMode = mode;
return msg;
```

### Sunrise/Sunset Offset

```javascript
// Calculate brightness based on sun position
const sunState = global.get("homeassistant").homeAssistant.states["sun.sun"];
const elevation = sunState?.attributes?.elevation || 0;

// Brightness curve: 100% at noon, lower at sunrise/sunset
let brightness;
if (elevation < 0) {
  brightness = 20;  // Night
} else if (elevation < 10) {
  brightness = 50;  // Dawn/dusk
} else {
  brightness = 100; // Day
}

msg.brightness = brightness;
return msg;
```

### Workday vs Weekend

```javascript
// Different behavior on workdays
const now = new Date();
const day = now.getDay();
const isWeekend = day === 0 || day === 6;

// Check for holidays using workday sensor
const isWorkday = global.get("homeassistant")
  .homeAssistant.states["binary_sensor.workday_sensor"]?.state === "on";

msg.scheduleType = isWorkday ? "workday" : "weekend";
return msg;
```

---

## Notification Routing

### Priority-Based Routing

```javascript
// Route notifications by priority
const priority = msg.payload.priority || "normal";
const message = msg.payload.message;
const title = msg.payload.title || "Home Assistant";

const outputs = [null, null, null];  // low, normal, high

const notification = {
  action: "notify.mobile_app",
  data: { message, title }
};

switch (priority) {
  case "high":
    notification.data.data = { priority: "high", ttl: 0 };
    outputs[2] = { payload: notification };
    break;
  case "low":
    outputs[0] = { payload: notification };
    break;
  default:
    outputs[1] = { payload: notification };
}

return outputs;
```

### Presence-Aware Notifications

```javascript
// Only notify people who are away
const message = msg.payload.message;
const people = ["john", "jane"];

people.forEach(person => {
  const state = global.get("homeassistant")
    .homeAssistant.states[`person.${person}`];

  if (state?.state !== "home") {
    // Person is away, send notification
    node.send({
      payload: {
        action: `notify.mobile_app_${person}_phone`,
        data: { message }
      }
    });
  }
});

return null;
```

### Notification Aggregation

```javascript
// Aggregate notifications to avoid spam
const MAX_PER_MINUTE = 5;
const WINDOW = 60 * 1000;

const history = context.get("notifyHistory") || [];
const now = Date.now();

// Clean old entries
const recent = history.filter(t => now - t < WINDOW);

if (recent.length >= MAX_PER_MINUTE) {
  // Too many notifications, aggregate
  flow.set("pendingCount", (flow.get("pendingCount") || 0) + 1);
  return null;
}

// Send notification
recent.push(now);
context.set("notifyHistory", recent);

// Include pending count if any
const pending = flow.get("pendingCount") || 0;
if (pending > 0) {
  msg.payload.message += ` (+${pending} more)`;
  flow.set("pendingCount", 0);
}

return msg;
```

---

## Climate Control

### Temperature-Based HVAC

```javascript
// Simple thermostat logic
const currentTemp = parseFloat(msg.payload);
const targetTemp = flow.get("targetTemp") || 22;
const hysteresis = 0.5;

let action;
if (currentTemp < targetTemp - hysteresis) {
  action = "heat";
} else if (currentTemp > targetTemp + hysteresis) {
  action = "cool";
} else {
  action = "off";
}

// Only act if state changed
const lastAction = flow.get("lastAction");
if (action !== lastAction) {
  flow.set("lastAction", action);
  msg.payload = { action, currentTemp, targetTemp };
  return msg;
}

return null;
```

### Schedule-Based Climate

```javascript
// Temperature schedule
const schedules = {
  morning: { start: 6, end: 9, temp: 22 },
  day: { start: 9, end: 17, temp: 20 },
  evening: { start: 17, end: 22, temp: 22 },
  night: { start: 22, end: 6, temp: 18 }
};

const hour = new Date().getHours();
let targetTemp = 18;  // Default

for (const [name, schedule] of Object.entries(schedules)) {
  if (schedule.start <= hour && hour < schedule.end) {
    targetTemp = schedule.temp;
    break;
  }
}

// Adjust for presence
const anyoneHome = flow.get("anyoneHome");
if (!anyoneHome) {
  targetTemp -= 2;  // Save energy when away
}

msg.payload = { targetTemp };
return msg;
```

### Window Open Detection

```javascript
// Disable HVAC when window is open
const windows = [
  "binary_sensor.window_living",
  "binary_sensor.window_bedroom"
];

const anyOpen = windows.some(id => {
  return global.get("homeassistant")
    .homeAssistant.states[id]?.state === "on";
});

if (anyOpen) {
  msg.payload = {
    action: "climate.set_hvac_mode",
    data: { hvac_mode: "off" }
  };
  return msg;
}

return null;
```

---

## Security Patterns

### Armed/Disarmed Logic

```javascript
// Alarm state machine
const STATES = {
  DISARMED: "disarmed",
  ARMING: "arming",
  ARMED_HOME: "armed_home",
  ARMED_AWAY: "armed_away",
  TRIGGERED: "triggered"
};

const state = flow.get("alarmState") || STATES.DISARMED;
const event = msg.payload.event;

const transitions = {
  disarmed: {
    arm_home: STATES.ARMING,
    arm_away: STATES.ARMING
  },
  arming: {
    timer_complete: msg.payload.mode === "home"
      ? STATES.ARMED_HOME
      : STATES.ARMED_AWAY,
    cancel: STATES.DISARMED
  },
  armed_home: {
    sensor_triggered: STATES.TRIGGERED,
    disarm: STATES.DISARMED
  },
  armed_away: {
    sensor_triggered: STATES.TRIGGERED,
    disarm: STATES.DISARMED
  },
  triggered: {
    disarm: STATES.DISARMED,
    timeout: STATES.DISARMED
  }
};

if (transitions[state]?.[event]) {
  const newState = transitions[state][event];
  flow.set("alarmState", newState);
  msg.alarmState = newState;
  return msg;
}

return null;
```

### Entry Delay

```javascript
// Entry delay countdown
const ENTRY_DELAY = 30;  // seconds

if (msg.payload === "entry_triggered") {
  // Start countdown
  flow.set("entryCountdown", ENTRY_DELAY);

  const interval = setInterval(() => {
    const remaining = flow.get("entryCountdown") - 1;
    flow.set("entryCountdown", remaining);

    if (remaining <= 0) {
      clearInterval(interval);
      node.send({ payload: "alarm_triggered" });
    }
  }, 1000);

  flow.set("entryInterval", interval);
}

if (msg.payload === "disarm") {
  // Cancel countdown
  const interval = flow.get("entryInterval");
  if (interval) clearInterval(interval);
  flow.set("entryCountdown", 0);
}

return null;
```

---

## Appliance Monitoring

### Washer/Dryer Detection

```javascript
// Detect appliance state based on power consumption
const THRESHOLDS = {
  off: 5,
  idle: 20,
  running: 100
};

const power = parseFloat(msg.payload);
let state;

if (power < THRESHOLDS.off) {
  state = "off";
} else if (power < THRESHOLDS.idle) {
  state = "idle";
} else {
  state = "running";
}

const lastState = flow.get("washerState");

// Detect state transitions
if (state !== lastState) {
  flow.set("washerState", state);

  if (lastState === "running" && state === "idle") {
    // Washing complete
    msg.notification = "Washer cycle complete!";
    return [msg, null];  // Output 1: Complete
  }
}

return [null, msg];  // Output 2: Status update
```

### Cycle Detection Pattern

```javascript
// More robust cycle detection with debounce
const power = parseFloat(msg.payload);
const now = Date.now();

// Get state
let state = flow.get("applianceState") || {
  status: "off",
  runningStart: null,
  idleStart: null
};

const RUNNING_THRESHOLD = 50;
const IDLE_THRESHOLD = 10;
const CYCLE_COMPLETE_DELAY = 60000;  // 1 minute

if (power > RUNNING_THRESHOLD) {
  if (state.status !== "running") {
    state.status = "running";
    state.runningStart = now;
    state.idleStart = null;
  }
} else if (power < IDLE_THRESHOLD) {
  if (state.status === "running") {
    state.idleStart = now;
  }

  if (state.idleStart && (now - state.idleStart > CYCLE_COMPLETE_DELAY)) {
    // Cycle complete
    const duration = now - state.runningStart;
    state.status = "off";
    state.runningStart = null;
    state.idleStart = null;

    flow.set("applianceState", state);

    msg.cycleComplete = true;
    msg.duration = Math.round(duration / 60000);  // minutes
    return msg;
  }
}

flow.set("applianceState", state);
return null;
```

---

## Related References

- [Flow Organization](flow-organization.md) - Structuring flows
- [State Machines](state-machines.md) - Complex state logic
- [Error Handling](error-handling.md) - Reliable patterns
- [HA Trigger Nodes](ha-trigger-nodes.md) - Event triggers
