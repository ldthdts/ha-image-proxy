"""Image entities that expose a converted copy of any image entity."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.image import ImageEntity, async_get_image
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    CONF_FIT,
    CONF_HEIGHT,
    CONF_SOURCE,
    CONF_TOKEN,
    CONF_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    DOMAIN,
    PROXY_PATH,
    SUBENTRY_TYPE_OUTPUT,
)
from .convert import to_jpeg

if TYPE_CHECKING:
    from . import ResizedImageProxyConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ResizedImageProxyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one image entity per output subentry."""
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_TYPE_OUTPUT:
            continue
        output = ResizedImageProxyOutput(hass, entry, subentry)
        entry.runtime_data[subentry.subentry_id] = output
        async_add_entities([output], config_subentry_id=subentry.subentry_id)


class ResizedImageProxyOutput(ImageEntity):
    """A display-sized JPEG converted from any image entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_content_type = "image/jpeg"
    _unrecorded_attributes = frozenset({"proxy_path"})

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ResizedImageProxyConfigEntry,
        subentry: ConfigSubentry,
    ) -> None:
        """Initialize the output from its subentry settings."""
        super().__init__(hass)
        self._source: str = subentry.data[CONF_SOURCE]
        self._width: int = int(subentry.data.get(CONF_WIDTH, DEFAULT_WIDTH))
        self._height: int = int(subentry.data.get(CONF_HEIGHT, DEFAULT_HEIGHT))
        self._fit: str = subentry.data[CONF_FIT]
        self._output_title = subentry.title
        self._cache: tuple[bytes, bytes] | None = None
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            model="Resized image",
        )
        self._attr_extra_state_attributes = {
            "source": self._source,
            "width": self._width,
            "height": self._height,
            "fit": self._fit,
            "proxy_path": PROXY_PATH.format(
                token=entry.data[CONF_TOKEN], output_id=subentry.subentry_id
            ),
        }

    async def async_added_to_hass(self) -> None:
        """Refresh the converted image whenever the source image changes."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source], self._async_source_changed
            )
        )
        await self.async_get_jpeg()

    @callback
    def _async_source_changed(self, event: Event[EventStateChangedData]) -> None:
        self.hass.async_create_task(self.async_get_jpeg())

    async def async_get_jpeg(self) -> bytes | None:
        """Return the converted JPEG, reconverting only when the source changes."""
        try:
            source = await async_get_image(self.hass, self._source)
        except HomeAssistantError as err:
            _LOGGER.warning(
                "Could not read source image %s for %s: %s",
                self._source,
                self._output_title,
                err,
            )
            return None

        if self._cache is None or self._cache[0] != source.content:
            jpeg = await self.hass.async_add_executor_job(
                to_jpeg, source.content, self._width, self._height, self._fit
            )
            self._cache = (source.content, jpeg)
            self._attr_image_last_updated = dt_util.utcnow()
            if self.entity_id:
                self.async_write_ha_state()
        return self._cache[1]

    async def async_image(self) -> bytes | None:
        """Return the converted image bytes."""
        return await self.async_get_jpeg()
