# Source and adaptation

- Project: https://github.com/qwdwqfwq/topconf-paper-figure-gallery
- Base revision: dbf360a533ee46bc7d4a8f6037717c83f21a633a (2026-10-21).
- Geometry backport reference: [1e2e6283c48d005fbbaae81bc21b0eb6405b9e58](https://github.com/qwdwqfwq/topconf-paper-figure-gallery/blob/1e2e6283c48d005fbbaae81bc21b0eb6405b9e58/forge/editable-native.mjs) (2026-11-04).
- Bundled files: forge/editable-native.mjs, forge/pptx-template.json, and the project's MIT LICENSE under vendor/figureforge. The template retains the base version; the exporter has the selective local adaptations below.
- Source documentation: https://github.com/qwdwqfwq/topconf-paper-figure-gallery/blob/dbf360a533ee46bc7d4a8f6037717c83f21a633a/forge/EDITABLE_EXPORT.md

The wrapper replaces browser fetch for the static template with a local-file reader and provides a deterministic ZIP writer. A package adapter supplies meaningful object names, explicit East Asian/complex-script fonts, a plain white background, and removes stale template notes, thumbnail, and document metadata. The independent audit examines emitted OOXML and image pixels.

## Selective local capability adaptations

- Backported native start arrowheads, custom dash lengths, all-primitive rotation, and the control-point geometry frame from the referenced exporter. Dash inputs are normalized and validated by our local wrapper before serialization.
- Kept explicit text size and line breaks. Did **not** import `editable-text-layout.mjs`, browser Canvas measurement, automatic font fitting, web UI, retrieval, relay, analytics, or the upstream single-request/no-validation workflow.
- Added rotation-aware bounds and independent checks for emitted rotations, arrow ends and dash spacing.
- Implemented local source-asset manifests and crop-pixel checks using Python/Pillow, inspired by upstream `resourceManifest` and `resourceDefects` in [bitmap-evidence.mjs](https://github.com/qwdwqfwq/topconf-paper-figure-gallery/blob/1e2e6283c48d005fbbaae81bc21b0eb6405b9e58/forge/bitmap-evidence.mjs). This is a separate local implementation; the upstream browser recognition and repair module is not bundled.
- Preserved compatibility with existing scenes. Source provenance is optional for legacy images; audits explicitly report images lacking it. Newly prepared crops retain provenance automatically.

Export reports keep both `upstreamRevision` and `geometryBackportRevision`. A backport reference does not claim that the entire upstream release has been adopted. All vendored copyright/license notices remain intact.

Further original local extensions add rich text runs, explicit scientific baseline shifts, gradient-stop alpha, and independent text/gradient audits. The helper `editable-rich-text.mjs` is local code, not part of the pinned FigureForge source. See the [related-project implementation review](related-projects.md) for inspected sources, reuse boundaries, and design decisions.

The current assistant reconstructs the user image into a pixel-coordinate scene. The website's vision-provider requests, retrieval gallery, UI, and API refinement pipeline are not bundled. This is an assistant-operated skill, not a standalone automatic OCR executable. These scripts send no user images to an additional vision service.

Recognition accuracy depends on the source and reconstruction. Structural tests do not establish pixel-perfect fidelity. The upstream example's manually calibrated quality is not a guarantee for other images.

Updating upstream is maintenance work: review changes, retain license attribution, and rerun export and native-render verification before changing the revision.
