"""Sensor platform for My Smart Hub."""
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
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .api import HubDevice
from .coordinator import MyHubCoordinator
from .const import DOMAIN
from .entity import MyHubEntity


@dataclass(frozen=True, kw_only=True)
class MyHubSensorEntityDescription(SensorEntityDescription):
    """Describes My Hub sensor entity."""

    value_fn: Callable[[HubDevice], StateType]
    exists_fn: Callable[[HubDevice], bool] = lambda _: True


SENSOR_DESCRIPTIONS: tuple[MyHubSensorEntityDescription, ...] = (
    MyHubSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: device.sensors.get("temperature"),
        exists_fn=lambda device: "temperature" in device.sensors,
    ),
    MyHubSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda device: device.sensors.get("humidity"),
        exists_fn=lambda device: "humidity" in device.sensors,
    ),
    MyHubSensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda device: device.sensors.get("battery"),
        exists_fn=lambda device: "battery" in device.sensors,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: MyHubCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MyHubSensor] = []
    for device_id, device in coordinator.data.items():
        for description in SENSOR_DESCRIPTIONS:
            if description.exists_fn(device):
                entities.append(
                    MyHubSensor(coordinator, device_id, description)
                )

    async_add_entities(entities)


class MyHubSensor(MyHubEntity, SensorEntity):
    """Sensor entity for My Smart Hub."""

    entity_description: MyHubSensorEntityDescription

    def __init__(
        self,
        coordinator: MyHubCoordinator,
        device_id: str,
        description: MyHubSensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return sensor value."""
        return self.entity_description.value_fn(self.device)
