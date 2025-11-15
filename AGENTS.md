# Repository Guidelines

## Project Structure & Module Organization
Automation for catalog, AI, and cleanup tasks sits in `scripts/`, while provisioning helpers are in `setup-scripts/` and root shell utilities such as `setup-wordpress-complete.sh`. Deployable WordPress assets, SQL backups, and theme overrides stay in `wordpress/`; QA notes belong in `reports/`, `relatorios/`, and `validation/`. Media folders (`homepage_photos/`, `processed_images/`, `instagram_*`) and generated CSVs under `output_catalogo/` are treated as data sources—regenerate them through their script instead of editing manually.

## Build, Test & Development Commands
- `npm install` — install Puppeteer + MCP adapters for the agents.
- `./setup-wordpress-complete.sh` — spin up the Docker WordPress/WooCommerce stack.
- `python import_to_wordpress.py` — push `catalog_completo_classificado.json` via the WooCommerce REST API.
- `php upload_images_final.php` — register processed imagery inside the Media Library.
- `node visual_debug_agent.js` — capture automated storefront screenshots and CSS diagnostics.
- `./test-integrations.sh` — confirm plugin, payment, and shipping health in the containers.

## Coding Style & Naming Conventions
Python modules use 4-space indents, dataclasses, and type hints; run `python -m black scripts/` before committing. PHP utilities follow PSR-12 spacing plus WordPress escaping helpers, and Node scripts stay CommonJS with the indentation already in the file. Shell files start with `#!/bin/bash`, enable `set -euo pipefail`, and avoid side effects. Branches follow `feature/<slug>` or `fix/<issue>`, while filenames stay snake_case for processors and kebab-case for shell wrappers.

## Testing Guidelines
Run `./test-integrations.sh` after every environment or plugin change and store failed logs in `reports/`. Catalog edits must rerun `python scripts/validate_and_enrich.py --dry-run` so `catalogo_clean_ready.csv` and `catalogo_pending.csv` stay in sync. UI or CSS work requires refreshed `validation/screenshots/` assets plus manual checks in `test-marquee.html`, `test-lazy-loading.html`, or by pasting `test-console.js` in DevTools.

## Commit & Pull Request Guidelines
Commits follow a light Conventional Commits tone (`type(scope): summary`) as seen in `docs(import): Add import status report` and `checkpoint: backup antes das correções críticas`. Keep each commit scoped to one subsystem and describe the user impact. PRs must provide a concise summary, repro steps, before/after evidence (screenshots or CSV diffs), and linked tickets. Always flag deployment risks, data migrations, or new environment variables.

## Security & Configuration Tips
Store secrets only in untracked `.env` files or `mcp_config.json`; never commit WooCommerce keys or Google credentials. Double-check `WORDPRESS_URL` (or other endpoints) before running importers so production data is not overwritten. SQL dumps and large media archives under `wordpress/` should be downloaded from the shared drive rather than recreated unless the team agrees otherwise.
