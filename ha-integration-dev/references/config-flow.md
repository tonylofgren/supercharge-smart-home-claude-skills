# Config Flow

UI-based configuration for Home Assistant integrations.

## Overview

Config flow enables users to configure integrations through the UI instead of YAML. Required for new integrations.

**Key Components:**
- `config_flow.py` - Flow handler class
- `strings.json` - UI text for forms
- `translations/` - Localized strings

---

## Basic Config Flow

### Minimal Example

```python
"""Config flow for My Integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_API_KEY

from .const import DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate input
            try:
                await self._async_validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                # Create entry
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _async_validate_input(self, data: dict[str, Any]) -> None:
        """Validate the user input."""
        # Test connection/authentication
        client = MyApiClient(data[CONF_HOST], data[CONF_API_KEY])
        await client.async_test_connection()
```

### strings.json

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to My Device",
        "description": "Enter the connection details for your device.",
        "data": {
          "host": "Host",
          "api_key": "API Key"
        },
        "data_description": {
          "host": "IP address or hostname of your device",
          "api_key": "API key from device settings"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect",
      "invalid_auth": "Invalid authentication",
      "unknown": "Unexpected error"
    },
    "abort": {
      "already_configured": "Device is already configured"
    }
  }
}
```

---

## Flow Steps

### Step Types

| Step | Purpose |
|------|---------|
| `async_step_user` | Manual setup from UI |
| `async_step_zeroconf` | Discovered via Zeroconf/mDNS |
| `async_step_ssdp` | Discovered via SSDP/UPnP |
| `async_step_dhcp` | Discovered via DHCP |
| `async_step_bluetooth` | Discovered via Bluetooth |
| `async_step_usb` | Discovered via USB |
| `async_step_homekit` | Discovered via HomeKit |
| `async_step_reauth` | Re-authentication required |
| `async_step_reconfigure` | Reconfigure existing entry |

### Multi-Step Flow

```python
class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Multi-step config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._host: str | None = None
        self._devices: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: Get host."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]

            # Discover devices on host
            try:
                self._devices = await self._async_discover_devices(self._host)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Select device."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device = next(d for d in self._devices if d["id"] == device_id)

            return self.async_create_entry(
                title=device["name"],
                data={
                    CONF_HOST: self._host,
                    CONF_DEVICE_ID: device_id,
                },
            )

        # Build device selection schema
        device_options = {d["id"]: d["name"] for d in self._devices}

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICE_ID): vol.In(device_options)}
            ),
        )
```

---

## Form Schemas (Voluptuous)

### Common Patterns

```python
import voluptuous as vol
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

# Basic schema
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=8080): int,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

# With defaults from existing entry (for reconfigure)
def get_user_schema(defaults: dict | None = None) -> vol.Schema:
    """Get schema with optional defaults."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST, default=defaults.get(CONF_HOST, "")
            ): str,
            vol.Optional(
                CONF_PORT, default=defaults.get(CONF_PORT, 8080)
            ): int,
        }
    )
```

### Selectors (Modern UI Elements)

```python
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    DeviceSelector,
    DeviceSelectorConfig,
    AreaSelector,
    AreaSelectorConfig,
    TimeSelector,
    DurationSelector,
    DurationSelectorConfig,
    ColorRGBSelector,
    IconSelector,
    LocationSelector,
)

SCHEMA_WITH_SELECTORS = vol.Schema(
    {
        # Dropdown select
        vol.Required("mode"): SelectSelector(
            SelectSelectorConfig(
                options=["option1", "option2", "option3"],
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="mode",
            )
        ),

        # Number slider
        vol.Optional("interval", default=60): NumberSelector(
            NumberSelectorConfig(
                min=10,
                max=3600,
                step=10,
                unit_of_measurement="seconds",
                mode=NumberSelectorMode.SLIDER,
            )
        ),

        # Password input
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),

        # Boolean toggle
        vol.Optional("enabled", default=True): BooleanSelector(),

        # Entity picker
        vol.Optional("target_entity"): EntitySelector(
            EntitySelectorConfig(domain="light")
        ),

        # Device picker
        vol.Optional("target_device"): DeviceSelector(
            DeviceSelectorConfig(integration=DOMAIN)
        ),

        # Area picker
        vol.Optional("area"): AreaSelector(AreaSelectorConfig()),

        # Duration picker
        vol.Optional("timeout"): DurationSelector(
            DurationSelectorConfig(enable_day=False)
        ),
    }
)
```

### Validation

```python
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

SCHEMA = vol.Schema(
    {
        # String validations
        vol.Required(CONF_HOST): cv.string,
        vol.Required("url"): cv.url,
        vol.Required("template"): cv.template,

        # Number validations
        vol.Required(CONF_PORT): cv.port,
        vol.Required("latitude"): cv.latitude,
        vol.Required("longitude"): cv.longitude,
        vol.Optional("percentage"): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100)
        ),

        # List/choices
        vol.Required("color"): vol.In(["red", "green", "blue"]),
        vol.Optional("items"): vol.All(cv.ensure_list, [cv.string]),

        # Time
        vol.Optional("time"): cv.time,
        vol.Optional("date"): cv.date,
        vol.Optional("datetime"): cv.datetime,

        # Slug (lowercase, underscores)
        vol.Required("device_id"): cv.slug,
    }
)
```

---

## Input Sanitization & Security

### Secure Validation Patterns

Use whitelist validation to prevent injection attacks:

```python
import re
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# ❌ VULNERABLE - Accepts any string
SCHEMA_UNSAFE = vol.Schema({
    vol.Required("device_id"): str,  # Can contain "../" or special chars
})

# ✅ SAFE - Whitelist allowed characters
SCHEMA_SAFE = vol.Schema({
    vol.Required("device_id"): vol.All(
        cv.string,
        vol.Match(r'^[a-zA-Z0-9_-]+$'),  # Only safe characters
        vol.Length(min=1, max=64),        # Limit length
    ),
})
```

### URL and Host Validation

```python
from urllib.parse import urlparse

def validate_host(value: str) -> str:
    """Validate host is safe."""
    # Reject if contains path traversal
    if ".." in value or "/" in value:
        raise vol.Invalid("Invalid host format")

    # Basic format check
    if not re.match(r'^[a-zA-Z0-9.-]+$', value):
        raise vol.Invalid("Host contains invalid characters")

    return value


SCHEMA_WITH_HOST = vol.Schema({
    vol.Required(CONF_HOST): vol.All(
        cv.string,
        validate_host,
    ),
    vol.Required(CONF_PORT): cv.port,
})
```

### Path Input Validation

```python
from pathlib import Path

def validate_safe_path(base_dir: str):
    """Create validator for paths within a directory."""
    def validator(value: str) -> str:
        """Validate path is within allowed directory."""
        base = Path(base_dir).resolve()
        target = (base / value).resolve()

        if not target.is_relative_to(base):
            raise vol.Invalid("Path traversal not allowed")

        return str(target)

    return validator


# Usage
SCHEMA_WITH_PATH = vol.Schema({
    vol.Required("config_file"): vol.All(
        cv.string,
        validate_safe_path("/config/my_integration"),
    ),
})
```

### Sensitive Field Handling

```python
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,

    # Password field - masked in UI, not shown in logs
    vol.Required(CONF_PASSWORD): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),

    # API key - same treatment
    vol.Required(CONF_API_KEY): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),
})

# Never log sensitive fields
async def _async_validate_input(self, data: dict) -> None:
    """Validate input."""
    _LOGGER.debug("Validating connection to %s", data[CONF_HOST])
    # ❌ NEVER: _LOGGER.debug("API key: %s", data[CONF_API_KEY])
```

### Common Security Validators

```python
# Device/entity ID - safe characters only
vol.Required("device_id"): vol.All(
    cv.string,
    vol.Match(r'^[a-zA-Z0-9_-]+$'),
    vol.Length(min=1, max=64),
)

# Username - alphanumeric with limited special chars
vol.Required(CONF_USERNAME): vol.All(
    cv.string,
    vol.Match(r'^[a-zA-Z0-9_@.-]+$'),
    vol.Length(min=1, max=128),
)

# Port - validated range
vol.Required(CONF_PORT): vol.All(
    vol.Coerce(int),
    vol.Range(min=1, max=65535),
)

# URL - must be valid URL format
vol.Required("webhook_url"): vol.All(
    cv.url,
    vol.Match(r'^https://'),  # Enforce HTTPS
)

# Enum - whitelist options
vol.Required("mode"): vol.In(["auto", "manual", "schedule"])
```

---

## Options Flow

Allow users to modify settings after setup.

### Enable Options Flow

```python
class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> MyOptionsFlow:
        """Get the options flow."""
        return MyOptionsFlow(config_entry)
```

### Options Flow Handler

```python
from homeassistant.config_entries import ConfigEntry, OptionsFlow
from homeassistant.core import callback


class MyOptionsFlow(OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values
        options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=options.get(CONF_SCAN_INTERVAL, 60),
                    ): NumberSelector(
                        NumberSelectorConfig(min=10, max=3600)
                    ),
                    vol.Optional(
                        "enable_notifications",
                        default=options.get("enable_notifications", True),
                    ): BooleanSelector(),
                }
            ),
        )
```

### Using Options in Integration

```python
# In __init__.py or coordinator
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration."""
    # Get options (with defaults from data)
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    coordinator = MyCoordinator(
        hass,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
```

### strings.json for Options

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Setup",
        "data": { "host": "Host" }
      }
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Options",
        "description": "Configure integration options",
        "data": {
          "scan_interval": "Update Interval",
          "enable_notifications": "Enable Notifications"
        },
        "data_description": {
          "scan_interval": "How often to poll for updates (seconds)"
        }
      }
    }
  }
}
```

---

## Reauth Flow

Handle authentication failures.

### Trigger Reauth

```python
# In coordinator or anywhere auth fails
from homeassistant.exceptions import ConfigEntryAuthFailed

async def _async_update_data(self) -> dict:
    """Fetch data."""
    try:
        return await self.client.async_get_data()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed("Invalid credentials") from err
```

### Reauth Step Handler

```python
class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauth upon authentication error."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauth dialog."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._async_validate_input(
                    {**self._reauth_entry.data, **user_input}
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                # Update entry with new credentials
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data={**self._reauth_entry.data, **user_input},
                )
                await self.hass.config_entries.async_reload(
                    self._reauth_entry.entry_id
                )
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_PASSWORD): str}
            ),
            errors=errors,
            description_placeholders={
                "host": self._reauth_entry.data[CONF_HOST]
            },
        )
```

### strings.json for Reauth

```json
{
  "config": {
    "step": {
      "reauth_confirm": {
        "title": "Re-authenticate",
        "description": "Please re-enter password for {host}",
        "data": {
          "password": "Password"
        }
      }
    },
    "abort": {
      "reauth_successful": "Re-authentication successful"
    }
  }
}
```

---

## Reconfigure Flow

Allow users to change setup parameters without deleting and recreating the entry (HA 2024+).

### Basic Reconfigure

```python
class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        reconfigure_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._async_validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                # Update entry and reload integration
                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=reconfigure_entry.data.get(CONF_HOST),
                    ): str,
                }
            ),
            errors=errors,
        )
```

### Reconfigure with Partial Updates

```python
async def async_step_reconfigure(
    self, user_input: dict[str, Any] | None = None
) -> ConfigFlowResult:
    """Handle reconfiguration with partial data updates."""
    entry = self._get_reconfigure_entry()

    if user_input is not None:
        # Merge with existing data (keep unchanged fields)
        new_data = {**entry.data, **user_input}

        # Optionally validate
        try:
            await self._async_validate_input(new_data)
        except InvalidAuth:
            return self.async_show_form(
                step_id="reconfigure",
                errors={"base": "invalid_auth"},
                data_schema=self._get_reconfigure_schema(entry),
            )

        return self.async_update_reload_and_abort(
            entry,
            data_updates=new_data,
            reload_even_if_entry_is_unchanged=True,
        )

    return self.async_show_form(
        step_id="reconfigure",
        data_schema=self._get_reconfigure_schema(entry),
    )


def _get_reconfigure_schema(self, entry: ConfigEntry) -> vol.Schema:
    """Get schema with current values as defaults."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=entry.data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=entry.data.get(CONF_PORT, 8080)): int,
            vol.Optional(CONF_USERNAME, default=entry.data.get(CONF_USERNAME, "")): str,
        }
    )
```

### Reconfigure with Title Update

```python
async def async_step_reconfigure(
    self, user_input: dict[str, Any] | None = None
) -> ConfigFlowResult:
    """Reconfigure with new title."""
    entry = self._get_reconfigure_entry()

    if user_input is not None:
        # Get device info for new title
        client = MyApiClient(user_input[CONF_HOST])
        device_info = await client.async_get_info()

        return self.async_update_reload_and_abort(
            entry,
            data_updates=user_input,
            title=device_info["name"],  # Update entry title
        )

    # Show form...
```

### Reconfigure vs Reauth

| Flow | Purpose | Trigger |
|------|---------|---------|
| Reconfigure | Change host, port, settings | User initiates from UI |
| Reauth | Update credentials only | `ConfigEntryAuthFailed` exception |

### strings.json for Reconfigure

```json
{
  "config": {
    "step": {
      "reconfigure": {
        "title": "Reconfigure {name}",
        "description": "Update the connection settings for your device.",
        "data": {
          "host": "Host",
          "port": "Port"
        },
        "data_description": {
          "host": "New IP address or hostname"
        }
      }
    }
  }
}
```

---

## Discovery Flows

### Zeroconf Discovery

```python
# manifest.json
{
  "zeroconf": [
    {"type": "_mydevice._tcp.local."}
  ]
}

# config_flow.py
from homeassistant.components.zeroconf import ZeroconfServiceInfo


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info.host

        # Set unique ID to prevent duplicate entries
        await self.async_set_unique_id(discovery_info.properties.get("id"))
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        # Store for later steps
        self._discovered_host = host
        self._discovered_name = discovery_info.name.split(".")[0]

        # Show confirmation
        self.context["title_placeholders"] = {"name": self._discovered_name}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovered_name,
                data={CONF_HOST: self._discovered_host},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self._discovered_name},
        )
```

### SSDP Discovery

```python
# manifest.json
{
  "ssdp": [
    {"manufacturer": "My Company", "deviceType": "urn:schemas-upnp-org:device:Basic:1"}
  ]
}

# config_flow.py
from homeassistant.components.ssdp import SsdpServiceInfo


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    async def async_step_ssdp(
        self, discovery_info: SsdpServiceInfo
    ) -> ConfigFlowResult:
        """Handle SSDP discovery."""
        host = urlparse(discovery_info.ssdp_location).hostname
        unique_id = discovery_info.upnp.get("serialNumber")

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._discovered_host = host
        return await self.async_step_discovery_confirm()
```

### DHCP Discovery

```python
# manifest.json
{
  "dhcp": [
    {"macaddress": "AA:BB:CC:*"}
  ]
}

# config_flow.py
from homeassistant.components.dhcp import DhcpServiceInfo


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow."""

    async def async_step_dhcp(
        self, discovery_info: DhcpServiceInfo
    ) -> ConfigFlowResult:
        """Handle DHCP discovery."""
        await self.async_set_unique_id(discovery_info.macaddress)
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.ip})

        self._discovered_host = discovery_info.ip
        return await self.async_step_discovery_confirm()
```

---

## Unique ID Management

### Setting Unique ID

```python
async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
    """Handle user step."""
    if user_input is not None:
        # Get unique identifier from device
        device_info = await self._async_get_device_info(user_input[CONF_HOST])

        # Set unique ID (prevents duplicate entries)
        await self.async_set_unique_id(device_info["serial_number"])

        # Abort if already configured, optionally update host
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: user_input[CONF_HOST]}
        )

        return self.async_create_entry(...)
```

### Unique ID Best Practices

| Source | Example |
|--------|---------|
| Serial number | `ABC123456` |
| MAC address | `AA:BB:CC:DD:EE:FF` |
| Cloud account ID | `user_12345` |
| Device UUID | `550e8400-e29b-41d4-a716-446655440000` |

**Never use:**
- IP addresses (can change)
- Hostnames (can change)
- User-provided names

---

## Translations

### File Structure

```
translations/
├── en.json     # English (required)
├── sv.json     # Swedish
├── de.json     # German
└── fr.json     # French
```

### Translation File Format

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Anslut till enhet",
        "description": "Ange anslutningsuppgifter.",
        "data": {
          "host": "Värd",
          "api_key": "API-nyckel"
        }
      }
    },
    "error": {
      "cannot_connect": "Kunde inte ansluta",
      "invalid_auth": "Ogiltig autentisering"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Inställningar",
        "data": {
          "scan_interval": "Uppdateringsintervall"
        }
      }
    }
  }
}
```

### Selector Translation Keys

```json
{
  "selector": {
    "mode": {
      "options": {
        "option1": "First Option",
        "option2": "Second Option"
      }
    }
  }
}
```

---

## Common Patterns

### Prevent Duplicate Entries

```python
async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
    if user_input is not None:
        # Check if host already configured
        self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

        # Or use unique ID
        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured()
```

### Progress Indicator

```python
async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
    if user_input is not None:
        return await self.async_step_progress()

async def async_step_progress(
    self, user_input: dict | None = None
) -> ConfigFlowResult:
    """Show progress while connecting."""
    if not hasattr(self, "_progress_task"):
        self._progress_task = self.hass.async_create_task(
            self._async_connect()
        )
        return self.async_show_progress(
            step_id="progress",
            progress_action="connecting",
        )

    try:
        await self._progress_task
    except Exception:
        return self.async_show_progress_done(next_step_id="error")

    return self.async_show_progress_done(next_step_id="finish")
```

### Menu Step

```python
async def async_step_user(
    self, user_input: dict | None = None
) -> ConfigFlowResult:
    """Show menu for setup method."""
    return self.async_show_menu(
        step_id="user",
        menu_options=["manual", "discover"],
    )

async def async_step_manual(self, user_input: dict | None = None):
    """Manual setup."""
    ...

async def async_step_discover(self, user_input: dict | None = None):
    """Discovery setup."""
    ...
```

---

## Result Methods

| Method | Purpose |
|--------|---------|
| `async_show_form` | Show form for user input |
| `async_create_entry` | Create config entry (success) |
| `async_abort` | Abort flow with message |
| `async_show_progress` | Show progress indicator |
| `async_show_progress_done` | Complete progress step |
| `async_show_menu` | Show menu for step selection |
| `async_update_reload_and_abort` | Update entry and reload |

---

## Testing Config Flow

```python
"""Tests for config flow."""
import pytest
from unittest.mock import patch, AsyncMock

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.my_integration.const import DOMAIN


async def test_user_flow(hass: HomeAssistant) -> None:
    """Test user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.my_integration.config_flow.MyApiClient"
    ) as mock_client:
        mock_client.return_value.async_test_connection = AsyncMock()

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100", CONF_API_KEY: "test-key"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "192.168.1.100"
    assert result["data"] == {
        CONF_HOST: "192.168.1.100",
        CONF_API_KEY: "test-key",
    }


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test handling connection error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.my_integration.config_flow.MyApiClient"
    ) as mock_client:
        mock_client.return_value.async_test_connection = AsyncMock(
            side_effect=CannotConnect
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.100", CONF_API_KEY: "test-key"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
```

---

For entity implementation, see `entities.md`.
For API integration patterns, see `api-integration.md`.
