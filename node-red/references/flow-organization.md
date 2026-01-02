# Flow Organization

## Table of Contents
- [Tab Organization](#tab-organization)
- [Node Naming](#node-naming)
- [Groups](#groups)
- [Comments & Documentation](#comments--documentation)
- [Link Nodes](#link-nodes)
- [Color Coding](#color-coding)
- [Environment Variables](#environment-variables)
- [Version Control](#version-control)

---

## Tab Organization

### By Domain

```
Tabs:
├── Lighting           # All lighting automations
├── Climate            # HVAC, temperature control
├── Security           # Alarms, sensors, cameras
├── Media              # Entertainment systems
├── Notifications      # Alert routing
├── Presence           # Occupancy detection
├── Utilities          # Shared flows, helpers
└── Development        # Testing, debugging
```

### By Room

```
Tabs:
├── Living Room        # All living room automation
├── Bedroom           # Bedroom automations
├── Kitchen           # Kitchen automations
├── Bathroom          # Bathroom automations
├── Garage            # Garage automations
├── Outdoor           # External areas
└── Whole House       # House-wide automation
```

### By Function

```
Tabs:
├── Triggers          # All event sources
├── Logic             # Processing, conditions
├── Actions           # Service calls, outputs
├── Subflows          # Reusable components
└── Debugging         # Test flows
```

### Recommended Structure

```
Tabs (for typical home):
1. Core Services      # HA connection, global helpers
2. Lighting           # All lighting automation
3. Climate            # Heating, cooling, humidity
4. Security           # Alarms, locks, cameras
5. Notifications      # Alert routing
6. Schedules          # Time-based automation
7. Presence           # Occupancy logic
8. Media              # Entertainment
9. Subflows           # Reusable components
10. Debug             # Testing (disable in production)
```

---

## Node Naming

### Naming Convention

```
[Location/Context] Action - Details
```

**Examples:**
```
Living Room - Motion On
Kitchen Light - Turn On
Security - Door Open Alert
Climate - Set Temperature
Notify - Send to John
```

### Good vs Bad Names

| Bad | Good | Why |
|-----|------|-----|
| `trigger-state` | `Living Room Motion` | Describes purpose |
| `function` | `Calculate Brightness` | Explains logic |
| `call-service` | `Turn On Bedroom Light` | Clear action |
| `switch` | `Is Daytime?` | Reveals decision |
| `node1` | `Parse Temperature` | Specific function |

### Naming by Node Type

```javascript
// Triggers
"Motion Sensor - Living Room"
"Front Door - Opened"
"Daily 8:00 AM"

// Conditions/Logic
"Is Dark Outside?"
"Anyone Home?"
"Check Temperature Range"

// Actions
"Turn On Kitchen Light"
"Send Mobile Notification"
"Set HVAC to Heat"

// Helpers
"Parse JSON Response"
"Calculate Average"
"Format Timestamp"
```

---

## Groups

### Creating Groups

1. Select nodes to group
2. Right-click → Group Selection
3. Name the group
4. Optionally set background color

### When to Group

```
✓ Related nodes that work together
✓ Logical sections of a flow
✓ Nodes that share a common purpose
✓ Complex subflows that can't be converted

✗ Don't group unrelated nodes
✗ Don't create overlapping groups
✗ Don't group single nodes
```

### Group Layout

```
┌─────────────────────────────────────────────────────────┐
│ Motion Detection                                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Trigger  │───▶│  Check   │───▶│  Action  │          │
│  │ Motion   │    │  Time    │    │  Lights  │          │
│  └──────────┘    └──────────┘    └──────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Notification Handling                                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  Format  │───▶│  Route   │───▶│   Send   │          │
│  │ Message  │    │  By User │    │  Notify  │          │
│  └──────────┘    └──────────┘    └──────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Comments & Documentation

### Comment Nodes

Add comment nodes to explain:
- Complex logic
- Configuration requirements
- Dependencies
- Author/date information

### Flow Info

Each flow (tab) has an Info section:

```markdown
## Living Room Automation

### Purpose
Controls all living room lighting and media based on presence and time.

### Dependencies
- binary_sensor.motion_living
- light.living_room
- media_player.tv

### Author
Created: 2024-01-15
Updated: 2024-01-20

### Notes
- Motion timeout: 5 minutes
- Override via input_boolean.living_room_manual
```

### Function Node Documentation

```javascript
/**
 * Calculate Brightness Based on Time
 *
 * Input:
 *   msg.payload - Current time (Date or timestamp)
 *
 * Output:
 *   msg.brightness - Calculated brightness (0-255)
 *   msg.colorTemp - Color temperature (153-500)
 *
 * Logic:
 *   - Sunrise-Sunset: Full brightness, neutral color
 *   - Evening: Reduced brightness, warm color
 *   - Night: Minimum brightness, very warm color
 */
const hour = new Date().getHours();
// ... rest of logic
```

---

## Link Nodes

### When to Use Links

```
✓ Connect distant parts of a flow
✓ Avoid cluttered crossing wires
✓ Create flow loops (inject back to start)
✓ Route to centralized handlers

✗ Don't use for adjacent nodes
✗ Don't create confusing link networks
✗ Don't replace proper subflows
```

### Link Naming

```
Link Out:               Link In:
"To: Notifications"     "From: Any Alert"
"To: Error Handler"     "From: Any Flow"
"To: Log Entry"         "From: Logging"
"To: Motion [loop]"     "From: Motion [loop]"
```

### Link Patterns

**Central Hub:**
```
Flow 1 ──▶ [Link Out: To Hub] ════════╗
Flow 2 ──▶ [Link Out: To Hub] ═══════╬═══▶ [Link In: Hub] ──▶ Central Handler
Flow 3 ──▶ [Link Out: To Hub] ════════╝
```

**Error Handler:**
```
Any Flow Error ──▶ [Link Out: Errors] ═══▶ [Link In: Errors] ──▶ Log/Notify
```

**Feedback Loop:**
```
                    ╔═══════════════════════════════╗
                    ║                               ║
Start ──▶ Process ──║──▶ [Link Out: Retry] ──▶ [Link In: Retry]
                    ║                               │
                    ╚═══════════════════════════════╝
```

---

## Color Coding

### By Status

| Color | Meaning |
|-------|---------|
| **Green** | Working, active |
| **Yellow** | Under development |
| **Red** | Disabled, error |
| **Blue** | Information, logging |
| **Gray** | Deprecated, legacy |

### By Domain

| Color | Domain |
|-------|--------|
| **Yellow** | Lighting |
| **Blue** | Climate |
| **Red** | Security |
| **Green** | Presence |
| **Purple** | Media |
| **Orange** | Notifications |

### Setting Colors

1. Select node(s)
2. Right-click → Edit
3. Choose color in appearance section

Or in flow JSON:
```json
{
  "color": "#C0DEED"
}
```

---

## Environment Variables

### Flow-Level Variables

Set in flow properties:
```javascript
// Access in function nodes
const threshold = env.get("MOTION_THRESHOLD") || 300;
const entityPrefix = env.get("ENTITY_PREFIX") || "sensor";
```

### Subflow Variables

Allow customization per instance:
```javascript
// Defined in subflow
{
  "name": "ENTITY_ID",
  "type": "str",
  "value": "light.default"
}

// Access in subflow nodes
const entity = env.get("ENTITY_ID");
```

### Global Settings

In `settings.js`:
```javascript
process.env.HOME_LATITUDE = "59.3293";
process.env.HOME_LONGITUDE = "18.0686";
```

Access:
```javascript
const lat = env.get("HOME_LATITUDE");
```

---

## Version Control

### Exporting Flows

**Full Export:**
Menu → Export → All Flows → Clipboard/File

**Selected Export:**
1. Select nodes/flows
2. Menu → Export → Selected
3. Save as `.json`

### File Structure

```
node-red-flows/
├── flows.json           # Main flow file
├── flows_cred.json      # Credentials (encrypted)
├── README.md            # Documentation
├── flows/               # Individual flow exports
│   ├── lighting.json
│   ├── climate.json
│   └── security.json
└── subflows/            # Reusable subflows
    ├── debounce.json
    └── notify.json
```

### Git Best Practices

```bash
# .gitignore
flows_cred.json          # Never commit credentials
.config.runtime.json
```

```bash
# Commit message format
feat: Add motion lighting for living room
fix: Correct timeout logic in presence detection
refactor: Split notification flow into subflow
docs: Add flow documentation
```

### Comparing Changes

Use JSON diff tools:
- VS Code with JSON diff
- `jq` for command line
- Node-RED Projects feature

---

## Best Practices Summary

1. **Organize by domain** - Lighting, Climate, Security
2. **Name descriptively** - "Living Room Motion" not "trigger1"
3. **Use groups** - Visually separate related nodes
4. **Document flows** - Info sections, comments
5. **Link sparingly** - Only when needed
6. **Color consistently** - Team-wide conventions
7. **Version control** - Regular exports
8. **Clean regularly** - Remove unused nodes/flows

---

## Related References

- [Core Concepts](core-concepts.md) - Node-RED basics
- [Subflows](subflows.md) - Reusable components
- [Best Practices](../CHEATSHEET.md) - Quick reference
