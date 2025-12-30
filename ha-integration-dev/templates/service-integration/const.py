"""Constants for My Service Integration."""
from __future__ import annotations

from logging import getLogger

DOMAIN = "my_service"
_LOGGER = getLogger(__name__)

# Services
SERVICE_GET_DATA = "get_data"
SERVICE_QUERY_STATUS = "query_status"
SERVICE_EXECUTE_ACTION = "execute_action"

# Attributes
ATTR_DEVICE_ID = "device_id"
ATTR_DATA_TYPE = "data_type"
ATTR_QUERY = "query"
ATTR_ACTION = "action"
ATTR_PARAMETERS = "parameters"
