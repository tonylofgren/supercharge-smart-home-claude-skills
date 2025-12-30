# Services and Events

Custom services and event handling for Home Assistant integrations.

## Services

### Basic Service Registration

```python
"""Service registration in __init__.py."""
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    # ... setup code ...

    async def handle_refresh(call: ServiceCall) -> None:
        """Handle refresh service."""
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "refresh",
        handle_refresh,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    # Remove services when last entry unloaded
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, "refresh")

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

### Service with Schema

```python
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

SERVICE_SET_MODE = "set_mode"
SERVICE_SET_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required("mode"): vol.In(["auto", "manual", "eco"]),
        vol.Optional("temperature"): vol.Coerce(float),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services."""

    async def handle_set_mode(call: ServiceCall) -> None:
        """Handle set_mode service."""
        device_id = call.data["device_id"]
        mode = call.data["mode"]
        temperature = call.data.get("temperature")

        # Get client from hass.data
        for entry_id, data in hass.data[DOMAIN].items():
            client = data["client"]
            await client.async_set_mode(device_id, mode, temperature)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MODE,
        handle_set_mode,
        schema=SERVICE_SET_MODE_SCHEMA,
    )
```

### Secure Service Schemas

Use strict validation to prevent injection and abuse:

```python
import re
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# ❌ VULNERABLE - Accepts any string
SERVICE_SCHEMA_UNSAFE = vol.Schema({
    vol.Required("device_id"): cv.string,  # No format validation
    vol.Required("command"): cv.string,     # Any command accepted
})

# ✅ SAFE - Whitelist validation
SERVICE_SCHEMA_SAFE = vol.Schema({
    # Strict device ID format
    vol.Required("device_id"): vol.All(
        cv.string,
        vol.Match(r'^[a-zA-Z0-9_-]+$'),  # Whitelist characters
        vol.Length(min=1, max=64),        # Limit length
    ),
    # Enum for commands - only known values
    vol.Required("command"): vol.In(["on", "off", "toggle", "refresh"]),
    # Bounded numeric values
    vol.Optional("value"): vol.All(
        vol.Coerce(int),
        vol.Range(min=0, max=100),
    ),
})


async def handle_secure_service(call: ServiceCall) -> None:
    """Handle service with secure input."""
    # Schema validates BEFORE this runs - inputs are safe
    device_id = call.data["device_id"]  # Already validated format
    command = call.data["command"]       # Already validated enum

    # Log safely - never log user input without sanitization
    _LOGGER.debug("Executing %s on device %s", command, device_id)
```

### Path and URL Validation in Services

```python
from pathlib import Path
from urllib.parse import urlparse

def validate_safe_filename(value: str) -> str:
    """Validate filename is safe (no path traversal)."""
    if "/" in value or "\\" in value or ".." in value:
        raise vol.Invalid("Invalid filename")
    if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
        raise vol.Invalid("Filename contains invalid characters")
    return value


def validate_https_url(value: str) -> str:
    """Validate URL uses HTTPS."""
    parsed = urlparse(value)
    if parsed.scheme != "https":
        raise vol.Invalid("URL must use HTTPS")
    return value


SERVICE_SCHEMA_WITH_URL = vol.Schema({
    vol.Required("callback_url"): vol.All(
        cv.url,
        validate_https_url,
    ),
    vol.Optional("filename"): validate_safe_filename,
})
```

### services.yaml

Define services for the UI and documentation.

```yaml
# services.yaml
refresh:
  name: Refresh
  description: Refresh data from the device
  fields: {}

set_mode:
  name: Set Mode
  description: Set the operating mode
  fields:
    device_id:
      name: Device ID
      description: The device to control
      required: true
      example: "abc123"
      selector:
        text:
    mode:
      name: Mode
      description: Operating mode
      required: true
      example: "auto"
      selector:
        select:
          options:
            - "auto"
            - "manual"
            - "eco"
    temperature:
      name: Temperature
      description: Target temperature (optional)
      required: false
      example: 22.5
      selector:
        number:
          min: 10
          max: 35
          step: 0.5
          unit_of_measurement: "°C"
```

### Service with Entity Target

```python
from homeassistant.helpers import entity_platform

SERVICE_CUSTOM_ACTION = "custom_action"
SERVICE_CUSTOM_ACTION_SCHEMA = {
    vol.Required("value"): vol.Coerce(int),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up platform with entity services."""
    platform = entity_platform.async_get_current_platform()

    # Register service that targets entities
    platform.async_register_entity_service(
        SERVICE_CUSTOM_ACTION,
        SERVICE_CUSTOM_ACTION_SCHEMA,
        "async_custom_action",  # Method name on entity
    )

    async_add_entities([MyEntity(coordinator, entry)])


class MyEntity(CoordinatorEntity, SensorEntity):
    """Entity with service."""

    async def async_custom_action(self, value: int) -> None:
        """Handle custom action service call."""
        await self.coordinator.client.async_set_value(self._device_id, value)
        await self.coordinator.async_request_refresh()
```

### Service Responses (HA 2024+)

Services can return data using `SupportsResponse`. This enables services to be used in scripts and automations with response variables.

#### Response Modes

```python
from homeassistant.core import SupportsResponse

# Response modes
SupportsResponse.NONE      # No response (default, legacy behavior)
SupportsResponse.ONLY      # Always returns data (cannot be called without response)
SupportsResponse.OPTIONAL  # Can return data if requested
```

#### Basic Service Response

```python
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services with response."""

    async def handle_get_info(call: ServiceCall) -> ServiceResponse:
        """Handle get_info service with response."""
        device_id = call.data["device_id"]

        for entry_id, data in hass.data[DOMAIN].items():
            client = data["client"]
            info = await client.async_get_device_info(device_id)
            return {
                "device_id": device_id,
                "firmware": info["firmware"],
                "uptime": info["uptime"],
                "model": info["model"],
            }

        return {"error": "Device not found"}

    hass.services.async_register(
        DOMAIN,
        "get_info",
        handle_get_info,
        schema=vol.Schema({vol.Required("device_id"): cv.string}),
        supports_response=SupportsResponse.ONLY,
    )
```

#### Optional Response

```python
async def handle_set_mode(call: ServiceCall) -> ServiceResponse:
    """Set mode with optional response."""
    device_id = call.data["device_id"]
    mode = call.data["mode"]

    client = get_client(hass, device_id)
    result = await client.async_set_mode(mode)

    # Return data if response was requested
    if call.return_response:
        return {
            "device_id": device_id,
            "new_mode": mode,
            "previous_mode": result.previous_mode,
            "timestamp": result.timestamp.isoformat(),
        }

    return None


hass.services.async_register(
    DOMAIN,
    "set_mode",
    handle_set_mode,
    schema=vol.Schema({
        vol.Required("device_id"): cv.string,
        vol.Required("mode"): vol.In(["auto", "manual", "eco"]),
    }),
    supports_response=SupportsResponse.OPTIONAL,
)
```

#### services.yaml for Response Services

```yaml
# services.yaml
get_info:
  name: Get Device Info
  description: Get detailed device information
  fields:
    device_id:
      name: Device ID
      description: The device identifier
      required: true
      selector:
        text:

get_statistics:
  name: Get Statistics
  description: Retrieve usage statistics for a device
  fields:
    device_id:
      name: Device ID
      required: true
      selector:
        device:
          integration: my_integration
    period:
      name: Period
      description: Time period for statistics
      required: true
      selector:
        select:
          options:
            - "day"
            - "week"
            - "month"
```

#### Using Response in Automations

```yaml
# automation.yaml
automation:
  - trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: my_integration.get_info
        data:
          device_id: "abc123"
        response_variable: device_info
      - service: notify.mobile
        data:
          message: "Device firmware: {{ device_info.firmware }}"
```

#### Returning Lists and Complex Data

```python
async def handle_list_devices(call: ServiceCall) -> ServiceResponse:
    """List all devices with details."""
    include_offline = call.data.get("include_offline", False)

    devices = []
    for entry_id, data in hass.data[DOMAIN].items():
        for device in data["coordinator"].data["devices"]:
            if include_offline or device["online"]:
                devices.append({
                    "id": device["id"],
                    "name": device["name"],
                    "online": device["online"],
                    "last_seen": device["last_seen"].isoformat(),
                })

    return {"devices": devices, "count": len(devices)}
```

---

## Events

### Firing Events

```python
from homeassistant.core import HomeAssistant

# Fire event
hass.bus.async_fire(
    f"{DOMAIN}_device_connected",
    {
        "device_id": "abc123",
        "ip_address": "192.168.1.100",
    },
)

# Fire with context
from homeassistant.core import Context

context = Context(user_id=user.id)
hass.bus.async_fire(
    f"{DOMAIN}_action_completed",
    {"action": "restart"},
    context=context,
)
```

### Listening for Events

```python
from homeassistant.core import Event


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with event listener."""

    async def handle_event(event: Event) -> None:
        """Handle event."""
        device_id = event.data.get("device_id")
        _LOGGER.info("Device %s connected", device_id)

    # Register listener
    remove_listener = hass.bus.async_listen(
        f"{DOMAIN}_device_connected",
        handle_event,
    )

    # Clean up on unload
    entry.async_on_unload(remove_listener)

    return True
```

### State Change Events

```python
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import Event


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with state listener."""

    async def handle_state_change(event: Event) -> None:
        """Handle state change."""
        entity_id = event.data.get("entity_id")
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")

        if entity_id == "sensor.target_sensor":
            _LOGGER.info(
                "Sensor changed from %s to %s",
                old_state.state if old_state else None,
                new_state.state if new_state else None,
            )

    remove_listener = hass.bus.async_listen(
        EVENT_STATE_CHANGED,
        handle_state_change,
    )

    entry.async_on_unload(remove_listener)
    return True
```

### Using async_track_state_change_event

```python
from homeassistant.helpers.event import async_track_state_change_event


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with state tracker."""

    @callback
    def handle_state_change(event: Event) -> None:
        """Handle specific entity state change."""
        new_state = event.data.get("new_state")
        if new_state:
            _LOGGER.info("New state: %s", new_state.state)

    # Track specific entities
    remove_listener = async_track_state_change_event(
        hass,
        ["sensor.temperature", "sensor.humidity"],
        handle_state_change,
    )

    entry.async_on_unload(remove_listener)
    return True
```

---

## Device Triggers

Allow automations to trigger on device events.

### device_trigger.py

```python
"""Device triggers for My Integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

TRIGGER_TYPES = {"button_pressed", "motion_detected", "device_offline"}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """Return list of triggers for device."""
    triggers = []

    for trigger_type in TRIGGER_TYPES:
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: trigger_type,
            }
        )

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: f"{DOMAIN}_event",
            event_trigger.CONF_EVENT_DATA: {
                CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                CONF_TYPE: config[CONF_TYPE],
            },
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
```

### Firing Device Trigger Events

```python
# In coordinator or entity when event occurs
hass.bus.async_fire(
    f"{DOMAIN}_event",
    {
        CONF_DEVICE_ID: device_id,
        CONF_TYPE: "button_pressed",
    },
)
```

### strings.json for Triggers

```json
{
  "device_automation": {
    "trigger_type": {
      "button_pressed": "Button pressed",
      "motion_detected": "Motion detected",
      "device_offline": "Device went offline"
    }
  }
}
```

---

## Device Conditions

### device_condition.py

```python
"""Device conditions for My Integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_CONDITION, CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import condition, config_validation as cv
from homeassistant.helpers.typing import ConfigType, TemplateVarsType

from .const import DOMAIN

CONDITION_TYPES = {"is_on", "is_off", "is_online"}

CONDITION_SCHEMA = cv.DEVICE_CONDITION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(CONDITION_TYPES),
    }
)


async def async_get_conditions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """Return conditions for device."""
    conditions = []

    for condition_type in CONDITION_TYPES:
        conditions.append(
            {
                CONF_CONDITION: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: condition_type,
            }
        )

    return conditions


@callback
def async_condition_from_config(
    hass: HomeAssistant, config: ConfigType
) -> condition.ConditionCheckerType:
    """Create condition from config."""

    @callback
    def test_condition(hass: HomeAssistant, variables: TemplateVarsType) -> bool:
        """Test the condition."""
        device_id = config[CONF_DEVICE_ID]
        condition_type = config[CONF_TYPE]

        # Get device state from coordinator
        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            coordinator = data.get("coordinator")
            if coordinator and device_id in coordinator.data:
                device_data = coordinator.data[device_id]

                if condition_type == "is_on":
                    return device_data.get("on", False)
                if condition_type == "is_off":
                    return not device_data.get("on", True)
                if condition_type == "is_online":
                    return device_data.get("online", False)

        return False

    return test_condition
```

---

## Device Actions

### device_action.py

```python
"""Device actions for My Integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType, TemplateVarsType

from .const import DOMAIN

ACTION_TYPES = {"turn_on", "turn_off", "restart"}

ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
    }
)


async def async_get_actions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """Return actions for device."""
    actions = []

    for action_type in ACTION_TYPES:
        actions.append(
            {
                CONF_DOMAIN: DOMAIN,
                CONF_DEVICE_ID: device_id,
                CONF_TYPE: action_type,
            }
        )

    return actions


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: TemplateVarsType,
    context: Context | None,
) -> None:
    """Execute device action."""
    device_id = config[CONF_DEVICE_ID]
    action_type = config[CONF_TYPE]

    for entry_id, data in hass.data.get(DOMAIN, {}).items():
        client = data.get("client")
        if client:
            if action_type == "turn_on":
                await client.async_set_power(device_id, True)
            elif action_type == "turn_off":
                await client.async_set_power(device_id, False)
            elif action_type == "restart":
                await client.async_restart(device_id)
```

---

## Best Practices

### Services

- Use descriptive service names
- Validate all input with voluptuous schemas
- Document in services.yaml
- Use entity services for entity-specific actions
- Clean up services when integration unloaded

### Events

- Prefix event names with domain: `{DOMAIN}_event_name`
- Include relevant data in event payload
- Use async_track_state_change_event for entity tracking
- Clean up listeners on unload

### Device Automation

- Implement triggers, conditions, and actions
- Use strings.json for UI labels
- Fire events for device triggers

---

For device registry, see `device-registry.md`.
For architecture overview, see `architecture.md`.
