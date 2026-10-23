import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)


def load_module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assets = load_module("image_assets", "image_assets.py")
audit_module = load_module("audit_pptx", "audit_pptx.py")


class ImageAuditTests(unittest.TestCase):
    def test_crop_and_embedded_image_round_trip(self):
        with tempfile.TemporaryDirectory(prefix="editable-ppt-", dir=BUILD) as tmp:
            tmp = Path(tmp)
            source = tmp / "source.png"
            Image.new("RGB", (1200, 650), (20, 120, 190)).save(source)
            scene = json.loads((ROOT / "examples/diagram.scene.json").read_text(encoding="utf-8"))
            scene["nodes"].append({"id": "sample-photo", "type": "image", "x": 70, "y": 500,
                                   "w": 120, "h": 80, "crop": {"x": 20, "y": 30, "w": 120, "h": 80},
                                   "assetPurpose": "photo", "assetDescription": "Synthetic crop fixture"})
            original = tmp / "scene.json"
            prepared = tmp / "prepared.json"
            original.write_text(json.dumps(scene), encoding="utf-8")
            assets.prepare(original, source, prepared)
            node = json.loads(prepared.read_text())["nodes"][-1]
            self.assertTrue(node["href"].startswith("data:image/png;base64,"))
            self.assertNotIn("crop", node)
            pptx = tmp / "figure.pptx"
            subprocess.run(["node", str(ROOT / "scripts/export_pptx.mjs"), "--scene", str(prepared),
                            "--output", str(pptx)], check=True, capture_output=True)
            normalized = tmp / "figure.exported.scene.json"
            report = audit_module.audit(pptx, normalized)
            self.assertTrue(report["passed"], report["errors"])
            self.assertEqual(report["images"], 1)
            self.assertEqual(report["textBoxes"], 6)
            self.assertEqual(report["arrows"], 3)
            broken = tmp / "broken.pptx"
            with zipfile.ZipFile(pptx) as src, zipfile.ZipFile(broken, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename == "ppt/slides/slide1.xml":
                        data = data.replace("输入图片".encode(), "错误内容".encode())
                    dst.writestr(info, data)
            self.assertFalse(audit_module.audit(broken, normalized)["passed"])

    def test_crop_bounds_and_canvas_mismatch(self):
        image = Image.new("RGB", (20, 20))
        with self.assertRaises(ValueError):
            assets.crop_box(image, 19, 0, 5, 5)
        with tempfile.TemporaryDirectory(dir=BUILD) as tmp:
            tmp = Path(tmp)
            source, scene = tmp / "image.png", tmp / "scene.json"
            image.save(source)
            scene.write_text('{"canvas":{"width":40,"height":40},"nodes":[]}')
            with self.assertRaises(ValueError):
                assets.prepare(scene, source, tmp / "prepared.json")


if __name__ == "__main__":
    unittest.main()
