# Home Assistant Backup, Restore & Data Management

## Table of Contents
- [Backup Strategies](#backup-strategies)
- [Automated Backups](#automated-backups)
- [Cloud Backup Integrations](#cloud-backup-integrations)
- [Backup Contents](#backup-contents)
- [Restore Procedures](#restore-procedures)
- [Selective Restore](#selective-restore)
- [Database Management](#database-management)
- [Configuration Snapshots](#configuration-snapshots)
- [Disaster Recovery](#disaster-recovery)
- [Migration Scenarios](#migration-scenarios)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Backup Strategies

### Backup Types

| Type | Contents | Size | Frequency |
|------|----------|------|-----------|
| **Full Backup** | Everything including add-ons | Large (1-10+ GB) | Weekly |
| **Partial Backup** | Selected components only | Medium | Daily |
| **Config Only** | YAML files, secrets, DB excluded | Small (< 100 MB) | On change |

### Recommended Strategy

```markdown
## 3-2-1 Backup Rule
- 3 copies of your data
- 2 different storage types (local + cloud)
- 1 off-site backup

## Suggested Schedule
- Daily: Automated partial backup (config + database)
- Weekly: Full backup including add-ons
- Monthly: Off-site/cloud backup verification
- Before updates: Manual full backup
```

### What to Backup

```yaml
# Critical (Always backup)
- Configuration files (*.yaml)
- secrets.yaml
- .storage/ directory
- Custom components
- Themes
- www/ folder (local resources)

# Important (Recommended)
- Add-on data (Node-RED flows, etc.)
- Database (home-assistant_v2.db)
- SSL certificates

# Optional (Large, can be recreated)
- Media files
- Camera recordings
- Backup history
```

---

## Automated Backups

### Using Home Assistant Built-in Service

```yaml
# configuration.yaml (optional, UI is preferred)
# Backups are managed via Settings > System > Backups
```

### Scheduled Backup Automation

```yaml
# automations/backup.yaml
automation:
  - id: daily_backup
    alias: "System - Daily Backup"
    description: "Create daily automated backup"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: backup.create
        data:
          name: "daily_{{ now().strftime('%Y%m%d') }}"

  - id: weekly_full_backup
    alias: "System - Weekly Full Backup"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: backup.create
        data:
          name: "weekly_full_{{ now().strftime('%Y%m%d') }}"

  - id: pre_update_backup
    alias: "System - Pre-Update Backup"
    trigger:
      - platform: state
        entity_id: update.home_assistant_core_update
        to: "on"
    action:
      - service: backup.create
        data:
          name: "pre_update_{{ state_attr('update.home_assistant_core_update', 'latest_version') }}"
      - service: notify.admin
        data:
          title: "Update Available"
          message: >
            HA {{ state_attr('update.home_assistant_core_update', 'latest_version') }} available.
            Pre-update backup created.
```

### Backup with Retention

```yaml
# Script to create backup and cleanup old ones
script:
  managed_backup:
    alias: "Create Managed Backup"
    sequence:
      - service: backup.create
        data:
          name: "auto_{{ now().strftime('%Y%m%d_%H%M') }}"
      # Note: Automatic cleanup requires shell commands or custom component
      - service: notify.admin
        data:
          message: "Backup created. Remember to periodically clean old backups."
```

### Backup Monitoring

```yaml
# Template sensor to monitor backups
template:
  - sensor:
      - name: "Last Backup Age"
        unit_of_measurement: "hours"
        state: >
          {% set backups = state_attr('sensor.backup_state', 'backups') %}
          {% if backups %}
            {% set last = backups | sort(attribute='date', reverse=true) | first %}
            {{ ((as_timestamp(now()) - as_timestamp(last.date)) / 3600) | round(1) }}
          {% else %}
            unknown
          {% endif %}
        icon: mdi:backup-restore

automation:
  - id: backup_overdue_alert
    alias: "System - Backup Overdue Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.last_backup_age
        above: 48
    action:
      - service: notify.admin
        data:
          title: "Backup Overdue"
          message: "No backup in {{ states('sensor.last_backup_age') }} hours. Please create a backup."
```

---

## Cloud Backup Integrations

### Google Drive Backup (Add-on)

```yaml
# Add-on: Home Assistant Google Drive Backup
# Repository: https://github.com/sabeechen/hassio-google-drive-backup

# After installation, configure via add-on UI:
# - max_backups_in_ha: 5
# - max_backups_in_google_drive: 10
# - days_between_backups: 1
# - backup_time_of_day: "03:00"
# - exclude_addons: []
# - exclude_folders: []
```

```yaml
# Automation to trigger manual upload
automation:
  - id: upload_backup_to_drive
    alias: "System - Upload to Google Drive"
    trigger:
      - platform: event
        event_type: backup_successful
    action:
      - delay: "00:05:00"  # Wait for backup to complete
      - service: hassio.addon_stdin
        data:
          addon: cebe7a76_hassio_google_drive_backup
          input:
            command: "backup"
```

### Dropbox Backup

```yaml
# Using shell commands (requires SSH access)
shell_command:
  backup_to_dropbox: >
    /usr/bin/rclone copy /backup/ dropbox:HomeAssistant/backups/
    --config=/config/rclone.conf
    --max-age 7d

automation:
  - id: sync_to_dropbox
    alias: "System - Sync Backups to Dropbox"
    trigger:
      - platform: time
        at: "04:00:00"
    action:
      - service: shell_command.backup_to_dropbox
```

### Network Share (Samba/NFS)

```yaml
# Mount network share in Home Assistant OS
# Settings > System > Storage > Add Network Storage

# Then use in automations
shell_command:
  copy_backup_to_nas: >
    cp /backup/*.tar /media/nas_backup/homeassistant/

automation:
  - id: backup_to_nas
    alias: "System - Copy Backup to NAS"
    trigger:
      - platform: time
        at: "04:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: backup.create
        data:
          name: "nas_backup_{{ now().strftime('%Y%m%d') }}"
      - delay: "00:30:00"  # Wait for backup
      - service: shell_command.copy_backup_to_nas
```

### AWS S3 Backup

```yaml
# Using rclone for S3
shell_command:
  backup_to_s3: >
    /usr/bin/rclone sync /backup/ s3:my-ha-bucket/backups/
    --config=/config/rclone.conf

# rclone.conf example:
# [s3]
# type = s3
# provider = AWS
# access_key_id = YOUR_KEY
# secret_access_key = YOUR_SECRET
# region = eu-north-1
```

---

## Backup Contents

### Full Backup Structure

```
backup.tar
├── backup.json           # Backup metadata
├── homeassistant.tar.gz  # HA configuration
│   ├── configuration.yaml
│   ├── automations.yaml
│   ├── scripts.yaml
│   ├── scenes.yaml
│   ├── secrets.yaml
│   ├── .storage/         # UI configurations, entity registry
│   ├── custom_components/
│   ├── www/
│   ├── themes/
│   └── home-assistant_v2.db  # Database
├── addons/
│   └── [addon-slug].tar.gz   # Each add-on's data
└── ssl/                  # SSL certificates
```

### Partial Backup Options

```yaml
# Via UI: Settings > System > Backups > Create Backup
# Select components:
# - Home Assistant configuration
# - Add-ons (select specific ones)
# - Folders (media, share, ssl, etc.)
```

### Exclude from Backup

```yaml
# .homeassistant/.storage/lovelace* - Dashboard configs (can be large)
# Large folders that can be recreated:
# - media/
# - www/cameras/  # Camera recordings
# - tts/          # Text-to-speech cache
```

---

## Restore Procedures

### Full System Restore

```markdown
## From Home Assistant UI
1. Settings > System > Backups
2. Upload backup file (if not present)
3. Click on backup
4. Select "Restore"
5. Choose what to restore
6. Confirm and wait

## From Fresh Installation
1. Install Home Assistant
2. Complete onboarding
3. Settings > System > Backups
4. Upload backup
5. Restore
```

### Command Line Restore

```bash
# SSH to Home Assistant
# List available backups
ha backups list

# Restore specific backup
ha backups restore [slug] --homeassistant

# Restore with add-ons
ha backups restore [slug] --homeassistant --addons

# Restore specific add-on
ha backups restore [slug] --addons=core_mosquitto
```

### Network Restore

```bash
# Copy backup to Home Assistant
scp backup.tar root@homeassistant:/backup/

# Or via Samba share
# Copy to \\homeassistant\backup\
```

### USB Restore (Home Assistant OS)

```markdown
## USB Recovery
1. Copy backup.tar to USB drive root
2. Name it exactly: [slug].tar (or keep original name)
3. Insert USB into Home Assistant device
4. Reboot
5. Backup will appear in UI

## Alternative: Use SD Card
1. Mount HA SD card on another computer
2. Copy backup to /backup/ partition
3. Reinsert and boot
```

---

## Selective Restore

### Restore Only Configuration

```bash
# Extract backup
tar -xf backup.tar

# Extract homeassistant config
tar -xzf homeassistant.tar.gz -C /tmp/ha_restore/

# Copy specific files
cp /tmp/ha_restore/automations.yaml /config/
cp /tmp/ha_restore/scripts.yaml /config/
```

### Restore Single Add-on

```bash
# From backup, restore only one add-on
ha backups restore [slug] --addons=core_mosquitto

# Or extract manually
tar -xf backup.tar
tar -xzf addons/core_mosquitto.tar.gz -C /tmp/addon_restore/
```

### Restore Database Only

```bash
# Stop Home Assistant
ha core stop

# Extract database from backup
tar -xf backup.tar
tar -xzf homeassistant.tar.gz home-assistant_v2.db

# Replace current database
mv /config/home-assistant_v2.db /config/home-assistant_v2.db.old
mv home-assistant_v2.db /config/

# Start Home Assistant
ha core start
```

### Restore .storage (Entity Registry, Areas, etc.)

```bash
# Extract .storage from backup
tar -xf backup.tar
tar -xzf homeassistant.tar.gz .storage/

# Carefully copy needed files
cp .storage/core.entity_registry /config/.storage/
cp .storage/core.area_registry /config/.storage/
cp .storage/core.device_registry /config/.storage/

# Restart Home Assistant
ha core restart
```

---

## Database Management

### Database Location

```yaml
# Default location
# /config/home-assistant_v2.db

# Custom location (configuration.yaml)
recorder:
  db_url: sqlite:////config/database/home-assistant_v2.db
```

### Database Size Management

```yaml
# configuration.yaml
recorder:
  purge_keep_days: 10          # Keep 10 days of history
  commit_interval: 1           # Commit every second
  auto_purge: true             # Automatically purge old data
  auto_repack: true            # Repack database after purge

  # Exclude entities to reduce size
  exclude:
    domains:
      - automation
      - script
      - updater
      - camera
    entity_globs:
      - sensor.weather_*
      - sensor.*_linkquality
    entities:
      - sun.sun
      - sensor.date
      - sensor.time

  # Only include specific entities
  include:
    domains:
      - sensor
      - binary_sensor
      - climate
    entities:
      - person.john
      - device_tracker.john_phone
```

### Manual Database Purge

```yaml
# Service call
service: recorder.purge
data:
  keep_days: 5
  repack: true

# Automation for scheduled purge
automation:
  - id: database_maintenance
    alias: "System - Database Maintenance"
    trigger:
      - platform: time
        at: "04:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: recorder.purge
        data:
          keep_days: 10
          repack: true
```

### Database Optimization

```bash
# SSH to Home Assistant
# Stop HA first
ha core stop

# Compact SQLite database
sqlite3 /config/home-assistant_v2.db "VACUUM;"

# Analyze for better performance
sqlite3 /config/home-assistant_v2.db "ANALYZE;"

# Start HA
ha core start
```

### Move to External Database

```yaml
# MariaDB (recommended for better performance)
# 1. Install MariaDB add-on
# 2. Configure:

recorder:
  db_url: mysql://homeassistant:password@core-mariadb/homeassistant?charset=utf8mb4
  # Note: History starts fresh after migration

# PostgreSQL
recorder:
  db_url: postgresql://user:password@localhost/homeassistant
```

### Database Corruption Recovery

```bash
# Signs of corruption:
# - "Database is locked" errors
# - History not recording
# - Slow startup

# Solution 1: Repack
ha core stop
sqlite3 /config/home-assistant_v2.db "PRAGMA integrity_check;"
sqlite3 /config/home-assistant_v2.db "VACUUM;"
ha core start

# Solution 2: Fresh start (lose history)
ha core stop
mv /config/home-assistant_v2.db /config/home-assistant_v2.db.corrupt
ha core start
# HA creates new database on start
```

---

## Configuration Snapshots

### Git-Based Version Control

```bash
# Initialize git in config directory
cd /config
git init

# Create .gitignore
cat > .gitignore << EOF
# Secrets
secrets.yaml
*.pem
*.key

# Database
*.db
*.db-shm
*.db-wal

# Temporary files
__pycache__/
.cloud/
.storage/auth*
deps/
tts/

# Large files
www/cameras/
media/
EOF

# Initial commit
git add .
git commit -m "Initial configuration"
```

```yaml
# Automation for config snapshots
shell_command:
  git_commit: 'cd /config && git add -A && git commit -m "Auto-commit: {{ states("sensor.date") }}"'
  git_push: 'cd /config && git push origin main'

automation:
  - id: config_snapshot_daily
    alias: "System - Daily Config Snapshot"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: shell_command.git_commit
```

### Manual Snapshots

```yaml
# Script for manual snapshots
script:
  config_snapshot:
    alias: "Create Config Snapshot"
    sequence:
      - service: shell_command.git_commit
      - service: notify.admin
        data:
          message: "Configuration snapshot created"
```

---

## Disaster Recovery

### Recovery Scenarios

#### Scenario 1: Corrupted SD Card (Raspberry Pi)

```markdown
## Recovery Steps
1. Get new SD card
2. Flash Home Assistant OS
3. Boot and complete minimal setup
4. Restore from backup (NAS/cloud)

## Prevention
- Use SSD instead of SD card
- Regular backups to external location
- Monitor SD card health
```

#### Scenario 2: Hardware Failure

```markdown
## Recovery Steps
1. Get replacement hardware (or VM)
2. Install Home Assistant
3. Restore from cloud backup
4. Verify all integrations
5. Re-pair Bluetooth/USB devices

## Prevention
- Document hardware-specific configs
- Keep spare USB devices (Zigbee/Z-Wave sticks)
- Test restore process periodically
```

#### Scenario 3: Ransomware/Malware

```markdown
## Recovery Steps
1. DO NOT pay ransom
2. Disconnect from network
3. Wipe system completely
4. Fresh install from known-good media
5. Restore from offline backup (before infection)
6. Change all passwords
7. Update all firmware

## Prevention
- Regular offline backups
- Strong passwords
- Disable unused services
- Keep system updated
```

### Disaster Recovery Plan Template

```yaml
# disaster_recovery.yaml (keep printed copy!)

# Critical Information
home_assistant_version: "2024.12.0"
installation_type: "Home Assistant OS"
hardware: "Raspberry Pi 4 8GB"

# Network Configuration
static_ip: "192.168.1.100"
gateway: "192.168.1.1"
dns: "192.168.1.1"

# Backup Locations
primary_backup: "Google Drive"
secondary_backup: "NAS (192.168.1.50)"
offline_backup: "USB drive in safe"

# Critical Integrations
zigbee_coordinator: "Sonoff ZBDongle-E on /dev/ttyUSB0"
zwave_controller: "Aeotec Z-Stick 7 on /dev/ttyUSB1"

# Recovery Steps
1. Flash HA OS to SD card/SSD
2. Configure network (static IP)
3. Access http://homeassistant.local:8123
4. Complete onboarding
5. Upload backup from [location]
6. Restore backup
7. Verify integrations
8. Re-pair if needed: [list devices]
```

---

## Migration Scenarios

### Pi to Different Hardware

```markdown
## Migration Steps
1. Create full backup on Pi
2. Download backup file
3. Install HA on new hardware
4. Upload and restore backup
5. Update IP/hostname if changed
6. Move USB devices to new hardware
7. Verify Z-Wave/Zigbee networks

## Notes
- Zigbee/Z-Wave networks stored on coordinator
- Most integrations auto-reconnect
- May need to reconfigure some add-ons
```

### Docker to Home Assistant OS

```markdown
## Migration Steps
1. Stop Docker container
2. Copy /config directory
3. Create backup tar manually:
   tar -czvf backup.tar.gz /config
4. Install HA OS
5. Upload backup
6. Restore
7. Install needed add-ons manually

## Differences
- Add-ons replace Docker containers
- Supervisor manages updates
- Some paths may change
```

### VM to Dedicated Hardware

```markdown
## Migration Steps
1. Create backup in VM
2. Export backup
3. Install HA OS on hardware
4. Import and restore backup
5. Update network configuration
6. Reconnect USB devices
7. Update any VM-specific configs
```

---

## Best Practices

### Backup Checklist

```markdown
## Weekly Verification
- [ ] Backup exists from last 24 hours
- [ ] Backup uploaded to cloud
- [ ] Backup size reasonable (not 0 bytes)

## Monthly Verification
- [ ] Download and verify backup can open
- [ ] Check cloud storage space
- [ ] Review retention policy

## Quarterly
- [ ] Test restore to test system
- [ ] Update recovery documentation
- [ ] Verify off-site backup accessible
```

### Security Considerations

```yaml
# Protect secrets in backups
# secrets.yaml should contain sensitive data

# Consider encrypting backups
# Google Drive Backup add-on supports encryption

# Limit backup access
# Use strong passwords for cloud storage
# Enable 2FA where possible
```

### Monitoring Setup

```yaml
automation:
  - id: backup_health_check
    alias: "System - Backup Health Check"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - choose:
          - conditions:
              - condition: numeric_state
                entity_id: sensor.last_backup_age
                above: 48
            sequence:
              - service: notify.admin
                data:
                  title: "Backup Warning"
                  message: "No backup in {{ states('sensor.last_backup_age') | round }} hours"
          - conditions:
              - condition: numeric_state
                entity_id: sensor.backup_count
                below: 3
            sequence:
              - service: notify.admin
                data:
                  title: "Backup Warning"
                  message: "Only {{ states('sensor.backup_count') }} backups stored"
```

---

## Troubleshooting

### Common Issues

#### Backup Fails to Create

```markdown
## Possible Causes
- Disk space full
- Permission issues
- Add-on stuck

## Solutions
1. Check disk space: Settings > System > Storage
2. Restart Home Assistant
3. Try partial backup (exclude large add-ons)
4. Check logs for specific errors
```

#### Restore Fails

```markdown
## Possible Causes
- Corrupted backup file
- Version mismatch
- Incomplete upload

## Solutions
1. Try uploading backup again
2. Check backup integrity (can open tar file)
3. Try restoring only configuration (not add-ons)
4. Check available disk space
```

#### Database Too Large

```yaml
# Check size
# Settings > System > Storage

# Reduce history
recorder:
  purge_keep_days: 5
  exclude:
    domains:
      - camera
      - media_player

# Force purge
service: recorder.purge
data:
  keep_days: 3
  repack: true
```

#### Backup Stuck

```bash
# SSH to Home Assistant
# Check running backups
ha backups list

# Cancel stuck backup
ha backups remove [stuck_slug]

# Restart supervisor
ha supervisor restart
```

### Logs and Diagnostics

```yaml
# Enable debug logging for backup issues
logger:
  default: info
  logs:
    homeassistant.components.backup: debug
    supervisor.backups: debug
```

```bash
# View backup logs
ha supervisor logs | grep -i backup

# Check supervisor status
ha supervisor info
```
