# Node-RED Prompt Ideas

Over 200 example prompts for building Node-RED automations with Home Assistant.

---

## Getting Started

### Setup & Configuration
- "Help me connect Node-RED to my Home Assistant instance"
- "How do I create a long-lived access token for Node-RED?"
- "What's the difference between the addon and external Node-RED setup?"
- "Configure Node-RED server for external installation"
- "Install the Home Assistant nodes in Node-RED"

### Basic Concepts
- "Explain how Node-RED flows work"
- "What is the msg object in Node-RED?"
- "How do I use the debug node effectively?"
- "Explain the difference between flow and global context"
- "What's the difference between Events: state and Trigger: state nodes?"

---

## Lighting Automation

### Basic
- "Create a simple motion-activated light"
- "Turn on lights when motion is detected in living room"
- "Make bathroom light turn off after 5 minutes"
- "Toggle kitchen light with a button press"

### Intermediate
- "Motion light that only works after sunset"
- "Create adaptive lighting based on time of day"
- "Motion light with manual override detection"
- "Turn on hallway lights when any door opens"

### Advanced
- "Create a lighting scene controller with multiple presets"
- "Implement circadian rhythm lighting automation"
- "Create vacation mode that randomly toggles lights"
- "Build a wake-up light sequence that gradually increases brightness"

---

## Presence Detection

### Basic
- "Create a presence-based automation"
- "Turn off all lights when everyone leaves"
- "Send notification when someone arrives home"

### Intermediate
- "Multi-sensor room presence detection"
- "Track room occupancy with motion timeout"
- "Different actions based on who is home"

### Advanced
- "Create a whole-house presence system"
- "Implement presence decay with configurable timeout"
- "Build guest mode that tracks temporary occupants"

---

## Climate Control

### Basic
- "Set thermostat based on temperature"
- "Turn off HVAC when window is open"
- "Adjust temperature at night"

### Intermediate
- "Create a schedule-based climate automation"
- "Different temperatures for home/away/sleep modes"
- "Control multiple climate zones"

### Advanced
- "Build a smart thermostat controller with humidity consideration"
- "Implement predictive heating based on forecast"
- "Create energy-efficient climate automation"

---

## Notifications

### Basic
- "Send mobile notification when door opens"
- "Create an alert when motion is detected"
- "Notify when washer cycle is complete"

### Intermediate
- "Route notifications based on priority"
- "Only notify people who are away from home"
- "Aggregate multiple alerts to avoid spam"

### Advanced
- "Build a notification hub with routing rules"
- "Create actionable notifications with responses"
- "Implement notification escalation for critical alerts"

---

## Security

### Basic
- "Alert when door opens while away"
- "Create a simple alarm trigger"
- "Monitor window sensors"

### Intermediate
- "Build arm/disarm system with entry delay"
- "Create security zones with different rules"
- "Motion detection with time-based sensitivity"

### Advanced
- "Implement a full security state machine"
- "Create panic button functionality"
- "Build surveillance automation with camera triggers"

---

## Energy Monitoring

### Basic
- "Track power consumption"
- "Alert when power exceeds threshold"
- "Monitor daily energy usage"

### Intermediate
- "Create energy dashboard data"
- "Calculate cost based on time-of-use rates"
- "Track individual device consumption"

### Advanced
- "Build appliance state detection from power usage"
- "Create energy optimization suggestions"
- "Implement load shedding during peak hours"

---

## Media Control

### Basic
- "Control media player with Node-RED"
- "Pause TV when doorbell rings"
- "Start music when I arrive home"

### Intermediate
- "Create media scenes for different activities"
- "Sync lights with media playback"
- "Voice command integration for media"

### Advanced
- "Build multi-room audio coordination"
- "Create dynamic media recommendations"
- "Implement follow-me audio across rooms"

---

## Time-Based Automation

### Basic
- "Run automation at specific time"
- "Create sunrise/sunset trigger"
- "Schedule weekend-only automation"

### Intermediate
- "Different schedules for weekdays vs weekends"
- "Time-based lighting scenes"
- "Workday-aware scheduling"

### Advanced
- "Create flexible scheduling with override"
- "Build calendar-based automation"
- "Implement astronomical time calculations"

---

## Device Integration

### Basic
- "Integrate button device with Node-RED"
- "Handle NFC tag scans"
- "Control smart plug"

### Intermediate
- "Create multi-press button handling"
- "Build device dashboard in Node-RED"
- "Integrate external API with automation"

### Advanced
- "Create custom device controller"
- "Implement device health monitoring"
- "Build fallback for offline devices"

---

## Voice & Conversation

### Basic
- "Create voice command trigger"
- "Handle Assist sentence in Node-RED"
- "Build voice feedback response"

### Intermediate
- "Multi-intent voice command handling"
- "Context-aware voice responses"
- "Voice confirmation for actions"

### Advanced
- "Build conversational automation flow"
- "Create custom voice assistant logic"
- "Implement voice-controlled routines"

---

## Data Processing

### Basic
- "Calculate average temperature"
- "Convert sensor units"
- "Parse JSON data from API"

### Intermediate
- "Build rolling average calculator"
- "Create trend detection"
- "Aggregate data from multiple sensors"

### Advanced
- "Implement statistical analysis on sensor data"
- "Build prediction model for consumption"
- "Create anomaly detection algorithm"

---

## Subflows & Organization

### Basic
- "Create a reusable debounce subflow"
- "Build notification subflow"
- "Organize flows by domain"

### Intermediate
- "Create parameterized subflow with env vars"
- "Build error handling subflow"
- "Design modular automation system"

### Advanced
- "Create self-documenting subflow library"
- "Build testing framework for flows"
- "Implement flow versioning system"

---

## Troubleshooting

### Connection Issues
- "Debug Home Assistant connection problems"
- "Fix 'entity not found' error"
- "Troubleshoot websocket disconnections"

### Flow Issues
- "Debug why my flow isn't triggering"
- "Find message routing problems"
- "Fix service call failures"

### Performance
- "Optimize slow-running flows"
- "Fix memory usage issues"
- "Improve flow response time"

---

## Integration Patterns

### External Services
- "Integrate weather API into automation"
- "Send data to external webhook"
- "Connect to MQTT broker"

### Home Assistant
- "Use HA templates in Node-RED"
- "Fire custom events from Node-RED"
- "Create HA entities from Node-RED"

### Advanced Integration
- "Build bidirectional data sync"
- "Create retry logic for API calls"
- "Implement webhook security"

---

## Best Practices

### Design
- "Best way to organize my flows"
- "How to name nodes effectively"
- "When to use subflows vs copy"

### Reliability
- "Make my automation more reliable"
- "Add error handling to flows"
- "Create fallback for failures"

### Maintenance
- "Document my flows properly"
- "Version control Node-RED flows"
- "Create backup strategy"

---

## Migration & Conversion

### From HA Automations
- "Convert HA automation to Node-RED"
- "When should I use Node-RED vs HA automations?"
- "Migrate complex automation to Node-RED"

### From Other Systems
- "Convert MQTT rules to Node-RED"
- "Migrate from AppDaemon to Node-RED"
- "Import existing Node-RED flows"

---

## Real-World Examples

### Complete Projects
- "Build a complete garage door controller"
- "Create smart doorbell automation"
- "Implement a plant watering system"
- "Build a weather-aware automation system"
- "Create a complete morning routine"
- "Build an air quality monitoring system"
- "Implement a pet feeder automation"
- "Create a whole-house off switch"

### Home Office
- "Create presence-based office automation"
- "Build meeting mode for home office"
- "Implement focus time automation"

### Entertainment
- "Create movie night scene automation"
- "Build party mode with coordinated lights"
- "Implement game room automation"

---

## Quick Tasks

- "Add debug node to my flow"
- "Create inject node for testing"
- "Set up error handling"
- "Add rate limiting"
- "Create simple switch logic"
- "Build delay between actions"
- "Store value in context"
- "Call Home Assistant service"
- "Get current entity state"
- "Filter events by entity"
