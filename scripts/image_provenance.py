"""Source-crop identity and pixel checks shared by preparation and PPTX audit."""
import base64
import hashlib
import io
import re
from PIL import Image, ImageOps


def open_image(path):
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGBA")


def decode_image(data):
    with Image.open(io.BytesIO(data)) as image:
        return image.convert("RGBA")


def embedded_image(href):
    if not isinstance(href, str) or not re.fullmatch(r"data:image/(png|jpeg);base64,[A-Za-z0-9+/=\s]+", href):
        raise ValueError("Expected an embedded PNG/JPEG")
    return decode_image(base64.b64decode(re.sub(r"\s", "", href.split(",", 1)[1]), validate=True))


def pixel_digest(image):
    rgba = image.convert("RGBA")
    header = f"{rgba.width}x{rgba.height}:RGBA\0".encode("ascii")
    return hashlib.sha256(header + rgba.tobytes()).hexdigest()


def checked_crop(image, crop):
    if not isinstance(crop, dict) or any(type(crop.get(k)) is not int for k in ("x", "y", "w", "h")):
        raise ValueError("Source crop needs integer pixel coordinates")
    x, y, w, h = (crop[k] for k in ("x", "y", "w", "h"))
    if w <= 0 or h <= 0 or min(x, y) < 0 or x + w > image.width or y + h > image.height:
        raise ValueError("Source crop is outside the source canvas")
    return image.crop((x, y, x + w, y + h))


def validate_resources(scene, source=None):
    """Check the declared manifest, not an inferred count of all photos in a figure."""
    errors, verified = [], 0
    assets = scene.get("sourceAssets", [])
    if not isinstance(assets, list):
        return ["sourceAssets must be an array"], 0
    ids = set()
    for asset in assets:
        try:
            identity = asset.get("id")
            if not isinstance(identity, str) or not identity.strip() or identity in ids:
                raise ValueError("sourceAssets has missing or duplicate IDs")
            ids.add(identity)
            canvas, crop = asset.get("canvas"), asset.get("crop")
            if not isinstance(canvas, dict) or any(type(canvas.get(k)) is not int or canvas[k] <= 0 for k in ("width", "height")):
                raise ValueError("invalid source canvas")
            if not isinstance(crop, dict) or any(type(crop.get(k)) is not int for k in ("x", "y", "w", "h")):
                raise ValueError("invalid source crop")
            if min(crop["x"], crop["y"]) < 0 or min(crop["w"], crop["h"]) <= 0 or crop["x"]+crop["w"] > canvas["width"] or crop["y"]+crop["h"] > canvas["height"]:
                raise ValueError("source crop outside canvas")
            if not re.fullmatch(r"[a-f0-9]{64}", asset.get("pixelSha256", "")):
                raise ValueError("missing source pixel digest")
            matches = [n for n in scene.get("nodes", []) if n.get("sourceAssetId") == identity]
            if len(matches) != 1 or matches[0].get("type") != "image":
                raise ValueError("expected exactly one bound image")
            node = matches[0]
            if node.get("sourceCrop") != crop or node.get("sourceCanvas") != canvas:
                raise ValueError("image provenance differs from manifest")
            if pixel_digest(embedded_image(node.get("href"))) != asset["pixelSha256"]:
                raise ValueError("embedded pixels differ from source asset")
            if source is not None:
                if source.size != (canvas["width"], canvas["height"]):
                    raise ValueError("original image dimensions differ from source canvas")
                if pixel_digest(checked_crop(source, crop)) != asset["pixelSha256"]:
                    raise ValueError("crop pixels differ from original image")
            verified += 1
        except (ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
            errors.append(f"Source asset {asset.get('id', '?') if isinstance(asset, dict) else '?'}: {exc}")
    for node in scene.get("nodes", []):
        if "sourceAssetId" in node and node["sourceAssetId"] not in ids:
            errors.append(node.get("id", "?") + ": unknown sourceAssetId")
        if ("sourceCrop" in node or "sourceCanvas" in node) and "sourceAssetId" not in node:
            errors.append(node.get("id", "?") + ": source metadata needs sourceAssetId")
    return errors, verified
