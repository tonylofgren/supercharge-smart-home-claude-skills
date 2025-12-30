"""Data coordinator for My Integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator[dict]):
    """Data update coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self._session = async_get_clientsession(hass)
        self._host = entry.data[CONF_HOST]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            # TODO: Replace with actual API call
            async with self._session.get(
                f"http://{self._host}/api/status"
            ) as response:
                if response.status == 401:
                    raise ConfigEntryAuthFailed("Invalid credentials")
                response.raise_for_status()
                return await response.json()
        except ConfigEntryAuthFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
