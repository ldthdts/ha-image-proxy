"""Config flow for the Resized Image Proxy integration."""

from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_FIT,
    CONF_HEIGHT,
    CONF_SOURCE,
    CONF_TOKEN,
    CONF_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    DOMAIN,
    FIT_CROP,
    FIT_LETTERBOX,
    MAX_SIZE,
    SUBENTRY_TYPE_OUTPUT,
)

OUTPUT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SOURCE): EntitySelector(EntitySelectorConfig(domain="image")),
        vol.Required(CONF_WIDTH, default=DEFAULT_WIDTH): NumberSelector(
            NumberSelectorConfig(
                min=16, max=MAX_SIZE, step=1, mode=NumberSelectorMode.BOX
            )
        ),
        vol.Required(CONF_HEIGHT, default=DEFAULT_HEIGHT): NumberSelector(
            NumberSelectorConfig(
                min=16, max=MAX_SIZE, step=1, mode=NumberSelectorMode.BOX
            )
        ),
        vol.Required(CONF_FIT, default=FIT_CROP): SelectSelector(
            SelectSelectorConfig(
                options=[FIT_CROP, FIT_LETTERBOX],
                mode=SelectSelectorMode.DROPDOWN,
                translation_key=CONF_FIT,
            )
        ),
    }
)


def _output_data(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_SOURCE: user_input[CONF_SOURCE],
        CONF_WIDTH: int(user_input[CONF_WIDTH]),
        CONF_HEIGHT: int(user_input[CONF_HEIGHT]),
        CONF_FIT: user_input[CONF_FIT],
    }


class ResizedImageProxyOutputSubentryFlow(ConfigSubentryFlow):
    """Add or edit an output: an image entity converted to a display size."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Create a new output."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME], data=_output_data(user_input)
            )
        return self.async_show_form(step_id="user", data_schema=OUTPUT_SCHEMA)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Edit an existing output."""
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()
        if user_input is not None:
            return self.async_update_and_abort(
                entry,
                subentry,
                title=user_input[CONF_NAME],
                data=_output_data(user_input),
            )
        schema = self.add_suggested_values_to_schema(
            OUTPUT_SCHEMA,
            {CONF_NAME: subentry.title, **subentry.data},
        )
        return self.async_show_form(step_id="reconfigure", data_schema=schema)


class ResizedImageProxyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the proxy. A random token guards the image URLs."""

    VERSION = 1

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Outputs can be added to the proxy."""
        return {SUBENTRY_TYPE_OUTPUT: ResizedImageProxyOutputSubentryFlow}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the proxy entry with a new random token."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(
                title="Resized Image Proxy",
                data={CONF_TOKEN: secrets.token_urlsafe(24)},
            )
        return self.async_show_form(step_id="user")
