"""My Service Integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .services import async_setup_services, async_unload_services


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up My Service from config entry."""
    # Initialize data storage
    hass.data.setdefault(DOMAIN, {})

    # Create API client and coordinator
    # client = MyServiceClient(entry.data[CONF_API_KEY])
    # coordinator = MyServiceCoordinator(hass, client)
    # await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    # hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup services (only once)
    if len(hass.data[DOMAIN]) == 0:
        await async_setup_services(hass)

    # Placeholder for coordinator
    hass.data[DOMAIN][entry.entry_id] = {"entry": entry}

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    # Remove entry data
    hass.data[DOMAIN].pop(entry.entry_id, None)

    # Unload services if no entries left
    if not hass.data[DOMAIN]:
        await async_unload_services(hass)

    return True
