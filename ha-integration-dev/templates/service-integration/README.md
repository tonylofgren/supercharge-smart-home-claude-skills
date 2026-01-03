# Service Integration Template

Template for integrations that expose custom services for advanced functionality.

## Features

- **Custom Services**: Actions beyond entity control
- **Response Data**: Services that return information
- **Schema Validation**: Voluptuous input validation
- **Entity Targeting**: Services that act on specific entities
- **Service Descriptions**: YAML-based UI documentation

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup, service registration |
| `services.py` | Service handlers and schemas |
| `services.yaml` | Service descriptions for UI |
| `const.py` | Service names and constants |
| `manifest.json` | Integration metadata |
| `strings.json` | UI strings and service labels |

## Customization Steps

### 1. Define Service Schema

In `services.py`:
```python
SERVICE_SET_MODE_SCHEMA = vol.Schema({
    vol.Required("mode"): vol.In(["auto", "manual", "eco"]),
    vol.Optional("device_id"): cv.string,
    vol.Optional("temperature"): vol.Coerce(float),
})
```

### 2. Implement Service Handler

In `services.py`:
```python
async def async_handle_set_mode(call):
    """Handle the set_mode service call."""
    mode = call.data["mode"]
    device_id = call.data.get("device_id")

    # Get coordinator from hass.data
    coordinator = hass.data[DOMAIN][entry_id]

    # Call API
    await coordinator.api.set_mode(device_id, mode)

    # Refresh data
    await coordinator.async_request_refresh()
```

### 3. Register Services

In `__init__.py`:
```python
async def async_setup_entry(hass, entry):
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MODE,
        async_handle_set_mode,
        schema=SERVICE_SET_MODE_SCHEMA,
    )
```

### 4. Add Service Descriptions

In `services.yaml`:
```yaml
set_mode:
  name: Set Mode
  description: Set the operating mode for a device.
  fields:
    mode:
      name: Mode
      description: The mode to set.
      required: true
      example: "auto"
      selector:
        select:
          options:
            - auto
            - manual
            - eco
    device_id:
      name: Device
      description: Target device (optional, defaults to all).
      selector:
        device:
          integration: your_integration
```

## Service Patterns

### Basic Service (No Response)

```python
hass.services.async_register(
    DOMAIN,
    "restart_device",
    handle_restart,
    schema=RESTART_SCHEMA,
)
```

### Service with Response Data

```python
from homeassistant.core import SupportsResponse

hass.services.async_register(
    DOMAIN,
    "get_diagnostics",
    handle_get_diagnostics,
    schema=DIAGNOSTICS_SCHEMA,
    supports_response=SupportsResponse.ONLY,
)

async def handle_get_diagnostics(call):
    return {
        "status": "ok",
        "uptime": 12345,
        "errors": [],
    }
```

### Entity-Targeted Service

```python
SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required("brightness"): vol.All(
        vol.Coerce(int), vol.Range(min=0, max=100)
    ),
})

async def handle_set_brightness(call):
    entity_ids = call.data[ATTR_ENTITY_ID]
    brightness = call.data["brightness"]

    for entity_id in entity_ids:
        await set_entity_brightness(entity_id, brightness)
```

### Service Cleanup on Unload

```python
async def async_unload_entry(hass, entry):
    # Remove services when last config entry unloaded
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_SET_MODE)
    return True
```

## When to Use This Template

- Complex operations beyond entity states
- Bulk operations on multiple devices
- Query operations returning data
- Integration-wide settings

## Resources

- [Service Documentation](https://developers.home-assistant.io/docs/dev_101_services)
- [Service Responses](https://developers.home-assistant.io/docs/core/entity/integration/#service-responses)
- [Voluptuous Schema](https://github.com/alecthomas/voluptuous)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
