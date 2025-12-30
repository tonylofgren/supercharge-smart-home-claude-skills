# Diagnostics & System Health

Debug information and system health reporting for Home Assistant integrations.

## Overview

Diagnostics provide debug information when users report issues. System health shows integration status in Settings → System → Repairs.

---

## Diagnostics

### Basic diagnostics.py

```python
"""Diagnostics support for My Integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# Keys to redact from diagnostic output
TO_REDACT = {
    "api_key",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "username",
    "email",
    "serial_number",
    "mac_address",
    "latitude",
    "longitude",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
            "update_interval": str(coordinator.update_interval),
        },
        "data": async_redact_data(coordinator.data, TO_REDACT),
    }
```

### Device-Specific Diagnostics

```python
"""Diagnostics with device support."""
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN

TO_REDACT = {"api_key", "password", "token", "mac", "serial"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "hub": {
            "connected": hub.connected,
            "firmware_version": hub.firmware_version,
            "device_count": len(hub.devices),
        },
        "devices": {
            device_id: async_redact_data(device.as_dict(), TO_REDACT)
            for device_id, device in hub.devices.items()
        },
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a specific device."""
    hub = hass.data[DOMAIN][entry.entry_id]

    # Find device by identifier
    device_id = next(
        (id for domain, id in device.identifiers if domain == DOMAIN),
        None
    )

    if device_id and device_id in hub.devices:
        device_data = hub.devices[device_id]
        return {
            "device": {
                "id": device_id,
                "name": device.name,
                "model": device.model,
                "sw_version": device.sw_version,
            },
            "data": async_redact_data(device_data.as_dict(), TO_REDACT),
            "raw_state": async_redact_data(device_data.raw_state, TO_REDACT),
        }

    return {"error": "Device not found"}
```

### Redaction Patterns

```python
from homeassistant.components.diagnostics import async_redact_data

# Redact specific keys
TO_REDACT = {"password", "token", "api_key"}
redacted = async_redact_data({"password": "secret", "host": "192.168.1.1"}, TO_REDACT)
# Result: {"password": "**REDACTED**", "host": "192.168.1.1"}

# Nested redaction
nested_data = {
    "auth": {"token": "abc123", "user": "admin"},
    "config": {"host": "192.168.1.1"},
}
redacted = async_redact_data(nested_data, TO_REDACT)
# Result: {"auth": {"token": "**REDACTED**", "user": "admin"}, "config": {...}}

# List redaction
list_data = [
    {"name": "Device 1", "token": "xyz"},
    {"name": "Device 2", "token": "abc"},
]
redacted = async_redact_data(list_data, TO_REDACT)
# Each dict in list is redacted
```

### Custom Redaction

```python
from homeassistant.components.diagnostics import async_redact_data

TO_REDACT = {"password", "token"}


def redact_ip_address(data: dict) -> dict:
    """Redact IP addresses from data."""
    import re

    def redact_value(value):
        if isinstance(value, str):
            # Redact IPv4 addresses
            return re.sub(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
                "x.x.x.x",
                value
            )
        elif isinstance(value, dict):
            return {k: redact_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [redact_value(v) for v in value]
        return value

    return redact_value(data)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics with custom redaction."""
    data = get_diagnostic_data()

    # Standard redaction
    data = async_redact_data(data, TO_REDACT)

    # Custom IP redaction
    data = redact_ip_address(data)

    return data
```

---

## System Health

### Basic System Health

```python
"""System health for My Integration."""
from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass: HomeAssistant) -> dict[str, str]:
    """Get system health info."""
    info: dict[str, str] = {}

    # Check if integration is loaded
    if DOMAIN not in hass.data:
        info["status"] = "Not loaded"
        return info

    # Get hub status
    for entry_id, hub in hass.data[DOMAIN].items():
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry:
            info[f"{entry.title} status"] = "Connected" if hub.connected else "Disconnected"
            info[f"{entry.title} devices"] = str(len(hub.devices))

    return info
```

### manifest.json for System Health

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "after_dependencies": ["system_health"]
}
```

### System Health with API Check

```python
"""System health with external API check."""
from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, API_URL


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info, "/config/integrations/integration/my_integration")


async def system_health_info(hass: HomeAssistant) -> dict[str, str | bool]:
    """Get system health info."""
    info: dict[str, str | bool] = {
        "api_endpoint": system_health.async_check_can_reach_url(hass, API_URL),
    }

    if DOMAIN in hass.data:
        for entry_id, data in hass.data[DOMAIN].items():
            entry = hass.config_entries.async_get_entry(entry_id)
            coordinator = data.get("coordinator")

            if entry and coordinator:
                info[entry.title] = (
                    "OK" if coordinator.last_update_success
                    else f"Error: {coordinator.last_exception}"
                )

    return info
```

---

## Debug Logging

### Configure Logger in __init__.py

```python
"""My Integration."""
import logging

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    _LOGGER.debug("Setting up entry: %s", entry.entry_id)

    try:
        client = MyApiClient(entry.data["host"])
        await client.async_connect()
        _LOGGER.info("Connected to %s", entry.data["host"])
    except Exception as err:
        _LOGGER.error("Failed to connect: %s", err, exc_info=True)
        raise ConfigEntryNotReady from err

    return True
```

### Enable Debug Logging

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.my_integration: debug
```

### Structured Logging

```python
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator):
    """Coordinator with structured logging."""

    async def _async_update_data(self) -> dict:
        """Fetch data with logging."""
        _LOGGER.debug(
            "Fetching data from API",
            extra={
                "host": self.host,
                "update_count": self._update_count,
            }
        )

        try:
            data = await self.client.async_get_data()
            _LOGGER.debug(
                "Received %d entities",
                len(data.get("entities", [])),
            )
            return data
        except AuthenticationError as err:
            _LOGGER.error(
                "Authentication failed for %s: %s",
                self.host,
                err,
            )
            raise
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching data")
            raise
```

---

## Complete Example

### diagnostics.py

```python
"""Diagnostics for My Integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN

TO_REDACT = {
    "api_key",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    diagnostics = {
        "entry": {
            "version": entry.version,
            "title": entry.title,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "client": {
            "connected": client.connected,
            "api_version": client.api_version,
            "response_time_ms": client.last_response_time,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update": str(coordinator.last_update_success_time),
            "update_interval": str(coordinator.update_interval),
            "update_failures": coordinator.update_failures,
        },
        "devices": [],
    }

    # Add device info
    if coordinator.data:
        for device_id, device_data in coordinator.data.get("devices", {}).items():
            diagnostics["devices"].append(
                async_redact_data(
                    {
                        "id": device_id,
                        "name": device_data.get("name"),
                        "model": device_data.get("model"),
                        "online": device_data.get("online"),
                        "last_seen": device_data.get("last_seen"),
                        "state": device_data.get("state"),
                    },
                    TO_REDACT,
                )
            )

    return diagnostics


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for specific device."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Find device ID
    device_id = next(
        (id for domain, id in device.identifiers if domain == DOMAIN),
        None,
    )

    if not device_id:
        return {"error": "Device ID not found"}

    device_data = coordinator.data.get("devices", {}).get(device_id, {})

    return {
        "device_entry": {
            "id": device.id,
            "name": device.name,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "sw_version": device.sw_version,
        },
        "data": async_redact_data(device_data, TO_REDACT),
    }
```

### system_health.py

```python
"""System health for My Integration."""
from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, API_ENDPOINT


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health."""
    register.async_register_info(system_health_info)


async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get system health info."""
    info: dict[str, Any] = {
        "api_reachable": system_health.async_check_can_reach_url(hass, API_ENDPOINT),
    }

    if DOMAIN not in hass.data:
        info["status"] = "Not configured"
        return info

    entries = 0
    devices = 0
    errors = []

    for entry_id, data in hass.data[DOMAIN].items():
        entries += 1
        coordinator = data.get("coordinator")

        if coordinator:
            devices += len(coordinator.data.get("devices", {}))

            if not coordinator.last_update_success:
                entry = hass.config_entries.async_get_entry(entry_id)
                errors.append(f"{entry.title}: {coordinator.last_exception}")

    info["configured_entries"] = entries
    info["total_devices"] = devices

    if errors:
        info["errors"] = ", ".join(errors)

    return info
```

---

## Best Practices

### DO

- Always redact sensitive data (tokens, passwords, locations)
- Include coordinator status in diagnostics
- Add device-level diagnostics for complex integrations
- Include timestamps and error messages
- Register system health for cloud integrations

### DON'T

- Expose API keys, tokens, or passwords
- Include exact GPS coordinates (redact or round)
- Dump entire raw API responses without review
- Forget to handle missing data gracefully
- Include PII (email, phone, names)

---

For coordinator patterns, see `coordinator.md`.
For error handling, see `debugging.md`.
