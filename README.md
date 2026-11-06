<div align="center">

# Image to Editable PowerPoint

**Reconstruct an existing diagram as PowerPoint objects you can keep editing.**

Visual understanding by your agent. Native PPTX export with a local FigureForge exporter.

[![Checks](https://github.com/moliflower/image-to-editable-ppt/actions/workflows/test.yml/badge.svg)](https://github.com/moliflower/image-to-editable-ppt/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563eb.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7c3aed.svg)](SKILL.md)

**English** · [简体中文](README.zh-CN.md)

[Showcase](#showcase) · [Quick start](#quick-start) · [How it works](#how-it-works) · [FAQ](#faq) · [Contributing](https://github.com/moliflower/image-to-editable-ppt/blob/main/.github/CONTRIBUTING.md)

</div>

---

<a id="showcase"></a>

## From image to editable PowerPoint

### PosDiffNet · AAAI 2024

Feature tensors, similarity matrices and attention paths, reconstructed from [PosDiffNet, Figure 1](https://doi.org/10.1609/aaai.v38i1.27775) by She et al.

**Reconstructed figure**

![PosDiffNet architecture rendered from the editable PowerPoint file](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/posdiffnet/preview.png)

**All objects selected in PowerPoint**

![Actual PowerPoint screenshot with all 478 PosDiffNet objects selected](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/docs/assets/posdiffnet-all-selected.png)

478 independent objects, including editable labels, matrix cells, feature faces and paths. Only the three point-cloud views remain images.

### RepoMaster · NeurIPS 2025

Repository trees, dependency graphs and a circular workflow, reconstructed from [RepoMaster, Figure 1](https://arxiv.org/abs/2505.21577) by Wang et al.

**Reconstructed figure**

![RepoMaster overview rendered from the editable PowerPoint file](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/repomaster/preview.png)

**All objects selected in PowerPoint**

![Actual PowerPoint screenshot with all 353 RepoMaster objects selected](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/docs/assets/repomaster-all-selected.png)

353 independent objects. Text, graph nodes, modules and routes remain editable; 16 complex logos and illustrations stay as separate images.

### Watch it edited · SAM 2

Select a label, change its text, move a module and select an arrow in desktop PowerPoint.

![Actual PowerPoint recording: selecting text, editing a label, moving a module and selecting an arrow in the SAM 2 example](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/docs/assets/powerpoint-editing.gif)

The selection screenshots and animation show real PowerPoint UI. Showcase media is hosted separately from the installed skill.

## What the skill does

- Reconstructs labels, modules, matrices and arrows as independent PowerPoint objects.
- Preserves reference wording, aspect ratio and connection topology where the source permits.
- Supports mixed text styles, superscripts/subscripts, gradients, custom dashes and rotated geometry.
- Retains photos and complex artwork as separate crops, with source-pixel checks.
- Exports locally, audits the PPTX and renders it with an available Office backend.

Image interpretation is performed by your vision-capable agent. The bundled exporter needs no extra vision API key, GPU, npm packages or browser Canvas.

<a id="quick-start"></a>

## Quick start

### Install the skill

**[Download the skill ZIP](https://github.com/moliflower/image-to-editable-ppt/archive/refs/heads/main.zip)** and extract it as `image-to-editable-ppt/` in your agent's skills directory. The ZIP includes the runtime, its instructions and licenses. It excludes tests, CI configuration and demonstration files.

For a Git installation, run this from your agent's skills directory:

```text
git clone --depth 1 --single-branch --branch main https://github.com/moliflower/image-to-editable-ppt.git image-to-editable-ppt
python -m pip install -r image-to-editable-ppt/requirements.txt
```

For a ZIP installation, run the same `pip install` command from the parent folder. For Codex, the usual skills directory is `~/.codex/skills`, or `<CODEX_HOME>/skills` when configured. Avoid an extra `image-to-editable-ppt-main/` nesting level.

The shallow Git command avoids downloading historical showcase assets. Git checkouts also contain small maintenance tests; these are excluded from the install ZIP.

### Requirements

| Dependency | Purpose |
| --- | --- |
| Vision-capable agent with skill support | Interpret the image and author the reconstruction |
| Node.js 18+ | Export native PPTX |
| Python 3.10+ and Pillow | Prepare crops and audit the exported file |
| LibreOffice + Poppler, or Microsoft PowerPoint on Windows | Optional actual-PPTX previews |

Export and audit work on **Windows, macOS and Linux** without Office or PowerShell. LibreOffice rendering works on all three platforms. [Renderer setup](references/rendering.md).

### Attach an image and ask

```text
Use $image-to-editable-ppt to reconstruct this image as an editable PPTX.
Preserve its wording, aspect ratio and layout. Make text, modules and arrows
independently editable. Return the PPTX and a preview rendered from that file.
```

The result is a single-slide PPTX plus an actual rendered preview when a renderer is installed. The scene JSON is retained for revisions. Raster regions, uncertain labels and incomplete visual verification are disclosed.

<a id="update"></a>

### Update

For an existing Git install, run `git pull --ff-only` from the skill folder, then `python -m pip install -r requirements.txt`. For a ZIP install, replace the installed skill with the current ZIP, preserving any changes you made yourself. Keep task outputs outside the installed skill folder.

<a id="how-it-works"></a>

## How it works

1. Inspect the reference and resolve dense or ambiguous details.
2. Author a pixel-coordinate scene with separate objects and reusable scientific components.
3. Export once, independently audit once, and render the actual PPTX.
4. Review the rendered PNG, correct material defects, and deliver the file.

Routine verification does not require Computer Use, desktop clicking or a recording. The visible UI examples above are demonstrations. Source fonts and explicit user typography take priority; otherwise scientific English and mathematics default to Times New Roman.

## Editability and limits

| Source content | Output and limits |
| --- | --- |
| Text, geometric modules, matrices | Native text and shapes; font substitution can affect spacing |
| Lines, arrows and curves | Native paths; they do not automatically reattach when a module moves |
| Photos, heatmaps and detailed artwork | Separate images; internal pixels remain raster |
| Equations and bitmap charts | Editable text/geometry; original equation structures and numerical data are not recovered |

Low resolution, occlusion and unusual glyphs need extra review. A successful example is not a guarantee of pixel-perfect reconstruction for every input. This skill reconstructs one image per slide; it does not bundle unattended batch recognition.

## What is installed

```text
image-to-editable-ppt/
├── SKILL.md                 Agent workflow
├── agents/                  Skill discovery metadata
├── scripts/                 Export, audit, rendering and scientific components
├── references/              Scene schema, components and renderer instructions
├── vendor/figureforge/      Bundled exporter, template and upstream notices
└── requirements.txt         Python dependency
```

The package also includes the README files and licenses. The three `references/` files are operational instructions for the agent, not paper reference images. They are read when needed. Showcase images, example PPTX files, reconstruction scenes, benchmark reports and research notes are not installed.

For manual debugging of an already-authored scene, run from the skill directory:

```text
python -X utf8 scripts/build_figure.py --scene /path/to/scene.json --source /path/to/reference.png --output /path/to/figure.pptx
```

Omit `--source` when the scene has no source crops. See the [scene schema](references/scene-schema.md), [component API](references/components.md) and [rendering options](references/rendering.md).

<a id="faq"></a>

## FAQ

**Can I share only `SKILL.md`?** Share the install ZIP. The instructions use the bundled scripts, reference guides and exporter.

**Why is the skill not detected?** Check that `image-to-editable-ppt/SKILL.md` is directly under your client's skills folder. Reload skills using your client's supported mechanism, or start a new session and invoke the skill explicitly.

**Does local export mean the image never leaves my computer?** The bundled scripts make no network requests. Image handling by the agent client follows that client's behavior. README showcase media is loaded by the page viewer, separately from the exporter.

## Contributing and attribution

Maintainer tests and CI remain in the Git repository; the install ZIP excludes them. [Contributing guide](https://github.com/moliflower/image-to-editable-ppt/blob/main/.github/CONTRIBUTING.md) · [Issues](https://github.com/moliflower/image-to-editable-ppt/issues).

Native export builds on [FigureForge](https://github.com/qwdwqfwq/topconf-paper-figure-gallery). Its [license](vendor/figureforge/LICENSE) and [pinned-source/adaptation notes](vendor/figureforge/UPSTREAM.md) are retained. Skill instructions and wrapper code use the [MIT License](LICENSE).

Showcase artwork retains its original rights: [PosDiffNet](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/posdiffnet/SOURCE.md), [RepoMaster](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/repomaster/SOURCE.md), and [SAM 2](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/sam2/NOTICE.md). These fixed-version media and notices are hosted separately and are not part of the install package.
