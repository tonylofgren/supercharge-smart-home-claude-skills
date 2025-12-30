"""Config flow for My Smart Hub."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import MyHubAuthError, MyHubClient, MyHubConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class MyHubConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for My Smart Hub."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate connection
            client = MyHubClient(user_input[CONF_HOST], user_input[CONF_API_KEY])
            try:
                hub_info = await client.async_get_hub_info()
            except MyHubAuthError:
                errors["base"] = "invalid_auth"
            except MyHubConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                # Use hub ID as unique_id
                await self.async_set_unique_id(hub_info["id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=hub_info.get("name", "My Hub"),
                    data=user_input,
                )
            finally:
                await client.async_close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate new settings
            client = MyHubClient(user_input[CONF_HOST], user_input[CONF_API_KEY])
            try:
                await client.async_get_hub_info()
            except MyHubAuthError:
                errors["base"] = "invalid_auth"
            except MyHubConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=user_input,
                )
            finally:
                await client.async_close()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get options flow."""
        return MyHubOptionsFlow(config_entry)


class MyHubOptionsFlow(OptionsFlow):
    """Options flow for My Smart Hub."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.options.get(
                            "scan_interval", DEFAULT_SCAN_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=10,
                            max=300,
                            step=10,
                            mode=NumberSelectorMode.SLIDER,
                            unit_of_measurement="seconds",
                        )
                    ),
                }
            ),
        )
