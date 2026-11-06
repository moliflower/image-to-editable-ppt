# Reusable scientific components

Use `scripts/scientific_components.py` to author repeated structures instead of rewriting primitive helpers for each image. It produces the same inspectable scene JSON as handwritten scenes. All component children remain individually editable PowerPoint objects. It adds no dependencies, browser runtime, font fitting or image-generation step.

Add the installed skill's `scripts` directory to Python's import path, then:

```python
from scientific_components import Figure
f = Figure(1200, 700, font="Times New Roman")
boxes = f.chain("encoder", 80, 120, ["Input", "Encoder", "Output"],
                w=180, h=60, gap=50, fontSize=25, radius=10)
f.arrow("feedback", boxes[-1].port("bottom"), boxes[0].port("bottom"),
        via=[(630, 240), (170, 240)], stroke="#416B88")
f.text("loss", 80, 330, 400, fontSize=30, runs=[
    {"text": "L", "italic": True},
    {"text": "cls", "fontSize": 19, "baselineShift": "sub"},
    {"text": " + λL", "italic": True},
    {"text": "box", "fontSize": 19, "baselineShift": "sub"},
])
f.save("build/scene.json")
```

Run the normal `build_figure.py` command on the saved scene. Geometry/style fields follow the [existing schema](scene-schema.md). `text(..., runs=...)` derives the plain text automatically so authors do not duplicate it. Explicit frame height `h` is supported; the helper's default height is only a convenience, not a font-metrics or visual-fit guarantee.

| Component | Arguments after `id` | Behavior |
| --- | --- | --- |
| `rect`, `text`, `line`, `path`, `polygon`, `circle` | Source coordinates and ordinary style fields | Thin wrappers around native scene nodes |
| `block` | `x, y, w, h, label`; `fontSize`, `textStyle`, shape styles | Separate module shape and centered text; returns a `Box` with `port(left/right/top/bottom)` |
| `chain` | `x, y, labels, w, h`; `gap`, `vertical`, `arrowStyle`, block styles | Repeated equal-size blocks with explicit edge-to-edge arrows; returns boxes |
| `stack` | `x, y, w, h`; `layers`, `dx`, `dy`, `fill`, `stroke` | Back-to-front feature maps; returns the overall box |
| `matrix` | `x, y, rows, cols, cellW, cellH`; `colors`, `gap`, `stroke` | Independent cells; colors can be one color or a flat row-major list |
| `bars` | `x, baseline, heights`; `barW`, `gap`, fill/stroke | Heights are source pixels, never normalized; zero-height bars have no painted object |
| `scatter` | `points`; `r`, `fill`, `stroke` | Individual circles at the given source coordinates |
| `boxplot` | `x, top, q1, median, q3, bottom`; `w`, fill/stroke | Native whisker, caps, box and median; all y values are source pixels |
| `axes` | `origin, right, top` | Two native arrow axes |
| `arrow` | `start, end`; optional `via` points and line styles | A straight or explicitly routed native path, with no automatic rerouting |
| `cycle` | `cx, cy, r`; `stroke`, `strokeWidth` | Two circular arc arrows with gaps |
| `fraction` | `x, y, w, numerator, denominator`; `fontSize`, `gap`, text styles | Separate native text and a fraction rule; strings or rich run lists |
| `summation` | `x, y, w, upper, lower`; `fontSize`, `limitSize`, text styles | Native operator and limits; `y` is the operator frame top |
| `image_crop` | `x, y, w, h, crop`; `purpose`, `description` | Declares source inventory and image binding together; preparation retains pixel provenance |

Helper defaults are not a design template. Supply measured source sizes/colors; use ordinary nodes when a composite does not fit. Do not change a source diagram to fit the library. Formula components are native text, not Office equations. Generated chart geometry does not recover its original numerical data.

The [component gallery](../examples/components_demo.py) exercises these helpers:

```text
python examples/components_demo.py build/components.scene.json
python -X utf8 scripts/build_figure.py --scene build/components.scene.json --output build/components.pptx
```

## Whole-task timing

For a measured trial, start **before source selection/download or image inspection**, after any unrelated tool development:

```text
python scripts/figure_session.py start --session output/session.json --label "New figure trial"
python scripts/figure_session.py mark --session output/session.json --label "source-ready"
```

Record a few meaningful stages, not every command. After the actual preview has been inspected and the deliverable is ready:

```text
python scripts/figure_session.py finish --session output/session.json --build-report output/figure.build.json --review "Checked labels, formulas, topology, crops and layout against reference"
```

This records elapsed wall time separately from script timings and binds completion to the exact audited/rendered files. It does not itself inspect an image or prove visual quality. The timer cannot be reset by reusing a session path. If tool development and the figure trial happen in the same request, report their durations separately. Be explicit that the timer ends before rendering the final chat reply; do not call a seconds-long build the entire reconstruction time.

## Minimal delivery

Return one PPTX and one preview in a predictable task folder, with a short ASCII filename. Keep the source scene and detailed reports there for revisions; do not copy them to multiple locations or create ZIPs/cache demonstrations by default. Retain necessary attribution. A local path is not an uploaded download attachment.

When the user asks to open the result or cannot use a local-file link, request its associated desktop application with:

```text
python scripts/open_artifact.py output/figure.pptx
```

This uses native file opening on Windows/macOS/Linux without PowerShell or shell interpolation. It reports `open-requested`, not successful on-screen verification. If no desktop/file association is available, return the literal absolute path and preview; do not rebuild a valid PPTX to fix a link-handler problem.
