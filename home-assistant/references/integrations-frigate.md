# Frigate NVR Integration Reference

> Object detection, camera management, and video recording with Frigate for Home Assistant 2024/2025

## Overview

Frigate is a complete local NVR solution with AI-powered object detection. It integrates seamlessly with Home Assistant for powerful camera automation without cloud dependencies.

### Key Features

- **Real-time Object Detection** - Person, car, animal, and custom object detection
- **Hardware Acceleration** - Coral TPU, NVIDIA GPU, Intel QSV support
- **24/7 Recording** - Continuous or motion-triggered recording
- **Zone-Based Detection** - Define areas for focused monitoring
- **MQTT Integration** - Real-time events to Home Assistant
- **Low Latency Streaming** - WebRTC and MSE support

---

## Installation

### Docker Installation

```yaml
# docker-compose.yml
version: "3.9"
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:stable
    restart: unless-stopped
    privileged: true  # Required for USB devices
    shm_size: "256mb"  # Increase for more cameras
    devices:
      - /dev/bus/usb:/dev/bus/usb  # Coral USB
      # - /dev/apex_0:/dev/apex_0  # Coral PCIe
      # - /dev/dri/renderD128:/dev/dri/renderD128  # Intel GPU
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /path/to/config:/config
      - /path/to/media:/media/frigate
    ports:
      - "5000:5000"  # Web UI
      - "8554:8554"  # RTSP
      - "8555:8555/tcp"  # WebRTC
      - "8555:8555/udp"  # WebRTC
    environment:
      FRIGATE_RTSP_PASSWORD: "your_password"
```

### Home Assistant Add-on

```yaml
# Via Home Assistant Add-on Store:
# Settings → Add-ons → Add-on Store → Frigate

# Add-on configuration
# Configuration tab in add-on
frigate:
  # Configuration is managed via frigate.yml
  # in your config directory
```

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores | 6+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Storage** | 128 GB SSD | 1+ TB HDD for recordings |
| **Coral TPU** | Optional | Highly recommended |
| **GPU** | Optional | NVIDIA/Intel for decoding |

### Coral TPU Options

```yaml
# USB Coral (easiest)
# Just plug in and pass /dev/bus/usb to container

# PCIe/M.2 Coral (fastest)
# Requires driver installation on host
# Pass /dev/apex_0 to container

# Multiple Corals
detectors:
  coral1:
    type: edgetpu
    device: usb:0
  coral2:
    type: edgetpu
    device: usb:1
```

---

## Basic Configuration

### Minimal Configuration

```yaml
# frigate.yml
mqtt:
  enabled: true
  host: 192.168.1.100  # Home Assistant IP or MQTT broker
  user: mqtt_user
  password: mqtt_password

detectors:
  coral:
    type: edgetpu
    device: usb

cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://user:pass@192.168.1.50:554/stream1
          roles:
            - detect
            - record
    detect:
      enabled: true
      width: 1280
      height: 720
      fps: 5
```

### Full Configuration Example

```yaml
# frigate.yml
mqtt:
  enabled: true
  host: 192.168.1.100
  port: 1883
  user: frigate
  password: !secret mqtt_password
  topic_prefix: frigate
  client_id: frigate

database:
  path: /config/frigate.db

detectors:
  coral:
    type: edgetpu
    device: usb

# Global object settings
objects:
  track:
    - person
    - car
    - dog
    - cat
  filters:
    person:
      min_area: 5000
      max_area: 100000
      min_score: 0.5
      threshold: 0.7

# Recording configuration
record:
  enabled: true
  retain:
    days: 7
    mode: motion
  events:
    retain:
      default: 14
      mode: active_objects

# Snapshot configuration
snapshots:
  enabled: true
  timestamp: true
  bounding_box: true
  retain:
    default: 14

# Live view settings
live:
  stream_name: camera_name
  quality: 8

# Go2RTC for WebRTC streaming
go2rtc:
  streams:
    front_door:
      - rtsp://user:pass@192.168.1.50:554/stream1
    front_door_sub:
      - rtsp://user:pass@192.168.1.50:554/stream2

cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/front_door
          input_args: preset-rtsp-restream
          roles:
            - detect
        - path: rtsp://127.0.0.1:8554/front_door
          input_args: preset-rtsp-restream
          roles:
            - record
    detect:
      enabled: true
      width: 1280
      height: 720
      fps: 5
    motion:
      threshold: 25
      contour_area: 100
    objects:
      track:
        - person
        - car
        - dog
      filters:
        person:
          min_area: 2000
          threshold: 0.75
    zones:
      front_yard:
        coordinates: 0,500,640,500,640,720,0,720
        objects:
          - person
          - car
      driveway:
        coordinates: 640,500,1280,500,1280,720,640,720
        objects:
          - car
    record:
      enabled: true
      retain:
        days: 7
    snapshots:
      enabled: true
```

---

## Camera Configuration

### RTSP Stream Setup

```yaml
# Common camera RTSP URLs

# Hikvision
path: rtsp://user:pass@192.168.1.50:554/Streaming/Channels/101

# Dahua
path: rtsp://user:pass@192.168.1.50:554/cam/realmonitor?channel=1&subtype=0

# Reolink
path: rtsp://user:pass@192.168.1.50:554/h264Preview_01_main

# Amcrest
path: rtsp://user:pass@192.168.1.50:554/cam/realmonitor?channel=1&subtype=0

# Ubiquiti UniFi
path: rtsp://192.168.1.50:7447/camera_id

# Generic ONVIF
path: rtsp://user:pass@192.168.1.50:554/onvif1
```

### Dual Stream Configuration

Use substream for detection (lower resolution, less CPU):

```yaml
cameras:
  front_door:
    ffmpeg:
      inputs:
        # Substream for detection (efficient)
        - path: rtsp://user:pass@192.168.1.50:554/stream2
          roles:
            - detect
        # Main stream for recording (high quality)
        - path: rtsp://user:pass@192.168.1.50:554/stream1
          roles:
            - record
    detect:
      width: 640   # Match substream resolution
      height: 480
      fps: 5
```

### Hardware Acceleration

```yaml
# Intel Quick Sync (QSV)
ffmpeg:
  hwaccel_args: preset-vaapi

# NVIDIA GPU
ffmpeg:
  hwaccel_args: preset-nvidia-h264

# Raspberry Pi 4 (V4L2)
ffmpeg:
  hwaccel_args: preset-rpi-64-h264

# Custom hwaccel args
ffmpeg:
  hwaccel_args:
    - -hwaccel
    - vaapi
    - -hwaccel_device
    - /dev/dri/renderD128
    - -hwaccel_output_format
    - yuv420p
```

### Motion Detection Tuning

```yaml
cameras:
  front_door:
    motion:
      # Sensitivity (lower = more sensitive)
      threshold: 25

      # Minimum motion area in pixels
      contour_area: 100

      # Motion mask (exclude areas)
      mask:
        - 0,0,200,0,200,200,0,200  # Top-left corner

      # Improve night detection
      improve_contrast: true

      # Lightning/headlight filter
      lightning_threshold: 0.8
```

---

## Object Detection

### Supported Objects

```yaml
# Default COCO model objects
objects:
  track:
    - person
    - bicycle
    - car
    - motorcycle
    - bus
    - truck
    - bird
    - cat
    - dog
    - horse
    - sheep
    - cow
    - bear
```

### Object Filters

```yaml
cameras:
  front_door:
    objects:
      track:
        - person
        - car
        - dog
      filters:
        person:
          # Minimum detection confidence
          min_score: 0.5

          # Tracking threshold (higher = fewer false positives)
          threshold: 0.7

          # Size filters (in pixels)
          min_area: 5000
          max_area: 100000

          # Aspect ratio (height/width)
          min_ratio: 0.5
          max_ratio: 2.0

        car:
          min_score: 0.6
          threshold: 0.8
          min_area: 10000

        dog:
          min_score: 0.5
          threshold: 0.7
          min_area: 2000
```

### Detection Zones

```yaml
cameras:
  front_door:
    zones:
      # Define polygon coordinates
      # Format: x1,y1,x2,y2,x3,y3,...
      front_porch:
        coordinates: 100,400,500,400,500,720,100,720
        objects:
          - person
        filters:
          person:
            min_area: 3000

      driveway:
        coordinates: 500,400,1280,400,1280,720,500,720
        objects:
          - person
          - car
        # Only trigger when object is in zone
        inertia: 3  # Frames before entering/leaving

      # Use Frigate UI to draw zones visually
      # Access at http://frigate:5000
```

### Detection Masks

Exclude areas from detection (trees, flags, etc.):

```yaml
cameras:
  front_door:
    motion:
      mask:
        # Polygon mask
        - 0,0,100,0,100,100,0,100

    objects:
      mask:
        # Object-specific mask
        - 500,0,600,0,600,100,500,100
```

---

## Home Assistant Integration

### MQTT Configuration

```yaml
# configuration.yaml
mqtt:
  broker: 192.168.1.100
  port: 1883
  username: !secret mqtt_user
  password: !secret mqtt_password

# Frigate integration handles the rest automatically
```

### Frigate Integration Setup

```yaml
# Via HACS or built-in integration
# Settings → Devices & Services → Add Integration → Frigate

# Integration creates:
# - Camera entities
# - Binary sensors (motion, person, car, etc.)
# - Sensor entities (detection counts)
# - Switch entities (detection toggles)
```

### Entities Created

```yaml
# Per camera entities:
camera.front_door                          # Live stream
binary_sensor.front_door_motion            # Motion detection
binary_sensor.front_door_person            # Person detected
binary_sensor.front_door_car               # Car detected
sensor.front_door_person_count             # Person count
switch.front_door_detect                   # Toggle detection
switch.front_door_snapshots                # Toggle snapshots
switch.front_door_recordings               # Toggle recording

# Per zone entities:
binary_sensor.front_door_front_porch_person
binary_sensor.front_door_driveway_car
```

### Event Handling

```yaml
# Frigate events via MQTT
# Topic: frigate/events

# Event structure:
# {
#   "type": "new",  # new, update, end
#   "before": {...},
#   "after": {
#     "id": "1234567.890-abc123",
#     "camera": "front_door",
#     "frame_time": 1234567.890,
#     "label": "person",
#     "score": 0.85,
#     "box": [100, 200, 300, 400],
#     "area": 20000,
#     "region": [0, 0, 640, 480],
#     "current_zones": ["front_porch"],
#     "entered_zones": ["front_porch"],
#     "has_snapshot": true,
#     "has_clip": true
#   }
# }
```

---

## Automations

### Person Detected Notification

```yaml
automation:
  - id: frigate_person_notification
    alias: "Frigate - Person Detection Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_person
        to: "on"
    condition:
      - condition: state
        entity_id: input_boolean.security_alerts
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Person Detected"
          message: "Person detected at front door"
          data:
            image: "http://frigate:5000/api/front_door/latest.jpg"
            actions:
              - action: "VIEW_CLIP"
                title: "View Clip"
                uri: "http://frigate:5000"

# With snapshot attachment
automation:
  - id: frigate_person_snapshot
    alias: "Frigate - Person Snapshot Notification"
    trigger:
      - platform: mqtt
        topic: frigate/events
    condition:
      - condition: template
        value_template: >
          {{ trigger.payload_json.type == 'end' and
             trigger.payload_json.after.label == 'person' and
             trigger.payload_json.after.has_snapshot }}
    action:
      - service: notify.mobile_app
        data:
          title: "Person Detected - {{ trigger.payload_json.after.camera }}"
          message: >
            Person detected for {{ (trigger.payload_json.after.end_time -
            trigger.payload_json.after.start_time) | round(0) }} seconds
          data:
            image: >
              http://frigate:5000/api/events/{{ trigger.payload_json.after.id }}/snapshot.jpg
```

### Zone-Based Alerts

```yaml
automation:
  - id: frigate_driveway_car
    alias: "Frigate - Car in Driveway"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_driveway_car
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Car Detected"
          message: "Car detected in driveway"

# Person at front porch
automation:
  - id: frigate_porch_person
    alias: "Frigate - Person at Porch"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_front_porch_person
        to: "on"
    condition:
      # Only when nobody home
      - condition: state
        entity_id: group.family
        state: "not_home"
    action:
      - service: notify.mobile_app
        data:
          title: "Visitor Alert"
          message: "Someone at the front porch"
          data:
            image: "http://frigate:5000/api/front_door/latest.jpg"
```

### Recording Management

```yaml
# Enable/disable recording based on presence
automation:
  - id: frigate_recording_away
    alias: "Frigate - Enable Recording When Away"
    trigger:
      - platform: state
        entity_id: group.family
        to: "not_home"
    action:
      - service: switch.turn_on
        target:
          entity_id:
            - switch.front_door_recordings
            - switch.back_door_recordings

  - id: frigate_recording_home
    alias: "Frigate - Disable Recording When Home"
    trigger:
      - platform: state
        entity_id: group.family
        to: "home"
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.front_door_recordings
            - switch.back_door_recordings
```

### Doorbell Integration

```yaml
automation:
  - id: frigate_doorbell_ring
    alias: "Frigate - Doorbell Person Detection"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell_person
        to: "on"
    action:
      # Show camera on smart display
      - service: media_player.play_media
        target:
          entity_id: media_player.kitchen_display
        data:
          media_content_type: image
          media_content_id: "http://frigate:5000/api/doorbell/latest.jpg"

      # Announce visitor
      - service: tts.speak
        target:
          entity_id: tts.piper
        data:
          media_player_entity_id: media_player.kitchen_speaker
          message: "Someone is at the front door"

      # Send notification
      - service: notify.mobile_app
        data:
          title: "Doorbell"
          message: "Someone at the front door"
          data:
            image: "http://frigate:5000/api/doorbell/latest.jpg"
            actions:
              - action: "UNLOCK_DOOR"
                title: "Unlock Door"
```

### Event-Based Clip Download

```yaml
# Save clips to local storage
automation:
  - id: frigate_save_clip
    alias: "Frigate - Save Important Clips"
    trigger:
      - platform: mqtt
        topic: frigate/events
    condition:
      - condition: template
        value_template: >
          {{ trigger.payload_json.type == 'end' and
             trigger.payload_json.after.has_clip and
             trigger.payload_json.after.label == 'person' and
             trigger.payload_json.after.camera in ['front_door', 'back_door'] }}
    action:
      - service: downloader.download_file
        data:
          url: >
            http://frigate:5000/api/events/{{ trigger.payload_json.after.id }}/clip.mp4
          filename: >
            frigate_{{ trigger.payload_json.after.camera }}_{{ now().strftime('%Y%m%d_%H%M%S') }}.mp4
```

---

## Dashboard Integration

### Camera Card

```yaml
type: picture-glance
title: Front Door
camera_image: camera.front_door
camera_view: live
entities:
  - binary_sensor.front_door_person
  - binary_sensor.front_door_car
  - binary_sensor.front_door_motion
tap_action:
  action: more-info
hold_action:
  action: call-service
  service: browser_mod.popup
  service_data:
    content:
      type: custom:frigate-card
      cameras:
        - camera_entity: camera.front_door
```

### Frigate Card (HACS)

```yaml
# Install via HACS: Frigate Card
type: custom:frigate-card
cameras:
  - camera_entity: camera.front_door
    live_provider: ha
    frigate:
      url: http://frigate:5000
      camera_name: front_door

menu:
  buttons:
    frigate:
      enabled: true
    fullscreen:
      enabled: true
    timeline:
      enabled: true

live:
  preload: true
  auto_unmute: false

timeline:
  show_recordings: true
  window_seconds: 3600
```

### Multi-Camera Grid

```yaml
type: custom:frigate-card
cameras:
  - camera_entity: camera.front_door
    frigate:
      camera_name: front_door
  - camera_entity: camera.back_door
    frigate:
      camera_name: back_door
  - camera_entity: camera.garage
    frigate:
      camera_name: garage
  - camera_entity: camera.driveway
    frigate:
      camera_name: driveway

view:
  default: live
  camera_select: current

dimensions:
  aspect_ratio_mode: dynamic

live:
  controls:
    builtin: true

performance:
  profile: low
```

---

## Performance Tuning

### CPU Optimization

```yaml
# Reduce detection FPS
cameras:
  front_door:
    detect:
      fps: 5  # Lower for less CPU

# Use substream for detection
cameras:
  front_door:
    ffmpeg:
      inputs:
        - path: rtsp://camera/substream
          roles:
            - detect
        - path: rtsp://camera/mainstream
          roles:
            - record
```

### GPU Acceleration

```yaml
# Intel Quick Sync
ffmpeg:
  hwaccel_args: preset-vaapi

# Verify GPU usage
# Check with: intel_gpu_top

# NVIDIA
ffmpeg:
  hwaccel_args: preset-nvidia-h264

# Verify with: nvidia-smi
```

### Coral TPU Optimization

```yaml
# Single Coral handles ~100 FPS
# For multiple cameras, consider:
# - Lower detection FPS
# - Multiple Corals
# - Detection priorities

# Priority detection
cameras:
  front_door:
    detect:
      fps: 10  # Higher priority

  backyard:
    detect:
      fps: 3  # Lower priority
```

### Storage Management

```yaml
record:
  enabled: true
  retain:
    days: 7
    mode: motion  # Only keep motion events
  events:
    pre_capture: 5
    post_capture: 5
    retain:
      default: 14
      objects:
        person: 30  # Keep person events longer

# Storage calculator:
# 1 camera @ 2 Mbps continuous = ~21 GB/day
# With motion-only: ~2-5 GB/day typically
```

---

## Troubleshooting

### Camera Connection Issues

```yaml
# Check RTSP stream
# ffprobe rtsp://user:pass@camera/stream

# Common fixes:
# 1. Verify credentials
# 2. Check firewall/VLAN rules
# 3. Try different RTSP port (554, 8554)
# 4. Use TCP transport:
ffmpeg:
  input_args: -rtsp_transport tcp
```

### Detection Not Working

```yaml
# Check detector status in Frigate UI
# http://frigate:5000 → System → Detectors

# Verify Coral is detected:
# - USB: lsusb | grep Google
# - PCIe: ls /dev/apex*

# Ensure detection is enabled:
cameras:
  front_door:
    detect:
      enabled: true
```

### High CPU Usage

```yaml
# 1. Use hardware acceleration
# 2. Lower detection FPS
# 3. Use substream for detection
# 4. Reduce motion detection sensitivity
# 5. Add motion masks for busy areas

motion:
  threshold: 30  # Higher = less sensitive
  mask:
    - 0,0,100,100  # Mask busy areas
```

### MQTT Connection Issues

```yaml
# Check MQTT connectivity:
# mosquitto_sub -h broker -u user -P pass -t 'frigate/#'

# Verify MQTT config:
mqtt:
  enabled: true
  host: 192.168.1.100
  port: 1883
  user: frigate
  password: password
  # client_id must be unique
  client_id: frigate_nvr
```

---

## Best Practices

### Camera Placement

1. **Entry points** - All doors, garage, driveway
2. **Height** - 8-10 feet for best detection
3. **Angle** - Slight downward angle
4. **Lighting** - Ensure adequate IR or visible light
5. **Avoid backlighting** - Don't point at bright lights

### Detection Zones

1. **Define entry zones** - Focus on approach areas
2. **Exclude false positive areas** - Trees, flags, shadows
3. **Use separate zones** - Different alerts per zone
4. **Test thoroughly** - Walk through detection areas

### Retention Strategy

```yaml
# Tiered retention
record:
  events:
    retain:
      default: 7
      objects:
        person: 30  # Keep person events longer
        car: 14
        dog: 3

# Archive important events manually via UI
# or automate with download automation
```

---

## Related References

- [MQTT Integration](integrations-mqtt.md) - MQTT setup
- [Automations](automations.md) - Automation patterns
- [Notifications](scripts.md#notifications) - Notification patterns
- [Dashboard Cards](dashboard-cards.md) - Dashboard configuration
