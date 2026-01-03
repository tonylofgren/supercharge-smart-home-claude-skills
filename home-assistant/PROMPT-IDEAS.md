# Home Assistant YAML Automation - Prompt Ideas

> 600+ categorized prompts for **Home Assistant YAML automations** (automations.yaml, blueprints, scripts)

**All prompts explicitly request "Home Assistant automation"** to distinguish from Node-RED flows or ESPHome device configs.

## Table of Contents
- [Automations](#automations)
- [Dashboards](#dashboards)
- [Templates](#templates)
- [Integrations](#integrations)
- [Scripts & Scenes](#scripts--scenes)
- [Troubleshooting](#troubleshooting)
- [Architecture & Planning](#architecture--planning)
- [Security & Privacy](#security--privacy)
- [Energy Management](#energy-management)
- [Voice Control](#voice-control)
- [Advanced Topics](#advanced-topics)

---

## Automations

### Lighting Automations

#### Basic
- "Create a Home Assistant automation to turn on [light] when [motion sensor] detects motion"
- "Create a Home Assistant automation to turn off [light] after 5 minutes of no motion"
- "Create a Home Assistant automation to dim [light] to 50% at sunset"
- "Create a Home Assistant automation for outdoor lights: on at sunset, off at sunrise"
- "Create a Home Assistant automation to toggle [light] when [button] is pressed"

#### Intermediate
- "Create a Home Assistant automation for motion-activated hallway lights with 3-minute timeout"
- "Create a Home Assistant automation for adaptive lighting that matches circadian rhythm"
- "Create a Home Assistant automation for a wake-up light that gradually increases brightness over 15 minutes"
- "Create a Home Assistant automation to sync all lights in [room] to match the main light"
- "Create a Home Assistant automation for party mode that cycles through colors"

#### Advanced
- "Create a Home Assistant automation for follow-me lighting that tracks motion across rooms"
- "Create a Home Assistant automation for smart dimming based on ambient light sensor readings"
- "Create a Home Assistant automation for light scenes that remember and restore previous states"
- "Create a Home Assistant automation for presence-aware lighting with timeout based on activity level"
- "Create a Home Assistant automation for multi-stage motion lighting: dim → bright → off"

### Presence Automations

#### Basic
- "Create a Home Assistant automation to send notification when [person] arrives home"
- "Create a Home Assistant automation to turn off all lights when everyone leaves"
- "Create a Home Assistant automation to arm alarm when house is empty"
- "Create a Home Assistant automation to set thermostat to away mode when no one home"
- "Create a Home Assistant automation to track who's home using phone presence"

#### Intermediate
- "Create a Home Assistant automation with grace period before triggering away mode (forgot something)"
- "Create a Home Assistant automation with different actions for first person arriving vs additional"
- "Create a Home Assistant automation for proximity-based pre-arrival"
- "Create a Home Assistant automation for guest mode that adjusts presence rules"
- "Create a Home Assistant automation for presence zone for different areas (upstairs/downstairs)"

#### Advanced
- "Create a Home Assistant automation with state machine for: home → recently_left → away → extended_away"
- "Create a Home Assistant automation for multi-person tracking with individual preferences"
- "Create a Home Assistant automation using Bayesian presence combining multiple sensors"
- "Create a Home Assistant automation for work-from-home detection with different schedules"
- "Create a Home Assistant automation for vacation mode with random light patterns"

### Climate Automations

#### Basic
- "Create a Home Assistant automation to set thermostat to 21°C at 7 AM on weekdays"
- "Create a Home Assistant automation to lower temperature to 18°C at night"
- "Create a Home Assistant automation to turn off AC when windows are opened"
- "Create a Home Assistant automation to turn on fan when temperature exceeds 25°C"
- "Create a Home Assistant automation for different temperatures for weekdays vs weekends"

#### Intermediate
- "Create a Home Assistant automation to pre-heat house 30 minutes before wake-up time"
- "Create a Home Assistant automation for room-by-room temperature control based on occupancy"
- "Create a Home Assistant automation for humidity-triggered bathroom ventilation"
- "Create a Home Assistant automation for weather-adaptive climate control"
- "Create a Home Assistant automation for energy-efficient cooling during peak hours"

#### Advanced
- "Create a Home Assistant automation for multi-zone climate with room priority"
- "Create a Home Assistant automation for learning thermostat that adapts to patterns"
- "Create a Home Assistant automation with electricity price integration for cost optimization"
- "Create a Home Assistant automation for climate scheduling with holiday/vacation overrides"
- "Create a Home Assistant automation for predictive heating based on outdoor temperature trends"

### Security Automations

#### Basic
- "Create a Home Assistant automation to alert when front door opens at night"
- "Create a Home Assistant automation to turn on lights when motion detected while away"
- "Create a Home Assistant automation to lock all doors at 11 PM"
- "Create a Home Assistant automation to notify when garage door left open"
- "Create a Home Assistant automation to flash lights when alarm triggers"

#### Intermediate
- "Create a Home Assistant automation for simulated occupancy when away (random lights)"
- "Create a Home Assistant automation for photo capture when doorbell pressed"
- "Create a Home Assistant automation with different alerting for family vs unknown motion"
- "Create a Home Assistant automation to auto-lock door 5 minutes after unlocking"
- "Create a Home Assistant automation for security check before arming (all doors/windows)"

#### Advanced
- "Create a Home Assistant automation for multi-tier security levels with escalating responses"
- "Create a Home Assistant automation for person detection with facial recognition integration"
- "Create a Home Assistant automation for intrusion detection with zone-specific actions"
- "Create a Home Assistant automation for panic mode triggered by specific button sequence"
- "Create a Home Assistant automation for smoke/CO alarm integration with auto-evacuation actions"

### Time-Based Automations

#### Basic
- "Create a Home Assistant automation to turn on porch light at sunset"
- "Create a Home Assistant automation for morning routine at 7 AM"
- "Create a Home Assistant automation for weekly backup reminder every Sunday"
- "Create a Home Assistant automation for birthday reminders from calendar"
- "Create a Home Assistant automation for monthly maintenance reminders"

#### Intermediate
- "Create a Home Assistant automation for workday vs weekend scheduling"
- "Create a Home Assistant automation for dynamic wake-up time from calendar"
- "Create a Home Assistant automation for school year vs summer schedules"
- "Create a Home Assistant automation for gradual transitions between time periods"
- "Create a Home Assistant automation for scheduled automations with exceptions"

#### Advanced
- "Create a Home Assistant automation for astronomical triggers with offsets"
- "Create a Home Assistant automation for holiday-aware scheduling"
- "Create a Home Assistant automation for season-adaptive automations"
- "Create a Home Assistant automation for work schedule integration (variable)"
- "Create a Home Assistant automation for multi-timezone handling for travel"

### Appliance Automations

#### Basic
- "Create a Home Assistant automation to notify when washing machine finishes"
- "Create a Home Assistant automation to turn off TV after 4 hours"
- "Create a Home Assistant automation to start robot vacuum when leaving"
- "Create a Home Assistant automation to alert if fridge door open too long"
- "Create a Home Assistant automation to remind to take out trash on collection day"

#### Intermediate
- "Create a Home Assistant automation to monitor dishwasher cycle and notify"
- "Create a Home Assistant automation for smart charging during off-peak hours"
- "Create a Home Assistant automation for dryer cycle detection and notification"
- "Create a Home Assistant automation for coffee maker scheduling with presence"
- "Create a Home Assistant automation for robot vacuum room-by-room scheduling"

#### Advanced
- "Create a Home Assistant automation for appliance energy optimization based on solar production"
- "Create a Home Assistant automation for predictive maintenance alerts (cycle counts, runtime)"
- "Create a Home Assistant automation for appliance usage patterns and anomaly detection"
- "Create a Home Assistant automation for multi-appliance coordination (don't run all at once)"
- "Create a Home Assistant automation for load balancing with power capacity limits"

### Notification Automations

#### Basic
- "Create a Home Assistant automation to send notification when [event] happens"
- "Create a Home Assistant automation for daily summary notification at 8 AM"
- "Create a Home Assistant automation to alert when sensor goes offline"
- "Create a Home Assistant automation for battery low notifications for devices"
- "Create a Home Assistant automation for weather alert notifications"

#### Intermediate
- "Create a Home Assistant automation for actionable notifications with response options"
- "Create a Home Assistant automation for escalating notifications (repeat until acknowledged)"
- "Create a Home Assistant automation for context-aware notifications (don't disturb sleep)"
- "Create a Home Assistant automation for notification routing (person-specific)"
- "Create a Home Assistant automation for notification grouping and rate limiting"

#### Advanced
- "Create a Home Assistant automation for AI-prioritized notifications based on importance"
- "Create a Home Assistant automation for multi-channel notifications (phone, speaker, display)"
- "Create a Home Assistant automation for time-sensitive vs non-urgent categorization"
- "Create a Home Assistant automation for notification history with pattern analysis"
- "Create a Home Assistant automation for smart suppression during meetings/focus time"

---

## Dashboards

### Overview Dashboards
- "Create home overview showing all key status at glance"
- "Design mobile-friendly dashboard for quick controls"
- "Build tablet wall panel dashboard"
- "Create status dashboard for bedroom (alarm clock)"
- "Design guest-friendly simplified controls"

### Room Dashboards
- "Living room dashboard with TV, lights, climate"
- "Kitchen dashboard with appliances and recipes"
- "Bedroom dashboard with sleep-focused features"
- "Bathroom dashboard with simple controls"
- "Office dashboard with focus and meeting modes"

### Functional Dashboards
- "Energy monitoring dashboard with real-time and historical"
- "Security dashboard with all cameras and sensors"
- "Climate dashboard for whole-house HVAC"
- "Media dashboard for multi-room audio"
- "Network status dashboard"

### Card Types
- "Use tile cards for compact room controls"
- "Create custom button cards for scenes"
- "Design picture-elements for floor plan"
- "Set up glance card for sensor overview"
- "Create history graph for temperature trends"

### Styling
- "Apply dark theme with accent colors"
- "Create consistent icon colors per room"
- "Design responsive layout for different screens"
- "Add card borders and shadows"
- "Create custom CSS for unique look"

---

## Templates

### Sensor Templates
- "Template sensor showing average temperature"
- "Count of open doors and windows"
- "Total power consumption sum"
- "Time since last motion in room"
- "Formatted uptime sensor"

### Binary Sensor Templates
- "Anyone home binary sensor"
- "Workday vs weekend sensor"
- "Daytime vs nighttime sensor"
- "House secure (all doors/windows closed)"
- "High energy usage alert"

### Text Templates
- "Friendly greeting based on time of day"
- "Status summary sentence"
- "Next calendar event formatted"
- "Weather forecast summary"
- "Trash/recycling collection day"

### Calculations
- "Calculate electricity cost from power sensor"
- "Temperature differential (indoor vs outdoor)"
- "Average of multiple sensors excluding unavailable"
- "Rate of change (temperature rising/falling)"
- "Daily/weekly/monthly aggregations"

### Advanced Templates
- "Jinja macro for reusable formatting"
- "List all entities with specific attribute"
- "Parse JSON from API response"
- "Multi-condition state determination"
- "Historical statistics queries"

---

## Integrations

### Zigbee/Z-Wave
- "Set up Zigbee2MQTT for IKEA devices"
- "Configure Z-Wave network for locks"
- "Optimize Zigbee mesh with router devices"
- "Migrate from deCONZ to Zigbee2MQTT"
- "Troubleshoot Zigbee device dropouts"

### ESPHome
- "Create ESP32 motion sensor with temperature"
- "Build custom LED strip controller"
- "DIY power monitoring sensor"
- "Bluetooth proxy for tracking"
- "Voice satellite with ESP32-S3"

### MQTT
- "Set up MQTT broker for external devices"
- "Create sensors from MQTT topics"
- "Publish Home Assistant states to MQTT"
- "Bridge multiple MQTT brokers"
- "MQTT-based command interface"

### Cloud Services
- "Integrate Google Home with Home Assistant"
- "Set up Alexa integration"
- "Connect to Home Connect appliances"
- "Weather service integration comparison"
- "Cloud vs local options for cameras"

### Matter/Thread
- "Add Matter device to Home Assistant"
- "Set up Thread border router"
- "Migrate Hue devices to Matter"
- "Multi-admin Matter setup"
- "Troubleshoot Matter commissioning"

---

## Scripts & Scenes

### Scenes
- "Create movie night scene with dim lights"
- "Morning routine scene activation"
- "Romantic dinner scene with candles"
- "Work from home focus scene"
- "Sleep scene with gradual dimming"

### Scripts
- "Announce text on all speakers"
- "Cycle through color scenes"
- "Reset room to default state"
- "Start timer with voice feedback"
- "Execute sequence with delays"

### Advanced Scripts
- "Scene with memory (save/restore previous state)"
- "Queued script for sequenced actions"
- "Script with parameters and validation"
- "Conditional execution based on context"
- "Error handling in long scripts"

---

## Troubleshooting

### Automations
- "Why isn't my automation triggering?"
- "Automation runs multiple times unexpectedly"
- "Template condition always evaluates false"
- "Race condition between automations"
- "Debug automation execution step by step"

### Entities
- "Entity shows unavailable intermittently"
- "Sensor value stuck/not updating"
- "Duplicate entities appearing"
- "Entity attributes missing"
- "State history not recording"

### Performance
- "Dashboard loads slowly"
- "Home Assistant database growing too large"
- "High CPU usage from automations"
- "Memory leaks investigation"
- "Network traffic optimization"

### Integration Issues
- "Zigbee device keeps dropping"
- "MQTT connection unstable"
- "Cloud integration authentication failing"
- "ESPHome device won't connect"
- "Matter device offline"

---

## Architecture & Planning

### Home Design
- "Plan smart home for new house build"
- "Retrofit automation for existing home"
- "Budget-friendly starter setup"
- "Room-by-room rollout plan"
- "Prioritize automations by impact"

### System Design
- "Best practices for naming conventions"
- "Organize entities with areas and labels"
- "Structure automations in packages"
- "Separate concerns: lighting/climate/security"
- "Version control for configuration"

### Reliability
- "Backup strategy for Home Assistant"
- "Disaster recovery planning"
- "High availability setup"
- "Monitoring and alerting for HA itself"
- "Fail-safe defaults for critical systems"

### Documentation
- "Document custom integrations"
- "Create maintenance runbook"
- "Guest/family instruction guide"
- "Troubleshooting decision tree"
- "Change log for configuration"

---

## Security & Privacy

### Access Control
- "Set up user accounts with different permissions"
- "Secure remote access options"
- "Two-factor authentication setup"
- "Audit logging for sensitive actions"
- "Rate limiting for failed attempts"

### Network Security
- "VLAN setup for IoT devices"
- "Firewall rules for Home Assistant"
- "VPN vs Cloudflare tunnel comparison"
- "Local-only integrations setup"
- "Network segmentation best practices"

### Privacy
- "Local-only voice assistant setup"
- "Data retention policies"
- "Camera privacy zones"
- "Guest WiFi with restrictions"
- "Remove cloud dependencies"

---

## Energy Management

### Monitoring
- "Set up whole-house energy monitoring"
- "Per-circuit energy tracking"
- "Solar production monitoring"
- "EV charging tracking"
- "Gas and water usage monitoring"

### Optimization
- "Automate based on electricity prices"
- "Load shifting for off-peak usage"
- "Solar self-consumption optimization"
- "Battery storage automation"
- "HVAC scheduling for energy savings"

### Reporting
- "Daily energy consumption report"
- "Month-over-month comparison"
- "Cost projection templates"
- "Carbon footprint calculation"
- "Energy goal tracking"

---

## Voice Control

### Local Voice
- "Set up Wyoming satellite with ESP32"
- "Configure Whisper for local speech-to-text"
- "Install Piper for local text-to-speech"
- "Create custom voice intents"
- "Multi-room voice announcement setup"

### Custom Commands
- "Create intent for 'goodnight' routine"
- "Custom sentence patterns for lights"
- "Area-aware voice commands"
- "Slot filling for complex commands"
- "Follow-up questions in conversations"

### Integration
- "Expose entities to Google Home"
- "Alexa skill development"
- "Voice feedback for automations"
- "Announcement routines"
- "Voice-triggered scenes"

---

## Advanced Topics

### State Machines
- "Implement presence state machine"
- "Appliance cycle state tracking"
- "Security system states"
- "Room occupancy states"
- "HVAC mode state machine"

### Multi-Area
- "Cross-room lighting coordination"
- "Follow-me audio"
- "Whole-house security zones"
- "Climate zone management"
- "Area-based presence detection"

### Error Handling
- "Retry failed service calls"
- "Graceful degradation patterns"
- "Notification on automation failure"
- "Watchdog for critical automations"
- "Self-healing automation patterns"

### Performance
- "Optimize template evaluation"
- "Efficient trigger patterns"
- "Database optimization"
- "Reduce state change frequency"
- "Parallel execution strategies"

### Testing
- "Test automations safely"
- "Simulation mode for complex automations"
- "Staged rollout for changes"
- "Regression testing for updates"
- "Monitoring automation success rates"

---

## Quick Categories

### By Room
| Room | Popular Prompts |
|------|-----------------|
| Living Room | TV control, ambient lighting, climate |
| Bedroom | Wake-up routines, sleep tracking, blinds |
| Kitchen | Appliance monitoring, cooking timers |
| Bathroom | Humidity control, motion lights |
| Office | Focus modes, meeting integration |
| Garage | Door monitoring, car charging |
| Outdoor | Irrigation, security lighting |

### By Device Type
| Device | Popular Prompts |
|--------|-----------------|
| Lights | Motion activation, schedules, scenes |
| Thermostats | Scheduling, presence, zones |
| Locks | Auto-lock, notifications, access control |
| Cameras | Motion detection, recording, privacy |
| Speakers | Announcements, TTS, music |
| Sensors | Alerting, history, aggregation |

### By Trigger Type
| Trigger | Popular Prompts |
|---------|-----------------|
| Time | Schedules, sunrise/sunset, calendar |
| State | Entity changes, thresholds, durations |
| Event | Button press, webhook, MQTT |
| Numeric | Above/below values, rate of change |
| Zone | Enter/leave, proximity |

### By Difficulty
| Level | Popular Prompts |
|-------|-----------------|
| Beginner | Single triggers, simple actions |
| Intermediate | Conditions, templates, multiple actions |
| Advanced | State machines, multi-area, error handling |
| Expert | Custom components, performance optimization |

---

## Prompt Templates

### Standard Format
```
Create an automation for [purpose] that:
- Triggers when [condition]
- Only runs if [conditions]
- Actions: [list of actions]
- Entities: [relevant entity_ids]
```

### Troubleshooting Format
```
My [component] isn't working correctly.
Expected: [what should happen]
Actual: [what is happening]
Code: [paste relevant yaml]
Logs: [relevant error messages]
```

### Feature Request Format
```
I want to [goal].
I have these devices/sensors: [list]
Constraints: [any limitations]
Nice to have: [optional features]
```

---

*Use these prompts as starting points - customize with your specific entity IDs and requirements for best results!*
