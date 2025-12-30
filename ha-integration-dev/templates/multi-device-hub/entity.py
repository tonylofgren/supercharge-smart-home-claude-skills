"""Base entity for My Smart Hub."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import HubDevice
from .coordinator import MyHubCoordinator
from .const import DOMAIN


class MyHubEntity(CoordinatorEntity[MyHubCoordinator]):
    """Base entity for My Smart Hub devices."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyHubCoordinator,
        device_id: str,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self._device_id = device_id

        # Device info with hub as parent
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=self.device.name,
            manufacturer="My Hub Manufacturer",
            model=self.device.model,
            sw_version=self.device.firmware,
            via_device=(DOMAIN, coordinator.config_entry.entry_id),
        )

    @property
    def device(self) -> HubDevice:
        """Return the device."""
        return self.coordinator.data[self._device_id]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self._device_id in self.coordinator.data
            and self.coordinator.data[self._device_id].online
        )
