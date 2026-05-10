# 2026-05-09 Tier-1 Freshness Audit Lessons

Use as a compact evidence reference for the daily tier-1 indexing freshness audit after the 2026-05-09 scheduled run.

## Status-level result

The 2026-05-09 scheduled local audit refreshed `docs/reports/tier-1-indexing-freshness-latest.md` and kept status levels unchanged:

- `workspace-hub`: RED
- `digitalmodel`: YELLOW
- `assetutilities`: YELLOW
- `aceengineer-website`: RED

Use **no status-level material drift detected** when statuses remain unchanged and the same material blockers remain.

## Evidence snapshot

- `workspace-hub` still lacks `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`.
- `workspace-hub` top-level `README.md` still references missing review-manager scripts:
  - `./scripts/ai-review/gemini-review-manager.sh`
  - `./scripts/ai-review/review-manager.sh`
- `workspace-hub/docs/README.md` still contains stale legacy `.agent-os/product/*` links. Report these as residue only; do not recommend legacy `.agent-os` routing patterns.
- `digitalmodel` still has a missing `README.md -> specs/data-needs.yaml` target.
- `digitalmodel/docs/maps/digitalmodel-operator-map.md` still references `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` as a repo-local target; the matching map exists only at workspace level (`/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`).
- `assetutilities` still has no broken/missing required canonical surfaces after false-positive filtering, but trusted-path runtime/cache noise remains.
- `aceengineer-website` still lacks `docs/registry/module-routing.yaml`; required canonical surfaces showed no broken local Markdown links after false-positive filtering.

## Scanner false-positive refinement

When scanning canonical docs for broken references:

- Markdown links should be resolved relative to the file containing the link.
- Backtick code spans inside routing tables often intentionally use repo-root paths (`src/...`, `tests/...`, `docs/...`, `scripts/...`, `AGENTS.md`, `MODULE_STRUCTURE.md`). Do **not** automatically resolve these relative to the current document directory and mark them broken. Either resolve obvious repo-root paths from repo root or treat them as routing descriptors unless surrounding text presents them as a literal local link.
- Keep existing false-positive filters: wildcards (`*.html`, `content/*.html`), placeholders (`feature-name.md`, `<domain>`), and descriptive module examples (`engine.py`, `calculation.py`, `math_helpers.py`).

## Reporting pattern

For scheduled/local-only runs:

- Refresh the timestamp even when nothing materially changed.
- Keep a compact status table plus per-repo evidence.
- Include exact broken/missing surfaces and concise next actions.
- Include the 2026-04-22 scorecard assumption check.
- State explicitly that no new cron jobs were scheduled.
