# 2026-05-08 Tier-1 Freshness Audit Lessons

Use as a compact evidence reference for future tier-1 indexing freshness audits.

## Status-level result

The 2026-05-08 scheduled local audit refreshed `docs/reports/tier-1-indexing-freshness-latest.md` and kept status levels unchanged:

- `workspace-hub`: RED
- `digitalmodel`: YELLOW
- `assetutilities`: YELLOW
- `aceengineer-website`: RED

The report wording used **no status-level material drift detected** because new non-status-changing evidence was surfaced.

## Canonical surfaces inspected

For each tier-1 repo, inspect these first:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md` where applicable
- `docs/registry/module-routing.yaml` where applicable

Do not recommend legacy `.agent-os` product-doc references as current routing surfaces; only report them as stale/broken residue if canonical docs still link them.

## Evidence patterns to preserve

- `workspace-hub` missing canonical routing surfaces: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`.
- `workspace-hub` README referenced missing scripts: `./scripts/ai-review/gemini-review-manager.sh`, `./scripts/ai-review/review-manager.sh`.
- `digitalmodel` had broken/stale refs: `README.md -> specs/data-needs.yaml`; `docs/maps/digitalmodel-operator-map.md -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` as a repo-local target, while the matching map existed only at workspace level.
- `assetutilities` had no broken/missing required canonical surfaces in the refined scan, but still had trusted-path runtime/cache noise.
- `aceengineer-website` still lacked `docs/registry/module-routing.yaml`.

## False-positive filters

Do not count the following as broken literal paths unless surrounding text explicitly presents them as canonical links:

- Wildcards/patterns: `*.html`, `content/*.html`, `tests/unit/test_common_*.py`.
- Descriptive module names in overview tables: `engine.py`, `calculation.py`, `math_helpers.py`.
- Naming placeholders: `feature-name.md`.
- Bare visible link labels when Markdown targets include a valid directory, e.g. resolve `modules/ai/AI_AGENT_GUIDELINES.md` from `docs/README.md` rather than treating bare `AI_AGENT_GUIDELINES.md` as missing.

## Validation checks used

Before finalizing the report, verify:

- timestamp refreshed to current audit date/time
- status table includes all four tier-1 repos
- no wildcard false positives remain in broken-ref lists
- the 2026-04-22 scorecard assumption check is present and still says partial readiness only unless evidence changes
- the report states no new cron jobs were scheduled when the audit is local-only
