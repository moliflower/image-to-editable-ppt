#!/usr/bin/env python3
"""Inspect images and materialize explicitly declared scene crops, locally."""
import argparse
import base64
import io
import json
from pathlib import Path
from image_provenance import open_image, checked_crop, pixel_digest, validate_resources


def crop_box(image, x, y, w, h):
    return checked_crop(image, dict(x=x, y=y, w=w, h=h))


def prepare(scene_path, source_path, output):
    scene_path, output = Path(scene_path).resolve(), Path(output).resolve()
    image = open_image(source_path)
    scene = json.loads(scene_path.read_text(encoding="utf-8-sig"))
    if scene.get("canvas") != {"width": image.width, "height": image.height}:
        raise ValueError("Scene canvas must equal EXIF-oriented source dimensions")
    if output in (scene_path, Path(source_path).resolve()):
        raise ValueError("Prepared output must not overwrite the source scene or image")
    manifest = scene.get("sourceAssets", [])
    if not isinstance(manifest, list):
        raise ValueError("sourceAssets must be an array")
    by_id = {}
    source_canvas = {"width": image.width, "height": image.height}
    for asset in manifest:
        if not isinstance(asset, dict) or not isinstance(asset.get("id"), str) or not asset["id"].strip() or asset["id"] in by_id:
            raise ValueError("Source asset IDs must be unique nonempty strings")
        if asset.get("canvas", source_canvas) != source_canvas:
            raise ValueError(asset["id"] + ": source canvas differs")
        asset["canvas"] = source_canvas.copy()
        digest = pixel_digest(checked_crop(image, asset.get("crop")))
        if asset.get("pixelSha256", digest) != digest:
            raise ValueError(asset["id"] + ": declared source pixels changed")
        asset["pixelSha256"] = digest
        by_id[asset["id"]] = asset
    for node in scene.get("nodes", []):
        if node.get("type") != "image":
            continue
        if "crop" in node:
            spec = node.pop("crop")
            part = crop_box(image, **{key: spec[key] for key in ("x", "y", "w", "h")})
            identity = node.get("sourceAssetId", node.get("id"))
            if not isinstance(identity, str) or not identity.strip():
                raise ValueError("Crop node needs a stable ID")
            canonical = {key: spec[key] for key in ("x", "y", "w", "h")}
            asset = by_id.get(identity)
            if asset is not None and asset["crop"] != canonical:
                raise ValueError(identity + ": crop differs from declared source asset")
            if asset is None:
                asset = {"id": identity, "crop": canonical, "canvas": source_canvas.copy(), "pixelSha256": pixel_digest(part)}
                manifest.append(asset)
                by_id[identity] = asset
            node.update(sourceAssetId=identity, sourceCrop=canonical.copy(), sourceCanvas=source_canvas.copy())
            data = io.BytesIO()
            part.save(data, format="PNG")
            node["href"] = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
        elif "file" in node:
            part = open_image(scene_path.parent / node.pop("file"))
            data = io.BytesIO()
            part.save(data, format="PNG")
            node["href"] = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
    if manifest:
        scene["sourceAssets"] = manifest
    errors, verified = validate_resources(scene, image)
    if errors:
        raise ValueError("\n".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"output": str(output), "width": image.width, "height": image.height, "sourceAssets": verified}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("image")
    crop = sub.add_parser("crop")
    crop.add_argument("image")
    crop.add_argument("--box", nargs=4, type=int, metavar=("X", "Y", "W", "H"), required=True)
    crop.add_argument("--output", required=True)
    prep = sub.add_parser("prepare")
    for key in ("scene", "source", "output"):
        prep.add_argument("--" + key, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.scene, args.source, args.output)
    else:
        image = open_image(args.image)
        if args.command == "inspect":
            result = {"width": image.width, "height": image.height, "coordinates": "EXIF-oriented pixels"}
        else:
            output = Path(args.output).resolve()
            if output == Path(args.image).resolve():
                raise ValueError("Crop output must not overwrite the source")
            output.parent.mkdir(parents=True, exist_ok=True)
            crop_box(image, *args.box).save(output, format="PNG")
            result = {"output": str(output), "sourceOffset": args.box[:2]}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
