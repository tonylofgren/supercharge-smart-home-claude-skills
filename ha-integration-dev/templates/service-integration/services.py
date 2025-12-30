"""Services for My Service Integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ACTION,
    ATTR_DATA_TYPE,
    ATTR_DEVICE_ID,
    ATTR_PARAMETERS,
    ATTR_QUERY,
    DOMAIN,
    SERVICE_EXECUTE_ACTION,
    SERVICE_GET_DATA,
    SERVICE_QUERY_STATUS,
    _LOGGER,
)

# Service schemas
GET_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_DATA_TYPE, default="status"): vol.In(
            ["status", "history", "config"]
        ),
    }
)

QUERY_STATUS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_QUERY): cv.string,
    }
)

EXECUTE_ACTION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_ACTION): vol.In(["restart", "refresh", "clear_cache"]),
        vol.Optional(ATTR_PARAMETERS): dict,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up integration services."""

    async def handle_get_data(call: ServiceCall) -> ServiceResponse:
        """Handle get_data service - returns data only."""
        device_id = call.data[ATTR_DEVICE_ID]
        data_type = call.data[ATTR_DATA_TYPE]

        # Get coordinator (assumes single entry for simplicity)
        if not hass.data.get(DOMAIN):
            return {"error": "Integration not configured"}

        coordinator = next(iter(hass.data[DOMAIN].values()))

        # Fetch data based on type
        if data_type == "status":
            data = await coordinator.client.async_get_status(device_id)
        elif data_type == "history":
            data = await coordinator.client.async_get_history(device_id)
        else:  # config
            data = await coordinator.client.async_get_config(device_id)

        return {
            "device_id": device_id,
            "data_type": data_type,
            "data": data,
        }

    async def handle_query_status(call: ServiceCall) -> ServiceResponse | None:
        """Handle query_status service - optional response."""
        device_id = call.data[ATTR_DEVICE_ID]
        query = call.data.get(ATTR_QUERY)

        coordinator = next(iter(hass.data[DOMAIN].values()))

        # Get status
        status = await coordinator.client.async_query(device_id, query)

        # Return response only if caller expects it
        if call.return_response:
            return {
                "device_id": device_id,
                "query": query,
                "result": status,
            }
        return None

    async def handle_execute_action(call: ServiceCall) -> None:
        """Handle execute_action service - no response."""
        device_id = call.data[ATTR_DEVICE_ID]
        action = call.data[ATTR_ACTION]
        parameters = call.data.get(ATTR_PARAMETERS, {})

        coordinator = next(iter(hass.data[DOMAIN].values()))

        # Execute action
        await coordinator.client.async_execute(device_id, action, parameters)

        _LOGGER.info("Executed %s on device %s", action, device_id)

    # Register services with appropriate response modes

    # SupportsResponse.ONLY - Always returns data, used for queries
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_DATA,
        handle_get_data,
        schema=GET_DATA_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    # SupportsResponse.OPTIONAL - Returns data when requested
    hass.services.async_register(
        DOMAIN,
        SERVICE_QUERY_STATUS,
        handle_query_status,
        schema=QUERY_STATUS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    # SupportsResponse.NONE (default) - Never returns data
    hass.services.async_register(
        DOMAIN,
        SERVICE_EXECUTE_ACTION,
        handle_execute_action,
        schema=EXECUTE_ACTION_SCHEMA,
        # supports_response=SupportsResponse.NONE is default
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload integration services."""
    hass.services.async_remove(DOMAIN, SERVICE_GET_DATA)
    hass.services.async_remove(DOMAIN, SERVICE_QUERY_STATUS)
    hass.services.async_remove(DOMAIN, SERVICE_EXECUTE_ACTION)
