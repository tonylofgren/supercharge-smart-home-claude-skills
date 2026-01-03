# Flow Organization in Node-RED

Structure flows for maintainability.

## Tabs (Flows)

### One Purpose Per Tab

```
[Motion Lights]     - All motion-triggered lighting
[Presence]          - Who's home detection
[Climate]           - Temperature automation
[Notifications]     - Alert routing
[Security]          - Door/window monitoring
```

### Tab Properties

```json
{
  "type": "tab",
  "label": "Motion Lights",
  "info": "Motion-triggered lighting automation.\n\nAreas:\n- Living Room\n- Kitchen\n- Hallway"
}
```

Use `info` for documentation that appears in sidebar.

---

## Naming Conventions

### Nodes

| Type | Convention | Example |
|------|------------|---------|
| Trigger | `[Area] [Event]` | `Living Room Motion` |
| Function | `[Verb] [Object]` | `Check Brightness` |
| Action | `[Action] [Target]` | `Turn On Lights` |
| Debug | `[What]` | `Motion State` |

### Entity References

```javascript
// Consistent naming in function nodes
const ENTITY_IDS = {
  motion: "binary_sensor.living_room_motion",
  light: "light.living_room",
  lux: "sensor.living_room_lux"
};
```

---

## Groups

Visual grouping for related nodes.

### Creating Groups

1. Select nodes
2. Ctrl+G (or menu)
3. Name the group

### Group Naming

```
[Area - Function]
Living Room - Motion Lights
Kitchen - Appliance Monitor
```

### Group Colors

| Color | Purpose |
|-------|---------|
| Default (light blue) | Normal automation |
| Green | Working, tested |
| Yellow | Needs configuration |
| Red | Error handling |
| Purple | External integrations |

---

## Link Nodes

Connect flows on same tab without wires.

### When to Use

- Avoid crossing wires
- Connect distant nodes
- Create reusable endpoints

### Link Node Pairs

```
[link out: "To Notification"]  →  [link in: "From Any"]
```

### Naming

```
Out: "To [Destination]"
In: "From [Source]" or "[Purpose]"
```

### Cross-Flow Links

Link nodes can connect across tabs:

```
[Tab: Motion] → [link out: "Alert"] → [Tab: Notifications] → [link in: "Alerts"]
```

---

## Comment Nodes

Document your flows.

### Header Comments

```
📋 MOTION LIGHTS
Automatically control lights based on motion.
Respects manual overrides and lux levels.
```

### Section Comments

```
--- TRIGGERS ---
[trigger nodes here]

--- LOGIC ---
[function nodes here]

--- ACTIONS ---
[action nodes here]
```

### Configuration Comments

```
⚙️ CONFIGURATION
Update these entity IDs:
- motion_sensor: binary_sensor.YOUR_MOTION
- light_entity: light.YOUR_LIGHT
- lux_sensor: sensor.YOUR_LUX (optional)
```

---

## Flow Layout

### Left to Right

```
[Input] → [Process] → [Output]

[Triggers]    [Logic]    [Actions]    [Debug]
     ↓           ↓          ↓           ↓
   x=100      x=300      x=500       x=700
```

### Vertical Alignment

Align related nodes vertically:

```
[Motion A] → [Logic] → [Light A]
                ↓
[Motion B] → [Logic] → [Light B]
                ↓
[Motion C] → [Logic] → [Light C]
```

### Spacing

| Direction | Spacing |
|-----------|---------|
| Horizontal | 200px between stages |
| Vertical | 60px between parallel nodes |

---

## Subflow Organization

### When to Create Subflow

- Same pattern used 3+ times
- Complex logic that should be abstracted
- Configurable automation component

### Subflow Naming

```
[Category] - [Function]
Lighting - Motion Timer
Notify - Smart Router
Climate - Hysteresis Controller
```

### Environment Variables

Define in subflow properties:

```json
{
  "env": [
    {
      "name": "TIMEOUT",
      "type": "num",
      "value": "300"
    },
    {
      "name": "ENTITY_ID",
      "type": "str",
      "value": ""
    }
  ]
}
```

---

## Configuration Patterns

### Config at Top

```
[comment: ⚙️ CONFIG] ← User updates here
         ↓
    [inject: Init]
         ↓
    [function: Set Config] → [context storage]
         ↓
    [... rest of flow ...]
```

### Function Node Config

```javascript
// === CONFIGURATION ===
const CONFIG = {
  // Update these values
  motionEntity: "binary_sensor.motion_CHANGE_ME",
  lightEntity: "light.living_room_CHANGE_ME",
  timeout: 300,          // seconds
  minBrightness: 20,     // percent
  maxBrightness: 100     // percent
};
// === END CONFIGURATION ===

// ... rest of code uses CONFIG object
```

### Input Number for Runtime Config

```javascript
const states = global.get("homeassistant").homeAssistant.states;
const timeout = parseFloat(states["input_number.motion_timeout"]?.state) || 300;
```

---

## Error Handling Layout

### Catch Node Placement

```
[Main Flow Nodes]
        ↓
[Catch] → [Error Handler] → [Notify/Log]
```

### Dedicated Error Tab

For complex flows:

```
[Tab: Error Handling]
├── [catch all: Flow 1] → [handler]
├── [catch all: Flow 2] → [handler]
└── [catch all: Flow 3] → [handler]
                              ↓
                         [unified logging]
                              ↓
                         [notification]
```

---

## Import/Export

### Selecting for Export

1. Select nodes (Ctrl+click or box select)
2. Ctrl+E to export
3. Copy JSON

### Tab Export

Right-click tab → Export → Selected Flow

### Clipboard vs Download

- Clipboard: Quick sharing
- Download: Backup/version control

---

## Version Control Integration

### Export Strategy

```
node-red-flows/
├── flows.json              # Full export (backup)
├── motion-lights.json      # Individual flow
├── presence.json
└── README.md
```

### Git Workflow

```bash
# Export flow
# Commit
git add flows/*.json
git commit -m "Update motion light timeout logic"
```

### Flow Diffs

JSON diffs are hard to read. Consider:
- Export with compact format
- Use node IDs that are meaningful
- Comment major changes

---

## Documentation Standards

### Flow Documentation

Each tab should have:

1. **Info section** (in tab properties)
2. **Header comment** with overview
3. **Config section** with placeholders
4. **Section comments** for stages

### Example Documentation

```markdown
# Motion Lights Flow

## Purpose
Automatically control lights based on motion detection.

## Entities Required
- binary_sensor.motion_* - Motion sensors
- light.* - Lights to control
- sensor.*_lux - Optional lux sensors

## Configuration
1. Update entity IDs in Config function
2. Set timeout in input_number helper
3. Adjust brightness levels as needed

## Behavior
- Motion detected → Light on
- No motion for X seconds → Light off
- Respects manual override for 30 minutes
```

---

## Maintenance Tips

### Regular Cleanup

1. Remove disabled/unused nodes
2. Update outdated comments
3. Check for deprecated nodes
4. Review error logs

### Debugging Aids

```
[flow] → [debug: Always On] ← Keep for troubleshooting
           ↓
        [debug: Detailed] ← Enable when debugging
```

### Status Nodes

Show flow health:

```javascript
// In function node
node.status({
  fill: "green",
  shape: "dot",
  text: `Active: ${count} triggers today`
});
```

---

## Anti-Patterns

### ❌ Spaghetti Wires

Crossing, tangled wires → Use link nodes

### ❌ Giant Functions

500+ line function → Break into stages

### ❌ Magic Numbers

```javascript
if (lux < 50) // What does 50 mean?
```

→ Use named constants

### ❌ No Documentation

Returning to flow months later → Add comments

### ❌ Duplicate Logic

Same code in 5 functions → Create subflow

---

## Quick Reference

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Select All | Ctrl+A |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Export | Ctrl+E |
| Import | Ctrl+I |
| Search | Ctrl+F |
| Deploy | Ctrl+D |
| Group | Ctrl+G |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |

### Node Arrangement

| Action | Shortcut |
|--------|----------|
| Align Left | A, L |
| Align Right | A, R |
| Align Top | A, T |
| Align Bottom | A, B |
| Distribute H | D, H |
| Distribute V | D, V |

