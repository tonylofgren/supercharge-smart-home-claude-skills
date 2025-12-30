# Automation Examples

Complete collection of 83 prompt examples for Home Assistant automations.
Use these as templates or inspiration for your own automations.

---

## Advanced Prompt Examples

Learn how to write detailed, effective prompts for complex automations.

### How to Write Effective Prompts

Include these elements for best results:

1. **What** - Describe the automation goal clearly
2. **Triggers** - What events should start the automation
3. **Conditions** - When should it run (time, state, etc.)
4. **Actions** - What should happen, in what order
5. **Entities** - List specific entity_ids to use
6. **Edge cases** - Timeouts, fallbacks, error handling
7. **Modes** - Day/night, away/home variations

---

### Example 1: Bathroom Occupancy Logic

```
Create a bathroom automation with "bee in the box" occupancy logic:

Triggers:
- Light turns ON when door opens and bathroom is empty (someone entering)
- Light turns OFF when door opens and bathroom is occupied (someone leaving)
- Light stays on while motion is detected and door is closed

Lighting modes:
- Night mode (22:00-07:00): Warm white (2700K) at 10% brightness
- Day mode (07:00-22:00): Neutral white (4000K) at 100% brightness

Entities:
- Motion sensor: binary_sensor.bathroom_motion
- Door sensor: binary_sensor.bathroom_door (on = open, off = closed)
- Light: light.bathroom

Include a 30-minute timeout fallback to turn off the light if no motion is detected.
```

### Example 2: Multi-room Follow-me Lighting

```
Create a follow-me lighting system that tracks presence across rooms:
- Rooms: living_room, kitchen, hallway, bedroom
- Turn on lights in the room where motion is detected
- Turn off lights in rooms where no motion for 5 minutes
- Do not turn off if someone is still in that room (door sensor logic)
- Night mode: only 20% brightness after 22:00
```

### Example 3: Smart Doorbell with AI Analysis

```
When doorbell button is pressed:
1. Take a snapshot from the door camera
2. If person detected by Frigate, send notification with image
3. If package detected, send "Package delivered" notification
4. If no person/package (false trigger), log but do not notify
5. Different notifications for family members vs strangers
```

### Example 4: Energy-aware Climate Control

```
Smart heating that considers electricity price:
- Entities: climate.living_room, sensor.nordpool_price
- When price < 0.5 SEK/kWh: Heat to 22C (comfort)
- When price 0.5-1.0 SEK/kWh: Heat to 20C (economy)
- When price > 1.0 SEK/kWh: Heat to 18C (minimum)
- Pre-heat 2 hours before wake-up time
- Never heat when no one home (group.family = not_home)
```

### Example 5: Washing Machine Notification

```
Create a smart washing machine notification:

Monitoring:
- Power sensor: sensor.washing_machine_power
- Machine is running when power > 10W
- Machine is done when power drops below 5W for 2 minutes

Notifications:
- Notify when cycle complete: "Washing done! Do not forget to empty."
- If not emptied within 30 min: Reminder every 15 min
- Stop reminders when power goes to 0W (door opened)

Entities:
- Power: sensor.washing_machine_power
- Notify: notify.mobile_app_phone
- Helper to track state: input_boolean.washing_running
```

### Example 6: Garage Door Safety System

```
Garage door automation with safety checks:

Auto-close:
- Close garage door 10 minutes after it opens
- BUT NOT if car is still in garage (binary_sensor.garage_car)
- AND NOT if someone is in garage (binary_sensor.garage_motion)

Safety alerts:
- Notify if door left open > 30 min at night (22:00-06:00)
- Notify immediately if door opens while alarm is armed
- Log all open/close events with timestamp

Entities:
- Door: cover.garage_door
- Car presence: binary_sensor.garage_car
- Motion: binary_sensor.garage_motion
- Alarm: alarm_control_panel.home_alarm
```

### Example 7: Multi-zone Audio Announcements

```
Create a whole-home announcement system:

Features:
- Announce to specific rooms or all rooms
- Lower music volume before announcement, restore after
- Different announcement volume for day (70%) vs night (40%)
- Queue announcements if one is already playing

Input:
- input_text.announcement_message
- input_select.announcement_zones (all, living_room, kitchen, bedroom)

Media players:
- media_player.living_room_speaker
- media_player.kitchen_speaker
- media_player.bedroom_speaker

Include TTS service call with Google/Amazon voice.
```

### Example 8: Plant Watering with Weather Check

```
Smart plant watering reminder:

Check daily at 08:00:
- If no rain forecasted today (weather.home)
- AND soil moisture < 30% (sensor.plant_moisture)
- AND last watered > 2 days ago (input_datetime.last_watered)

Actions:
- Send notification with plant status
- Include forecast info in message
- Add action button "Mark as watered" to update input_datetime

Skip if:
- Rain probability > 60%
- Soil moisture > 50%
- Already watered today
```

### Example 9: Morning Routine Orchestration

```
Create a morning routine that starts when alarm is dismissed:

Trigger: alarm dismissed on phone (companion app event)

Sequence (with delays):
1. Turn on bedroom light at 20% warm white
2. After 5 min: Increase to 50%, start coffee machine
3. After 10 min: Turn on bathroom light, play morning playlist
4. After 15 min: Full brightness, announce weather + calendar events

Cancel if:
- Weekend AND input_boolean.weekend_sleep_in is on
- Anyone already awake (motion in living room last 30 min)
```

### Example 10: TV Mode Multi-device Control

```
Smart TV watching mode:

When TV turns on (media_player.living_room_tv state: playing):
- Dim lights to 30%
- Close blinds if it is daytime
- Set soundbar volume to 35%
- Pause any music playing elsewhere

When TV turns off:
- Restore lights to previous level
- Open blinds if before sunset
- Resume music if it was paused

Do not dim lights if:
- It is already dark outside (sun below horizon)
- Movie mode is already active
```

### Example 11: Sleep Quality Monitoring

```
Track sleep patterns and bedroom conditions:

When bedroom motion stops for 15 min after 22:00:
- Record "sleep started" timestamp
- Monitor and log every hour:
  - Temperature (sensor.bedroom_temperature)
  - Humidity (sensor.bedroom_humidity)
  - CO2 level (sensor.bedroom_co2)

When bedroom motion detected after 05:00:
- Record "wake up" timestamp
- Calculate sleep duration
- Send morning report with sleep duration, avg temp, air quality score

Alert if CO2 > 1000ppm during night.
```

### Example 12: Package Delivery Tracker

```
Track incoming packages:

When motion at front door + no person detected (Frigate):
- Likely package drop-off
- Take snapshot, save to /media/packages/
- Send notification: "Package possibly delivered"

Confirmation:
- If front door opens within 30 min: "Package collected"
- If no collection after 2 hours: Reminder notification
- Track packages in counter.uncollected_packages

Evening summary at 18:00:
- List uncollected packages with timestamps and images
```

### Example 13: Smart Vacuum Scheduling

```
Intelligent vacuum robot scheduling:

Run vacuum when:
- Everyone has left home (group.family = not_home)
- Last cleaned > 2 days ago
- Not during quiet hours (22:00-08:00)
- No one working from home (calendar check)

Before starting:
- Send notification: "Starting vacuum in 5 minutes"
- Wait for potential cancel via actionable notification

While running:
- If doorbell rings: Pause and dock
- If someone comes home: Pause and dock
- Resume when home empty again

After completion:
- Send notification with cleaned area
- Log to history for tracking
```

### Example 14: Freezer Door Alert

```
Critical freezer monitoring:

Monitor binary_sensor.freezer_door:
- If open > 1 minute: First notification
- If still open > 3 minutes: Second notification + flash kitchen light
- If still open > 5 minutes: Critical alert with sound to all devices

Also monitor sensor.freezer_temperature:
- Alert if temperature > -15C
- Critical alert if temperature > -10C
- Log temperature history for insurance claims

Include:
- Door open duration in notifications
- Current temperature in all alerts
- "I am handling it" action button to snooze 10 min
```

### Example 15: Adaptive Activity-based Lighting

```
Smart lighting that adapts to what you are doing:

Detection:
- TV on + low motion: Movie mode (10% warm)
- Desk area motion + computer on: Work mode (100% cool)
- Kitchen motion + stove on: Cooking mode (100% neutral)
- No motion + music playing: Ambient mode (30% warm)

Transitions:
- Fade between modes over 3 seconds
- Do not switch if mode active < 5 minutes (avoid flickering)
- Log mode changes for pattern analysis

Entities:
- Multiple motion sensors per room
- Light groups for different areas
- Various activity indicators (power, media, etc.)
```

### Example 16: Guest Mode Automation

```
Guest-friendly smart home behavior:

When input_boolean.guest_mode turned on:
- Disable: Motion-based lighting off
- Disable: Auto-lock doors
- Disable: Presence-based heating
- Set standard temperatures (21C everywhere)
- Disable personal notifications

Guest Wi-Fi:
- Enable guest network
- Set temporary password
- Share via QR code notification

When guests leave (guest_mode turned off):
- Re-enable all automations
- Reset temperatures to normal
- Disable guest network
- Send summary of guest period
```

### Example 17: Water Leak Emergency

```
Multi-sensor water leak detection:

When ANY water sensor triggers:
1. Immediately send critical notification to all phones
2. Flash all lights red 3 times
3. If available: Close main water valve
4. Announce on all speakers: "Water leak detected in [location]"

Identify location from sensor:
- binary_sensor.leak_kitchen: "Kitchen"
- binary_sensor.leak_bathroom: "Bathroom"
- binary_sensor.leak_laundry: "Laundry room"

Follow-up:
- Reminder every 5 minutes until acknowledged
- Log event with timestamp and location
- Send email with incident report

Recovery:
- When sensor clears: "Leak no longer detected"
- Open water valve (manual confirmation required)
```

### Example 18: Face Recognition Doorbell

```
Advanced doorbell automation:

When doorbell pressed:
1. Take snapshot from camera
2. Check Frigate for known faces

If family member:
- Unlock door automatically (if enabled)
- Announce "[Name] is at the door"
- No notification needed

If unknown person:
- Send notification with snapshot
- Start recording video clip
- Two-way talk option in notification

If no person detected (probably delivery):
- Short notification: "Someone at door - no person visible"
- Save video for later review

Track all visitors in database with timestamps.
```

### Example 19: Window/AC Coordination

```
Climate efficiency automation:

Monitor all window sensors:
- When ANY window opens:
  - Turn off HVAC in that room
  - Send notification if AC was running

- When all windows close:
  - Wait 2 minutes (air exchange)
  - Resume previous HVAC mode

Smart suggestions:
- If outdoor temp is pleasant (18-24C) and AC running:
  Suggest opening windows instead

- If outdoor temp is extreme and window open:
  Alert: "Window open in [room], outdoor temp is [temp]C"

Energy tracking:
- Log wasted energy when AC runs with open window
- Monthly efficiency report
```

### Example 20: Pet Feeding Schedule

```
Smart pet feeding system:

Scheduled feedings:
- Morning: 07:00 (input_number.pet_food_morning grams)
- Evening: 18:00 (input_number.pet_food_evening grams)

Trigger feeder:
- switch.pet_feeder: Dispense food

Monitoring:
- sensor.pet_feeder_level: Track remaining food
- Alert when level < 20%

Smart adjustments:
- If pet has not eaten in 12 hours (motion sensor near bowl):
  Send health alert notification
- If food dispensed but not eaten within 2 hours:
  Log and notify

Manual feed button:
- input_button.feed_pet_now
- Includes anti-spam (max 4 feedings/day)
```

### Example 21: Commute Traffic Helper

```
Smart commute notifications:

Every workday at input_time.commute_alert_time:
1. Check Google Travel Time sensor
2. Compare with average commute

Notifications:
- If traffic > average + 15 min:
  "Heavy traffic! Leave 20 min early"
  Adjust morning routine timing

- If traffic normal:
  "Traffic normal, leave at usual time"

- If traffic < average - 10 min:
  "Light traffic today!"

Include in notification:
- Current estimated time
- Comparison to average
- Weather at destination
- Calendar first meeting time
```

### Example 22: Home Theater Scene

```
Complete movie night automation:

When script.movie_mode called:
1. Turn off all room lights (fade 5 sec)
2. Close all blinds
3. Set TV to correct input
4. Set soundbar to movie preset
5. Turn on bias lighting behind TV (10% color)
6. Set climate to 22C (movie comfort)
7. Enable Do Not Disturb on phones (if integrated)
8. Dim hallway lights to 5% (pathway lighting)

Pause mode (doorbell or motion in hallway):
- Pause playback
- Raise lights to 30%
- Resume on "resume" button

End movie (TV off or script.movie_mode_end):
- Restore all lights
- Open blinds (if daytime)
- Disable DND
```

### Example 23: Power Outage Recovery

```
Handle power outage and recovery:

Detection:
- When HA restarts + last shutdown was unclean
- OR when sensor.ups_status = "On Battery"

Immediate (on battery):
- Send critical notification
- Turn off non-essential devices
- Log outage start time

When power restored:
- Send recovery notification with duration
- Re-enable essential automations first
- Check all smart devices responding
- Report any devices that did not recover

Generate report:
- Outage duration
- Devices affected
- Any automation failures
- Estimated data loss (sensors gaps)
```

### Example 24: Seasonal Lighting

```
Automatic seasonal decorations:

Christmas (Dec 1-Jan 6):
- Enable Christmas light schedule
- Special doorbell chime
- Holiday scenes available
- Outdoor lights at sunset

Halloween (Oct 15-Nov 1):
- Spooky porch lighting
- Motion-triggered sounds at door
- Orange/purple color schemes

Summer mode (Jun-Aug):
- Extended outdoor light schedule
- Pool light automation
- Garden watering integration

Based on:
- Date range checks
- input_boolean overrides for each season
- Weather-aware (rain = no outdoor lights)
```

### Example 25: Senior Check-in System

```
Wellness monitoring for elderly family:

Daily check-in:
- Expect motion by 09:00 each day
- If no motion by 09:00: Send check-in request
- If no response by 10:00: Alert family members
- If no response by 11:00: Emergency contacts

Activity patterns:
- Track daily patterns (bathroom, kitchen, bedroom)
- Alert on significant deviation
- Log activity for family dashboard

Emergency button:
- input_button.emergency_help
- Triggers immediate notification to all contacts
- Includes GPS location if mobile

Weekly report to family:
- Activity summary
- Any alerts triggered
- Overall wellness score
```

### Example 26: Smart Irrigation

```
Intelligent garden watering:

Before watering check:
- Weather forecast (rain probability > 30% = skip)
- Recent rain (sensor.rain_last_24h > 5mm = skip)
- Soil moisture (if available)
- Current temperature (skip if < 5C)

Watering schedule:
- Front yard: Mon/Wed/Fri at 05:00
- Back yard: Tue/Thu/Sat at 05:00
- Flower beds: Daily at 06:00 (shorter)

Adjust duration:
- Hot day (> 30C): +50% water
- Cool day (< 15C): -30% water
- Recent rain: Skip or reduce

Alerts:
- System running notification
- Flow sensor anomaly (leak detection)
- End of season winterization reminder
```

### Example 27: Multi-room Music Sync

```
Whole-home audio management:

Music sync:
- input_select.music_zone (all, downstairs, upstairs, specific room)
- Sync playback across selected zones
- Individual volume controls per room

Smart pausing:
- Doorbell: Pause + announcement + resume
- Phone call: Duck volume 50%
- Timer complete: Pause + announcement + resume

Announcements:
- Queue system (do not interrupt current announcement)
- Different voices for different types
- Volume based on time of day
- Skip sleeping rooms at night

Follow-me audio:
- Track motion across rooms
- Move music to room with activity
- Fade out empty rooms
```

### Example 28: EV Charging Optimizer

```
Smart EV charging with solar and price:

When car plugged in (sensor.ev_plug_status):
- Get current charge level
- Get target charge level (input_number.ev_target_soc)
- Calculate kWh needed

Charging strategy:
1. If solar surplus > 1kW: Charge from solar (free)
2. If electricity price < input_number.cheap_rate: Charge
3. Otherwise: Wait for cheaper rate

Ensure ready by:
- input_time.ev_ready_by (default 07:00)
- Calculate latest start time to reach target
- Force charge if needed regardless of price

Notifications:
- Charging started/stopped
- Target reached
- Estimated cost saved vs immediate charging
- Weekly charging cost summary
```


### Example 29: Garage Door on Phone Bluetooth

```
Create automation to open garage when arriving home:

Trigger:
- Phone connects to car Bluetooth AND phone approaching home zone

Conditions:
- Only between 06:00-23:00
- Garage door is currently closed
- Car was away for > 10 minutes (prevent false triggers)

Actions:
- Open garage door
- Turn on garage lights
- Send notification: "Welcome home, garage opening"

Entities:
- Garage: cover.garage_door
- Phone tracker: device_tracker.my_phone
- Car Bluetooth: binary_sensor.car_bluetooth_connected
- Zone: zone.home
```

### Example 30: Find Phone Announcement

```
Find your phone using smart home:

Trigger:
- Long press (> 3 seconds) on any smart button

Actions:
1. Check which room phone was last seen (Bluetooth proxy)
2. Announce on all speakers: "Phone is in [room]"
3. Send critical alert to phone (rings even on silent)
4. Flash lights in that room 3 times

Entities:
- Buttons: All Shelly BLU buttons
- Speakers: media_player group
- Phone: device_tracker.phone_ble
- Bluetooth proxies: All ESP32 proxies
```

### Example 31: Presence State Machine

```
Presence state machine with grace periods:

States:
- home: Someone is home
- recently_left: Everyone left < 10 minutes ago
- away: Gone > 10 minutes
- extended_away: Gone > 24 hours
- vacation: Gone > 3 days

Transitions:
- home -> recently_left: Last person leaves
- recently_left -> home: Someone returns (forgot something)
- recently_left -> away: 10 minutes pass
- away -> extended_away: 24 hours pass
- extended_away -> vacation: 3 days pass

Actions per state:
- recently_left: Keep lights on, do not arm alarm yet
- away: Turn off everything, arm alarm, adjust climate
- extended_away: Enable presence simulation
- vacation: Lower heating to 15C

Use input_select.presence_state for tracking.
```

### Example 32: Car Bluetooth Menu

```
Show options menu when connecting to car Bluetooth:

Trigger:
- Phone connects to car Bluetooth

Actions:
- Send actionable notification with buttons:
  - "Cool the house" -> Set climate to 21C
  - "Notify spouse" -> Send "On my way home" message
  - "Open garage on arrival" -> Enable proximity trigger
  - "Skip" -> Do nothing

Timeout:
- Auto-dismiss after 30 seconds

Entities:
- Notify: notify.mobile_app
- Climate: climate.home
- Garage trigger: input_boolean.garage_on_arrival
```

### Example 33: Work-from-home Detection

```
Detect work-from-home days from calendar:

Check daily at 06:00:
- Scan calendar.work for "WFH" or "Remote" events
- If found, set input_boolean.working_from_home = on

Adjustments when WFH:
- Do not start vacuum robot
- Keep office at 22C (not eco mode)
- Disable motion-off for office lights
- Extend quiet hours until 09:00

Reset:
- Turn off WFH mode at 18:00 or when leaving home

Entities:
- Calendar: calendar.work
- WFH flag: input_boolean.working_from_home
- Vacuum: vacuum.robot
- Office climate: climate.office
```

### Example 34: Dishwasher Cycle Detection

```
Smart dishwasher monitoring:

Detection:
- Power sensor: sensor.dishwasher_power
- Running: Power > 10W
- Washing phase: Power > 100W (heating)
- Drying phase: Power 50-100W
- Done: Power < 5W for 5 minutes

Notifications:
- Start: "Dishwasher started"
- Done: "Dishwasher finished! Ready to empty"
- Not emptied after 2 hours: Reminder

Tracking:
- input_datetime.dishwasher_started
- input_boolean.dishwasher_running
- counter.dishwasher_cycles
```

### Example 35: Dryer Completion Alert

```
Dryer cycle monitoring with vibration:

Detection methods:
1. Power sensor: sensor.dryer_power
2. Vibration sensor: binary_sensor.dryer_vibration

Cycle complete when:
- Power drops below 5W AND
- No vibration for 2 minutes

Notifications:
- Send to all adults in house
- Include estimated dry time
- Actionable button: "Remind me in 15 min"

Repeat reminders every 20 min until:
- Door sensor triggers (clothes removed)
- Manual dismiss
```

### Example 36: Robot Mower Status

```
Robot lawn mower monitoring:

Normal operation:
- Leaves dock between 10:00-12:00 on schedule
- Returns within 3 hours

Alerts:
- If not returned after 3 hours: "Mower may be stuck"
- If error state: Send notification with error code
- If rain detected: "Mower returned due to rain"

Tracking:
- sensor.mower_status (mowing, returning, docked, error)
- sensor.mower_battery
- sensor.mower_last_activity
```

### Example 37: Coffee Machine Pre-heat

```
Smart coffee machine warm-up:

Triggers:
1. 15 minutes before morning alarm
2. Motion in bedroom after 06:00 on weekdays
3. Manual button press

Conditions:
- Workday (binary_sensor.workday)
- Not on vacation
- Machine has water (if sensor available)

Actions:
- Turn on coffee machine
- After 10 min: Announce "Coffee is ready"

Skip if already running or no one home.
```

### Example 38: Iron Left On Safety

```
Safety automation for iron/curling iron:

Monitor power sensor: sensor.bathroom_iron_power

Alerts:
- After 30 min on: "Iron has been on for 30 minutes"
- After 45 min: Warning + flash lights
- After 60 min: Turn off automatically

Location check:
- If no motion in room for 15 min while iron on:
  Critical alert: "Iron on but room empty!"

Entities:
- Iron: switch.bathroom_iron
- Motion: binary_sensor.bathroom_motion
```

### Example 39: Laundry Basket Sensor

```
Laundry basket fullness detection:

Sensor:
- Pressure mat under laundry basket
- Or load cell/weight sensor

Thresholds:
- Empty: < 1 kg
- Light: 1-3 kg
- Medium: 3-6 kg
- Full: > 6 kg

Notifications:
- When full: "Laundry basket is full"
- Only notify when someone is home
- Max once per day
```

### Example 40: HVAC Pause Cooking

```
Pause ventilation when cooking:

Trigger:
- Stove turns on (power > 100W)
- OR range hood turns on

Actions:
- Pause central HVAC circulation fan
- Switch to recirculate mode
- Turn on kitchen exhaust fan to high

Resume:
- 10 minutes after stove turns off
- OR range hood is turned off
```

### Example 41: Bedroom Air Quality

```
Bedroom air quality during sleep:

Monitor:
- CO2: sensor.bedroom_co2
- Humidity: sensor.bedroom_humidity

Alerts (only 22:00-07:00):
- CO2 > 1000 ppm: "Bedroom air stale, open window"
- CO2 > 1500 ppm: Open motorized window
- Humidity > 70%: Turn on dehumidifier

Morning report:
- Average CO2 during night
- Time spent above 1000 ppm
```

### Example 42: Window Climate Pause

```
Coordinate HVAC with window status:

When any window opens:
- Pause HVAC in that zone
- Send notification: "[Room] window open, HVAC paused"

When window closes:
- Wait 2 minutes (stabilize)
- Resume previous HVAC mode

Long open alert:
- If window open > 30 min in winter (< 10C outside):
  "Window open in [room] - it is cold outside!"
```

### Example 43: Humidity Bathroom Fan

```
Smart bathroom ventilation:

Trigger:
- Humidity rises > 10% above baseline
- OR humidity > 70% absolute

Fan control:
- Turn on bathroom fan
- Run until humidity returns to baseline + 5%
- Maximum runtime: 30 minutes

Speed control (if variable):
- 60-70%: Low speed
- 70-80%: Medium speed
- > 80%: High speed
```

### Example 44: Heated Toilet Seat

```
Adjust toilet seat warmer based on conditions:

Temperature logic:
- Outdoor < 0C: Seat to 35C (warm)
- Outdoor 0-10C: Seat to 32C (medium)
- Outdoor > 10C: Seat to 28C or off

Schedule:
- Enable 06:00-08:00 (morning)
- Enable 21:00-23:00 (bedtime)
- Motion-triggered other times
```

### Example 45: Panic Button Network

```
Whole-home emergency button system:

Devices:
- RF buttons in each room
- Bedside buttons
- Bathroom pull cord

When any panic button pressed:
1. Send critical notification to all adults
2. Flash all lights red 3 times
3. Announce room name: "Help needed in [room]"
4. Log event with timestamp
```

### Example 46: Camera Snapshot to TV

```
Display camera snapshot on TV:

Trigger:
- Motion at front door while home
- Living room TV is on

Actions:
1. Take snapshot from door camera
2. Display on TV for 10 seconds
3. Return to previous content

If TV off: Send to phone instead.
```

### Example 47: Drawer Intrusion Alert

```
Monitor sensitive storage areas:

Sensors on:
- Medicine cabinet
- Gun safe
- Document drawer

Alerts:
- When opened while alarm armed: Critical alert
- Log all access with timestamp

Night rule:
- Medicine cabinet at night: "Someone accessed medicine"
```

### Example 48: Sleep Mode Auto-arm

```
Automatic alarm arming at bedtime:

Trigger conditions (ALL true):
- Time after 22:00
- Bedroom motion stopped for 15 min
- Phone charging (power > 5W)
- All doors/windows closed

Actions:
1. Arm alarm in "home" mode
2. Turn off all non-bedroom lights
3. Set climate to night mode
4. Lock all doors
```

### Example 49: Vacation Simulation

```
Simulate presence when on vacation:

Activate when:
- input_boolean.vacation_mode = on
- OR away for > 48 hours

Simulation (17:00-23:00):
- Turn on/off various lights randomly
- Play TV audio occasionally
- Move blinds
- Vary timing each day

Disable: When first person returns home.
```

### Example 50: Auto-lock Timeout

```
Automatic door locking:

Triggers:
- Door unlocked for > 5 minutes
- OR door closed after being open

Conditions:
- Time is 21:00-07:00 (always lock at night)
- OR no one in entry area for 2 minutes

Actions:
1. Lock the door
2. Send confirmation notification
```

### Example 51: School Time Countdown

```
Morning school countdown announcer:

Trigger:
- Weekday mornings at configured time

Announcements:
- 30 min before: "30 minutes until school bus"
- 15 min before: "15 minutes - time to get ready"
- 5 min before: "5 minutes - get your bags!"
- 0 min: "Bus time! Everyone out!"

Skip on school holidays (calendar.school).
```

### Example 52: Kid Bedtime Sequence

```
Automated bedtime routine for children:

Schedule:
- Weekdays: 20:00
- Weekends: 21:00

Sequence:
1. Living room lights dim to 30%
2. After 15 min: "Bedtime in 15 minutes"
3. After 25 min: Kids room lights on
4. After 30 min: Living room lights off
5. After 45 min: All kids lights off except nightlight

Override: Button can delay 15 min (max once).
```

### Example 53: Chore Reminder Dashboard

```
Dashboard-based chore tracking:

Dashboard elements:
- Buttons for each chore (tap when done)
- Color coding: Green=done, Yellow=due, Red=overdue

Daily chores:
- Dishes, Make beds, Take out dog

Weekly chores (assigned to days):
- Monday: Vacuum
- Wednesday: Trash out
- Friday: Laundry

Notifications:
- Send reminder at 18:00 if daily chores not done
```

### Example 54: Vitamin Tracker

```
Daily medication reminder with dashboard:

Dashboard buttons:
- One button per person
- Tap when vitamins taken
- Resets at 06:00 each day

Reminders:
- 08:00: "Time to take vitamins"
- 12:00: If not taken - reminder
- 18:00: Final reminder

Tracking:
- Log daily compliance
- Weekly summary
```

### Example 55: Elf on the Shelf Mode

```
Holiday Elf on the Shelf automation:

Activate: Dec 1 - Dec 25

Each night after kids bedtime:
1. Set smart switch LEDs to red
2. Red lights stay until elf is moved

When elf is moved:
- Switches return to normal white LEDs
- Play subtle chime sound

Detection: Motion sensor near elf OR parent button.
```

### Example 56: Xbox Auto-reply

```
Gaming session auto-responder:

Trigger:
- Xbox turns on

Actions:
1. If text from spouse: Auto-reply "In gaming mode"
2. Track gaming session start time

When Xbox turns off:
1. Calculate session duration
2. Send notification: "You played for X hours"
3. Reminder: "You have X unread messages"
```

### Example 57: Nintendo Theater Mode

```
Voice-activated basement theater:

Voice command: "Hey Google, Nintendo time"

Actions:
1. Turn on projector
2. Wait 30 seconds (warm-up)
3. Turn on AV receiver, set to Game input
4. Set lights to 10% warm
5. Turn on LED bias lighting
6. Set climate to 22C

"Nintendo off" reverses all actions.
```

### Example 58: Media Player Automation

```
Automated media room when streaming:

Trigger:
- Plex/Jellyfin starts playing

Actions for Movies:
- Close blinds completely
- Dim lights to 5%
- Set soundbar to Movie mode

Actions for TV Shows:
- Close blinds 50%
- Dim lights to 20%

When paused > 5 min:
- Raise lights to 30%

When stopped:
- Restore previous light state
```

### Example 59: Gaming Lighting Profile

```
RGB lighting profiles for gaming:

Trigger:
- PC turns on AND Steam running

Profiles:
- FPS games: Red accent, low ambient
- Racing games: Blue dynamic
- Horror games: Dim purple, random flickers
- Relaxing games: Warm ambient

Default gaming:
- Cool white bias, 20% ambient
```

### Example 60: Media Doorbell Pause

```
Pause media on doorbell:

Trigger:
- Doorbell pressed or motion at door

Actions:
1. If media playing: Pause all
2. Store playing state
3. Take camera snapshot
4. Display on TV or send to phone
5. Announce: "Someone at the door"

After 30 seconds:
6. Resume all previously playing media
```

### Example 61: Automated Fish Feeder

```
Smart aquarium feeding system:

Feeding schedule:
- Morning: 08:00 (small portion)
- Evening: 18:00 (regular portion)

Sequence:
1. Turn off filter
2. Wait 30 seconds
3. Trigger feeder
4. Wait 5 minutes
5. Turn filter back on

Monitoring:
- Track feeder hopper level
- Alert when food running low
```

### Example 62: Tank Temperature Control

```
Precise aquarium temperature control:

Target: 25.5C (tropical fish)
Tolerance: +/- 0.5C

Control loop:
- If temp < 25.0C: Turn on heater
- If temp > 26.0C: Turn off heater

Alerts:
- Temp < 23C: "Tank too cold!"
- Temp > 28C: "Tank overheating!"
- Heater on > 4 hours: "Heater running too long"
```

### Example 63: Pet Zone AI Detection

```
Detect pets in forbidden areas using AI:

Camera integration:
- Frigate or YOLO for object detection
- Detect: dog, cat

Forbidden zones:
- Kitchen counter
- Dining table
- Baby room

When pet detected in forbidden zone:
1. Play deterrent sound
2. Send notification with snapshot
3. Flash nearby light
```

### Example 64: Litter Box Status

```
Cat litter box monitoring:

Door sensor on litter box entrance:
- Track usage frequency

Kitchen light indicator:
- Light turns red if litter door closed (needs cleaning)
- Returns to normal when opened (cleaned)

Health monitoring:
- Alert if cat has not used box in 24 hours
- Alert if usage too frequent (possible UTI)
```

### Example 65: Weather-smart Irrigation

```
Intelligent garden watering:

Before watering check:
- Rain probability > 30%: Skip
- Recent rain > 5mm: Skip
- Temperature < 5C: Skip

Watering zones:
- Front lawn: Mon/Wed/Fri 05:00
- Back lawn: Tue/Thu/Sat 05:00
- Flower beds: Daily 06:00

Duration adjustments:
- Hot day (> 30C): +50% water time
- Cool day (< 15C): -30% water time
```

### Example 66: Garden Door Lighting

```
Backyard lighting when door opens:

Trigger:
- Back door opens after sunset

Actions:
1. Turn on patio lights
2. Turn on pathway lights
3. Start 10-minute timer

Auto-off:
- No motion for 10 minutes
- OR door closes and no outdoor motion
```

### Example 67: Pool Light Schedule

```
Seasonal pool lighting:

Summer schedule (Jun-Aug):
- On at sunset
- Off at 23:00
- Color: Rotating cycle

Winter: Disabled (pool covered)

Party mode:
- Color changing every 30 seconds
- Sync with outdoor speakers

Safety: Always on if motion detected near pool after dark.
```

### Example 68: Rain Forecast Check

```
Check rain before outdoor activities:

Trigger:
- Before scheduled irrigation
- Before outdoor event in calendar

Weather check:
- Get forecast from weather.home
- Check rain probability for next 6 hours

Actions:
- If rain likely: Skip/reschedule
- Send notification with forecast summary
```

### Example 69: Outdoor Motion Lighting

```
Motion-activated outdoor lights:

Trigger:
- Motion at: Front yard, back yard, side gate

Conditions:
- After sunset OR before sunrise
- Not already on from manual control

Brightness by time:
- Evening (sunset-22:00): 100%
- Night (22:00-05:00): 50%
- Morning (05:00-sunrise): 75%

Timeout: 5 minutes after last motion.
```

### Example 70: E-paper Weather Display

```
ESPHome e-paper display with weather:

Display elements:
- Current temperature (large)
- Weather icon
- High/low for today
- 3-day forecast icons
- Indoor temperature and humidity

Update schedule:
- Full refresh every 4 hours
- Partial update every 30 minutes
```

### Example 71: LED Matrix Dashboard

```
Wall-mounted LED matrix display:

Hardware:
- 128x64 RGB LED matrix
- Raspberry Pi Zero or ESP32

Display modes (rotate every 30 sec):
1. Time and date
2. Current weather + temp
3. Calendar - next 3 events
4. HVAC status
5. Who is home

Brightness: Auto-adjust based on room light sensor.
```

### Example 72: Calendar Popup

```
Show calendar when computer starts:

Trigger:
- Computer turns on
- OR user unlocks computer

Check calendar:
- Get today's events from calendar.work
- Filter next 4 hours

If events exist:
- Show notification on computer
- Duration: 60 seconds
```

### Example 73: Server Rack Status

```
Server rack monitoring:

Sensors:
- mmWave presence near rack
- Temperature sensors
- UPS status

LED strip indicators:
- Normal: Soft blue
- Someone present: Bright blue
- High temp: Orange pulse
- UPS on battery: Red strobe
- Internet down: Purple
```

### Example 74: Doom Scrolling Reminder

```
Break social media habit:

Trigger:
- Phone opens Instagram/TikTok/Twitter

First opening:
- Send reminder: "You have opened [app]"

After 15 minutes:
- "15 minutes scrolling"
- Suggest alternative: "How about reading?"

Daily stats:
- Track total time per app
- Evening summary
```

### Example 75: Phone Battery Cutoff

```
Preserve battery health:

Trigger:
- Phone battery reaches 80%

Actions:
1. Turn off smart charger
2. Send notification: "Charging stopped at 80%"

Conditions:
- Only when battery health mode is on
- Not active during travel days

Morning override:
- If phone < 50% at 06:00, charge to 80% anyway
```

### Example 76: Standing Desk Reminder

```
Remind to change desk position:

Trigger:
- Every 45 minutes during work hours (09:00-17:00)

Conditions:
- Workday
- Office occupied
- Not in a meeting

Actions:
1. Flash office light briefly
2. Send notification: "Time to stand/sit!"
```

### Example 77: Air Quality Indicator

```
Ambient air quality indicator light:

Monitor:
- CO2: sensor.room_co2
- PM2.5: sensor.room_pm25

LED color:
- Green: Air excellent
- Yellow: Moderate
- Orange: Poor - open windows
- Red: Very poor

Thresholds (CO2):
- < 600 ppm: Green
- 600-1000 ppm: Yellow
- 1000-1500 ppm: Orange
- > 1500 ppm: Red
```

### Example 78: Water Softener Salt Level

```
Monitor salt level in water softener:

Sensor:
- Ultrasonic distance sensor
- Mounted at top of salt tank

Calculations:
- Empty tank: ~60cm distance
- Full tank: ~10cm distance
- Convert to percentage

Alerts:
- Below 30%: "Salt running low"
- Below 10%: "Salt critical!"
```

### Example 79: Sump Pit Flood Prevention

```
Sump pit water level monitoring:

Sensor:
- Ultrasonic distance in pit
- Or float switches at multiple levels

Levels:
- Normal: < 30cm water
- Warning: 30-45cm
- Critical: > 45cm

Alerts:
- Warning: Notification to check pump
- Critical: Critical alert + flash all lights
- Pump running > 10 min: Alert
```

### Example 80: Mailbox Notification

```
Smart mailbox delivery detection:

Sensor:
- Magnetic contact on mailbox door
- Or light sensor inside

When mail delivered:
1. Send notification: "You have got mail!"
2. Mark as uncollected

When mailbox opened (by you):
- Mark as collected

Evening reminder:
- If mail not collected by 18:00: reminder
```

### Example 81: Garage Door Tilt Sensor

```
Garage door position using accelerometer:

Sensor:
- MPU6050 accelerometer
- Mounted on garage door panel

States:
- Closed: Vertical orientation
- Open: Horizontal orientation
- Partially open: In between

Alerts:
- Door left open > 15 minutes
- Door opened while away from home
```

### Example 82: Soil Moisture Watering

```
Automated plant watering based on soil moisture:

Sensors:
- Capacitive soil moisture sensors

Watering logic:
- If moisture < 30%: Water needed
- If moisture < 20%: Water immediately
- If moisture > 60%: Skip

Watering action:
- Turn on pump for X seconds
- Wait 10 minutes
- Re-check moisture level
```

### Example 83: mmWave Room Presence

```
Accurate room presence using mmWave radar:

Sensor:
- 24GHz mmWave radar (LD2410, LD2450)
- Detects stationary people

Zones (if supported):
- Zone 1: Near desk (working)
- Zone 2: Middle room
- Zone 3: Far corner

Automations:
- Presence in any zone: Room occupied
- Only zone 1: Work mode lighting
- No presence 10 min: Room empty

Advantages over PIR:
- Detects still people
- Through-obstacle detection
```

---

