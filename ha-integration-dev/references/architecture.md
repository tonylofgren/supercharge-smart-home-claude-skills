# Integration Architecture

Complete reference for Home Assistant custom integration structure.

## Directory Structure

```
custom_components/my_integration/
├── manifest.json           # Required: Metadata and dependencies
├── __init__.py             # Required: Setup and config entry handling
├── const.py                # Constants, DOMAIN definition
├── config_flow.py          # UI-based configuration
├── coordinator.py          # Data fetching (DataUpdateCoordinator)
├── entity.py               # Base entity class (optional)
├── sensor.py               # Entity platform
├── switch.py               # Entity platform
├── binary_sensor.py        # Entity platform
├── strings.json            # UI strings for config flow
├── translations/           # Localization files
│   ├── en.json
│   └── sv.json
├── services.yaml           # Service definitions (optional)
└── diagnostics.py          # Diagnostic data (optional)
```

---

## manifest.json

**Required file.** Defines integration metadata.

### Complete Example

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "version": "1.0.0",
  "codeowners": ["@username"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/user/my_integration",
  "iot_class": "cloud_polling",
  "requirements": ["aiohttp>=3.8.0"],
  "integration_type": "hub"
}
```

### All Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `domain` | Yes | Unique identifier, lowercase with underscores |
| `name` | Yes | Human-readable name |
| `version` | Yes (HACS) | Semantic version (1.0.0) |
| `codeowners` | No | GitHub usernames for notifications |
| `config_flow` | No | `true` if UI configuration supported |
| `dependencies` | No | Other integrations that must load first |
| `documentation` | Yes | URL to documentation |
| `iot_class` | Yes | How integration communicates |
| `requirements` | No | Python packages to install |
| `integration_type` | No | Type of integration |
| `after_dependencies` | No | Load after these, but don't require |
| `quality_scale` | No | Core only: platinum, gold, silver, bronze |
| `loggers` | No | Logger names for frontend filtering |
| `bluetooth` | No | Bluetooth matcher configuration |
| `dhcp` | No | DHCP discovery configuration |
| `homekit` | No | HomeKit discovery configuration |
| `ssdp` | No | SSDP/UPnP discovery configuration |
| `usb` | No | USB discovery configuration |
| `zeroconf` | No | Zeroconf/mDNS discovery configuration |

### iot_class Values

| Value | Description | Example |
|-------|-------------|---------|
| `cloud_polling` | Cloud API with polling | Weather APIs |
| `cloud_push` | Cloud API with push updates | Cloud webhooks |
| `local_polling` | Local device with polling | Local HTTP APIs |
| `local_push` | Local device with push | Websocket devices |
| `calculated` | No external communication | Template sensors |
| `assumed_state` | State can't be read | IR blasters |

### integration_type Values

| Value | Description |
|-------|-------------|
| `hub` | Connects to device/service creating devices/entities |
| `device` | Single device integration |
| `service` | Background service (no entities) |
| `entity` | Entity component platform |
| `system` | Core Home Assistant functionality |
| `hardware` | Physical hardware interface |

---

## __init__.py

**Required file.** Handles setup and config entry lifecycle.

### Minimal Example (Config Entry)

```python
"""My Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up My Integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Store any runtime data
    hass.data[DOMAIN][entry.entry_id] = {
        "client": None,  # API client, coordinator, etc.
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
```

### With DataUpdateCoordinator

```python
"""My Integration with coordinator."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MyCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type MyConfigEntry = ConfigEntry[MyCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up My Integration from a config entry."""
    coordinator = MyCoordinator(hass, entry)

    # Fetch initial data - raises ConfigEntryNotReady on failure
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in entry.runtime_data (HA 2024.1+)
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

### With API Client

```python
"""My Integration with API client."""
from __future__ import annotations

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .api import MyApiClient, AuthenticationError, ConnectionError

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up My Integration from a config entry."""
    session = async_get_clientsession(hass)
    client = MyApiClient(
        session=session,
        api_key=entry.data[CONF_API_KEY],
    )

    try:
        await client.async_validate_connection()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed from err
    except ConnectionError as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
```

### Entry Lifecycle Functions

| Function | When Called | Purpose |
|----------|-------------|---------|
| `async_setup_entry` | Entry loaded | Initialize integration |
| `async_unload_entry` | Entry unloaded | Clean up resources |
| `async_remove_entry` | Entry deleted | Remove persistent data |
| `async_migrate_entry` | Version mismatch | Migrate config data |
| `async_setup` | YAML config (legacy) | Setup from configuration.yaml |

### Config Entry Migration

```python
async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry data to new version."""
    if entry.version == 1:
        # Migrate from version 1 to 2
        new_data = {**entry.data}
        new_data["new_key"] = entry.data.get("old_key", "default")

        hass.config_entries.async_update_entry(
            entry,
            data=new_data,
            version=2,
        )

    return True
```

---

## const.py

**Constants file.** Centralizes all constants.

```python
"""Constants for My Integration."""
from __future__ import annotations

from typing import Final

# Domain
DOMAIN: Final = "my_integration"

# Config keys
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_DEVICE_ID: Final = "device_id"

# Defaults
DEFAULT_UPDATE_INTERVAL: Final = 60  # seconds
DEFAULT_NAME: Final = "My Device"

# API
API_BASE_URL: Final = "https://api.example.com/v1"
API_TIMEOUT: Final = 30

# Platforms
PLATFORMS: Final = ["sensor", "switch", "binary_sensor"]

# Attributes
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_ERROR_COUNT: Final = "error_count"
```

---

## Data Storage Patterns

### Using hass.data (Legacy)

```python
# Store data per config entry
hass.data.setdefault(DOMAIN, {})
hass.data[DOMAIN][entry.entry_id] = {
    "client": client,
    "coordinator": coordinator,
}

# Access in entities
client = hass.data[DOMAIN][entry.entry_id]["client"]

# Clean up on unload
hass.data[DOMAIN].pop(entry.entry_id)
```

### Using entry.runtime_data (HA 2024.1+)

```python
# Define typed config entry
from homeassistant.config_entries import ConfigEntry
from .coordinator import MyCoordinator

type MyConfigEntry = ConfigEntry[MyCoordinator]

# Store coordinator directly
entry.runtime_data = coordinator

# Access in entities (type-safe)
coordinator = entry.runtime_data
```

### Choosing Storage Method

| Method | When to Use |
|--------|-------------|
| `entry.runtime_data` | Single object (coordinator or client) |
| `hass.data[DOMAIN]` | Multiple objects or shared state |
| `entry.data` | Persistent config (read-only) |
| `entry.options` | User-adjustable settings |

---

## Platform Setup

### Entity Platform File (sensor.py)

```python
"""Sensor platform for My Integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: MyCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        MyTemperatureSensor(coordinator, entry),
        MyHumiditySensor(coordinator, entry),
    ]

    async_add_entities(entities)


class MyTemperatureSensor(SensorEntity):
    """Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True
    _attr_name = "Temperature"

    def __init__(
        self,
        coordinator: MyCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("temperature")
```

---

## Dependencies

### Python Package Dependencies (requirements)

```json
{
  "requirements": ["aiohttp>=3.8.0", "my-api-lib==1.2.3"]
}
```

- Packages installed automatically
- Pin versions for stability
- Use async libraries (aiohttp, not requests)

### Integration Dependencies (dependencies)

```json
{
  "dependencies": ["http", "webhook"]
}
```

- Required integrations that must load first
- Integration fails if dependency unavailable

### Soft Dependencies (after_dependencies)

```json
{
  "after_dependencies": ["recorder", "cloud"]
}
```

- Load after these if present
- Don't require them

---

## Common Patterns

### Reloading Config Entry

```python
# Listen for options updates
entry.async_on_unload(entry.add_update_listener(async_reload_entry))

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
```

### Service Registration in Setup

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    # ... setup code ...

    async def handle_refresh(call: ServiceCall) -> None:
        """Handle refresh service call."""
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "refresh",
        handle_refresh,
    )

    return True
```

### Cleanup on Unload

```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Clean up API client
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.async_close()

        # Remove data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
```

---

## Type Hints

### Common Imports

```python
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
```

### Typed ConfigEntry with runtime_data (HA 2024.1+)

The modern approach stores runtime data directly in `entry.runtime_data` with type safety.

#### Simple Pattern (Single Coordinator)

```python
# __init__.py
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import MyCoordinator

# Define typed config entry
type MyConfigEntry = ConfigEntry[MyCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up from config entry."""
    coordinator = MyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Store in runtime_data (type-safe)
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


# sensor.py - Access runtime_data
async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyConfigEntry,  # Use typed entry
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data  # Type: MyCoordinator
    async_add_entities([MySensor(coordinator, entry)])
```

#### Complex Pattern (Multiple Objects)

```python
# __init__.py
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import MyApiClient
from .coordinator import MyCoordinator


@dataclass
class MyRuntimeData:
    """Runtime data for My Integration."""

    coordinator: MyCoordinator
    client: MyApiClient
    hub_version: str


type MyConfigEntry = ConfigEntry[MyRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up from config entry."""
    client = MyApiClient(entry.data["host"], entry.data["api_key"])
    await client.async_connect()

    coordinator = MyCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    # Store all runtime data
    entry.runtime_data = MyRuntimeData(
        coordinator=coordinator,
        client=client,
        hub_version=await client.async_get_version(),
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Unload config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.client.async_disconnect()
    return unload_ok
```

### TypedDict for Data Structures

Use TypedDict for coordinator data and API responses:

```python
from typing import TypedDict, NotRequired


class DeviceData(TypedDict):
    """Device data from API."""

    id: str
    name: str
    online: bool
    temperature: float | None
    humidity: float | None
    firmware: str
    last_seen: str


class HubData(TypedDict):
    """Hub data structure."""

    devices: dict[str, DeviceData]
    hub_name: str
    hub_version: str
    connected: bool


class CoordinatorData(TypedDict):
    """Data returned by coordinator."""

    hub: HubData
    last_update: str
    error_count: NotRequired[int]  # Optional field
```

#### Using TypedDict in Coordinator

```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .types import CoordinatorData


class MyCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Coordinator with typed data."""

    async def _async_update_data(self) -> CoordinatorData:
        """Fetch data from API."""
        hub_data = await self.client.async_get_hub()
        devices = await self.client.async_get_devices()

        return CoordinatorData(
            hub={
                "devices": {d["id"]: d for d in devices},
                "hub_name": hub_data["name"],
                "hub_version": hub_data["version"],
                "connected": True,
            },
            last_update=datetime.now().isoformat(),
        )


# In entities - data is typed
class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    @property
    def native_value(self) -> float | None:
        # self.coordinator.data is CoordinatorData
        device = self.coordinator.data["hub"]["devices"].get(self._device_id)
        return device["temperature"] if device else None
```

### Config Entry Data Types

```python
from typing import TypedDict, NotRequired


class MyConfigData(TypedDict):
    """Config entry data structure."""

    host: str
    api_key: str
    device_id: str
    port: NotRequired[int]


class MyOptionsData(TypedDict):
    """Config entry options structure."""

    scan_interval: int
    enable_notifications: bool


# Usage
def get_host(entry: ConfigEntry) -> str:
    data: MyConfigData = entry.data  # Type hint for IDE
    return data["host"]
```

---

## Best Practices

### DO

- Use `async_forward_entry_setups` (not deprecated `async_setup_platforms`)
- Raise `ConfigEntryNotReady` for connection issues
- Raise `ConfigEntryAuthFailed` for auth issues (triggers reauth)
- Store runtime data in `entry.runtime_data` or `hass.data[DOMAIN]`
- Clean up all resources in `async_unload_entry`
- Use type hints everywhere
- Pin package versions in requirements

### DON'T

- Use blocking I/O (use aiohttp, not requests)
- Store credentials in hass.data (keep in entry.data)
- Ignore `async_unload_entry` return value
- Create entities in `__init__.py` (use platform files)
- Use `async_setup` for config entries (only for YAML)
- Catch and ignore exceptions silently

---

## Error Handling

### Setup Errors

```python
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    ConfigEntryError,
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    try:
        await client.connect()
    except AuthError as err:
        # Triggers reauth flow
        raise ConfigEntryAuthFailed("Invalid credentials") from err
    except ConnectionError as err:
        # Retries setup later
        raise ConfigEntryNotReady("Cannot connect") from err
    except ValueError as err:
        # Permanent failure
        raise ConfigEntryError("Invalid configuration") from err
```

### Exception Hierarchy

| Exception | Behavior |
|-----------|----------|
| `ConfigEntryNotReady` | Retry setup with backoff |
| `ConfigEntryAuthFailed` | Trigger reauth flow |
| `ConfigEntryError` | Mark entry as failed |
| Other exceptions | Mark entry as failed |

---

## Version Compatibility

### HA Version Checks

```python
from homeassistant.const import __version__ as HA_VERSION
from packaging.version import Version

if Version(HA_VERSION) >= Version("2024.1.0"):
    # Use new API
    entry.runtime_data = coordinator
else:
    # Use legacy API
    hass.data[DOMAIN][entry.entry_id] = coordinator
```

### Deprecation Handling

| Deprecated | Replacement | Since |
|------------|-------------|-------|
| `async_setup_platforms` | `async_forward_entry_setups` | 2022.8 |
| `hass.data[DOMAIN][entry.entry_id]` | `entry.runtime_data` | 2024.1 |
| `TEMP_CELSIUS` | `UnitOfTemperature.CELSIUS` | 2022.11 |

---

For config flow implementation, see `config-flow.md`.
For entity platforms, see `entities.md`.
For DataUpdateCoordinator, see `coordinator.md`.
