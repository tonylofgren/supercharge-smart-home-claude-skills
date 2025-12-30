# DataUpdateCoordinator

Centralized data fetching for Home Assistant integrations.

## Overview

`DataUpdateCoordinator` handles:
- Scheduled polling
- Error handling with retry
- Rate limiting
- Sharing data across entities
- Automatic entity updates

---

## Basic Coordinator

```python
"""Coordinator for My Integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator[dict]):
    """Data update coordinator."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: MyApiClient,
    ) -> None:
        """Initialize coordinator."""
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            return await self.client.async_get_data()
        except AuthenticationError as err:
            # Triggers reauth flow
            raise ConfigEntryAuthFailed("Invalid credentials") from err
        except ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
```

---

## Usage in __init__.py

```python
from .coordinator import MyCoordinator

type MyConfigEntry = ConfigEntry[MyCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up integration."""
    client = MyApiClient(entry.data[CONF_HOST])

    coordinator = MyCoordinator(hass, entry, client)

    # Fetch initial data - raises ConfigEntryNotReady on failure
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
```

---

## Usage in Entities

```python
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Sensor entity."""

    def __init__(self, coordinator: MyCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = "my_sensor"

    @property
    def native_value(self) -> float | None:
        """Return state from coordinator data."""
        return self.coordinator.data.get("temperature")
```

---

## Error Handling

### Exception Types

| Exception | Effect |
|-----------|--------|
| `UpdateFailed` | Log error, retry next interval |
| `ConfigEntryAuthFailed` | Trigger reauth flow |
| `ConfigEntryNotReady` | Retry setup with backoff |

### Complete Error Handling

```python
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed


class MyCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator with complete error handling."""

    async def _async_update_data(self) -> dict:
        """Fetch data with error handling."""
        try:
            async with asyncio.timeout(30):
                return await self.client.async_get_data()

        except AuthenticationError as err:
            # Auth failed - trigger reauth
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="auth_failed",
            ) from err

        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout fetching data") from err

        except ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

        except ValueError as err:
            # Data parsing error
            _LOGGER.warning("Invalid data received: %s", err)
            # Return last known good data
            if self.data:
                return self.data
            raise UpdateFailed("Invalid data and no cached data") from err
```

---

## Typed Data

### Using TypedDict

```python
from typing import TypedDict


class DeviceData(TypedDict):
    """Device data structure."""

    temperature: float
    humidity: float
    battery: int
    online: bool


class MyCoordinator(DataUpdateCoordinator[DeviceData]):
    """Coordinator with typed data."""

    async def _async_update_data(self) -> DeviceData:
        """Fetch typed data."""
        raw = await self.client.async_get_data()
        return DeviceData(
            temperature=raw["temp"],
            humidity=raw["hum"],
            battery=raw["bat"],
            online=raw["status"] == "online",
        )
```

### Using Dataclass

```python
from dataclasses import dataclass


@dataclass
class DeviceData:
    """Device data."""

    temperature: float
    humidity: float
    battery: int
    online: bool


class MyCoordinator(DataUpdateCoordinator[DeviceData]):
    """Coordinator with dataclass."""

    async def _async_update_data(self) -> DeviceData:
        """Fetch data."""
        raw = await self.client.async_get_data()
        return DeviceData(
            temperature=raw["temp"],
            humidity=raw["hum"],
            battery=raw["bat"],
            online=raw["status"] == "online",
        )
```

---

## Multiple Devices

### Dictionary of Devices

```python
class MultiDeviceCoordinator(DataUpdateCoordinator[dict[str, DeviceData]]):
    """Coordinator for multiple devices."""

    async def _async_update_data(self) -> dict[str, DeviceData]:
        """Fetch all devices."""
        devices = await self.client.async_get_all_devices()
        return {
            device["id"]: DeviceData(
                temperature=device["temp"],
                humidity=device["hum"],
                battery=device["bat"],
                online=device["online"],
            )
            for device in devices
        }


# Entity usage
class MySensor(CoordinatorEntity[MultiDeviceCoordinator], SensorEntity):
    """Sensor for specific device."""

    def __init__(self, coordinator, device_id: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def native_value(self) -> float | None:
        """Return value for this device."""
        if device := self.coordinator.data.get(self._device_id):
            return device.temperature
        return None

    @property
    def available(self) -> bool:
        """Return availability."""
        if not self.coordinator.last_update_success:
            return False
        device = self.coordinator.data.get(self._device_id)
        return device is not None and device.online
```

---

## Dynamic Update Interval

```python
class AdaptiveCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator with dynamic interval."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )
        self._fast_interval = timedelta(seconds=10)
        self._slow_interval = timedelta(seconds=300)

    async def _async_update_data(self) -> dict:
        """Fetch data and adjust interval."""
        data = await self.client.async_get_data()

        # Adjust interval based on activity
        if data.get("active"):
            self.update_interval = self._fast_interval
        else:
            self.update_interval = self._slow_interval

        return data
```

---

## Rate Limiting

### Using asyncio.Semaphore

```python
class RateLimitedCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator with rate limiting."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        # Limit concurrent requests
        self._semaphore = asyncio.Semaphore(3)

    async def _async_update_data(self) -> dict:
        """Fetch data with rate limiting."""
        async with self._semaphore:
            return await self.client.async_get_data()
```

### Debounced Refresh

```python
from homeassistant.helpers.debounce import Debouncer


class DebouncedCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator with debounced refresh."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=5.0,  # Minimum seconds between refreshes
                immediate=True,
            ),
        )
```

---

## Manual Refresh

### Refresh After Action

```python
class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Sensor with actions."""

    async def async_custom_action(self) -> None:
        """Execute action and refresh."""
        await self.coordinator.client.async_do_something()

        # Request coordinator refresh
        await self.coordinator.async_request_refresh()


class MySwitch(CoordinatorEntity[MyCoordinator], SwitchEntity):
    """Switch entity."""

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on."""
        await self.coordinator.client.async_set_power(True)

        # Optimistic update
        self._attr_is_on = True
        self.async_write_ha_state()

        # Schedule refresh for confirmed state
        await self.coordinator.async_request_refresh()
```

### Force Immediate Update

```python
# Request refresh (respects debouncer)
await coordinator.async_request_refresh()

# Force immediate refresh (ignores debouncer)
await coordinator.async_refresh()
```

---

## Refresh Listeners

```python
class MyCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator with refresh listener."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data."""
        return await self.client.async_get_data()


# Add listener for external refresh triggers
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    coordinator = MyCoordinator(hass, entry)

    async def handle_webhook(data: dict) -> None:
        """Handle webhook push update."""
        coordinator.async_set_updated_data(data)

    # Register webhook handler
    entry.async_on_unload(
        async_register_webhook(hass, handle_webhook)
    )

    return True
```

---

## Push Updates

### With Websocket

```python
class PushCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for push-based updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # No polling - updates come via push
            update_interval=None,
        )
        self._connection: WebSocketConnection | None = None

    async def async_setup(self) -> None:
        """Set up websocket connection."""
        self._connection = await self.client.async_connect_websocket()
        self._connection.register_callback(self._handle_update)

    def _handle_update(self, data: dict) -> None:
        """Handle pushed data."""
        self.async_set_updated_data(data)

    async def async_shutdown(self) -> None:
        """Shut down connection."""
        if self._connection:
            await self._connection.async_disconnect()
```

### Hybrid (Push + Polling Fallback)

```python
class HybridCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator with push and polling fallback."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # Poll as fallback
            update_interval=timedelta(minutes=5),
        )

    async def async_setup(self) -> None:
        """Set up with push updates."""
        try:
            await self._setup_websocket()
            # Disable polling when push is active
            self.update_interval = None
        except ConnectionError:
            _LOGGER.warning("Push updates unavailable, using polling")
```

---

## Multiple Coordinators

```python
# Different coordinators for different data types/intervals


class DeviceCoordinator(DataUpdateCoordinator[dict]):
    """Fast updates for device state."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_devices",
            update_interval=timedelta(seconds=30),
        )


class StatsCoordinator(DataUpdateCoordinator[dict]):
    """Slow updates for statistics."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_stats",
            update_interval=timedelta(hours=1),
        )


# Store both in runtime data
@dataclass
class RuntimeData:
    """Runtime data."""

    device_coordinator: DeviceCoordinator
    stats_coordinator: StatsCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with multiple coordinators."""
    device_coordinator = DeviceCoordinator(hass)
    stats_coordinator = StatsCoordinator(hass)

    await device_coordinator.async_config_entry_first_refresh()
    await stats_coordinator.async_config_entry_first_refresh()

    entry.runtime_data = RuntimeData(
        device_coordinator=device_coordinator,
        stats_coordinator=stats_coordinator,
    )

    return True
```

---

## Initial Data Fetch

### async_config_entry_first_refresh

```python
# Recommended - raises ConfigEntryNotReady on failure
await coordinator.async_config_entry_first_refresh()
```

### Manual First Refresh

```python
# Alternative with custom handling
try:
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("Initial data fetch failed")
except UpdateFailed as err:
    raise ConfigEntryNotReady from err
```

---

## Testing Coordinators

```python
"""Test coordinator."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.my_integration.coordinator import MyCoordinator


async def test_coordinator_update(hass: HomeAssistant) -> None:
    """Test coordinator data update."""
    mock_client = AsyncMock()
    mock_client.async_get_data.return_value = {"temperature": 22.5}

    coordinator = MyCoordinator(hass, mock_entry, mock_client)
    await coordinator.async_config_entry_first_refresh()

    assert coordinator.data["temperature"] == 22.5


async def test_coordinator_error(hass: HomeAssistant) -> None:
    """Test coordinator error handling."""
    mock_client = AsyncMock()
    mock_client.async_get_data.side_effect = ConnectionError("Failed")

    coordinator = MyCoordinator(hass, mock_entry, mock_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
```

---

## Best Practices

### DO

- Use `DataUpdateCoordinator` for all polling integrations
- Raise `ConfigEntryAuthFailed` for auth errors
- Raise `UpdateFailed` for transient errors
- Use `async_config_entry_first_refresh` for initial fetch
- Type your coordinator data
- Use debouncer for frequent refresh requests

### DON'T

- Poll in entity properties
- Create multiple instances for same data
- Ignore `last_update_success` in entity availability
- Use short intervals without rate limiting
- Block in `_async_update_data`

---

For API integration patterns, see `api-integration.md`.
For entity implementation, see `entities.md`.
