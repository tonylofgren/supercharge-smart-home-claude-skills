# AI & LLM Integration in Home Assistant

> Guide to integrating AI language models for intelligent home automation

## Overview

Home Assistant supports various AI/LLM integrations for natural language control, intelligent decision-making, and enhanced conversation capabilities. This guide covers both local (Ollama) and cloud-based (OpenAI) options.

---

## Local LLM with Ollama

### Why Local LLM?
- **Privacy**: All processing stays on your network
- **No API costs**: Run unlimited queries
- **Offline capable**: Works without internet
- **Customizable**: Fine-tune for your home

### Ollama Installation

#### Prerequisites
- Linux/macOS/Windows with Docker
- 8GB+ RAM (16GB recommended for larger models)
- GPU optional but recommended (NVIDIA/AMD)

#### Install Ollama

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Docker:**
```yaml
# docker-compose.yml
version: '3'
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]  # For NVIDIA GPU
    restart: unless-stopped

volumes:
  ollama_data:
```

#### Pull a Model

```bash
# Recommended models for home automation
ollama pull llama2          # General purpose, 7B
ollama pull mistral         # Fast, good quality
ollama pull phi             # Small, efficient
ollama pull llama2:13b      # Better quality, needs more RAM
```

### Home Assistant Integration

#### Install via HACS

1. Add custom repository: `https://github.com/acon96/home-llm`
2. Install "Local LLM Conversation" integration
3. Restart Home Assistant

#### Configuration

```yaml
# configuration.yaml
conversation:
  intents:
    # Your custom intents here

# Or configure via UI:
# Settings → Devices & Services → Add Integration → Ollama
```

#### Ollama Configuration

```yaml
# Example via UI configuration:
# Host: http://192.168.1.100:11434 (or localhost:11434)
# Model: mistral
# Temperature: 0.7
# Max tokens: 500
```

### Model Selection Guide

| Model | RAM Required | Speed | Quality | Best For |
|-------|-------------|-------|---------|----------|
| phi | 4GB | Very Fast | Good | Simple commands |
| mistral | 8GB | Fast | Very Good | General use |
| llama2:7b | 8GB | Medium | Good | Balanced |
| llama2:13b | 16GB | Slow | Excellent | Complex tasks |
| mixtral | 32GB | Slow | Best | Advanced reasoning |

### Custom System Prompt for Home Control

```yaml
# In the Ollama conversation agent configuration
system_prompt: |
  You are a helpful home assistant AI. You control a smart home with Home Assistant.

  Available commands you can suggest:
  - Turn on/off lights: "turn on the living room light"
  - Set temperature: "set thermostat to 21 degrees"
  - Check status: "is the front door locked?"
  - Run scenes: "activate movie mode"

  When responding:
  - Be concise and helpful
  - Confirm actions taken
  - Ask clarifying questions if needed
  - Only suggest actions for devices that exist

  Available areas: Living Room, Kitchen, Bedroom, Bathroom, Office
  Available devices: lights, thermostat, locks, covers, media players
```

---

## Extended OpenAI Conversation

### Setup

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Settings → Devices & Services → Add Integration → OpenAI Conversation
3. Enter API key

### Configuration Options

```yaml
# Via UI configuration
conversation_agent:
  model: gpt-4o-mini  # or gpt-4o, gpt-3.5-turbo
  max_tokens: 500
  temperature: 0.7
  top_p: 1.0
```

### Cost Optimization

| Model | Input Cost | Output Cost | Recommendation |
|-------|-----------|-------------|----------------|
| gpt-4o-mini | $0.15/1M | $0.60/1M | Best value |
| gpt-4o | $5/1M | $15/1M | Complex tasks |
| gpt-3.5-turbo | $0.50/1M | $1.50/1M | Legacy |

**Tips to reduce costs:**
- Use gpt-4o-mini for routine queries
- Limit max_tokens to necessary minimum
- Cache common responses
- Use local LLM for high-frequency queries

### Custom Instructions

```yaml
# In OpenAI conversation agent settings
instructions: |
  You control a smart home through Home Assistant.

  Guidelines:
  1. Execute commands by calling Home Assistant services
  2. Confirm actions with brief responses
  3. If unsure, ask for clarification
  4. Never expose sensitive information
  5. Suggest energy-saving alternatives when appropriate

  Home context:
  - Location: Stockholm, Sweden
  - Residents: 2 adults, 1 child
  - Preferences: Energy efficiency, comfort
```

---

## Prompt Engineering for Home Assistant

### Effective System Prompts

#### Basic Home Control

```
You are a smart home assistant. Keep responses brief.
Available actions: lights, climate, covers, locks, media.
Always confirm what you did.
```

#### Context-Aware Assistant

```
You are an intelligent home assistant for the Smith family.

Current context:
- Time: {{ now().strftime('%H:%M') }}
- Weather: {{ states('weather.home') }}
- People home: {{ states('sensor.people_home') }}
- Energy price: {{ states('sensor.electricity_price') }} SEK/kWh

Adjust suggestions based on:
- Time of day (morning routines, bedtime)
- Weather (heating, cooling, blinds)
- Occupancy (away mode, presence)
- Energy prices (defer high-consumption tasks)
```

#### Safety-Focused Prompt

```
You are a home automation assistant with safety constraints.

NEVER:
- Unlock doors without explicit confirmation
- Disable security systems
- Share sensitive information
- Control devices outside approved list

ALWAYS:
- Confirm dangerous actions twice
- Log security-related requests
- Suggest safer alternatives
```

### Intent Extraction Patterns

```yaml
# Custom intent for LLM to recognize
intents:
  SetTemperature:
    description: "Set thermostat to a specific temperature"
    slots:
      temperature:
        type: number
        min: 15
        max: 28
      area:
        type: area
    examples:
      - "Set temperature to {temperature} degrees"
      - "Make it {temperature} in the {area}"
      - "Heat the {area} to {temperature}"

  # LLM should extract and call:
  # service: climate.set_temperature
  # data:
  #   temperature: {{ temperature }}
  # target:
  #   area_id: {{ area }}
```

---

## LLM-Based Automation Decisions

### Template Sensor with LLM Analysis

```yaml
# This is a conceptual example - actual implementation varies
template:
  - sensor:
      - name: "AI Energy Recommendation"
        state: >
          {% set price = states('sensor.electricity_price') | float %}
          {% set solar = states('sensor.solar_production') | float %}
          {% set usage = states('sensor.power_consumption') | float %}
          {% if solar > usage %}
            Use solar surplus
          {% elif price < 0.5 %}
            Low price - run appliances
          {% elif price > 2.0 %}
            High price - minimize usage
          {% else %}
            Normal operation
          {% endif %}
```

### Smart Suggestions Automation

```yaml
automation:
  - id: ai_suggestions
    alias: "AI: Daily Suggestions"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: conversation.process
        data:
          agent_id: conversation.openai
          text: >
            Based on today's weather ({{ states('weather.home') }}),
            energy prices ({{ states('sensor.nordpool_kwh_se3_sek_3_10_025') }}),
            and calendar ({{ states('calendar.family') }}),
            what should I consider for home automation today?
        response_variable: ai_response
      - service: notify.mobile_app
        data:
          title: "AI Home Suggestions"
          message: "{{ ai_response.speech.plain.speech }}"
```

### Natural Language Automation Triggers

```yaml
automation:
  - id: voice_command_handler
    alias: "Handle Voice Commands via LLM"
    trigger:
      - platform: conversation
        command:
          - "I'm going to bed"
          - "Goodnight"
          - "Time to sleep"
    action:
      - service: script.bedtime_routine
      - service: conversation.process
        data:
          agent_id: conversation.ollama
          text: "Confirm bedtime routine started and wish goodnight"
```

---

## Fallback Patterns

### Local to Cloud Failover

```yaml
automation:
  - id: conversation_with_fallback
    alias: "Conversation with Fallback"
    trigger:
      - platform: event
        event_type: conversation_started
    action:
      - choose:
          # Try local first
          - conditions:
              - condition: state
                entity_id: binary_sensor.ollama_available
                state: "on"
            sequence:
              - service: conversation.process
                data:
                  agent_id: conversation.ollama
                  text: "{{ trigger.event.data.text }}"
          # Fallback to cloud
          - conditions:
              - condition: state
                entity_id: binary_sensor.ollama_available
                state: "off"
            sequence:
              - service: conversation.process
                data:
                  agent_id: conversation.openai
                  text: "{{ trigger.event.data.text }}"
```

### Availability Sensor for Ollama

```yaml
binary_sensor:
  - platform: rest
    name: "Ollama Available"
    resource: http://localhost:11434/api/tags
    method: GET
    scan_interval: 60
    value_template: "{{ value_json is defined }}"
```

### Response Caching

```yaml
# Using input_text to cache common responses
input_text:
  cached_weather_response:
    name: "Cached Weather Response"
    max: 500

automation:
  - id: cache_weather_response
    alias: "Cache Weather Response"
    trigger:
      - platform: state
        entity_id: weather.home
    action:
      - service: conversation.process
        data:
          agent_id: conversation.ollama
          text: "Describe current weather: {{ states('weather.home') }}, {{ state_attr('weather.home', 'temperature') }}°C"
        response_variable: response
      - service: input_text.set_value
        target:
          entity_id: input_text.cached_weather_response
        data:
          value: "{{ response.speech.plain.speech }}"
```

---

## Custom Conversation Agents

### Python-Based Agent

```python
# custom_components/my_agent/conversation.py
from homeassistant.components.conversation import AbstractConversationAgent

class MyCustomAgent(AbstractConversationAgent):
    """Custom conversation agent."""

    @property
    def supported_languages(self) -> list[str]:
        return ["en", "sv"]

    async def async_process(
        self,
        user_input: str,
        conversation_id: str | None = None,
        context: Context | None = None
    ) -> ConversationResult:
        """Process user input."""

        # Your custom logic here
        # Can combine multiple LLMs, rules, etc.

        response = await self._process_with_rules(user_input)
        if not response:
            response = await self._process_with_llm(user_input)

        return ConversationResult(
            response=IntentResponse(self.language),
            conversation_id=conversation_id
        )
```

### Integration with Scripts

```yaml
script:
  ai_assisted_decision:
    alias: "AI Assisted Decision"
    fields:
      question:
        description: "Question for AI"
        example: "Should I turn on heating?"
    sequence:
      - service: conversation.process
        data:
          agent_id: conversation.ollama
          text: >
            Context: Temperature is {{ states('sensor.indoor_temp') }}°C,
            outdoor is {{ states('sensor.outdoor_temp') }}°C,
            energy price is {{ states('sensor.electricity_price') }} SEK/kWh.

            Question: {{ question }}

            Respond with only YES or NO.
        response_variable: ai_response
      - variables:
          decision: "{{ ai_response.speech.plain.speech | trim | upper }}"
      - choose:
          - conditions: "{{ decision == 'YES' }}"
            sequence:
              - service: climate.turn_on
                target:
                  entity_id: climate.living_room
```

---

## Best Practices

### Security

1. **Never expose API keys** in logs or responses
2. **Limit LLM capabilities** to safe actions
3. **Require confirmation** for destructive actions
4. **Audit logging** for all LLM-initiated commands

### Performance

1. **Use local LLM** for high-frequency queries
2. **Cache common responses** to reduce API calls
3. **Set reasonable timeouts** (5-10 seconds)
4. **Monitor token usage** for cost control

### Reliability

1. **Implement fallbacks** (local → cloud → predefined)
2. **Handle errors gracefully** with user feedback
3. **Test edge cases** (unclear commands, errors)
4. **Regular model updates** for local LLMs

### User Experience

1. **Keep responses concise** (under 100 words typically)
2. **Confirm actions taken** explicitly
3. **Ask clarifying questions** when ambiguous
4. **Provide alternatives** when request can't be fulfilled

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Ollama not responding | Check if service is running: `ollama list` |
| Slow responses | Use smaller model, add GPU |
| Incorrect commands | Improve system prompt with examples |
| API rate limits | Implement caching, use local LLM |
| Context too long | Reduce max_tokens, summarize history |

### Debug Logging

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    homeassistant.components.conversation: debug
    homeassistant.components.openai_conversation: debug
    custom_components.ollama: debug
```

---

## Resources

- [Home Assistant Conversation](https://www.home-assistant.io/integrations/conversation/)
- [OpenAI Conversation Integration](https://www.home-assistant.io/integrations/openai_conversation/)
- [Ollama Documentation](https://ollama.ai/)
- [Home-LLM Project](https://github.com/acon96/home-llm)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
