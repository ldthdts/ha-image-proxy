"""Constants for the Resized Image Proxy integration."""

from typing import Final

DOMAIN: Final = "resized_image_proxy"

CONF_TOKEN: Final = "token"
CONF_SOURCE: Final = "source"
CONF_WIDTH: Final = "width"
CONF_HEIGHT: Final = "height"
CONF_FIT: Final = "fit"

FIT_CROP: Final = "crop"
FIT_LETTERBOX: Final = "letterbox"

DEFAULT_WIDTH: Final = 320
DEFAULT_HEIGHT: Final = 480
MAX_SIZE: Final = 4096

JPEG_QUALITY: Final = 90

SUBENTRY_TYPE_OUTPUT: Final = "output"

PROXY_PATH: Final = "/api/resized_image_proxy/{token}/{output_id}.jpg"
