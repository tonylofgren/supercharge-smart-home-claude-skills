# Basic Integration Template

Minimal starter template for a Home Assistant custom integration with config flow.

## Features

- **Config Flow**: User-facing setup wizard
- **Single Sensor**: Basic entity implementation
- **API Key Authentication**: Simple credential validation
- **Clean Structure**: Follows HA conventions

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration setup and config entry handling |
| `config_flow.py` | User setup wizard with validation |
| `const.py` | Constants and domain definition |
| `sensor.py` | Basic sensor entity |
| `manifest.json` | Integration metadata |
| `strings.json` | UI labels for config flow |

## Customization Steps

### 1. Update Domain Name

In `const.py`:
```python
DOMAIN = "your_integration_name"
```

Update the folder name and all imports to match.

### 2. Add API Client

In `__init__.py`:
```python
from your_api_library import YourAPI

async def async_setup_entry(hass, entry):
    api = YourAPI(entry.data[CONF_API_KEY])
    # Store for use by entities
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api
```

### 3. Customize Config Flow Validation

In `config_flow.py`:
```python
async def _validate_input(self, data):
    api = YourAPI(data[CONF_API_KEY])
    try:
        await api.authenticate()
    except AuthError:
        raise InvalidAuth
```

### 4. Add Your Sensor Logic

In `sensor.py`:
```python
@property
def native_value(self):
    return self.api.get_value()
```

## When to Use This Template

- Starting your first integration
- Simple API with one or few sensors
- Learning Home Assistant integration patterns

## Next Steps

Once working, consider:
- Adding `DataUpdateCoordinator` (see polling-integration template)
- Adding more entity types
- Adding options flow
- Adding diagnostics

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Config Flow Documentation](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
