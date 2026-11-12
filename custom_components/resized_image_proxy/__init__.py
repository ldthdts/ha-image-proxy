"""The Resized Image Proxy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .view import ResizedImageProxyView

if TYPE_CHECKING:
    from .image import ResizedImageProxyOutput

PLATFORMS = [Platform.IMAGE]

type ResizedImageProxyConfigEntry = ConfigEntry[dict[str, ResizedImageProxyOutput]]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Serve converted images over Home Assistant's HTTP server."""
    hass.http.register_view(ResizedImageProxyView())
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ResizedImageProxyConfigEntry
) -> bool:
    """Set up the proxy from a config entry."""
    entry.runtime_data = {}
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: ResizedImageProxyConfigEntry
) -> None:
    """Reload the entry so outputs match the current subentries."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: ResizedImageProxyConfigEntry
) -> bool:
    """Unload the proxy config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
