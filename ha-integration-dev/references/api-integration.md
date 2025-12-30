# API Integration

HTTP, OAuth2, and WebSocket patterns for Home Assistant integrations.

## HTTP Client (aiohttp)

### Using Home Assistant's Session

Always use the shared session for proper connection pooling and SSL handling.

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession


class MyApiClient:
    """API client."""

    def __init__(self, hass: HomeAssistant, host: str, api_key: str) -> None:
        """Initialize client."""
        self._session = async_get_clientsession(hass)
        self._host = host
        self._api_key = api_key
        self._base_url = f"https://{host}/api/v1"

    async def async_get_data(self) -> dict:
        """Fetch data from API."""
        async with asyncio.timeout(30):
            response = await self._session.get(
                f"{self._base_url}/data",
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            return await response.json()
```

### Complete API Client

```python
"""API client for My Service."""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    ApiError,
)


class MyApiClient:
    """API client."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        api_key: str,
        timeout: int = 30,
    ) -> None:
        """Initialize client."""
        self._session = async_get_clientsession(hass)
        self._host = host
        self._api_key = api_key
        self._timeout = timeout
        self._base_url = f"https://{host}/api/v1"

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict:
        """Make API request."""
        url = f"{self._base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            **kwargs.pop("headers", {}),
        }

        try:
            async with asyncio.timeout(self._timeout):
                response = await self._session.request(
                    method,
                    url,
                    headers=headers,
                    **kwargs,
                )
        except asyncio.TimeoutError as err:
            raise ConnectionError("Request timed out") from err
        except aiohttp.ClientError as err:
            raise ConnectionError(f"Connection error: {err}") from err

        if response.status == 401:
            raise AuthenticationError("Invalid API key")
        if response.status == 403:
            raise AuthenticationError("Access forbidden")
        if response.status >= 400:
            text = await response.text()
            raise ApiError(f"API error {response.status}: {text}")

        return await response.json()

    async def async_get(self, endpoint: str, **kwargs) -> dict:
        """GET request."""
        return await self._request("GET", endpoint, **kwargs)

    async def async_post(self, endpoint: str, data: dict, **kwargs) -> dict:
        """POST request."""
        return await self._request("POST", endpoint, json=data, **kwargs)

    async def async_put(self, endpoint: str, data: dict, **kwargs) -> dict:
        """PUT request."""
        return await self._request("PUT", endpoint, json=data, **kwargs)

    async def async_delete(self, endpoint: str, **kwargs) -> dict:
        """DELETE request."""
        return await self._request("DELETE", endpoint, **kwargs)

    # Specific methods
    async def async_get_devices(self) -> list[dict]:
        """Get all devices."""
        return await self.async_get("devices")

    async def async_get_device(self, device_id: str) -> dict:
        """Get single device."""
        return await self.async_get(f"devices/{device_id}")

    async def async_set_power(self, device_id: str, on: bool) -> dict:
        """Set device power."""
        return await self.async_post(
            f"devices/{device_id}/power",
            {"on": on},
        )

    async def async_validate_connection(self) -> bool:
        """Test API connection."""
        try:
            await self.async_get("ping")
            return True
        except (ConnectionError, AuthenticationError):
            raise
        except ApiError:
            return True  # API works, just maybe different response
```

### Custom Exceptions

```python
"""Exceptions for My Integration."""


class MyIntegrationError(Exception):
    """Base exception."""


class ConnectionError(MyIntegrationError):
    """Connection error."""


class AuthenticationError(MyIntegrationError):
    """Authentication error."""


class ApiError(MyIntegrationError):
    """API error."""


class RateLimitError(MyIntegrationError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")
```

---

## Security: HTTPS & SSL

### HTTPS Enforcement

**Always use HTTPS for cloud APIs:**

```python
# ❌ AVOID - Credentials sent in plaintext
self._base_url = f"http://{host}/api"

# ✅ CORRECT - Encrypted communication
self._base_url = f"https://{host}/api"
```

### SSL Certificate Handling

```python
import ssl
import certifi
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# Standard: Use HA's session (validates certificates)
session = async_get_clientsession(hass)

# Local devices with self-signed certificates
session = async_get_clientsession(hass, verify_ssl=False)

# Custom SSL context for specific requirements
ssl_context = ssl.create_default_context(cafile=certifi.where())
connector = aiohttp.TCPConnector(ssl=ssl_context)
```

### Config Flow SSL Option

```python
STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_API_KEY): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),
    vol.Optional(CONF_VERIFY_SSL, default=True): bool,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with configurable SSL."""
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)
    session = async_get_clientsession(hass, verify_ssl=verify_ssl)
```

---

## Rate Limiting & HTTP 429

### HTTP 429 Handling

```python
async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
    """Make API request with rate limit handling."""
    url = f"{self._base_url}/{endpoint}"
    headers = {"Authorization": f"Bearer {self._api_key}"}

    try:
        async with asyncio.timeout(self._timeout):
            response = await self._session.request(method, url, headers=headers, **kwargs)
    except asyncio.TimeoutError as err:
        raise ConnectionError("Request timed out") from err

    # Handle rate limiting
    if response.status == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        raise RateLimitError(retry_after)

    if response.status == 401:
        raise AuthenticationError("Invalid credentials")

    if response.status >= 400:
        raise ApiError(f"API error: {response.status}")

    return await response.json()
```

### Exponential Backoff with Jitter

```python
import asyncio
from random import uniform

async def request_with_backoff(
    self,
    method: str,
    endpoint: str,
    max_retries: int = 5,
    base_delay: float = 1.0,
    **kwargs,
) -> dict:
    """Make request with exponential backoff."""
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            return await self._request(method, endpoint, **kwargs)
        except RateLimitError as err:
            last_error = err
            if attempt == max_retries - 1:
                raise

            # Use server's retry-after or calculate backoff
            delay = max(
                err.retry_after,
                base_delay * (2 ** attempt) + uniform(0, 1)
            )
            _LOGGER.debug(
                "Rate limited, retry in %.1fs (attempt %d/%d)",
                delay, attempt + 1, max_retries
            )
            await asyncio.sleep(delay)
        except (ConnectionError, aiohttp.ClientError) as err:
            last_error = err
            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + uniform(0, 1)
            _LOGGER.debug(
                "Request failed, retry in %.1fs (attempt %d/%d): %s",
                delay, attempt + 1, max_retries, err
            )
            await asyncio.sleep(delay)

    raise last_error
```

### Coordinator with Rate Limit Awareness

```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

class MyCoordinator(DataUpdateCoordinator):
    """Coordinator with rate limit handling."""

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.client = client
        self._rate_limit_until: datetime | None = None

    async def _async_update_data(self) -> dict:
        """Fetch data with rate limit awareness."""
        # Check if we're still rate limited
        if self._rate_limit_until and datetime.now() < self._rate_limit_until:
            remaining = (self._rate_limit_until - datetime.now()).seconds
            raise UpdateFailed(f"Rate limited, {remaining}s remaining")

        try:
            return await self.client.async_get_data()
        except RateLimitError as err:
            self._rate_limit_until = datetime.now() + timedelta(seconds=err.retry_after)
            raise UpdateFailed(f"Rate limited for {err.retry_after}s") from err
```

---

## OAuth2 Authentication

### Application Credentials

For cloud services using OAuth2, register as an application credentials provider.

#### manifest.json

```json
{
  "domain": "my_integration",
  "dependencies": ["application_credentials"],
  "requirements": []
}
```

#### application_credentials.py

```python
"""Application credentials for My Integration."""
from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant

AUTHORIZATION_SERVER = AuthorizationServer(
    authorize_url="https://auth.example.com/oauth/authorize",
    token_url="https://auth.example.com/oauth/token",
)


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AUTHORIZATION_SERVER


async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    """Return description placeholders for config flow."""
    return {
        "more_info_url": "https://example.com/oauth-setup",
        "oauth_consent_url": "https://example.com/developer/apps",
    }
```

#### config_flow.py with OAuth2

```python
"""Config flow with OAuth2."""
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=DOMAIN,
):
    """Handle OAuth2 config flow."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data for authorization."""
        return {
            "scope": "read write",
        }

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create entry from OAuth data."""
        # Get user info from API
        async with aiohttp.ClientSession() as session:
            token = data["token"]["access_token"]
            async with session.get(
                "https://api.example.com/me",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                user_info = await response.json()

        # Check for existing entry
        await self.async_set_unique_id(user_info["id"])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_info["name"],
            data=data,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauth."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()
```

### Using OAuth2 Token

```python
"""API client with OAuth2."""
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)


class OAuth2ApiClient:
    """OAuth2 API client."""

    def __init__(
        self,
        session: OAuth2Session,
    ) -> None:
        """Initialize client."""
        self._session = session

    async def async_get_data(self) -> dict:
        """Get data with automatic token refresh."""
        # OAuth2Session handles token refresh automatically
        response = await self._session.async_request(
            "GET",
            "https://api.example.com/data",
        )
        response.raise_for_status()
        return await response.json()


# In __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with OAuth2."""
    implementation = await async_get_config_entry_implementation(hass, entry)
    session = OAuth2Session(hass, entry, implementation)

    client = OAuth2ApiClient(session)

    # Verify token works
    try:
        await client.async_get_data()
    except aiohttp.ClientResponseError as err:
        if err.status == 401:
            raise ConfigEntryAuthFailed from err
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = client
    return True
```

---

## WebSocket Client

### Basic WebSocket

```python
"""WebSocket client."""
from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client."""

    def __init__(
        self,
        hass: HomeAssistant,
        url: str,
        callback: Callable[[dict], None],
    ) -> None:
        """Initialize client."""
        self._hass = hass
        self._url = url
        self._callback = callback
        self._session = async_get_clientsession(hass)
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task | None = None
        self._running = False

    async def async_connect(self) -> None:
        """Connect to WebSocket."""
        self._running = True
        self._ws = await self._session.ws_connect(self._url)
        self._task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        """Listen for messages."""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        self._callback(data)
                    except json.JSONDecodeError:
                        _LOGGER.warning("Invalid JSON: %s", msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOGGER.error("WebSocket error: %s", self._ws.exception())
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if self._running:
                # Reconnect on unexpected disconnect
                asyncio.create_task(self._reconnect())

    async def _reconnect(self) -> None:
        """Reconnect with backoff."""
        delay = 5
        while self._running:
            _LOGGER.info("Reconnecting in %s seconds", delay)
            await asyncio.sleep(delay)
            try:
                await self.async_connect()
                return
            except Exception as err:
                _LOGGER.error("Reconnect failed: %s", err)
                delay = min(delay * 2, 300)  # Max 5 minutes

    async def async_send(self, data: dict) -> None:
        """Send message."""
        if self._ws:
            await self._ws.send_json(data)

    async def async_disconnect(self) -> None:
        """Disconnect."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._ws:
            await self._ws.close()
```

### With Authentication

```python
class AuthenticatedWebSocket(WebSocketClient):
    """WebSocket with authentication."""

    def __init__(
        self,
        hass: HomeAssistant,
        url: str,
        token: str,
        callback: Callable[[dict], None],
    ) -> None:
        """Initialize."""
        super().__init__(hass, url, callback)
        self._token = token

    async def async_connect(self) -> None:
        """Connect with auth header."""
        self._running = True
        self._ws = await self._session.ws_connect(
            self._url,
            headers={"Authorization": f"Bearer {self._token}"},
        )

        # Or authenticate after connection
        await self._ws.send_json({
            "type": "auth",
            "token": self._token,
        })

        # Wait for auth response
        msg = await self._ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data.get("type") != "auth_ok":
                raise AuthenticationError("WebSocket auth failed")

        self._task = asyncio.create_task(self._listen())
```

---

## Local Device Discovery

### Zeroconf/mDNS

```python
# manifest.json
{
  "zeroconf": [
    {"type": "_mydevice._tcp.local."}
  ]
}

# config_flow.py
from homeassistant.components.zeroconf import ZeroconfServiceInfo


async def async_step_zeroconf(
    self, discovery_info: ZeroconfServiceInfo
) -> ConfigFlowResult:
    """Handle zeroconf discovery."""
    host = discovery_info.host
    port = discovery_info.port
    name = discovery_info.name.split(".")[0]
    properties = discovery_info.properties

    # Set unique ID from discovery
    unique_id = properties.get("id") or properties.get("mac")
    await self.async_set_unique_id(unique_id)
    self._abort_if_unique_id_configured(updates={"host": host})

    self._discovered = {
        "host": host,
        "port": port,
        "name": name,
    }

    self.context["title_placeholders"] = {"name": name}
    return await self.async_step_discovery_confirm()
```

### SSDP/UPnP

```python
# manifest.json
{
  "ssdp": [
    {
      "manufacturer": "My Company",
      "deviceType": "urn:schemas-upnp-org:device:Basic:1"
    }
  ]
}

# config_flow.py
from homeassistant.components.ssdp import SsdpServiceInfo


async def async_step_ssdp(
    self, discovery_info: SsdpServiceInfo
) -> ConfigFlowResult:
    """Handle SSDP discovery."""
    from urllib.parse import urlparse

    host = urlparse(discovery_info.ssdp_location).hostname
    upnp = discovery_info.upnp

    unique_id = upnp.get("serialNumber") or upnp.get("UDN")
    await self.async_set_unique_id(unique_id)
    self._abort_if_unique_id_configured(updates={"host": host})

    self._discovered = {
        "host": host,
        "name": upnp.get("friendlyName", "Device"),
        "model": upnp.get("modelName"),
    }

    return await self.async_step_discovery_confirm()
```

### DHCP

```python
# manifest.json
{
  "dhcp": [
    {"macaddress": "AA:BB:CC:*"},
    {"hostname": "mydevice-*"}
  ]
}

# config_flow.py
from homeassistant.components.dhcp import DhcpServiceInfo


async def async_step_dhcp(
    self, discovery_info: DhcpServiceInfo
) -> ConfigFlowResult:
    """Handle DHCP discovery."""
    await self.async_set_unique_id(discovery_info.macaddress)
    self._abort_if_unique_id_configured(updates={"host": discovery_info.ip})

    self._discovered = {
        "host": discovery_info.ip,
        "mac": discovery_info.macaddress,
        "hostname": discovery_info.hostname,
    }

    return await self.async_step_discovery_confirm()
```

---

## API Key Authentication

### Config Flow

```python
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


async def async_step_user(
    self, user_input: dict[str, Any] | None = None
) -> ConfigFlowResult:
    """Handle API key setup."""
    errors: dict[str, str] = {}

    if user_input is not None:
        client = MyApiClient(
            self.hass,
            user_input[CONF_HOST],
            user_input[CONF_API_KEY],
        )

        try:
            await client.async_validate_connection()
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except AuthenticationError:
            errors[CONF_API_KEY] = "invalid_auth"
        else:
            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data=user_input,
            )

    return self.async_show_form(
        step_id="user",
        data_schema=STEP_USER_DATA_SCHEMA,
        errors=errors,
    )
```

### Storing Credentials

```python
# Credentials stored in entry.data (encrypted at rest)
api_key = entry.data[CONF_API_KEY]

# Never store credentials in:
# - hass.data (in memory, not encrypted)
# - entry.options (for user-visible settings)
# - Logs (use _LOGGER.debug, never log credentials)
```

---

## Retry and Backoff

### Using tenacity

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class MyApiClient:
    """Client with retry."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(ConnectionError),
    )
    async def async_get_data(self) -> dict:
        """Get data with retry."""
        return await self._request("GET", "data")
```

### Manual Backoff

```python
async def async_get_with_retry(
    self,
    endpoint: str,
    max_retries: int = 3,
) -> dict:
    """Get with manual retry."""
    last_error = None
    delay = 1

    for attempt in range(max_retries):
        try:
            return await self._request("GET", endpoint)
        except ConnectionError as err:
            last_error = err
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2

    raise last_error
```

---

## Testing API Clients

```python
"""Test API client."""
import pytest
from aiohttp import ClientResponseError
from unittest.mock import AsyncMock, patch

from custom_components.my_integration.api import MyApiClient


@pytest.fixture
def mock_session():
    """Create mock session."""
    return AsyncMock()


async def test_get_data_success(hass, mock_session):
    """Test successful data fetch."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"temp": 22.5})
    mock_session.get = AsyncMock(return_value=mock_response)

    with patch(
        "homeassistant.helpers.aiohttp_client.async_get_clientsession",
        return_value=mock_session,
    ):
        client = MyApiClient(hass, "192.168.1.100", "test-key")
        data = await client.async_get_data()

    assert data["temp"] == 22.5


async def test_authentication_error(hass, mock_session):
    """Test auth error handling."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_session.request = AsyncMock(return_value=mock_response)

    with patch(
        "homeassistant.helpers.aiohttp_client.async_get_clientsession",
        return_value=mock_session,
    ):
        client = MyApiClient(hass, "192.168.1.100", "bad-key")

        with pytest.raises(AuthenticationError):
            await client.async_get_data()
```

---

## Best Practices

### DO

- Use `async_get_clientsession(hass)` for HTTP
- Use `asyncio.timeout()` for all network operations
- Raise specific exceptions for different errors
- Store credentials in `entry.data`
- Support both cloud and local endpoints where applicable
- **Always use HTTPS for cloud APIs**
- **Handle HTTP 429 with exponential backoff**
- **Validate SSL certificates in production**

### DON'T

- Use `requests` (blocking)
- Create new `aiohttp.ClientSession` instances
- Log credentials or tokens
- Hardcode timeouts without override option
- Ignore SSL errors in production
- **Send credentials over HTTP (unencrypted)**
- **Retry immediately on rate limit (use backoff)**

---

For coordinator patterns, see `coordinator.md`.
For services and events, see `services-events.md`.
For security patterns, see `security.md`.
