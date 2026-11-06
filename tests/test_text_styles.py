import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "build").mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
from audit_pptx import audit, NS


class TextStyleTests(unittest.TestCase):
    def test_audit_catches_corrupted_styles_and_gradient_semantics(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmp:
            tmp = Path(tmp)
            out = tmp / "figure.pptx"
            subprocess.run(["node", str(ROOT / "scripts/export_pptx.mjs"), "--scene",
                            str(ROOT / "tests/fixtures/scientific-text.scene.json"), "--output", str(out)],
                           check=True, capture_output=True)
            scene = tmp / "figure.exported.scene.json"
            report = audit(out, scene)
            self.assertTrue(report["passed"], report["errors"])
            self.assertEqual(report["richTextBoxes"], 3)
            self.assertEqual(report["gradientShapes"], 1)
            mutations = [
                ("font size", ".//a:rPr", "sz", "1000"),
                ("font family", ".//a:rPr/a:latin", "typeface", "Arial"),
                ("color", ".//a:rPr/a:solidFill/a:srgbClr", "val", "FF00FF"),
                ("baseline", ".//a:rPr[@baseline='-25000']", "baseline", "0"),
                ("bold", ".//a:rPr[@b='1']", "b", "0"),
                ("underline", ".//a:rPr[@u='sng']", "u", "none"),
                ("line spacing", ".//a:lnSpc/a:spcPts", "val", "999"),
                ("gradient angle", ".//a:gradFill/a:lin", "ang", "5400000"),
                ("gradient color", ".//a:gs/a:srgbClr", "val", "FFFFFF"),
                ("gradient opacity", ".//a:gs/a:srgbClr/a:alpha", "val", "40000"),
                ("gradient position", ".//a:gs", "pos", "10000")]
            for label, xpath, attr, value in mutations:
                with self.subTest(label=label):
                    broken = tmp / "broken.pptx"
                    with zipfile.ZipFile(out) as src, zipfile.ZipFile(broken, "w") as dst:
                        for info in src.infolist():
                            data = src.read(info.filename)
                            if info.filename == "ppt/slides/slide1.xml":
                                xml = ET.fromstring(data)
                                target = xml.find(xpath, NS)
                                self.assertIsNotNone(target, label)
                                target.set(attr, value)
                                data = ET.tostring(xml, encoding="utf-8")
                            dst.writestr(info, data)
                    failed = audit(broken, scene)
                    self.assertFalse(failed["passed"], label)
                    self.assertTrue(any("gradient" in e if label.startswith("gradient") else "text" in e for e in failed["errors"]), failed["errors"])

    def test_blank_lines_and_plain_text_stay_auditable(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmp:
            tmp = Path(tmp)
            for rich in (False, True):
                node = {"id": "label", "type": "text", "x": 30, "y": 30, "w": 800, "h": 300,
                        "fontSize": 25, "text": "  first\n\n最后  \n", "fontFamily": "Microsoft YaHei"}
                if rich:
                    node["runs"] = [{"text": "  first\n\n", "italic": True}, {"text": "最后  \n", "fill": "#396"}]
                scene = tmp / "input.json"
                scene.write_text(json.dumps({"canvas": {"width": 1000, "height": 600}, "nodes": [node]}), encoding="utf-8")
                out = tmp / "figure.pptx"
                subprocess.run(["node", str(ROOT / "scripts/export_pptx.mjs"), "--scene", str(scene), "--output", str(out)], check=True, capture_output=True)
                report = audit(out, tmp / "figure.exported.scene.json")
                self.assertTrue(report["passed"], report["errors"])
                self.assertEqual(report["text"], [node["text"]])


if __name__ == "__main__":
    unittest.main()
