# The Reading Room

Research, reference notes, and working documents for Mahmoud Sharif Ata.

Public site: https://shadowm-mounarch.github.io/published-pages/

## Publish a document

1. Save Markdown in `content/<slug>.md`.
2. Add an entry to `catalog.json` with `slug`, `title`, `category`, `summary`, and an ISO `date`. The Markdown may begin with its own title; the renderer normalizes heading levels for the document page.
3. Run `python build.py` and `python verify.py` locally. Verification uses installed Microsoft Edge through Playwright.
4. Verify `gh api repos/shadowm-mounarch/published-pages/actions/permissions --jq .enabled` returns `false`.
5. Commit sources, assets, and generated `docs/` files; push `main`.
6. Check the published URLs and `gh api repos/shadowm-mounarch/published-pages/pages`.

GitHub Pages publishes `main:/docs`. `.nojekyll` bypasses server-side Jekyll builds, and GitHub Actions is disabled for this repository. No cloud CI workflows are used.

The site uses local CSS and JavaScript, system fonts, no analytics, and no third-party runtime services. All published content and source files in this repository are public.
