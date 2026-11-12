"""HTTP endpoint that serves a converted image to a display."""

from __future__ import annotations

import hmac

from aiohttp import web
from homeassistant.components.http import KEY_HASS, HomeAssistantView

from .const import CONF_TOKEN, DOMAIN, PROXY_PATH


class ResizedImageProxyView(HomeAssistantView):
    """Serve a converted JPEG for one output, guarded by the entry's token."""

    url = PROXY_PATH
    name = f"api:{DOMAIN}"
    requires_auth = False

    async def get(
        self, request: web.Request, token: str, output_id: str
    ) -> web.Response:
        """Return the converted JPEG for the output if the token matches."""
        hass = request.app[KEY_HASS]
        for entry in hass.config_entries.async_entries(DOMAIN):
            if hmac.compare_digest(entry.data[CONF_TOKEN], token):
                break
        else:
            return web.Response(status=404)

        output = (entry.runtime_data or {}).get(output_id)
        if output is None:
            return web.Response(status=404)

        jpeg = await output.async_get_jpeg()
        if jpeg is None:
            return web.Response(status=503)
        return web.Response(
            body=jpeg,
            content_type="image/jpeg",
            headers={"Cache-Control": "no-store"},
        )
