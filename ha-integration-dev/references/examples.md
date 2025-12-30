# Complete Examples

Full integration examples for different patterns.

## Minimal Integration

Simplest possible integration with sensor.

### File Structure

```
custom_components/minimal_example/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── sensor.py
├── strings.json
└── translations/
    └── en.json
```

### manifest.json

```json
{
  "domain": "minimal_example",
  "name": "Minimal Example",
  "version": "1.0.0",
  "codeowners": ["@username"],
  "config_flow": true,
  "documentation": "https://github.com/user/minimal_example",
  "iot_class": "local_polling",
  "requirements": []
}
```

### const.py

```python
"""Constants for Minimal Example."""
DOMAIN = "minimal_example"
```

### __init__.py

```python
"""Minimal Example Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Minimal Example from config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

### config_flow.py

```python
"""Config flow for Minimal Example."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class MinimalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Minimal Example",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
```

### sensor.py

```python
"""Sensor platform for Minimal Example."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor."""
    async_add_entities([MinimalSensor(entry)])


class MinimalSensor(SensorEntity):
    """Minimal sensor."""

    _attr_has_entity_name = True
    _attr_name = "Example"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        self._attr_unique_id = f"{entry.entry_id}_example"

    @property
    def native_value(self) -> str:
        """Return state."""
        return "Hello World"
```

### strings.json

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Set up Minimal Example"
      }
    }
  }
}
```

---

## Polling Integration

Integration with DataUpdateCoordinator for API polling.

### File Structure

```
custom_components/polling_example/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── coordinator.py
├── entity.py
├── sensor.py
└── strings.json
```

### const.py

```python
"""Constants."""
from datetime import timedelta

DOMAIN = "polling_example"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)
```

### coordinator.py

```python
"""Data coordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PollingCoordinator(DataUpdateCoordinator[dict]):
    """Polling coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self._session = async_get_clientsession(hass)
        self._host = entry.data[CONF_HOST]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data."""
        try:
            async with self._session.get(f"http://{self._host}/api/status") as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
```

### __init__.py

```python
"""Polling Example Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PollingCoordinator

PLATFORMS = [Platform.SENSOR]

type PollingConfigEntry = ConfigEntry[PollingCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: PollingConfigEntry) -> bool:
    """Set up from config entry."""
    coordinator = PollingCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PollingConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

### entity.py

```python
"""Base entity."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PollingCoordinator


class PollingEntity(CoordinatorEntity[PollingCoordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PollingCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Polling Device",
            manufacturer="Example Corp",
        )
```

### sensor.py

```python
"""Sensor platform."""
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

from .coordinator import PollingCoordinator
from .entity import PollingEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: PollingCoordinator = entry.runtime_data

    async_add_entities([
        TemperatureSensor(coordinator),
        HumiditySensor(coordinator),
    ])


class TemperatureSensor(PollingEntity, SensorEntity):
    """Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "Temperature"

    def __init__(self, coordinator: PollingCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_temperature"

    @property
    def native_value(self) -> float | None:
        """Return temperature."""
        return self.coordinator.data.get("temperature")


class HumiditySensor(PollingEntity, SensorEntity):
    """Humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_name = "Humidity"

    def __init__(self, coordinator: PollingCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_humidity"

    @property
    def native_value(self) -> float | None:
        """Return humidity."""
        return self.coordinator.data.get("humidity")
```

---

## Push Integration (WebSocket)

Integration with WebSocket for real-time updates.

### coordinator.py

```python
"""WebSocket coordinator."""
from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PushCoordinator(DataUpdateCoordinator[dict]):
    """WebSocket coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # No polling, push only
        )

        self._session = async_get_clientsession(hass)
        self._host = entry.data[CONF_HOST]
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._listen_task: asyncio.Task | None = None

    async def async_setup(self) -> None:
        """Set up WebSocket connection."""
        url = f"ws://{self._host}/ws"
        self._ws = await self._session.ws_connect(url)
        self._listen_task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        """Listen for messages."""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    self.async_set_updated_data(data)
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break
        except asyncio.CancelledError:
            pass
        except Exception as err:
            _LOGGER.error("WebSocket error: %s", err)

    async def async_shutdown(self) -> None:
        """Shut down coordinator."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            await self._ws.close()
```

### __init__.py

```python
"""Push Example Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PushCoordinator

PLATFORMS = [Platform.SENSOR]

type PushConfigEntry = ConfigEntry[PushCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: PushConfigEntry) -> bool:
    """Set up from config entry."""
    coordinator = PushCoordinator(hass, entry)
    await coordinator.async_setup()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PushConfigEntry) -> bool:
    """Unload config entry."""
    await entry.runtime_data.async_shutdown()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

---

## Multiple Devices Integration

Integration managing multiple devices from one hub.

### coordinator.py

```python
"""Multi-device coordinator."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import MyApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceData:
    """Device data."""

    name: str
    online: bool
    temperature: float | None
    humidity: float | None


class MultiDeviceCoordinator(DataUpdateCoordinator[dict[str, DeviceData]]):
    """Coordinator for multiple devices."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: MyApiClient
    ) -> None:
        """Initialize."""
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict[str, DeviceData]:
        """Fetch all devices."""
        devices = await self.client.async_get_devices()

        return {
            device["id"]: DeviceData(
                name=device["name"],
                online=device["online"],
                temperature=device.get("temperature"),
                humidity=device.get("humidity"),
            )
            for device in devices
        }
```

### sensor.py

```python
"""Sensor platform for multiple devices."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MultiDeviceCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for all devices."""
    coordinator: MultiDeviceCoordinator = entry.runtime_data

    entities = []
    for device_id, device_data in coordinator.data.items():
        entities.extend([
            DeviceTemperatureSensor(coordinator, device_id),
            DeviceHumiditySensor(coordinator, device_id),
        ])

    async_add_entities(entities)


class DeviceTemperatureSensor(CoordinatorEntity[MultiDeviceCoordinator], SensorEntity):
    """Temperature sensor for a device."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True
    _attr_name = "Temperature"

    def __init__(self, coordinator: MultiDeviceCoordinator, device_id: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id

        device = coordinator.data[device_id]
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device.name,
            manufacturer="Example Corp",
            via_device=(DOMAIN, coordinator.config_entry.entry_id),
        )

    @property
    def native_value(self) -> float | None:
        """Return temperature."""
        if device := self.coordinator.data.get(self._device_id):
            return device.temperature
        return None

    @property
    def available(self) -> bool:
        """Return availability."""
        if not self.coordinator.last_update_success:
            return False
        if device := self.coordinator.data.get(self._device_id):
            return device.online
        return False
```

---

## Integration with Services

### __init__.py

```python
"""Integration with custom services."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import MyCoordinator

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    coordinator = MyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register services
    await async_setup_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services."""

    async def handle_refresh(call: ServiceCall) -> None:
        """Handle refresh all."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.async_request_refresh()

    async def handle_set_mode(call: ServiceCall) -> None:
        """Handle set mode."""
        device_id = call.data["device_id"]
        mode = call.data["mode"]

        for coordinator in hass.data[DOMAIN].values():
            await coordinator.client.async_set_mode(device_id, mode)
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "refresh",
        handle_refresh,
    )

    hass.services.async_register(
        DOMAIN,
        "set_mode",
        handle_set_mode,
        schema=vol.Schema({
            vol.Required("device_id"): cv.string,
            vol.Required("mode"): vol.In(["auto", "manual", "eco"]),
        }),
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

        # Remove services if last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "refresh")
            hass.services.async_remove(DOMAIN, "set_mode")

    return unload_ok
```

### services.yaml

```yaml
refresh:
  name: Refresh All
  description: Refresh data from all devices

set_mode:
  name: Set Mode
  description: Set device operating mode
  fields:
    device_id:
      name: Device ID
      required: true
      selector:
        text:
    mode:
      name: Mode
      required: true
      selector:
        select:
          options:
            - auto
            - manual
            - eco
```

---

For more patterns, see the reference files:
- `architecture.md` - Integration structure
- `config-flow.md` - Configuration flows
- `entities.md` - Entity platforms
- `coordinator.md` - Data coordination
