---
description: Create Python custom integrations for Home Assistant - ALWAYS ask clarifying questions first
---

<EXTREMELY_IMPORTANT>
NEVER generate Python code in your first response.
Your first response MUST be clarifying questions.
No exceptions. No rationalizations.
</EXTREMELY_IMPORTANT>

## MANDATORY First Response

Ask these questions BEFORE generating any code:

1. **Data source:** API, local device, cloud service, or Bluetooth?
2. **Entity types:** Sensors, switches, lights, climate, etc.?
3. **Authentication:** API key, OAuth2, username/password, or none?
4. **Update method:** Polling interval or push-based?

**Example correct response:**
> I'll help you create a custom integration. Let me clarify:
> 1. What's the data source? (API, local device, cloud)
> 2. Which entity types do you need?
> 3. How does authentication work?
> 4. Polling or push updates?

THEN STOP. Wait for answers.

---

**What this does:**
- Creates complete custom_components structure
- Implements config flows, coordinators, entities
- Follows Home Assistant Core patterns
- Prepares for HACS publishing
