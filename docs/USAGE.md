# Usage guide

[Home](../README.md) · [简体中文](USAGE.zh-CN.md) · [Scene schema](../references/scene-schema.md)

The agent interprets the reference image and reconstructs its elements. The local tools prepare image crops, export a scene, audit the package, and render the actual PPTX.

## Recommended command on Windows, macOS and Linux

```text
python -X utf8 scripts/build_figure.py --scene build/scene.json --source reference.png --output build/figure.pptx
```

Omit `--source` for scenes without source crops. This command prepares crops only if declared, exports once, audits once, and selects a renderer. Windows can use PowerPoint; all platforms can use LibreOffice plus Poppler. See [rendering setup and backend selection](../references/rendering.md). No PowerShell is needed for core export/audit or for LibreOffice rendering.

Inspect `render.status`: `rendered` means the actual PPTX produced a preview; `unavailable` means visual verification still needs a renderer. The `.build.json` report includes stage timings. Matching previews are cached using document/output hashes and renderer identity. Use `--force-render` after changing fonts. A cached image still needs visual review.

Ordinary figures do not need an edit probe, the repository test suite or another example regression. Perform those when maintaining the exporter or diagnosing a specific problem. The sections below expose the individual tools for troubleshooting and advanced use.

Visual review means inspecting the PNG rendered from the PPTX. It does not require Computer Use, opening the editor, clicking through slide objects or recording a GIF. Interactive demonstrations are separate, explicitly requested work.

## Installation and directory layout

Start with the [quick start](../README.md#quick-start). Install the complete repository:

```text
image-to-editable-ppt/
├── SKILL.md                     # Agent instructions
├── agents/openai.yaml           # Skill display and invocation configuration
├── scripts/
│   ├── export_pptx.mjs          # Native PPTX exporter
│   ├── image_assets.py         # Image inspection, crops, and embedding
│   ├── audit_pptx.py           # Independent OOXML audit
│   ├── build_figure.py         # Unified cross-platform build
│   ├── render_pptx.py          # Renderer selection and preview cache
│   └── render_powerpoint.ps1   # Optional Windows backend and edit probe
├── references/                 # Scene format and upstream provenance
├── vendor/figureforge/          # Pinned exporter and template
├── examples/                   # Minimal scene and public SAM 2 example
├── tests/
└── requirements.txt            # Pillow
```

Run the following commands from the repository root:

```bash
node --version
python --version
python -m pip install -r requirements.txt
```

Use Node.js 18+ and Python 3.10+. Install Pillow in the Python environment that will run the scripts. The Node exporter requires no `npm install`.

<a id="update"></a>

## Update an existing installation

From the installed skill directory:

```bash
git status --short
git pull --ff-only
python -m pip install -r requirements.txt
```

Preserve any local modifications before updating. For ZIP installations, back up your customized files and replace the complete skill directory. Keep generated outputs in a task directory or the ignored `build/` directory.

## From image to scene

Attach the image to a vision-capable agent session and invoke `$image-to-editable-ppt`. Specify whether to preserve source typography, use only the supplied bitmap, or consult additional source files. Identify any regions that may remain raster images.

Inspect source dimensions:

```bash
python -X utf8 scripts/image_assets.py inspect path/to/reference.png
```

Create a detail crop for closer inspection. Adjust these example coordinates to the source image:

```bash
python -X utf8 scripts/image_assets.py crop path/to/reference.png --box 100 80 300 200 --output build/detail.png
```

Coordinates refer to the EXIF-oriented source image. Retain crop offsets when mapping measurements back to the full canvas.

## Export an existing scene

```bash
node scripts/export_pptx.mjs --scene examples/diagram.scene.json --output build/figure.pptx
```

The exporter creates:

| Output | Purpose |
| --- | --- |
| `build/figure.pptx` | Native editable slide |
| `build/figure.exported.scene.json` | Normalized scene for auditing and revisions |
| `build/figure.editability.json` | Object counts, raster regions, warnings, and verification status |

The initial `visualVerification` status is `required`: successful export does not establish visual fidelity.

Re-export the public SAM 2 example:

```bash
node scripts/export_pptx.mjs --scene examples/sam2/scene.json --output build/sam2.pptx
```

The [example notes](../examples/sam2/README.md) describe its source, retained photo regions, and actual PowerPoint demonstration.

## Prepare image crops

A scene may declare a photographic region using `crop`:

```json
{
  "id": "sample-photo",
  "type": "image",
  "x": 100, "y": 200, "w": 180, "h": 120,
  "crop": {"x": 100, "y": 200, "w": 180, "h": 120},
  "assetPurpose": "photo",
  "assetDescription": "Photograph from the reference image"
}
```

Prepare those crops before exporting:

```bash
python -X utf8 scripts/image_assets.py prepare --scene build/scene.json --source path/to/reference.png --output build/prepared.scene.json
node scripts/export_pptx.mjs --scene build/prepared.scene.json --output build/figure.pptx
```

The helper checks canvas dimensions and crop boundaries, then embeds PNG data. Diagram labels, modules, and arrows must remain native objects rather than being concealed inside photo crops.

New crops retain `sourceAssetId`, `sourceCrop`, and `sourceCanvas`, plus a `sourceAssets` manifest containing pixel digests. Declare the expected crop inventory before preparation to detect missing or duplicate source regions. Without a predeclared inventory, the manifest covers only the crop nodes you supplied. Placement and rotation can change without changing source coordinates.

## Audit the PPTX

Audit against the normalized exported scene:

```bash
python -X utf8 scripts/audit_pptx.py --pptx build/figure.pptx --scene build/figure.exported.scene.json --report build/audit.json
```

`passed: true` confirms the checked object names, counts, text, arrow ends, rotations, dash spacing, image pixels, aspect ratio, and package relationships. It does not assess visual similarity, occlusion, or font metrics.

For prepared source crops, verify against the original pixels as well:

```bash
python -X utf8 scripts/audit_pptx.py --pptx build/figure.pptx --scene build/figure.exported.scene.json --source path/to/reference.png --report build/audit.json
```

Check `originalSourceVerifiedAssets` and `imagesWithoutSourceProvenance` in the report. Existing embedded-image scenes remain supported; a scene without crop provenance cannot establish source correspondence from its object count.

## Native geometry capabilities

Use `arrowStart: true` with `arrow: true` for a bidirectional path, `dash: [12, 6]` for source-pixel dash/gap lengths, and `rotation` for clockwise degrees on any supported object. The exporter preserves explicit font sizes and line breaks without browser Canvas or automatic fitting.

```bash
node scripts/export_pptx.mjs --scene examples/native-capabilities.scene.json --output build/native-capabilities.pptx
python -X utf8 scripts/audit_pptx.py --pptx build/native-capabilities.pptx --scene build/native-capabilities.exported.scene.json --source examples/sam2/reference.png
```

See the [scene schema](../references/scene-schema.md) for normalized dash inputs and source manifests.

## Scientific text

For mixed-format scientific labels, use `runs` within one text node. Run text must concatenate exactly to the node's `text`; font/color/emphasis inherit from the node, and `baselineShift` selects `super`/`sub` without shrinking the declared size. Optional `lineSpacing` uses source pixels. Gradient stops can include `opacity` from 0 to 1.

```bash
node scripts/export_pptx.mjs --scene examples/scientific-text.scene.json --output build/scientific-text.pptx
python -X utf8 scripts/audit_pptx.py --pptx build/scientific-text.pptx --scene build/scientific-text.exported.scene.json
```

The audit checks native run styles and gradient values, including intentional package-corruption cases in the test suite. See [schema examples](../references/scene-schema.md#scientific-text-within-one-editable-box) and the [rendered demo](../examples/scientific-text/README.md). Actual rendering is still needed to verify font availability and visual fit.

## Render an existing PPTX

```text
python -X utf8 scripts/render_pptx.py --pptx build/figure.pptx --output build/figure.png --renderer auto --width 1600
```

This uses the same backend selection and cache as the build command. It renders the actual PPTX, not the scene JSON. Fonts and renderers can differ, so check the result in the intended application when exact typography matters. Windows maintenance-only edit probes and installation instructions are in [rendering.md](../references/rendering.md).

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Skill is not discovered | Check `skills/image-to-editable-ppt/SKILL.md`, custom `CODEX_HOME`, and the client's skill reload mechanism |
| Missing exporter module | Install the complete repository, including `vendor/figureforge/` |
| `No module named PIL` | Install `requirements.txt` using the same Python environment that runs the script |
| Windows encoding error for symbols | Use the documented `python -X utf8 ...` invocation |
| Export asks to prepare crops | Run `image_assets.py prepare` and export its output scene |
| Crop bounds or canvas mismatch | Verify dimensions and EXIF orientation with `inspect` |
| Text overflows or fonts differ | Install the required font or explicitly choose a fallback, adjust the scene, and render again |
| PowerPoint COM access denied | Check desktop PowerPoint and whether the process is allowed to access desktop COM; use an authorized local process in restricted environments |
| PowerShell blocks script execution | Follow your environment's approved execution mechanism, or open and export the file manually in PowerPoint |
| Audit passes but the slide looks wrong | Inspect actual rendering, correct the scene, and repeat export and review |

## Revise a generated figure

Edit the retained scene, then export, audit, and render again. If you have already changed the PPTX directly, inspect that edited file before regenerating from an older scene.

See the [scene schema](../references/scene-schema.md) for supported fields and the [contribution guide](../CONTRIBUTING.md) for development checks.
