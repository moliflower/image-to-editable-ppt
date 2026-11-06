---
name: image-to-editable-ppt
description: Convert a supplied diagram, screenshot, or scientific figure into a PowerPoint .pptx with individually editable text boxes, shapes, and arrows. Use for 图片转可编辑PPT, 在PPT里重画这张图, image-to-PPT reconstruction, and FigureForge-based editable export. Preserve the reference layout. This is for reconstructing an existing figure, not general slide-deck creation or photo editing.
---

# Image to editable PowerPoint

Reconstruct the supplied figure as one editable PPTX slide in its original aspect ratio. The current assistant understands the image; the bundled local exporter needs no separate vision API or key. Export and audit use Node.js 18+ and Python 3.10+/Pillow on Windows, macOS and Linux. The rendering backend is optional and selected separately; PowerShell is not a core dependency.

## Default workflow

1. **Inspect once, resolve details early.** View the actual supplied image and obtain its EXIF-oriented dimensions (`python scripts/image_assets.py inspect reference.png`) if not already known. Identify text, modules, arrow directions, layering and photo regions. Batch detail crops for uncertain symbols or dense areas before authoring; avoid reopening unchanged full images. Preserve the original. For PNG-only requests, use only that bitmap, not neighboring SVG/PDF/draw.io/source files, and record this boundary in `reviewNotes`.
2. **Build the scene.** Use source-pixel coordinates, stable meaningful IDs and back-to-front node order. Read [scene-schema.md](references/scene-schema.md) when the schema is unfamiliar or a needed field is unclear; reuse known conventions on subsequent figures. Keep ordinary labels in one native text box, using `runs` for mixed styles and indices. Use native shapes/paths for diagrams, charts and arrows. Only photos/complex artwork may remain image regions. Declare their crop inventory in `sourceAssets` when multiple regions must be accounted for. Record recognition uncertainty rather than guessing.
3. **Build and check in one call.** Run the unified command below. It prepares declared crops only when needed, exports once, independently audits once, then renders the actual PPTX with an available backend. Keep generated files in the task directory. Inspect the short result; consult detailed sidecars only for warnings or failures.

   ```text
   python -X utf8 "<skill>/scripts/build_figure.py" --scene "<build>/scene.json" --source "<reference.png>" --output "<output>/figure.pptx"
   ```

   `--source` is required for crop preparation and useful for independent provenance checks; omit it for a scene with no source crops. `--renderer auto` prefers installed PowerPoint on Windows, otherwise LibreOffice with Poppler on any supported OS. See [rendering.md](references/rendering.md) only for setup, troubleshooting or explicit backend selection. Discover bundled runtime paths only when existing Python/Node paths are missing.
4. **Review and deliver.** Inspect the rendered preview against the reference, including unresolved small labels. Check wording, topology, clipping, overlaps, font metrics and photos. Correct detected defects in the scene and rebuild once per coherent set of changes; review changed areas plus overall layout. Deliver PPTX and preview, retaining scene JSON for revisions. Disclose unresolved recognition and regions that remain images. If no renderer exists, deliver the editable file and state that visual verification is incomplete. A scene preview is not a render of the PPTX.

## Quality without redundant work

- Keep one independent package audit and one visual review for each changed final PPTX. Passing structural checks does not establish visual fidelity.
- Reuse a preview only when the renderer's cache confirms matching PPTX bytes, width, backend and preview hash. Font/environment changes require `--force-render`. Cached rendering still needs visual review; the script never marks that review complete.
- Do not run edit probes, repository-wide tests, example regressions, repeated installation checks or both Office renderers for every user figure. Those are toolchain maintenance checks, needed after exporter/backend changes or a specific suspected failure. Ordinary reconstruction uses the existing tested toolchain.
- Do not reread the complete skill, generic slide-design guidance or already-understood schema on every correction. A supplied scientific figure determines composition, text size and slide count.
- For revisions, change the retained scene; if the user edited the PPTX, inspect that file before regenerating from an older scene. Do not overwrite the user's edits from stale scene data.

## Typography and editability

- English scientific labels, numerals and math default to Times New Roman; explicit user/journal/template/source-font instructions override it. Set `fontFamily` explicitly. Use installed fallbacks for missing glyphs/fonts and disclose material substitutions. Use upright operators/units, italic variables, and the reference's emphasis. Do not assume Windows fonts exist on Linux or macOS.
- Preserve explicit sizes and line breaks; no browser Canvas measurement or automatic font fitting. `runs` retain one editable box; `baselineShift: "super" / "sub"` keeps native text indices with explicit sizes. They are not native equation objects.
- Keep text, modules and arrows individually editable. Never insert the whole reference as a background, overlay invisible text or flatten diagram content into image crops. Reconstructed chart shapes do not recover source data.
- Paths are native editable geometry but are not automatically attached to modules. Preserve arrow direction and topology. Geometry, rich text, gradients, dashes, rotation and image provenance are specified in the [schema](references/scene-schema.md); the audit checks their supported OOXML declarations.
- A complete photo inventory and correct layering remain the assistant's responsibility. Source-pixel checks cannot prove that an undeclared photo was recognized or that another object does not cover it.

The bundled exporter and adaptation provenance are documented in [UPSTREAM.md](references/UPSTREAM.md).
