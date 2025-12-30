# Testing

pytest patterns for Home Assistant custom integrations.

## Setup

### pytest-homeassistant-custom-component

```bash
pip install pytest-homeassistant-custom-component
```

### conftest.py

```python
"""Fixtures for tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.my_integration.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture
def mock_client() -> Generator[AsyncMock, None, None]:
    """Create mock API client."""
    with patch(
        "custom_components.my_integration.MyApiClient",
        autospec=True,
    ) as mock:
        client = mock.return_value
        client.async_get_data.return_value = {
            "temperature": 22.5,
            "humidity": 45,
        }
        client.async_validate_connection.return_value = True
        yield client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Device",
        data={
            "host": "192.168.1.100",
            "api_key": "test-key",
        },
        unique_id="test-unique-id",
    )
```

---

## Config Flow Tests

### test_config_flow.py

```python
"""Test config flow."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.my_integration.const import DOMAIN


async def test_user_flow_success(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "192.168.1.100", "api_key": "test-key"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "192.168.1.100"
    assert result["data"] == {
        "host": "192.168.1.100",
        "api_key": "test-key",
    }


async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test connection error."""
    mock_client.async_validate_connection.side_effect = ConnectionError

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "192.168.1.100", "api_key": "test-key"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_auth(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test invalid authentication."""
    mock_client.async_validate_connection.side_effect = AuthenticationError

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "192.168.1.100", "api_key": "bad-key"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test already configured."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "192.168.1.100", "api_key": "test-key"},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
```

### Options Flow Tests

```python
async def test_options_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test options flow."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"scan_interval": 120},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {"scan_interval": 120}
```

---

## Integration Setup Tests

### test_init.py

```python
"""Test integration setup."""
import pytest
from unittest.mock import AsyncMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.my_integration.const import DOMAIN


async def test_setup_entry(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test successful setup."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert DOMAIN in hass.data


async def test_setup_entry_connection_error(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup with connection error."""
    mock_client.async_get_data.side_effect = ConnectionError

    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_entry_auth_error(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup with auth error triggers reauth."""
    mock_client.async_get_data.side_effect = AuthenticationError

    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR

    # Check reauth flow started
    flows = hass.config_entries.flow.async_progress()
    assert len(flows) == 1
    assert flows[0]["context"]["source"] == "reauth"


async def test_unload_entry(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test entry unload."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})
```

---

## Entity Tests

### test_sensor.py

```python
"""Test sensor platform."""
import pytest
from unittest.mock import AsyncMock

from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from custom_components.my_integration.const import DOMAIN


async def test_sensor_state(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensor state."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_device_temperature")

    assert state is not None
    assert state.state == "22.5"
    assert state.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS


async def test_sensor_unavailable(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensor unavailable on error."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Simulate update failure
    mock_client.async_get_data.side_effect = ConnectionError

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=60))
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_device_temperature")
    assert state.state == STATE_UNAVAILABLE


async def test_sensor_update(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensor updates."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Initial state
    state = hass.states.get("sensor.test_device_temperature")
    assert state.state == "22.5"

    # Update data
    mock_client.async_get_data.return_value = {"temperature": 25.0}

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=60))
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_device_temperature")
    assert state.state == "25.0"
```

### test_switch.py

```python
"""Test switch platform."""
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)


async def test_switch_turn_on(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test switch turn on."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.test_device_power"},
        blocking=True,
    )

    mock_client.async_set_power.assert_called_once_with(True)


async def test_switch_turn_off(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test switch turn off."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.test_device_power"},
        blocking=True,
    )

    mock_client.async_set_power.assert_called_once_with(False)
```

---

## Coordinator Tests

### test_coordinator.py

```python
"""Test coordinator."""
import pytest
from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.my_integration.coordinator import MyCoordinator


async def test_coordinator_update(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test coordinator data update."""
    coordinator = MyCoordinator(hass, mock_config_entry, mock_client)

    await coordinator.async_config_entry_first_refresh()

    assert coordinator.data == {"temperature": 22.5, "humidity": 45}
    assert coordinator.last_update_success is True


async def test_coordinator_update_error(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test coordinator handles errors."""
    mock_client.async_get_data.side_effect = ConnectionError("Connection failed")

    coordinator = MyCoordinator(hass, mock_config_entry, mock_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_coordinator_auth_error(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test coordinator handles auth errors."""
    mock_client.async_get_data.side_effect = AuthenticationError

    coordinator = MyCoordinator(hass, mock_config_entry, mock_client)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()
```

---

## Service Tests

### test_services.py

```python
"""Test services."""
from homeassistant.core import HomeAssistant

from custom_components.my_integration.const import DOMAIN


async def test_refresh_service(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test refresh service."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        DOMAIN,
        "refresh",
        {},
        blocking=True,
    )

    # Verify client was called
    assert mock_client.async_get_data.call_count >= 2  # Initial + refresh


async def test_set_mode_service(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test set_mode service."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        DOMAIN,
        "set_mode",
        {"device_id": "device_123", "mode": "eco"},
        blocking=True,
    )

    mock_client.async_set_mode.assert_called_once_with("device_123", "eco", None)
```

---

## Mocking Patterns

### Mock API Response

```python
@pytest.fixture
def mock_client():
    """Mock client with responses."""
    with patch("custom_components.my_integration.MyApiClient") as mock:
        client = mock.return_value

        # Simple return value
        client.async_get_data.return_value = {"temperature": 22.5}

        # Side effect for multiple calls
        client.async_get_data.side_effect = [
            {"temperature": 20.0},
            {"temperature": 22.0},
            {"temperature": 24.0},
        ]

        # Async mock
        client.async_get_data = AsyncMock(return_value={"temperature": 22.5})

        yield client
```

### Mock Time

```python
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_fire_time_changed


async def test_scheduled_update(hass: HomeAssistant) -> None:
    """Test scheduled coordinator update."""
    # ... setup ...

    # Advance time by 60 seconds
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=60))
    await hass.async_block_till_done()

    # Verify update occurred
    assert mock_client.async_get_data.call_count == 2
```

### Mock aiohttp

```python
from aioresponses import aioresponses


async def test_api_request(hass: HomeAssistant) -> None:
    """Test API request."""
    with aioresponses() as mock:
        mock.get(
            "https://api.example.com/data",
            payload={"temperature": 22.5},
        )

        client = MyApiClient(hass, "api.example.com", "key")
        data = await client.async_get_data()

        assert data["temperature"] == 22.5
```

---

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_config_flow.py      # Config flow tests
├── test_init.py             # Setup/unload tests
├── test_coordinator.py      # Coordinator tests
├── test_sensor.py           # Sensor tests
├── test_switch.py           # Switch tests
├── test_services.py         # Service tests
└── test_diagnostics.py      # Diagnostics tests
```

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config_flow.py

# Run specific test
pytest tests/test_config_flow.py::test_user_flow_success

# With coverage
pytest tests/ --cov=custom_components/my_integration --cov-report=html

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x
```

---

## Best Practices

- Use `async_block_till_done()` after state changes
- Mock external APIs, don't make real requests
- Test error conditions, not just happy path
- Use fixtures for common setup
- Test config flow, setup, and entity states
- Verify cleanup in unload tests

---

For debugging tips, see `debugging.md`.
For coordinator patterns, see `coordinator.md`.
