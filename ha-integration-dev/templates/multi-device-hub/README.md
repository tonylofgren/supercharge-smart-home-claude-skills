# Multi-Device Hub Template

Template for integrations that manage a hub with multiple child devices (like Philips Hue, SmartThings, etc.).

## Features

- **Device Registry**: Parent/child device relationships
- **Per-Device Coordinators**: Independent update cycles
- **EntityDescription Pattern**: DRY sensor/switch definitions
- **Dynamic Entity Discovery**: Add devices without restart
- **Diagnostics**: Debug information with redaction

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Hub setup, device discovery |
| `api.py` | Hub API client |
| `config_flow.py` | Multi-step setup wizard |
| `coordinator.py` | Per-device data coordinator |
| `entity.py` | Base entity with device_info |
| `sensor.py` | Sensor entities with descriptions |
| `binary_sensor.py` | Binary sensor entities |
| `switch.py` | Switch entities |
| `diagnostics.py` | Debug data with redaction |
| `manifest.json` | Integration metadata |
| `strings.json` | UI strings |

## Customization Steps

### 1. Implement Hub API

In `api.py`:
```python
class HubAPI:
    async def get_devices(self):
        """Return list of connected devices."""
        return await self._request("GET", "/devices")

    async def get_device_data(self, device_id):
        """Return data for specific device."""
        return await self._request("GET", f"/devices/{device_id}")
```

### 2. Set Up Per-Device Coordinators

In `__init__.py`:
```python
async def async_setup_entry(hass, entry):
    api = HubAPI(entry.data[CONF_HOST])
    devices = await api.get_devices()

    coordinators = {}
    for device in devices:
        coordinator = DeviceCoordinator(hass, api, device)
        await coordinator.async_config_entry_first_refresh()
        coordinators[device.id] = coordinator
```

### 3. Configure Device Info

In `entity.py`:
```python
@property
def device_info(self):
    return DeviceInfo(
        identifiers={(DOMAIN, self._device_id)},
        name=self._device.name,
        manufacturer=self._device.manufacturer,
        model=self._device.model,
        sw_version=self._device.firmware,
        via_device=(DOMAIN, self._hub_id),  # Parent hub
    )
```

### 4. Add Entity Descriptions

In `sensor.py`:
```python
SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # More sensors...
)
```

### 5. Handle Device Discovery

For runtime discovery:
```python
async def async_discover_devices(hass, entry):
    """Discover new devices and add entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    new_devices = await coordinator.api.get_devices()

    async_dispatcher_send(
        hass,
        f"{DOMAIN}_new_device",
        new_devices,
    )
```

## Architecture Patterns

### Coordinator Per Device

Best for devices with independent data:
```
Hub ─┬─ Device A Coordinator
     ├─ Device B Coordinator
     └─ Device C Coordinator
```

### Single Coordinator for All

Best when hub returns all data at once:
```
Hub ─── Hub Coordinator ─┬─ Device A Entities
                         ├─ Device B Entities
                         └─ Device C Entities
```

### Device Grouping

For mixed entity types per device:
```python
# Create all entity types for each device
for device in devices:
    sensors.append(TemperatureSensor(coordinator, device))
    sensors.append(HumiditySensor(coordinator, device))
    switches.append(PowerSwitch(coordinator, device))
```

## When to Use This Template

- Smart home hubs (Hue, SmartThings, Tuya)
- Network equipment (routers, switches)
- Multi-zone systems (HVAC, audio)
- Any system with parent/child relationship

## Resources

- [Device Registry](https://developers.home-assistant.io/docs/device_registry_index)
- [Entity Descriptions](https://developers.home-assistant.io/docs/core/entity/#entity-descriptions)
- [Diagnostics](https://developers.home-assistant.io/docs/core/entity/diagnostics)

---

*Generated with [ha-integration@aurora-smart-home](https://github.com/tonylofgren/aurora-smart-home)*
