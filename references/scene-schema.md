# Scene schema

Coordinates and font sizes are pixels in the EXIF-oriented image. Slide width is 10 inches; height follows the source aspect ratio. Font points = fontSize * 720 / canvas.width.

~~~json
{
  "canvas": {"width": 1200, "height": 600},
  "reviewNotes": [],
  "nodes": [
    {"id":"module-a","type":"rect","x":80,"y":180,"w":260,"h":160,"radius":16,"fill":"#E5EFFA","stroke":"#315C88","strokeWidth":2},
    {"id":"module-b","type":"rect","x":600,"y":180,"w":260,"h":160,"fill":"#E3F2E7","stroke":"#34764A","strokeWidth":2},
    {"id":"a-to-b","type":"line","x":340,"y":260,"x2":600,"y2":260,"stroke":"#334155","strokeWidth":3,"arrow":true},
    {"id":"a-label","type":"text","x":100,"y":235,"w":220,"h":50,"text":"输入 Input","fontSize":32,"fontFamily":"Microsoft YaHei","anchor":"middle","fill":"#142536"},
    {"id":"b-label","type":"text","x":620,"y":235,"w":220,"h":50,"text":"输出 Output","fontSize":32,"fontFamily":"Microsoft YaHei","anchor":"middle","fill":"#142536"}
  ]
}
~~~

All nodes require unique string IDs. Use optional name for a human-readable selection-pane name. Numbers must be finite.

| Type | Required geometry | Useful properties |
|---|---|---|
| text | x,y,w,h,text,fontSize | fontFamily, bold, italic, underline, runs, baselineShift, lineSpacing, anchor: start/middle/end, verticalAlign: top/middle, rotation |
| rect | x,y,w,h | radius, fill, stroke, strokeWidth, dash, rotation |
| ellipse | x,y,w,h | fill, stroke, strokeWidth, dash, rotation |
| line | x,y,x2,y2 | stroke, strokeWidth, arrow, arrowStart, dash, rotation |
| polyline | points: "x,y x,y ..." | closed, fill, stroke, strokeWidth, arrow, arrowStart, dash, rotation |
| path | d with SVG M/L/H/V/C/S/Q/T/A/Z commands | fill, stroke, strokeWidth, arrow, arrowStart, dash, rotation |
| image | x,y,w,h,assetPurpose plus href, file, or crop | assetPurpose: photo/texture/logo/complex-artwork; assetDescription, rotation, sourceAssetId |

Colors accept #RGB, #RRGGBB, or "none". Geometry defaults to no fill/stroke; set visible colors explicitly. Default text is black. Text needs a box about fontSize * 1.3 high per line; inspect actual font metrics in native rendering. Wrapping is disabled; preserve explicit newline breaks. Text coordinates denote the layout box top-left, not the baseline.

Use Times New Roman by default for English scientific labels, numerals, and mathematical text. An explicit user, journal, template, or source-typography requirement overrides this default. Set fontFamily explicitly. Microsoft YaHei is a reasonable Windows fallback for Chinese; use a symbol fallback only when required by missing glyphs. Keep small scientific labels faithful rather than applying presentation-wide font-size defaults, and recheck text widths after a font change.

Array order is draw order. For a cube, use a separate closed polygon for each visible face. Table cells reconstructed this way are shapes, not a native data table.

## Scientific text within one editable box

Use `runs` to preserve mixed formatting without splitting a label into independently positioned boxes:

~~~json
{"id":"loss-label","type":"text","x":80,"y":80,"w":320,"h":65,
 "text":"Lcls + λLbox","fontSize":36,"fontFamily":"Times New Roman","fill":"#172F49",
 "runs":[
   {"text":"L","italic":true},
   {"text":"cls","fontSize":23,"baselineShift":"sub"},
   {"text":" + "},
   {"text":"λL","italic":true,"fill":"#286C62"},
   {"text":"box","fontSize":23,"baselineShift":"sub","fill":"#286C62"}
 ]}
~~~

Run `text` values must concatenate exactly to the box's `text`, including spaces and line breaks; CRLF/CR normalize to LF. Each run inherits the box's `fontFamily`, `fontSize`, `fill`, `bold`, `italic`, `underline`, and `baselineShift`. Explicit `false` overrides inherited emphasis. These are the only supported run properties; misspellings fail validation. `runs` must be a nonempty array and cannot be combined with `textPath`.

`baselineShift` accepts `none`, `super`, or `sub`, mapped to native baseline offsets of 0%, +30%, and -25%. It does not change the declared font size: set index size explicitly. Font sizes must map to 1–4000 PowerPoint points; export rejects values that would otherwise be clamped. This supports scientific indices, not native equation structures such as editable fractions or matrices.

`lineSpacing` optionally sets the baseline-to-baseline distance in source pixels. Without it, multiline text uses 1.14 times the largest font size on each line (at least the box's base size). Empty lines, explicit spaces and Unicode survive export. Wrapping and automatic fitting remain disabled. Review superscript clearance, descenders and mixed font metrics in the real renderer.

The independent audit checks run contents, font names in Latin/East Asian/complex-script slots, sizes, colors, emphasis, baseline offsets, alignment and line spacing. It checks OOXML declarations, not installed-font availability or visual fit.

## Native linear gradients

`gradient` applies to rectangles, ellipses, paths and polylines, with `angle` in clockwise degrees and at least two `stops`. Stops must be in nondecreasing `offset` order from 0 to 1; equal positions allow hard transitions. Colors are visible hex colors. Optional stop `opacity` is 0–1, defaults to 1, and blends with underlying objects. Example:

~~~json
"gradient": {"angle":0,"stops":[
  {"offset":0,"color":"#315C88","opacity":1},
  {"offset":1,"color":"#428B7D","opacity":0.05}
]}
~~~

These are native linear shape fills, rotated with the shape. Text/image gradients, radial gradients, and unrecognized gradient properties are rejected. Open paths do not gain an enclosed fill automatically. The audit verifies native gradient presence, angle, stop order/positions/colors/opacity. Generic object opacity is still unsupported.

## Native arrows, dashes and rotation

`arrow: true` places a triangular arrowhead at the path end. `arrowStart: true` places one at the start; both may be true. These fields apply to line, polyline and path nodes, and require a visible stroke.

`dash: true` keeps the standard dashed line. A numeric array such as `[12, 6]` specifies source-pixel lengths for alternating painted strokes and gaps. Odd patterns repeat, so `[3, 2, 1]` becomes `[3, 2, 1, 3, 2, 1]`. Nonnegative values are accepted if at least one is positive. A string such as `"12 6"`, or the aliases `dashed` / `strokeDasharray`, is normalized to `dash` during export. Specify only one dash field. Dash patterns apply to geometric objects with visible strokes, including closed borders and curved paths.

`rotation` is a finite clockwise angle in degrees on every supported object type. Coordinates describe the unrotated layout frame. Paths rotate about their exported control-point frame, and clipping warnings account for rotation. For text measured as a narrow vertical OCR box at 90/270 degrees, the existing normalization converts it to a horizontal layout frame; use `rotationBounds: "layout"` when the input already describes that frame.

Explicit font sizes, wording and line breaks remain unchanged. No Canvas text measurement, font fitting, or browser runtime is used.

## Image crops

~~~json
{"id":"sample-photo","type":"image","x":100,"y":100,"w":180,"h":120,
 "crop":{"x":100,"y":100,"w":180,"h":120},
 "assetPurpose":"photo","assetDescription":"Microscopy sample"}
~~~

Crop coordinates refer to the source independently of placement. Run image_assets.py prepare first; it checks canvas dimensions and crop bounds and embeds lossless PNG. Alternatively file resolves relative to the scene and embeds a local PNG/JPEG. href accepts only embedded PNG/JPEG data, never remote URLs. Convert GIF/WebP through the image helper. Image objects covering over 55% of the canvas are rejected. Smaller crops still need visual review so they do not conceal diagram content.

### Source-asset provenance

Source crop coordinates must be integers in the EXIF-oriented image. Preparation records `sourceAssetId`, `sourceCrop`, and `sourceCanvas` on each crop node and a top-level `sourceAssets` manifest. The default asset ID is the node ID. To catch omitted regions against an independently prepared inventory, declare the expected assets before preparation:

~~~json
"sourceAssets": [
  {"id":"sample-photo", "crop":{"x":100,"y":100,"w":180,"h":120}}
]
~~~

Preparation fills each entry's `canvas` and `pixelSha256`. The digest is SHA-256 of the ASCII header `WIDTHxHEIGHT:RGBA` followed by one NUL byte and the decoded RGBA pixel bytes. Let the helper compute it. Each manifest entry must bind exactly one image; unknown IDs, missing/duplicate bindings and inconsistent crop metadata fail validation. When no inventory is supplied, the manifest is derived from declared crop nodes and cannot detect photographs never declared.

Placement, scaling and rotation can change independently of the source crop. The PPTX audit compares every embedded image's decoded pixels with its scene image, even for legacy scenes without a manifest. With `--source reference.png`, it also re-crops the original and checks manifest pixel digests. Legacy images without provenance remain supported and are counted in `imagesWithoutSourceProvenance`. Layering and visual completeness still need an actual render review.

## Uncertainty and unsupported features

Use reviewNotes for unreadable labels or unresolved measurements. Do not guess technical terms. Only use a visibly marked placeholder when unavoidable and disclose it.

Generic object opacity, HTML/CSS text, embedded SVG pictures, automatic connector binding, native charts, and native equations are unsupported. Use the supported text-run and linear-gradient contracts above for those specific styles.

Export produces figure.exported.scene.json with normalized nodes and figure.editability.json. Audit against the normalized scene so object expansion and image embedding are counted correctly.
