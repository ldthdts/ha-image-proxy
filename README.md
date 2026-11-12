# Resized Image Proxy

A Home Assistant custom integration that converts any image entity into a
display-sized baseline JPEG and serves it over Home Assistant's HTTP server.
It is useful for small screens (for example a 320x480 clock) that only accept
standard, non-progressive JPEG.

It works with any `image` entity, such as a Stash feed from the Stash
integration, a camera snapshot, or a picture from another integration.

## Install

1. In HACS, add this repository as a custom repository (type: Integration).
2. Install **Resized Image Proxy** and restart Home Assistant.
3. Go to **Settings > Devices & services > Add integration** and choose
   **Resized Image Proxy**. Only one proxy is needed.

## Add an output

For each display, select **Add image output** on the proxy and set:

- **Source image entity**: any `image.*` entity.
- **Width / Height**: the size the display needs (default 320 x 480).
- **Fit**:
  - *Crop to fill* fills the whole screen and cuts off the edges.
  - *Fit inside* keeps the whole image and adds black bars.

Each output creates its own device and image entity, named after the output,
for example `image.clock`. You can preview the converted image there.

## Use the URL on the display

Each output has a `proxy_path` attribute, for example:

```
/api/resized_image_proxy/<token>/<output_id>.jpg
```

Put your Home Assistant base URL in front of it, for example
`http://homeassistant.local:8123/api/resized_image_proxy/...`.
The clock should fetch this URL.

The token is random and generated when you add the proxy. Anyone with the
full URL can read the image, so treat it as a secret. Do not share it.
The token is not recorded in the history database.

## Notes

- Every request uses the source entity's current image. Conversion only runs
  again when the source image changes.
- Transparency is flattened onto black, since JPEG has no alpha channel.
- EXIF rotation is applied before resizing.
