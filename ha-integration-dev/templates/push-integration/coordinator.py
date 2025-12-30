"""WebSocket coordinator for My Integration."""
from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PushCoordinator(DataUpdateCoordinator[dict]):
    """WebSocket coordinator for push updates."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # Push-based, no polling
        )

        self._session = async_get_clientsession(hass)
        self._host = entry.data[CONF_HOST]
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._listen_task: asyncio.Task | None = None

    async def async_setup(self) -> None:
        """Set up WebSocket connection."""
        url = f"ws://{self._host}/ws"
        self._ws = await self._session.ws_connect(url)
        self._listen_task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        """Listen for WebSocket messages."""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        self.async_set_updated_data(data)
                    except json.JSONDecodeError:
                        _LOGGER.warning("Invalid JSON received")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOGGER.error("WebSocket error: %s", self._ws.exception())
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as err:
            _LOGGER.error("WebSocket error: %s", err)

    async def async_shutdown(self) -> None:
        """Shut down coordinator."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            await self._ws.close()
