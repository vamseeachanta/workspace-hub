---
name: gtm-site-readiness-audit-local-vs-production
description: Audit GTM feature work by separating local artifact readiness from production deployment state, then fix common blockers in aceengineer-website and GTM collateral.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-15
metadata:
  tags: ["gtm", "website", "review", "deployment", "aceengineer-website", "collateral"]
---

# GTM Site Readiness Audit: Local vs Production

Use when GTM/demo/collateral work looks "done" in issues but you need an adversarial review before user approval.

## Why this skill exists

Recent GTM work showed a recurring failure mode: issue status and local repo artifacts suggested completion, but public collateral still had stale placeholders, built-site links were broken, and production URLs were not actually live. The fix was to explicitly separate:

1. local implementation readiness
2. built-site readiness
3. production deployment readiness

Do not collapse those into a single "done" state.

## Workflow

### 1. Review issue claims, but do not trust them
Inspect the relevant GitHub issues and acceptance criteria first, then verify every public-facing claim against files and URLs.

Look especially for:
- closed issues whose acceptance criteria are only partially reflected in files
- tracker issues (`#2016`-style) that still describe old blockers after implementation shipped
- issue bodies that point to old file paths instead of the actual delivered repo paths

### 2. Audit public GTM collateral for trust-killing placeholders
Search the GTM docs and website-page collateral for placeholders or stale identity claims.

High-value checks:
- `Texas #XXXXX`
- fake phone/email/contact values
- stale counts or capability totals
- contradictory claims like "published" vs "ready for publication"

Typical paths:
- `docs/gtm/capability-summary.md`
- `docs/gtm/website-pages/*.html`
- `docs/gtm/capability-map.md`

Rule: placeholders in public/client-facing collateral are blockers, not minor polish.

### 3. Check source and built-site paths separately
In `aceengineer-website`, verify both:
- source: `content/...`
- built artifact: `dist/...`

Do not assume a source file implies a built file exists.

For every CTA/link on a GTM page, confirm the target exists in the built tree. Example failure pattern:
- `content/demos/index.html` links to `demos/jumper-installation.html`
- `dist/demos/jumper-installation.html` is missing
- result: locally or publicly broken link even though a standalone file exists elsewhere in repo

### 4. Validate local built site with an HTTP server and browser
Serve the built site locally and inspect it in browser tools.

Pattern:
```bash
python -m http.server 8788 --directory /path/to/aceengineer-website/dist
```

Then verify in browser:
- gallery page loads
- detailed report links resolve
- methodology links resolve
- page titles are sensible
- no obvious broken navigation/placeholder artifacts remain

This catches issues that static file inspection misses.

### 5. Validate production separately with curl
After local validation, check live URLs explicitly.

Pattern:
```bash
curl -L -s -o /dev/null -w '%{http_code}\n' https://aceengineer.com/demos/
curl -L -s -o /dev/null -w '%{http_code}\n' https://aceengineer.com/methodology/compound-engineering
```

Interpretation:
- local 200 + production 404 = implementation exists but deployment/publish step is still pending
- do not report this as fully approved/live

### 6. If methodology pages exist only as docs, promote them into website content + dist
A common GTM gap is: publication-ready markdown exists under docs, but no website pages exist yet.

Source set:
- `docs/methodology/published/*.md`

Target set:
- `aceengineer-website/content/methodology/<slug>/index.html`
- `aceengineer-website/dist/methodology/<slug>/index.html`

Also add links from a live GTM hub page (for example the demos gallery) so the pages are navigable and reviewable.

### 7. Watch for unresolved build placeholders when writing dist files manually
If you generate `dist/...` files outside the normal site build pipeline, built output may still contain unresolved template tokens such as:
- `{{ rootPath }}`

This can make browser snapshots look superficially okay while links are actually wrong.

Fix by either:
- running the real build pipeline, or
- patching/replacing unresolved placeholders in `dist/...` before validation

### 8. Reconcile GitHub issue state after fixing artifacts
Once the local blockers are fixed, post reconciliation comments to the tracker and affected GTM issues instead of leaving the issue thread stale.

Typical targets:
- tracker issue (`#2016`-style)
- implementation issue for the gallery/site page
- methodology publication issue
- collateral issue with earlier adversarial blockers
- downstream outreach/issues whose blockers changed because assets now exist

What to say:
- which blocker is now cleared locally
- whether the item is ready for local user review vs production deployment
- what is still outstanding (deployment, PDF export, issue-body cleanup, etc.)

Important: do not over-correct into claiming production readiness if live URLs still 404.

### 9. Report readiness in layers
Use a 3-layer readiness model:

- Ready for local artifact review
- Ready in built local site
- Ready/live in production

This avoids the common mistake of marking a GTM item "done" when it is only locally implemented.

### 10. If you must generate site pages outside the normal build pipeline, expect one more cleanup pass
A practical pattern that worked:
- promote `docs/methodology/published/*.md` into `content/methodology/<slug>/index.html`
- mirror to `dist/methodology/<slug>/index.html`
- then do a second verification pass specifically for unresolved build placeholders and broken relative links

Observed failure mode:
- manually generated `dist/...` pages still contained `{{ rootPath }}` in nav/footer assets and links
- browser could render the page body, making the page look superficially okay
- navigation/assets were still wrong until placeholders were replaced

Rule: after any manual `dist/...` generation, explicitly search built output for unresolved template tokens before declaring success.

## Reusable checklist

- [ ] issue claims reviewed
- [ ] GTM collateral searched for public placeholders
- [ ] source and built paths both verified
- [ ] local built site served and browser-checked
- [ ] live production URLs checked with curl
- [ ] methodology pages promoted from docs to site when needed
- [ ] unresolved `{{ rootPath }}` or similar placeholders removed from built output
- [ ] final report distinguishes local readiness from production deployment

## Typical outputs from this workflow

- fixes to `docs/gtm/*` collateral
- fixes/additions under `aceengineer-website/content/demos/*`
- new pages under `aceengineer-website/content/methodology/*`
- mirrored built files under `aceengineer-website/dist/...`
- a short readiness packet stating exactly what is ready now vs what still needs deployment or issue hygiene cleanup
