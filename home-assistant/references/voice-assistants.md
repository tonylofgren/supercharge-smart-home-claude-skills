# Voice Assistants Reference

## Table of Contents
- [Overview](#overview)
- [Assist Pipeline](#assist-pipeline)
- [Local Voice Processing](#local-voice-processing)
- [Speech-to-Text (Whisper)](#speech-to-text-whisper)
- [Text-to-Speech (Piper)](#text-to-speech-piper)
- [Wyoming Protocol](#wyoming-protocol)
- [Voice Satellites](#voice-satellites)
- [Custom Sentences](#custom-sentences)
- [Conversation Agents](#conversation-agents)
- [Cloud Voice Services](#cloud-voice-services)
- [Troubleshooting](#troubleshooting)

---

## Overview

### Voice Control Architecture

```
Voice Input
    │
    ├── Wake Word Detection (optional)
    │
    ├── Speech-to-Text (STT)
    │   ├── Local: Whisper, faster-whisper
    │   └── Cloud: Google, Azure
    │
    ├── Intent Recognition
    │   ├── Home Assistant Conversation
    │   └── Custom intents
    │
    ├── Action Execution
    │
    └── Text-to-Speech (TTS)
        ├── Local: Piper
        └── Cloud: Google, Amazon, Azure
```

### Options Overview

| Component | Local Options | Cloud Options |
|-----------|---------------|---------------|
| Wake Word | openWakeWord | - |
| STT | Whisper, faster-whisper | Google, Azure |
| Intent | HA Conversation | - |
| TTS | Piper | Google, Amazon, Azure |

---

## Assist Pipeline

### What is Assist?

Assist is Home Assistant's built-in voice assistant framework, introduced in 2023. It allows voice control entirely local or hybrid with cloud services.

### Pipeline Configuration

```markdown
## Settings > Voice assistants > Add assistant

Pipeline Components:
1. Conversation agent (required)
2. Speech-to-text engine (for voice input)
3. Text-to-speech engine (for voice output)
4. Wake word (for hands-free activation)
```

### Default Pipeline Setup

```markdown
## Create Basic Pipeline
1. Settings > Voice assistants
2. "Add assistant"
3. Name: "Home Assistant"
4. Conversation agent: "Home Assistant"
5. STT: Whisper (if installed)
6. TTS: Piper (if installed)
7. Language: Your language
```

### Multiple Pipelines

```yaml
# Use different pipelines for different purposes

# Pipeline 1: Living Room (local, fast)
- STT: faster-whisper (small model)
- TTS: Piper (fast voice)
- Wake word: "Hey Jarvis"

# Pipeline 2: Bedroom (quiet, high quality)
- STT: Whisper (medium model)
- TTS: Piper (high quality voice)
- Wake word: "OK Home"

# Pipeline 3: Mobile (cloud, reliable)
- STT: Google Cloud
- TTS: Google Cloud
- No wake word (button activated)
```

---

## Local Voice Processing

### Benefits of Local Processing

| Benefit | Description |
|---------|-------------|
| **Privacy** | Voice never leaves your home |
| **Reliability** | Works without internet |
| **Speed** | No cloud latency (with good hardware) |
| **Cost** | No cloud API fees |

### Hardware Requirements

```markdown
## Minimum (slow but works)
- Raspberry Pi 4 (4GB)
- Basic STT/TTS quality

## Recommended
- x86_64 with 8GB+ RAM
- SSD storage
- Good STT/TTS quality

## Optimal
- Modern CPU (Intel 10th gen+, AMD Ryzen)
- 16GB+ RAM
- GPU (NVIDIA) for faster processing
- Excellent quality and speed
```

### Add-on Installation

```markdown
## Whisper Add-on (STT)
1. Settings > Add-ons
2. Search "Whisper"
3. Install "Whisper"
4. Start add-on
5. Integration auto-discovered

## Piper Add-on (TTS)
1. Settings > Add-ons
2. Search "Piper"
3. Install "Piper"
4. Start add-on
5. Integration auto-discovered

## openWakeWord Add-on
1. Settings > Add-ons
2. Search "openWakeWord"
3. Install and start
4. Configure wake words
```

---

## Speech-to-Text (Whisper)

### Whisper Overview

Whisper is OpenAI's speech recognition model, available locally through Home Assistant.

### Model Sizes

| Model | Size | Speed | Accuracy | RAM |
|-------|------|-------|----------|-----|
| tiny | 75MB | Very fast | Basic | 1GB |
| base | 142MB | Fast | Good | 1GB |
| small | 488MB | Medium | Better | 2GB |
| medium | 1.5GB | Slow | Great | 5GB |
| large | 3GB | Very slow | Best | 10GB |

### Add-on Configuration

```yaml
# Whisper Add-on Configuration

# Model selection
model: small  # tiny, base, small, medium, large-v2
language: sv  # ISO language code or "auto"

# Performance tuning
beam_size: 5  # Higher = more accurate, slower
compute_type: int8  # float32, float16, int8

# For faster-whisper (recommended)
# Uses CTranslate2 for better performance
```

### Language Support

```yaml
# Auto-detect language
language: auto

# Force specific language
language: en  # English
language: sv  # Swedish
language: de  # German
language: fr  # French
language: es  # Spanish
# ... 90+ languages supported
```

### faster-whisper Alternative

```markdown
## Benefits over standard Whisper
- 4x faster transcription
- Lower memory usage
- Same accuracy

## Installation
1. Use "Whisper" add-on
2. Configuration > compute_type: int8
3. This enables faster-whisper mode
```

---

## Text-to-Speech (Piper)

### Piper Overview

Piper is a fast, local neural text-to-speech system with natural-sounding voices.

### Voice Selection

```markdown
## Download Voices
1. Settings > Voice assistants
2. Click Piper TTS engine
3. Browse available voices
4. Download desired voices

## Voice Quality Levels
- Low: Faster, robotic
- Medium: Balanced
- High: Slower, natural
```

### Available Languages

| Language | Voices | Quality |
|----------|--------|---------|
| English (US) | 10+ | Excellent |
| English (UK) | 5+ | Good |
| German | 5+ | Good |
| French | 3+ | Good |
| Spanish | 3+ | Good |
| Swedish | 2+ | Good |
| Dutch | 2+ | Good |
| More... | Varies | Varies |

### Configuration

```yaml
# Piper Add-on Configuration

# Default voice
voice: en_US-lessac-medium

# Voice speed (0.5 - 2.0)
speaker: 0
length_scale: 1.0  # 1.0 = normal, <1 = faster

# Audio settings
sample_rate: 22050
```

### Custom TTS Automation

```yaml
# Use specific voice for notifications
automation:
  - id: doorbell_announce
    alias: "Doorbell Announcement"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: tts.speak
        target:
          entity_id: tts.piper
        data:
          media_player_entity_id: media_player.living_room
          message: "Someone is at the front door"
          options:
            voice: en_US-lessac-medium
```

---

## Wyoming Protocol

### What is Wyoming?

Wyoming is a protocol that allows voice components to communicate over the network. It enables distributed voice processing.

### Architecture

```
┌──────────────────────┐
│   Voice Satellite    │
│   (ESPHome/Pi/etc)   │
└──────────┬───────────┘
           │ Wyoming Protocol
           │
┌──────────▼───────────┐
│   Home Assistant     │
│   ┌────────────────┐ │
│   │ Assist Pipeline│ │
│   │ - Whisper STT  │ │
│   │ - Piper TTS    │ │
│   │ - Wake Word    │ │
│   └────────────────┘ │
└──────────────────────┘
```

### Wyoming Services

```yaml
# Wyoming satellite connection
# Auto-discovered when on same network

# Manual configuration (if needed)
# Settings > Devices & Services > Wyoming

# Port assignments:
# - STT (Whisper): 10300
# - TTS (Piper): 10200
# - Wake Word: 10400
# - Satellite: 10700
```

---

## Voice Satellites

### ESPHome Voice Satellite

Complete voice assistant using ESP32-S3 with microphone and speaker.

```yaml
# ESPHome configuration for voice satellite
esphome:
  name: voice-satellite
  platform: ESP32
  board: esp32-s3-devkitc-1

# Enable voice assistant
voice_assistant:
  microphone: mic
  speaker: speaker
  use_wake_word: true

  on_wake_word_detected:
    - light.turn_on:
        id: led
        effect: pulse

  on_stt_end:
    - light.turn_off:
        id: led

# I2S Microphone
i2s_audio:
  - id: i2s_in
    i2s_lrclk_pin: GPIO3
    i2s_bclk_pin: GPIO2

microphone:
  - platform: i2s_audio
    id: mic
    i2s_audio_id: i2s_in
    i2s_din_pin: GPIO4
    adc_type: external
    pdm: false

# I2S Speaker
speaker:
  - platform: i2s_audio
    id: speaker
    i2s_audio_id: i2s_out
    dac_type: external
    i2s_dout_pin: GPIO5
```

### M5Stack ATOM Echo

Popular pre-built voice satellite option.

```yaml
# ESPHome for M5Stack ATOM Echo
esphome:
  name: m5stack-atom-echo
  friendly_name: Atom Echo

esp32:
  board: m5stack-atom
  framework:
    type: esp-idf

voice_assistant:
  microphone: mic
  speaker: speaker
  use_wake_word: true

i2s_audio:
  - id: i2s_audio_bus
    i2s_lrclk_pin: GPIO33
    i2s_bclk_pin: GPIO19

microphone:
  - platform: i2s_audio
    id: mic
    adc_type: external
    i2s_din_pin: GPIO23
    pdm: true

speaker:
  - platform: i2s_audio
    id: speaker
    dac_type: external
    i2s_dout_pin: GPIO22
    mode: mono
```

### Raspberry Pi Satellite

```markdown
## Hardware Required
- Raspberry Pi 3/4/Zero 2W
- USB microphone or I2S mic (ReSpeaker)
- Speaker (3.5mm or I2S)

## Software Setup
1. Install Wyoming Satellite
   pip install wyoming-satellite

2. Configure and run
   wyoming-satellite \
     --name "Living Room" \
     --uri tcp://0.0.0.0:10700 \
     --mic-command "arecord -D plughw:1,0 -r 16000 -c 1 -f S16_LE -t raw" \
     --snd-command "aplay -D plughw:0,0 -r 22050 -c 1 -f S16_LE -t raw"
```

### Commercial Options

| Device | Status | Notes |
|--------|--------|-------|
| Home Assistant Voice PE | Announced | Official satellite |
| Seeed ReSpeaker | Supported | USB or HAT |
| M5Stack ATOM Echo | Popular | Budget option |
| ESP32-S3-BOX | Supported | Dev board with screen |

---

## Custom Sentences

### Intent Recognition

Home Assistant uses custom sentences to understand voice commands.

### Built-in Intents

```markdown
## Supported Commands (out of box)
- "Turn on/off the [device]"
- "Open/close the [cover]"
- "Set [device] to [value]"
- "What is the [sensor]?"
- "Lock/unlock the [lock]"
- "What's the weather?"
- "What time is it?"
```

### Custom Sentences Configuration

```yaml
# custom_sentences/en/intents.yaml
language: en
intents:
  # Custom intent for movie mode
  MovieMode:
    data:
      - sentences:
          - "movie time"
          - "start movie mode"
          - "I want to watch a movie"
          - "movie night"

  # Custom intent for bedtime
  GoodNight:
    data:
      - sentences:
          - "good night"
          - "bedtime"
          - "I'm going to bed"
          - "time for bed"

  # Intent with slots
  SetRoomTemperature:
    data:
      - sentences:
          - "set {room} temperature to {temperature}"
          - "make {room} {temperature} degrees"
        slots:
          room:
            - living room
            - bedroom
            - kitchen
          temperature:
            - type: number
              min: 16
              max: 28
```

### Intent Scripts

```yaml
# intent_script.yaml
intent_script:
  MovieMode:
    speech:
      text: "Starting movie mode. Enjoy your movie!"
    action:
      - service: script.turn_on
        target:
          entity_id: script.movie_mode

  GoodNight:
    speech:
      text: "Good night! Setting everything up for sleep."
    action:
      - service: script.turn_on
        target:
          entity_id: script.goodnight_routine

  SetRoomTemperature:
    speech:
      text: "Setting {{ room }} to {{ temperature }} degrees."
    action:
      - service: climate.set_temperature
        target:
          entity_id: "climate.{{ room | replace(' ', '_') }}"
        data:
          temperature: "{{ temperature }}"
```

### Sentence Templates with Wildcards

```yaml
# Match flexible phrases
intents:
  PlayMusic:
    data:
      - sentences:
          - "play {music} in {room}"
          - "play {music}"
          - "put on {music}"
        slots:
          music:
            - type: text
          room:
            - living room
            - kitchen
            - bedroom
            - everywhere
```

### Response Templates

```yaml
# Dynamic responses
intent_script:
  GetTemperature:
    speech:
      text: >
        {% set temp = states('sensor.living_room_temperature') %}
        The living room is currently {{ temp }} degrees.
        {% if temp | float > 25 %}
          It's quite warm!
        {% elif temp | float < 18 %}
          It's a bit chilly.
        {% endif %}
```

---

## Conversation Agents

### Built-in Conversation Agent

The default agent handles home control commands using pattern matching.

```yaml
# No configuration needed
# Uses custom_sentences for intent matching

# Supported out of box:
# - "Turn on/off [device]"
# - "Set [device] to [value]"
# - "What is the [sensor]?"
# - Basic home control commands
```

### Extended OpenAI Conversation (Comprehensive Guide)

Use OpenAI's GPT models for advanced natural language understanding.

#### Setup

```markdown
## Initial Configuration
1. Get API key from platform.openai.com
2. Settings > Devices & Services
3. Add "OpenAI Conversation" integration
4. Enter API key
5. Configure model and options
```

#### Model Selection

| Model | Input Cost | Output Cost | Best For |
|-------|-----------|-------------|----------|
| gpt-4o-mini | $0.15/1M | $0.60/1M | Daily use, cost-effective |
| gpt-4o | $5.00/1M | $15.00/1M | Complex reasoning |
| gpt-3.5-turbo | $0.50/1M | $1.50/1M | Legacy, basic tasks |

#### Configuration Options

```yaml
# Via UI: Settings > Devices & Services > OpenAI Conversation > Configure

# Key settings:
model: gpt-4o-mini          # Recommended for cost/quality
max_tokens: 500             # Limit response length
temperature: 0.7            # Creativity (0-2, lower = focused)
top_p: 1.0                  # Nucleus sampling
```

#### Custom Instructions (System Prompt)

```yaml
# Advanced prompt for home control
instructions: |
  You are a smart home assistant controlling Home Assistant.

  Guidelines:
  1. Execute commands by calling Home Assistant services
  2. Be concise - responses should be under 50 words
  3. Always confirm what action you took
  4. If unsure about a device, ask for clarification
  5. Never expose sensitive information like codes or passwords
  6. Suggest energy-efficient alternatives when appropriate

  Home context:
  - Location: Stockholm, Sweden
  - Residents: 2 adults, 1 child
  - Preferences: Energy efficiency, comfort

  Available areas: Living Room, Kitchen, Bedroom, Bathroom, Office
  Key devices: Philips Hue lights, Ecobee thermostat, Ring doorbell
```

#### Exposed Entities

```yaml
# Control what the AI can access
# Settings > Voice assistants > [Agent] > Exposed entities

# Recommended exposures:
# ✓ Lights - safe to control
# ✓ Climate - thermostats, fans
# ✓ Covers - blinds, shutters
# ✓ Media players - safe
# ✓ Sensors - for status queries
#
# Consider carefully:
# ⚠ Locks - require confirmation
# ⚠ Alarms - security implications
# ⚠ Scripts - depends on content
```

#### Function Calling (Tool Use)

```yaml
# OpenAI Conversation can execute HA services
# Example prompts and actions:

# User: "Turn on all living room lights"
# → Calls: light.turn_on with area_id: living_room

# User: "Set temperature to 22 degrees"
# → Calls: climate.set_temperature with temperature: 22

# User: "What's the temperature outside?"
# → Reads: sensor.outdoor_temperature state
```

#### Cost Optimization

```yaml
# Tips to reduce API costs:

# 1. Use gpt-4o-mini for routine queries
# 2. Limit max_tokens to necessary minimum (150-300 for most)
# 3. Cache common responses using template sensors
# 4. Use local LLM for high-frequency queries
# 5. Set up rate limiting via automations

# Rate limiting example:
automation:
  - id: voice_rate_limit
    alias: "Voice: Rate Limit OpenAI"
    trigger:
      - platform: state
        entity_id: conversation.openai
    condition:
      - condition: template
        value_template: >
          {{ states('counter.openai_calls') | int > 50 }}
    action:
      - service: notify.mobile_app
        data:
          message: "OpenAI usage limit reached for today"
```

### Local LLM with Ollama (Comprehensive Guide)

Run large language models locally for privacy and cost savings.

#### Why Local LLM?

| Benefit | Description |
|---------|-------------|
| **Privacy** | Voice data never leaves your network |
| **No API Costs** | Run unlimited queries |
| **Offline Capable** | Works without internet |
| **Customizable** | Fine-tune for your home |

#### Hardware Requirements

```markdown
## Minimum (slow but works)
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8GB
- Models: phi, tinyllama
- Response time: 5-15 seconds

## Recommended
- CPU: Intel i7/i9 or AMD Ryzen 7/9
- RAM: 16GB
- GPU: NVIDIA GTX 1060+ (6GB VRAM)
- Models: mistral, llama2:7b
- Response time: 1-5 seconds

## Optimal
- CPU: Modern multi-core
- RAM: 32GB+
- GPU: NVIDIA RTX 3080+ (10GB+ VRAM)
- Models: llama2:13b, mixtral
- Response time: <1 second
```

#### Ollama Installation

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull models
ollama pull mistral     # Fast, good quality (7B)
ollama pull llama2      # General purpose (7B)
ollama pull phi         # Small, efficient (2.7B)
ollama pull llama2:13b  # Better quality (13B, needs 16GB RAM)
```

#### Docker Installation

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

#### Model Selection Guide

| Model | Parameters | RAM | Speed | Quality | Best For |
|-------|-----------|-----|-------|---------|----------|
| phi | 2.7B | 4GB | Very Fast | Good | Simple commands |
| tinyllama | 1.1B | 2GB | Fastest | Basic | Quick responses |
| mistral | 7B | 8GB | Fast | Very Good | General use |
| llama2:7b | 7B | 8GB | Medium | Good | Balanced |
| llama2:13b | 13B | 16GB | Slow | Excellent | Complex tasks |
| mixtral | 47B | 32GB | Slow | Best | Advanced reasoning |

#### Home Assistant Integration

```markdown
## Via HACS (Recommended)
1. HACS > Integrations > Search "Ollama"
2. Install "Ollama Conversation"
3. Restart Home Assistant
4. Settings > Devices & Services > Add Integration > Ollama

## Configuration
Host: http://192.168.1.100:11434  # Ollama server IP
Model: mistral
Max tokens: 500
Temperature: 0.7
```

#### Custom System Prompt for Home Control

```yaml
# Ollama conversation agent configuration
system_prompt: |
  You are a helpful home assistant AI named Jarvis.
  You control a smart home through Home Assistant.

  CAPABILITIES:
  - Control lights, switches, covers
  - Adjust thermostats and climate
  - Check sensor values and device status
  - Run scenes and scripts

  RULES:
  - Keep responses brief (1-2 sentences)
  - Confirm actions taken
  - Ask for clarification if needed
  - Never guess - ask if unsure
  - Suggest alternatives when helpful

  AVAILABLE AREAS:
  Living Room, Kitchen, Bedroom, Bathroom, Office, Garage

  AVAILABLE DEVICES:
  - Lights in all rooms
  - Thermostat (climate.living_room)
  - Robot vacuum (vacuum.roborock)
  - Door locks (lock.front_door)
  - Media players

  RESPONSE STYLE:
  - Friendly but concise
  - Confirm what you did
  - Use natural language
```

### Hybrid LLM Setup (Local + Cloud Fallback)

```yaml
# Use local Ollama primarily, fall back to OpenAI if unavailable

# First, create availability sensor
binary_sensor:
  - platform: rest
    name: "Ollama Available"
    resource: http://localhost:11434/api/tags
    method: GET
    scan_interval: 60
    value_template: "{{ value_json is defined }}"

# Automation to route conversation
automation:
  - id: voice_hybrid_routing
    alias: "Voice: Hybrid LLM Routing"
    trigger:
      - platform: event
        event_type: assist_pipeline_run_start
    action:
      - choose:
          # Use local Ollama if available
          - conditions:
              - condition: state
                entity_id: binary_sensor.ollama_available
                state: "on"
            sequence:
              - service: conversation.process
                data:
                  agent_id: conversation.ollama
                  text: "{{ trigger.event.data.text }}"
          # Fall back to OpenAI
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

### Conversation Triggers (2024.11+)

Enhanced conversation triggers with slot handling and response variables.

#### Basic Conversation Trigger

```yaml
automation:
  - id: voice_movie_mode
    alias: "Voice: Movie Mode"
    trigger:
      - platform: conversation
        command:
          - "movie time"
          - "start movie mode"
          - "I want to watch a movie"
    action:
      - service: script.movie_mode
      - stop: ""
        response_variable: "Movie mode activated. Enjoy your movie!"
```

#### Slots and Variables

```yaml
automation:
  - id: voice_set_light
    alias: "Voice: Set Light Brightness"
    trigger:
      - platform: conversation
        command:
          - "set {room} lights to {level} percent"
          - "dim {room} to {level}"
          - "{level} percent in {room}"
    action:
      - service: light.turn_on
        target:
          area_id: "{{ trigger.slots.room | replace(' ', '_') }}"
        data:
          brightness_pct: "{{ trigger.slots.level | int }}"
      - stop: ""
        response_variable: >
          Set {{ trigger.slots.room }} lights to {{ trigger.slots.level }} percent.
```

#### Wildcards and Alternatives

```yaml
# Syntax:
# [option1|option2] = alternatives (either/or)
# [optional|] = optional word
# {slot} = capture variable

automation:
  - id: voice_flexible
    alias: "Voice: Flexible Commands"
    trigger:
      - platform: conversation
        command:
          - "[please|] turn {state} [the|] {room} [light|lights]"
          - "[can you|] set {room} [lights|] to {state}"
    action:
      - service: "light.turn_{{ trigger.slots.state }}"
        target:
          area_id: "{{ trigger.slots.room | replace(' ', '_') }}"
```

### Wake Word Training

#### openWakeWord Configuration

```yaml
# openWakeWord add-on settings

# Available wake words:
# - hey_jarvis
# - alexa (caution: may trigger Amazon devices)
# - ok_nabu
# - hey_mycroft

# Sensitivity (0.0 - 1.0)
# Lower = fewer false positives, might miss real commands
# Higher = more responsive, more false positives
sensitivity: 0.5

# Threshold for secondary confirmation
vad_threshold: 0.5
```

#### Custom Wake Word Training

```markdown
## Training Your Own Wake Word

1. Record samples
   - Minimum 50 recordings of wake word
   - Different voices, distances, background noise
   - 16kHz mono WAV format

2. Use openWakeWord training notebook
   - https://github.com/dscripka/openWakeWord
   - Train on Google Colab or local

3. Deploy custom model
   - Place .tflite file in openWakeWord add-on
   - Configure in add-on settings

## Tips for Good Wake Words
- 2-4 syllables work best
- Avoid common words
- Distinct sounds (not easily confused)
- Test with household noise
```

### Multi-Turn Conversations

#### Context Preservation

```yaml
# OpenAI Conversation maintains context automatically
# Example conversation:

# User: "What's the temperature in the living room?"
# AI: "The living room is 22 degrees."
# User: "And the bedroom?"
# AI: "The bedroom is 19 degrees."  # Understands context

# Configure context window:
# Settings > OpenAI Conversation > Max messages: 5
```

#### Follow-Up Questions

```yaml
automation:
  - id: voice_followup
    alias: "Voice: Handle Follow-up"
    trigger:
      - platform: conversation
        command:
          - "and {action} {target}"
          - "also {action} {target}"
          - "what about {target}"
    condition:
      - condition: template
        value_template: >
          {{ states('input_text.last_voice_context') != '' }}
    action:
      - variables:
          context: "{{ states('input_text.last_voice_context') }}"
      - service: conversation.process
        data:
          agent_id: conversation.openai
          text: >
            Context: {{ context }}
            Follow-up: {{ trigger.sentence }}
```

#### Conversation State Machine

```yaml
# Track conversation state for complex interactions
input_select:
  conversation_state:
    name: "Conversation State"
    options:
      - idle
      - awaiting_confirmation
      - awaiting_room
      - awaiting_temperature
    initial: idle

automation:
  - id: voice_confirmation_flow
    alias: "Voice: Confirmation Flow"
    trigger:
      - platform: conversation
        command:
          - "lock all doors"
          - "arm the alarm"
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.conversation_state
        data:
          option: awaiting_confirmation
      - stop: ""
        response_variable: >
          Are you sure you want to {{ trigger.sentence }}? Say yes to confirm.

  - id: voice_handle_confirmation
    alias: "Voice: Handle Confirmation"
    trigger:
      - platform: conversation
        command:
          - "yes"
          - "confirm"
          - "do it"
    condition:
      - condition: state
        entity_id: input_select.conversation_state
        state: awaiting_confirmation
    action:
      # Execute pending action
      - service: script.execute_pending_voice_action
      - service: input_select.select_option
        target:
          entity_id: input_select.conversation_state
        data:
          option: idle
```

---

## Cloud Voice Services

### Google Cloud Speech

```yaml
# configuration.yaml
stt:
  - platform: google_cloud
    key_file: google_cloud_key.json
    model: command_and_search  # or latest_long

tts:
  - platform: google_cloud
    key_file: google_cloud_key.json
    voice: en-US-Neural2-F
```

### Amazon Polly

```yaml
# configuration.yaml
tts:
  - platform: amazon_polly
    aws_access_key_id: YOUR_KEY
    aws_secret_access_key: YOUR_SECRET
    region_name: eu-north-1
    voice: Joanna
    engine: neural
```

### Azure Speech

```yaml
# configuration.yaml
tts:
  - platform: microsoft
    api_key: YOUR_KEY
    region: northeurope
    voice: en-US-JennyNeural
```

---

## Troubleshooting

### Voice Not Recognized

```markdown
## Checklist
1. Microphone working? Test with other apps
2. Correct language configured?
3. Whisper model appropriate for language?
4. Background noise too high?

## Solutions
- Use larger Whisper model
- Improve microphone quality/position
- Reduce background noise
- Check audio levels in add-on logs
```

### Slow Response

```markdown
## Causes
- Large Whisper model on weak hardware
- Network latency (cloud services)
- Complex intent processing

## Solutions
1. Use smaller Whisper model
2. Use faster-whisper
3. Ensure SSD storage
4. Upgrade hardware
```

### Wake Word Not Detected

```markdown
## Checklist
1. openWakeWord add-on running?
2. Correct wake word configured?
3. Microphone sensitivity appropriate?

## Common Wake Words
- "hey jarvis"
- "alexa" (caution: may trigger real Alexa)
- "ok nabu"
- Custom trained words
```

### Debug Logging

```yaml
# Enable voice debug logging
logger:
  default: info
  logs:
    homeassistant.components.voice_assistant: debug
    homeassistant.components.stt: debug
    homeassistant.components.tts: debug
    homeassistant.components.conversation: debug
    homeassistant.components.intent: debug
```

### Test Pipeline

```markdown
## Via Developer Tools > Services

# Test STT
service: stt.process
data:
  audio_input: base64_audio_data

# Test TTS
service: tts.speak
target:
  entity_id: tts.piper
data:
  media_player_entity_id: media_player.living_room
  message: "This is a test"

# Test Intent
service: conversation.process
data:
  text: "Turn on the living room lights"
```

---

## Best Practices

### Hardware Recommendations

```markdown
## For Best Local Experience
- x86_64 mini PC (Intel N100+) or better
- 8GB+ RAM
- SSD storage
- Quality USB microphone

## For Satellites
- ESP32-S3 with I2S audio
- Quality MEMS microphone
- Small speaker for TTS output
```

### Pipeline Optimization

```markdown
## Speed vs Quality Trade-offs

Fast (basic accuracy):
- Whisper tiny/base
- Piper low quality voice
- Simple wake word

Balanced:
- Whisper small
- Piper medium voice
- openWakeWord

Quality (slower):
- Whisper medium
- Piper high voice
- Multiple wake word options
```

### Security Considerations

```markdown
## Local Processing Benefits
- Voice never leaves home
- No cloud account needed
- Works offline

## If Using Cloud Services
- Use dedicated API keys
- Monitor usage/costs
- Consider data privacy policies
```
