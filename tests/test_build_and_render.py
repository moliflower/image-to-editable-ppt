import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))
from build_figure import build
import render_pptx as rendering


class BuildAndRenderTests(unittest.TestCase):
    def test_portable_build_with_unicode_paths_and_no_office(self):
        with tempfile.TemporaryDirectory(prefix="ppt test 中文 ", dir=BUILD) as folder:
            out = Path(folder) / "图 figure.pptx"
            result = build(ROOT / "tests/fixtures/scientific-text.scene.json", out, renderer="none")
            self.assertTrue(result["auditPassed"])
            self.assertEqual(result["objectCount"], 18)
            self.assertEqual(result["render"]["status"], "not-rendered")
            self.assertEqual(result["visualReview"], "pending")
            self.assertFalse(out.with_suffix(".prepared.scene.json").exists())
            self.assertTrue(out.with_suffix(".build.json").exists())
            with patch.object(rendering, "available_renderers", return_value={}):
                missing = rendering.render(out, out.with_suffix(".png"))
            self.assertEqual(missing["status"], "unavailable")
            self.assertNotIn("preview", missing)

    def test_crops_are_prepared_once_and_source_pixels_verified(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder = Path(folder)
            scene = json.loads((ROOT / "tests/fixtures/diagram.scene.json").read_text(encoding="utf-8"))
            scene["nodes"].append({"id":"crop", "type":"image", "x":800, "y":400, "w":40, "h":30,
                                   "crop":{"x":10,"y":20,"w":40,"h":30}, "assetPurpose":"photo"})
            source = folder / "source.png"
            Image.new("RGB", (1200, 650), (30, 100, 150)).save(source)
            input_file = folder / "input.json"
            original = json.dumps(scene)
            input_file.write_text(original, encoding="utf-8")
            out = folder / "figure.pptx"
            with self.assertRaisesRegex(ValueError, "source"):
                build(input_file, out, renderer="none")
            result = build(input_file, out, source, renderer="none")
            self.assertTrue(result["auditPassed"])
            audit = json.loads(out.with_suffix(".audit.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["originalSourceVerifiedAssets"], 1)
            self.assertEqual(input_file.read_text(encoding="utf-8"), original)
            with self.assertRaisesRegex(ValueError, "overwrite"):
                build(out.with_suffix(".exported.scene.json"), out, source, renderer="none")

    def test_clipping_warnings_survive_the_compact_build_report(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder = Path(folder)
            scene = json.loads((ROOT / "tests/fixtures/diagram.scene.json").read_text(encoding="utf-8"))
            scene["nodes"][0]["x"] = -50
            source = folder / "scene.json"
            source.write_text(json.dumps(scene), encoding="utf-8")
            result = build(source, folder / "figure.pptx", renderer="none")
            self.assertTrue(any("outside the canvas" in warning for warning in result["warnings"]))

    def test_fallback_and_cache_invalidation_verify_current_bytes(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder = Path(folder)
            out = folder / "figure.pptx"
            build(ROOT / "tests/fixtures/scientific-text.scene.json", out, renderer="none")
            png = folder / "preview.png"
            calls = []
            def fake_command(command, timeout=120):
                args = [str(arg) for arg in command]
                calls.append(args)
                if "-File" in args:
                    raise RuntimeError("Test backend unavailable")
                if "--convert-to" in args:
                    target = Path(args[args.index("--outdir") + 1]) / "figure.pdf"
                    target.write_bytes(b"test-only PDF marker")
                else:
                    width = int(args[args.index("-scale-to-x") + 1])
                    height = int(args[args.index("-scale-to-y") + 1])
                    Image.new("RGB", (width, height), (70, 130, 190)).save(args[-1] + ".png")
                return ""
            backends = {"powerpoint":[sys.executable], "libreoffice":[sys.executable,sys.executable]}
            with patch.object(rendering, "available_renderers", return_value=backends), patch.object(rendering, "run_command", side_effect=fake_command):
                first = rendering.render(out, png, width=800)
                self.assertEqual(first["status"], "rendered")
                self.assertEqual(first["renderer"], "libreoffice")
                self.assertEqual(len(first["attempts"]), 1)
                self.assertEqual(len(calls), 3)
                cached = rendering.render(out, png, renderer="auto", width=800)
                self.assertTrue(cached["cacheHit"])
                self.assertEqual(len(calls), 3)
                Image.new("RGB", (800, 440), "red").save(png)
                self.assertFalse(rendering.render(out, png, renderer="libreoffice", width=800)["cacheHit"])
                with out.open("ab") as f:
                    f.write(b"changed container bytes")
                self.assertFalse(rendering.render(out, png, renderer="libreoffice", width=800)["cacheHit"])
                self.assertFalse(rendering.render(out, png, renderer="libreoffice", width=900)["cacheHit"])
                self.assertFalse(rendering.render(out, png, renderer="libreoffice", width=900, force=True)["cacheHit"])
                self.assertEqual(len(calls), 11)

    def test_failure_does_not_claim_an_old_png_as_current(self):
        with tempfile.TemporaryDirectory(dir=BUILD) as folder:
            folder = Path(folder)
            out = folder / "figure.pptx"
            build(ROOT / "tests/fixtures/diagram.scene.json", out, renderer="none")
            png = folder / "preview.png"
            Image.new("RGB", (100,100), "red").save(png)
            with patch.object(rendering, "available_renderers", return_value={"libreoffice":[sys.executable,sys.executable]}), patch.object(rendering, "run_command", return_value=""):
                result = rendering.render(out, png, renderer="libreoffice")
            self.assertEqual(result["status"], "failed")
            self.assertNotIn("preview", result)
            self.assertIn("without producing", result["attempts"][0]["error"])


if __name__ == "__main__":
    unittest.main()
