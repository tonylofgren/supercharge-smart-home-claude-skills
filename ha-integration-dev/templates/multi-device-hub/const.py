"""Constants for My Smart Hub integration."""
from __future__ import annotations

from logging import getLogger

DOMAIN = "my_hub"
_LOGGER = getLogger(__name__)

# Configuration
CONF_HUB_ID = "hub_id"

# Defaults
DEFAULT_SCAN_INTERVAL = 30

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "switch"]
