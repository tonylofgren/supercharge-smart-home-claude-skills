"""Sensor platform for My Integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    async_add_entities([MySensor(entry)])


class MySensor(SensorEntity):
    """My sensor."""

    _attr_has_entity_name = True
    _attr_name = "Status"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize sensor."""
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str | None:
        """Return state."""
        return "OK"
