# EntityDescription Pattern

Modern dataclass-based entity definitions for Home Assistant (2024+).

## Overview

`EntityDescription` is the recommended pattern for defining entity attributes declaratively. It separates entity metadata (device class, units, icons) from entity behavior (state fetching, actions).

**Benefits:**
- Type-safe entity definitions
- Declarative configuration
- Easy to add new entities
- Better IDE support
- Reduced boilerplate

---

## Basic Pattern

### 1. Define Description Dataclass

```python
"""Entity descriptions for My Integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class MySensorEntityDescription(SensorEntityDescription):
    """Describes a sensor entity."""

    # Custom fields for value extraction
    value_fn: Callable[[dict[str, Any]], StateType]
    exists_fn: Callable[[dict[str, Any]], bool] = lambda _: True
```

**Key Attributes:**
- `frozen=True` - Immutable after creation (required)
- `kw_only=True` - All fields must be keyword arguments (recommended)
- `value_fn` - Function to extract value from coordinator data
- `exists_fn` - Function to check if entity should be created

### 2. Define Entity Descriptions

```python
SENSOR_DESCRIPTIONS: tuple[MySensorEntityDescription, ...] = (
    MySensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("temp"),
    ),
    MySensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.get("humidity"),
    ),
    MySensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda data: data.get("power"),
        exists_fn=lambda data: "power" in data,  # Only create if device has power sensor
    ),
    MySensorEntityDescription(
        key="energy",
        translation_key="energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data.get("total_energy"),
        exists_fn=lambda data: "total_energy" in data,
    ),
)
```

### 3. Create Entity Class

```python
"""Sensor platform for My Integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyCoordinator
from .descriptions import SENSOR_DESCRIPTIONS, MySensorEntityDescription


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator: MyCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        MySensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
        if description.exists_fn(coordinator.data)
    ]
    async_add_entities(entities)


class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Sensor entity using EntityDescription."""

    entity_description: MySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyCoordinator,
        entry: ConfigEntry,
        description: MySensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        # Unique ID from entry + description key
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

        # Device info
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
```

---

## Platform-Specific Descriptions

### Binary Sensor

```python
from dataclasses import dataclass
from collections.abc import Callable
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)


@dataclass(frozen=True, kw_only=True)
class MyBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a binary sensor entity."""

    is_on_fn: Callable[[dict], bool | None]
    exists_fn: Callable[[dict], bool] = lambda _: True


BINARY_SENSOR_DESCRIPTIONS: tuple[MyBinarySensorEntityDescription, ...] = (
    MyBinarySensorEntityDescription(
        key="motion",
        translation_key="motion",
        device_class=BinarySensorDeviceClass.MOTION,
        is_on_fn=lambda data: data.get("motion_detected"),
    ),
    MyBinarySensorEntityDescription(
        key="door",
        translation_key="door",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.get("door_open"),
    ),
    MyBinarySensorEntityDescription(
        key="battery_low",
        translation_key="battery_low",
        device_class=BinarySensorDeviceClass.BATTERY,
        is_on_fn=lambda data: (data.get("battery", 100) or 100) < 20,
    ),
)


class MyBinarySensor(CoordinatorEntity[MyCoordinator], BinarySensorEntity):
    """Binary sensor using description."""

    entity_description: MyBinarySensorEntityDescription
    _attr_has_entity_name = True

    @property
    def is_on(self) -> bool | None:
        """Return true if sensor is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)
```

### Switch

```python
from dataclasses import dataclass
from collections.abc import Callable, Coroutine
from typing import Any
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntityDescription,
)


@dataclass(frozen=True, kw_only=True)
class MySwitchEntityDescription(SwitchEntityDescription):
    """Describes a switch entity."""

    is_on_fn: Callable[[dict], bool | None]
    turn_on_fn: Callable[[Any], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[Any], Coroutine[Any, Any, None]]
    exists_fn: Callable[[dict], bool] = lambda _: True


# Usage with API client reference
def create_switch_descriptions(client: MyApiClient) -> tuple[MySwitchEntityDescription, ...]:
    """Create switch descriptions with API client."""
    return (
        MySwitchEntityDescription(
            key="power",
            translation_key="power",
            device_class=SwitchDeviceClass.SWITCH,
            is_on_fn=lambda data: data.get("power_on"),
            turn_on_fn=lambda _: client.async_set_power(True),
            turn_off_fn=lambda _: client.async_set_power(False),
        ),
        MySwitchEntityDescription(
            key="child_lock",
            translation_key="child_lock",
            device_class=SwitchDeviceClass.SWITCH,
            is_on_fn=lambda data: data.get("child_lock"),
            turn_on_fn=lambda _: client.async_set_child_lock(True),
            turn_off_fn=lambda _: client.async_set_child_lock(False),
        ),
    )


class MySwitch(CoordinatorEntity[MyCoordinator], SwitchEntity):
    """Switch using description."""

    entity_description: MySwitchEntityDescription
    _attr_has_entity_name = True

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self.entity_description.turn_on_fn(kwargs)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self.entity_description.turn_off_fn(kwargs)
        await self.coordinator.async_request_refresh()
```

### Number

```python
from dataclasses import dataclass
from collections.abc import Callable, Coroutine
from typing import Any
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription,
    NumberMode,
)


@dataclass(frozen=True, kw_only=True)
class MyNumberEntityDescription(NumberEntityDescription):
    """Describes a number entity."""

    value_fn: Callable[[dict], float | None]
    set_value_fn: Callable[[float], Coroutine[Any, Any, None]]
    exists_fn: Callable[[dict], bool] = lambda _: True


# Example descriptions
NUMBER_DESCRIPTIONS: tuple[MyNumberEntityDescription, ...] = (
    MyNumberEntityDescription(
        key="brightness",
        translation_key="brightness",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement="%",
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("brightness"),
        set_value_fn=lambda val: client.async_set_brightness(int(val)),
    ),
    MyNumberEntityDescription(
        key="volume",
        translation_key="volume",
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement="%",
        mode=NumberMode.SLIDER,
        value_fn=lambda data: data.get("volume"),
        set_value_fn=lambda val: client.async_set_volume(int(val)),
    ),
)
```

### Select

```python
from dataclasses import dataclass
from collections.abc import Callable, Coroutine
from typing import Any
from homeassistant.components.select import SelectEntityDescription


@dataclass(frozen=True, kw_only=True)
class MySelectEntityDescription(SelectEntityDescription):
    """Describes a select entity."""

    current_fn: Callable[[dict], str | None]
    select_fn: Callable[[str], Coroutine[Any, Any, None]]
    options_fn: Callable[[dict], list[str]] | None = None  # Dynamic options
    exists_fn: Callable[[dict], bool] = lambda _: True


SELECT_DESCRIPTIONS: tuple[MySelectEntityDescription, ...] = (
    MySelectEntityDescription(
        key="mode",
        translation_key="mode",
        options=["auto", "manual", "eco", "boost"],
        current_fn=lambda data: data.get("mode"),
        select_fn=lambda opt: client.async_set_mode(opt),
    ),
    MySelectEntityDescription(
        key="preset",
        translation_key="preset",
        options=["home", "away", "sleep", "comfort"],
        current_fn=lambda data: data.get("preset"),
        select_fn=lambda opt: client.async_set_preset(opt),
    ),
)
```

---

## Advanced Patterns

### Conditional Entity Creation

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors with conditional creation."""
    coordinator: MyCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MySensor] = []
    for description in SENSOR_DESCRIPTIONS:
        # Check if entity should exist based on device capabilities
        if description.exists_fn(coordinator.data):
            entities.append(MySensor(coordinator, entry, description))

    async_add_entities(entities)
```

### Dynamic Descriptions from Device

```python
def get_sensor_descriptions(
    device_capabilities: dict[str, Any],
) -> tuple[MySensorEntityDescription, ...]:
    """Generate descriptions based on device capabilities."""
    descriptions: list[MySensorEntityDescription] = []

    # Always add basic sensors
    descriptions.append(
        MySensorEntityDescription(
            key="status",
            translation_key="status",
            value_fn=lambda data: data.get("status"),
        )
    )

    # Add temperature if device supports it
    if device_capabilities.get("has_temperature"):
        descriptions.append(
            MySensorEntityDescription(
                key="temperature",
                translation_key="temperature",
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                value_fn=lambda data: data.get("temp"),
            )
        )

    # Add energy sensors for power monitoring devices
    if device_capabilities.get("has_power_monitoring"):
        descriptions.extend([
            MySensorEntityDescription(
                key="power",
                translation_key="power",
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=UnitOfPower.WATT,
                value_fn=lambda data: data.get("power"),
            ),
            MySensorEntityDescription(
                key="energy",
                translation_key="energy",
                device_class=SensorDeviceClass.ENERGY,
                state_class=SensorStateClass.TOTAL_INCREASING,
                native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
                value_fn=lambda data: data.get("energy"),
            ),
        ])

    return tuple(descriptions)
```

### Multi-Device with Descriptions

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for multiple devices."""
    coordinator: MyCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MySensor] = []

    # Create sensors for each device
    for device_id, device_data in coordinator.data["devices"].items():
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_data["name"],
            manufacturer="My Company",
            model=device_data.get("model", "Unknown"),
        )

        for description in SENSOR_DESCRIPTIONS:
            if description.exists_fn(device_data):
                entities.append(
                    MySensor(
                        coordinator,
                        entry,
                        description,
                        device_id=device_id,
                        device_info=device_info,
                    )
                )

    async_add_entities(entities)


class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Sensor for multi-device setup."""

    entity_description: MySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyCoordinator,
        entry: ConfigEntry,
        description: MySensorEntityDescription,
        device_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id

        self._attr_unique_id = f"{entry.entry_id}_{device_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> StateType:
        """Return sensor value."""
        device_data = self.coordinator.data["devices"].get(self._device_id, {})
        return self.entity_description.value_fn(device_data)
```

### Extra State Attributes

```python
@dataclass(frozen=True, kw_only=True)
class MySensorEntityDescription(SensorEntityDescription):
    """Sensor with extra attributes."""

    value_fn: Callable[[dict], StateType]
    extra_attrs_fn: Callable[[dict], dict[str, Any]] | None = None


class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Sensor with extra attributes from description."""

    entity_description: MySensorEntityDescription

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.extra_attrs_fn:
            return self.entity_description.extra_attrs_fn(self.coordinator.data)
        return None


# Usage
MySensorEntityDescription(
    key="temperature",
    translation_key="temperature",
    device_class=SensorDeviceClass.TEMPERATURE,
    value_fn=lambda data: data.get("temp"),
    extra_attrs_fn=lambda data: {
        "raw_value": data.get("temp_raw"),
        "sensor_type": data.get("temp_sensor_type"),
        "calibration_offset": data.get("temp_offset"),
    },
)
```

---

## Translation Keys

```json
{
  "entity": {
    "sensor": {
      "temperature": {
        "name": "Temperature"
      },
      "humidity": {
        "name": "Humidity"
      },
      "power": {
        "name": "Power"
      },
      "energy": {
        "name": "Energy"
      }
    },
    "binary_sensor": {
      "motion": {
        "name": "Motion"
      },
      "door": {
        "name": "Door"
      }
    },
    "switch": {
      "power": {
        "name": "Power"
      },
      "child_lock": {
        "name": "Child Lock"
      }
    }
  }
}
```

---

## Best Practices

### DO

- Use `frozen=True, kw_only=True` for all descriptions
- Use `translation_key` for entity names (not hardcoded strings)
- Use `exists_fn` for conditional entity creation
- Keep descriptions in a separate file (`descriptions.py`)
- Use type hints for all custom fields

### DON'T

- Mutate description objects after creation
- Use mutable default values in dataclasses
- Hardcode entity names (use translations)
- Put API logic directly in descriptions (use Callables)

---

For entity basics, see `entities.md`.
For coordinator patterns, see `coordinator.md`.
