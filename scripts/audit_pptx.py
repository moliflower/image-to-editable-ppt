#!/usr/bin/env python3
"""Independently inspect native objects and package integrity; no rendering claim."""
import argparse
import collections
import json
import math
import posixpath
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from image_provenance import decode_image, embedded_image, open_image, pixel_digest, validate_resources

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def audit(pptx, scene_path, source_path=None):
    scene = json.loads(Path(scene_path).read_text(encoding="utf-8-sig"))
    source = open_image(source_path) if source_path is not None else None
    errors, verified_assets = validate_resources(scene, source)
    with zipfile.ZipFile(pptx) as package:
        if package.testzip():
            errors.append("ZIP CRC check failed")
        names = set(package.namelist())
        documents = {}
        for name in names:
            if name.endswith((".xml", ".rels")):
                try:
                    documents[name] = ET.fromstring(package.read(name))
                except ET.ParseError as exc:
                    errors.append(f"Invalid XML {name}: {exc}")
        for name, doc in documents.items():
            if not name.endswith(".rels"):
                continue
            folder = posixpath.dirname(name).removesuffix("_rels").rstrip("/")
            for rel in doc:
                if rel.get("TargetMode") == "External":
                    errors.append("External relationship: " + name)
                    continue
                target = rel.get("Target", "")
                resolved = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(folder, target))
                if resolved not in names:
                    errors.append(f"Missing relationship target: {name} -> {target}")
        slides = sorted(n for n in documents if n.startswith("ppt/slides/slide") and n.endswith(".xml"))
        if len(slides) != 1:
            errors.append("Expected exactly one figure slide")
        slide = documents.get("ppt/slides/slide1.xml")
        if slide is None:
            raise ValueError("Missing slide XML")
        tree = slide.find("p:cSld/p:spTree", NS)
        objects = [n for n in tree if n.tag.rsplit("}", 1)[-1] in ("sp", "pic", "cxnSp", "grpSp", "graphicFrame")]
        expected = scene["nodes"]
        if len(objects) != len(expected):
            errors.append(f"Object count differs: {len(objects)} vs {len(expected)}")
        texts, images, arrows, arrowheads, verified_images = [], 0, 0, 0, 0
        rels = documents.get("ppt/slides/_rels/slide1.xml.rels")
        media = {r.get("Id"): posixpath.normpath(posixpath.join("ppt/slides", r.get("Target", ""))) for r in rels} if rels is not None else {}
        unit = 9144000 / scene["canvas"]["width"]
        for obj, node in zip(objects, expected):
            identity = obj.find(".//p:cNvPr", NS)
            if identity is None or identity.get("name") != node.get("name", node["id"]):
                errors.append(node["id"] + ": missing independent object name")
            kind = obj.tag.rsplit("}", 1)[-1]
            if node["type"] == "image":
                images += 1
                if kind != "pic":
                    errors.append(node["id"] + ": expected picture")
                try:
                    blip = obj.find(".//a:blip", NS)
                    actual_image = decode_image(package.read(media[blip.get("{" + NS["r"] + "}embed")]))
                    if pixel_digest(actual_image) != pixel_digest(embedded_image(node.get("href"))):
                        errors.append(node["id"] + ": PPTX image pixels differ from scene")
                    else:
                        verified_images += 1
                except (KeyError, AttributeError, ValueError, OSError) as exc:
                    errors.append(node["id"] + ": could not verify embedded image: " + str(exc))
            elif kind != "sp":
                errors.append(node["id"] + ": expected native editable shape")
            if node["type"] == "text":
                actual = "\n".join("".join(p.itertext()) for p in obj.findall("p:txBody/a:p", NS))
                if actual != node["text"].replace("\r\n", "\n"):
                    errors.append(node["id"] + ": text differs")
                texts.append(actual)
            transform = obj.find("p:spPr/a:xfrm", NS)
            expected_rotation = math.floor(float(node.get("rotation", 0)) * 60000 + .5) % 21600000
            actual_rotation = int(transform.get("rot", "0")) % 21600000 if transform is not None else 0
            if actual_rotation != expected_rotation:
                errors.append(node["id"] + ": rotation differs")
            if node.get("arrow") or node.get("arrowStart"):
                arrows += 1
            for field, element in [("arrowStart", "headEnd"), ("arrow", "tailEnd")]:
                expected_head = bool(node.get(field))
                head = obj.find(".//a:" + element, NS)
                actual = head is not None and head.get("type", "none") != "none"
                arrowheads += int(expected_head)
                if expected_head != actual or (expected_head and head.get("type") != "triangle"):
                    errors.append(node["id"] + ": " + field + " arrowhead differs")
            if node.get("stroke") not in (None, "none") and node["type"] not in ("image", "text"):
                custom = obj.findall("p:spPr/a:ln/a:custDash/a:ds", NS)
                preset = obj.find("p:spPr/a:ln/a:prstDash", NS)
                dash = node.get("dash", False)
                if isinstance(dash, list):
                    pattern = dash + dash if len(dash) % 2 else dash
                    width = max(1, math.floor(node.get("strokeWidth", 1) * unit + .5))
                    relative = lambda v: min(2147483647, math.floor(v * unit / width * 100000 + .5))
                    wanted = [(relative(pattern[i]), relative(pattern[i+1])) for i in range(0, len(pattern), 2)]
                    actual = [(int(d.get("d", -1)), int(d.get("sp", -1))) for d in custom]
                    if actual != wanted or preset is not None:
                        errors.append(node["id"] + ": custom dash spacing differs")
                elif dash is True:
                    if custom or preset is None or preset.get("val") != "dash":
                        errors.append(node["id"] + ": preset dash differs")
                elif custom or (preset is not None and preset.get("val") != "solid"):
                    errors.append(node["id"] + ": expected solid stroke")
        if not any(n["type"] != "image" for n in expected):
            errors.append("No native editable objects")
        pres = documents["ppt/presentation.xml"]
        size = pres.find("p:sldSz", NS)
        aspect = int(size.get("cy")) / int(size.get("cx"))
        if abs(aspect - scene["canvas"]["height"] / scene["canvas"]["width"]) > 1e-6:
            errors.append("Aspect ratio differs from source")
    return {"passed": not errors, "errors": errors, "objectCount": len(objects),
            "textBoxes": len(texts), "nativeShapes": len(objects) - images, "images": images,
            "arrows": arrows, "arrowheads": arrowheads, "verifiedImagePixels": verified_images,
            "verifiedSourceAssets": verified_assets,
            "originalSourceChecked": source_path is not None and bool(scene.get("sourceAssets")),
            "originalSourceVerifiedAssets": verified_assets if source is not None else 0,
            "imagesWithoutSourceProvenance": sum(n.get("type") == "image" and "sourceAssetId" not in n for n in scene["nodes"]),
            "text": texts, "visualVerification": "not-performed-by-this-audit"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pptx", required=True)
    p.add_argument("--scene", required=True)
    p.add_argument("--report")
    p.add_argument("--source", help="Original reference image for independent source-crop pixel verification")
    args = p.parse_args()
    result = audit(args.pptx, args.scene, args.source)
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
