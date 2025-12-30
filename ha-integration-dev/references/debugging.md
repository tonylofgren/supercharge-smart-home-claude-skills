# Debugging

Logging, common errors, and debugging techniques for Home Assistant integrations.

## Logger Setup

### Basic Logging

```python
"""My Integration."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    """Set up integration."""
    _LOGGER.debug("Setting up entry: %s", entry.entry_id)
    _LOGGER.info("Connected to device at %s", entry.data["host"])
    _LOGGER.warning("Connection slow, retrying...")
    _LOGGER.error("Failed to connect: %s", error)
```

### Log Levels

| Level | When to Use |
|-------|-------------|
| `DEBUG` | Detailed flow, variable values |
| `INFO` | Normal operations, milestones |
| `WARNING` | Recoverable issues |
| `ERROR` | Failed operations |
| `CRITICAL` | System-critical failures |

### Enable Debug Logging

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.my_integration: debug
```

Or via UI: Settings → System → Logs → (three dots) → Set log level

---

## Debug Component

### Adding Debug Platform

```python
# debug.py - Optional debug platform
"""Debug platform for My Integration."""
from homeassistant.components.sensor import SensorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up debug sensors."""
    async_add_entities([
        DebugSensor(hass.data[DOMAIN][entry.entry_id]["coordinator"]),
    ])


class DebugSensor(SensorEntity):
    """Debug sensor showing coordinator state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Debug Info"

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def native_value(self):
        return f"Updates: {self.coordinator.update_interval}"

    @property
    def extra_state_attributes(self):
        return {
            "last_update": self.coordinator.last_update_success_time,
            "update_count": getattr(self.coordinator, "_update_count", 0),
            "raw_data": self.coordinator.data,
        }
```

---

## Common Errors

### ConfigEntryNotReady

**Symptom:** Integration shows "Retrying setup"

**Causes:**
- Network timeout
- Device offline
- API not responding

**Solution:**
```python
from homeassistant.exceptions import ConfigEntryNotReady

async def async_setup_entry(hass, entry):
    try:
        await client.async_connect()
    except ConnectionError as err:
        raise ConfigEntryNotReady(
            f"Cannot connect to {entry.data['host']}: {err}"
        ) from err
```

### ConfigEntryAuthFailed

**Symptom:** Integration shows "Reauth required"

**Causes:**
- Invalid credentials
- Token expired
- API key revoked

**Solution:**
```python
from homeassistant.exceptions import ConfigEntryAuthFailed

async def _async_update_data(self):
    try:
        return await self.client.async_get_data()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed("Invalid credentials") from err
```

### Blocking I/O in Event Loop

**Symptom:**
```
Detected blocking call to ... in ... inside the event loop
```

**Cause:** Using synchronous libraries (requests, time.sleep)

**Solution:**
```python
# Bad
import requests
response = requests.get(url)  # Blocking!

# Good
import aiohttp
async with session.get(url) as response:
    data = await response.json()

# Or wrap blocking code
await hass.async_add_executor_job(blocking_function)
```

### Entity Not Appearing

**Causes:**
1. Missing `unique_id`
2. Platform not in PLATFORMS list
3. Entity not added to async_add_entities

**Debug:**
```python
_LOGGER.debug("Adding entities: %s", entities)
async_add_entities(entities)
```

### State Always Unknown

**Causes:**
1. Property returns None
2. Coordinator data not populated
3. Entity not registered

**Debug:**
```python
@property
def native_value(self):
    value = self.coordinator.data.get("temperature")
    _LOGGER.debug("native_value called, returning: %s", value)
    return value
```

### Import Errors

**Symptom:**
```
Unable to import component: No module named 'xxx'
```

**Solution:**
1. Check `requirements` in manifest.json
2. Restart Home Assistant
3. Check virtual environment

### Config Flow Not Showing

**Causes:**
1. `config_flow: true` missing in manifest.json
2. Syntax error in config_flow.py
3. Missing strings.json

**Debug:**
```bash
# Check HA logs for import errors
grep -i "my_integration" home-assistant.log
```

---

## Debugging Techniques

### Print to Log

```python
_LOGGER.debug("Variable state: %r", variable)
_LOGGER.debug("Dict contents: %s", json.dumps(data, indent=2))
```

### Breakpoint Debugging

```python
# Add to code
import pdb; pdb.set_trace()  # Stops execution

# Or with VS Code debugger
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### Inspect Coordinator Data

```python
# In Developer Tools → States
# Look for sensor.my_integration_debug

# Or in code
_LOGGER.debug("Coordinator data: %s", coordinator.data)
_LOGGER.debug("Last success: %s", coordinator.last_update_success)
```

### Track Entity State Changes

```yaml
# configuration.yaml
logger:
  logs:
    homeassistant.components.my_integration: debug
    homeassistant.helpers.entity: debug
```

### Network Debugging

```python
import logging

# Enable aiohttp debug
logging.getLogger("aiohttp").setLevel(logging.DEBUG)

# Log all requests
async def _request(self, method, url, **kwargs):
    _LOGGER.debug("Request: %s %s", method, url)
    response = await self._session.request(method, url, **kwargs)
    _LOGGER.debug("Response: %s %s", response.status, await response.text())
    return response
```

---

## Developer Tools

### States Panel

Check entity states at: Developer Tools → States

### Services Panel

Test services at: Developer Tools → Services

### Template Editor

Test templates at: Developer Tools → Template

```jinja
{{ states('sensor.my_integration_temperature') }}
{{ state_attr('sensor.my_integration_temperature', 'last_update') }}
```

### Logs Panel

View logs at: Settings → System → Logs

---

## VS Code Debugging

### launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Home Assistant",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/config/custom_components/my_integration"
        }
      ]
    }
  ]
}
```

### Enable Debug in HA

```yaml
# configuration.yaml
debugpy:
  start: true
  port: 5678
```

---

## Performance Profiling

### Measure Execution Time

```python
import time

async def async_setup_entry(hass, entry):
    start = time.monotonic()

    await coordinator.async_config_entry_first_refresh()

    elapsed = time.monotonic() - start
    _LOGGER.info("Setup completed in %.2f seconds", elapsed)
```

### Profile Coordinator Updates

```python
class MyCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        start = time.monotonic()

        data = await self.client.async_get_data()

        elapsed = time.monotonic() - start
        _LOGGER.debug("Data fetch took %.2f seconds", elapsed)

        return data
```

---

## Diagnostics Download

### diagnostics.py

```python
"""Diagnostics for debugging."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    return {
        "config_entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "data": {
                "host": entry.data.get("host"),
                "api_key": "**REDACTED**",
            },
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "data": coordinator.data,
        },
    }
```

Download at: Settings → Devices & Services → (integration) → ... → Download diagnostics

---

## Error Messages

### Common Log Messages

| Message | Meaning |
|---------|---------|
| `Setup of integration failed` | async_setup_entry raised exception |
| `Config entry failed to load` | ConfigEntryNotReady raised |
| `Detected blocking call` | Synchronous code in async context |
| `Entity not ready` | Entity properties returned None |
| `Unable to import` | Missing dependency or syntax error |

### Useful Log Searches

```bash
# Find errors
grep -i "error\|exception\|failed" home-assistant.log | grep my_integration

# Find warnings
grep -i "warning" home-assistant.log | grep my_integration

# Find setup issues
grep -i "setup\|config" home-assistant.log | grep my_integration
```

---

## Best Practices

### DO

- Use DEBUG for detailed info, INFO for operations
- Include context in log messages
- Use `%s` formatting (not f-strings) for lazy evaluation
- Add diagnostics.py for downloadable debug info
- Test error paths, not just happy paths

### DON'T

- Log sensitive data (passwords, tokens)
- Use print() statements
- Leave DEBUG logging in production
- Ignore warnings and errors
- Use blocking calls in async code

---

For testing patterns, see `testing.md`.
For publishing, see `publishing.md`.
