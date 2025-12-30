"""Constants for the ISS Tracker integration."""

from typing import Final

DOMAIN: Final = "iss_tracker"

# API endpoints
API_ISS_POSITION: Final = "http://api.open-notify.org/iss-now.json"
API_ASTROS: Final = "http://api.open-notify.org/astros.json"

# Update intervals (seconds)
UPDATE_INTERVAL_POSITION: Final = 30  # ISS position updates
UPDATE_INTERVAL_ASTROS: Final = 3600  # Astronaut count (hourly, rarely changes)

# Attribution
ATTRIBUTION: Final = "Data provided by Open Notify API"
