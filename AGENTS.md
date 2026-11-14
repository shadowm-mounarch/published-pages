# Publishing rules

This is Mahmoud Sharif Ata's approved repository for polished, cloud-hosted HTML research and reference pages. Publish here when useful without requiring a separate upload request. ChatGPT Pages, Spaces, and related cloud storage still require an explicit request.

- Content lives in `content/`, with entries in `catalog.json`. Keep source wording and citations intact when migrating documents.
- Build with `python build.py`, then run `python verify.py` locally. Install dependencies from `requirements.txt` if needed.
- Generated public files live in `docs/`; publish `main:/docs` through GitHub Pages.
- Keep `docs/.nojekyll` and repository-level GitHub Actions disabled. Never add or trigger cloud CI. Verify the setting before every push.
- Do not publish secrets, credentials, or unrelated local files. Only stage this repository's intended publishing files.
- Preserve readable typography, accessible contrast, mobile layout, print styles, local search, and document navigation. No trackers or external runtime dependencies.
- Use Mahmoud's name in public-facing content.
