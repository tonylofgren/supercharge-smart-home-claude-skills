# Home Assistant Code Assistant - Usage Guide

> 70+ practical examples organized by use case, including debugging workflows and migration guides

## Table of Contents
- [Getting Started](#getting-started)
- [Automation Examples](#automation-examples)
- [Dashboard Examples](#dashboard-examples)
- [Template Examples](#template-examples)
- [Integration Examples](#integration-examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Patterns](#advanced-patterns)
- [Advanced Debugging](#advanced-debugging)
- [Safe Testing](#safe-testing)
- [Performance Tuning](#performance-tuning)
- [Migration Guide](#migration-guide)

---

## Getting Started

### Basic Questions to Ask Claude

```
"Help me create an automation that turns on lights when motion is detected"

"How do I set up a notification when my washing machine is done?"

"Create a dashboard card showing temperature in all rooms"

"Why isn't my automation triggering?"
```

### Providing Context

For best results, include:
1. **What you want to achieve** (the goal)
2. **What entities/devices you have** (sensor.X, light.Y)
3. **Any conditions** (only at night, when home, etc.)
4. **Current code** (if troubleshooting)

---

## Automation Examples

### 1. Motion-Activated Lights

**Simple version:**
```
"Create an automation that turns on the hallway light when motion is
detected by sensor.hallway_motion, and turns it off after 3 minutes"
```

**Advanced version:**
```
"Create a motion light automation for the hallway with:
- Motion sensor: binary_sensor.hallway_motion
- Light: light.hallway
- Different brightness: 100% during day, 20% at night
- Illuminance check: only when below 50 lux
- Off delay: 5 minutes
- Don't turn on if someone manually turned it off"
```

### 2. Presence-Based Actions

**When leaving home:**
```
"Create an automation that when the last person leaves home:
- Turns off all lights
- Sets thermostat to 17°C
- Locks the front door
- Sends a notification with summary"
```

**When arriving home:**
```
"Create an automation for arriving home that:
- Triggers when my phone connects to home WiFi
- Or when I'm within 500m and heading home
- Turns on hallway lights
- Sets comfortable temperature
- Plays welcome announcement"
```

### 3. Time-Based Schedules

**Morning routine:**
```
"Create a morning routine automation for weekdays:
- Starts at 6:30
- Gradually increases bedroom light over 15 minutes
- Opens bedroom blinds at 6:45
- Turns on coffee maker at 6:50
- Announces weather and calendar at 7:00"
```

**Bedtime routine:**
```
"Create a bedtime scene automation:
- Triggered by voice command or button press
- Dims all lights to 10%
- Sets thermostat to night mode (18°C)
- Locks all doors
- Arms alarm
- After 15 minutes, turns off all lights"
```

### 4. Security & Monitoring

**Door/window monitoring:**
```
"Create an automation that alerts me when:
- Any door or window is open for more than 10 minutes
- Send actionable notification with options to dismiss or view camera"
```

**Security mode:**
```
"Create a security automation that when alarm is armed:
- Monitors all motion sensors
- If motion detected, sends high-priority notification
- Includes camera snapshot
- Turns on all lights
- Offers options to disarm or call security"
```

### 5. Climate Control

**Smart thermostat:**
```
"Create climate automations for my living room:
- 21°C when occupied
- 18°C when empty for 30 minutes
- 17°C when everyone is away
- Turn off when windows are open
- Pre-heat before scheduled arrival"
```

**Humidity management:**
```
"Create an automation that turns on the bathroom fan when:
- Humidity rises above 70%
- Keeps running until below 60%
- Maximum runtime 30 minutes
- Sends alert if it runs maximum time"
```

### 6. Appliance Automation

**Washing machine notifications:**
```
"Create an automation for washing machine monitoring:
- Uses power sensor (sensor.washing_machine_power)
- Detects when cycle starts (>10W)
- Detects when cycle ends (<5W for 3 minutes)
- Sends notification when done
- Reminds again in 30 minutes if door not opened"
```

**Smart charging:**
```
"Create an EV charging automation:
- Only charge when electricity price is below 0.50 SEK/kWh
- Or when solar production exceeds house consumption
- Stop charging at 80% on weekdays
- Full charge on weekends"
```

### 7. Media & Entertainment

**TV ambient lighting:**
```
"Create an automation that syncs lights with TV:
- When TV turns on in evening, dim lights to 30%
- When TV plays movie, set movie scene
- When TV pauses, increase lights
- When TV off, restore previous lighting"
```

**Multi-room audio:**
```
"Create a script that follows me with music:
- Detects which room I'm in via motion
- Moves music to that room's speaker
- Adjusts volume based on time of day"
```

---

## Dashboard Examples

### 1. Overview Dashboard

```
"Create a home overview dashboard with:
- Weather and outdoor temp at top
- Security status (doors/windows)
- People home status
- Energy consumption today
- Quick action buttons (scenes)
- Rooms as sections with key controls"
```

### 2. Room-Specific View

```
"Create a bedroom dashboard section:
- Tile cards for each light with brightness control
- Climate with temperature control
- Blind position slider
- Motion sensor status
- Air quality (if available)
- Scene buttons"
```

### 3. Energy Dashboard

```
"Create an energy monitoring dashboard:
- Current total power consumption
- Today vs yesterday comparison
- Top power consumers list
- Solar production (if available)
- Cost estimation based on current rate"
```

### 4. Security Dashboard

```
"Create a security dashboard with:
- Alarm panel control
- All door/window sensors status
- Camera feeds
- Lock controls
- Motion sensor history
- Arrival/departure log"
```

### 5. Mobile-Optimized View

```
"Create a mobile-friendly dashboard with:
- Large tap targets for common actions
- Only essential information
- Swipe between rooms
- Quick scene activation
- Emergency buttons at top"
```

---

## Template Examples

### 1. Sensor Aggregation

```
"Create template sensors that show:
- Average temperature of all indoor sensors
- Total power consumption
- Devices with low battery
- Count of open doors/windows
- List of currently active lights"
```

### 2. Friendly State Display

```
"Create a template sensor that shows the home status as:
- 'Morgon' between 6-9
- 'Dag' between 9-17
- 'Kväll' between 17-22
- 'Natt' between 22-6
Include icon that matches"
```

### 3. Presence Summary

```
"Create a template that shows:
- 'Hemma: [names]' if anyone home
- 'Ingen hemma' if empty
- Show ETA for closest person if away"
```

### 4. Complex Calculations

```
"Create a template sensor for energy cost:
- Reads current power consumption
- Multiplies by current electricity price
- Shows hourly, daily, and monthly projections
- Rounds to 2 decimals"
```

### 5. Conditional Attributes

```
"Create a sensor with attributes showing:
- All rooms with temperatures below 18°C
- All rooms above 24°C
- The coldest and warmest rooms"
```

---

## Integration Examples

### 1. Zigbee2MQTT Setup

```
"Help me configure Zigbee2MQTT for:
- IKEA Tradfri lights
- Aqara temperature sensors
- IKEA Styrbar remotes
Include network optimization tips"
```

### 2. ESPHome Device

```
"Create an ESPHome config for:
- ESP32 board
- DHT22 temperature/humidity sensor
- PIR motion sensor
- Relay for controlling a light
- Include filters for stable readings"
```

### 3. MQTT Integration

```
"Help me set up MQTT integration for:
- External sensor publishing to 'home/sensors/outdoor/temperature'
- Need to create sensor entity from MQTT topic
- Include availability tracking"
```

### 4. Matter Device

```
"Help me add a Matter device:
- Eve Energy plug
- Already on Thread network via HomePod
- Need to commission to Home Assistant"
```

---

## Troubleshooting

### 1. Automation Not Triggering

```
"My automation isn't working. Here's the code:
[paste automation yaml]

The trigger entity shows state changes in Developer Tools
but automation never fires."
```

### 2. Template Errors

```
"I'm getting 'undefined' in my template:
{{ states.sensor.temperature.state }}

What's wrong and how do I fix it?"
```

### 3. Entity Not Available

```
"My Zigbee sensor shows unavailable every few hours.
- Device: Aqara temperature sensor
- Zigbee2MQTT logs show nothing
- How do I diagnose and fix this?"
```

### 4. Slow Dashboard

```
"My dashboard is slow to load:
- 5+ seconds to render
- Uses picture-elements with cameras
- How can I optimize it?"
```

### 5. Migration Issues

```
"I updated to HA 2024.x and now I see deprecation warnings:
[paste warning]
How do I update my config?"
```

---

## Advanced Patterns

### 1. State Machine

```
"Create a presence state machine with states:
- Present (someone home)
- Recently_Left (grace period 10 min)
- Away (confirmed empty)
- Extended_Away (24+ hours)
- Arriving (approaching home)

Each state should have entry/exit actions"
```

### 2. Multi-Area Coordination

```
"Create a 'follow me' lighting system:
- Track which room has most recent motion
- Turn on lights in active room
- Dim lights in adjacent rooms
- Turn off lights in empty rooms after delay
- Consider time of day for brightness"
```

### 3. Conditional Cascades

```
"Create a smart heating system:
- Base temperature on occupancy
- Adjust for outdoor temperature
- Factor in solar gain (south-facing rooms warmer)
- Pre-heat before wake time
- Never let pipes freeze (min 8°C)"
```

### 4. Error Handling

```
"Make my automation more robust:
- Retry if service call fails
- Log failures
- Send notification after 3 failures
- Don't retry if entity unavailable"
```

### 5. Scene with Memory

```
"Create a scene system that:
- Remembers state before activating
- Can restore to 'before scene' state
- Tracks who activated it
- Auto-restores after timeout"
```

---

## Advanced Debugging

### 1. Using Automation Traces

```
"Explain how to use automation traces to debug:
- Where to find traces in the UI
- How to interpret the timeline
- Understanding condition results
- Identifying why an action failed"
```

**Trace-based debugging workflow:**
```
"My automation ran but the action didn't work.
Show me how to:
1. Open the trace for automation.living_room_lights
2. Check if all conditions passed
3. Find the exact error in the action step
4. Understand variable values at each step"
```

### 2. Template Debugging

```
"Help me debug this template step by step:
{{ states.sensor.temperature.state | float * 1.8 + 32 }}

Show me:
- How to test in Developer Tools > Template
- What 'None' or 'unavailable' means
- How to add default values
- How to handle missing attributes"
```

**Real-time debugging:**
```
"Create a template that shows debug info:
- Current value of sensor.power
- Whether it's numeric or string
- Last changed time
- Available attributes"
```

### 3. Service Call Testing

```
"Before using a service in automation, how do I:
- Test it in Developer Tools > Services
- See what parameters are available
- Check the response/result
- Identify entity_id vs target format"
```

**Testing complex services:**
```
"Test this service call step by step:
service: light.turn_on
target:
  entity_id: light.living_room
data:
  brightness_pct: 50
  transition: 2

Show me how to verify each parameter works"
```

### 4. Log Analysis

```
"How do I enable debug logging for:
- A specific automation
- Zigbee2MQTT
- A custom integration

And how do I read the relevant entries?"
```

**Finding errors:**
```
"My automation shows an error in logs:
'Error executing script. Service notify.mobile_app not found'

How do I:
1. Enable more verbose logging
2. Find related log entries
3. Identify the root cause
4. Fix the issue"
```

### 5. State History Analysis

```
"Help me understand why my sensor shows unexpected values:
- How to view state history graph
- How to find exact timestamps of changes
- How to correlate with other entities
- How to export history for analysis"
```

---

## Safe Testing

### 1. Test Mode Setup

```
"Create a test mode for my automations:
- input_boolean.test_mode that disables all real actions
- Replace actual service calls with notifications
- Log what WOULD have happened
- Easy toggle from dashboard"
```

**Implementation example:**
```yaml
# Test mode helper
input_boolean:
  test_mode:
    name: "Test Mode"
    icon: mdi:test-tube

# In automations, wrap actions:
action:
  - if:
      - condition: state
        entity_id: input_boolean.test_mode
        state: "on"
    then:
      - service: notify.mobile_app
        data:
          message: "TEST: Would turn on {{ trigger.entity_id }}"
    else:
      - service: light.turn_on
        target:
          entity_id: light.living_room
```

### 2. Dry Run Automations

```
"Create a 'dry run' version of my automation that:
- Executes all conditions normally
- Logs all action decisions
- Doesn't actually execute actions
- Shows what would have happened"
```

### 3. Staged Rollout

```
"Help me safely test a new automation:
1. Create disabled automation with new logic
2. Add logging to see when it WOULD trigger
3. Run for a week to verify triggers are correct
4. Enable for a single device first
5. Gradually expand to all devices"
```

### 4. Notification-First Testing

```
"Before implementing this automation fully:
- Replace all actions with notifications
- Include trigger info, condition results
- Run for 3 days to verify logic
- Then add real actions"
```

**Example workflow:**
```
"Convert this automation to notification-only for testing:
[paste automation]

I want to see every time it would trigger and what it would do"
```

### 5. Rollback Strategy

```
"Create a safe rollback approach:
- Keep backup of working automation
- Use input_select to switch between versions
- If new version fails, revert with one click
- Log which version is active"
```

---

## Performance Tuning

### 1. Template Optimization

```
"Optimize this template for better performance:
{% for sensor in states.sensor %}
  {% if 'temperature' in sensor.entity_id %}
    {{ sensor.state }}
  {% endif %}
{% endfor %}

Show me the efficient alternative"
```

**Common optimizations:**
```
"What's wrong with these patterns and how to fix:
1. {{ states.sensor.x.state }} vs {{ states('sensor.x') }}
2. Looping through all entities
3. Multiple state calls to same entity
4. Complex templates in often-triggered automations"
```

### 2. Automation Efficiency

```
"Review this automation for performance:
[paste automation]

Check for:
- Unnecessary triggers
- Template complexity in triggers
- Actions that could be parallelized
- Delays that could be replaced with wait_for_trigger"
```

**High-frequency triggers:**
```
"My automation triggers on every state change of sensor.power.
It updates every second. How do I:
- Add debouncing
- Use time_pattern instead
- Filter insignificant changes
- Reduce system load"
```

### 3. Dashboard Performance

```
"My dashboard is slow. Help me optimize:
- Reduce number of entities polled
- Replace history graphs with statistics
- Lazy-load camera feeds
- Use conditional cards effectively
- Minimize template card recalculations"
```

**Card-specific optimization:**
```
"This card redraws constantly:
[paste card config]

How do I reduce update frequency while keeping useful info?"
```

### 4. Database Optimization

```
"My home-assistant_v2.db is 5GB. Help me:
- Identify what's filling the database
- Exclude high-frequency sensors from recorder
- Set appropriate purge_keep_days
- Clean up without losing important history"
```

**Recorder configuration:**
```yaml
recorder:
  purge_keep_days: 10
  exclude:
    domains:
      - automation
      - script
    entity_globs:
      - sensor.*_power  # High-frequency power sensors
    entities:
      - sensor.uptime
```

### 5. Integration Tuning

```
"Tune these integrations for better performance:
- Reduce Zigbee2MQTT polling
- Optimize ESPHome update intervals
- Balance MQTT QoS settings
- Adjust weather update frequency"
```

---

## Migration Guide

### 1. 2024.x Changes

```
"Update my automation from deprecated trigger syntax:
platform: state
entity_id: sensor.x

to the new format used in 2024.x"
```

**Common migrations:**
```
"Help me update these deprecated patterns:
1. entity_id in trigger (string → list)
2. service_template → service with template
3. value_template in conditions → template condition
4. Old forecast attributes → weather.get_forecasts service"
```

### 2. Template Updates

```
"Update these templates for 2024.x best practices:
- {{ states.sensor.x.state }} → {{ states('sensor.x') }}
- Float conversion without defaults
- Accessing unavailable entities
- Handling None values"
```

**Before/after examples:**
```
"Show me the modern way to write:

Old: {{ states.sensor.temp.state | float }}
New: ?

Old: {{ states.sensor.temp.last_changed }}
New: ?

Old: {{ states.sensor.temp.attributes.unit_of_measurement }}
New: ?"
```

### 3. Weather Integration Changes

```
"My weather templates stopped working after update:
{{ state_attr('weather.home', 'forecast')[0].temperature }}

How do I use the new weather.get_forecasts service?"
```

**New pattern:**
```yaml
# Old (deprecated):
{{ state_attr('weather.home', 'forecast')[0].temperature }}

# New (2024.x+):
action:
  - service: weather.get_forecasts
    target:
      entity_id: weather.home
    data:
      type: daily
    response_variable: forecast
  - service: notify.mobile_app
    data:
      message: "Tomorrow: {{ forecast['weather.home'].forecast[0].temperature }}°"
```

### 4. Script/Automation Structure

```
"Update my automation to use the new 2024.x structure:
- Parallel action execution
- Response variables
- Continue on error
- Variables in triggers"
```

**Modern patterns:**
```
"Show me how to convert:
1. Sequential → parallel actions
2. Add error handling to actions
3. Use response_variable for service results
4. Create reusable script with variables"
```

### 5. Integration-Specific Migrations

```
"I'm upgrading from HA 2023.x to 2024.x.
Check my config for deprecated patterns in:
- MQTT sensor configuration
- Template sensor format
- Climate entity attributes
- Media player services"
```

**Migration checklist:**
```
"Create a migration checklist for my configs:
1. Find all deprecated patterns
2. List required changes
3. Prioritize by breakage risk
4. Create test plan for each change"
```

---

## Quick Reference Prompts

### One-Liners

| Want | Prompt |
|------|--------|
| Motion light | "Motion light for [room] with [sensor] and [light]" |
| Schedule | "Turn on [entity] at [time] on [days]" |
| Notification | "Notify when [entity] is [state] for [duration]" |
| Scene | "Create scene [name] with [light] at [brightness]%" |
| Template | "Template showing [calculation] from [sensors]" |

### Debugging

| Issue | Prompt |
|-------|--------|
| Not triggering | "Why doesn't this trigger: [yaml]" |
| Wrong state | "Template returns wrong value: [template]" |
| Slow | "Optimize this for performance: [yaml]" |
| Error | "Getting error [message] from [component]" |

### Best Practices

| Topic | Prompt |
|-------|--------|
| Structure | "Best way to organize automations for [rooms]" |
| Naming | "Naming convention for [entity type]" |
| Performance | "Performance tips for [use case]" |
| Backup | "Backup strategy for production HA" |

---

## Tips for Better Results

1. **Be specific** - Include entity IDs and exact requirements
2. **Share context** - Mention HA version, integrations used
3. **Iterate** - Start simple, add complexity in follow-ups
4. **Test incrementally** - Ask Claude to explain before implementing
5. **Provide errors** - Include exact error messages when troubleshooting

---

## Related Resources

- [PROMPT-IDEAS.md](./PROMPT-IDEAS.md) - 600+ categorized prompt ideas
- [SKILL.md](./SKILL.md) - Full skill documentation
- [references/](./references/) - Detailed reference documentation
- [assets/templates/](./assets/templates/) - Ready-to-use YAML templates
