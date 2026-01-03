---
description: Create Home Assistant YAML automations - ALWAYS ask clarifying questions first
---

<EXTREMELY_IMPORTANT>
NEVER generate YAML in your first response.
Your first response MUST be clarifying questions.
No exceptions. No rationalizations.
</EXTREMELY_IMPORTANT>

## MANDATORY First Response

Ask these questions BEFORE generating any code:

1. **Type:** Automation, Blueprint, Script, or Scene?
2. **Format:** UI editor or YAML files?
3. **Entities:** Which specific entity IDs? (e.g., light.living_room)
4. **Options:** Brightness? Conditions? Timing?

**Example correct response:**
> I'll help you create a sunset light automation. Let me clarify:
> 1. Automation or Blueprint?
> 2. UI editor or YAML file?
> 3. Which lights? (entity IDs)
> 4. Any brightness or conditions?

THEN STOP. Wait for answers.

---

**What this does:**
- Creates automations, scripts, scenes, blueprints
- Uses modern syntax (no deprecated service_template/data_template)
- Follows Home Assistant best practices
