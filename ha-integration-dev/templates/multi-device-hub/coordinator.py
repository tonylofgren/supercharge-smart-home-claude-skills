"""DataUpdateCoordinator for My Smart Hub."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HubDevice, MyHubApiError, MyHubClient
from .const import _LOGGER, DEFAULT_SCAN_INTERVAL, DOMAIN


class MyHubCoordinator(DataUpdateCoordinator[dict[str, HubDevice]]):
    """Coordinator for My Smart Hub."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: MyHubClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.client = client
        self.config_entry = entry
        self.hub_info: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, HubDevice]:
        """Fetch data from API."""
        try:
            # Get hub info (less frequently if needed)
            if not self.hub_info:
                self.hub_info = await self.client.async_get_hub_info()

            # Get all devices
            devices = await self.client.async_get_devices()
            return {device.id: device for device in devices}

        except MyHubApiError as err:
            raise UpdateFailed(f"Error communicating with hub: {err}") from err

    def get_device(self, device_id: str) -> HubDevice | None:
        """Get a specific device by ID."""
        if self.data:
            return self.data.get(device_id)
        return None
