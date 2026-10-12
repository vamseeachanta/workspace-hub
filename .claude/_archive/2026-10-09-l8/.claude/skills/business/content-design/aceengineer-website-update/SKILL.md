---
name: aceengineer-website-update
description: Daily automated website updates with competitor analysis and content sync
type: reference
version: 1.0.0
category: business
capabilities: []
requires: []
see_also: []
tags: []
---

# AceEngineer Website Update Skill

Automates daily website maintenance including competitor SEO analysis and content synchronization from related repositories.

## Quick Start

```bash
# Run full daily update
./scripts/daily-update.sh

# Manual competitor analysis
python scripts/competitor_analysis.py

# Manual content sync
python scripts/content_sync.py --digitalmodel ../digitalmodel --worldenergydata ../worldenergydata

# Setup cron job
./scripts/cron-setup.sh
```

## Proven website publish workflow

Use this when adding or fixing public pages on aceengineer.com.

1. Edit source files under `content/` only.
   - Do not hand-edit `dist/` as the source of truth.
   - For new public pages, create `content/<section>/.../index.html`.
   - If using shared nav/footer/assets, include frontmatter like:
   ```html
   ---
   rootPath: "../../"
   ---
   ```

2. Build locally from repo root:
   ```bash
   npm test -- --runInBand
   npm run build
   ```
   This regenerates `dist/` via `node build.js` using the PostHTML include/expression pipeline.

3. Verify local routes before pushing.
   Example:
   ```bash
   python -m http.server 8788 --directory dist
   curl -I http://127.0.0.1:8788/<path>
   ```
   For important pages, also browser-check the rendered page.

4. Commit only source changes required for deployment.
   In this repo, `dist/` is gitignored; Vercel rebuilds from `content/`.

5. Push to `main`:
   ```bash
   git push origin main
   ```
   Vercel auto-deploys from `main` using:
   - `buildCommand: npm run build`
   - `outputDirectory: dist`

6. Poll production until live:
   ```bash
   curl -k -L -s -o /dev/null -w '%{http_code}\n' https://www.aceengineer.com/<path>
   ```
   Expect an initial 404 during rollout; retry until 200.

7. For GTM/demo work, verify both:
   - the new page itself
   - any inbound links from gallery/index pages

## Critical findings

- The real source tree is `content/`; `dist/` is generated and ignored by git.
- Vercel deployment is automatic after push to `main`; no manual deploy command was needed.
- Production propagation can lag briefly; polling with `curl` caught the transition from 404 to 200.
- For new nested pages (e.g. `content/methodology/.../index.html`), `rootPath` must match nesting depth so shared assets/nav links resolve correctly after build.

## Features

### Competitor Analysis
- Tracks keyword rankings for offshore engineering terms
- Auto-detects competitors from search results
- Generates weekly HTML reports with trends
- Provides SEO improvement recommendations

### Content Sync
- Syncs S-N curve statistics from digitalmodel
- Updates Python module counts
- Imports BSEE production dashboards from worldenergydata
- Generates blog posts from documentation

## Configuration

- `config/keywords.yaml` - Keywords to track
- `config/content-sync.yaml` - Source paths and sync rules

## Outputs

- `reports/competitor-analysis/latest.html` - Latest competitor report
- `assets/data/statistics.json` - Updated site statistics
- `dist/demos/` - Synced demonstration files

## Cron Schedule

Daily at 6 AM local time:
```
0 6 * * * /mnt/github/workspace-hub/aceengineer-website/scripts/daily-update.sh
```

## Dependencies

```bash
pip install pyyaml requests beautifulsoup4
```
