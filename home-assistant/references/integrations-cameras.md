# Camera Integrations

Complete guide for integrating IP cameras, NVRs, and surveillance systems with Home Assistant.

---

## Overview

Home Assistant supports numerous camera integrations:

| Integration | Type | Key Features |
|-------------|------|--------------|
| **Reolink** | Native | PTZ, motion, 2-way audio |
| **Synology** | NVR | Surveillance Station |
| **Generic RTSP** | Protocol | Any RTSP camera |
| **Frigate** | NVR | Object detection |
| **ONVIF** | Protocol | Industry standard |

---

## Reolink Integration

### Supported Features

- Live stream (RTSP/RTMP)
- Motion detection events
- PTZ control
- 2-way audio
- Spotlight/siren control
- Recording playback

### Setup

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **Reolink**
3. Enter camera IP address
4. Enter admin credentials
5. Camera entities are created automatically

### Entities Created

```yaml
# camera.reolink_front_door           # Live stream
# binary_sensor.reolink_front_door_motion   # Motion detection
# binary_sensor.reolink_front_door_person   # Person detection
# binary_sensor.reolink_front_door_vehicle  # Vehicle detection
# switch.reolink_front_door_record     # Recording control
# button.reolink_front_door_ptz_*      # PTZ controls
# siren.reolink_front_door            # Siren control
# light.reolink_front_door_floodlight # Spotlight
```

### Motion Detection Automation

```yaml
automation:
  - alias: "Reolink Motion Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.reolink_front_door_motion
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Motion detected at front door"
          data:
            image: /api/camera_proxy/camera.reolink_front_door

# Person-specific detection
automation:
  - alias: "Person at Front Door"
    trigger:
      - platform: state
        entity_id: binary_sensor.reolink_front_door_person
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Person detected at front door"
          data:
            entity_id: camera.reolink_front_door
            actions:
              - action: "UNLOCK_DOOR"
                title: "Unlock Door"
```

### PTZ Control

```yaml
# Move to preset
service: button.press
target:
  entity_id: button.reolink_ptz_preset_1

# PTZ movement
service: camera.ptz
target:
  entity_id: camera.reolink_front_door
data:
  move: "LEFT"  # UP, DOWN, LEFT, RIGHT, ZOOM_IN, ZOOM_OUT
```

### Spotlight Control

```yaml
# Turn on floodlight
service: light.turn_on
target:
  entity_id: light.reolink_front_door_floodlight
data:
  brightness_pct: 100

# Trigger siren
service: siren.turn_on
target:
  entity_id: siren.reolink_front_door
data:
  duration: 10
```

---

## Synology Surveillance Station

### Setup

1. Enable Surveillance Station package on NAS
2. Go to **Settings > Devices & Services**
3. Click **Add Integration** > **Synology DSM**
4. Enter NAS credentials
5. Surveillance cameras appear automatically

### Entities Created

```yaml
# camera.synology_cam_name          # Live stream
# binary_sensor.synology_cam_motion # Motion detection
# switch.synology_cam_home_mode     # Home mode
```

### Motion Automation

```yaml
automation:
  - alias: "Synology Motion Recording"
    trigger:
      - platform: state
        entity_id: binary_sensor.synology_front_cam_motion
        to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.synology_front_cam
        data:
          filename: "/config/www/snapshots/front_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
      - service: notify.mobile_app
        data:
          message: "Motion at front camera"
          data:
            image: /local/snapshots/front_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg
```

### Home Mode Control

```yaml
# Enable home mode (disables recording)
automation:
  - alias: "Synology Home Mode When Home"
    trigger:
      - platform: state
        entity_id: group.family
        to: "home"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.synology_home_mode

# Disable home mode (enables recording)
automation:
  - alias: "Synology Away Mode"
    trigger:
      - platform: state
        entity_id: group.family
        to: "not_home"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.synology_home_mode
```

---

## Generic RTSP Camera

### Configuration

```yaml
# configuration.yaml
camera:
  - platform: generic
    name: Front Door
    still_image_url: http://192.168.1.100/snapshot.jpg
    stream_source: rtsp://user:pass@192.168.1.100:554/stream1
    verify_ssl: false
```

### Common RTSP URLs by Brand

```yaml
# Hikvision
rtsp://user:pass@ip:554/Streaming/Channels/101  # Main stream
rtsp://user:pass@ip:554/Streaming/Channels/102  # Sub stream

# Dahua
rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=0  # Main
rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=1  # Sub

# Amcrest (same as Dahua)
rtsp://user:pass@ip:554/cam/realmonitor?channel=1&subtype=0

# Reolink (if not using native integration)
rtsp://user:pass@ip:554/h264Preview_01_main
rtsp://user:pass@ip:554/h264Preview_01_sub

# Foscam
rtsp://user:pass@ip:88/videoMain
rtsp://user:pass@ip:88/videoSub

# Wyze (with RTSP firmware)
rtsp://user:pass@ip/live

# Tapo
rtsp://user:pass@ip:554/stream1
rtsp://user:pass@ip:554/stream2

# Ubiquiti UniFi
rtsp://ip:7447/camera_id
```

### Multiple Streams

```yaml
# Use sub-stream for dashboard, main for recording
camera:
  - platform: generic
    name: Front Door Sub
    stream_source: rtsp://user:pass@ip:554/stream2

  - platform: generic
    name: Front Door Main
    stream_source: rtsp://user:pass@ip:554/stream1
```

---

## ONVIF Integration

### Setup

1. Go to **Settings > Devices & Services**
2. Click **Add Integration** > **ONVIF**
3. Enter camera IP and credentials
4. Select profile (main/sub stream)

### Features

- Auto-discovery of ONVIF cameras
- PTZ control via ONVIF
- Event subscriptions (motion, etc.)
- Multiple stream profiles

### PTZ Control

```yaml
# ONVIF PTZ service
service: onvif.ptz
target:
  entity_id: camera.onvif_camera
data:
  move_mode: "ContinuousMove"
  pan: 0.5    # -1 to 1
  tilt: 0.0   # -1 to 1
  zoom: 0.0   # -1 to 1

# Stop PTZ
service: onvif.ptz
target:
  entity_id: camera.onvif_camera
data:
  move_mode: "Stop"
```

---

## Camera Automations

### Snapshot on Motion

```yaml
automation:
  - alias: "Motion Snapshot"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_motion
        to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/snapshots/motion_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

### Notification with Camera Image

```yaml
automation:
  - alias: "Doorbell Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell_press
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Doorbell"
          message: "Someone at the door"
          data:
            entity_id: camera.front_door
            # Or use image URL:
            # image: /api/camera_proxy/camera.front_door
            actions:
              - action: "OPEN_GATE"
                title: "Open Gate"
              - action: "IGNORE"
                title: "Ignore"
```

### Recording on Event

```yaml
# Record video clip on motion
automation:
  - alias: "Record on Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_motion
        to: "on"
    action:
      - service: camera.record
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/recordings/motion_{{ now().strftime('%Y%m%d_%H%M%S') }}.mp4"
          duration: 30
          lookback: 5  # Include 5 seconds before trigger
```

### Night Vision Mode

```yaml
# Some cameras support IR control
automation:
  - alias: "Enable Night Vision"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.front_door_ir_lights
```

---

## Dashboard Integration

### Picture Glance Card

```yaml
type: picture-glance
title: Front Door
camera_image: camera.front_door
camera_view: live
entities:
  - binary_sensor.front_door_motion
  - binary_sensor.front_door_person
  - switch.front_door_record
```

### Conditional Camera Display

```yaml
type: conditional
conditions:
  - entity: binary_sensor.front_door_motion
    state: "on"
card:
  type: picture-entity
  entity: camera.front_door
  camera_view: live
```

### Grid of Cameras

```yaml
type: grid
columns: 2
cards:
  - type: picture-entity
    entity: camera.front_door
    camera_view: auto
  - type: picture-entity
    entity: camera.backyard
    camera_view: auto
  - type: picture-entity
    entity: camera.garage
    camera_view: auto
  - type: picture-entity
    entity: camera.driveway
    camera_view: auto
```

---

## Integration with Frigate

### Using Cameras with Frigate

See [integrations-frigate.md](integrations-frigate.md) for full Frigate setup.

```yaml
# Configure camera for Frigate
# frigate.yaml
cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://user:pass@192.168.1.100:554/stream1
          roles:
            - detect
            - record
    detect:
      enabled: true
```

### Frigate Camera in HA

```yaml
# Frigate creates camera entities automatically
# camera.front_door  # Live view
# camera.front_door_person  # Last detected person
# binary_sensor.front_door_person  # Person detected
```

---

## Performance Optimization

### Stream vs Snapshot

```yaml
# Use snapshot for static views (less bandwidth)
camera:
  - platform: generic
    name: Garage Static
    still_image_url: http://192.168.1.101/snapshot.jpg
    # No stream_source = snapshot only

# Use stream for live views
camera:
  - platform: generic
    name: Front Door Live
    stream_source: rtsp://user:pass@192.168.1.100/stream1
```

### Resolution Settings

```yaml
# Use sub-stream for dashboard viewing
# Use main-stream for recording

# Sub-stream typically:
# - 640x480 or 1280x720
# - Lower bitrate
# - Less CPU/bandwidth

# Main-stream typically:
# - 1920x1080 or 4K
# - Higher bitrate
# - Better for recording
```

### Hardware Acceleration

```yaml
# Enable hardware decoding (if available)
# Requires FFmpeg with VA-API or NVIDIA support

# In Home Assistant OS, hardware acceleration
# is enabled automatically when supported
```

---

## Troubleshooting

### Stream Not Loading

1. **Verify RTSP URL** - test with VLC player
2. **Check credentials** - URL-encode special characters
3. **Verify port** - default RTSP is 554
4. **Check firewall** - allow RTSP traffic

### High CPU Usage

```yaml
# Use sub-stream instead of main
# Reduce frame rate if possible
# Enable hardware acceleration
# Use Frigate for efficient processing
```

### Snapshot Delays

```yaml
# Increase timeout
camera:
  - platform: generic
    name: Slow Camera
    still_image_url: http://192.168.1.100/snapshot.jpg
    timeout: 15  # seconds
```

### Authentication Issues

```yaml
# URL-encode special characters in password
# Example: pass@word becomes pass%40word

# Some cameras need digest auth
camera:
  - platform: generic
    name: Camera
    authentication: digest  # or basic
    username: admin
    password: "your_password"
```

---

## Security Best Practices

### Network Isolation

```yaml
# 1. Put cameras on separate VLAN
# 2. Block camera internet access
# 3. Only allow HA to communicate with cameras
# 4. Use VPN for remote access
```

### Credentials

```yaml
# 1. Change default passwords
# 2. Create separate HA user on camera
# 3. Use secrets.yaml for credentials
# 4. Don't expose RTSP to internet
```

### Firmware

```yaml
# 1. Keep camera firmware updated
# 2. Check for security patches
# 3. Disable unnecessary services (Telnet, FTP)
```

---

## Reference

### Useful Links

- [Reolink Integration](https://www.home-assistant.io/integrations/reolink/)
- [Generic Camera](https://www.home-assistant.io/integrations/generic/)
- [ONVIF Integration](https://www.home-assistant.io/integrations/onvif/)
- [Stream Component](https://www.home-assistant.io/integrations/stream/)
- [FFmpeg](https://www.home-assistant.io/integrations/ffmpeg/)

### Common Camera Ports

| Protocol | Port | Description |
|----------|------|-------------|
| RTSP | 554 | Real-Time Streaming |
| HTTP | 80 | Web interface |
| HTTPS | 443 | Secure web |
| ONVIF | 80/8080 | ONVIF protocol |
| RTMP | 1935 | Flash streaming |
