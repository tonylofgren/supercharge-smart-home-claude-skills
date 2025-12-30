"""My Smart Hub integration.

Generated with ha-integration@aurora-smart-home v1.0.0
https://github.com/tonylofgren/aurora-smart-home
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .api import MyHubApiError, MyHubClient
from .coordinator import MyHubCoordinator
from .const import DOMAIN, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up My Smart Hub from config entry."""
    # Create API client
    client = MyHubClient(entry.data[CONF_HOST], entry.data[CONF_API_KEY])

    # Create coordinator
    coordinator = MyHubCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register hub device (parent of all child devices)
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=coordinator.hub_info.get("name", "My Hub"),
        manufacturer="My Hub Manufacturer",
        model=coordinator.hub_info.get("model", "Hub"),
        sw_version=coordinator.hub_info.get("firmware"),
        configuration_url=f"http://{entry.data[CONF_HOST]}",
    )

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Close client
        coordinator: MyHubCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.async_close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
