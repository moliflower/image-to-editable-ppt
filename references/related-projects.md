# Related implementation review

Reviewed on 2026-11-06. These are code-level comparisons of selected modules, not benchmark rankings or claims that an entire project was audited. Links pin the reviewed revisions.

| Project / inspected implementation | Useful observation | Decision for this skill |
| --- | --- | --- |
| [PPT Master: text property contract](https://github.com/hugohe3/ppt-master/blob/f3633771fe699d327f02ae86393831bbcf5169f7/skills/ppt-master/scripts/svg_to_pptx/drawingml/text_properties.py) and [gradient payload validation](https://github.com/hugohe3/ppt-master/blob/f3633771fe699d327f02ae86393831bbcf5169f7/skills/ppt-master/scripts/pptx_gradients.py) | A bounded text-property grammar prevents silent style loss; baseline shifts map to native DrawingML. Imported gradients have explicit integrity checks. | Implement a small local JSON run contract, native superscripts/subscripts, and independent text/gradient audits. Our gradient inputs are scene data, so we do not need its SVG payload transport. |
| [DeckWeaver / GuopengLin Image2PPT: color runs](https://github.com/GuopengLin/Image2PPT/blob/eeb8ef23bf2e07d59250041812831165080cb0cc/scripts/page/layout/text_runs.py) and [package inspection](https://github.com/GuopengLin/Image2PPT/blob/eeb8ef23bf2e07d59250041812831165080cb0cc/scripts/verify/inspect_pptx.py) | Per-word/per-character color segments retain emphasis within OCR lines; package checks catch missing slides/media. | Support agent-authored run boundaries in one text box and strengthen our independent audit. No OCR model, pixel color-segmentation code, inpainting or font-calibration code is imported. |
| [benouinirachid/svg2pptx: text writer](https://github.com/benouinirachid/svg2pptx/blob/258534f43a2a38fd2c9f7827811237439d33a0fc/src/svg2pptx/pptx_writer/text.py) and [freeform writer](https://github.com/benouinirachid/svg2pptx/blob/258534f43a2a38fd2c9f7827811237439d33a0fc/src/svg2pptx/pptx_writer/freeform.py) | Text uses zero insets/no wrap; its freeform writer builds line segments from parsed points. | Keep our explicit source-coordinate boxes and native cubic Bézier geometry. Character-count width estimates are not an improvement over measured source boxes for scientific reconstruction. |
| [guohuan-xie/image2PPT: PPTX writer](https://github.com/guohuan-xie/image2PPT/blob/1847650afe8022b68429fe066982c81003078b3f/src/image2pptx/pptx_writer.py) and [vectorization](https://github.com/guohuan-xie/image2PPT/blob/1847650afe8022b68429fe066982c81003078b3f/src/image2pptx/vectorize.py) | Separates primitive/freeform/image assets and uses source-image coordinates. Residual image assets and heuristic font fitting improve some conversion workflows. | Keep explicit asset-purpose/provenance and editable primitive boundaries. Retain declared type sizes and photo-only crop policy; automatic residual bitmaps and font shrinking do not fit this skill's reconstruction contract. |

## Local implementation and scope

- `scripts/scene_text.mjs` validates text/run declarations before normalization; unknown run fields cannot disappear silently.
- `vendor/figureforge/editable-rich-text.mjs` is original local code that emits multiple native text runs inside the same shape. It is not a downloaded upstream file. Existing plain text uses the existing serialization route.
- The existing FigureForge linear-gradient exporter now retains optional per-stop alpha; validation rejects unsupported gradient semantics.
- `scripts/audit_styles.py` independently reads emitted OOXML to check styles and gradients. Corruption tests alter the saved package, including fonts, baseline offsets, colors, positions and opacity.
- Actual desktop PowerPoint rendering remains the visual check. No browser Canvas, OCR model download, new API service, or automatic font fitting was added.

## Attribution and reuse

The above projects were read for design comparison; no source code from them is bundled in this change. PPT Master has an [MIT license](https://github.com/hugohe3/ppt-master/blob/f3633771fe699d327f02ae86393831bbcf5169f7/LICENSE). DeckWeaver uses a [personal/non-commercial license](https://github.com/GuopengLin/Image2PPT/blob/eeb8ef23bf2e07d59250041812831165080cb0cc/LICENSE), so its code was not incorporated. No standalone license file was present in the inspected trees of the other two projects; their code was not incorporated either. Existing FigureForge attribution and retained license remain described in [UPSTREAM.md](UPSTREAM.md).

The shipped [scientific text fixture](../examples/scientific-text.scene.json) is an original demonstration of the added capability. It is not a reconstruction-quality benchmark and does not use a private paper figure.
