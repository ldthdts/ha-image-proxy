"""Resize and re-encode images as baseline JPEG for small displays."""

from __future__ import annotations

import io

from PIL import Image, ImageOps

from .const import FIT_LETTERBOX, JPEG_QUALITY


def to_jpeg(content: bytes, width: int, height: int, fit: str) -> bytes:
    """Return a non-progressive JPEG of exactly width x height."""
    with Image.open(io.BytesIO(content)) as source:
        image = _to_rgb(ImageOps.exif_transpose(source))

    if fit == FIT_LETTERBOX:
        image = ImageOps.pad(
            image, (width, height), method=Image.Resampling.LANCZOS, color=(0, 0, 0)
        )
    else:
        image = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS)

    out = io.BytesIO()
    image.save(
        out,
        format="JPEG",
        quality=JPEG_QUALITY,
        progressive=False,
        optimize=False,
        subsampling=2,
    )
    return out.getvalue()


def _to_rgb(image: Image.Image) -> Image.Image:
    """Flatten transparency onto black, since JPEG has no alpha channel."""
    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        return Image.alpha_composite(background, rgba).convert("RGB")
    return image.convert("RGB")
