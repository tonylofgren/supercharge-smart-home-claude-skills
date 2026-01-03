# Node-RED Usage Guide

How to use the Node-RED skill effectively with Claude.

## When to Use This Skill

Use when:
- Building Node-RED flows for home automation
- Integrating with Home Assistant via Node-RED
- Creating visual automations
- Using node-red-contrib-home-assistant-websocket
- Debugging flow issues

## Getting Started

### 1. Describe Your Goal

Be specific about what you want to automate:

```
Good: "Turn on the living room light when motion is detected,
      but only after sunset and only if the light is off"

Bad: "Make a motion light"
```

### 2. Provide Context

Include relevant details:
- Entity IDs if you know them
- Any conditions or constraints
- Whether it should work with existing flows
- Special requirements (quiet hours, manual override, etc.)

### 3. Review the Generated Flow

Claude will provide:
- JSON that can be imported directly
- Explanation of how it works
- Configuration steps
- Any entities you need to create in HA

---

## Example Requests

### Simple Automation

```
Create a Node-RED flow that turns off all lights when I leave home.
The person entity is person.john.
```

### Complex Automation

```
I need a motion-activated light for my hallway that:
- Only activates when lux is below 50
- Stays on for 2 minutes after last motion
- Has a manual override that disables automation for 30 minutes
- Uses different brightness during night (10%) vs day (100%)
```

### Debugging

```
My motion light flow isn't working. Here's my current flow:
[paste JSON]
The light doesn't turn off after the timeout.
```

### Integration

```
I want to send a Telegram notification when my washing machine
finishes. The power sensor is sensor.washing_machine_power.
The machine is "done" when power drops below 5W for 30 seconds.
```

---

## Importing Flows

### From JSON

1. Copy the JSON Claude provides
2. In Node-RED: Menu → Import
3. Paste and click Import
4. Position the nodes
5. Configure server node (select your HA server)
6. Deploy

### Configure After Import

Most flows need configuration:

1. **Server nodes** - Select your Home Assistant server
2. **Entity IDs** - Update `CHANGE_ME` placeholders
3. **Thresholds** - Adjust values for your environment
4. **Names** - Rename for your preference

---

## Best Practices

### 1. Start Simple

Build incrementally:
```
Step 1: Basic trigger and action
Step 2: Add conditions
Step 3: Add error handling
Step 4: Add logging/notifications
```

### 2. Test Before Deploying

Use inject nodes to simulate triggers:
```
[inject: test] → [your flow] → [debug]
```

### 3. Use Debug Nodes

Add debug nodes at each stage:
```
[trigger] → [debug] → [logic] → [debug] → [action] → [debug]
```

### 4. Document Your Flows

Add comment nodes explaining:
- What the flow does
- Required configuration
- Dependencies

---

## Understanding Output

### JSON Flow Output

Claude provides importable JSON:

```json
[
  {
    "id": "...",
    "type": "trigger-state",
    "name": "Motion Detected",
    "entityId": "binary_sensor.motion",
    ...
  },
  ...
]
```

### Configuration Instructions

Look for `CHANGE_ME` markers:
```
1. Update entity ID: binary_sensor.motion_CHANGE_ME
2. Set your timeout value in the function node
3. Select your notification service
```

### Wiring Diagrams

Text representation of flow:
```
[Motion Trigger] → [Check Lux] → [Turn On Light]
                        ↓
                   [Do Nothing]
```

---

## Troubleshooting

### Flow Doesn't Work

1. Check server connection (green status)
2. Verify entity IDs exist in HA
3. Add debug nodes to trace message flow
4. Check constraints and conditions

### Import Errors

- Ensure complete JSON (opening and closing brackets)
- Check for version compatibility
- Verify required nodes are installed

### Ask for Help

Provide:
1. What you expected to happen
2. What actually happens
3. Your current flow JSON
4. Error messages if any

---

## Templates

### Quick Start Templates

The skill includes ready-to-use templates:

| Template | Use Case |
|----------|----------|
| basic-motion-light.json | Simple motion lighting |
| advanced-motion-light.json | Motion with conditions |
| presence-detection.json | Who's home tracking |
| notification-router.json | Smart notifications |
| climate-control.json | Temperature automation |
| security-alerts.json | Door/window monitoring |
| energy-monitor.json | Power consumption |
| scene-controller.json | Scene activation |

Request a template:
```
Give me the basic-motion-light template
```

---

## Common Patterns

### Motion Light

```
Motion sensor → Check conditions → Turn on light → Wait → Turn off
```

### Presence Automation

```
Person state → First/last detection → Actions for arrive/leave
```

### Notification

```
Event → Check quiet hours → Route to recipients → Send
```

### Climate

```
Temperature sensor → Compare to target → Heat on/off
```

### Security

```
Door/window sensor → Check if away → Alert if open
```

---

## What Claude Can Do

### Generate

- Complete flows from descriptions
- Individual node configurations
- Function node JavaScript
- JSONata expressions
- Subflows

### Debug

- Analyze existing flows
- Identify issues
- Suggest fixes
- Explain error messages

### Explain

- How flows work
- Node configurations
- Best practices
- HA integration concepts

### Optimize

- Performance improvements
- Error handling
- Code organization
- Flow structure

---

## What Claude Cannot Do

### Limitations

- Access your actual Node-RED instance
- Test flows in your environment
- See your entity IDs (you must provide them)
- Install nodes for you

### You Must

- Import flows manually
- Configure server connections
- Update entity IDs
- Deploy changes
- Test in your environment

---

## Getting Better Results

### Be Specific

```
Instead of: "Make an automation"
Say: "Create a Node-RED flow that [specific behavior]"
```

### Provide Entities

```
Motion sensor: binary_sensor.hallway_motion
Light: light.hallway
Lux sensor: sensor.hallway_lux (optional)
```

### Describe Behavior

```
When motion is detected:
- If lux is below 30
- And time is after sunset
- Turn on light at 80% brightness
- After 3 minutes of no motion, turn off
```

### Mention Constraints

```
- Don't trigger during sleep mode
- Maximum 10 notifications per hour
- Only on weekdays
```

---

## Example Conversation

**You:**
```
Create a Node-RED flow that sends me a notification
when the front door has been open for more than 5 minutes.
Door sensor: binary_sensor.front_door
Notification service: notify.mobile_app_phone
```

**Claude:**
```
Here's a flow for door-open alerts:

[JSON flow...]

Configuration:
1. Import the flow
2. Select your HA server
3. Deploy

How it works:
1. Triggers when door opens
2. Waits 5 minutes
3. If door still open, sends notification
4. Resets if door closes before 5 minutes

The flow uses a trigger node with extend:true
to reset the timer if the door closes and reopens.
```

---

## Reference Documents

The skill includes detailed references:

| Document | Contents |
|----------|----------|
| node-reference.md | All 31 HA nodes |
| cookbook.md | Common code recipes |
| troubleshooting.md | Problem solutions |
| automation-patterns.md | Design patterns |
| function-nodes.md | JavaScript guide |
| error-handling.md | Error patterns |

