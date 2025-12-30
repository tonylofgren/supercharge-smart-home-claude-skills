"""API client for My Smart Hub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


@dataclass
class HubDevice:
    """Representation of a hub device."""

    id: str
    name: str
    model: str
    firmware: str
    online: bool
    sensors: dict[str, Any]
    switches: dict[str, bool]


class MyHubApiError(Exception):
    """Base exception for API errors."""


class MyHubAuthError(MyHubApiError):
    """Authentication error."""


class MyHubConnectionError(MyHubApiError):
    """Connection error."""


class MyHubClient:
    """API client for My Smart Hub."""

    def __init__(self, host: str, api_key: str) -> None:
        """Initialize the client."""
        self.host = host
        self.api_key = api_key
        self._session: aiohttp.ClientSession | None = None

    async def async_get_hub_info(self) -> dict[str, Any]:
        """Get hub information."""
        return await self._request("GET", "/api/hub")

    async def async_get_devices(self) -> list[HubDevice]:
        """Get all devices connected to hub."""
        data = await self._request("GET", "/api/devices")
        return [
            HubDevice(
                id=d["id"],
                name=d["name"],
                model=d["model"],
                firmware=d["firmware"],
                online=d["online"],
                sensors=d.get("sensors", {}),
                switches=d.get("switches", {}),
            )
            for d in data.get("devices", [])
        ]

    async def async_turn_on(self, device_id: str, switch_id: str) -> None:
        """Turn on a switch."""
        await self._request(
            "POST",
            f"/api/devices/{device_id}/switches/{switch_id}",
            json={"state": True},
        )

    async def async_turn_off(self, device_id: str, switch_id: str) -> None:
        """Turn off a switch."""
        await self._request(
            "POST",
            f"/api/devices/{device_id}/switches/{switch_id}",
            json={"state": False},
        )

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make API request."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"http://{self.host}{path}"

        try:
            async with self._session.request(
                method, url, headers=headers, **kwargs
            ) as resp:
                if resp.status == 401:
                    raise MyHubAuthError("Invalid API key")
                if resp.status >= 400:
                    raise MyHubApiError(f"API error: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise MyHubConnectionError(f"Connection error: {err}") from err

    async def async_close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
