# State Machines

Implementing complex state-based logic in Node-RED.

---

## What is a State Machine?

A state machine manages:
- **States**: Distinct modes of operation (idle, running, paused)
- **Transitions**: Rules for moving between states
- **Actions**: What happens on state entry/exit/during

---

## Basic Pattern

### Flow Structure

```
[Trigger] --> [Get Current State] --> [Process Event] --> [Update State]
                                            |
                                            v
                                      [Execute Actions]
```

### State Storage

```javascript
// Initialize state machine
let machine = flow.get("stateMachine") || {
    currentState: "idle",
    previousState: null,
    lastTransition: null,
    data: {}
};
```

---

## Simple Two-State Example

### Light with Manual Override

```javascript
// States: auto, manual
// Events: motion, timeout, switch_toggle

const event = msg.payload;
let state = flow.get("lightState") || { mode: "auto", lastMotion: 0 };

switch (state.mode) {
    case "auto":
        if (event === "motion") {
            state.lastMotion = Date.now();
            msg.action = "turn_on";
        } else if (event === "timeout") {
            msg.action = "turn_off";
        } else if (event === "switch_toggle") {
            state.mode = "manual";
            state.manualStart = Date.now();
            msg.action = "toggle";
        }
        break;

    case "manual":
        if (event === "switch_toggle") {
            msg.action = "toggle";
        }
        // Auto-return after 30 minutes
        if (Date.now() - state.manualStart > 30 * 60 * 1000) {
            state.mode = "auto";
        }
        break;
}

flow.set("lightState", state);
return msg;
```

---

## Multi-State Example

### Security System

```javascript
// States: disarmed, arming, armed_away, armed_home, triggered
// Events: arm_away, arm_home, disarm, sensor_trip, timeout

const STATES = {
    DISARMED: "disarmed",
    ARMING: "arming",
    ARMED_AWAY: "armed_away",
    ARMED_HOME: "armed_home",
    TRIGGERED: "triggered"
};

const event = msg.event;
const payload = msg.payload;

let machine = flow.get("securityMachine") || {
    state: STATES.DISARMED,
    armingStart: null,
    triggeredBy: null
};

const previousState = machine.state;

// State transitions
switch (machine.state) {
    case STATES.DISARMED:
        if (event === "arm_away") {
            machine.state = STATES.ARMING;
            machine.armingStart = Date.now();
            machine.nextState = STATES.ARMED_AWAY;
            msg.action = "start_exit_delay";
        } else if (event === "arm_home") {
            machine.state = STATES.ARMED_HOME;
            msg.action = "armed_notification";
        }
        break;

    case STATES.ARMING:
        if (event === "disarm") {
            machine.state = STATES.DISARMED;
            msg.action = "cancel_arming";
        } else if (event === "timeout") {
            machine.state = machine.nextState;
            msg.action = "armed_notification";
        }
        break;

    case STATES.ARMED_AWAY:
        if (event === "disarm") {
            machine.state = STATES.DISARMED;
            msg.action = "disarmed_notification";
        } else if (event === "sensor_trip") {
            machine.state = STATES.TRIGGERED;
            machine.triggeredBy = payload.sensor;
            msg.action = "trigger_alarm";
        }
        break;

    case STATES.ARMED_HOME:
        if (event === "disarm") {
            machine.state = STATES.DISARMED;
        } else if (event === "sensor_trip" && payload.type === "perimeter") {
            machine.state = STATES.TRIGGERED;
            machine.triggeredBy = payload.sensor;
            msg.action = "trigger_alarm";
        }
        // Interior motion ignored in armed_home
        break;

    case STATES.TRIGGERED:
        if (event === "disarm") {
            machine.state = STATES.DISARMED;
            msg.action = "cancel_alarm";
        }
        // Stay triggered until disarmed
        break;
}

// Log transition
if (machine.state !== previousState) {
    machine.lastTransition = {
        from: previousState,
        to: machine.state,
        event: event,
        time: Date.now()
    };
    node.status({fill: "blue", shape: "dot", text: machine.state});
}

flow.set("securityMachine", machine);

msg.currentState = machine.state;
msg.previousState = previousState;
msg.stateChanged = machine.state !== previousState;

return msg;
```

---

## Hierarchical States

### Nested State Example

```javascript
// Top level: off, on
// On substates: idle, active, cooling_down

const machine = flow.get("hvacMachine") || {
    power: "off",
    mode: null,
    substate: null
};

const event = msg.event;

if (machine.power === "off") {
    if (event === "power_on") {
        machine.power = "on";
        machine.mode = "heat";
        machine.substate = "idle";
    }
} else if (machine.power === "on") {
    // Power-level events
    if (event === "power_off") {
        machine.power = "off";
        machine.mode = null;
        machine.substate = null;
    } else if (event === "change_mode") {
        machine.mode = msg.payload.mode;
    }

    // Substate transitions
    switch (machine.substate) {
        case "idle":
            if (event === "demand") {
                machine.substate = "active";
            }
            break;
        case "active":
            if (event === "satisfied") {
                machine.substate = "cooling_down";
                machine.cooldownStart = Date.now();
            }
            break;
        case "cooling_down":
            if (Date.now() - machine.cooldownStart > 60000) {
                machine.substate = "idle";
            }
            break;
    }
}

flow.set("hvacMachine", machine);
```

---

## State Machine with History

### Remember Previous State

```javascript
const machine = flow.get("machine") || {
    current: "idle",
    history: [],
    maxHistory: 10
};

function transition(newState) {
    machine.history.push({
        from: machine.current,
        to: newState,
        time: Date.now()
    });

    while (machine.history.length > machine.maxHistory) {
        machine.history.shift();
    }

    machine.current = newState;
}

// Can analyze patterns
function wasRecentlyIn(state, withinMs = 60000) {
    return machine.history.some(h =>
        h.to === state &&
        Date.now() - h.time < withinMs
    );
}
```

---

## Timed Transitions

### Auto-Timeout States

```javascript
const TIMEOUTS = {
    "arming": 30000,      // 30 seconds to arm
    "warning": 60000,     // 60 second warning
    "boost": 7200000      // 2 hour boost mode
};

const machine = flow.get("machine");

// Check for timeout
if (TIMEOUTS[machine.state]) {
    const elapsed = Date.now() - machine.stateEnteredAt;
    if (elapsed > TIMEOUTS[machine.state]) {
        // Trigger timeout transition
        msg.event = "timeout";
        msg.timedOutState = machine.state;
        // Process timeout event...
    }
}

// Record state entry time on transition
function transition(newState) {
    machine.current = newState;
    machine.stateEnteredAt = Date.now();
}
```

---

## Parallel States

### Multiple Independent Machines

```javascript
// Run multiple state machines independently
const machines = flow.get("machines") || {
    lighting: { state: "off", brightness: 0 },
    climate: { state: "idle", setpoint: 20 },
    security: { state: "disarmed" }
};

// Process event for appropriate machine
const target = msg.target;  // "lighting", "climate", "security"

if (machines[target]) {
    machines[target] = processMachine(machines[target], msg.event, msg.payload);
}

flow.set("machines", machines);
```

---

## Visualization

### Export State for Dashboard

```javascript
msg.dashboard = {
    currentState: machine.state,
    stateColor: STATE_COLORS[machine.state],
    availableTransitions: getAvailableTransitions(machine.state),
    stateData: machine.data,
    history: machine.history.slice(-5)
};
```

### State Diagram (Mermaid)

```
stateDiagram-v2
    [*] --> disarmed
    disarmed --> arming: arm_away
    disarmed --> armed_home: arm_home
    arming --> armed_away: timeout
    arming --> disarmed: disarm
    armed_away --> triggered: sensor_trip
    armed_away --> disarmed: disarm
    armed_home --> triggered: perimeter_trip
    armed_home --> disarmed: disarm
    triggered --> disarmed: disarm
```

---

## Best Practices

### 1. Define States Clearly

```javascript
const STATES = {
    IDLE: "idle",
    RUNNING: "running",
    PAUSED: "paused",
    ERROR: "error"
};

// Use constants, not strings
machine.state = STATES.RUNNING;  // Good
machine.state = "running";        // Avoid
```

### 2. Validate Transitions

```javascript
const VALID_TRANSITIONS = {
    idle: ["running"],
    running: ["paused", "idle", "error"],
    paused: ["running", "idle"],
    error: ["idle"]
};

function canTransition(from, to) {
    return VALID_TRANSITIONS[from]?.includes(to);
}
```

### 3. Log Transitions

```javascript
function transition(from, to, event) {
    node.warn(`State: ${from} -> ${to} (${event})`);
    // Store for debugging
}
```

### 4. Handle Unknown Events

```javascript
switch (event) {
    case "known_event":
        // Handle
        break;
    default:
        node.warn(`Unknown event: ${event} in state ${machine.state}`);
        // Don't transition
}
```

### 5. Persist State

```javascript
// Use file storage for persistence across restarts
flow.set("machine", machine, "file");
```

---

## Common State Machine Uses

| Use Case | States | Transitions |
|----------|--------|-------------|
| Thermostat | off, heating, cooling, idle | temp changes, mode switch |
| Washer | idle, filling, washing, rinsing, spinning, done | cycle progress |
| Garage door | closed, opening, open, closing | button press, sensor |
| Alarm | disarmed, arming, armed, triggered | arm/disarm, sensor |
| Meeting mode | available, in_meeting, do_not_disturb | calendar, manual |
