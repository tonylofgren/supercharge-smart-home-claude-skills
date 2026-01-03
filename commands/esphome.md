---
description: Create ESPHome device configurations - ALWAYS ask clarifying questions first
---

<EXTREMELY_IMPORTANT>
NEVER generate YAML in your first response.
Your first response MUST be clarifying questions.
No exceptions. No rationalizations.
</EXTREMELY_IMPORTANT>

## MANDATORY First Response

Ask these questions BEFORE generating any code:

1. **Board:** Which ESP board? (ESP32, ESP8266, ESP32-S3, ESP32-C3)
2. **Components:** Which sensors/outputs? (DHT22, BME280, relay, LED strip, etc.)
3. **Pins:** Which GPIO pins are connected?
4. **Features:** WiFi fallback AP? OTA updates? Web server?

**Example correct response:**
> I'll help you create an ESPHome config. Let me clarify:
> 1. Which board? (ESP32, ESP8266, etc.)
> 2. Which sensors/components?
> 3. GPIO pin connections?
> 4. Any special features needed?

THEN STOP. Wait for answers.

---

**What this does:**
- Creates complete ESPHome YAML configs
- Supports 160+ components (sensors, displays, LEDs, etc.)
- Includes WiFi, API, OTA setup
