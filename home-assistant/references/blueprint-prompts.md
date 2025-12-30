# Blueprint Prompt Examples

Complete collection of 50 blueprint prompts for creating reusable Home Assistant blueprints.

---

## Blueprint Prompt Examples

Learn to create reusable automation blueprints based on the most popular community blueprints.

### Blueprint Prompt 1: Sensor Light (Blacky Style - 500K+ views)

```
Create a comprehensive motion-activated light blueprint like the popular "Sensor Light" by Blacky:

Required inputs:
- motion_sensor: entity selector (binary_sensor, device_class: motion)
- door_sensor: entity selector (binary_sensor, device_class: door) - optional
- light_target: target selector (light, switch, scene)
- illuminance_sensor: entity selector (sensor, device_class: illuminance) - optional
- illuminance_threshold: number (0-1000 lux, default 100)

Timing inputs:
- no_motion_wait: number (seconds, 10-600, default 120)
- door_wait: number (seconds, 1-60, default 15) - time after door closes

Sun inputs:
- sun_elevation: number (-90 to 90, default 0) - only run below this elevation
- use_sun: boolean (default true)

Brightness inputs:
- brightness_day: number (1-100, default 100)
- brightness_night: number (1-100, default 30)
- night_start: time (default 22:00)
- night_end: time (default 07:00)

Scene inputs:
- scene_day: entity selector (scene) - optional
- scene_night: entity selector (scene) - optional

Logic:
- Turn on light when motion detected AND (illuminance < threshold OR no sensor)
- Use day/night brightness OR scene based on time
- Turn off after no_motion_wait with no motion
- If door sensor: Also trigger on door open, reset timer on door close
- Respect sun elevation setting
- Do not trigger if light is already on (manual control)

Include blocker entity option to disable automation temporarily.
```

### Blueprint Prompt 2: Low Battery Notifications (161K+ views)

```
Create a low battery notification blueprint:

Required inputs:
- battery_threshold: number (1-100, default 20)
- notification_service: text (default notify.mobile_app)
- check_interval: time_pattern selector (default daily at 09:00)

Optional inputs:
- excluded_entities: entity selector (multiple) - batteries to ignore
- notification_title: text (default "Low Battery Alert")
- group_notifications: boolean (default true) - send one message with all low batteries

Logic:
1. At check_interval, scan all entities with device_class: battery
2. Filter entities below battery_threshold
3. Exclude entities in excluded_entities list
4. If group_notifications: Send single notification listing all low batteries
5. If not grouped: Send individual notification per device

Notification content:
- Device friendly name
- Current battery level
- Days estimate until dead (if available)

Include option to create persistent notification as well.
```

### Blueprint Prompt 3: Appliance Notifications (Washer/Dryer/Dishwasher)

```
Create an appliance cycle monitoring blueprint like the popular "Appliance Notifications":

Required inputs:
- power_sensor: entity selector (sensor, device_class: power)
- appliance_name: text (e.g., "Washing Machine")
- notification_service: text

Threshold inputs:
- running_threshold: number (watts, default 10)
- finished_threshold: number (watts, default 5)
- delay_before_finished: number (minutes, default 3)

Notification inputs:
- start_notification: boolean (default false)
- finished_notification: boolean (default true)
- finished_message: text (default "[appliance] has finished!")

Reminder inputs:
- enable_reminders: boolean (default false)
- reminder_interval: number (minutes, default 30)
- max_reminders: number (1-10, default 3)

Logic:
1. Detect running: power > running_threshold
2. Detect finished: power < finished_threshold for delay_before_finished minutes
3. Send start notification (if enabled)
4. Send finished notification
5. If reminders enabled: Send reminder every interval until acknowledged or max reached

Include action button in notification to dismiss reminders.
Support for door sensor to auto-dismiss when emptied.
```

### Blueprint Prompt 4: Frigate Mobile Notifications 2.0 (227K+ views)

```
Create a Frigate camera notification blueprint:

Required inputs:
- frigate_camera: text (camera name in Frigate)
- notification_service: text
- mobile_app: boolean (true for iOS/Android, false for other)

Detection inputs:
- object_filter: multi-select (person, car, dog, cat, package, etc.)
- zones: text (comma-separated zone names) - optional
- minimum_score: number (0-1, default 0.7)

Notification inputs:
- notification_title: text (default "Motion Detected")
- include_thumbnail: boolean (default true)
- include_snapshot: boolean (default true)
- include_clip: boolean (default true)
- critical_notification: boolean (default false)

Timing inputs:
- cooldown: number (seconds, default 30) - prevent spam
- only_during_away: boolean (default false)

Actions:
- Send notification with thumbnail/snapshot
- Include action buttons: "View Clip", "Silence 1h", "Disable Camera"
- If critical: Use critical notification (bypass DND)

Conditions:
- Only trigger for specified objects
- Only trigger if in specified zones
- Respect cooldown period
- Check away state if enabled
```

### Blueprint Prompt 5: IKEA/Zigbee Button Controller

```
Create a universal Zigbee button controller blueprint supporting multiple protocols:

Required inputs:
- controller_device: device selector
- controller_model: selector (IKEA E1743, E1524, E1812, Hue Dimmer, Aqara Mini, etc.)
- integration: selector (ZHA, Zigbee2MQTT, deCONZ)

Action inputs (per button event):
- short_press_action: action selector
- long_press_action: action selector
- double_press_action: action selector
- release_action: action selector (for dimming)

Light control inputs (if controlling lights):
- target_light: target selector (light)
- brightness_step: number (1-50, default 10)
- transition_time: number (seconds, 0-5, default 0.5)

Mode inputs:
- mode: selector (custom_actions, light_control, media_control)

Logic by mode:
- custom_actions: Execute specified actions for each event
- light_control: Toggle on short, dim on hold, color temp on double
- media_control: Play/pause on short, volume on hold, next/prev on double

Support event mapping for different controller models and integrations.
Include virtual_double_press option for controllers without native support.
```

### Blueprint Prompt 6: Zooz/Z-Wave Scene Controller

```
Create a Z-Wave scene controller blueprint for Zooz switches:

Required inputs:
- switch_device: device selector (Z-Wave node)
- switch_model: selector (ZEN32, ZEN76, ZEN77, ZEN34)

Scene inputs (for each button):
- button_1_tap_action: action selector
- button_1_2x_action: action selector
- button_1_3x_action: action selector
- button_1_4x_action: action selector
- button_1_5x_action: action selector
- button_1_hold_action: action selector
- button_1_release_action: action selector
(repeat for each button on device)

LED inputs:
- led_brightness_day: number (0-100, default 50)
- led_brightness_night: number (0-100, default 10)
- night_mode_start: time (default 22:00)
- night_mode_end: time (default 07:00)
- led_color: selector (color options supported by device)

Logic:
- Listen for zwave_js_value_notification events
- Map scene IDs to button actions
- Execute corresponding action
- Optionally adjust LED brightness based on time
- Support LED color changes for status indication
```

### Blueprint Prompt 7: Adaptive/Circadian Lighting

```
Create an adaptive lighting blueprint for circadian rhythm:

Required inputs:
- target_lights: target selector (light)
- update_interval: number (minutes, 1-30, default 5)

Color temperature inputs:
- min_color_temp: number (Kelvin, 2000-4000, default 2700)
- max_color_temp: number (Kelvin, 4000-6500, default 5500)
- sunrise_offset: number (minutes, -120 to 120, default 0)
- sunset_offset: number (minutes, -120 to 120, default 0)

Brightness inputs:
- min_brightness: number (1-100, default 30)
- max_brightness: number (1-100, default 100)
- brightness_mode: selector (static, sun_based, time_based)

Advanced inputs:
- transition_time: number (seconds, 0-10, default 1)
- only_update_when_on: boolean (default true)
- sleep_mode: boolean input entity - optional
- sleep_color_temp: number (Kelvin, default 2200)
- sleep_brightness: number (default 10)

Logic:
- Calculate optimal color temp based on sun elevation
- Noon = max_color_temp, sunset/sunrise = min_color_temp
- Smooth transition throughout day
- If sleep_mode active: Override with sleep settings
- Only update lights that are currently on (unless configured otherwise)
- Respect manual changes (detect-sleep option)
```

### Blueprint Prompt 8: Advanced Heating Control

```
Create an advanced climate control blueprint:

Required inputs:
- climate_entity: entity selector (climate)
- temperature_sensor: entity selector (sensor, device_class: temperature) - optional

Schedule inputs:
- schedule_entity: entity selector (schedule helper) - optional
- morning_temp: number (15-25, default 21)
- day_temp: number (15-25, default 20)
- evening_temp: number (15-25, default 21)
- night_temp: number (15-25, default 18)
- morning_start: time (default 06:00)
- day_start: time (default 09:00)
- evening_start: time (default 17:00)
- night_start: time (default 22:00)

Presence inputs:
- presence_entity: entity selector (person, group, or binary_sensor)
- away_temp: number (10-18, default 16)
- away_delay: number (minutes, 0-60, default 15)

Window inputs:
- window_sensor: entity selector (binary_sensor) - optional
- window_open_action: selector (turn_off, eco_mode, reduce_temp)
- window_reaction_delay: number (seconds, 0-120, default 30)

Comfort inputs:
- pre_heat_time: number (minutes, 0-60, default 30)
- outdoor_temp_sensor: entity selector - optional
- outdoor_compensation: boolean (adjust based on outdoor temp)

Logic:
- Follow schedule for normal operation
- Override to away_temp when nobody home (after delay)
- React to window opening
- Pre-heat before schedule changes
- Compensate for outdoor temperature
- Use external temp sensor if climate thermostat sensor is inaccurate
```

### Blueprint Prompt 9: Calendar Notifications & Actions

```
Create a calendar-triggered automation blueprint:

Required inputs:
- calendar_entity: entity selector (calendar)
- trigger_offset: number (minutes before event, -1440 to 0, default -15)

Filter inputs:
- title_contains: text - optional (only events containing this text)
- title_regex: text - optional (regex pattern for matching)
- all_day_events: boolean (include all-day events, default false)

Action inputs:
- notification_service: text - optional
- notification_message: template text
- run_script: entity selector (script) - optional
- turn_on_entity: target selector - optional
- turn_off_entity: target selector - optional

Template variables available:
- trigger.calendar_event.summary (event title)
- trigger.calendar_event.start (start time)
- trigger.calendar_event.end (end time)
- trigger.calendar_event.location
- trigger.calendar_event.description

Logic:
- Trigger at offset before matching events
- Apply filters (title match, all-day exclusion)
- Execute configured actions
- Support variables in notification message
- Option to run different actions for start vs end of event
```

### Blueprint Prompt 10: Vacuum Schedule with Presence

```
Create an intelligent vacuum scheduling blueprint:

Required inputs:
- vacuum_entity: entity selector (vacuum)
- schedule_helper: entity selector (schedule)

Presence inputs:
- presence_entity: entity selector (group.family or similar)
- only_when_away: boolean (default true)
- return_on_arrival: boolean (default true) - dock when someone comes home

Notification inputs:
- notification_service: text - optional
- pre_start_notification: boolean (default true)
- pre_start_delay: number (minutes, 1-30, default 5)
- completion_notification: boolean (default true)

Actionable notification inputs:
- enable_snooze: boolean (default true)
- snooze_duration: number (minutes, 15-120, default 30)
- enable_skip: boolean (default true)

Additional conditions:
- door_sensor: entity selector - do not start if door open
- quiet_hours_start: time - optional
- quiet_hours_end: time - optional
- minimum_days_since_clean: number (0-7, default 0)

Logic:
1. Check if scheduled time reached
2. Verify presence condition (away if required)
3. Send pre-start notification with snooze/skip buttons
4. Wait for pre_start_delay or user response
5. If snoozed: Reschedule for snooze_duration later
6. If skipped: Do not clean today
7. Start vacuum
8. If someone comes home and return_on_arrival: Send to dock
9. Send completion notification with cleaned area
```

### Blueprint Prompt 11: Door/Window Left Open Alert

```
Create a door/window left open alert blueprint:

Required inputs:
- door_sensor: entity selector (binary_sensor, device_class: door/window/garage_door)
- alert_delay: number (minutes, 1-60, default 5)
- notification_service: text

Alert inputs:
- notification_title: text (default "Door Left Open")
- notification_message: template text (include door name and duration)
- critical_alert: boolean (default false)

Repeat inputs:
- repeat_notification: boolean (default true)
- repeat_interval: number (minutes, 5-60, default 15)
- max_repeats: number (1-20, default 5)

Additional actions:
- flash_light: target selector (light) - optional
- play_sound: media_player selector - optional
- sound_file: text (path to audio file) - optional

Climate integration:
- climate_entity: entity selector (climate) - optional
- pause_climate: boolean (default false)
- resume_on_close: boolean (default true)

Logic:
1. Wait alert_delay after door opens
2. Send notification with door name
3. Execute additional actions (flash, sound)
4. If climate integration: Pause/resume HVAC
5. Repeat notifications at interval until closed or max reached
6. Send "door closed" notification when resolved

Use trigger context for door name in notifications.
```

### Blueprint Prompt 12: Sun-based Blind/Cover Control

```
Create a sun position blind control blueprint:

Required inputs:
- cover_entity: target selector (cover)
- window_azimuth: number (0-360) - compass direction window faces

Sun inputs:
- sun_azimuth_offset: number (degrees, 0-90, default 45) - sun angle from window direction
- sun_elevation_min: number (0-90, default 15) - minimum sun height to close
- sun_elevation_max: number (0-90, default 70) - close fully above this

Position inputs:
- open_position: number (0-100, default 100)
- partial_position: number (0-100, default 50)
- closed_position: number (0-100, default 0)

Conditions:
- only_when_home: boolean (default true)
- presence_entity: entity selector - optional
- indoor_temp_sensor: entity selector - optional
- outdoor_temp_sensor: entity selector - optional
- temp_threshold: number (close if indoor > threshold, default 24)

Time restrictions:
- start_time: time (earliest action, default 08:00)
- end_time: time (latest action, default 20:00)
- weekend_start_time: time - optional

Logic:
1. Calculate if sun is hitting window (azimuth check)
2. Check sun elevation
3. Determine position: open/partial/closed based on sun angle
4. Apply temperature override (close if too hot)
5. Respect time restrictions
6. Only act if change needed (avoid constant adjustments)
7. Option to open at sunset
```

### Blueprint Prompt 13: Media Room Automation

```
Create a media room automation blueprint:

Required inputs:
- media_player: entity selector (media_player)
- room_lights: target selector (light)

Light behavior inputs:
- playing_brightness: number (0-100, default 10)
- paused_brightness: number (0-100, default 40)
- stopped_brightness: number (0-100, default 100)
- transition_time: number (seconds, 0-10, default 2)

Content-specific inputs:
- movie_brightness: number (0-100, default 5)
- tv_show_brightness: number (0-100, default 20)
- music_brightness: number (0-100, default 50)
- detect_content_type: boolean (default false)

Additional devices:
- cover_entity: target selector (cover) - optional
- close_cover_on_play: boolean (default true)
- open_cover_on_stop: boolean (default true)

Interruption handling:
- doorbell_entity: entity selector (binary_sensor) - optional
- pause_on_doorbell: boolean (default true)
- raise_lights_on_pause: boolean (default true)

Logic:
1. When media starts playing: Dim lights, close covers
2. Detect content type if enabled (movie vs TV)
3. When paused: Raise lights after delay
4. When stopped: Restore lights, open covers
5. Handle doorbell interruption
6. Do not change if lights already off (manual control)

Include bias lighting option for TV backlighting.
```

### Blueprint Prompt 14: Presence-based Room Climate

```
Create a room-by-room presence-based climate blueprint:

Required inputs:
- climate_entity: entity selector (climate)
- presence_sensor: entity selector (binary_sensor, occupancy/motion)
- room_name: text (for notifications)

Temperature inputs:
- occupied_temp: number (15-25, default 21)
- unoccupied_temp: number (10-20, default 17)
- transition_delay: number (minutes, 5-60, default 15)

Schedule inputs:
- schedule_entity: entity selector (schedule) - optional
- schedule_occupied_temp: number - temp during scheduled times
- schedule_unoccupied_temp: number

Boost mode:
- enable_boost: boolean (default true)
- boost_temp_increase: number (1-5, default 2)
- boost_duration: number (minutes, 15-120, default 30)
- boost_trigger: entity selector (button/input_boolean)

Window integration:
- window_sensor: entity selector (binary_sensor) - optional
- window_open_temp: number (frost protection, default 7)

Logic:
1. When presence detected: Set to occupied_temp (after brief delay to confirm)
2. When presence lost for transition_delay: Set to unoccupied_temp
3. Override with schedule if defined
4. Boost mode increases temp temporarily
5. Window open forces frost protection
6. Option to notify on temperature changes
```

### Blueprint Prompt 15: Actionable Notification Script

```
Create a reusable actionable notification script blueprint:

Required inputs:
- notification_service: text
- title: text
- message: text

Action button inputs:
- action_1_title: text - optional
- action_1_action: action selector - optional
- action_2_title: text - optional
- action_2_action: action selector - optional
- action_3_title: text - optional
- action_3_action: action selector - optional

Timeout inputs:
- timeout_duration: number (seconds, 0-3600, default 300)
- timeout_action: action selector - optional
- clear_on_timeout: boolean (default true)

Image inputs:
- camera_entity: entity selector (camera) - optional
- include_snapshot: boolean (default false)
- snapshot_delay: number (seconds, 0-5, default 0)

Notification settings:
- critical: boolean (default false)
- sticky: boolean (default true)
- notification_tag: text - for replacing/clearing
- notification_group: text - for grouping

Logic:
1. Build notification with action buttons
2. Include camera snapshot if configured
3. Send notification
4. Wait for response or timeout
5. Execute corresponding action based on response
6. Execute timeout_action if no response
7. Clear notification if configured

Return selected action for use in calling automation.
```

### Blueprint Prompt 16: Energy Price-based Automation

```
Create an energy price automation blueprint:

Required inputs:
- price_sensor: entity selector (sensor) - electricity price
- target_device: target selector (switch, climate, water_heater)

Price threshold inputs:
- cheap_threshold: number (price below = cheap)
- expensive_threshold: number (price above = expensive)
- currency: text (default from sensor)

Actions by price level:
- cheap_action: action selector (turn on, boost, etc.)
- normal_action: action selector
- expensive_action: action selector (turn off, eco mode)

Schedule inputs:
- only_during_hours: time range - optional
- minimum_runtime: number (hours, 0-24) - ensure device runs this many hours
- preferred_hours: number (1-24) - target cheapest X hours

Forecast inputs:
- use_forecast: boolean (default true)
- forecast_hours: number (1-48, default 24)
- optimize_for_cheapest: boolean (default true)

Logic:
1. Monitor price sensor
2. Compare to thresholds
3. Execute corresponding action
4. If using forecast: Calculate cheapest hours and schedule
5. Ensure minimum_runtime is met using cheapest available hours
6. Consider preferred_hours for optimal scheduling
7. Override options for manual control
```

### Blueprint Prompt 17: Notification Rate Limiter

```
Create a notification rate limiting blueprint:

Required inputs:
- trigger_entity: entity selector (any)
- trigger_state: text (state to trigger on)
- notification_service: text
- message: template text

Rate limiting inputs:
- cooldown_period: number (seconds, 60-86400, default 300)
- max_per_hour: number (1-60, default 10)
- max_per_day: number (1-1000, default 50)

Escalation inputs:
- escalation_count: number (after this many, escalate)
- escalation_notification: text (different service for escalation)
- escalation_message: template text

Quiet hours:
- quiet_hours_start: time - optional
- quiet_hours_end: time - optional
- quiet_hours_action: selector (skip, queue, critical_only)

Logic:
1. Track notification history (use helpers or attributes)
2. Check cooldown since last notification
3. Check hourly and daily limits
4. If within quiet hours: Apply quiet_hours_action
5. Track count for escalation
6. Escalate if threshold reached
7. Reset counters appropriately (hourly/daily)
8. Option to queue notifications for after quiet hours
```

### Blueprint Prompt 18: Device Availability Monitor

```
Create a device availability monitoring blueprint:

Required inputs:
- monitored_entities: entity selector (multiple)
- check_interval: number (minutes, 5-60, default 15)
- notification_service: text

Unavailable detection:
- unavailable_duration: number (minutes, 5-60, default 10)
- include_unknown: boolean (default true)

Notification inputs:
- notification_title: text (default "Device Offline")
- notify_on_unavailable: boolean (default true)
- notify_on_restore: boolean (default true)
- group_notifications: boolean (default true)

Recovery actions:
- restart_integration: text (integration to restart) - optional
- power_cycle_switch: entity selector (switch) - optional
- power_cycle_delay: number (seconds, 5-60, default 10)

Dashboard:
- create_sensor: boolean (create sensor showing offline count)
- offline_list_sensor: boolean (create sensor listing offline devices)

Logic:
1. Regularly check entity availability
2. Track duration of unavailability
3. After unavailable_duration: Send notification
4. Attempt recovery actions if configured
5. Notify when device comes back online
6. Maintain list of currently offline devices
7. Optional: Power cycle via smart plug
```

### Blueprint Prompt 19: Time-based Scene Scheduler

```
Create a scene scheduling blueprint:

Required inputs:
- scene_entity: entity selector (scene)
- schedule_time: time
- days_of_week: multi-select (mon, tue, wed, thu, fri, sat, sun)

Variation inputs:
- random_offset: number (minutes, 0-30, default 0)
- transition_time: number (seconds, 0-60, default 0)

Conditions:
- only_when_home: boolean (default false)
- presence_entity: entity selector - optional
- illuminance_sensor: entity selector - optional
- illuminance_below: number - only run if dark enough

Override inputs:
- override_entity: entity selector (input_boolean) - skip if on
- holiday_calendar: entity selector (calendar) - skip on holidays

Mode inputs:
- mode: selector (scene, script, automation)
- target_entity: entity selector (for script/automation mode)

Logic:
1. Trigger at schedule_time (+/- random_offset)
2. Check day of week
3. Verify conditions (presence, illuminance, overrides)
4. Skip if holiday in calendar
5. Apply transition if configured
6. Activate scene/script/automation
```

### Blueprint Prompt 20: Multi-zone Audio Announcement

```
Create a whole-home announcement blueprint:

Required inputs:
- tts_service: text (e.g., tts.google_translate_say)
- media_players: target selector (media_player, multiple)

Announcement inputs:
- message: template text
- volume: number (0-100, default 50)
- language: text (default "en")

Zone inputs:
- zone_mode: selector (all, specific, presence_based)
- specific_zones: target selector - if specific mode
- presence_entities: entity selector (multiple) - for presence mode

Volume adjustments:
- day_volume: number (0-100, default 60)
- night_volume: number (0-100, default 30)
- night_start: time (default 22:00)
- night_end: time (default 07:00)

Music handling:
- duck_music: boolean (default true)
- duck_volume: number (0-100, default 20)
- restore_music: boolean (default true)
- restore_delay: number (seconds, 2-10, default 3)

Queue handling:
- queue_announcements: boolean (default true)
- max_queue_size: number (1-10, default 5)

Logic:
1. Determine target zones (all/specific/presence)
2. Check current time for volume adjustment
3. If playing music: Duck volume or pause
4. Set announcement volume
5. Play TTS message
6. Wait for completion
7. Restore music if configured
8. Process next in queue if exists
```

### Blueprint Prompt 21: Occupancy State Machine

```
Create a presence state machine blueprint with multiple states:

Required inputs:
- presence_group: entity selector (group or person entities)
- state_helper: entity selector (input_select for tracking state)

State definitions:
- home: At least one person home
- recently_left: Everyone left < grace_period ago
- away: Gone > grace_period, < extended_time
- extended_away: Gone > extended_time, < vacation_time
- vacation: Gone > vacation_time

Timing inputs:
- grace_period: number (minutes, 5-60, default 15)
- extended_time: number (hours, 1-48, default 24)
- vacation_time: number (days, 1-14, default 3)

Actions per state transition:
- home → recently_left: action selector (keep lights, hold alarm)
- recently_left → home: action selector (cancel away prep)
- recently_left → away: action selector (turn off, arm alarm)
- away → extended_away: action selector (enable simulation)
- extended_away → vacation: action selector (lower heating)
- any → home: action selector (welcome home actions)

Notification inputs:
- notify_on_state_change: boolean (default true)
- notification_service: text

Logic:
1. Monitor presence_group for state changes
2. When last person leaves: Start recently_left timer
3. If someone returns during grace: Cancel transition, stay home
4. After grace_period: Transition to away, execute actions
5. Continue timing for extended states
6. Any arrival: Immediate transition to home

Include input_datetime helpers for tracking state timestamps.
```

### Blueprint Prompt 22: Multi-Person Tracking with Individual Routines

```
Create a multi-person presence blueprint with individual preferences:

Required inputs:
- persons: entity selector (person, multiple)
- person_preferences_helper: entity selector (input_text for JSON prefs)

Per-person settings (stored in helper as JSON):
- preferred_temperature: number
- preferred_lights: entity list
- arrival_scene: scene entity
- departure_scene: scene entity
- notification_enabled: boolean

Tracking inputs:
- track_zones: entity selector (zone, multiple)
- home_zone: entity selector (zone, default zone.home)
- proximity_threshold: number (meters, 100-5000, default 500)

Priority inputs:
- conflict_resolution: selector (first_home, last_home, average, specific_person)
- priority_person: entity selector (person) - if specific_person mode

Logic:
1. Track each person's zone and proximity separately
2. When first person arrives home:
   - Apply their preferences
   - Run their arrival scene
3. When additional person arrives:
   - Merge preferences based on conflict_resolution
   - Run their arrival scene (optionally)
4. When person leaves but others remain:
   - Recalculate merged preferences
   - Run their departure scene
5. When last person leaves:
   - Run house-wide departure routine

Include dashboard card template showing all person states.
```

### Blueprint Prompt 23: Guest Mode with Restricted Access

```
Create a guest mode blueprint with smart restrictions:

Required inputs:
- guest_mode_toggle: entity selector (input_boolean)
- guest_wifi_switch: entity selector (switch) - optional

Duration inputs:
- auto_disable_after: number (hours, 1-168, default 24)
- extend_on_activity: boolean (default true)
- activity_sensors: entity selector (binary_sensor, multiple)

Automation control:
- disable_automations: entity selector (automation, multiple)
- simplify_automations: entity selector (automation, multiple)

Climate inputs:
- guest_temperature: number (18-25, default 21)
- override_schedule: boolean (default true)

Security inputs:
- keep_security_active: boolean (default true)
- guest_access_code: text - optional (for smart locks)
- allowed_entry_times: time range - optional

WiFi guest network:
- guest_wifi_ssid: text
- generate_qr_code: boolean (default true)

Logic:
1. When guest_mode enabled:
   - Disable complex automations
   - Set standard temperatures
   - Enable guest WiFi
   - Generate and notify QR code
   - Start auto-disable timer
2. During guest mode:
   - Extend timer on activity (if enabled)
   - Maintain basic comfort automations
   - Log guest-related events
3. When guest_mode disabled (manual or timeout):
   - Re-enable all automations
   - Restore normal schedules
   - Disable guest WiFi
   - Clear temporary access codes

Send summary of guest period when deactivated.
```

### Blueprint Prompt 24: Work-from-Home Detection Blueprint

```
Create a WFH detection blueprint using multiple signals:

Required inputs:
- person: entity selector (person)
- wfh_indicator: entity selector (input_boolean for WFH state)

Detection methods (at least one required):
- calendar_entity: entity selector (calendar) - check for WFH events
- calendar_keywords: text (comma-separated, default "WFH,Remote,Home Office")
- work_computer_entity: entity selector (device_tracker/binary_sensor)
- work_hours: time range selector (default 09:00-17:00)

Confirmation inputs:
- require_home_presence: boolean (default true)
- confirmation_delay: number (minutes, 5-30, default 15)

WFH adjustments:
- office_climate: entity selector (climate) - optional
- office_temperature: number (20-24, default 22)
- quiet_mode_start: time (default 09:00)
- quiet_mode_end: time (default 12:00)
- disable_vacuum: boolean (default true)
- vacuum_entity: entity selector (vacuum) - optional

Focus mode inputs:
- enable_focus_mode: boolean (default false)
- focus_dnd_devices: entity selector (multiple)
- meeting_calendar: entity selector (calendar) - optional

Logic:
1. Daily check at work_hours start:
   - Check calendar for WFH keywords
   - Check if person is home
   - Check work computer presence
2. If WFH detected:
   - Set wfh_indicator on
   - Apply office temperature
   - Enable quiet hours (no robot vacuum)
   - Optionally enable focus mode
3. During meetings (from calendar):
   - Enable DND on specified devices
   - Optionally adjust lighting
4. At work_hours end:
   - Reset wfh_indicator
   - Restore normal schedules

Include weekly WFH summary notification.
```

### Blueprint Prompt 25: Bayesian Presence Combining Multiple Sensors

```
Create a Bayesian presence blueprint combining multiple sensor types:

Required inputs:
- room_name: text
- presence_output: entity selector (input_boolean for result)

Sensor inputs (all optional, at least 2 required):
- pir_motion_sensor: entity selector (binary_sensor, motion)
- mmwave_sensor: entity selector (binary_sensor, occupancy)
- door_sensor: entity selector (binary_sensor, door)
- bed_sensor: entity selector (binary_sensor) - pressure mat
- desk_sensor: entity selector (binary_sensor) - chair occupancy
- media_player: entity selector (media_player)
- computer_tracker: entity selector (device_tracker)
- light_switch_usage: entity selector (binary_sensor)

Probability weights:
- pir_weight: number (0-1, default 0.6)
- mmwave_weight: number (0-1, default 0.9)
- door_weight: number (0-1, default 0.3)
- bed_weight: number (0-1, default 0.95)
- desk_weight: number (0-1, default 0.85)
- media_weight: number (0-1, default 0.7)
- computer_weight: number (0-1, default 0.8)

Threshold inputs:
- presence_threshold: number (0-1, default 0.7)
- absence_threshold: number (0-1, default 0.3)
- update_interval: number (seconds, 5-60, default 10)

Decay inputs:
- pir_decay_time: number (minutes, 1-30, default 5)
- door_decay_time: number (minutes, 1-10, default 2)

Logic:
1. Calculate probability score from all active sensors
2. Apply decay to sensors that haven't triggered recently
3. Weight sensors based on reliability (mmwave > PIR)
4. If score > presence_threshold: Mark as occupied
5. If score < absence_threshold: Mark as empty
6. Between thresholds: Keep previous state (hysteresis)

Create template sensor showing:
- Current probability score
- Contributing sensors
- Time in current state

Include calibration mode to tune weights.
```

### Blueprint Prompt 26: Follow-Me Lighting Across Rooms

```
Create a follow-me lighting blueprint:

Required inputs:
- rooms: text (comma-separated room names matching areas)
- motion_sensors: entity selector (binary_sensor, multiple)
- lights: target selector (light, multiple)

Mapping inputs:
- room_sensor_mapping: object (JSON mapping rooms to sensors)
- room_light_mapping: object (JSON mapping rooms to lights)

Timing inputs:
- follow_delay: number (seconds, 0-30, default 5) - delay before following
- trail_off_delay: number (minutes, 1-30, default 5) - turn off after leaving
- transition_time: number (seconds, 0-10, default 2)

Brightness inputs:
- day_brightness: number (1-100, default 100)
- night_brightness: number (1-100, default 30)
- night_start: time (default 22:00)
- night_end: time (default 07:00)

Advanced inputs:
- pathway_lighting: boolean (default true) - light path between rooms
- pathway_brightness: number (1-100, default 20)
- adaptive_brightness: boolean (default false) - adjust based on activity

Exclusions:
- excluded_rooms: entity selector (area, multiple) - never auto-light
- excluded_times: time range selector - disable during times

Logic:
1. Track motion across all rooms
2. When motion in new room:
   - Wait follow_delay (confirm not passing through)
   - Turn on lights in new room
   - If pathway_lighting: Light path from previous room
3. When no motion in room for trail_off_delay:
   - Fade out lights
   - Update "last seen" room
4. Maintain presence history for smart predictions

Include occupancy heatmap data for dashboard.
```

### Blueprint Prompt 27: Wake-Up Light with Gradual Brightness

```
Create a sunrise simulation wake-up light blueprint:

Required inputs:
- target_light: entity selector (light with brightness + color_temp)
- alarm_time_source: selector (manual_time, phone_alarm, calendar)

Time inputs (if manual_time):
- wake_time: time
- weekday_only: boolean (default true)
- weekend_offset: number (minutes, 0-180, default 60)

Duration inputs:
- fade_duration: number (minutes, 10-60, default 30)
- hold_duration: number (minutes, 5-30, default 15)
- fade_steps: number (10-100, default 50)

Color temperature inputs:
- start_color_temp: number (Kelvin, 1800-3000, default 2000)
- end_color_temp: number (Kelvin, 3500-6500, default 4500)
- color_temp_curve: selector (linear, exponential, natural_sunrise)

Brightness inputs:
- start_brightness: number (1-10, default 1)
- end_brightness: number (50-100, default 100)
- brightness_curve: selector (linear, exponential, logarithmic)

Sound integration:
- enable_sound: boolean (default false)
- media_player: entity selector (media_player) - optional
- sound_source: selector (nature_sounds, music_playlist, radio)
- sound_fade_in: boolean (default true)
- max_volume: number (1-100, default 30)

Snooze inputs:
- enable_snooze: boolean (default true)
- snooze_button: entity selector (binary_sensor/input_button)
- snooze_duration: number (minutes, 5-15, default 9)
- max_snoozes: number (1-5, default 3)

Logic:
1. Calculate start time (wake_time - fade_duration)
2. Begin fade sequence at start_color_temp and start_brightness
3. Gradually increase every (fade_duration / fade_steps) minutes
4. Follow curve for natural progression
5. At wake_time: Start sounds if enabled
6. Hold at end values for hold_duration
7. Handle snooze: Dim to 30%, restart after snooze_duration

Include motion detection to cancel if already awake.
```

### Blueprint Prompt 28: Party Mode Color Cycling

```
Create a party mode lighting blueprint:

Required inputs:
- party_lights: target selector (light with RGB)
- party_toggle: entity selector (input_boolean)

Color inputs:
- color_palette: selector (rainbow, warm, cool, custom)
- custom_colors: text (comma-separated hex colors) - if custom
- saturation: number (50-100, default 100)

Animation inputs:
- animation_mode: selector (cycle, random, music_sync, strobe, wave)
- cycle_speed: number (seconds per color, 1-30, default 5)
- transition_style: selector (instant, fade, crossfade)
- transition_time: number (seconds, 0-5, default 1)

Music sync inputs (if music_sync mode):
- audio_sensor: entity selector (sensor) - for beat detection
- bass_color: color selector (default red)
- mid_color: color selector (default green)
- treble_color: color selector (default blue)

Zone inputs:
- sync_all_lights: boolean (default true)
- zone_offset: number (0-5, default 1) - stagger between lights

Strobe inputs (if strobe mode):
- strobe_speed: number (Hz, 1-10, default 3)
- strobe_color: color selector (default white)
- strobe_max_duration: number (seconds, 10-300, default 60)

Safety inputs:
- max_duration: number (hours, 1-12, default 4)
- auto_disable_time: time - optional
- photosensitivity_safe: boolean (default false) - slower, no strobe

Logic:
1. When party_toggle enabled:
   - Store current light states for restoration
   - Start animation loop based on mode
2. Animation loop:
   - Calculate next color(s) based on mode
   - Apply to lights with transition
   - Handle zone offset for wave effects
3. Music sync:
   - Monitor audio sensor
   - Map frequency bands to colors
   - Adjust brightness based on volume
4. Auto-disable after max_duration or at auto_disable_time
5. Restore original light states when disabled

Include intensity slider for real-time control.
```

### Blueprint Prompt 29: Ambient Light Sensor Adaptive Brightness

```
Create an adaptive brightness blueprint using ambient light sensors:

Required inputs:
- target_lights: target selector (light with brightness)
- illuminance_sensor: entity selector (sensor, device_class: illuminance)

Brightness mapping:
- min_ambient_lux: number (0-100, default 10)
- max_ambient_lux: number (100-2000, default 500)
- min_light_brightness: number (1-100, default 100)
- max_light_brightness: number (1-100, default 20)
- response_curve: selector (linear, logarithmic, inverse_square)

Control inputs:
- enable_toggle: entity selector (input_boolean) - optional
- only_when_on: boolean (default true)
- update_interval: number (seconds, 10-300, default 60)

Transition inputs:
- transition_time: number (seconds, 0-10, default 2)
- rate_limit: number (changes per minute, 1-10, default 2)
- min_change: number (percent, 1-20, default 5)

Time restrictions:
- active_start: time - optional
- active_end: time - optional
- respect_sun: boolean (default true) - only active after sunset

Manual override:
- override_duration: number (minutes, 5-120, default 30)
- detect_manual_change: boolean (default true)

Logic:
1. Monitor illuminance_sensor at update_interval
2. Calculate target brightness based on mapping curve:
   - Low ambient light → High brightness
   - High ambient light → Low brightness
3. Apply rate limiting to prevent rapid changes
4. Skip if change is below min_change threshold
5. Detect manual brightness changes and pause automation
6. Resume after override_duration

Include template sensor showing current adaptation level.
```

### Blueprint Prompt 30: Multi-Stage Motion Lighting

```
Create a multi-stage motion lighting blueprint:

Required inputs:
- motion_sensor: entity selector (binary_sensor, motion)
- target_light: entity selector (light with brightness)

Stage definitions:
- stage_1_brightness: number (1-100, default 100)
- stage_1_duration: number (minutes, 1-60, default 10)
- stage_2_brightness: number (1-100, default 50)
- stage_2_duration: number (minutes, 1-60, default 5)
- stage_3_brightness: number (1-100, default 20)
- stage_3_duration: number (minutes, 1-30, default 2)

Optional stages:
- enable_stage_4: boolean (default false)
- stage_4_brightness: number (1-100, default 5)
- stage_4_duration: number (minutes, 1-10, default 1)

Transition inputs:
- inter_stage_transition: number (seconds, 0-30, default 5)
- final_off_transition: number (seconds, 0-60, default 10)

Time-based adjustments:
- night_mode: boolean (default true)
- night_start: time (default 22:00)
- night_end: time (default 07:00)
- night_max_brightness: number (1-100, default 30)
- night_stage_multiplier: number (0.5-2, default 1.5) - longer stages at night

Motion sensitivity:
- reset_on_motion: boolean (default true)
- motion_debounce: number (seconds, 0-10, default 2)

Door integration:
- door_sensor: entity selector (binary_sensor, door) - optional
- door_triggers_stage_1: boolean (default true)

Logic:
1. Motion detected:
   - If light off: Turn on at stage_1_brightness
   - If light on (any stage): Reset to stage_1
   - Start stage_1_duration timer
2. Timer expires without motion:
   - Transition to next stage
   - Start next stage timer
3. Continue through stages until final off
4. Apply night mode adjustments during night hours

Include stage indicator helper for dashboard.
```

### Blueprint Prompt 31: EV Smart Charging with Price + Solar

```
Create an EV smart charging blueprint:

Required inputs:
- charger_switch: entity selector (switch)
- ev_soc_sensor: entity selector (sensor) - state of charge
- price_sensor: entity selector (sensor) - electricity price

Solar inputs:
- solar_power_sensor: entity selector (sensor) - optional
- solar_threshold: number (watts, 500-5000, default 1500)
- prefer_solar: boolean (default true)

Price inputs:
- cheap_price_threshold: number (currency, default 0.5)
- expensive_price_threshold: number (currency, default 1.5)
- use_price_forecast: boolean (default true)

Charging targets:
- target_soc: number (50-100, default 80)
- minimum_soc: number (10-50, default 20)
- ready_by_time: time (default 07:00)
- ready_by_day: multi-select (weekdays)

Charging rate inputs:
- charger_power: number (kW, 1-22, default 7.4)
- charging_efficiency: number (0.8-1, default 0.9)

Priority inputs:
- charging_priority: selector (cheapest_first, solar_first, fastest, scheduled)
- force_charge_below: number (percent, 10-30, default 20)

Notification inputs:
- notify_service: text - optional
- notify_on_start: boolean (default false)
- notify_on_complete: boolean (default true)
- notify_cost_summary: boolean (default true)

Logic:
1. When car plugged in:
   - Calculate kWh needed: (target_soc - current_soc) * battery_capacity
   - Calculate hours needed: kWh / (charger_power * efficiency)
2. Based on priority:
   - cheapest_first: Find cheapest hours before ready_by_time
   - solar_first: Wait for solar > threshold, supplement with cheap hours
   - fastest: Charge immediately
   - scheduled: Charge during specified window
3. During charging:
   - Monitor solar production if available
   - Adjust charging based on real-time price
4. Stop when target_soc reached
5. Force charge if below minimum_soc regardless of price

Include charging cost tracking and weekly summary.
```

### Blueprint Prompt 32: Solar Self-Consumption Optimizer

```
Create a solar self-consumption optimization blueprint:

Required inputs:
- solar_power_sensor: entity selector (sensor) - current production
- grid_import_sensor: entity selector (sensor) - power from grid
- grid_export_sensor: entity selector (sensor) - power to grid

Controllable loads (priority order):
- loads: object selector (JSON array of load definitions)
  Each load: {entity: switch/climate, power: watts, priority: 1-10, min_runtime: minutes}

Example loads:
- EV charger: 7000W, priority 1
- Heat pump: 2000W, priority 2
- Water heater: 3000W, priority 3
- Pool pump: 1500W, priority 4
- Dishwasher: 2000W, priority 5

Threshold inputs:
- export_threshold: number (watts, 100-1000, default 200)
- import_threshold: number (watts, 100-1000, default 200)
- hysteresis: number (watts, 50-200, default 100)

Timing inputs:
- min_on_time: number (minutes, 5-60, default 15)
- min_off_time: number (minutes, 5-30, default 10)
- forecast_lookahead: number (hours, 0-4, default 1)

Battery inputs (optional):
- battery_soc_sensor: entity selector (sensor)
- battery_power_sensor: entity selector (sensor)
- min_battery_soc: number (10-50, default 20)
- prefer_battery_over_export: boolean (default true)

Logic:
1. Monitor solar production and consumption continuously
2. When export > export_threshold:
   - Find highest priority load that fits available power
   - Turn on load, record start time
3. When import > import_threshold:
   - Find lowest priority running load
   - Check min_runtime satisfied
   - Turn off load
4. Respect hysteresis to prevent rapid switching
5. Use forecast to pre-position loads

Create dashboard showing:
- Current solar production
- Current consumption breakdown
- Self-consumption percentage
- Daily savings
```

### Blueprint Prompt 33: Multi-Appliance Load Balancer

```
Create a load balancing blueprint to prevent electrical overload:

Required inputs:
- main_power_sensor: entity selector (sensor) - total consumption
- max_load: number (watts, 1000-50000)

Appliance definitions:
- appliances: object (JSON array)
  Each: {entity: switch, name: text, power: watts, priority: 1-10, deferrable: boolean}

Priority levels:
- 1-3: Critical (never disable: heating, fridge)
- 4-6: Important (delay if needed: EV charger, water heater)
- 7-10: Deferrable (dishwasher, washing machine)

Safety inputs:
- warning_threshold: number (percent of max, 70-90, default 80)
- critical_threshold: number (percent of max, 85-99, default 95)
- trip_prevention_margin: number (watts, 100-1000, default 500)

Queue inputs:
- enable_queue: boolean (default true)
- max_queue_time: number (minutes, 30-480, default 120)
- queue_notification: boolean (default true)

Notification inputs:
- notify_service: text
- notify_on_shed: boolean (default true)
- notify_on_restore: boolean (default true)

Logic:
1. Continuous monitoring of main_power_sensor
2. Warning threshold crossed:
   - Send notification
   - Prepare to shed loads
3. Critical threshold crossed:
   - Find lowest priority deferrable appliance
   - Turn off, add to queue
   - Repeat until below warning threshold
4. When load decreases:
   - Check queue for waiting appliances
   - Turn on highest priority queued appliance if capacity allows
5. Queue timeout:
   - Notify user if appliance waited too long
   - Option to force-run regardless

Create priority override option for special circumstances.
```

### Blueprint Prompt 34: Battery Storage Automation

```
Create a home battery storage optimization blueprint:

Required inputs:
- battery_soc_sensor: entity selector (sensor)
- battery_power_sensor: entity selector (sensor)
- battery_mode_select: entity selector (select/input_select)

Available modes:
- self_consumption: Maximize solar use
- time_of_use: Charge cheap, discharge expensive
- backup: Maintain reserve for outages
- grid_support: Respond to grid signals

Price inputs:
- price_sensor: entity selector (sensor)
- cheap_threshold: number
- expensive_threshold: number
- use_forecast: boolean (default true)

Reserve inputs:
- minimum_soc: number (10-50, default 20)
- backup_reserve: number (20-80, default 30)
- winter_reserve: number (20-80, default 50)
- season_aware: boolean (default true)

Charging inputs:
- max_charge_rate: number (kW)
- max_discharge_rate: number (kW)
- charge_from_grid: boolean (default true)

Time windows:
- force_charge_window: time range - optional
- block_discharge_window: time range - optional

Grid export inputs:
- enable_grid_export: boolean (default true)
- export_price_minimum: number - only export above this price

Logic per mode:

self_consumption:
1. Solar available > home load: Charge battery
2. Solar < home load: Discharge to meet demand
3. Never charge from grid

time_of_use:
1. During cheap hours: Charge to 100%
2. During expensive hours: Discharge to minimum_soc
3. Between: Self-consumption mode

backup:
1. Always maintain backup_reserve
2. Only use excess for optimization

Include battery health tracking (cycle count, degradation).
```

### Blueprint Prompt 35: Peak Hour Load Shifting

```
Create a peak hour load shifting blueprint:

Required inputs:
- price_sensor: entity selector (sensor)
- shiftable_loads: target selector (switch, multiple)

Peak definition:
- peak_detection: selector (price_based, time_based, utility_signal)
- peak_price_threshold: number - if price_based
- peak_start_time: time (default 17:00) - if time_based
- peak_end_time: time (default 21:00) - if time_based
- peak_signal_entity: entity selector - if utility_signal

Load categories:
- loads_config: object (JSON)
  Each: {entity, name, can_pre_run: bool, can_delay: bool, max_delay: minutes}

Pre-conditioning:
- pre_cool_temperature: number (degrees below setpoint)
- pre_heat_temperature: number (degrees above setpoint)
- climate_entities: target selector (climate)
- pre_condition_duration: number (minutes, 30-180, default 60)

Notification inputs:
- notify_before_peak: boolean (default true)
- notify_minutes_before: number (15-60, default 30)
- notify_service: text

User override:
- override_entity: entity selector (input_boolean)
- override_duration: number (minutes, 30-120, default 60)

Logic:
1. Detect upcoming peak (forecast or schedule)
2. Before peak starts:
   - Run deferrable loads that can pre-run
   - Pre-condition climate (cool/heat building mass)
   - Send notification
3. During peak:
   - Pause all shiftable loads
   - Let climate drift within comfort range
4. After peak ends:
   - Resume shiftable loads in priority order
   - Restore climate setpoints

Track savings from load shifting.
```

### Blueprint Prompt 36: Multi-Room Audio Zone Controller

```
Create a multi-room audio zone management blueprint:

Required inputs:
- media_players: entity selector (media_player, multiple)
- zone_definitions: object (JSON mapping zones to players)

Zone grouping:
- enable_grouping: boolean (default true)
- group_method: selector (native, snapcast, squeezebox, chromecast)

Follow-me inputs:
- enable_follow_me: boolean (default true)
- presence_sensors: entity selector (binary_sensor, multiple)
- room_sensor_mapping: object (JSON)
- transfer_delay: number (seconds, 5-30, default 10)

Volume management:
- per_room_volume: object (JSON - room: default_volume)
- night_volume_reduction: number (percent, 20-50, default 30)
- night_start: time (default 22:00)
- night_end: time (default 07:00)

Source inputs:
- available_sources: text (comma-separated)
- default_source: text

Announcement handling:
- announcement_volume: number (1-100, default 50)
- duck_music_volume: number (1-100, default 20)
- resume_delay: number (seconds, 2-10, default 3)
- skip_sleeping_rooms: boolean (default true)
- sleeping_indicator: entity selector (input_boolean)

Queue management:
- queue_announcements: boolean (default true)
- max_queue: number (1-10, default 5)
- announcement_priority: selector (normal, high, critical)

Logic:
1. Zone grouping:
   - Create/modify speaker groups on demand
   - Sync playback across grouped zones
2. Follow-me audio:
   - Track presence across rooms
   - When motion in new room: Wait transfer_delay
   - Transfer audio to new room
   - Optionally keep playing in previous room
3. Announcement system:
   - Detect zones where music is playing
   - Duck volume, play TTS, restore
   - Queue if announcement in progress

Create dashboard for zone selection and volume control.
```

### Blueprint Prompt 37: Content-Type Detection Automation

```
Create a content-type detection blueprint for media rooms:

Required inputs:
- media_player: entity selector (media_player)
- room_lights: target selector (light)

Detection methods:
- detection_source: selector (media_player_attribute, plex_api, jellyfin_api, emby_api, manual)
- api_sensor: entity selector (sensor) - for API-based detection

Content types and settings:
- movie_settings:
  - brightness: number (0-100, default 5)
  - color_temp: number (Kelvin, default 2700)
  - close_blinds: boolean (default true)
- tv_show_settings:
  - brightness: number (0-100, default 20)
  - color_temp: number (Kelvin, default 3000)
  - close_blinds: boolean (default true)
- music_settings:
  - brightness: number (0-100, default 50)
  - enable_visualizer: boolean (default false)
- sports_settings:
  - brightness: number (0-100, default 60)
  - color_temp: number (Kelvin, default 4000)
- gaming_settings:
  - brightness: number (0-100, default 30)
  - bias_lighting: boolean (default true)

Additional devices:
- cover_entity: target selector (cover) - blinds/curtains
- soundbar_entity: entity selector (media_player)
- soundbar_presets: object (JSON mapping content_type to preset)

Transition inputs:
- transition_time: number (seconds, 0-10, default 3)
- restore_on_stop: boolean (default true)

Override inputs:
- manual_mode_entity: entity selector (input_boolean)
- content_type_override: entity selector (input_select)

Logic:
1. Monitor media_player state changes
2. When playing starts:
   - Detect content type from metadata
   - Apply corresponding settings
   - Set soundbar preset
3. When paused for > X minutes:
   - Partially restore lights
4. When stopped:
   - Restore original settings

Include learning mode to improve detection accuracy.
```

### Blueprint Prompt 38: Doorbell Media Interruption Handler

```
Create a doorbell interruption handler blueprint:

Required inputs:
- doorbell_sensor: entity selector (binary_sensor)
- camera_entity: entity selector (camera)
- media_players: target selector (media_player)

Display options:
- display_method: selector (tv_overlay, chromecast, dashboard, notification_only)
- display_entity: entity selector (media_player) - for TV
- display_duration: number (seconds, 10-60, default 15)

Audio handling:
- pause_audio: boolean (default true)
- duck_audio: boolean (default false)
- duck_volume: number (1-100, default 20)
- announcement_volume: number (1-100, default 50)

TTS inputs:
- enable_tts: boolean (default true)
- tts_service: text
- tts_message: template text (default "Someone is at the door")

Snapshot inputs:
- take_snapshot: boolean (default true)
- snapshot_path: text

Resume inputs:
- auto_resume: boolean (default true)
- resume_delay: number (seconds, 5-30, default 10)
- resume_if_no_response: boolean (default true)

Two-way communication:
- enable_intercom: boolean (default false)
- intercom_entity: entity selector (camera with 2-way audio)

Logic:
1. Doorbell pressed:
   - Store current media states (playing, position, volume)
   - Take camera snapshot
   - Pause or duck all media
2. Display:
   - Show camera feed on TV/display
   - Play TTS announcement
   - Start display_duration timer
3. After display_duration:
   - Close camera display
   - Wait resume_delay
   - Resume media playback at saved position
4. If intercom used:
   - Extend display duration
   - Do not resume until intercom ends

Handle multiple doorbell presses gracefully.
```

### Blueprint Prompt 39: Music/Speech Priority Queue

```
Create an audio priority queue blueprint:

Required inputs:
- media_players: target selector (media_player)
- tts_service: text

Priority levels:
- critical: 1 (emergency alerts - interrupt everything)
- high: 2 (doorbell, timer complete)
- normal: 3 (routine announcements)
- low: 4 (informational)

Queue inputs:
- max_queue_size: number (5-20, default 10)
- queue_timeout: number (seconds, 60-600, default 300)
- combine_duplicates: boolean (default true)

Speech handling:
- default_priority: number (1-4, default 3)
- speech_volume: number (1-100, default 50)
- speech_rate: number (0.5-2, default 1)

Music handling:
- duck_music: boolean (default true)
- duck_volume: number (1-100, default 20)
- pause_for_critical: boolean (default true)
- resume_music: boolean (default true)
- resume_delay: number (seconds, 1-5, default 2)

Chime inputs:
- pre_announcement_chime: boolean (default false)
- chime_file: text - media file path
- post_announcement_chime: boolean (default false)

Time restrictions:
- quiet_hours_start: time - optional
- quiet_hours_end: time - optional
- quiet_hours_min_priority: number (1-4, default 2)

Room selection:
- announcement_mode: selector (all, occupied, specific)
- occupied_sensor_mapping: object (JSON)
- specific_rooms: target selector - if specific mode

Logic:
1. Announcement request received:
   - Check priority level
   - Add to queue based on priority
   - Check quiet hours restrictions
2. Queue processing:
   - Take highest priority item
   - Determine target rooms
   - Duck/pause music if needed
   - Play pre-chime if enabled
   - Play TTS message
   - Play post-chime if enabled
   - Wait and resume music
3. Process next item in queue
4. Remove expired items

Create announcement script for easy calling.
```

### Blueprint Prompt 40: Retry Framework with Exponential Backoff

```
Create a service call retry framework blueprint:

Required inputs:
- target_service: text (service to call)
- target_entity: entity selector (target of service)

Retry configuration:
- max_retries: number (1-10, default 3)
- initial_delay: number (seconds, 1-30, default 5)
- backoff_multiplier: number (1.5-3, default 2)
- max_delay: number (seconds, 30-300, default 60)

Failure detection:
- success_state: text - expected state after call
- success_attribute: text - optional attribute to check
- verification_delay: number (seconds, 1-10, default 2)
- timeout_seconds: number (5-60, default 30)

Error handling:
- retry_on_unavailable: boolean (default true)
- retry_on_timeout: boolean (default true)
- skip_on_already_state: boolean (default true)

Notification inputs:
- notify_on_failure: boolean (default true)
- notify_on_success_after_retry: boolean (default true)
- notify_service: text
- failure_actions: action selector - optional (run on final failure)

Logging:
- create_logbook_entries: boolean (default true)
- log_all_attempts: boolean (default false)

Jitter:
- enable_jitter: boolean (default true)
- jitter_percent: number (10-50, default 20)

Logic:
1. Attempt service call
2. Wait verification_delay
3. Check if target reached success_state
4. If failed:
   - Calculate next delay with backoff and jitter
   - Wait delay
   - Increment retry counter
   - If retries < max_retries: Goto step 1
   - Else: Execute failure_actions, send notification
5. If succeeded:
   - If retry_count > 0: Send success notification
   - Log outcome

Include retry statistics helper for monitoring.
```

### Blueprint Prompt 41: Automation Health Monitor & Watchdog

```
Create an automation health monitoring blueprint:

Required inputs:
- monitored_automations: entity selector (automation, multiple)
- health_indicator: entity selector (input_select for status)

Monitoring inputs:
- expected_frequency: selector (hourly, daily, weekly, custom)
- custom_frequency: number (hours) - if custom
- max_missed_runs: number (1-10, default 3)

Health states:
- healthy: Running as expected
- warning: Missed 1-2 expected runs
- critical: Missed max_missed_runs
- disabled: Automation turned off
- error: Automation failed

Error detection:
- check_for_errors: boolean (default true)
- error_log_entity: entity selector (sensor) - optional
- error_keywords: text (comma-separated)

Performance tracking:
- track_execution_time: boolean (default true)
- slow_threshold: number (seconds, 5-60, default 10)
- track_trigger_count: boolean (default true)

Alert inputs:
- alert_on_warning: boolean (default true)
- alert_on_critical: boolean (default true)
- alert_service: text
- alert_cooldown: number (hours, 1-24, default 6)

Recovery actions:
- auto_enable_disabled: boolean (default false)
- auto_retry_failed: boolean (default false)
- restart_ha_on_critical: boolean (default false)

Dashboard:
- create_dashboard_sensors: boolean (default true)

Logic:
1. Track each automation's:
   - Last trigger time
   - Trigger count (daily/weekly)
   - Execution duration
   - Success/failure status
2. Calculate expected vs actual runs
3. Update health_indicator based on status
4. Send alerts when thresholds crossed
5. Optionally attempt recovery

Create health summary notification (daily/weekly).
```

### Blueprint Prompt 42: Self-Healing Automation Patterns

```
Create a self-healing automation blueprint:

Required inputs:
- main_automation: entity selector (automation)
- target_entities: entity selector (multiple)

Healing actions:
- healing_strategies: multi-select
  - retry_service_call
  - restart_integration
  - power_cycle_device
  - reload_automation
  - restart_ha_core

Retry strategy inputs:
- retry_delay: number (seconds, 5-60, default 10)
- max_retries: number (1-10, default 3)

Integration restart inputs:
- target_integration: text
- restart_delay: number (seconds, 10-60, default 30)

Power cycle inputs:
- power_switch: entity selector (switch) - smart plug for device
- off_duration: number (seconds, 5-30, default 10)

Detection inputs:
- failure_detection: selector (state_check, error_log, timeout, manual)
- expected_state: text - for state_check
- state_timeout: number (seconds, 10-300, default 60)
- error_pattern: text - for error_log

Escalation:
- escalation_enabled: boolean (default true)
- escalation_order: object (JSON array of strategies)
- final_notification: boolean (default true)
- final_action: action selector - optional

Logging:
- detailed_logging: boolean (default true)
- healing_history_days: number (7-90, default 30)

Safeguards:
- max_healing_attempts_per_day: number (1-20, default 5)
- cooldown_between_attempts: number (minutes, 5-60, default 15)
- disable_after_max_failures: boolean (default true)

Logic:
1. Monitor target_entities for expected behavior
2. Detect failure (state not reached, error in log)
3. Start healing sequence:
   - Try first strategy
   - Wait and verify
   - If still failed: Try next strategy
   - Continue through escalation_order
4. Track healing attempts and outcomes
5. Apply safeguards to prevent infinite loops

Create healing report for analysis.
```

### Blueprint Prompt 43: Graceful Degradation Blueprint

```
Create a graceful degradation blueprint for critical systems:

Required inputs:
- critical_function: text (description of what must work)
- primary_method: action selector
- primary_entities: entity selector (multiple)

Fallback chain:
- fallback_1_method: action selector
- fallback_1_entities: entity selector (multiple)
- fallback_1_description: text
- fallback_2_method: action selector - optional
- fallback_2_entities: entity selector (multiple) - optional
- fallback_3_method: action selector - optional (manual notification)

Detection inputs:
- health_check_interval: number (seconds, 30-300, default 60)
- entity_availability_check: boolean (default true)
- service_test_call: boolean (default false)
- response_timeout: number (seconds, 5-30, default 10)

Degraded mode behavior:
- degraded_mode_entity: entity selector (input_select)
- notify_on_degradation: boolean (default true)
- notification_service: text

Recovery:
- auto_restore_primary: boolean (default true)
- restore_check_interval: number (minutes, 5-60, default 15)
- restore_confirmation_count: number (1-5, default 3)

Example use cases:
- Lighting: Zigbee → WiFi bulbs → Smart plug with lamp
- Climate: Smart thermostat → Smart plug heater → Manual notification
- Security: Cloud alarm → Local alarm → Phone notification

Logic:
1. Regular health check of primary_entities
2. If primary unavailable:
   - Switch to fallback_1
   - Update degraded_mode_entity
   - Send notification
3. If fallback_1 unavailable:
   - Switch to fallback_2
   - Escalate notification
4. Continue through chain
5. When primary recovers:
   - Verify stability (restoration_confirmation_count checks)
   - Switch back to primary
   - Send recovery notification

Track time spent in each degradation level.
```

### Blueprint Prompt 44: ESPHome Device Integration Blueprint

```
Create an ESPHome device integration helper blueprint:

Required inputs:
- esphome_device: device selector (ESPHome device)
- device_type: selector (sensor, binary_sensor, switch, light, climate, cover, fan)

Sensor configuration:
- update_interval: number (seconds, 1-3600, default 60)
- filters_enabled: boolean (default true)
- filter_type: selector (none, sliding_window_moving_average, exponential_moving_average, median)
- filter_window: number (3-20, default 5)

Binary sensor configuration:
- device_class: selector (motion, door, window, smoke, etc.)
- delayed_on: number (milliseconds, 0-10000, default 0)
- delayed_off: number (milliseconds, 0-60000, default 0)
- invert: boolean (default false)

Availability tracking:
- offline_alert_delay: number (minutes, 1-60, default 5)
- notify_on_offline: boolean (default true)
- notify_on_restore: boolean (default true)
- notification_service: text

OTA update handling:
- auto_update: boolean (default false)
- update_window_start: time - optional
- update_window_end: time - optional
- notify_before_update: boolean (default true)

Diagnostics:
- track_wifi_signal: boolean (default true)
- track_uptime: boolean (default true)
- weak_signal_threshold: number (dBm, -90 to -50, default -70)

Automation triggers:
- create_state_trigger: boolean (default true)
- create_event_trigger: boolean (default false)

Logic:
1. Monitor device connectivity
2. Apply sensor filters for stability
3. Track diagnostics (WiFi, uptime)
4. Alert on offline/weak signal
5. Handle OTA updates in maintenance window

Generate YAML for ESPHome device configuration.
```

### Blueprint Prompt 45: MQTT Device Discovery & Control

```
Create an MQTT device management blueprint:

Required inputs:
- mqtt_topic_prefix: text (e.g., "homeassistant")
- device_name: text
- device_type: selector (switch, light, sensor, binary_sensor, climate, cover)

Discovery configuration:
- enable_discovery: boolean (default true)
- discovery_prefix: text (default "homeassistant")
- unique_id_prefix: text

Topic structure:
- state_topic: text (auto-generated or custom)
- command_topic: text (auto-generated or custom)
- availability_topic: text (auto-generated or custom)
- json_attributes_topic: text - optional

Payload configuration:
- payload_on: text (default "ON")
- payload_off: text (default "OFF")
- payload_available: text (default "online")
- payload_not_available: text (default "offline")
- value_template: text - optional

QoS and retain:
- qos: number (0, 1, 2, default 1)
- retain: boolean (default false)

Device info:
- manufacturer: text - optional
- model: text - optional
- sw_version: text - optional

Tasmota specific:
- is_tasmota: boolean (default false)
- tasmota_template: selector (common templates)
- sync_power_state: boolean (default true)

Shelly specific:
- is_shelly: boolean (default false)
- shelly_gen: selector (gen1, gen2, gen3)
- enable_scripts: boolean (default false)

Availability monitoring:
- offline_timeout: number (seconds, 30-600, default 60)
- notify_offline: boolean (default true)

Logic:
1. Generate MQTT discovery payload
2. Publish to discovery topic
3. Subscribe to state updates
4. Handle command publishing
5. Monitor availability
6. Sync with device-specific features (Tasmota/Shelly)

Include MQTT debug mode for troubleshooting.
```

### Blueprint Prompt 46: Tasmota Device Manager

```
Create a Tasmota device management blueprint:

Required inputs:
- device_topic: text (Tasmota topic prefix)
- device_type: selector (switch, dimmer, rgb_light, sensor, plug_with_power)

Power monitoring (for plugs):
- enable_power_monitoring: boolean (default true)
- power_sensor_name: text
- voltage_sensor_name: text
- current_sensor_name: text
- energy_tracking: boolean (default true)

State synchronization:
- sync_on_connect: boolean (default true)
- sync_interval: number (minutes, 0=disabled, default 5)
- use_state_topic: boolean (default true)
- use_result_topic: boolean (default true)

Firmware management:
- auto_update: boolean (default false)
- update_channel: selector (stable, development)
- notify_new_version: boolean (default true)

Telemetry:
- telemetry_period: number (seconds, 10-3600, default 300)
- track_wifi_signal: boolean (default true)
- track_uptime: boolean (default true)

Button configuration:
- button_topic: text - optional
- button_events: multi-select (single, double, triple, hold)
- button_actions: object (JSON mapping event to action)

Rules:
- enable_rules: boolean (default false)
- rule_1: text - optional
- rule_2: text - optional

Timer integration:
- import_timers: boolean (default false)
- sync_timers_to_ha: boolean (default false)

Calibration (for power monitoring):
- power_calibration: number - optional
- voltage_calibration: number - optional
- current_calibration: number - optional

Logic:
1. Connect to device via MQTT
2. Configure telemetry period
3. Set up power monitoring if applicable
4. Handle button events
5. Track firmware version
6. Sync state bidirectionally

Include Tasmota console command sender.
```

### Blueprint Prompt 47: Shelly Device Integration

```
Create a Shelly device integration blueprint:

Required inputs:
- device_ip: text (for local API)
- device_type: selector (1, 1PM, 2.5, Dimmer, Duo, RGBW2, Plus1, Plus2PM, Pro4PM)
- integration_method: selector (cloud, local_polling, local_coiot, mqtt)

Generation handling:
- device_generation: selector (gen1, gen2, gen3)

Channel configuration (multi-channel devices):
- channels_enabled: multi-select (0, 1, 2, 3)
- channel_names: object (JSON mapping channel to name)

Power monitoring:
- enable_power_monitoring: boolean (default true)
- power_sensors_enabled: boolean (default true)
- energy_counters_enabled: boolean (default true)

Input configuration:
- input_mode: selector (momentary, toggle, edge, detached)
- input_actions: object (JSON mapping input events to actions)
- long_press_duration: number (ms, 500-3000, default 800)

Cover mode (for 2.5):
- cover_mode: boolean (default false)
- open_time: number (seconds)
- close_time: number (seconds)
- obstacle_detection: boolean (default true)

Temperature protection:
- overtemp_threshold: number (Celsius, 60-100, default 80)
- overtemp_action: selector (turn_off, reduce_power, notify)

Firmware:
- auto_update: boolean (default false)
- beta_channel: boolean (default false)

Scripts (Gen2+):
- enable_scripts: boolean (default false)
- script_1: text - optional

Schedules:
- import_schedules: boolean (default false)
- sync_schedules_to_ha: boolean (default false)

Local API:
- local_api_enabled: boolean (default true)
- webhook_enabled: boolean (default false)
- webhook_url: text - optional

Logic:
1. Detect device generation and capabilities
2. Configure based on device_type
3. Set up channels/inputs
4. Enable monitoring features
5. Handle firmware updates
6. Sync schedules if enabled

Include device diagnostics dashboard.
```

### Blueprint Prompt 48: Learning Thermostat Blueprint

```
Create a learning thermostat blueprint:

Required inputs:
- climate_entity: entity selector (climate)
- temperature_sensor: entity selector (sensor) - optional external sensor
- learning_data_store: entity selector (input_text for JSON storage)

Learning inputs:
- learning_enabled: boolean (default true)
- learning_period: number (days, 7-30, default 14)
- adjustment_sensitivity: number (0.1-1, default 0.5)

Pattern detection:
- track_occupancy: boolean (default true)
- occupancy_sensor: entity selector (binary_sensor)
- track_manual_changes: boolean (default true)
- track_time_patterns: boolean (default true)

Thermal modeling:
- track_heating_rate: boolean (default true)
- track_cooling_rate: boolean (default true)
- track_outdoor_influence: boolean (default true)
- outdoor_temp_sensor: entity selector (sensor) - optional

Comfort inputs:
- base_comfort_temp: number (18-24, default 21)
- min_temp: number (10-18, default 15)
- max_temp: number (22-28, default 25)
- hysteresis: number (0.1-1, default 0.5)

Schedule adaptation:
- adapt_to_wake_time: boolean (default true)
- wake_time_source: selector (manual, phone_alarm, calendar)
- pre_heat_time: number (minutes, 0-120, default 30)

Away detection:
- auto_away: boolean (default true)
- away_temp_setback: number (degrees, 2-6, default 4)
- away_delay: number (minutes, 15-120, default 30)

Sleep detection:
- auto_sleep: boolean (default true)
- sleep_temp_setback: number (degrees, 1-4, default 2)
- sleep_detection_time: time (default 23:00)

Logic:
1. Collect data during learning_period:
   - Manual temperature changes
   - Occupancy patterns
   - Heating/cooling response times
2. Build schedule from patterns
3. Calculate pre-heat times based on thermal model
4. Adjust setpoints based on outdoor temperature
5. Detect and respond to away/sleep states

Show learning progress and predictions in dashboard.
```

### Blueprint Prompt 49: Multi-Zone Room Priority Climate

```
Create a multi-zone climate priority blueprint:

Required inputs:
- zones: object (JSON array of zone definitions)
  Each: {climate: entity, temp_sensor: entity, priority: 1-10, name: text}

Priority rules:
- conflict_resolution: selector (highest_priority, average, comfort_range)
- priority_boost_duration: number (minutes, 30-120, default 60)
- priority_boost_entity: entity selector (input_boolean) - optional

Occupancy integration:
- zone_occupancy_sensors: object (JSON mapping zone to sensor)
- boost_occupied_priority: boolean (default true)
- occupied_priority_boost: number (1-5, default 2)

Temperature targets:
- default_target: number (18-24, default 21)
- per_zone_targets: object (JSON mapping zone to target)
- target_override: entity selector (input_number) - optional

Comfort range:
- comfort_min: number (18-22, default 20)
- comfort_max: number (21-25, default 23)

Balancing:
- enable_zone_balancing: boolean (default true)
- max_zone_difference: number (degrees, 1-5, default 3)
- balancing_method: selector (damper_control, setpoint_adjustment, fan_boost)

Damper control (if applicable):
- zone_dampers: object (JSON mapping zone to cover entity)

Energy optimization:
- limit_simultaneous_heating: number (zones, 0=unlimited)
- stagger_startup: boolean (default true)
- stagger_delay: number (minutes, 5-30, default 10)

Schedule integration:
- schedule_entity: entity selector (schedule) - optional
- override_schedule_for_priority: boolean (default true)

Logic:
1. Monitor all zones continuously
2. Calculate priority order based on:
   - Static priority
   - Occupancy boost
   - Distance from target
3. For highest priority zone:
   - Set target temperature
   - Open dampers (if applicable)
4. For lower priority zones:
   - Reduce heating if necessary
   - Partially close dampers
5. Balance to keep zones within max_difference

Create zone status dashboard showing priorities and temps.
```

### Blueprint Prompt 50: Predictive Pre-heating/Pre-cooling

```
Create a predictive climate pre-conditioning blueprint:

Required inputs:
- climate_entity: entity selector (climate)
- target_time_source: selector (schedule, calendar, alarm, manual)

Time sources:
- schedule_entity: entity selector (schedule) - if schedule
- calendar_entity: entity selector (calendar) - if calendar
- alarm_entity: entity selector (sensor) - if alarm
- manual_time: time - if manual

Thermal model inputs:
- heating_rate_per_degree: number (minutes, 1-30, default 5)
- cooling_rate_per_degree: number (minutes, 1-60, default 10)
- thermal_mass: selector (low, medium, high)
- building_insulation: selector (poor, average, good, excellent)

Weather compensation:
- outdoor_temp_sensor: entity selector (sensor)
- wind_speed_sensor: entity selector (sensor) - optional
- compensation_factor: number (0-1, default 0.5)

Learning:
- enable_learning: boolean (default true)
- track_actual_times: boolean (default true)
- learning_weight: number (0-1, default 0.3)
- min_data_points: number (5-30, default 10)

Calculation inputs:
- target_temperature: number (18-24, default 21)
- acceptable_variance: number (0.5-2, default 1)
- safety_margin: number (minutes, 0-30, default 5)

Energy awareness:
- price_sensor: entity selector (sensor) - optional
- delay_if_expensive: boolean (default true)
- max_delay: number (minutes, 0-30, default 15)
- expensive_threshold: number

Notification:
- notify_start_time: boolean (default true)
- notify_prediction_accuracy: boolean (default false)
- notification_service: text

Logic:
1. Calculate required temperature change
2. Estimate time needed:
   - Base time from rate per degree
   - Adjust for outdoor temperature
   - Adjust for thermal mass
   - Apply learning corrections
3. Add safety_margin
4. Schedule start time = target_time - estimated_time
5. Optionally delay for energy prices
6. Track actual performance for learning

Create sensor showing predicted vs actual accuracy.
```


---

