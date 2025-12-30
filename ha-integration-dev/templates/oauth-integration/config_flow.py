"""OAuth2 config flow for My Integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=DOMAIN,
):
    """Handle OAuth2 config flow."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data for authorization."""
        return {
            "scope": "read write",
        }

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create entry from OAuth data."""
        # Get user info from API
        token = data["token"]["access_token"]

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.example.com/me",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                if response.status != 200:
                    return self.async_abort(reason="oauth_error")
                user_info = await response.json()

        # Check for existing entry
        await self.async_set_unique_id(user_info["id"])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_info.get("name", "My Account"),
            data=data,
        )
