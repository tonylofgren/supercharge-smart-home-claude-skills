# State Machines in Node-RED

Implement complex stateful logic.

## When to Use State Machines

- Appliance monitoring (washing machine cycles)
- Multi-step processes (alarm arming sequence)
- Mode management (home/away/vacation)
- Complex automation sequences
- Processes with defined transitions

## Basic Pattern

```javascript
// Define states
const STATES = {
  IDLE: 'idle',
  ACTIVE: 'active',
  COOLDOWN: 'cooldown'
};

// Get current state from context
let state = flow.get('machineState') || STATES.IDLE;

// Process event
const event = msg.payload;

// State machine logic
switch (state) {
  case STATES.IDLE:
    if (event === 'start') {
      state = STATES.ACTIVE;
    }
    break;

  case STATES.ACTIVE:
    if (event === 'complete') {
      state = STATES.COOLDOWN;
    } else if (event === 'cancel') {
      state = STATES.IDLE;
    }
    break;

  case STATES.COOLDOWN:
    if (event === 'reset') {
      state = STATES.IDLE;
    }
    break;
}

// Save new state
flow.set('machineState', state);
msg.state = state;
return msg;
```

## Washing Machine Example

### States

| State | Description | Power Range |
|-------|-------------|-------------|
| `idle` | Not running | < 5W |
| `filling` | Filling water | 50-100W |
| `washing` | Washing cycle | 200-400W |
| `rinsing` | Rinse cycle | 100-200W |
| `spinning` | Spin cycle | > 400W |
| `done` | Cycle complete | < 5W after active |

### Implementation

```javascript
const STATES = {
  IDLE: 'idle',
  FILLING: 'filling',
  WASHING: 'washing',
  RINSING: 'rinsing',
  SPINNING: 'spinning',
  DONE: 'done'
};

const THRESHOLDS = {
  IDLE: 5,
  FILLING: 50,
  RINSING: 100,
  WASHING: 200,
  SPINNING: 400
};

const power = parseFloat(msg.payload);
let currentState = flow.get('washerState') || STATES.IDLE;
let startTime = flow.get('washerStartTime');

function determineState(power, current) {
  if (power < THRESHOLDS.IDLE) {
    if (current !== STATES.IDLE && current !== STATES.DONE) {
      return STATES.DONE;
    }
    return STATES.IDLE;
  }

  if (power >= THRESHOLDS.SPINNING) return STATES.SPINNING;
  if (power >= THRESHOLDS.WASHING) return STATES.WASHING;
  if (power >= THRESHOLDS.RINSING) return STATES.RINSING;
  if (power >= THRESHOLDS.FILLING) return STATES.FILLING;

  return current;
}

const newState = determineState(power, currentState);

if (newState !== currentState) {
  // State changed
  if (newState === STATES.FILLING && currentState === STATES.IDLE) {
    // New cycle started
    flow.set('washerStartTime', Date.now());
    startTime = Date.now();
  }

  flow.set('washerState', newState);

  msg.previousState = currentState;
  msg.state = newState;
  msg.power = power;

  if (newState === STATES.DONE) {
    const duration = Math.round((Date.now() - startTime) / 60000);
    msg.duration = duration;
    msg.message = `Washing complete after ${duration} minutes`;
    return [msg, msg]; // Output 1: state, Output 2: notification
  }

  return [msg, null];
}

return [null, null];
```

## Alarm System Example

### States

```javascript
const STATES = {
  DISARMED: 'disarmed',
  ARMING: 'arming',
  ARMED_HOME: 'armed_home',
  ARMED_AWAY: 'armed_away',
  PENDING: 'pending',
  TRIGGERED: 'triggered'
};
```

### Transitions

```javascript
const TRANSITIONS = {
  'disarmed': {
    'arm_home': 'arming',
    'arm_away': 'arming'
  },
  'arming': {
    'armed': 'armed_home',  // or armed_away
    'cancel': 'disarmed'
  },
  'armed_home': {
    'disarm': 'disarmed',
    'trigger': 'triggered'
  },
  'armed_away': {
    'disarm': 'pending',
    'trigger': 'triggered'
  },
  'pending': {
    'disarm': 'disarmed',
    'timeout': 'triggered'
  },
  'triggered': {
    'disarm': 'disarmed'
  }
};

function transition(currentState, event) {
  const stateTransitions = TRANSITIONS[currentState];
  if (stateTransitions && stateTransitions[event]) {
    return stateTransitions[event];
  }
  return currentState;
}
```

## Mode Management Example

### Home Mode State Machine

```javascript
const MODES = {
  HOME: 'home',
  AWAY: 'away',
  NIGHT: 'night',
  VACATION: 'vacation'
};

const states = global.get("homeassistant").homeAssistant.states;
let currentMode = flow.get('homeMode') || MODES.HOME;

const anyoneHome = Object.keys(states)
  .filter(id => id.startsWith("person."))
  .some(id => states[id].state === "home");

const hour = new Date().getHours();
const isNightTime = hour >= 23 || hour < 6;
const vacationMode = states["input_boolean.vacation_mode"]?.state === "on";

function determineMode() {
  if (vacationMode) return MODES.VACATION;
  if (!anyoneHome) return MODES.AWAY;
  if (isNightTime && anyoneHome) return MODES.NIGHT;
  return MODES.HOME;
}

const newMode = determineMode();

if (newMode !== currentMode) {
  flow.set('homeMode', newMode);

  msg.previousMode = currentMode;
  msg.mode = newMode;

  return msg;
}

return null;
```

## State History

Track state transitions:

```javascript
// Initialize
let history = flow.get('stateHistory') || [];

// Add transition
const transition = {
  from: previousState,
  to: newState,
  timestamp: new Date().toISOString(),
  trigger: msg.trigger || 'unknown'
};

history.push(transition);

// Keep last 50 transitions
if (history.length > 50) {
  history = history.slice(-50);
}

flow.set('stateHistory', history);
```

## Timed States

States with automatic timeout:

```javascript
// Check for timed states
const timedStates = {
  'arming': { timeout: 60000, nextState: 'armed_away' },
  'pending': { timeout: 30000, nextState: 'triggered' }
};

const currentState = flow.get('alarmState');
const stateEnteredAt = flow.get('stateEnteredAt');

const timedConfig = timedStates[currentState];
if (timedConfig) {
  const elapsed = Date.now() - stateEnteredAt;
  if (elapsed >= timedConfig.timeout) {
    // Auto-transition
    flow.set('alarmState', timedConfig.nextState);
    flow.set('stateEnteredAt', Date.now());
    msg.state = timedConfig.nextState;
    msg.reason = 'timeout';
    return msg;
  }
}
```

## Parallel States

Multiple independent state machines:

```javascript
// Machine 1: Presence
const presenceState = flow.get('presenceState') || 'unknown';

// Machine 2: Mode
const modeState = flow.get('modeState') || 'normal';

// Machine 3: Alarm
const alarmState = flow.get('alarmState') || 'disarmed';

// Combined state
msg.combinedState = {
  presence: presenceState,
  mode: modeState,
  alarm: alarmState
};

// React to combinations
if (presenceState === 'away' && alarmState === 'disarmed') {
  // Should arm alarm
  msg.action = 'arm_alarm';
}
```

## Visualization

Use status to show current state:

```javascript
const stateColors = {
  'idle': 'grey',
  'active': 'green',
  'warning': 'yellow',
  'error': 'red'
};

node.status({
  fill: stateColors[state] || 'blue',
  shape: 'dot',
  text: state
});
```

## Best Practices

1. **Define all states upfront** as constants
2. **Log all transitions** for debugging
3. **Handle unknown states** gracefully
4. **Use timeout protection** for stuck states
5. **Store state in flow context** for persistence
6. **Limit history size** to prevent memory issues
7. **Add status visualization** for monitoring
8. **Document state transitions** clearly

## Flow Structure

```
[trigger] ──> [state machine function] ──> [switch by state] ──> [actions]
                    │
                    └──> [debug/log]
```

The switch node routes to different action nodes based on state:

```json
{
  "type": "switch",
  "property": "state",
  "rules": [
    { "t": "eq", "v": "idle" },
    { "t": "eq", "v": "active" },
    { "t": "eq", "v": "done" }
  ]
}
```
