"""Config flow for ISS Tracker integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_ISS_POSITION, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ISSTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ISS Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        # Only allow single instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # Test API connectivity
            if await self._test_api_connection():
                return self.async_create_entry(
                    title="ISS Tracker",
                    data={},
                )
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            errors=errors,
        )

    async def _test_api_connection(self) -> bool:
        """Test if we can connect to the API."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(API_ISS_POSITION, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("message") == "success"
        except Exception:
            _LOGGER.exception("Error testing API connection")
        return False
