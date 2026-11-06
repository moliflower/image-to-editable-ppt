#!/usr/bin/env python3
"""Render a one-slide PPTX using an installed Office renderer, on any OS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_command(command, timeout=120):
    result = subprocess.run([str(arg) for arg in command], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or f"Command failed: {command[0]}")[-6000:])
    return result.stdout


def executable(override, names, paths=()):
    if os.environ.get(override):
        candidate = Path(os.environ[override]).expanduser()
        return str(candidate.resolve()) if candidate.is_file() else None
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return next((str(Path(p)) for p in paths if Path(p).is_file()), None)


def available_renderers():
    found = {}
    if platform.system() == "Windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application\CLSID"):
                host = shutil.which("powershell.exe")
                if host:
                    found["powerpoint"] = [host]
        except OSError:
            pass
    office_paths = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    for root in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if root:
            office_paths.extend(str(Path(root) / "LibreOffice/program" / name) for name in ("soffice.com", "soffice.exe"))
    office = executable("SOFFICE_PATH", ["soffice.com", "soffice", "libreoffice"], office_paths)
    poppler = executable("PDFTOPPM_PATH", ["pdftoppm"])
    if office and poppler:
        found["libreoffice"] = [office, poppler]
    return found


def slide_ratio(pptx):
    with zipfile.ZipFile(pptx) as package:
        ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        root = ET.fromstring(package.read("ppt/presentation.xml"))
        if len(root.findall("p:sldIdLst/p:sldId", ns)) != 1:
            raise ValueError("Expected exactly one figure slide")
        size = root.find("p:sldSz", ns)
        return int(size.get("cy")) / int(size.get("cx"))


def backend_signature(backend, binaries):
    tools = []
    for binary in binaries:
        path = Path(binary).resolve()
        stat = path.stat()
        tools.append([str(path), stat.st_size, stat.st_mtime_ns])
    return {"backend": backend, "tools": tools, "adapter": digest(__file__),
            "powerpointScript": digest(HERE / "render_powerpoint.ps1") if backend == "powerpoint" else None}


def render(pptx, output, renderer="auto", width=1600, force=False):
    pptx, output = Path(pptx).resolve(), Path(output).resolve()
    if output.suffix.lower() != ".png" or output == pptx:
        raise ValueError("Preview must be a separate .png file")
    if not isinstance(width, int) or not 100 <= width <= 10000:
        raise ValueError("Preview width must be between 100 and 10000 pixels")
    if renderer not in ("auto", "none", "powerpoint", "libreoffice"):
        raise ValueError("Unknown renderer")
    height = max(1, int(width * slide_ratio(pptx) + .5))
    source_hash = digest(pptx)
    report = {"status": "not-rendered", "pptxSha256": source_hash,
              "visualReview": "pending", "width": width, "height": height}
    if renderer == "none":
        return {**report, "reason": "Rendering explicitly disabled"}
    available = available_renderers()
    choices = list(available) if renderer == "auto" else [renderer] if renderer in available else []
    if not choices:
        return {**report, "status": "unavailable", "reason": "Install LibreOffice and Poppler (pdftoppm), or desktop PowerPoint on Windows. See references/rendering.md."}
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = output.with_suffix(".render.json")
    failures = []
    try:
        if not force and output.is_file() and metadata.is_file():
            previous = json.loads(metadata.read_text(encoding="utf-8"))
            cached_backend = previous.get("renderer")
            if (cached_backend in choices and previous.get("status") == "rendered" and previous.get("pptxSha256") == source_hash
                    and previous.get("signature") == backend_signature(cached_backend, available[cached_backend])
                    and previous.get("width") == width and previous.get("height") == height
                    and previous.get("pngSha256") == digest(output)):
                return {**previous, "cacheHit": True, "attempts": failures}
    except (ValueError, OSError):
        pass  # An absent or damaged cache is rendered afresh.
    for backend in choices:
        try:
            signature = backend_signature(backend, available[backend])
            with tempfile.TemporaryDirectory(prefix=".pptx-render-", dir=output.parent) as folder:
                temp = Path(folder)
                image = temp / "preview.png"
                if backend == "powerpoint":
                    run_command([available[backend][0], "-NoProfile", "-NonInteractive", "-File",
                                 HERE / "render_powerpoint.ps1", "-InputPptx", pptx,
                                 "-OutputPng", image, "-Width", width, "-SummaryOnly"])
                else:
                    profile = (temp / "profile").as_uri()
                    run_command([available[backend][0], "-env:UserInstallation=" + profile, "--headless",
                                 "--nologo", "--norestore", "--convert-to", "pdf:impress_pdf_Export",
                                 "--outdir", temp, pptx])
                    pdf = temp / (pptx.stem + ".pdf")
                    if not pdf.is_file() or pdf.stat().st_size == 0:
                        raise RuntimeError("LibreOffice returned without producing a PDF")
                    run_command([available[backend][1], "-f", "1", "-l", "1", "-singlefile",
                                 "-scale-to-x", width, "-scale-to-y", height, "-png", pdf, temp / "preview"])
                with Image.open(image) as preview:
                    preview.load()
                    if preview.size != (width, height):
                        raise RuntimeError(f"Renderer returned unexpected preview dimensions: {preview.size}")
                if digest(pptx) != source_hash:
                    raise RuntimeError("PPTX changed while rendering; run again")
                shutil.copyfile(image, output)
            result = {**report, "status": "rendered", "renderer": backend, "cacheHit": False,
                      "signature": signature, "pngSha256": digest(output), "preview": str(output), "attempts": failures}
            metadata.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            return result
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            failures.append({"renderer": backend, "error": str(exc)})
    failed = {**report, "status": "failed", "attempts": failures,
              "reason": "Available renderers failed; no current preview verified"}
    metadata.write_text(json.dumps(failed, indent=2) + "\n", encoding="utf-8")
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pptx", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--renderer", choices=["auto", "powerpoint", "libreoffice", "none"], default="auto")
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--force", action="store_true", help="Re-render after font or renderer changes")
    args = parser.parse_args()
    result = render(args.pptx, args.output, args.renderer, args.width, args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] in ("rendered", "not-rendered") else 1)


if __name__ == "__main__":
    main()
