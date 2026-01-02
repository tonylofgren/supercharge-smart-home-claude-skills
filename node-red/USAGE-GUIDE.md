# Usage Guide

How to effectively use the Node-RED skill with Claude Code.

---

## Getting Started

### When to Use This Skill

This skill activates when you mention:
- "Node-RED"
- "flow" (in automation context)
- "visual automation"
- "node-red-contrib-home-assistant-websocket"

### Example Prompts

**Basic:**
```
"Create a motion light flow in Node-RED"
"Help me understand the Events: state node"
"Why isn't my trigger firing?"
```

**Intermediate:**
```
"Build presence detection using multiple motion sensors"
"Create a notification system with priority routing"
"Add manual override to my motion light"
```

**Advanced:**
```
"Implement a state machine for my security system"
"Create a subflow for debouncing"
"Optimize my flows for better performance"
```

---

## The Process

When building Node-RED flows, Claude follows this process:

```
┌─────────────────────────────────────────────────┐
│                UNDERSTAND                        │
│  • What entities are involved?                   │
│  • What triggers the automation?                 │
│  • What conditions apply?                        │
│  • What actions should occur?                    │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│                  DESIGN                          │
│  • Choose appropriate node types                 │
│  • Plan message flow                             │
│  • Consider edge cases                           │
│  • Plan error handling                           │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│                 IMPLEMENT                        │
│  • Build flow step by step                       │
│  • Configure each node properly                  │
│  • Add debug nodes for testing                   │
│  • Document complex logic                        │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│                  VALIDATE                        │
│  • Review node configurations                    │
│  • Check for common mistakes                     │
│  • Verify error handling                         │
│  • Test edge cases                               │
└─────────────────────────────────────────────────┘
```

---

## Working with Flows

### Flow JSON Format

Claude can provide flows in two formats:

**1. JSON Export (Recommended)**
```json
[
  {"id": "node1", "type": "inject", ...},
  {"id": "node2", "type": "function", ...}
]
```

Import: Menu → Import → Paste JSON → Import

**2. Step-by-Step Instructions**
```
1. Add inject node
2. Configure: repeat every 1 minute
3. Add function node
4. Wire inject to function
5. Paste this code: ...
```

### Using Templates

Templates are provided in `templates/` directory:

1. Open the template file
2. Copy the JSON content
3. In Node-RED: Menu → Import → Paste
4. Click Import
5. Configure entity IDs for your setup
6. Deploy

---

## Best Practices for Prompts

### Be Specific

**Good:**
```
"Create a flow that turns on light.living_room when
binary_sensor.motion_living_room detects motion,
but only after sunset, and turns off after 5 minutes
of no motion"
```

**Vague:**
```
"Make a motion light"
```

### Provide Context

**Good:**
```
"I have Zigbee motion sensors (binary_sensor.motion_*)
and Hue lights (light.*). I want presence detection
that combines multiple sensors with a 10-minute timeout."
```

**Missing context:**
```
"Help with presence detection"
```

### Mention Requirements

**Good:**
```
"Build a notification system that:
- Routes based on priority
- Only notifies people who are away
- Rate limits to prevent spam
- Aggregates low-priority for daily digest"
```

**Incomplete:**
```
"Make notifications smarter"
```

---

## Asking for Help

### Debugging Help

Provide:
1. What you expected to happen
2. What actually happens
3. Relevant node configurations
4. Any error messages

**Example:**
```
"My motion light flow triggers but the light doesn't turn on.

Trigger node: Events: state on binary_sensor.motion_living
Service node: light.turn_on on light.living_room

The trigger fires (I see debug output) but the service
call doesn't seem to do anything. No errors in log."
```

### Understanding Nodes

Ask about specific aspects:
```
"What's the difference between Events: state and Trigger: state?"
"When should I use Current State vs Poll State?"
"How do constraints work in trigger nodes?"
```

### Code Review

Share your flow:
```
"Can you review this flow for issues?
[paste JSON]

It's supposed to track room presence but sometimes
misses when people leave."
```

---

## Common Requests

| Request | How to Ask |
|---------|-----------|
| New flow | "Create a flow for [automation]" |
| Fix issue | "My [flow] isn't working: [symptoms]" |
| Optimize | "How can I improve [flow]?" |
| Explain | "What does [node/pattern] do?" |
| Convert | "Convert this HA automation to Node-RED: [yaml]" |
| Best practice | "What's the best way to [task]?" |

---

## Reference Materials

### Quick Reference

Use `CHEATSHEET.md` for:
- Message structure
- Context storage syntax
- Service call formats
- Common patterns

### Detailed Documentation

Use `references/` for:
- Node configuration details
- Pattern implementations
- Troubleshooting guides
- Best practices

### Ready-to-Use Code

Use `templates/` for:
- Working flow examples
- Subflows
- Common automations

---

## Tips for Success

### Start Simple

1. Get basic functionality working
2. Add features incrementally
3. Test after each change

### Use Debug Nodes

- Add debug after triggers to confirm activation
- Add debug before services to verify data
- Use `node.status()` for visual feedback

### Handle Errors

- Add Catch nodes for error handling
- Validate inputs before processing
- Use null checks for optional data

### Document Your Work

- Name nodes descriptively
- Add comment nodes for complex logic
- Use groups to organize related nodes

---

## Getting More Help

### Clarification

If Claude's response doesn't match your needs:
```
"That's not quite what I meant. I need [clarification]"
"Can you modify that to also handle [case]?"
"I'm using [specific setup], does that change anything?"
```

### More Detail

```
"Can you explain how the [specific part] works?"
"What happens if [edge case]?"
"Are there alternatives to this approach?"
```

### Step by Step

```
"Walk me through setting up [feature] step by step"
"Explain each node in this flow"
"How do I test this properly?"
```
