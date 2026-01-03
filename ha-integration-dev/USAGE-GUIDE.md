# Home Assistant Python Integration Development - Usage Guide

Complete guide with 50+ usage examples organized by skill level. Learn how to build custom_components for Home Assistant.

## Table of Contents

- [How It Works](#how-it-works)
- [Beginner Examples](#beginner-examples)
- [Intermediate Examples](#intermediate-examples)
- [Advanced Examples](#advanced-examples)
- [Troubleshooting Examples](#troubleshooting-examples)
- [Tips and Tricks](#tips-and-tricks)

---

## How It Works

### Basic Interaction Pattern

1. **Describe what you need** - API type, authentication, entity types
2. **Claude generates** complete Python integration code
3. **Copy to custom_components** folder and restart Home Assistant

### Example Conversation

**You:** Create a Python custom integration for a cloud API that returns temperature and humidity data with API key authentication

**Claude:** Here's a complete custom integration:

```
custom_components/
  my_integration/
    __init__.py          # Setup and config entry handling
    config_flow.py       # User interface for adding integration
    coordinator.py       # DataUpdateCoordinator for API polling
    sensor.py            # Sensor entities
    manifest.json        # Integration metadata
    strings.json         # UI labels
```

```python
# coordinator.py
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class MyCoordinator(DataUpdateCoordinator):
    """Fetch data from API."""

    def __init__(self, hass, api_key):
        super().__init__(
            hass,
            _LOGGER,
            name="My Integration",
            update_interval=timedelta(seconds=30),
        )
        self.api_key = api_key

    async def _async_update_data(self):
        async with async_timeout.timeout(10):
            return await self.hass.async_add_executor_job(
                self._fetch_data
            )
```

---

## Beginner Examples

### 1. First Integration Skeleton

**You:** Create a minimal Python custom integration skeleton with config flow

**What you get:**
- `__init__.py` with async_setup_entry/async_unload_entry
- `config_flow.py` with basic ConfigFlow class
- `manifest.json` with proper metadata
- `strings.json` for UI labels

---

### 2. Simple Config Flow

**You:** Add a config flow that asks for API key and validates it

**What you get:**
```python
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await self._validate_api_key(user_input[CONF_API_KEY])
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title="My Integration",
                    data=user_input,
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )
```

---

### 3. Basic Sensor Entity

**You:** Create a sensor entity that displays temperature from the coordinator

**What you get:**
```python
class MySensor(CoordinatorEntity, SensorEntity):
    """Sensor entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device_id):
        super().__init__(coordinator)
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_name = "Temperature"

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature")
```

---

### 4. Binary Sensor Entity

**You:** Create a binary sensor for motion detection

**What you get:**
```python
class MotionSensor(CoordinatorEntity, BinarySensorEntity):
    """Motion sensor entity."""

    _attr_device_class = BinarySensorDeviceClass.MOTION

    @property
    def is_on(self):
        return self.coordinator.data.get("motion_detected", False)
```

---

### 5. Switch Entity

**You:** Create a switch that controls a device power state

**What you get:**
```python
class MySwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity."""

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_power(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_power(False)
        await self.coordinator.async_request_refresh()

    @property
    def is_on(self):
        return self.coordinator.data.get("power", False)
```

---

### 6. Device Registry Entry

**You:** Add device info so my entities appear under one device

**What you get:**
```python
@property
def device_info(self):
    return DeviceInfo(
        identifiers={(DOMAIN, self._device_id)},
        name="My Device",
        manufacturer="ACME Corp",
        model="Model X",
        sw_version=self.coordinator.data.get("firmware"),
    )
```

---

### 7. Manifest.json Setup

**You:** Create a proper manifest.json for my integration

**What you get:**
```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "codeowners": ["@username"],
  "config_flow": true,
  "documentation": "https://github.com/user/my_integration",
  "iot_class": "cloud_polling",
  "requirements": ["my-api-library==1.0.0"],
  "version": "1.0.0"
}
```

---

### 8. Strings.json for UI

**You:** Add proper UI labels for config flow

**What you get:**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to My Service",
        "description": "Enter your API key from the My Service dashboard.",
        "data": {
          "api_key": "API Key"
        }
      }
    },
    "error": {
      "invalid_auth": "Invalid API key",
      "cannot_connect": "Failed to connect to service"
    }
  }
}
```

---

### 9. Extra State Attributes

**You:** Add extra attributes to my sensor

**What you get:**
```python
@property
def extra_state_attributes(self):
    return {
        "last_updated": self.coordinator.data.get("timestamp"),
        "battery_level": self.coordinator.data.get("battery"),
        "signal_strength": self.coordinator.data.get("rssi"),
    }
```

---

### 10. Entity Categories

**You:** Mark some entities as diagnostic or configuration

**What you get:**
```python
# Diagnostic sensor (shown under Diagnostics)
_attr_entity_category = EntityCategory.DIAGNOSTIC

# Configuration entity (shown under Configuration)
_attr_entity_category = EntityCategory.CONFIG
```

---

## Intermediate Examples

### 11. DataUpdateCoordinator Setup

**You:** Create a Python custom integration with DataUpdateCoordinator that polls every 30 seconds

**What you get:**
```python
class MyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                return await self.api.get_data()
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
```

---

### 12. Error Handling in Coordinator

**You:** Add proper error handling with exponential backoff

**What you get:**
```python
async def _async_update_data(self):
    try:
        async with async_timeout.timeout(10):
            return await self.api.get_data()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed from err
    except ConnectionError as err:
        raise UpdateFailed(f"Connection failed: {err}")
```

---

### 13. Options Flow

**You:** Add options flow to change polling interval after setup

**What you get:**
```python
class OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, 30
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            }),
        )
```

---

### 14. Reauth Flow

**You:** Add reauth flow when API credentials expire

**What you get:**
```python
async def async_step_reauth(self, entry_data):
    """Handle reauth when credentials are invalid."""
    self._reauth_entry = self.hass.config_entries.async_get_entry(
        self.context["entry_id"]
    )
    return await self.async_step_reauth_confirm()

async def async_step_reauth_confirm(self, user_input=None):
    errors = {}
    if user_input is not None:
        try:
            await self._validate_credentials(user_input)
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        else:
            self.hass.config_entries.async_update_entry(
                self._reauth_entry,
                data={**self._reauth_entry.data, **user_input},
            )
            await self.hass.config_entries.async_reload(
                self._reauth_entry.entry_id
            )
            return self.async_abort(reason="reauth_successful")
    # Show form...
```

---

### 15. Multiple Entity Platforms

**You:** Set up multiple entity platforms (sensor, switch, binary_sensor)

**What you get:**
```python
# __init__.py
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.BINARY_SENSOR]

async def async_setup_entry(hass, entry):
    coordinator = MyCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
```

---

### 16. Climate Entity

**You:** Create a climate entity with heat/cool modes

**What you get:**
```python
class MyClimate(CoordinatorEntity, ClimateEntity):
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
    )

    @property
    def current_temperature(self):
        return self.coordinator.data.get("current_temp")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("target_temp")

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        await self.coordinator.api.set_temperature(temp)
        await self.coordinator.async_request_refresh()
```

---

### 17. Cover Entity

**You:** Create a cover entity for a garage door

**What you get:**
```python
class MyGarageDoor(CoordinatorEntity, CoverEntity):
    _attr_device_class = CoverDeviceClass.GARAGE
    _attr_supported_features = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
    )

    @property
    def is_closed(self):
        return self.coordinator.data.get("state") == "closed"

    async def async_open_cover(self, **kwargs):
        await self.coordinator.api.open_door()
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs):
        await self.coordinator.api.close_door()
        await self.coordinator.async_request_refresh()
```

---

### 18. Light Entity with Colors

**You:** Create a light entity with brightness and RGB color

**What you get:**
```python
class MyLight(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    @property
    def is_on(self):
        return self.coordinator.data.get("on", False)

    @property
    def brightness(self):
        return self.coordinator.data.get("brightness")

    @property
    def rgb_color(self):
        return self.coordinator.data.get("rgb")

    async def async_turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        rgb = kwargs.get(ATTR_RGB_COLOR)
        await self.coordinator.api.set_light(
            on=True, brightness=brightness, rgb=rgb
        )
        await self.coordinator.async_request_refresh()
```

---

### 19. Zeroconf Discovery

**You:** Add mDNS/Zeroconf discovery to my Python integration

**What you get:**
```python
# config_flow.py
async def async_step_zeroconf(self, discovery_info):
    """Handle zeroconf discovery."""
    host = discovery_info.host
    name = discovery_info.name.removesuffix("._mydevice._tcp.local.")

    await self.async_set_unique_id(discovery_info.properties["mac"])
    self._abort_if_unique_id_configured(updates={CONF_HOST: host})

    self.context["title_placeholders"] = {"name": name}
    self._discovered_host = host
    self._discovered_name = name
    return await self.async_step_confirm()
```

```json
// manifest.json
{
  "zeroconf": ["_mydevice._tcp.local."]
}
```

---

### 20. SSDP Discovery

**You:** Add UPnP/SSDP discovery to find devices on network

**What you get:**
```python
async def async_step_ssdp(self, discovery_info):
    """Handle SSDP discovery."""
    unique_id = discovery_info.upnp.get(ssdp.ATTR_UPNP_SERIAL)
    await self.async_set_unique_id(unique_id)
    self._abort_if_unique_id_configured()

    self._discovered_host = urlparse(
        discovery_info.ssdp_location
    ).hostname
    return await self.async_step_confirm()
```

```json
// manifest.json
{
  "ssdp": [
    {"st": "urn:schemas-upnp-org:device:MyDevice:1"}
  ]
}
```

---

### 21. Button Entity

**You:** Create button entities for device actions

**What you get:**
```python
class RestartButton(CoordinatorEntity, ButtonEntity):
    """Button to restart the device."""

    _attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self):
        await self.coordinator.api.restart()
```

---

### 22. Number Entity

**You:** Create a number entity for a setting (0-100 range)

**What you get:**
```python
class BrightnessNumber(CoordinatorEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    @property
    def native_value(self):
        return self.coordinator.data.get("brightness")

    async def async_set_native_value(self, value):
        await self.coordinator.api.set_brightness(int(value))
        await self.coordinator.async_request_refresh()
```

---

### 23. Select Entity

**You:** Create a select entity for choosing device modes

**What you get:**
```python
class ModeSelect(CoordinatorEntity, SelectEntity):
    _attr_options = ["auto", "manual", "eco", "boost"]

    @property
    def current_option(self):
        return self.coordinator.data.get("mode")

    async def async_select_option(self, option):
        await self.coordinator.api.set_mode(option)
        await self.coordinator.async_request_refresh()
```

---

### 24. Text Entity

**You:** Create a text entity for device name input

**What you get:**
```python
class DeviceNameText(CoordinatorEntity, TextEntity):
    _attr_native_max = 32
    _attr_mode = TextMode.TEXT

    @property
    def native_value(self):
        return self.coordinator.data.get("device_name")

    async def async_set_value(self, value):
        await self.coordinator.api.set_name(value)
        await self.coordinator.async_request_refresh()
```

---

### 25. Image Entity

**You:** Create an image entity that shows a device snapshot

**What you get:**
```python
class SnapshotImage(CoordinatorEntity, ImageEntity):
    _attr_content_type = "image/jpeg"

    async def async_image(self):
        return await self.coordinator.api.get_snapshot()
```

---

## Advanced Examples

### 26. OAuth2 Authentication

**You:** Create a Python custom integration with OAuth2 for a cloud service

**What you get:**
- OAuth2FlowHandler with authorization_url and token_url
- Token refresh handling
- Application credentials support
- Proper token storage in config entry

---

### 27. Multi-Device Hub

**You:** Create a hub integration that manages multiple child devices

**What you get:**
```python
async def async_setup_entry(hass, entry):
    api = MyHubAPI(entry.data[CONF_API_KEY])
    devices = await api.get_devices()

    coordinators = {}
    for device in devices:
        coordinator = DeviceCoordinator(hass, api, device.id)
        await coordinator.async_config_entry_first_refresh()
        coordinators[device.id] = coordinator

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinators": coordinators,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
```

---

### 28. EntityDescription Pattern

**You:** Use EntityDescription for multiple similar sensors

**What you get:**
```python
@dataclass(frozen=True)
class MySensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], float | None] = None

SENSOR_DESCRIPTIONS = [
    MySensorDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("temp"),
    ),
    MySensorDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.get("humidity"),
    ),
]

class MySensor(CoordinatorEntity, SensorEntity):
    entity_description: MySensorDescription

    def __init__(self, coordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data)
```

---

### 29. Custom Services

**You:** Add custom services to my Python integration

**What you get:**
```python
# __init__.py
async def async_setup_entry(hass, entry):
    # ... coordinator setup ...

    async def handle_set_mode(call):
        mode = call.data["mode"]
        device_id = call.data.get("device_id")
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.api.set_mode(device_id, mode)
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "set_mode",
        handle_set_mode,
        schema=vol.Schema({
            vol.Required("mode"): vol.In(["auto", "manual", "eco"]),
            vol.Optional("device_id"): cv.string,
        }),
    )
```

---

### 30. Service with Response Data

**You:** Create a service that returns response data

**What you get:**
```python
from homeassistant.core import SupportsResponse

async def async_setup_entry(hass, entry):
    async def handle_get_history(call):
        days = call.data.get("days", 7)
        history = await coordinator.api.get_history(days)
        return {"history": history, "count": len(history)}

    hass.services.async_register(
        DOMAIN,
        "get_history",
        handle_get_history,
        schema=vol.Schema({
            vol.Optional("days", default=7): vol.Coerce(int),
        }),
        supports_response=SupportsResponse.ONLY,
    )
```

---

### 31. WebSocket Push Updates

**You:** Create a Python custom integration with WebSocket for real-time updates

**What you get:**
```python
class WebSocketCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.api = api
        self._ws_task = None

    async def async_start_websocket(self):
        self._ws_task = self.hass.async_create_task(
            self._websocket_loop()
        )

    async def _websocket_loop(self):
        while True:
            try:
                async with self.api.websocket() as ws:
                    async for message in ws:
                        self.async_set_updated_data(message)
            except ConnectionError:
                await asyncio.sleep(5)  # Reconnect delay
```

---

### 32. Diagnostics

**You:** Add diagnostics.py with sensitive data redaction

**What you get:**
```python
from homeassistant.components.diagnostics import async_redact_data

TO_REDACT = {"api_key", "token", "password", "serial"}

async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": async_redact_data(coordinator.data, TO_REDACT),
    }
```

---

### 33. Repair Issues

**You:** Create repair issues when authentication fails

**What you get:**
```python
from homeassistant.helpers import issue_registry as ir

async def _async_update_data(self):
    try:
        return await self.api.get_data()
    except AuthenticationError:
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "auth_failed",
            is_fixable=True,
            severity=ir.IssueSeverity.ERROR,
            translation_key="auth_failed",
        )
        raise ConfigEntryAuthFailed
```

---

### 34. Config Entry Migration

**You:** Migrate config entry from version 1 to version 2

**What you get:**
```python
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    @staticmethod
    async def async_migrate_entry(hass, entry):
        if entry.version == 1:
            # Migrate from v1 to v2
            new_data = {**entry.data}
            new_data["new_field"] = "default_value"
            hass.config_entries.async_update_entry(
                entry, data=new_data, version=2
            )
        return True
```

---

### 35. Event Firing

**You:** Fire custom events when device state changes

**What you get:**
```python
async def _async_update_data(self):
    new_data = await self.api.get_data()

    # Fire event on state change
    if self.data and new_data.get("state") != self.data.get("state"):
        self.hass.bus.async_fire(
            f"{DOMAIN}_state_changed",
            {
                "device_id": self.device_id,
                "old_state": self.data.get("state"),
                "new_state": new_data.get("state"),
            },
        )
    return new_data
```

---

### 36. Conversation Agent

**You:** Create a Python custom integration as a conversation agent

**What you get:**
```python
from homeassistant.components import conversation
from homeassistant.components.conversation import ConversationEntity

class MyConversationAgent(ConversationEntity):
    _attr_supported_features = (
        conversation.ConversationEntityFeature.CONTROL
    )

    async def async_process(self, user_input):
        response = await self.coordinator.api.chat(user_input.text)
        return conversation.ConversationResult(
            response=intent.IntentResponse(language=user_input.language),
            conversation_id=user_input.conversation_id,
        )
```

---

### 37. Device Triggers

**You:** Add device triggers for automations

**What you get:**
```python
# device_trigger.py
TRIGGER_TYPES = {"motion_detected", "button_pressed"}

async def async_get_triggers(hass, device_id):
    triggers = []
    for trigger_type in TRIGGER_TYPES:
        triggers.append({
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: trigger_type,
        })
    return triggers

async def async_attach_trigger(hass, config, action, trigger_info):
    event_config = {
        event_trigger.CONF_PLATFORM: "event",
        event_trigger.CONF_EVENT_TYPE: f"{DOMAIN}_{config[CONF_TYPE]}",
        event_trigger.CONF_EVENT_DATA: {
            CONF_DEVICE_ID: config[CONF_DEVICE_ID],
        },
    }
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info
    )
```

---

### 38. Energy Platform Support

**You:** Add energy platform support for power monitoring

**What you get:**
```python
# sensor.py
class EnergySensor(CoordinatorEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        return self.coordinator.data.get("total_energy")
```

```json
// manifest.json
{
  "quality_scale": "silver",
  "iot_class": "local_polling"
}
```

---

### 39. HACS Preparation

**You:** Make my Python custom integration HACS-compatible

**What you get:**
```json
// hacs.json
{
  "name": "My Integration",
  "homeassistant": "2024.1.0"
}
```

```yaml
# .github/workflows/validate.yml
name: Validate
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: home-assistant/actions/hassfest@master
      - uses: hacs/action@main
        with:
          category: integration
```

---

### 40. Pytest Fixtures

**You:** Create pytest fixtures for testing my integration

**What you get:**
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_api():
    with patch("custom_components.my_integration.MyAPI") as mock:
        api = mock.return_value
        api.get_data = AsyncMock(return_value={"temperature": 22.5})
        api.authenticate = AsyncMock(return_value=True)
        yield api

@pytest.fixture
def mock_config_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={"api_key": "test_key"},
        unique_id="test_unique_id",
    )
```

---

## Troubleshooting Examples

### 41. ConfigEntryNotReady

**You:** My integration shows "Retrying setup" - how to handle connection errors?

**What you get:**
```python
async def async_setup_entry(hass, entry):
    api = MyAPI(entry.data[CONF_API_KEY])
    try:
        await api.connect()
    except ConnectionError as err:
        raise ConfigEntryNotReady(f"Unable to connect: {err}") from err
```

---

### 42. Authentication Errors

**You:** How to trigger reauth when API returns 401?

**What you get:**
```python
async def _async_update_data(self):
    try:
        return await self.api.get_data()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed("Invalid credentials") from err
```

---

### 43. Entity Not Appearing

**You:** My entity isn't showing up in Home Assistant

**Checklist:**
- Check `unique_id` is set (required for entity registry)
- Verify platform is in `PLATFORMS` list
- Check `async_add_entities` is called
- Verify `native_value`/`is_on` returns valid value (not None during setup)

---

### 44. Coordinator Not Updating

**You:** My coordinator data isn't refreshing

**Checklist:**
```python
# Make sure to call first refresh
await coordinator.async_config_entry_first_refresh()

# After API calls, request refresh
await coordinator.async_request_refresh()

# Check update_interval is set
update_interval=timedelta(seconds=30)
```

---

### 45. Import Errors

**You:** Getting "ModuleNotFoundError" for my requirements

**What you get:**
```json
// manifest.json - ensure requirements are listed
{
  "requirements": ["aiohttp>=3.8.0", "my-api-library==1.0.0"]
}
```

Also verify: package name in requirements matches pip install name

---

### 46. State Not Updating

**You:** Entity state changes in API but not in HA

**What you get:**
```python
# Use @callback for state updates
@callback
def _handle_coordinator_update(self):
    self.async_write_ha_state()

# Or ensure entity extends CoordinatorEntity
class MySensor(CoordinatorEntity, SensorEntity):
    # CoordinatorEntity handles updates automatically
    pass
```

---

### 47. Memory Leaks

**You:** My integration is using too much memory

**Checklist:**
- Implement `async_unload_entry` properly
- Cancel all tasks in unload
- Remove event listeners
- Close API connections

```python
async def async_unload_entry(hass, entry):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.api.close()
    # Cancel any running tasks
    if coordinator._ws_task:
        coordinator._ws_task.cancel()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

---

### 48. Type Errors

**You:** Getting datetime serialization errors

**What you get:**
```python
# ❌ Wrong - datetime object
return {"timestamp": datetime.now()}

# ✅ Correct - ISO string
from homeassistant.util import dt as dt_util
return {"timestamp": dt_util.now().isoformat()}

# ✅ Or use dt_util for Home Assistant timezone
from homeassistant.util import dt as dt_util
now = dt_util.now()  # Returns timezone-aware datetime
```

---

### 49. Config Flow Errors

**You:** Config flow shows "Unknown error occurred"

**What you get:**
```python
# Always define error in strings.json
{
  "config": {
    "error": {
      "cannot_connect": "Failed to connect",
      "invalid_auth": "Invalid credentials",
      "unknown": "Unexpected error"  # Fallback
    }
  }
}

# And handle all exceptions
async def async_step_user(self, user_input=None):
    errors = {}
    try:
        await self._validate(user_input)
    except CannotConnect:
        errors["base"] = "cannot_connect"
    except InvalidAuth:
        errors["base"] = "invalid_auth"
    except Exception:
        _LOGGER.exception("Unexpected exception")
        errors["base"] = "unknown"
```

---

### 50. Debug Logging

**You:** How to add debug logging to my integration?

**What you get:**
```python
import logging

_LOGGER = logging.getLogger(__name__)

async def _async_update_data(self):
    _LOGGER.debug("Fetching data from API")
    data = await self.api.get_data()
    _LOGGER.debug("Received data: %s", data)
    return data
```

Enable in configuration.yaml:
```yaml
logger:
  logs:
    custom_components.my_integration: debug
```

---

## Tips and Tricks

### Effective Communication

| Instead of... | Say... |
|---------------|--------|
| "Help me with HA integration" | "Create a Python custom integration with config flow for API key auth" |
| "Fix my code" | "Fix this error: [paste traceback]" |
| "Add a sensor" | "Add a temperature sensor entity using DataUpdateCoordinator" |
| "It doesn't work" | "Entity shows unavailable - here's my code: [paste]" |

### Iterative Building

1. Start with config flow + one sensor
2. Test setup/unload works
3. Add more entity types
4. Add options flow
5. Add services if needed
6. Add tests
7. Prepare for HACS

### Using Templates

Ask: "Show me the polling-integration template" to get a starting point.

### Getting Architecture Advice

Ask: "Should I use polling or WebSocket for an API that supports both?"

### Reference Documentation

For detailed component documentation, see:

- [architecture.md](references/architecture.md) - Integration structure
- [config-flow.md](references/config-flow.md) - Config & Options flows
- [coordinator.md](references/coordinator.md) - DataUpdateCoordinator
- [entities.md](references/entities.md) - Entity platforms
- [entity-description.md](references/entity-description.md) - EntityDescription pattern
- [services-events.md](references/services-events.md) - Custom services
- [testing.md](references/testing.md) - pytest patterns
- [publishing.md](references/publishing.md) - HACS preparation
