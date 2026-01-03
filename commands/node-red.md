---
description: Create Node-RED flows for Home Assistant - ALWAYS ask clarifying questions first
---

<EXTREMELY_IMPORTANT>
NEVER generate JSON flow in your first response.
Your first response MUST be clarifying questions.
No exceptions. No rationalizations.
</EXTREMELY_IMPORTANT>

## MANDATORY First Response

Ask these questions BEFORE generating any code:

1. **Trigger:** What starts the flow? (state change, time, webhook, etc.)
2. **Entities:** Which Home Assistant entity IDs?
3. **Actions:** What should happen? (turn on lights, send notification, etc.)
4. **Conditions:** Any filtering? (only at night, only when home, etc.)

**Example correct response:**
> I'll help you create a Node-RED flow. Let me clarify:
> 1. What triggers the flow?
> 2. Which HA entities are involved?
> 3. What actions should occur?
> 4. Any conditions to check?

THEN STOP. Wait for answers.

---

**What this does:**
- Uses node-red-contrib-home-assistant-websocket nodes
- Generates importable JSON flows
- Follows current API (trigger-state, api-call-service)
