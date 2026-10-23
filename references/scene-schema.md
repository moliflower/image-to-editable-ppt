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
| text | x,y,w,h,text,fontSize | fontFamily, bold, italic, anchor: start/middle/end, verticalAlign: top/middle, rotation |
| rect | x,y,w,h | radius, fill, stroke, strokeWidth, dash |
| ellipse | x,y,w,h | fill, stroke, strokeWidth |
| line | x,y,x2,y2 | stroke, strokeWidth, arrow, dash |
| polyline | points: "x,y x,y ..." | closed, fill, stroke, strokeWidth, arrow, dash |
| path | d with SVG M/L/H/V/C/S/Q/T/A/Z commands | fill, stroke, strokeWidth, arrow, dash |
| image | x,y,w,h,assetPurpose plus href, file, or crop | assetPurpose: photo/texture/logo/complex-artwork; assetDescription |

Colors accept #RGB, #RRGGBB, or "none". Geometry defaults to no fill/stroke; set visible colors explicitly. Default text is black. Text needs a box about fontSize * 1.3 high per line; inspect actual font metrics in native rendering. Wrapping is disabled; preserve explicit newline breaks. Text coordinates denote the layout box top-left, not the baseline.

Use Times New Roman by default for English scientific labels, numerals, and mathematical text. An explicit user, journal, template, or source-typography requirement overrides this default. Set fontFamily explicitly. Microsoft YaHei is a reasonable Windows fallback for Chinese; use a symbol fallback only when required by missing glyphs. Keep small scientific labels faithful rather than applying presentation-wide font-size defaults, and recheck text widths after a font change.

Array order is draw order. For a cube, use a separate closed polygon for each visible face. Table cells reconstructed this way are shapes, not a native data table.

## Image crops

~~~json
{"id":"sample-photo","type":"image","x":100,"y":100,"w":180,"h":120,
 "crop":{"x":100,"y":100,"w":180,"h":120},
 "assetPurpose":"photo","assetDescription":"Microscopy sample"}
~~~

Crop coordinates refer to the source independently of placement. Run image_assets.py prepare first; it checks canvas dimensions and crop bounds and embeds lossless PNG. Alternatively file resolves relative to the scene and embeds a local PNG/JPEG. href accepts only embedded PNG/JPEG data, never remote URLs. Convert GIF/WebP through the image helper. Image objects covering over 55% of the canvas are rejected. Smaller crops still need visual review so they do not conceal diagram content.

## Uncertainty and unsupported features

Use reviewNotes for unreadable labels or unresolved measurements. Do not guess technical terms. Only use a visibly marked placeholder when unavoidable and disclose it.

Generic opacity, HTML/CSS text, embedded SVG pictures, automatic connector binding, native charts, and native equations are unsupported. Basic gradients use gradient: {angle, stops:[{offset:0,color:"#FFFFFF"},{offset:1,color:"#AACCEE"}]}.

Export produces figure.exported.scene.json with normalized nodes and figure.editability.json. Audit against the normalized scene so object expansion and image embedding are counted correctly.
