# Repair Issues

User notifications and actionable issues in Home Assistant (2024+).

## Overview

Repair issues allow integrations to notify users about problems that require their attention. Issues appear in the **Settings → System → Repairs** panel.

**Use Cases:**
- Configuration problems requiring user action
- Deprecated features that need migration
- Firmware updates available
- Authentication failures
- Device connectivity issues

---

## Basic Usage

### Create an Issue

```python
"""Example of creating repair issues."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN


def create_firmware_update_issue(
    hass: HomeAssistant,
    device_name: str,
    current_version: str,
    new_version: str,
) -> None:
    """Create an issue for firmware update."""
    ir.async_create_issue(
        hass,
        DOMAIN,
        f"firmware_update_{device_name}",
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="firmware_update",
        translation_placeholders={
            "device": device_name,
            "current": current_version,
            "new": new_version,
        },
    )
```

### Delete an Issue

```python
def clear_firmware_update_issue(
    hass: HomeAssistant,
    device_name: str,
) -> None:
    """Clear the firmware update issue."""
    ir.async_delete_issue(hass, DOMAIN, f"firmware_update_{device_name}")
```

---

## Issue Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hass` | `HomeAssistant` | Home Assistant instance |
| `domain` | `str` | Integration domain |
| `issue_id` | `str` | Unique identifier for this issue |
| `is_fixable` | `bool` | Can be fixed via HA UI |
| `severity` | `IssueSeverity` | Importance level |
| `translation_key` | `str` | Key in strings.json |
| `translation_placeholders` | `dict` | Values for translation placeholders |
| `learn_more_url` | `str` | Optional URL for documentation |
| `data` | `dict` | Custom data for fixable issues |
| `is_persistent` | `bool` | Survives restart (default: False) |

### Severity Levels

```python
from homeassistant.helpers import issue_registry as ir

ir.IssueSeverity.CRITICAL  # Breaks functionality
ir.IssueSeverity.ERROR     # Significant problem
ir.IssueSeverity.WARNING   # User should be aware
```

---

## Translations

### strings.json Structure

```json
{
  "issues": {
    "firmware_update": {
      "title": "Firmware update available for {device}",
      "description": "Your device **{device}** is running firmware {current}, but version {new} is available.\n\nPlease update to get the latest features and security fixes."
    },
    "auth_failed": {
      "title": "Authentication failed",
      "description": "Unable to authenticate with {host}. Please reconfigure the integration with valid credentials."
    },
    "deprecated_feature": {
      "title": "Deprecated feature detected",
      "description": "The feature **{feature}** is deprecated and will be removed in {version}.\n\nPlease migrate to {replacement}."
    }
  }
}
```

### Markdown Support

Issue descriptions support markdown:
- `**bold**` for emphasis
- `\n\n` for paragraphs
- `[link text](url)` for links
- `` `code` `` for inline code

---

## Fixable Issues

Fixable issues can be resolved through the Home Assistant UI.

### Create Fixable Issue

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN


async def create_reconfigure_issue(
    hass: HomeAssistant,
    entry: ConfigEntry,
    reason: str,
) -> None:
    """Create an issue that can be fixed by reconfiguring."""
    ir.async_create_issue(
        hass,
        DOMAIN,
        f"needs_reconfigure_{entry.entry_id}",
        is_fixable=True,
        is_persistent=True,
        severity=ir.IssueSeverity.ERROR,
        translation_key="needs_reconfigure",
        translation_placeholders={
            "name": entry.title,
            "reason": reason,
        },
        data={"entry_id": entry.entry_id},
    )
```

### Handle Fix Flow

```python
"""Config flow with repair fix handler."""
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    async def async_step_fix_issue(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Handle fixing an issue from repairs."""
        # Get issue data
        issue_data = self.init_data  # Contains data from async_create_issue

        if user_input is not None:
            # Fix was successful
            entry = self.hass.config_entries.async_get_entry(
                issue_data["entry_id"]
            )
            if entry:
                # Update configuration
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={**entry.data, **user_input},
                )
                # Delete the issue
                ir.async_delete_issue(
                    self.hass,
                    DOMAIN,
                    f"needs_reconfigure_{entry.entry_id}",
                )
                return self.async_abort(reason="fixed")

        return self.async_show_form(
            step_id="fix_issue",
            data_schema=vol.Schema({
                vol.Required("new_value"): str,
            }),
        )
```

---

## Common Patterns

### Authentication Failed

```python
from homeassistant.exceptions import ConfigEntryAuthFailed

async def _async_update_data(self) -> dict:
    """Fetch data from API."""
    try:
        return await self.client.async_get_data()
    except AuthenticationError as err:
        # This automatically creates a repair issue
        raise ConfigEntryAuthFailed(
            translation_domain=DOMAIN,
            translation_key="auth_failed",
            translation_placeholders={"host": self.host},
        ) from err
```

### Deprecation Warning

```python
def check_deprecated_config(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Check for deprecated configuration."""
    if "old_option" in entry.data:
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"deprecated_option_{entry.entry_id}",
            is_fixable=True,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="deprecated_option",
            translation_placeholders={
                "option": "old_option",
                "replacement": "new_option",
            },
            data={"entry_id": entry.entry_id},
        )
```

### Device Offline

```python
class MyCoordinator(DataUpdateCoordinator):
    """Coordinator with offline detection."""

    _offline_issue_created: bool = False

    async def _async_update_data(self) -> dict:
        """Fetch data."""
        try:
            data = await self.client.async_get_data()
            # Device is back online, clear issue
            if self._offline_issue_created:
                ir.async_delete_issue(
                    self.hass,
                    DOMAIN,
                    f"device_offline_{self.device_id}",
                )
                self._offline_issue_created = False
            return data
        except ConnectionError:
            # Create issue if not already created
            if not self._offline_issue_created:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    f"device_offline_{self.device_id}",
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="device_offline",
                    translation_placeholders={
                        "device": self.device_name,
                    },
                )
                self._offline_issue_created = True
            raise UpdateFailed("Device offline") from err
```

### Configuration Migration

```python
async def async_migrate_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Migrate old config entry to new format."""
    if entry.version < 2:
        # Create migration notice
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"config_migrated_{entry.entry_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="config_migrated",
            translation_placeholders={
                "old_version": str(entry.version),
                "new_version": "2",
            },
        )

        # Perform migration
        new_data = migrate_config(entry.data)
        hass.config_entries.async_update_entry(
            entry,
            data=new_data,
            version=2,
        )

    return True
```

---

## Issue Management in Setup

### Check Issues During Setup

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up integration."""
    # Clear any stale issues from previous runs
    ir.async_delete_issue(hass, DOMAIN, f"setup_failed_{entry.entry_id}")

    try:
        client = MyApiClient(entry.data)
        await client.async_connect()
    except AuthenticationError:
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"auth_failed_{entry.entry_id}",
            is_fixable=True,
            severity=ir.IssueSeverity.ERROR,
            translation_key="auth_failed",
            data={"entry_id": entry.entry_id},
        )
        raise ConfigEntryAuthFailed from err
    except ConnectionError:
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"connection_failed_{entry.entry_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key="connection_failed",
            translation_placeholders={"host": entry.data["host"]},
        )
        raise ConfigEntryNotReady from err

    return True
```

### Cleanup Issues on Unload

```python
async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload integration."""
    # Clear device-specific issues
    ir.async_delete_issue(hass, DOMAIN, f"device_offline_{entry.entry_id}")

    # Unload platforms
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

---

## Learn More URL

```python
ir.async_create_issue(
    hass,
    DOMAIN,
    "needs_setup",
    is_fixable=False,
    severity=ir.IssueSeverity.WARNING,
    translation_key="needs_setup",
    learn_more_url="https://my-integration.example.com/setup-guide",
)
```

---

## Best Practices

### DO

- Use unique `issue_id` per issue type (include entry_id if entry-specific)
- Clean up issues when the problem is resolved
- Use appropriate severity levels
- Provide actionable descriptions
- Include `learn_more_url` for complex issues
- Use `is_persistent=True` for issues that survive restarts

### DON'T

- Create duplicate issues (check before creating)
- Leave stale issues after resolution
- Use CRITICAL for minor issues
- Create issues for transient errors (use logging instead)
- Forget to handle issue cleanup in unload

---

For config flow integration, see `config-flow.md`.
For authentication patterns, see `api-integration.md`.
