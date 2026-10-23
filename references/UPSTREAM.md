# Source and adaptation

- Project: https://github.com/qwdwqfwq/topconf-paper-figure-gallery
- Revision: dbf360a533ee46bc7d4a8f6037717c83f21a633a (2026-10-21).
- Bundled files: forge/editable-native.mjs, forge/pptx-template.json, and the project's MIT LICENSE under vendor/figureforge. Exporter and template are unchanged apart from possible line-ending normalization.
- Source documentation: https://github.com/qwdwqfwq/topconf-paper-figure-gallery/blob/dbf360a533ee46bc7d4a8f6037717c83f21a633a/forge/EDITABLE_EXPORT.md

The wrapper replaces browser fetch for the static template with a local-file reader and provides a deterministic ZIP writer. A package adapter supplies meaningful object names, explicit East Asian/complex-script fonts, a plain white background, and removes stale template notes, thumbnail, and document metadata. It does not modify the vendored exporter. The independent audit examines the emitted OOXML.

The current assistant reconstructs the user image into a pixel-coordinate scene. The website's vision-provider requests, retrieval gallery, UI, and API refinement pipeline are not bundled. This is an assistant-operated skill, not a standalone automatic OCR executable. These scripts send no user images to an additional vision service.

Recognition accuracy depends on the source and reconstruction. Structural tests do not establish pixel-perfect fidelity. The upstream example's manually calibrated quality is not a guarantee for other images.

Updating upstream is maintenance work: review changes, retain license attribution, and rerun export and native-render verification before changing the revision.
