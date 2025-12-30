# Media Player Integrations

Complete guide for integrating smart TVs, streaming devices, and media servers with Home Assistant.

---

## Overview

Home Assistant supports numerous media player integrations:

| Integration | Installs | Key Features |
|-------------|----------|--------------|
| **Samsung Smart TV** | 76K | Tizen OS, Wake-on-LAN |
| **LG webOS TV** | 55K | WebSocket, Magic Remote |
| **Android TV** | 90K | ADB, app control |
| **Apple TV** | 69K | PyATV protocol |
| **Plex** | - | Media library triggers |
| **Sonos** | 71K | Multi-room audio |

---

## Samsung Smart TV

### Setup

Samsung TVs (2016+) are discovered automatically. Manual setup:

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Samsung Smart TV**
3. Enter TV IP address
4. Accept pairing prompt on TV

### Configuration

```yaml
# No YAML needed - UI configured

# Enable Wake-on-LAN for remote power on
# In TV Settings > General > Network > Expert Settings
# Enable "Power on with Mobile"
```

### Entities Created

```yaml
# media_player.samsung_tv
# - State: on, off, playing, paused, idle
# - Attributes: source, volume_level, media_title

# remote.samsung_tv
# - Send remote commands
```

### Common Automations

```yaml
# Turn off TV at night
automation:
  - alias: "TV Auto-Off"
    trigger:
      - platform: time
        at: "01:00:00"
    condition:
      - condition: state
        entity_id: media_player.samsung_tv
        state: "on"
    action:
      - service: media_player.turn_off
        target:
          entity_id: media_player.samsung_tv

# Wake TV with Wake-on-LAN
automation:
  - alias: "Turn on TV"
    trigger:
      - platform: state
        entity_id: input_boolean.watch_tv
        to: "on"
    action:
      - service: wake_on_lan.send_magic_packet
        data:
          mac: "AA:BB:CC:DD:EE:FF"
      - delay: "00:00:10"
      - service: media_player.select_source
        target:
          entity_id: media_player.samsung_tv
        data:
          source: "HDMI1"
```

### Source Selection

```yaml
# Change input source
service: media_player.select_source
target:
  entity_id: media_player.samsung_tv
data:
  source: "HDMI1"  # HDMI1, HDMI2, TV, USB, etc.

# Launch app (Samsung TV Plus, Netflix, etc.)
service: media_player.select_source
target:
  entity_id: media_player.samsung_tv
data:
  source: "Netflix"
```

### Remote Commands

```yaml
# Send remote key
service: remote.send_command
target:
  entity_id: remote.samsung_tv
data:
  command: KEY_POWER  # KEY_HOME, KEY_MENU, KEY_UP, etc.

# Common keys:
# KEY_POWER, KEY_HOME, KEY_MENU, KEY_RETURN
# KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_ENTER
# KEY_VOLUMEUP, KEY_VOLUMEDOWN, KEY_MUTE
# KEY_CHUP, KEY_CHDOWN
# KEY_1 through KEY_9, KEY_0
```

---

## LG webOS TV

### Setup

1. Enable **LG Connect Apps** on TV
2. Go to **Settings > Devices & Services**
3. Click **Add Integration** > **LG webOS Smart TV**
4. Enter TV IP address or let discovery find it
5. Accept pairing prompt on TV

### Configuration

```yaml
# Optional: Wake-on-LAN
wake_on_lan:

# Store pairing key for reconnection
# Automatic after first pairing
```

### Entities Created

```yaml
# media_player.lg_tv
# - Full media player controls
# - Source/app selection

# Sensors (optional):
# sensor.lg_tv_current_app
# sensor.lg_tv_current_channel
```

### Magic Remote Events

```yaml
# LG TVs send button events
automation:
  - alias: "Magic Remote Button"
    trigger:
      - platform: event
        event_type: webostv.button
        event_data:
          entity_id: media_player.lg_tv
          button: BACK
    action:
      - service: light.toggle
        target:
          entity_id: light.living_room
```

### App Control

```yaml
# Launch specific app
service: media_player.select_source
target:
  entity_id: media_player.lg_tv
data:
  source: "Netflix"

# Available sources depend on installed apps
# Common: Netflix, YouTube, Amazon Prime Video, Disney+, Plex
```

### Channel Control

```yaml
# Change channel (for TV input)
service: webostv.select_channel
target:
  entity_id: media_player.lg_tv
data:
  channel: "5.1"  # Channel number

# Or by channel name (if available)
service: webostv.select_channel
target:
  entity_id: media_player.lg_tv
data:
  channel: "BBC One"
```

### Commands

```yaml
# Send command
service: webostv.command
target:
  entity_id: media_player.lg_tv
data:
  command: "system.launcher/launch"
  payload:
    id: "netflix"

# Turn on with Wake-on-LAN
service: wake_on_lan.send_magic_packet
data:
  mac: "AA:BB:CC:DD:EE:FF"
```

---

## Android TV / Fire TV

### Setup Methods

#### Method 1: Android TV Remote (Recommended for Android TV)

1. Enable Developer Options on TV
2. Go to **Settings > Devices & Services**
3. Click **Add Integration** > **Android TV Remote**
4. Enter TV IP address
5. Accept pairing prompt on TV

#### Method 2: Android Debug Bridge (ADB)

```yaml
# For advanced control and older devices
# Requires ADB debugging enabled on device

# configuration.yaml
media_player:
  - platform: androidtv
    name: Living Room TV
    host: 192.168.1.100
    adb_server_ip: 127.0.0.1  # Optional: external ADB server
```

### Entities Created

```yaml
# media_player.android_tv
# remote.android_tv (for Android TV Remote integration)
```

### App Control

```yaml
# Launch app by package name
service: media_player.select_source
target:
  entity_id: media_player.android_tv
data:
  source: "com.netflix.ninja"  # Netflix

# Common app package names:
# Netflix: com.netflix.ninja
# YouTube: com.google.android.youtube.tv
# Plex: com.plexapp.android
# Disney+: com.disney.disneyplus
# Prime Video: com.amazon.amazonvideo.livingroom
# Kodi: org.xbmc.kodi
```

### ADB Commands

```yaml
# Send ADB command
service: androidtv.adb_command
target:
  entity_id: media_player.android_tv
data:
  command: "input keyevent 26"  # Power key

# Common key codes:
# 3 = Home, 4 = Back, 19-22 = D-pad
# 23 = Select, 24/25 = Volume Up/Down
# 26 = Power, 82 = Menu
# 164 = Mute, 176 = Settings
```

### Remote Commands

```yaml
# Using Android TV Remote integration
service: remote.send_command
target:
  entity_id: remote.android_tv
data:
  command: HOME  # BACK, MENU, SELECT, etc.

# Navigation
service: remote.send_command
target:
  entity_id: remote.android_tv
data:
  command: DPAD_UP  # DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT
```

---

## Apple TV

### Setup

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Apple TV**
3. Apple TV is discovered automatically
4. Enter PIN shown on TV
5. Choose services (AirPlay, Companion)

### Entities Created

```yaml
# media_player.apple_tv
# remote.apple_tv
```

### Media Control

```yaml
# Standard media player controls
service: media_player.play_media
target:
  entity_id: media_player.apple_tv
data:
  media_content_type: "app"
  media_content_id: "com.netflix.Netflix"  # Bundle ID
```

### Remote Commands

```yaml
# Send remote command
service: remote.send_command
target:
  entity_id: remote.apple_tv
data:
  command: "home"  # menu, top_menu, select, up, down, left, right
```

### App Launch

```yaml
# Launch app by bundle ID
service: remote.send_command
target:
  entity_id: remote.apple_tv
data:
  command: "launch_app=com.netflix.Netflix"

# Common bundle IDs:
# Netflix: com.netflix.Netflix
# YouTube: com.google.ios.youtube
# Disney+: com.disney.disneyplus
# Plex: com.plexapp.plex
```

---

## Plex Integration

### Setup

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Plex**
3. Sign in with Plex account
4. Authorize Home Assistant

### Entities Created

```yaml
# media_player.plex_<server_name>
# One entity per active Plex client
```

### Automations

```yaml
# Dim lights when Plex starts playing
automation:
  - alias: "Plex Movie Mode"
    trigger:
      - platform: state
        entity_id: media_player.plex_living_room_tv
        to: "playing"
        attribute: media_content_type
    condition:
      - condition: template
        value_template: "{{ state_attr('media_player.plex_living_room_tv', 'media_content_type') == 'movie' }}"
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.movie_mode

# Recently added notification
automation:
  - alias: "New Plex Content"
    trigger:
      - platform: event
        event_type: plex_new_media
    action:
      - service: notify.mobile_app
        data:
          message: "New on Plex: {{ trigger.event.data.title }}"
```

### Plex Webhooks

For more responsive automations, use Plex webhooks:

1. In Plex, go to **Settings > Webhooks**
2. Add webhook URL: `http://your-ha:8123/api/webhook/plex`
3. Create automation:

```yaml
automation:
  - alias: "Plex Webhook Handler"
    trigger:
      - platform: webhook
        webhook_id: plex
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.json.event == 'media.play' }}"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: light.living_room
```

---

## Media Automations

### Movie Night Scene

```yaml
automation:
  - alias: "Movie Night"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        to: "playing"
    condition:
      - condition: time
        after: "18:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.bias_lighting
        data:
          brightness_pct: 20
          color_temp_kelvin: 2700
      - service: light.turn_off
        target:
          entity_id: light.ceiling_light
      - service: cover.close_cover
        target:
          entity_id: cover.living_room_blinds
```

### Pause on Motion

```yaml
automation:
  - alias: "Pause TV on Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    condition:
      - condition: state
        entity_id: media_player.living_room_tv
        state: "playing"
    action:
      - service: media_player.media_pause
        target:
          entity_id: media_player.living_room_tv
      - service: notify.tv_notification
        data:
          message: "Someone at the door!"
```

### Ambient Lighting Sync

```yaml
# Sync lights with media
automation:
  - alias: "TV Ambient Sync"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: media_player.living_room_tv
                state: "playing"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.tv_backlight
                data:
                  brightness_pct: 30
                  rgb_color: [255, 180, 100]
          - conditions:
              - condition: state
                entity_id: media_player.living_room_tv
                state: "paused"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.tv_backlight
                data:
                  brightness_pct: 50
          - conditions:
              - condition: state
                entity_id: media_player.living_room_tv
                state: "off"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: light.tv_backlight
```

### Volume Normalization

```yaml
# Limit volume after certain time
automation:
  - alias: "Night Volume Limit"
    trigger:
      - platform: numeric_state
        entity_id: media_player.living_room_tv
        attribute: volume_level
        above: 0.3
    condition:
      - condition: time
        after: "22:00:00"
        before: "08:00:00"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.living_room_tv
        data:
          volume_level: 0.3
      - service: notify.mobile_app
        data:
          message: "Volume limited to 30% (night mode)"
```

---

## Troubleshooting

### TV Not Responding

1. **Check network connectivity** - ping TV IP
2. **Verify TV is on same network** as Home Assistant
3. **Restart TV** - sometimes needed after HA updates
4. **Re-pair** - remove and re-add integration

### Wake-on-LAN Not Working

```yaml
# Ensure WoL is enabled on TV
# Verify MAC address is correct
# TV may need to be in specific standby mode

# Test manually:
service: wake_on_lan.send_magic_packet
data:
  mac: "AA:BB:CC:DD:EE:FF"
  broadcast_address: "192.168.1.255"
```

### ADB Connection Issues

```yaml
# Ensure ADB debugging is enabled on device
# Check if ADB server is running (if using external)
# Try reconnecting:
service: androidtv.adb_command
target:
  entity_id: media_player.android_tv
data:
  command: "reconnect"
```

---

## Reference

### Useful Links

- [Samsung TV Integration](https://www.home-assistant.io/integrations/samsungtv/)
- [LG webOS Integration](https://www.home-assistant.io/integrations/webostv/)
- [Android TV Integration](https://www.home-assistant.io/integrations/androidtv/)
- [Apple TV Integration](https://www.home-assistant.io/integrations/apple_tv/)
- [Plex Integration](https://www.home-assistant.io/integrations/plex/)

### Media Player States

| State | Description |
|-------|-------------|
| `on` | Powered on |
| `off` | Powered off or standby |
| `playing` | Media playing |
| `paused` | Media paused |
| `idle` | On but no media |
| `unavailable` | Connection lost |
