# Node-RED Cookbook

Ready-to-use recipes for common automation tasks.

---

## Lighting Recipes

### Motion Light with Timeout

```javascript
// Function: Check if light should turn on
const motion = msg.payload;
const isNight = global.get("homeassistant")
    .homeAssistant.states["sun.sun"]?.state === "below_horizon";

if (motion === "on" && isNight) {
    msg.payload = {
        action: "light.turn_on",
        target: { entity_id: ["light.hallway"] }
    };
    return [msg, msg];  // Output 1: turn on, Output 2: start timer
}
return [null, null];
```

Flow: `[Trigger] → [Function] → [Service]`
                         `→ [Trigger 5min] → [Turn Off Service]`

### Dim Lights at Night

```javascript
const hour = new Date().getHours();
let brightness = 100;

if (hour >= 22 || hour < 6) {
    brightness = 30;
} else if (hour >= 20) {
    brightness = 60;
}

msg.payload = {
    action: "light.turn_on",
    target: { entity_id: msg.data.entity_id },
    data: { brightness_pct: brightness }
};
return msg;
```

### Toggle Light Group

```javascript
const ha = global.get("homeassistant").homeAssistant.states;
const lights = ["light.living_room", "light.kitchen"];

// Check if any light is on
const anyOn = lights.some(l => ha[l]?.state === "on");

msg.payload = {
    action: anyOn ? "light.turn_off" : "light.turn_on",
    target: { entity_id: lights }
};
return msg;
```

---

## Presence Recipes

### Nobody Home Actions

```javascript
const ha = global.get("homeassistant").homeAssistant.states;
const people = ["person.john", "person.jane"];

const anyoneHome = people.some(p => ha[p]?.state === "home");

if (!anyoneHome) {
    // Turn off everything
    const actions = [];

    actions.push({
        payload: { action: "light.turn_off", target: { entity_id: ["all"] }}
    });
    actions.push({
        payload: { action: "climate.set_temperature",
                   target: { entity_id: ["climate.home"] },
                   data: { temperature: 16 }}
    });

    return [actions];
}
return null;
```

### Welcome Home

```javascript
// Trigger: person.john state changed to "home"
const hour = new Date().getHours();

const actions = [];

// Turn on entry light
actions.push({
    payload: {
        action: "light.turn_on",
        target: { entity_id: ["light.entry"] },
        data: { brightness_pct: hour >= 18 ? 80 : 50 }
    }
});

// Set comfortable temperature
actions.push({
    payload: {
        action: "climate.set_temperature",
        target: { entity_id: ["climate.home"] },
        data: { temperature: 21 }
    }
});

return [actions];
```

---

## Notification Recipes

### Smart Notification

```javascript
// Only notify away people
const ha = global.get("homeassistant").homeAssistant.states;
const people = [
    { person: "person.john", notify: "notify.mobile_app_john" },
    { person: "person.jane", notify: "notify.mobile_app_jane" }
];

const messages = [];
for (const p of people) {
    if (ha[p.person]?.state !== "home") {
        messages.push({
            payload: {
                action: p.notify,
                data: {
                    title: msg.title || "Home Alert",
                    message: msg.message
                }
            }
        });
    }
}

if (messages.length > 0) {
    return [messages];
}
return null;
```

### Actionable Notification

```javascript
msg.payload = {
    action: "notify.mobile_app_phone",
    data: {
        title: "Garage Door Open",
        message: "The garage door has been open for 10 minutes",
        data: {
            actions: [
                { action: "CLOSE_GARAGE", title: "Close Door" },
                { action: "IGNORE", title: "Ignore" }
            ]
        }
    }
};
return msg;

// Handle response in separate flow with tag trigger
```

---

## Climate Recipes

### Temperature-Based Fan Control

```javascript
const temp = parseFloat(msg.payload);
const ha = global.get("homeassistant").homeAssistant.states;
const fanOn = ha["switch.ceiling_fan"]?.state === "on";

if (temp > 26 && !fanOn) {
    msg.payload = {
        action: "switch.turn_on",
        target: { entity_id: ["switch.ceiling_fan"] }
    };
    return msg;
} else if (temp < 24 && fanOn) {
    msg.payload = {
        action: "switch.turn_off",
        target: { entity_id: ["switch.ceiling_fan"] }
    };
    return msg;
}
return null;
```

### Window Open HVAC Control

```javascript
// Trigger: Any window opens
const ha = global.get("homeassistant").homeAssistant.states;
const windows = Object.keys(ha)
    .filter(id => id.startsWith("binary_sensor.window_"))
    .filter(id => ha[id].state === "on");

if (windows.length > 0) {
    // Windows open - turn off HVAC
    msg.payload = {
        action: "climate.turn_off",
        target: { entity_id: ["climate.home"] }
    };
    node.status({text: `${windows.length} windows open`});
    return msg;
}
return null;
```

---

## Security Recipes

### Door Open Too Long

```javascript
// After 10 minute delay node
const ha = global.get("homeassistant").homeAssistant.states;
const doorId = msg.data.entity_id;

// Check if still open
if (ha[doorId]?.state === "on") {
    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "Door Alert",
            message: `${doorId.split('.')[1]} has been open for 10 minutes`,
            data: { priority: "high" }
        }
    };
    return msg;
}
return null;
```

### Night Mode Auto-Arm

```javascript
// Trigger: Time 23:00
const ha = global.get("homeassistant").homeAssistant.states;

// Check all doors/windows closed
const openSensors = Object.keys(ha)
    .filter(id => id.match(/binary_sensor\.(door|window)/))
    .filter(id => ha[id].state === "on");

if (openSensors.length === 0) {
    msg.payload = {
        action: "input_select.select_option",
        target: { entity_id: ["input_select.alarm_mode"] },
        data: { option: "armed_night" }
    };
    return [msg, null];
} else {
    // Alert about open sensors
    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "Cannot Arm",
            message: `Open: ${openSensors.map(s => s.split('.')[1]).join(', ')}`
        }
    };
    return [null, msg];
}
```

---

## Data Processing Recipes

### Rolling Average

```javascript
const MAX_SAMPLES = 10;
const history = context.get("history") || [];

history.push(parseFloat(msg.payload));
while (history.length > MAX_SAMPLES) history.shift();
context.set("history", history);

msg.average = history.reduce((a, b) => a + b, 0) / history.length;
msg.min = Math.min(...history);
msg.max = Math.max(...history);

return msg;
```

### Change Detection

```javascript
const threshold = 2;  // Minimum change to report
const lastValue = context.get("lastValue");
const currentValue = parseFloat(msg.payload);

if (lastValue === undefined) {
    context.set("lastValue", currentValue);
    return msg;
}

const change = Math.abs(currentValue - lastValue);
if (change >= threshold) {
    msg.change = currentValue - lastValue;
    msg.previousValue = lastValue;
    context.set("lastValue", currentValue);
    return msg;
}

return null;  // No significant change
```

### Unit Conversion

```javascript
// Temperature: C to F
msg.fahrenheit = (msg.payload * 9/5) + 32;

// Power: W to kWh (over time)
const lastReading = context.get("lastReading") || { value: 0, time: Date.now() };
const hours = (Date.now() - lastReading.time) / 3600000;
const kwh = (msg.payload / 1000) * hours;

context.set("lastReading", { value: msg.payload, time: Date.now() });
msg.kwh = kwh;

return msg;
```

---

## Time-Based Recipes

### Weekday vs Weekend

```javascript
const day = new Date().getDay();
const isWeekend = day === 0 || day === 6;

if (isWeekend) {
    return [null, msg];  // Output 2: Weekend
} else {
    return [msg, null];  // Output 1: Weekday
}
```

### Time Window Check

```javascript
function isInTimeWindow(startHour, endHour) {
    const hour = new Date().getHours();
    if (startHour < endHour) {
        return hour >= startHour && hour < endHour;
    } else {
        // Overnight window (e.g., 22-6)
        return hour >= startHour || hour < endHour;
    }
}

if (isInTimeWindow(22, 6)) {
    // Night time
    msg.period = "night";
} else if (isInTimeWindow(6, 9)) {
    msg.period = "morning";
} else if (isInTimeWindow(17, 22)) {
    msg.period = "evening";
} else {
    msg.period = "day";
}

return msg;
```

### Schedule-Based Actions

```javascript
const schedule = {
    "06:00": { action: "scene.turn_on", scene: "scene.morning" },
    "08:00": { action: "climate.set_temperature", temp: 18 },
    "17:00": { action: "climate.set_temperature", temp: 21 },
    "22:00": { action: "scene.turn_on", scene: "scene.night" }
};

const now = new Date().toTimeString().slice(0, 5);
const scheduled = schedule[now];

if (scheduled) {
    msg.payload = {
        action: scheduled.action,
        target: { entity_id: [scheduled.scene || "climate.home"] },
        data: scheduled.temp ? { temperature: scheduled.temp } : {}
    };
    return msg;
}
return null;
```

---

## Media Recipes

### Pause on Doorbell

```javascript
// Trigger: doorbell pressed
const ha = global.get("homeassistant").homeAssistant.states;
const playing = Object.keys(ha)
    .filter(id => id.startsWith("media_player."))
    .filter(id => ha[id].state === "playing");

if (playing.length > 0) {
    msg.payload = {
        action: "media_player.media_pause",
        target: { entity_id: playing }
    };
    // Store to resume later
    flow.set("pausedPlayers", playing);
    return msg;
}
return null;
```

### TTS Announcement

```javascript
const message = msg.message || msg.payload;
const volume = msg.volume || 0.5;

msg.payload = {
    action: "tts.speak",
    target: { entity_id: ["media_player.kitchen_speaker"] },
    data: {
        message: message,
        cache: true
    }
};

// Set volume first
const volumeMsg = {
    payload: {
        action: "media_player.volume_set",
        target: { entity_id: ["media_player.kitchen_speaker"] },
        data: { volume_level: volume }
    }
};

return [[volumeMsg, msg]];  // Volume then speak
```

---

## Utility Recipes

### Debounce

```javascript
const DEBOUNCE_MS = 500;
const timeout = context.get("timeout");

if (timeout) clearTimeout(timeout);

context.set("timeout", setTimeout(() => {
    context.set("timeout", null);
    node.send(msg);
}, DEBOUNCE_MS));

return null;
```

### Throttle

```javascript
const MIN_INTERVAL = 1000;
const lastSent = context.get("lastSent") || 0;

if (Date.now() - lastSent >= MIN_INTERVAL) {
    context.set("lastSent", Date.now());
    return msg;
}
return null;
```

### State Memory

```javascript
// Remember state changes
const key = msg.data.entity_id;
const history = context.get("stateHistory") || {};

if (!history[key]) history[key] = [];

history[key].push({
    state: msg.payload,
    time: Date.now()
});

// Keep last 10 changes
while (history[key].length > 10) {
    history[key].shift();
}

context.set("stateHistory", history);
msg.history = history[key];
return msg;
```
