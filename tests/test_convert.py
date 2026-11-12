"""Tests for the image conversion used by the proxy."""

from __future__ import annotations

import io
import unittest

from PIL import Image

from custom_components.resized_image_proxy.const import FIT_CROP, FIT_LETTERBOX
from custom_components.resized_image_proxy.convert import to_jpeg


def _encode(image: Image.Image, **kwargs) -> bytes:
    out = io.BytesIO()
    image.save(out, format="JPEG", **kwargs)
    return out.getvalue()


def _red_landscape() -> bytes:
    """A progressive JPEG, 1000x300, to prove progressive input is re-encoded."""
    return _encode(Image.new("RGB", (1000, 300), (255, 0, 0)), progressive=True)


class ConvertTests(unittest.TestCase):
    def test_output_is_exact_size_and_baseline_jpeg(self) -> None:
        for fit in (FIT_CROP, FIT_LETTERBOX):
            with self.subTest(fit=fit):
                jpeg = to_jpeg(_red_landscape(), 320, 480, fit)
                image = Image.open(io.BytesIO(jpeg))
                self.assertEqual(image.size, (320, 480))
                self.assertEqual(image.format, "JPEG")
                self.assertNotIn("progression", image.info)

    def test_crop_fills_the_frame(self) -> None:
        image = Image.open(io.BytesIO(to_jpeg(_red_landscape(), 320, 480, FIT_CROP)))
        red, _, _ = image.convert("RGB").getpixel((160, 5))
        self.assertGreater(red, 200)

    def test_letterbox_keeps_whole_image_with_black_bars(self) -> None:
        image = Image.open(
            io.BytesIO(to_jpeg(_red_landscape(), 320, 480, FIT_LETTERBOX))
        )
        top = image.convert("RGB").getpixel((160, 5))
        middle = image.convert("RGB").getpixel((160, 240))
        self.assertLess(max(top), 40)
        self.assertGreater(middle[0], 200)

    def test_transparent_png_is_flattened(self) -> None:
        out = io.BytesIO()
        Image.new("RGBA", (64, 64), (0, 255, 0, 0)).save(out, format="PNG")
        jpeg = to_jpeg(out.getvalue(), 320, 480, FIT_CROP)
        self.assertEqual(Image.open(io.BytesIO(jpeg)).size, (320, 480))


if __name__ == "__main__":
    unittest.main()
