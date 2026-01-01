# Security Best Practices

Security patterns and guidelines for Home Assistant integration development.

## Home Assistant Security Model

### What Home Assistant Provides

- **Authentication required** for most actions
- **Code review** for official integrations
- **Security notifications** via Supervisor and mobile apps
- **Cloud protection** (Nabu Casa can block vulnerable versions)

### What Home Assistant Does NOT Provide

| Feature | Reality |
|---------|---------|
| **Sandboxing** | Does NOT exist - Integrations run in same Python process as Core |
| **Isolation** | Does NOT exist - Full access to `hass.data` and filesystem |
| **Credential encryption** | Does NOT exist - Config entries stored as plaintext JSON |
| **Memory isolation** | Does NOT exist - All integrations share memory space |

### Developer Responsibility

As an integration developer, YOU are responsible for:
- Secure credential handling
- Input validation and sanitization
- HTTPS for sensitive data transmission
- Not exposing user data in logs or diagnostics
- Proper error handling that doesn't leak secrets

> **Important:** Custom integrations are explicitly excluded from Home Assistant's
> vulnerability reporting policy. Users install custom integrations "at their own risk."

---

## Secure API Communication

### HTTPS Enforcement

**Always use HTTPS for cloud APIs:**

```python
# ❌ AVOID - Credentials sent in plaintext
url = f"http://{self.host}/api/data"

# ✅ CORRECT - Encrypted communication
url = f"https://{self.host}/api/data"
```

### SSL Certificate Validation

```python
import ssl
import certifi
import aiohttp

# Production: Full certificate validation
ssl_context = ssl.create_default_context(cafile=certifi.where())
session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))

# Local network devices (self-signed certs) - Document why!
# Only use for local devices on trusted network
async def create_local_session(verify_ssl: bool = True) -> aiohttp.ClientSession:
    """Create session for local device communication."""
    if verify_ssl:
        return aiohttp.ClientSession()

    # WARNING: Only for local trusted devices with self-signed certificates
    return aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    )
```

### Using Home Assistant's Session

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up using HA's shared session."""
    # Preferred: Uses HA's connection pooling and SSL settings
    session = async_get_clientsession(hass)

    # For devices requiring disabled SSL verification
    session = async_get_clientsession(hass, verify_ssl=False)
```

---

## Input Validation & Injection Prevention

### URL Parameter Sanitization

```python
# ❌ VULNERABLE - SSRF attack possible
async def fetch_device(self, device_id: str) -> dict:
    url = f"https://api.example.com/devices/{device_id}"
    # If device_id = "../admin" or "?admin=true" -> Security breach

# ✅ SAFE - Validate and encode
import re
from urllib.parse import quote

async def fetch_device(self, device_id: str) -> dict:
    """Fetch device with validated ID."""
    # Validate format (whitelist approach)
    if not re.match(r'^[a-zA-Z0-9_-]+$', device_id):
        raise ValueError(f"Invalid device ID format: {device_id}")

    # URL-encode to prevent injection
    safe_id = quote(device_id, safe='')
    url = f"https://api.example.com/devices/{safe_id}"
    return await self._request("GET", url)
```

### Path Traversal Prevention

```python
from pathlib import Path

# ❌ VULNERABLE - Directory traversal
async def read_config(self, filename: str) -> str:
    path = f"/config/{filename}"
    # If filename = "../secrets.yaml" -> Reads sensitive file!

# ✅ SAFE - Resolve and validate path
async def read_config(self, filename: str) -> str:
    """Read config file with path validation."""
    base_dir = Path("/config/my_integration")
    file_path = (base_dir / filename).resolve()

    # Ensure path stays within allowed directory
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Invalid path: directory traversal detected")

    return file_path.read_text()
```

### Command Execution Security

Some integrations need to run external commands (ping, system tools).

**Dangerous patterns to avoid:**
- Using `subprocess.run()` with `shell=True` and user input
- Using `os.system()` with string interpolation
- Building command strings from user input

```python
import asyncio
import re

# ✅ SAFE - Use asyncio subprocess with list arguments
async def ping_device(self, host: str) -> bool:
    """Ping device safely."""
    # Validate input format first (whitelist approach)
    if not re.match(r'^[a-zA-Z0-9._-]+$', host):
        raise ValueError(f"Invalid hostname format: {host}")

    # Use list arguments - separates command from data
    proc = await asyncio.create_subprocess_exec(
        "ping",
        "-c", "1",  # Count
        "-W", "2",  # Timeout
        host,       # Validated input as separate argument
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode == 0


# ✅ SAFE - Predefined command whitelist
async def run_tool(self, action: str) -> str:
    """Run predefined tool action."""
    ALLOWED_ACTIONS = {
        "status": ["systemctl", "status", "my-service"],
        "version": ["my-tool", "--version"],
    }

    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unknown action: {action}")

    # Command is fully static - no user input in args
    proc = await asyncio.create_subprocess_exec(
        *ALLOWED_ACTIONS[action],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode()
```

**Key Rules:**
1. Always use list arguments with `create_subprocess_exec`
2. Validate and whitelist input before passing to commands
3. Prefer predefined command lists over dynamic construction
4. Never interpolate user input into command strings

### Service Call Validation

```python
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# Strong schema with character whitelist
SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): vol.All(
        cv.string,
        vol.Match(r'^[a-zA-Z0-9_-]+$'),  # Whitelist safe characters
        vol.Length(min=1, max=64),        # Limit length
    ),
    vol.Required("command"): vol.In(["on", "off", "toggle"]),  # Enum only
    vol.Optional("value"): vol.All(
        vol.Coerce(int),
        vol.Range(min=0, max=100),
    ),
})

async def handle_service(call: ServiceCall) -> None:
    """Handle service call with validated input."""
    # Schema validates BEFORE this function runs
    device_id = call.data["device_id"]  # Safe - validated
    command = call.data["command"]       # Safe - enum validated
```

### Config Flow Input Validation

```python
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

# Use selectors for type-safe UI input
STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): TextSelector(
        TextSelectorConfig(type=TextSelectorType.TEXT)
    ),
    vol.Required(CONF_API_KEY): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),
    vol.Optional(CONF_PORT, default=443): vol.All(
        vol.Coerce(int),
        vol.Range(min=1, max=65535),
    ),
})
```

---

## Credential Management

### Storage Security Levels

| Location | Security Level | Encryption | Use Case |
|----------|---------------|------------|----------|
| `entry.data` | Low | None (JSON) | Connection credentials |
| `entry.options` | Low | None (JSON) | User preferences |
| `secrets.yaml` | Low | None (plaintext) | Shared secrets |
| OAuth tokens | Medium | Auto-refresh | Cloud services |
| Environment vars | Medium | Not persisted | Container deployments |

### Never Log Credentials

```python
# ❌ DANGEROUS - Credentials in logs
_LOGGER.debug("Connecting with API key: %s", api_key)
_LOGGER.error("Auth failed for user %s with password %s", user, password)

# ✅ SAFE - Redact sensitive data
_LOGGER.debug("Connecting to %s", host)
_LOGGER.error("Authentication failed for host %s", host)

# If you must reference credentials exist:
_LOGGER.debug("API key configured: %s", bool(api_key))
```

### Token Refresh Pattern

```python
from datetime import datetime, timedelta
from homeassistant.util import dt as dt_util

class MyApiClient:
    """API client with automatic token refresh."""

    def __init__(self, token: str, refresh_token: str) -> None:
        """Initialize client."""
        self._token = token
        self._refresh_token = refresh_token
        self._token_expires: datetime | None = None
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_valid_token(self) -> None:
        """Refresh token if expired."""
        # NOTE: Always use dt_util.now() for timezone-aware timestamps
        if self._token_expires and dt_util.now() >= self._token_expires:
            await self._refresh_access_token()

    async def _refresh_access_token(self) -> None:
        """Refresh the access token."""
        async with self._session.post(
            "https://auth.example.com/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            },
        ) as resp:
            if resp.status == 401:
                raise AuthenticationError("Refresh token expired")

            data = await resp.json()
            self._token = data["access_token"]
            # Refresh slightly before expiration
            expires_in = data.get("expires_in", 3600)
            self._token_expires = dt_util.now() + timedelta(
                seconds=expires_in - 60
            )

    async def request(self, method: str, url: str, _retry: bool = True) -> dict:
        """Make authenticated request."""
        await self._ensure_valid_token()

        headers = {"Authorization": f"Bearer {self._token}"}
        async with self._session.request(method, url, headers=headers) as resp:
            if resp.status == 401 and _retry:
                # Token invalid, try refresh ONCE
                await self._refresh_access_token()
                return await self.request(method, url, _retry=False)
            if resp.status == 401:
                raise AuthenticationError("Authentication failed after token refresh")
            return await resp.json()
```

### ConfigEntryAuthFailed Pattern

```python
from homeassistant.exceptions import ConfigEntryAuthFailed

class MyCoordinator(DataUpdateCoordinator):
    """Coordinator with auth failure handling."""

    async def _async_update_data(self) -> dict:
        """Fetch data with auth error handling."""
        try:
            return await self.client.async_get_data()
        except AuthenticationError as err:
            # Triggers reauth flow - user must re-enter credentials
            raise ConfigEntryAuthFailed(
                "Authentication failed. Please re-authenticate."
            ) from err
        except TokenExpiredError as err:
            # Also triggers reauth
            raise ConfigEntryAuthFailed(
                "Token expired and could not be refreshed."
            ) from err
```

---

## Rate Limiting & Backoff

### HTTP 429 Handling

```python
class RateLimitError(Exception):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")


async def _request(self, method: str, url: str) -> dict:
    """Make request with rate limit handling."""
    async with self._session.request(method, url) as resp:
        if resp.status == 429:
            retry_after = int(resp.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)

        if resp.status == 401:
            raise AuthenticationError("Invalid credentials")

        resp.raise_for_status()
        return await resp.json()
```

### Exponential Backoff with Jitter

```python
import asyncio
from random import uniform

async def request_with_backoff(
    self,
    method: str,
    url: str,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> dict:
    """Make request with exponential backoff."""
    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            return await self._request(method, url)
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
                "Rate limited, retrying in %.1f seconds (attempt %d/%d)",
                delay, attempt + 1, max_retries
            )
            await asyncio.sleep(delay)
        except aiohttp.ClientError as err:
            last_error = err
            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter for connection errors
            delay = base_delay * (2 ** attempt) + uniform(0, 1)
            await asyncio.sleep(delay)

    raise last_error
```

### Coordinator Rate Limiting

```python
from homeassistant.helpers.debounce import Debouncer

class MyCoordinator(DataUpdateCoordinator):
    """Coordinator with rate limiting."""

    def __init__(self, hass: HomeAssistant, client: MyApiClient) -> None:
        """Initialize with debouncer."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=5.0,  # Minimum 5s between refreshes
                immediate=True,
            ),
        )
        self.client = client
```

---

## WebSocket Security

### Secure WebSocket Connections

```python
import aiohttp
import ssl
import certifi

async def connect_websocket(
    host: str,
    token: str,
    verify_ssl: bool = True,
) -> aiohttp.ClientWebSocketResponse:
    """Connect to WebSocket with security."""
    # Always use wss:// for cloud services
    url = f"wss://{host}/api/websocket"

    # SSL context for certificate validation
    ssl_context = ssl.create_default_context(cafile=certifi.where()) if verify_ssl else False

    session = aiohttp.ClientSession()
    try:
        ws = await session.ws_connect(
            url,
            ssl=ssl_context,
            headers={"Authorization": f"Bearer {token}"},
            heartbeat=30,  # Keep-alive ping every 30s
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return ws
    except Exception:
        await session.close()
        raise
```

### Message Validation

```python
import json
from typing import Any

ALLOWED_MESSAGE_TYPES = {"state_changed", "event", "result", "auth_ok", "auth_required"}


async def receive_message(ws: aiohttp.ClientWebSocketResponse) -> dict[str, Any] | None:
    """Receive and validate WebSocket message."""
    msg = await ws.receive()

    if msg.type == aiohttp.WSMsgType.TEXT:
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            _LOGGER.warning("Received invalid JSON, ignoring")
            return None

        # Validate structure
        if not isinstance(data, dict):
            _LOGGER.warning("Message is not a dict, ignoring")
            return None

        # Validate message type (whitelist)
        msg_type = data.get("type")
        if msg_type and msg_type not in ALLOWED_MESSAGE_TYPES:
            _LOGGER.debug("Unknown message type: %s", msg_type)

        return data

    if msg.type == aiohttp.WSMsgType.ERROR:
        _LOGGER.error("WebSocket error: %s", ws.exception())
        return None

    if msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
        return None

    return None
```

### Reconnection with Backoff

```python
import asyncio
from random import uniform

class WebSocketClient:
    """WebSocket client with automatic reconnection."""

    def __init__(self, host: str, token: str) -> None:
        """Initialize client."""
        self._host = host
        self._token = token
        self._running = False
        self._ws: aiohttp.ClientWebSocketResponse | None = None

    async def start(self) -> None:
        """Start WebSocket loop with reconnection."""
        self._running = True
        retry_delay = 1.0
        max_delay = 300.0  # 5 minutes max

        while self._running:
            try:
                self._ws = await connect_websocket(self._host, self._token)
                retry_delay = 1.0  # Reset on successful connect
                _LOGGER.info("WebSocket connected")

                await self._handle_messages()

            except aiohttp.ClientError as err:
                _LOGGER.warning(
                    "WebSocket error: %s, reconnecting in %.0fs",
                    err,
                    retry_delay,
                )
            except Exception:
                _LOGGER.exception("Unexpected WebSocket error")

            if self._running:
                # Exponential backoff with jitter
                await asyncio.sleep(retry_delay + uniform(0, 1))
                retry_delay = min(retry_delay * 2, max_delay)

    async def stop(self) -> None:
        """Stop WebSocket client."""
        self._running = False
        if self._ws:
            await self._ws.close()
```

---

## Diagnostics Security

### Comprehensive Redaction Set

```python
from homeassistant.components.diagnostics import async_redact_data

# Standard fields to redact
TO_REDACT = {
    # Credentials
    "api_key",
    "password",
    "token",
    "secret",
    "access_token",
    "refresh_token",
    "client_secret",
    "private_key",
    "bearer_token",

    # Personal Identifiable Information (PII)
    "email",
    "username",
    "serial_number",
    "phone",
    "address",

    # Network identifiers
    "mac_address",
    "ip_address",
    "ip",
    "mac",

    # Location data
    "latitude",
    "longitude",
    "location",
    "gps",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics with redacted sensitive data."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": async_redact_data(coordinator.data, TO_REDACT),
    }
```

### Custom Redaction Functions

```python
import re
from typing import Any

def redact_ip_addresses(data: dict) -> dict:
    """Redact IP addresses from diagnostic data."""
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

    def redact_value(value: Any) -> Any:
        if isinstance(value, str):
            return re.sub(ip_pattern, "**REDACTED_IP**", value)
        if isinstance(value, dict):
            return {k: redact_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [redact_value(item) for item in value]
        return value

    return redact_value(data)


def redact_coordinates(data: dict) -> dict:
    """Redact GPS coordinates."""
    result = dict(data)

    for lat_key in ("lat", "latitude", "gps_lat"):
        if lat_key in result:
            result[lat_key] = "**REDACTED**"

    for lon_key in ("lon", "lng", "longitude", "gps_lon"):
        if lon_key in result:
            result[lon_key] = "**REDACTED**"

    return result
```

---

## Secure File Storage

### Where to Store Integration Data

| Location | Use Case | Security |
|----------|----------|----------|
| `hass.config.path(".storage/my_integration")` | Persistent user data | HA managed, survives updates |
| `entry.data` | Connection credentials | Config entry (JSON) |
| `entry.options` | User preferences | Config entry (JSON) |
| `hass.config.path("custom_components/...")` | Static files | Read-only at runtime |

### Using Home Assistant's Store Helper

```python
from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1
STORAGE_KEY = "my_integration"


class MyIntegrationStore:
    """Persistent storage for integration data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize store."""
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict = {}

    async def async_load(self) -> dict:
        """Load data from storage."""
        data = await self._store.async_load()
        self._data = data or {}
        return self._data

    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(self._data)

    async def async_remove(self) -> None:
        """Remove storage file."""
        await self._store.async_remove()


# Usage in __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with persistent storage."""
    store = MyIntegrationStore(hass)
    await store.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "store": store,
        # ... other data
    }
```

### Secure File Writing

```python
from pathlib import Path
import aiofiles

async def write_cache_file(
    hass: HomeAssistant,
    filename: str,
    content: str,
) -> None:
    """Write file securely within integration storage."""
    # Define allowed directory
    base_dir = Path(hass.config.path(".storage/my_integration_cache"))
    base_dir.mkdir(parents=True, exist_ok=True)

    # Validate filename (no path components)
    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValueError("Invalid filename - path traversal not allowed")

    # Double-check resolved path stays within base
    file_path = (base_dir / filename).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Path traversal detected")

    # Write atomically (aiofiles handles async I/O)
    async with aiofiles.open(file_path, "w") as f:
        await f.write(content)
```

### What NOT to Store in Files

```python
# ❌ DANGEROUS - Never store credentials in cache files
cache_data = {
    "api_key": "secret123",           # NO!
    "access_token": "bearer_xyz",     # NO!
    "password": "user_password",      # NO!
}
await store.async_save(cache_data)

# ✅ SAFE - Credentials belong in entry.data
# Cache only non-sensitive data
cache_data = {
    "last_sync": "2024-01-15T10:30:00",
    "device_cache": {"device1": {"name": "Living Room"}},
    "schema_version": 2,
}
await store.async_save(cache_data)

# Access credentials from config entry instead
api_key = entry.data[CONF_API_KEY]
```

---

## Error Message Security

### Safe Error Messages

```python
# ❌ DANGEROUS - Exposes credentials in error
raise ConfigEntryNotReady(
    f"Failed to connect to {host} with API key {api_key}"
)

# ❌ DANGEROUS - Exposes internal paths
raise HomeAssistantError(
    f"Config file not found at /home/user/.config/secrets.yaml"
)

# ✅ SAFE - Generic message, details in logs
raise ConfigEntryNotReady(f"Failed to connect to {host}")

# ✅ SAFE - User-friendly without internals
raise HomeAssistantError("Configuration file not found")
```

### Exception Handling Pattern

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with secure error handling."""
    try:
        client = MyApiClient(entry.data[CONF_HOST], entry.data[CONF_API_KEY])
        await client.async_connect()
    except AuthenticationError:
        # Don't expose what authentication method failed
        raise ConfigEntryAuthFailed("Authentication failed")
    except ConnectionError as err:
        # Log details, but don't expose to user
        _LOGGER.error("Connection error: %s", err)
        raise ConfigEntryNotReady("Could not connect to device")
    except Exception as err:
        # Never expose unexpected errors with full traceback to user
        _LOGGER.exception("Unexpected error during setup")
        raise ConfigEntryNotReady("Setup failed") from err
```

---

## Dependency Security

### Vetting Dependencies

Before adding a requirement to `manifest.json`:

1. **Check popularity** - Well-maintained packages with active communities
2. **Review source** - Open source with visible code
3. **Check security history** - Search for past CVEs
4. **Pin versions** - Use specific versions, not ranges

```json
{
  "requirements": [
    "aiohttp>=3.8.0,<4.0",
    "my-api-client==2.1.0"
  ]
}
```

### Avoid Dangerous Packages

Never use packages that:
- Execute arbitrary code from remote sources
- Have known unpatched vulnerabilities
- Are abandoned (no updates in 2+ years)
- Have suspicious or obfuscated code

---

## Security Checklist

Before publishing your integration:

### Credentials & Authentication
- [ ] All cloud API calls use HTTPS
- [ ] Local device connections document SSL policy
- [ ] Credentials are never logged (even at debug level)
- [ ] Token refresh handles expiration gracefully
- [ ] ConfigEntryAuthFailed triggers reauth flow

### Input Validation
- [ ] All user input validated with voluptuous schemas
- [ ] URL parameters are sanitized (no string interpolation without encoding)
- [ ] File paths checked for directory traversal
- [ ] Service schemas use whitelist validation

### Error Handling
- [ ] Error messages don't expose credentials
- [ ] Stack traces logged but not shown to users
- [ ] Connection errors don't leak internal paths

### Data Protection
- [ ] Diagnostics redact all sensitive data
- [ ] Coordinator data doesn't expose secrets
- [ ] No PII in entity attributes

### Rate Limiting
- [ ] HTTP 429 responses handled properly
- [ ] Exponential backoff implemented
- [ ] Debouncer prevents API abuse

### Dependencies
- [ ] All requirements from trusted sources
- [ ] Versions pinned appropriately
- [ ] No known vulnerabilities

---

## Common Vulnerabilities to Avoid

| Vulnerability | Prevention |
|---------------|------------|
| **SSRF** | Validate and whitelist URL parameters |
| **Path Traversal** | Use `pathlib` with `is_relative_to()` |
| **Command Injection** | Use `create_subprocess_exec` with list args, never shell=True |
| **Credential Leak** | Never log secrets, redact in diagnostics |
| **Injection** | Schema validation, parameterized queries |
| **DoS** | Rate limiting, timeouts, backoff |
| **Token Theft** | HTTPS only, secure storage |

---

For API client patterns, see `api-integration.md`.
For config flow validation, see `config-flow.md`.
For diagnostics, see `diagnostics.md`.
