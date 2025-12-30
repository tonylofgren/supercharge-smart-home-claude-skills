"""Binary sensor platform for My Smart Hub."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HubDevice
from .coordinator import MyHubCoordinator
from .const import DOMAIN
from .entity import MyHubEntity


@dataclass(frozen=True, kw_only=True)
class MyHubBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes My Hub binary sensor entity."""

    value_fn: Callable[[HubDevice], bool]
    exists_fn: Callable[[HubDevice], bool] = lambda _: True


BINARY_SENSOR_DESCRIPTIONS: tuple[MyHubBinarySensorEntityDescription, ...] = (
    MyHubBinarySensorEntityDescription(
        key="motion",
        translation_key="motion",
        device_class=BinarySensorDeviceClass.MOTION,
        value_fn=lambda device: device.sensors.get("motion", False),
        exists_fn=lambda device: "motion" in device.sensors,
    ),
    MyHubBinarySensorEntityDescription(
        key="door",
        translation_key="door",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda device: device.sensors.get("door", False),
        exists_fn=lambda device: "door" in device.sensors,
    ),
    MyHubBinarySensorEntityDescription(
        key="online",
        translation_key="online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda device: device.online,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator: MyHubCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MyHubBinarySensor] = []
    for device_id, device in coordinator.data.items():
        for description in BINARY_SENSOR_DESCRIPTIONS:
            if description.exists_fn(device):
                entities.append(
                    MyHubBinarySensor(coordinator, device_id, description)
                )

    async_add_entities(entities)


class MyHubBinarySensor(MyHubEntity, BinarySensorEntity):
    """Binary sensor entity for My Smart Hub."""

    entity_description: MyHubBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: MyHubCoordinator,
        device_id: str,
        description: MyHubBinarySensorEntityDescription,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return binary sensor state."""
        return self.entity_description.value_fn(self.device)
