"""The ISS Tracker integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import ISSPositionCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type ISSConfigEntry = ConfigEntry[ISSPositionCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ISSConfigEntry) -> bool:
    """Set up ISS Tracker from a config entry."""
    coordinator = ISSPositionCoordinator(hass)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.data:
        raise ConfigEntryNotReady("Unable to fetch ISS data")

    # Store coordinator in runtime_data (modern pattern)
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ISSConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
