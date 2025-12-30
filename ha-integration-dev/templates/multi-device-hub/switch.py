"""Switch platform for My Smart Hub."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import HubDevice
from .coordinator import MyHubCoordinator
from .const import DOMAIN
from .entity import MyHubEntity


@dataclass(frozen=True, kw_only=True)
class MyHubSwitchEntityDescription(SwitchEntityDescription):
    """Describes My Hub switch entity."""

    switch_key: str
    exists_fn: Callable[[HubDevice], bool] = lambda _: True


SWITCH_DESCRIPTIONS: tuple[MyHubSwitchEntityDescription, ...] = (
    MyHubSwitchEntityDescription(
        key="power",
        translation_key="power",
        switch_key="power",
        device_class=SwitchDeviceClass.OUTLET,
        exists_fn=lambda device: "power" in device.switches,
    ),
    MyHubSwitchEntityDescription(
        key="night_light",
        translation_key="night_light",
        switch_key="night_light",
        exists_fn=lambda device: "night_light" in device.switches,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    coordinator: MyHubCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MyHubSwitch] = []
    for device_id, device in coordinator.data.items():
        for description in SWITCH_DESCRIPTIONS:
            if description.exists_fn(device):
                entities.append(
                    MyHubSwitch(coordinator, device_id, description)
                )

    async_add_entities(entities)


class MyHubSwitch(MyHubEntity, SwitchEntity):
    """Switch entity for My Smart Hub."""

    entity_description: MyHubSwitchEntityDescription

    def __init__(
        self,
        coordinator: MyHubCoordinator,
        device_id: str,
        description: MyHubSwitchEntityDescription,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return switch state."""
        return self.device.switches.get(self.entity_description.switch_key, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on switch."""
        await self.coordinator.client.async_turn_on(
            self._device_id, self.entity_description.switch_key
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off switch."""
        await self.coordinator.client.async_turn_off(
            self._device_id, self.entity_description.switch_key
        )
        await self.coordinator.async_request_refresh()
