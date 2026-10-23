#!/usr/bin/env python3
"""Inspect images and materialize explicitly declared scene crops, locally."""
import argparse
import base64
import io
import json
from pathlib import Path
from PIL import Image, ImageOps


def open_image(filename):
    with Image.open(filename) as source:
        return ImageOps.exif_transpose(source).convert("RGBA")


def crop_box(image, x, y, w, h):
    if w <= 0 or h <= 0 or min(x, y) < 0 or x + w > image.width or y + h > image.height:
        raise ValueError("Crop is outside source image or has nonpositive size")
    return image.crop((x, y, x + w, y + h))


def prepare(scene_path, source_path, output):
    scene_path, output = Path(scene_path).resolve(), Path(output).resolve()
    image = open_image(source_path)
    scene = json.loads(scene_path.read_text(encoding="utf-8-sig"))
    if scene.get("canvas") != {"width": image.width, "height": image.height}:
        raise ValueError("Scene canvas must equal EXIF-oriented source dimensions")
    for node in scene.get("nodes", []):
        if node.get("type") != "image":
            continue
        if "crop" in node:
            spec = node.pop("crop")
            part = crop_box(image, **{key: spec[key] for key in ("x", "y", "w", "h")})
            data = io.BytesIO()
            part.save(data, format="PNG")
            node["href"] = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
        elif "file" in node:
            part = open_image(scene_path.parent / node.pop("file"))
            data = io.BytesIO()
            part.save(data, format="PNG")
            node["href"] = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"output": str(output), "width": image.width, "height": image.height}


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
