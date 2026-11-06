"""Opt-in actual LibreOffice/Poppler smoke test for the Linux CI renderer job."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
from build_figure import build


@unittest.skipUnless(os.environ.get("TEST_LIBREOFFICE") == "1", "Requires installed LibreOffice and Poppler")
class LibreOfficeIntegrationTests(unittest.TestCase):
    def test_real_pptx_render_and_reuse(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            out = Path(folder) / "scientific.pptx"
            first = build(ROOT / "examples/scientific-text.scene.json", out, renderer="libreoffice", width=1200)
            self.assertTrue(first["auditPassed"])
            self.assertEqual(first["render"]["status"], "rendered", first["render"])
            with Image.open(out.with_suffix(".png")) as image:
                self.assertEqual(image.size, (1200,660))
                difference = ImageChops.difference(image.convert("RGB"), Image.new("RGB", image.size, "white"))
                self.assertIsNotNone(difference.getbbox(), "Renderer produced a blank slide")
            second = build(ROOT / "examples/scientific-text.scene.json", out, renderer="libreoffice", width=1200)
            self.assertTrue(second["render"]["cacheHit"])
            self.assertEqual(first["render"]["pptxSha256"], second["render"]["pptxSha256"])


if __name__ == "__main__":
    unittest.main()

