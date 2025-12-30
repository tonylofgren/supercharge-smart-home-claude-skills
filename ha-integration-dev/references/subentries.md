# Config Entry Subentries

Multi-device hub support with config entry subentries (HA 2024.12+).

## Overview

Subentries allow a single config entry (hub/gateway) to manage multiple child devices independently. Each subentry can be configured, reloaded, and removed separately.

**Use Cases:**
- Zigbee/Z-Wave coordinators with multiple devices
- Cloud services with multiple accounts/locations
- Gateways managing multiple child devices
- Multi-room audio systems
- Smart home bridges

---

## Basic Pattern

### manifest.json

```json
{
  "domain": "my_hub",
  "name": "My Hub",
  "config_flow": true,
  "single_config_entry": true,
  "iot_class": "local_push"
}
```

### __init__.py - Hub Setup

```python
"""My Hub integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import MyHub

PLATFORMS = ["sensor", "switch", "light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up hub from config entry."""
    hub = MyHub(hass, entry.data["host"])
    await hub.async_connect()

    # Store hub reference
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub

    # Discover devices and create subentries
    devices = await hub.async_discover_devices()

    for device in devices:
        # Check if subentry already exists
        existing = next(
            (sub for sub in entry.subentries.values()
             if sub.unique_id == device.id),
            None
        )

        if not existing:
            # Create new subentry for device
            await hass.config_entries.async_add_subentry(
                entry,
                ConfigSubentry(
                    data={
                        "device_id": device.id,
                        "model": device.model,
                    },
                    subentry_type="device",
                    title=device.name,
                    unique_id=device.id,
                ),
            )

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
```

### ConfigSubentry Structure

```python
from homeassistant.config_entries import ConfigSubentry

subentry = ConfigSubentry(
    data={"device_id": "abc123", "settings": {...}},
    subentry_type="device",  # or "location", "account", etc.
    title="Living Room Light",
    unique_id="abc123",
)
```

---

## Subentry Config Flow

### config_flow.py

```python
"""Config flow with subentry support."""
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)

from .const import DOMAIN


class MyHubConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle hub config flow."""

    VERSION = 1

    @staticmethod
    def async_get_subentry_flow(
        config_entry: ConfigEntry,
    ) -> type[ConfigSubentryFlow]:
        """Get the subentry flow handler."""
        return DeviceSubentryFlow


class DeviceSubentryFlow(ConfigSubentryFlow, domain=DOMAIN):
    """Handle device subentry configuration."""

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> SubentryFlowResult:
        """Handle subentry configuration."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        # Get hub and available devices
        hub = self.hass.data[DOMAIN][self.source_entry.entry_id]
        devices = await hub.async_get_unconfigured_devices()

        if not devices:
            return self.async_abort(reason="no_devices")

        device_options = {d.id: d.name for d in devices}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("device_id"): vol.In(device_options),
                vol.Required("name"): str,
            }),
        )

    async def async_step_reconfigure(
        self, user_input: dict | None = None
    ) -> SubentryFlowResult:
        """Handle reconfiguration of subentry."""
        subentry = self._get_reconfigure_subentry()

        if user_input is not None:
            return self.async_update_and_abort(
                self.source_entry,
                subentry,
                data=user_input,
                title=user_input.get("name", subentry.title),
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required("name", default=subentry.title): str,
                vol.Optional("setting", default=subentry.data.get("setting")): str,
            }),
        )
```

---

## Accessing Subentries

### In Entity Setup

```python
"""Sensor platform with subentry support."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from hub and subentries."""
    hub = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Create entities for each subentry (device)
    for subentry in entry.subentries.values():
        device_id = subentry.data["device_id"]
        device = hub.get_device(device_id)

        if device:
            entities.extend([
                MySensor(hub, entry, subentry, device, "temperature"),
                MySensor(hub, entry, subentry, device, "humidity"),
            ])

    async_add_entities(entities)


class MySensor(CoordinatorEntity, SensorEntity):
    """Sensor entity from subentry."""

    def __init__(
        self,
        hub: MyHub,
        entry: ConfigEntry,
        subentry: ConfigSubentry,
        device: Device,
        sensor_type: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(hub.coordinator)
        self._device = device
        self._sensor_type = sensor_type

        # Use subentry info for unique_id and device
        self._attr_unique_id = f"{subentry.unique_id}_{sensor_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.unique_id)},
            name=subentry.title,
            model=subentry.data.get("model"),
            via_device=(DOMAIN, entry.entry_id),
        )
```

---

## Subentry Lifecycle

### Adding Subentries Programmatically

```python
from homeassistant.config_entries import ConfigSubentry

async def async_add_discovered_device(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: DiscoveredDevice,
) -> None:
    """Add a newly discovered device as subentry."""
    await hass.config_entries.async_add_subentry(
        entry,
        ConfigSubentry(
            data={
                "device_id": device.id,
                "model": device.model,
                "firmware": device.firmware_version,
            },
            subentry_type="device",
            title=device.name,
            unique_id=device.id,
        ),
    )
```

### Removing Subentries

```python
async def async_remove_device(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device_id: str,
) -> None:
    """Remove device subentry."""
    # Find subentry by unique_id
    subentry = next(
        (sub for sub in entry.subentries.values() if sub.unique_id == device_id),
        None
    )

    if subentry:
        await hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
```

### Updating Subentry Data

```python
async def async_update_device_settings(
    hass: HomeAssistant,
    entry: ConfigEntry,
    subentry_id: str,
    new_settings: dict,
) -> None:
    """Update subentry configuration."""
    subentry = entry.subentries.get(subentry_id)
    if subentry:
        await hass.config_entries.async_update_subentry(
            entry,
            subentry,
            data={**subentry.data, **new_settings},
        )
```

---

## Subentry Types

Define different subentry types for different purposes:

```python
SUBENTRY_TYPES = {
    "device": "Physical Device",
    "location": "Location/Room",
    "account": "User Account",
}


class MySubentryFlow(ConfigSubentryFlow, domain=DOMAIN):
    """Handle multiple subentry types."""

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> SubentryFlowResult:
        """Select subentry type."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_device", "add_location"],
        )

    async def async_step_add_device(
        self, user_input: dict | None = None
    ) -> SubentryFlowResult:
        """Add device subentry."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={**user_input, "type": "device"},
            )
        # Show device form...

    async def async_step_add_location(
        self, user_input: dict | None = None
    ) -> SubentryFlowResult:
        """Add location subentry."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={**user_input, "type": "location"},
            )
        # Show location form...
```

---

## strings.json

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Hub",
        "data": {
          "host": "Host"
        }
      }
    }
  },
  "config_subentries": {
    "device": {
      "initiate_flow": {
        "user": "Add Device"
      },
      "step": {
        "init": {
          "title": "Add Device",
          "data": {
            "device_id": "Select Device",
            "name": "Device Name"
          }
        },
        "reconfigure": {
          "title": "Reconfigure Device",
          "data": {
            "name": "Device Name",
            "setting": "Custom Setting"
          }
        }
      },
      "abort": {
        "no_devices": "No unconfigured devices found"
      }
    }
  }
}
```

---

## Complete Example: Zigbee Hub

```python
"""Zigbee hub with subentries for each device."""
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .zigbee import ZigbeeHub


PLATFORMS = ["sensor", "switch", "light", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zigbee hub."""
    hub = ZigbeeHub(entry.data["port"])
    await hub.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub

    # Listen for new devices
    async def device_discovered(device):
        """Handle newly discovered device."""
        if device.id not in [s.unique_id for s in entry.subentries.values()]:
            await hass.config_entries.async_add_subentry(
                entry,
                ConfigSubentry(
                    data={
                        "ieee": device.ieee,
                        "model": device.model_identifier,
                        "manufacturer": device.manufacturer,
                    },
                    subentry_type="device",
                    title=device.name or f"Zigbee {device.model_identifier}",
                    unique_id=device.id,
                ),
            )

    hub.on_device_discovered = device_discovered

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload hub."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hub = hass.data[DOMAIN].pop(entry.entry_id)
        await hub.async_stop()
    return unload_ok
```

---

## Best Practices

### DO

- Use `unique_id` to prevent duplicate subentries
- Store minimal data in subentry (device ID, settings)
- Implement reconfigure flow for subentry modifications
- Clean up entities when subentry is removed
- Use `via_device` to link subentry devices to hub

### DON'T

- Store large amounts of data in subentries
- Create subentries without unique_id
- Forget to handle subentry removal in entity cleanup
- Mix hub configuration with device configuration

---

For config flow basics, see `config-flow.md`.
For device registry, see `device-registry.md`.
