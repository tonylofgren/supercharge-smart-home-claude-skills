# Device and Entity Registry

Device grouping and entity identification for Home Assistant integrations.

## Device Info

### Basic DeviceInfo

```python
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


class MyEntity(CoordinatorEntity, SensorEntity):
    """Entity with device info."""

    def __init__(self, coordinator, device_id: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="My Device",
            manufacturer="Acme Corp",
            model="Model X",
        )
```

### Complete DeviceInfo

```python
from homeassistant.helpers.entity import DeviceInfo

device_info = DeviceInfo(
    # REQUIRED: At least one identifier
    identifiers={(DOMAIN, "unique_device_id")},

    # RECOMMENDED
    name="Living Room Sensor",
    manufacturer="Acme Corporation",
    model="SmartSensor Pro",

    # OPTIONAL - Additional identification
    model_id="SS-PRO-001",           # Model ID/number
    serial_number="ABC123456",        # Serial number
    hw_version="2.0",                 # Hardware version
    sw_version="1.2.3",               # Software/firmware version

    # OPTIONAL - Alternative identifiers
    connections={
        ("mac", "AA:BB:CC:DD:EE:FF"),
        ("ip", "192.168.1.100"),
    },

    # OPTIONAL - Configuration
    configuration_url="http://192.168.1.100/settings",

    # OPTIONAL - Device hierarchy
    via_device=(DOMAIN, "hub_device_id"),

    # OPTIONAL - Area suggestion
    suggested_area="Living Room",

    # OPTIONAL - Entry reference
    entry_type=None,  # DeviceEntryType.SERVICE for virtual devices
)
```

### DeviceInfo Fields Reference

| Field | Type | Description |
|-------|------|-------------|
| `identifiers` | `set[tuple[str, str]]` | Primary identifiers `{(domain, id)}` |
| `connections` | `set[tuple[str, str]]` | Network identifiers `{(type, value)}` |
| `name` | `str` | Device name |
| `manufacturer` | `str` | Manufacturer name |
| `model` | `str` | Model name |
| `model_id` | `str` | Model identifier |
| `serial_number` | `str` | Serial number |
| `hw_version` | `str` | Hardware version |
| `sw_version` | `str` | Software/firmware version |
| `configuration_url` | `str` | Web interface URL |
| `via_device` | `tuple[str, str]` | Parent device identifier |
| `suggested_area` | `str` | Area name hint |
| `entry_type` | `DeviceEntryType` | Device type |

### Connection Types

| Type | Example |
|------|---------|
| `mac` | `AA:BB:CC:DD:EE:FF` |
| `upnp` | `uuid:12345678-1234-1234-1234-123456789abc` |
| `zigbee` | `00:11:22:33:44:55:66:77` |
| `bluetooth` | `AA:BB:CC:DD:EE:FF` |

---

## Entity Unique ID

### Requirements

- **REQUIRED** for entity customization in UI
- Must be stable across restarts
- Must be unique within integration
- Should not change when device is reconfigured

### Patterns

```python
# Good patterns
unique_id = f"{entry.entry_id}_{device_id}_temperature"
unique_id = f"{serial_number}_sensor"
unique_id = f"{mac_address}_switch"

# Bad patterns (don't use)
unique_id = f"{ip_address}_sensor"      # IP can change
unique_id = f"sensor_{random.random()}"  # Not stable
unique_id = "temperature"                # Not unique
```

### Entity with Unique ID

```python
class MyTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor."""

    _attr_has_entity_name = True
    _attr_name = "Temperature"

    def __init__(self, coordinator, entry: ConfigEntry, device_id: str) -> None:
        """Initialize."""
        super().__init__(coordinator)

        # Unique ID pattern: entry_device_type
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_temperature"

        # Device grouping
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
        )
```

---

## Entity Naming

### has_entity_name Pattern

```python
class MyEntity(SensorEntity):
    """Entity using has_entity_name."""

    # Enable new naming pattern
    _attr_has_entity_name = True

    # Entity name (appended to device name)
    _attr_name = "Temperature"

    # Device name is "Living Room Sensor"
    # Entity name becomes "Living Room Sensor Temperature"
```

### Translation Keys

```python
class MyEntity(SensorEntity):
    """Entity with translated name."""

    _attr_has_entity_name = True
    _attr_translation_key = "temperature"

    # Name from strings.json: entity.sensor.my_integration.temperature.name
```

```json
{
  "entity": {
    "sensor": {
      "my_integration": {
        "temperature": {
          "name": "Temperature"
        }
      }
    }
  }
}
```

### Device as Entity Name

```python
class MyEntity(SensorEntity):
    """Entity where device IS the entity."""

    _attr_has_entity_name = True
    _attr_name = None  # Entity name = Device name
```

---

## Entity Categories

```python
from homeassistant.helpers.entity import EntityCategory

class MyDiagnosticSensor(SensorEntity):
    """Diagnostic sensor (hidden from main UI)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Signal Strength"


class MyConfigEntity(NumberEntity):
    """Configuration entity."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Update Interval"
```

| Category | Purpose | Example |
|----------|---------|---------|
| `None` | Primary entities | Temperature, power state |
| `DIAGNOSTIC` | Status/debug info | Signal strength, uptime |
| `CONFIG` | Settings | Update interval, thresholds |

---

## Device Registry Operations

### Getting Device Registry

```python
from homeassistant.helpers import device_registry as dr


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with device registry access."""
    device_registry = dr.async_get(hass)

    # Get device by identifiers
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, "device_id")}
    )

    if device:
        _LOGGER.info("Found device: %s", device.name)

    return True
```

### Creating Device Without Entity

```python
from homeassistant.helpers import device_registry as dr


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register device without entities."""
    device_registry = dr.async_get(hass)

    # Create/update device
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "hub_device")},
        name="Hub Device",
        manufacturer="Acme Corp",
        model="Hub Pro",
    )

    return True
```

### Updating Device

```python
device_registry = dr.async_get(hass)
device = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})

if device:
    device_registry.async_update_device(
        device.id,
        sw_version="2.0.0",
        name_by_user="My Custom Name",
    )
```

### Removing Device

```python
device_registry = dr.async_get(hass)
device = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})

if device:
    device_registry.async_remove_device(device.id)
```

---

## Entity Registry Operations

### Getting Entity Registry

```python
from homeassistant.helpers import entity_registry as er


async def get_entity_info(hass: HomeAssistant) -> None:
    """Access entity registry."""
    entity_registry = er.async_get(hass)

    # Get entity by entity_id
    entry = entity_registry.async_get("sensor.my_sensor")
    if entry:
        _LOGGER.info("Unique ID: %s", entry.unique_id)

    # Get entity by unique_id
    entry = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "unique_id_here"
    )
```

### Disabling Entities

```python
class MyEntity(SensorEntity):
    """Entity disabled by default."""

    _attr_entity_registry_enabled_default = False
    _attr_name = "Debug Info"
```

### Entity Visibility

```python
class MyEntity(SensorEntity):
    """Hidden entity."""

    _attr_entity_registry_visible_default = False
```

---

## Device Hierarchy

### Parent-Child Devices

```python
# Hub device (parent)
class HubEntity(SensorEntity):
    """Hub entity."""

    _attr_device_info = DeviceInfo(
        identifiers={(DOMAIN, "hub_123")},
        name="Smart Hub",
        manufacturer="Acme",
        model="Hub Pro",
    )


# Child device
class ChildEntity(SensorEntity):
    """Child device entity."""

    _attr_device_info = DeviceInfo(
        identifiers={(DOMAIN, "sensor_456")},
        name="Room Sensor",
        manufacturer="Acme",
        model="Sensor Mini",
        via_device=(DOMAIN, "hub_123"),  # Link to parent
    )
```

---

## Diagnostics

### diagnostics.py

```python
"""Diagnostics for My Integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": {
                # Redact sensitive data
                "host": entry.data.get("host"),
                "api_key": "**REDACTED**" if "api_key" in entry.data else None,
            },
            "options": dict(entry.options),
        },
        "coordinator_data": coordinator.data,
        "last_update_success": coordinator.last_update_success,
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a specific device."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Find device data
    device_id = None
    for identifier in device.identifiers:
        if identifier[0] == DOMAIN:
            device_id = identifier[1]
            break

    device_data = coordinator.data.get(device_id, {})

    return {
        "device": {
            "name": device.name,
            "model": device.model,
            "sw_version": device.sw_version,
            "identifiers": list(device.identifiers),
        },
        "data": device_data,
    }
```

---

## Area Assignment

### Suggesting Area

```python
class MyEntity(SensorEntity):
    """Entity with suggested area."""

    _attr_device_info = DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name="Temperature Sensor",
        suggested_area="Living Room",  # Suggests area on first setup
    )
```

### Getting Area

```python
from homeassistant.helpers import area_registry as ar


async def get_device_area(hass: HomeAssistant, device_id: str) -> str | None:
    """Get area name for device."""
    device_registry = dr.async_get(hass)
    area_registry = ar.async_get(hass)

    device = device_registry.async_get_device(identifiers={(DOMAIN, device_id)})
    if device and device.area_id:
        area = area_registry.async_get_area(device.area_id)
        return area.name if area else None

    return None
```

---

## Device Automation

Allow automations to trigger/condition/act on device events.

### Required Files

```
custom_components/my_integration/
├── device_trigger.py     # Automation triggers
├── device_condition.py   # Automation conditions
└── device_action.py      # Automation actions
```

### Device Triggers Summary

```python
# device_trigger.py
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger

TRIGGER_TYPES = {"button_pressed", "motion_detected", "device_offline"}


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """Return triggers for device."""
    return [
        {
            CONF_PLATFORM: "device",
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: trigger_type,
        }
        for trigger_type in TRIGGER_TYPES
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    # Listen for {DOMAIN}_event events with matching device/type
    return await event_trigger.async_attach_trigger(...)
```

### Firing Trigger Events

```python
# In coordinator when event occurs
hass.bus.async_fire(
    f"{DOMAIN}_event",
    {
        CONF_DEVICE_ID: device_id,
        CONF_TYPE: "button_pressed",
    },
)
```

### strings.json for Device Automation

```json
{
  "device_automation": {
    "trigger_type": {
      "button_pressed": "Button pressed",
      "motion_detected": "Motion detected",
      "device_offline": "Device went offline"
    },
    "condition_type": {
      "is_on": "Is on",
      "is_off": "Is off"
    },
    "action_type": {
      "turn_on": "Turn on",
      "turn_off": "Turn off"
    }
  }
}
```

For complete device automation examples, see `services-events.md`.

---

## Best Practices

### Device Info

- Always include `identifiers` (required)
- Use stable identifiers (serial, MAC, not IP)
- Set `via_device` for child devices
- Include `configuration_url` if device has web UI
- Use `suggested_area` for better UX

### Unique ID

- Always set unique_id
- Use stable, predictable values
- Include entry_id for multi-instance support
- Never use random or changing values

### Entity Naming

- Use `_attr_has_entity_name = True`
- Use translation keys for localization
- Set `name = None` for primary device entity

### Categories

- Use `DIAGNOSTIC` for debug/status entities
- Use `CONFIG` for settings entities
- Leave as `None` for primary control entities

---

For services and events, see `services-events.md`.
For entity platforms, see `entities.md`.
For diagnostics, see `diagnostics.md`.
