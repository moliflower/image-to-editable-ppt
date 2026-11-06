#!/usr/bin/env python3
"""Prepare when needed, export, independently audit, and render a figure once."""
import argparse
import json
from pathlib import Path
import shutil
import time
from audit_pptx import audit
from image_assets import prepare
from render_pptx import render, run_command

HERE = Path(__file__).resolve().parent


def build(scene, output, source=None, renderer="auto", width=1600, force_render=False):
    scene, output = Path(scene).resolve(), Path(output).resolve()
    source = Path(source).resolve() if source else None
    if output.suffix.lower() != ".pptx":
        raise ValueError("Output must end in .pptx")
    stem = output.with_suffix("")
    files = {key: Path(str(stem) + suffix) for key, suffix in {
        "prepared": ".prepared.scene.json", "normalized": ".exported.scene.json", "audit": ".audit.json",
        "build": ".build.json", "preview": ".png", "render": ".render.json", "editability": ".editability.json"}.items()}
    if scene in [output, *files.values()] or source in [output, *files.values()]:
        raise ValueError("Output artifacts must not overwrite the input scene or source image")
    data = json.loads(scene.read_text(encoding="utf-8-sig"))
    if source and not source.is_file():
        raise ValueError("Source image does not exist")
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js 18+ is required for export")
    timings = {}
    start = time.perf_counter()
    export_scene = scene
    if any("crop" in n for n in data.get("nodes", [])):
        if source is None:
            raise ValueError("--source is required when the scene declares image crops")
        prepare(scene, source, files["prepared"])
        export_scene = files["prepared"]
    timings["prepare"] = round(time.perf_counter() - start, 3)
    at = time.perf_counter()
    exported = json.loads(run_command([node, HERE / "export_pptx.mjs", "--scene", export_scene, "--output", output]))
    timings["export"] = round(time.perf_counter() - at, 3)
    at = time.perf_counter()
    normalized = json.loads(files["normalized"].read_text(encoding="utf-8"))
    # The original image is relevant to the independent audit only for declared source crops.
    audit_source = source if normalized.get("sourceAssets") else None
    checked = audit(output, files["normalized"], audit_source)
    files["audit"].write_text(json.dumps(checked, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    timings["audit"] = round(time.perf_counter() - at, 3)
    if checked["passed"]:
        at = time.perf_counter()
        preview = render(output, files["preview"], renderer, width, force_render)
        timings["render"] = round(time.perf_counter() - at, 3)
    else:
        preview = {"status": "not-rendered", "reason": "Package audit failed"}
    timings["total"] = round(time.perf_counter() - start, 3)
    result = {"output": str(output), "auditPassed": checked["passed"], "objectCount": checked["objectCount"],
              "textBoxes": checked["textBoxes"], "images": checked["images"], "errors": checked["errors"],
              "warnings": exported.get("warnings", []), "reviewNotes": exported.get("reviewNotes", []),
              "render": preview, "timingsSeconds": timings, "visualReview": "pending"}
    files["build"].write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source")
    parser.add_argument("--renderer", choices=["auto", "powerpoint", "libreoffice", "none"], default="auto")
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--force-render", action="store_true")
    args = parser.parse_args()
    result = build(args.scene, args.output, args.source, args.renderer, args.width, args.force_render)
    preview = result["render"]
    print(json.dumps({"output": result["output"], "auditPassed": result["auditPassed"],
                      "objects": result["objectCount"], "textBoxes": result["textBoxes"], "images": result["images"],
                      "warningCount": len(result["warnings"]), "warnings": result["warnings"][:8],
                      "render": {k: preview[k] for k in ("status", "renderer", "preview", "cacheHit", "reason", "attempts") if k in preview},
                      "timingsSeconds": result["timingsSeconds"], "visualReview": "pending"}, ensure_ascii=False, indent=2))
    failed_render = preview["status"] == "failed" or (args.renderer not in ("auto", "none") and preview["status"] != "rendered")
    raise SystemExit(0 if result["auditPassed"] and not failed_render else 1)


if __name__ == "__main__":
    main()
