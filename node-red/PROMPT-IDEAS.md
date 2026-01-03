# Node-RED Prompt Ideas

Example prompts for Node-RED flows. **All prompts explicitly mention "Node-RED flow"** to distinguish from HA YAML or ESPHome.

## Lighting Automations

### Motion Lights

```
Create a Node-RED flow for a motion-activated light in my hallway.
Motion sensor: binary_sensor.hallway_motion
Light: light.hallway
```

```
Build a Node-RED flow for a motion light that only works at night
and turns off after 2 minutes.
Motion: binary_sensor.kitchen_motion
Light: light.kitchen
```

```
Create a Node-RED flow for motion light with manual override -
if I manually turn on the light, disable automation for 30 minutes.
Motion: binary_sensor.bathroom_motion
Light: light.bathroom
```

### Adaptive Lighting

```
Create a Node-RED flow that adjusts light brightness based on time:
- 6-9 AM: 60%
- 9 AM - 9 PM: 100%
- 9-11 PM: 40%
- 11 PM - 6 AM: 10%
Light: light.living_room
```

```
Build a Node-RED flow where lights follow lux sensor - brighter
when it's darker.
Lux sensor: sensor.living_room_lux
Light: light.living_room
Target lux: 300
```

### Scene Control

```
Create a Node-RED flow for a scene controller that activates
different scenes from a dropdown in HA:
- Morning (bright, cool)
- Day (full brightness)
- Evening (dimmed, warm)
- Movie (very dim)
- Night (minimal)
```

```
Build a Node-RED flow that cycles through scenes with a button press.
Button: sensor.living_room_switch_action
Scenes: scene.morning, scene.day, scene.evening, scene.night
```

---

## Presence Detection

### Basic Presence

```
Create a Node-RED flow to turn off all lights and set thermostat
to away mode when the last person leaves home.
Persons: person.john, person.jane
```

```
Build a Node-RED flow: when the first person arrives home,
turn on entry lights and set thermostat to home mode.
```

### Advanced Presence

```
Create a Node-RED flow for arrival automation:
- First person: turn on entry light, disable alarm
- Specific person: play their preferred music
- Anyone: announce "Welcome home" on speaker
```

```
Create a Node-RED flow for leaving automation:
- Last person: turn off all lights, lock doors, arm alarm
- During work hours: set thermostat to away
- Check if windows are open and notify
```

---

## Climate Control

### Temperature

```
Create a Node-RED flow to control my thermostat based on
temperature sensor:
- Below target: heat on
- Above target: heat off
- Use 0.5 degree hysteresis
Sensor: sensor.living_room_temperature
Target: input_number.target_temperature
Thermostat: climate.living_room
```

```
Build a Node-RED flow to turn off heating if any window is open.
Windows: binary_sensor.window_living_room, binary_sensor.window_kitchen
Thermostat: climate.living_room
```

### Scheduling

```
Create a Node-RED flow for a heating schedule:
- Weekdays: 21°C 6-8 AM, 18°C 8 AM-4 PM, 21°C 4-10 PM, 17°C night
- Weekend: 21°C 8 AM-11 PM, 17°C night
```

```
Build a Node-RED flow to reduce heating by 2 degrees when no
motion for 2 hours.
Motion sensors: binary_sensor.motion_*
Thermostat: climate.home
```

---

## Notifications

### Alert Notifications

```
Create a Node-RED flow to send notifications when:
- Door left open more than 5 minutes
- Window open and raining
- Smoke detector triggered
- Water leak detected
```

```
Create a Node-RED flow for security alerts that sends critical
notification when door opens while in away mode.
Door: binary_sensor.front_door
Alarm: alarm_control_panel.home
Notify: notify.mobile_app_phone
```

### Smart Routing

```
Create a Node-RED flow for a notification router that:
- Respects quiet hours (11 PM - 7 AM)
- Only notifies people who are home
- Escalates critical alerts always
```

```
Build a Node-RED flow to route notifications:
- If home: TTS on speakers
- If away: push notification
- If critical: both + phone call
```

### Daily Summaries

```
Create a Node-RED flow to send daily summary at 8 AM with:
- Today's weather
- Calendar events
- Energy usage yesterday
- Any overnight alerts
```

---

## Security

### Door Monitoring

```
Create a Node-RED flow to track when doors are opened and by whom.
Log to a file or Home Assistant sensor.
Doors: binary_sensor.front_door, binary_sensor.back_door
```

```
Build a Node-RED flow to alert if door opens:
- When no one is home
- Between midnight and 6 AM
- More than 5 times in an hour
```

### Window Monitoring

```
Create a Node-RED flow for "leaving home" check that lists all
open windows and doors before arming the alarm.
```

```
Build a Node-RED flow to alert if windows are open and:
- Rain is forecast
- Temperature drops below 10°C
- Alarm is armed
```

---

## Energy Monitoring

### Appliance Tracking

```
Create a Node-RED flow to detect when washing machine finishes:
- Running: power > 10W
- Finished: power < 5W for 2 minutes after running
Notify when done.
Power sensor: sensor.washing_machine_power
```

```
Build a Node-RED flow to track daily energy usage and send
summary at 11 PM.
Energy sensor: sensor.home_energy_daily
```

### High Usage Alerts

```
Create a Node-RED flow to alert if power consumption exceeds
5000W for more than 1 minute.
Power sensor: sensor.home_power
```

```
Build a Node-RED flow for an energy dashboard that tracks:
- Current power usage
- Today's energy
- Cost (at 1.50 SEK/kWh)
- Peak power today
```

---

## Media Control

### Playback Control

```
Create a Node-RED flow for button controller:
- Single press: play/pause
- Double press: next track
- Long press: toggle mute
Button: sensor.bedroom_switch_action
Player: media_player.bedroom_speaker
```

```
Build a Node-RED flow to pause all media when doorbell rings.
Doorbell: binary_sensor.doorbell
Players: media_player.living_room, media_player.kitchen
```

### Automation Integration

```
Create a Node-RED flow for movie scene automation:
- Dim lights to 10%
- Set TV to correct input
- Pause music
- Lower blinds
```

---

## Voice and Presence

### Voice Commands

```
Create a Node-RED flow that responds to "good night" sentence:
- Turn off all lights
- Lock doors
- Set alarm
- Set thermostat to night mode
```

```
Build a Node-RED flow to handle "I'm leaving" command:
- Turn off all lights
- Check all windows
- Announce any issues
- Arm alarm after 30 seconds
```

### Room Presence

```
Create a Node-RED flow to track which room someone is in based
on motion sensors. Update input_select.current_room.
```

```
Build a Node-RED flow for "follow me" light that:
- Turns on light in room with motion
- Turns off light in room without motion (after 5 min)
- Doesn't affect manually controlled lights
```

---

## Time-Based Automations

### Schedules

```
Create a Node-RED flow to turn on porch light at sunset,
off at sunrise.
Light: light.porch
```

```
Build a Node-RED flow for weekday 6:30 AM routine:
- Turn on bedroom light at 30%
- Gradually increase to 100% over 15 minutes
- Start playing news on speaker
```

### Conditional Schedules

```
Create a Node-RED flow for weekday morning routine (skip on holidays):
- 6:30 AM: Bedroom light to 30%
- 6:45 AM: Start coffee maker
- 7:00 AM: Announce weather
Holidays: input_boolean.holiday_mode
```

---

## Integration Patterns

### External Services

```
Fetch weather forecast and adjust today's heating schedule
based on expected temperature.
```

```
When GitHub CI/CD pipeline fails, send notification
with repo name and error type.
```

### Multi-System

```
Sync Spotify playback state to a Home Assistant sensor
for use in automations.
```

```
When Philips Hue motion sensor triggers, also update
corresponding Home Assistant entity.
```

---

## Debugging and Monitoring

### Flow Monitoring

```
Create a monitoring flow that tracks:
- How many times each automation ran today
- Average execution time
- Any errors
Display in HA sensor.
```

```
Log all Node-RED errors to a file with timestamp
and flow name.
```

### Testing

```
Add a test mode to my motion light that simulates
motion every 30 seconds for testing.
```

---

## Advanced Patterns

### State Machines

```
Create an alarm system state machine:
- States: disarmed, arming, armed_home, armed_away, triggered
- Handle transitions between states
- Appropriate actions for each state
```

### Debouncing

```
Debounce my motion sensor - only trigger if motion
is detected for at least 2 seconds.
```

### Rate Limiting

```
Rate limit notifications - maximum 3 per hour
for the same event type.
```

### Retry Logic

```
Create a flow that retries failed API calls
up to 3 times with exponential backoff.
```

---

## Template Requests

### Use a Template

```
Give me the basic-motion-light template
```

```
I need the advanced-motion-light template with
lux sensor and manual override
```

```
Show me the notification-router template
```

### Customize Template

```
Take the presence-detection template and modify it for
3 people instead of 2.
```

```
Adapt the energy-monitor template to use Swedish krona
instead of the default currency.
```

---

## Explanation Requests

### Understanding

```
Explain how the trigger node's extend property works
```

```
What's the difference between trigger-state and events:state?
```

```
How do I access entity attributes in a function node?
```

### Best Practices

```
What's the best way to debounce a motion sensor?
```

```
How should I structure a complex multi-room automation?
```

```
What's the recommended way to handle errors in Node-RED?
```

---

## Quick Reference

### One-Liners

| Request | Example |
|---------|---------|
| Simple trigger | "Turn on X when Y changes to Z" |
| Conditional | "Only if A is true" |
| Delayed | "After N minutes" |
| Scheduled | "Every day at HH:MM" |
| On change | "When X changes from Y to Z" |
| Threshold | "When X goes above/below N" |
| Template | "Give me the X template" |
| Debug | "Why isn't my X flow working?" |

### Common Phrases

```
"Create a flow that..."
"Make an automation for..."
"I need a Node-RED flow that..."
"Build me a..."
"Show me how to..."
"What's wrong with this flow..."
"Optimize my..."
"Add error handling to..."
```

