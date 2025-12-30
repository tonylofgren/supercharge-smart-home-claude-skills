"""DataUpdateCoordinator for ISS Tracker."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ASTROS,
    API_ISS_POSITION,
    DOMAIN,
    UPDATE_INTERVAL_ASTROS,
    UPDATE_INTERVAL_POSITION,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class ISSData:
    """Data class for ISS tracker data."""

    latitude: float
    longitude: float
    timestamp: int
    people_in_space: int
    astronauts: list[dict[str, str]]


class ISSPositionCoordinator(DataUpdateCoordinator[ISSData]):
    """Coordinator for fetching ISS position and astronaut data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_POSITION),
        )
        self._session = async_get_clientsession(hass)
        self._astros_data: dict[str, Any] = {}
        self._astros_update_count = 0

    async def _async_update_data(self) -> ISSData:
        """Fetch data from the API."""
        try:
            # Fetch ISS position
            position_data = await self._fetch_iss_position()

            # Fetch astronaut data less frequently
            self._astros_update_count += 1
            if (
                not self._astros_data
                or self._astros_update_count
                >= UPDATE_INTERVAL_ASTROS // UPDATE_INTERVAL_POSITION
            ):
                self._astros_data = await self._fetch_astronauts()
                self._astros_update_count = 0

            return ISSData(
                latitude=float(position_data["iss_position"]["latitude"]),
                longitude=float(position_data["iss_position"]["longitude"]),
                timestamp=position_data["timestamp"],
                people_in_space=self._astros_data.get("number", 0),
                astronauts=self._astros_data.get("people", []),
            )

        except Exception as err:
            raise UpdateFailed(f"Error fetching ISS data: {err}") from err

    async def _fetch_iss_position(self) -> dict[str, Any]:
        """Fetch current ISS position."""
        async with self._session.get(API_ISS_POSITION) as response:
            if response.status != 200:
                raise UpdateFailed(f"API returned status {response.status}")
            data = await response.json()
            if data.get("message") != "success":
                raise UpdateFailed("API returned unsuccessful response")
            return data

    async def _fetch_astronauts(self) -> dict[str, Any]:
        """Fetch astronauts currently in space."""
        async with self._session.get(API_ASTROS) as response:
            if response.status != 200:
                raise UpdateFailed(f"Astros API returned status {response.status}")
            data = await response.json()
            if data.get("message") != "success":
                raise UpdateFailed("Astros API returned unsuccessful response")
            return data
