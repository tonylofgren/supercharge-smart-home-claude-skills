# Home Assistant Integration Development - Prompt Ideas

> 50+ advanced prompts for building custom Home Assistant integrations in Python

## Table of Contents
- [Config Flow & Authentication](#config-flow--authentication)
- [Data Fetching Patterns](#data-fetching-patterns)
- [Entity Implementations](#entity-implementations)
- [Multi-Device Hub Patterns](#multi-device-hub-patterns)
- [Services & Events](#services--events)
- [Advanced Patterns](#advanced-patterns)
- [Publishing & HACS](#publishing--hacs)
- [Testing & Quality](#testing--quality)
- [Real-World Integration Examples](#real-world-integration-examples)

---

## Config Flow & Authentication

### OAuth2 Authentication
- "Create a config flow with OAuth2 authentication for a cloud API like Spotify or Google"
- "Implement application credentials for OAuth2 with automatic token refresh"
- "Add reauth flow that triggers when OAuth2 access token is revoked"
- "Create OAuth2 flow with PKCE (Proof Key for Code Exchange) for mobile apps"

### API Key Authentication
- "Create a config flow that validates an API key before saving"
- "Implement config flow with API key stored securely in config entry"
- "Add test connection button in config flow to verify API credentials"

### Local Device Authentication
- "Create config flow with local IP address and optional password"
- "Implement config flow that discovers devices via Zeroconf/mDNS"
- "Add SSDP discovery for UPnP devices with automatic config flow"
- "Create DHCP discovery that detects devices by MAC address prefix"

### Advanced Config Flow
- "Implement multi-step config wizard with device selection"
- "Create options flow with dynamically loaded defaults from current config"
- "Add reconfigure flow that allows changing host without removing integration"
- "Implement import flow to migrate YAML configuration to config entry"

---

## Data Fetching Patterns

### Polling with DataUpdateCoordinator
- "Create DataUpdateCoordinator with 30-second polling interval"
- "Implement coordinator with exponential backoff on API errors"
- "Add rate limiting to coordinator to respect API limits (max 100 requests/hour)"
- "Create coordinator that handles pagination for large API responses"

### WebSocket / Push Updates
- "Implement WebSocket connection for real-time device updates"
- "Create coordinator that maintains persistent WebSocket with auto-reconnect"
- "Add fallback to polling when WebSocket connection fails"
- "Implement Server-Sent Events (SSE) for push notifications"

### Advanced Data Patterns
- "Create multiple coordinators with different update intervals (fast/slow)"
- "Implement coordinator with local caching to reduce API calls"
- "Add conditional updates - only fetch when entity is being observed"
- "Create coordinator that batches requests for multiple devices"

---

## Entity Implementations

### Sensors
- "Create sensor entity with native_value and extra_state_attributes"
- "Implement sensor with device_class and state_class for statistics"
- "Add sensor with unit conversion (Celsius/Fahrenheit, km/miles)"
- "Create diagnostic sensor for API rate limit remaining"

### Binary Sensors
- "Implement binary sensor for motion detection with device_class"
- "Create connectivity binary sensor that tracks device online status"
- "Add problem binary sensor for device error states"

### Switches
- "Create switch entity with optimistic mode for slow devices"
- "Implement switch with assumed_state for devices without feedback"
- "Add switch that controls multiple device parameters at once"

### Climate (HVAC)
- "Implement climate entity with heat/cool/auto modes"
- "Create climate with target temperature range (heat_cool mode)"
- "Add climate entity with fan modes and swing modes"
- "Implement climate with preset modes (home, away, sleep)"

### Covers
- "Create cover entity for garage door with open/close/stop"
- "Implement cover with position control (0-100%)"
- "Add cover with tilt position for blinds"

### Lights
- "Implement light entity with brightness and color temperature"
- "Create light with RGB color support and effects"
- "Add light entity with transition support"

### Other Entity Types
- "Create media_player entity with play/pause/volume controls"
- "Implement vacuum entity with start/stop/return_to_base"
- "Add lock entity with lock/unlock and optional code"
- "Create button entity for triggering device actions"
- "Implement number entity for device settings (1-100 range)"
- "Add select entity for choosing device modes"
- "Create calendar entity that syncs with external calendar API"

---

## Multi-Device Hub Patterns

### Hub Architecture
- "Create hub integration that discovers and manages multiple child devices"
- "Implement device registry with parent/child relationships"
- "Add dynamic entity creation when new devices are discovered"
- "Create hub that supports adding/removing devices without restart"

### EntityDescription Pattern
- "Implement EntityDescription dataclasses for sensor definitions"
- "Create typed EntityDescription with custom value extraction functions"
- "Add entity descriptions with translation keys for localization"

### Device Management
- "Implement device info with connections (MAC address) and identifiers"
- "Create device triggers for automation support"
- "Add device actions for service calls targeting specific devices"
- "Implement suggested_area based on device location from API"

---

## Services & Events

### Custom Services
- "Create custom service with voluptuous schema validation"
- "Implement service that returns response data (SupportsResponse.ONLY)"
- "Add service with entity targeting using cv.entity_ids"
- "Create service with optional parameters and defaults"

### Event Handling
- "Fire custom events when device state changes"
- "Listen to Home Assistant events (state_changed, call_service)"
- "Implement event-based updates instead of polling"
- "Create integration that responds to homeassistant_started event"

---

## Advanced Patterns

### Diagnostics & Debugging
- "Add diagnostics.py with sensitive data redaction (API keys, tokens)"
- "Implement async_get_config_entry_diagnostics with device info"
- "Create system health reporting for integration status"

### Repair Issues
- "Create repair issue when authentication fails with fix flow"
- "Implement repair issue for deprecated configuration"
- "Add repair issue with learn_more_url for documentation"

### Migration & Compatibility
- "Implement config entry migration from version 1 to version 2"
- "Create backward-compatible entity unique_id migration"
- "Add migration that converts old entity IDs to new format"

### Integration Patterns
- "Create integration that exposes entities to Google Assistant/Alexa"
- "Implement conversation agent for voice commands"
- "Add energy platform support for power monitoring"
- "Create recorder statistics for long-term data"

### Error Handling
- "Implement ConfigEntryNotReady for temporary connection failures"
- "Create ConfigEntryAuthFailed to trigger reauth flow"
- "Add graceful degradation when some devices are offline"
- "Implement proper cleanup in async_unload_entry"

---

## Publishing & HACS

### HACS Preparation
- "Make my integration HACS-compatible with correct folder structure"
- "Create hacs.json with proper metadata and minimum HA version"
- "Add GitHub workflow for HACS validation (hassfest, hacs/action)"
- "Create README.md with HACS badge and installation instructions"
- "Add proper version numbering in manifest.json for releases"

### GitHub Repository Setup
- "Set up GitHub repository structure for HACS custom integration"
- "Create GitHub Actions workflow for automated testing on PR"
- "Add issue templates for bug reports and feature requests"
- "Create CONTRIBUTING.md with development setup instructions"

### Publishing to HACS
- "Submit my integration to HACS default repository"
- "Add required GitHub topics (hacs, home-assistant, custom-integration)"
- "Create GitHub release with proper version tag"
- "Set up automatic release workflow when tag is pushed"

### Home Assistant Core Contribution
- "Prepare my integration for Home Assistant Core submission"
- "Add 100% test coverage required for Core integrations"
- "Implement quality scale requirements (bronze/silver/gold)"
- "Create documentation PR for home-assistant.io"

---

## Testing & Quality

### Unit Tests
- "Create pytest fixtures for mocking API responses"
- "Implement config flow tests with user input simulation"
- "Add entity tests that verify state updates from coordinator"
- "Create tests for error handling and edge cases"

### Integration Tests
- "Test full setup/unload cycle for config entry"
- "Verify device and entity registry entries are created correctly"
- "Test service calls and verify device API is called"

---

## Real-World Integration Examples

### Cloud API Integrations (like Local Tuya, Xiaomi Miot)
- "Create integration for cloud API with OAuth2 and local fallback"
- "Implement integration that syncs devices from cloud but controls locally"
- "Add integration with cloud push notifications for instant updates"

### Local Device Integrations (like Shelly, ESPHome)
- "Create integration for local HTTP API with mDNS discovery"
- "Implement integration with local CoAP protocol"
- "Add integration that uses local MQTT for communication"

### Monitoring Integrations (like Powercalc, Battery Notes)
- "Create integration that estimates power consumption from device states"
- "Implement integration that tracks and alerts on battery levels"
- "Add integration that monitors API usage and costs"

### Security Integrations (like Alarmo, Frigate)
- "Create alarm control panel integration with arm/disarm modes"
- "Implement camera integration with motion detection events"
- "Add integration that processes camera feeds for object detection"

### Data Integrations (like Weather, Calendar)
- "Create weather integration with forecast data"
- "Implement calendar integration with event synchronization"
- "Add integration that aggregates data from multiple sources"

---

## Quick Reference

| Pattern | Use When |
|---------|----------|
| DataUpdateCoordinator | Polling APIs at regular intervals |
| WebSocket | Real-time updates from device/cloud |
| OAuth2 | Cloud services requiring user authorization |
| Zeroconf | Local devices advertising via mDNS |
| EntityDescription | Multiple similar entities (sensors, switches) |
| Repair Issues | User action needed to fix problems |
| Services | Custom actions beyond entity control |

---

For detailed implementation examples, see the reference files in `references/`.
