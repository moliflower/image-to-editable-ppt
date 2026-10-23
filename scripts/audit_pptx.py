#!/usr/bin/env python3
"""Independently inspect native objects and package integrity; no rendering claim."""
import argparse
import collections
import json
import posixpath
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def audit(pptx, scene_path):
    scene = json.loads(Path(scene_path).read_text(encoding="utf-8-sig"))
    errors = []
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
        texts, images, arrows = [], 0, 0
        for obj, node in zip(objects, expected):
            identity = obj.find(".//p:cNvPr", NS)
            if identity is None or identity.get("name") != node.get("name", node["id"]):
                errors.append(node["id"] + ": missing independent object name")
            kind = obj.tag.rsplit("}", 1)[-1]
            if node["type"] == "image":
                images += 1
                if kind != "pic":
                    errors.append(node["id"] + ": expected picture")
            elif kind != "sp":
                errors.append(node["id"] + ": expected native editable shape")
            if node["type"] == "text":
                actual = "\n".join("".join(p.itertext()) for p in obj.findall("p:txBody/a:p", NS))
                if actual != node["text"].replace("\r\n", "\n"):
                    errors.append(node["id"] + ": text differs")
                texts.append(actual)
            if node.get("arrow"):
                arrows += 1
                if obj.find(".//a:tailEnd", NS) is None:
                    errors.append(node["id"] + ": missing arrowhead")
        if not any(n["type"] != "image" for n in expected):
            errors.append("No native editable objects")
        pres = documents["ppt/presentation.xml"]
        size = pres.find("p:sldSz", NS)
        aspect = int(size.get("cy")) / int(size.get("cx"))
        if abs(aspect - scene["canvas"]["height"] / scene["canvas"]["width"]) > 1e-6:
            errors.append("Aspect ratio differs from source")
    return {"passed": not errors, "errors": errors, "objectCount": len(objects),
            "textBoxes": len(texts), "nativeShapes": len(objects) - images, "images": images,
            "arrows": arrows, "text": texts, "visualVerification": "not-performed-by-this-audit"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pptx", required=True)
    p.add_argument("--scene", required=True)
    p.add_argument("--report")
    args = p.parse_args()
    result = audit(args.pptx, args.scene)
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
