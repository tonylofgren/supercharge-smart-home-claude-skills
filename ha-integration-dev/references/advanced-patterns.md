# Advanced Patterns

Expert-level patterns for Home Assistant integrations.

## Multi-Coordinator Pattern

Use multiple coordinators when an integration needs to fetch different types of data at different intervals.

### When to Use

- Different API endpoints with different rate limits
- Data that updates at different frequencies
- Separate data sources (cloud + local)
- Independent failure domains

### Implementation

```python
# coordinator.py
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import MyApiClient


class DeviceCoordinator(DataUpdateCoordinator):
    """Coordinator for device state (fast updates)."""

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize device coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="device_state",
            update_interval=timedelta(seconds=30),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch device state."""
        return await self.client.async_get_device_state()


class StatisticsCoordinator(DataUpdateCoordinator):
    """Coordinator for statistics (slow updates)."""

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize statistics coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="statistics",
            update_interval=timedelta(hours=1),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch statistics data."""
        return await self.client.async_get_statistics()


class FirmwareCoordinator(DataUpdateCoordinator):
    """Coordinator for firmware updates (very slow)."""

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize firmware coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="firmware",
            update_interval=timedelta(hours=24),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Check for firmware updates."""
        return await self.client.async_check_firmware()
```

### Runtime Data Structure

```python
# __init__.py
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import DeviceCoordinator, StatisticsCoordinator, FirmwareCoordinator


@dataclass
class MyRuntimeData:
    """Runtime data with multiple coordinators."""

    device: DeviceCoordinator
    statistics: StatisticsCoordinator
    firmware: FirmwareCoordinator


type MyConfigEntry = ConfigEntry[MyRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up with multiple coordinators."""
    client = MyApiClient(entry.data["host"])

    # Create coordinators
    device_coordinator = DeviceCoordinator(hass, client)
    stats_coordinator = StatisticsCoordinator(hass, client)
    firmware_coordinator = FirmwareCoordinator(hass, client)

    # Fetch initial data in parallel
    await asyncio.gather(
        device_coordinator.async_config_entry_first_refresh(),
        stats_coordinator.async_config_entry_first_refresh(),
        firmware_coordinator.async_config_entry_first_refresh(),
    )

    entry.runtime_data = MyRuntimeData(
        device=device_coordinator,
        statistics=stats_coordinator,
        firmware=firmware_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
```

### Entities Using Multiple Coordinators

```python
# sensor.py
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class DeviceSensor(CoordinatorEntity[DeviceCoordinator], SensorEntity):
    """Sensor using device coordinator (fast updates)."""

    def __init__(self, runtime_data: MyRuntimeData, entry: ConfigEntry) -> None:
        super().__init__(runtime_data.device)
        self._runtime_data = runtime_data

    @property
    def native_value(self) -> float:
        return self.coordinator.data.get("temperature")


class StatisticsSensor(CoordinatorEntity[StatisticsCoordinator], SensorEntity):
    """Sensor using statistics coordinator (slow updates)."""

    def __init__(self, runtime_data: MyRuntimeData, entry: ConfigEntry) -> None:
        super().__init__(runtime_data.statistics)

    @property
    def native_value(self) -> float:
        return self.coordinator.data.get("total_energy")
```

---

## Conversation Agent Integration

Allow your integration to respond to voice commands via Assist.

### manifest.json

```json
{
  "domain": "my_integration",
  "dependencies": ["conversation"]
}
```

### Basic Conversation Agent

```python
# conversation.py
from homeassistant.components import conversation
from homeassistant.components.conversation import agent
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up conversation platform."""
    conversation.async_set_agent(
        hass,
        entry,
        MyConversationAgent(hass, entry),
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unload conversation platform."""
    conversation.async_unset_agent(hass, entry)


class MyConversationAgent(conversation.AbstractConversationAgent):
    """Conversation agent for My Integration."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize agent."""
        self.hass = hass
        self.entry = entry

    @property
    def supported_languages(self) -> list[str]:
        """Return supported languages."""
        return ["en", "sv"]  # Or "*" for all

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        text = user_input.text.lower()

        # Parse intent from text
        if "turn on" in text:
            response = await self._handle_turn_on(text)
        elif "status" in text or "how is" in text:
            response = await self._handle_status(text)
        else:
            response = "I don't understand that command."

        return conversation.ConversationResult(
            response=agent.IntentResponse(
                speech={"plain": {"speech": response}},
            ),
            conversation_id=user_input.conversation_id,
        )

    async def _handle_turn_on(self, text: str) -> str:
        """Handle turn on command."""
        coordinator = self.hass.data[DOMAIN][self.entry.entry_id]
        await coordinator.client.async_turn_on()
        return "Done! I've turned it on."

    async def _handle_status(self, text: str) -> str:
        """Handle status query."""
        coordinator = self.hass.data[DOMAIN][self.entry.entry_id]
        temp = coordinator.data.get("temperature")
        return f"The current temperature is {temp} degrees."
```

### Intent-Based Agent

```python
from homeassistant.components.conversation import agent
from homeassistant.helpers import intent


class MyIntentAgent(conversation.AbstractConversationAgent):
    """Agent using Home Assistant intents."""

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process using intents."""
        # Let HA handle standard intents
        intent_response = await intent.async_handle(
            self.hass,
            DOMAIN,
            "MyCustomIntent",
            slots={"device": "living_room"},
            text_input=user_input.text,
            language=user_input.language,
        )

        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=user_input.conversation_id,
        )
```

---

## System Health Handler

Report integration health in Settings → System → Repairs.

### system_health.py

```python
"""System health for My Integration."""
from typing import Any

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, API_ENDPOINT


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info, "/config/integrations/integration/my_integration")


async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get system health info."""
    info: dict[str, Any] = {}

    # Check API reachability
    info["api_endpoint"] = system_health.async_check_can_reach_url(
        hass, API_ENDPOINT
    )

    # Check integration status
    if DOMAIN not in hass.data:
        info["status"] = "Not configured"
        return info

    # Aggregate status from all entries
    entries = 0
    devices = 0
    online_devices = 0
    errors = []

    for entry_id, data in hass.data[DOMAIN].items():
        entries += 1
        coordinator = data.get("coordinator")

        if coordinator:
            device_count = len(coordinator.data.get("devices", {}))
            devices += device_count
            online_devices += sum(
                1 for d in coordinator.data.get("devices", {}).values()
                if d.get("online")
            )

            if not coordinator.last_update_success:
                entry = hass.config_entries.async_get_entry(entry_id)
                errors.append(f"{entry.title}: Update failed")

    info["configured_hubs"] = entries
    info["total_devices"] = devices
    info["online_devices"] = f"{online_devices}/{devices}"

    if errors:
        info["errors"] = "; ".join(errors)
    else:
        info["status"] = "OK"

    return info
```

### manifest.json

```json
{
  "after_dependencies": ["system_health"]
}
```

---

## Options Flow with Auto-Reload

Automatically reload integration when options change.

### Pattern 1: Using Update Listener

```python
# __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    # ... setup code ...

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
```

### Pattern 2: Selective Reload

```python
# __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    # Store original options to compare
    hass.data[DOMAIN][entry.entry_id]["original_options"] = dict(entry.options)

    entry.async_on_unload(entry.add_update_listener(async_options_updated))
    return True


async def async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    original = hass.data[DOMAIN][entry.entry_id].get("original_options", {})
    current = dict(entry.options)

    # Check what changed
    scan_interval_changed = original.get("scan_interval") != current.get("scan_interval")
    notification_changed = original.get("notifications") != current.get("notifications")

    if scan_interval_changed:
        # Update coordinator interval without full reload
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        coordinator.update_interval = timedelta(seconds=current["scan_interval"])
        await coordinator.async_request_refresh()
    elif notification_changed:
        # Just update notification settings
        client = hass.data[DOMAIN][entry.entry_id]["client"]
        await client.async_update_notifications(current["notifications"])
    else:
        # Full reload for other changes
        await hass.config_entries.async_reload(entry.entry_id)

    # Update stored options
    hass.data[DOMAIN][entry.entry_id]["original_options"] = current
```

### Pattern 3: Options in Coordinator

```python
# coordinator.py
class MyCoordinator(DataUpdateCoordinator):
    """Coordinator with configurable options."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        # Get interval from options with fallback to data
        interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self.entry = entry

    def update_from_options(self) -> None:
        """Update coordinator from entry options."""
        interval = self.entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        self.update_interval = timedelta(seconds=interval)
```

---

## Websocket API

Expose real-time data via websocket for frontend integrations.

```python
# websocket.py
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register websocket commands."""
    websocket_api.async_register_command(hass, websocket_get_devices)
    websocket_api.async_register_command(hass, websocket_subscribe_updates)


@websocket_api.websocket_command(
    {
        "type": f"{DOMAIN}/devices",
    }
)
@callback
def websocket_get_devices(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Return list of devices."""
    devices = []

    for entry_id, data in hass.data.get(DOMAIN, {}).items():
        coordinator = data.get("coordinator")
        if coordinator and coordinator.data:
            for device_id, device_data in coordinator.data.get("devices", {}).items():
                devices.append({
                    "id": device_id,
                    "name": device_data["name"],
                    "online": device_data["online"],
                })

    connection.send_result(msg["id"], {"devices": devices})


@websocket_api.websocket_command(
    {
        "type": f"{DOMAIN}/subscribe",
    }
)
@websocket_api.async_response
async def websocket_subscribe_updates(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Subscribe to device updates."""

    @callback
    def forward_updates(data: dict) -> None:
        """Forward coordinator updates to websocket."""
        connection.send_message(
            websocket_api.event_message(
                msg["id"],
                {"devices": data.get("devices", {})},
            )
        )

    # Subscribe to coordinator updates
    for entry_id, data in hass.data.get(DOMAIN, {}).items():
        coordinator = data.get("coordinator")
        if coordinator:
            unsub = coordinator.async_add_listener(forward_updates)
            connection.subscriptions[msg["id"]] = unsub

    connection.send_result(msg["id"])
```

### Register in __init__.py

```python
from .websocket import async_register_websocket_api


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    # ... setup code ...

    # Register websocket API (only once)
    if not hass.data[DOMAIN]:
        async_register_websocket_api(hass)

    return True
```

---

## Best Practices

### DO

- Use multiple coordinators for data with different update frequencies
- Implement system health for cloud integrations
- Use selective reload for options when possible
- Provide websocket API for real-time dashboard data
- Clean up resources properly on unload

### DON'T

- Create too many coordinators (keep it manageable)
- Reload on every option change (use selective updates)
- Expose sensitive data via websocket
- Forget to unsubscribe websocket listeners

---

For basic coordinator patterns, see `coordinator.md`.
For entity patterns, see `entities.md`.
