---
name: image-to-editable-ppt
description: Convert a supplied diagram, screenshot, or scientific figure into a PowerPoint .pptx with individually editable text boxes, shapes, and arrows. Use for 图片转可编辑PPT, 在PPT里重画这张图, image-to-PPT reconstruction, and FigureForge-based editable export. Preserve the reference layout. This is for reconstructing an existing figure, not general slide-deck creation or photo editing.
---

# Image to editable PowerPoint

Reconstruct the supplied figure as a one-slide PPTX in its original aspect ratio. Each label, module, and arrow must be independently selectable. Use the bundled FigureForge native DrawingML exporter, pinned in [UPSTREAM.md](references/UPSTREAM.md). The assistant performs image understanding in the current conversation; no separate vision API or API key is required.

## Typography and input boundaries

- Use **Times New Roman** by default for English labels, titles, numerals, and mathematical text in reconstructed scientific figures. This is this skill's default convention, not a universal journal requirement. Explicit user, journal, or template font requirements override it; an explicit request to preserve the source typography also overrides it. Preserve the reference layout and relative type sizes when changing the font, and recheck spacing after native rendering.
- Set fontFamily explicitly on text nodes. Use italic mathematical variables, upright operators and units, and the reference's bold emphasis. Use an installed fallback only for glyphs Times New Roman cannot display (for example Chinese or special symbols); disclose a material substitution.
- When the user requests a **PNG-only / image-only** conversion, use only the supplied bitmap for recognition and measurement. Do not inspect neighboring draw.io, SVG, PDF, slide, code, or prior reconstructed scene files for the figure. Record the input boundary in scene.reviewNotes. If source-assisted reconstruction is permitted and used, say so rather than presenting it as a bitmap-only test.

## Workflow

1. **Inspect the reference.** Obtain the actual local image, inspect it with the available image viewer, and read its dimensions with scripts/image_assets.py inspect. If an attachment has no accessible file, obtain it through the available file tools; ask for the file only when necessary. Preserve the original source.
2. **Inventory and measure.** Identify labels, containers, shapes, arrow endpoints, routing, layers, and photographic regions. Use source-image pixel coordinates. Zoom into dense regions with image_assets.py crop; keep crop offsets when mapping measurements to the full image. Preserve wording, capitalization, symbols, line breaks, colors, and layout. Record uncertain text or missing details in scene.reviewNotes; do not invent them.
3. **Create a scene.** Read [scene-schema.md](references/scene-schema.md), then write a JSON scene in the task's private build directory. Every object needs a stable, meaningful ID. Each label must be a text node and each independently editable module/arrow a separate node. Array order is back-to-front. Photos and complex artwork may use declared image crops; diagram modules, labels, and arrows must not be flattened into those crops.
4. **Materialize crops when needed.** Use image_assets.py prepare with --scene, --source, and --output to embed declared photographic/artwork crops. It also handles EXIF orientation. All scene coordinates refer to the EXIF-oriented image. Keep the source canvas size unchanged.
5. **Export and audit.** Run the bundled exporter, followed by the independent package audit. The exporter is local, has no npm dependencies, and makes no network requests. Use Node 18+ and Python 3 with Pillow; use load_workspace_dependencies if runtime paths are missing.

   ~~~powershell
   node "<skill>/scripts/export_pptx.mjs" --scene "<build>/scene.json" --output "<output>/figure.pptx"
   python "<skill>/scripts/audit_pptx.py" --pptx "<output>/figure.pptx" --scene "<output>/figure.exported.scene.json" --report "<build>/audit.json"
   ~~~

6. **Render and compare.** On Windows with PowerPoint, run the bundled renderer. It opens only the generated file without a presentation window and does not quit PowerPoint if an existing presentation remains open. Inspect the actual PNG alongside the reference, including small-label close-ups. Check wording, objects, arrow directions, overlaps, clipping, type sizes, and crop boundaries. Correct the scene and rerun export/audit/render until detected defects are resolved.

   ~~~powershell
   powershell -NoProfile -File "<skill>/scripts/render_powerpoint.ps1" -InputPptx "<output>/figure.pptx" -OutputPng "<build>/figure.png" -Width 1600
   ~~~

   If PowerPoint is unavailable, use an available PPTX renderer such as LibreOffice or presentation tools. A scene preview does not verify PowerPoint rendering. If no renderer is usable, deliver the editable file with a note that visual verification remains incomplete. Failed fidelity checks require correction or disclosure, not a bitmap-only replacement.
7. **Deliver.** Return the PPTX and a preview. State material recognition uncertainties and any regions that remain images. Keep build/audit files private unless useful or requested. Retain the scene JSON beside the output for revisions; do not require the user to edit JSON.

## Editability contract

- Text is native PowerPoint text, not outlines or image patches. Use separate text nodes for mixed formatting where necessary. Ordinary labels remain whole text boxes.
- Rectangles, ellipses, polygons, lines, and curves are native DrawingML shapes. A connector drawn as a path is editable but is not automatically attached to adjacent modules. Do not promise automatic rerouting.
- Each arrow is a separate line/path node with its own arrowhead. Preserve direction and branch topology.
- Use explicit fill/stroke colors or "none". Complex image regions require assetPurpose and are reported in the audit.
- Do not insert the whole reference as a slide background, overlay invisible text, or silently replace hard-to-rebuild modules with image crops.
- Reconstructing a chart as shapes does not recover its data. Mathematical symbols in text boxes are not native PowerPoint equations. Explain these distinctions when relevant.
- Match the reference's layout instead of applying generic slide templates, cover pages, or minimum deck font-size rules.

For revisions, change the retained scene, regenerate, and compare again. If the user edited the PPTX, inspect that file before regenerating from an older scene.
