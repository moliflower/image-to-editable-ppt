# Installation guide for agents

Use this guide when the user asks you to install or update **image-to-editable-ppt**.

Repository: https://github.com/moliflower/image-to-editable-ppt

## Install

1. **Locate the active client's skills directory.** Honor its existing configuration and installation scope. If the directory is unknown, consult that client's skill documentation. Ask the user only if the intended client cannot be determined.
2. **Clone the skill into that directory:**

   ```bash
   git clone https://github.com/moliflower/image-to-editable-ppt.git
   ```

   The final path must be `<skills-directory>/image-to-editable-ppt/SKILL.md`. If this repository is already installed there, follow the update steps below.
3. **Prepare dependencies.** Use an available Node.js 18+ runtime and Python 3.10+ environment. From the cloned directory, run:

   ```bash
   python -m pip install -r requirements.txt
   ```

   Use the same Python interpreter for future skill commands. Set up a missing runtime through the environment's normal package manager when permitted.
4. **Set up previews.** Reuse an available Microsoft PowerPoint renderer on Windows, or LibreOffice with Poppler on Windows, macOS or Linux. Follow [renderer setup](references/rendering.md) if one is missing. Report whether previews are ready.
5. **Check readiness and discovery.** Run these once from the installed skill directory, then use the client's supported skill reload/discovery mechanism:

   ```bash
   node scripts/export_pptx.mjs --help
   python scripts/build_figure.py --help
   ```

   Read [SKILL.md](SKILL.md) for the reconstruction workflow. Confirm the installed location and tell the user they can attach an image and ask to convert it to PPT.

## Update

Locate the existing installation. Preserve local changes and confirm its Git remote is this repository. From the skill directory, run:

```bash
git pull
```

If dependency declarations changed, update them with the same Python environment. Reload the skill using the client's supported mechanism and confirm the new revision. If local edits prevent the update, preserve them and explain the conflict before proceeding.

If the existing folder is not a Git checkout, preserve its local changes and migrate it to a Git installation so future updates use `git pull`.
