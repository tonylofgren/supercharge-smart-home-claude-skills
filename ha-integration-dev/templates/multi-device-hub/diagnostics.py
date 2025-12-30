"""Diagnostics for My Smart Hub."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MyHubCoordinator

TO_REDACT = {CONF_API_KEY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for config entry."""
    coordinator: MyHubCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Serialize devices
    devices_data = {}
    for device_id, device in coordinator.data.items():
        devices_data[device_id] = {
            "name": device.name,
            "model": device.model,
            "firmware": device.firmware,
            "online": device.online,
            "sensors": device.sensors,
            "switches": device.switches,
        }

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "hub_info": coordinator.hub_info,
        "devices": devices_data,
        "last_update_success": coordinator.last_update_success,
    }
