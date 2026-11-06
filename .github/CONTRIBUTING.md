# Contributing

The repository root is an installable skill. Keep its runtime self-contained and small. README showcase media is linked to a fixed published revision; do not add demonstration PPTX files, paper reference images, generated scenes or reports to the install tree.

## Validation

```text
python -m pip install -r requirements.txt
node --test tests/test_export.mjs
python -X utf8 -m unittest discover -s tests -p "test_*.py"
```

Tests use small original fixtures in `tests/fixtures/`, including a synthetic image. They do not require downloads of research figures. CI tests Windows, macOS and Linux and performs an actual LibreOffice/Poppler rendering check on Linux. Appearance changes also require review of a PPTX-rendered PNG with a relevant renderer. Routine user figures do not need repository tests or UI demonstrations.

The distribution test archives the committed tree with `git archive HEAD`, extracts it to an isolated directory, and runs export/audit there. Run it after committing packaging changes; it verifies the tree that a source ZIP will contain. `.gitattributes` excludes this directory and `tests/` from source ZIPs. Keep the required agent reference guides and all vendor license notices in the package.

## Changes and reports

Describe the concrete issue, expected behavior, environment and validation. Preserve native editability, explicit text sizes and source-pixel provenance. Keep private figures, machine-specific paths and generated output out of version control. Test inputs must be small and either original or licensed for redistribution.

Preserve the source revision and licensing of vendored code in `vendor/figureforge/UPSTREAM.md`. Record substantive adaptations there. Large demonstrations and research notes belong outside the install tree; keep their sources and rights notices with the separately hosted showcase.
