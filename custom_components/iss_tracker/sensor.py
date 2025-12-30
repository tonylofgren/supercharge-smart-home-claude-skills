"""Sensor platform for ISS Tracker."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import DEGREE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ISSConfigEntry
from .const import ATTRIBUTION, DOMAIN
from .coordinator import ISSData, ISSPositionCoordinator


@dataclass(frozen=True, kw_only=True)
class ISSSensorEntityDescription(SensorEntityDescription):
    """Describes ISS Tracker sensor entity."""

    value_fn: Callable[[ISSData], StateType]
    attr_fn: Callable[[ISSData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[ISSSensorEntityDescription, ...] = (
    ISSSensorEntityDescription(
        key="latitude",
        translation_key="latitude",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.latitude,
    ),
    ISSSensorEntityDescription(
        key="longitude",
        translation_key="longitude",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
        value_fn=lambda data: data.longitude,
    ),
    ISSSensorEntityDescription(
        key="people_in_space",
        translation_key="people_in_space",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:account-group",
        value_fn=lambda data: data.people_in_space,
        attr_fn=lambda data: {
            "astronauts": [
                {"name": p["name"], "craft": p["craft"]} for p in data.astronauts
            ]
        },
    ),
    ISSSensorEntityDescription(
        key="location",
        translation_key="location",
        icon="mdi:map-marker",
        value_fn=lambda data: f"{data.latitude:.4f}, {data.longitude:.4f}",
        attr_fn=lambda data: {
            "latitude": data.latitude,
            "longitude": data.longitude,
            "timestamp": data.timestamp,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ISSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ISS Tracker sensors based on a config entry."""
    coordinator = entry.runtime_data

    async_add_entities(
        ISSSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class ISSSensor(CoordinatorEntity[ISSPositionCoordinator], SensorEntity):
    """Representation of an ISS Tracker sensor."""

    entity_description: ISSSensorEntityDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ISSPositionCoordinator,
        description: ISSSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="International Space Station",
            manufacturer="NASA",
            model="ISS",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="http://api.open-notify.org",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if self.coordinator.data is None or self.entity_description.attr_fn is None:
            return None
        return self.entity_description.attr_fn(self.coordinator.data)
