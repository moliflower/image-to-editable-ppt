# Rendering and platform support

The core exporter, crop preparation and independent audit run with Node.js 18+ and Python 3.10+/Pillow on Windows, macOS and Linux. PowerPoint, PowerShell and LibreOffice are not required to create or audit a PPTX.

| Platform | Automatic preview backend | Optional dependency |
| --- | --- | --- |
| Windows | Registered desktop PowerPoint first, then LibreOffice | PowerPoint and Windows PowerShell, or LibreOffice plus Poppler |
| macOS | LibreOffice | LibreOffice plus Poppler (`pdftoppm`) |
| Linux | LibreOffice | LibreOffice Impress plus Poppler (`pdftoppm`) |

PowerPoint for macOS can open/edit the resulting file, but this project does not automate its UI or AppleScript interface. A LibreOffice preview is identified as such and is not claimed to be a Microsoft PowerPoint render. Fonts and renderer differences may change text metrics.

## Unified build

```text
python -X utf8 scripts/build_figure.py --scene build/scene.json --source reference.png --output build/figure.pptx
```

Crop preparation is conditional. Export and the independent audit run once; unchanged PPTX rendering can be reused. For a scene without source crops, omit `--source`. Detailed diagnostics are in `figure.audit.json`, `figure.build.json`, and `figure.render.json`. Terminal output stays short and includes timings, object counts and renderer status.

Select `--renderer auto` (default), `powerpoint`, `libreoffice`, or `none`. `none` explicitly requests export/audit only. `auto` may finish with `unavailable` when there is no renderer; it never labels that as visually verified. An explicit unavailable backend, failed render or failed audit returns a failing CLI exit status. Inspect `render.status`, not merely the presence of an old PNG.

## Install a LibreOffice renderer

Install [LibreOffice](https://www.libreoffice.org/download/) and [Poppler](https://poppler.freedesktop.org/) using your platform's normal installer/package manager. No model downloads or extra Python libraries are needed.

Typical macOS/Homebrew setup:

```sh
brew install --cask libreoffice
brew install poppler
```

Typical Debian/Ubuntu setup:

```sh
sudo apt-get install libreoffice-impress poppler-utils
```

The adapter searches `PATH`, the normal LibreOffice macOS app location, and standard Windows Program Files locations. For custom installations, set `SOFFICE_PATH` and `PDFTOPPM_PATH` to executable file paths using your shell's normal environment-variable syntax. No shell command is assembled from document names.

LibreOffice runs headlessly with a fresh temporary user profile and exports PDF using `impress_pdf_Export`; Poppler renders its single page to PNG. Temporary output avoids accepting a stale PDF after a failed conversion. The original PPTX is never converted in place. See the official [startup parameters](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html) and [PDF export parameters](https://help.libreoffice.org/latest/en-US/text/shared/guide/pdf_params.html).

## Preview an existing PPTX

```text
python -X utf8 scripts/render_pptx.py --pptx build/figure.pptx --output build/figure.png --renderer auto --width 1600
```

Cache matching checks the PPTX SHA-256, output PNG SHA-256, requested dimensions, adapter code and renderer executable identities. Changing fonts or Office components that are not represented by the executable fingerprint requires `--force` here, or `--force-render` in the build command. Rendering success means a preview was produced, not that an agent inspected it.

## Optional Windows maintenance checks

The existing native PowerPoint script remains an optional backend. It opens only the target document without a presentation window, closes that document, and keeps PowerPoint running if other decks are open. The unified renderer requests a compact count report, not a full object enumeration.

Only use an edit probe when validating a new exporter/backend or investigating editability:

```powershell
powershell -NoProfile -File scripts/render_powerpoint.ps1 -InputPptx build/figure.pptx -OutputPng build/figure.png -EditProbePath build/edited-probe.pptx
```

It changes text, moves a shape and recolors an arrow in a separate copy. It is not required for every reconstructed image. Follow your environment's script-execution policy; the portable wrapper does not change it.
