# Contributing

[Home](README.md) · [简体中文首页](README.zh-CN.md)

Contributions to reconstruction instructions, documentation, exporter compatibility, auditing, and public examples are welcome. Keep each change focused on a concrete, reproducible problem.

## Report a problem

Open an [issue](https://github.com/moliflower/image-to-editable-ppt/issues) with:

- Actual and expected behavior, plus minimal reproduction steps.
- Operating system, Node.js / Python versions, and the agent client used.
- PowerPoint or other renderer version when the problem is visual.
- A reference image, scene JSON, PPTX, or screenshot that you are allowed to share publicly.
- Relevant exporter warnings, audit results, or error messages.

Remove private content, account details, and credentials before attaching files. Recognition errors, scene errors, export bugs, and renderer differences have different causes; retaining the scene helps isolate them.

## Verify changes locally

```bash
python -m pip install -r requirements.txt
node --test tests/test_export.mjs
python -X utf8 -m unittest discover -s tests -p "test_*.py"
```

GitHub Actions runs structural and script tests with Node.js 22 and Python 3.12 on Windows, macOS and Linux, plus a Linux LibreOffice/Poppler rendering job. It does not run Microsoft PowerPoint. Changes affecting appearance also need visual review; backend changes should be tested with the relevant installed renderer.

```bash
python -X utf8 scripts/build_figure.py --scene examples/diagram.scene.json --output build/figure.pptx
```

See [platform rendering](references/rendering.md) for backend setup and optional edit probes. Tests and edit probes are maintenance checks, not steps to repeat on every user's reconstructed image. Documentation-only changes need working relative links, images, anchors, and accurate command examples.

## Submit a change

- Explain the concrete problem, resulting behavior, and validation performed.
- Preserve native editability. Do not substitute full-slide images or invisible text for reconstruction.
- Record uncertain recognition instead of inventing source content.
- Distinguish a successful example from a general accuracy benchmark.
- Preserve upstream attribution and licenses when updating vendored components.
- Keep absolute local paths, private materials, and temporary build files out of the repository.

## Add an example or demonstration

Use original material or a public source that permits redistribution. Include a clear source URL, pinned revision where possible, and the applicable license or permission. Do not use private research figures without explicit permission for publication.

In `examples/<case-name>/`, include the reference, generated PPTX, actual rendered preview, scene JSON, and brief notes. Describe font substitutions, raster regions, formula or connector limitations, and whether verification is structural or visual.

For UI demonstrations, record the real presentation application. Keep actual selection handles and edits visible, exclude private account information, and disclose trimming, captions, or other post-processing. Preserve a clean downloadable PPTX independently of temporary demonstration edits.
