# Tier-1 Indexing Freshness Audit — Latest

Generated: 2026-05-02T03:35:39-05:00 / 2026-05-02T08:35:39+00:00

Working directory: `/mnt/local-analysis/workspace-hub`

Baseline authority: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

Required canonical routing surfaces per tier-1 repo:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- `docs/registry/module-routing.yaml`

Raw/generated inventory such as `docs/CONTENT_INDEX.md` remains discovery-only and is not treated as trusted routing authority.

## Executive Summary

Portfolio status: **red**

No material portfolio-level drift detected: readiness remains partial rather than green. The report timestamp was refreshed, no new cron jobs were scheduled, and current exact gaps/noise are listed below.

The active canonical registry path is treated as `docs/registry/module-routing.yaml`. Legacy `.agent-os` / product-doc references are not used or recommended as routing surfaces.

## Per-Repo Status

| Repo | Status | Summary |
| --- | --- | --- |
| `workspace-hub` | **red** | Missing `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; `docs/README.md` still has active broken legacy links; root still contains tracked report-fragment noise. |
| `digitalmodel` | **yellow** | All required routing surfaces are now present; one broken README link remains and one tracked temp artifact remains under `tests/`. |
| `assetutilities` | **green** | Required canonical surfaces are present; no broken canonical links or tracked trusted-path backup/temp noise detected in this pass. |
| `aceengineer-website` | **red** | Human-readable routing surfaces are present, but required `docs/registry/module-routing.yaml` is missing; historical blog content still contains legacy product-doc references. |

## Exact Findings

### `workspace-hub` — red

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`

Missing canonical surfaces:

- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken/stale references in active canonical surfaces:

- `docs/README.md:299 -> ../.agent-os/product/mission.md`
- `docs/README.md:300 -> ../.agent-os/product/tech-stack.md`
- `docs/README.md:301 -> ../.agent-os/product/roadmap.md`
- `docs/README.md:302 -> ../.agent-os/product/decisions.md`

Noise/hygiene drift:

- No tracked backup/temp artifacts detected under trusted source paths.
- Workspace root still has tracked report-fragment files that weaken root/index trust:
  - `**Complexity:**`
  - `**Date:**`
  - `**Issue:**`
  - `**Review`
  - `**Status:**`
- `docs/CONTENT_INDEX.md` remains a large raw inventory and must remain non-authoritative for routing. It contains many stale-looking inventory entries because it spans archived/cross-repo paths; that reinforces the 2026-04-22 warning, but those entries are not counted as canonical routing breaks.

Concise next actions:

1. Add `docs/maps/workspace-hub-operator-map.md`.
2. Add `docs/registry/module-routing.yaml`.
3. Replace or retire the active broken legacy links in `docs/README.md:299-302` with current canonical routing surfaces.
4. Remove or quarantine tracked root report-fragment files.

2026-04-22 scorecard assumption check:

- **Still holds.** `workspace-hub` remains the strongest control-plane repo, but missing map/registry surfaces plus root/index noise still limit trust.

### `digitalmodel` — yellow

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing canonical surfaces:

- None detected.

Broken/stale references in active canonical surfaces:

- `README.md:63 -> specs/data-needs.yaml`

Noise/hygiene drift:

- Tracked temp artifact in trusted test path:
  - `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`

Concise next actions:

1. Repair or retire the `README.md:63` link to `specs/data-needs.yaml`.
2. Remove the tracked temp test artifact.
3. Keep `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, and `docs/registry/module-routing.yaml` synchronized as source/test/docs routing changes.

2026-04-22 scorecard assumption check:

- **Needs positive revision.** The prior “missing repo-wide routing surfaces” finding has improved: the docs entry point, operator map, and registry are now present. Remaining status is yellow due to one broken README link and one trusted-path temp artifact, not missing routing surfaces.

### `assetutilities` — green

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing canonical surfaces:

- None detected.

Broken/stale references in active canonical surfaces:

- None detected.

Noise/hygiene drift:

- No tracked backup/cache/runtime artifacts detected under trusted source paths.
- No suspicious tracked root fragments detected.

Concise next actions:

1. Keep the present canonical routing surfaces synchronized with source/test/docs changes.
2. Continue trusted-path noise checks during issue work.
3. Avoid reintroducing legacy `.agent-os` / product-doc routing references into active docs.

2026-04-22 scorecard assumption check:

- **Needs positive revision.** `assetutilities` has improved materially since 2026-04-22: the required canonical human and machine-readable routing surfaces are now present and no tracked trusted-path backup/temp noise was detected in this pass.

### `aceengineer-website` — red

Present canonical surfaces:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Missing canonical surfaces:

- `docs/registry/module-routing.yaml`

Broken/stale references in active canonical surfaces:

- None detected.

Noise/hygiene drift:

- No tracked backup/cache/runtime artifacts detected under trusted source paths.
- No suspicious tracked root fragments detected.

Legacy reference residue, not routing authority:

- `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md:433`
- `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md:434`
- `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md:435`

Concise next actions:

1. Add `docs/registry/module-routing.yaml`.
2. Keep `AGENTS.md`, `docs/README.md`, and `docs/maps/aceengineer-website-operator-map.md` synchronized with site source paths.
3. Qualify or clean historical blog references so legacy product-doc mentions cannot be mistaken for current routing instructions.

2026-04-22 scorecard assumption check:

- **Still holds with stricter registry interpretation.** Human-readable routing improved, but the repo remains incomplete until the required machine-readable registry exists.

## 2026-04-22 Scorecard Assumptions

Status: **still hold directionally, with targeted revisions**

- **Still holds:** overall readiness is partial; the tier-1 portfolio cannot be treated as green for deterministic code placement/retrieval.
- **Still holds:** `workspace-hub` remains the control-plane repo but needs curated routing-map/registry completion and root/index hygiene cleanup.
- **Needs positive revision:** `digitalmodel` now has the required repo-wide docs entry point, operator map, and registry; it is yellow for remaining broken-link/temp-artifact cleanup rather than red for missing surfaces.
- **Needs positive revision:** `assetutilities` now has the required canonical surfaces and appears green in this pass.
- **Needs stricter registry interpretation:** `aceengineer-website` remains incomplete until `docs/registry/module-routing.yaml` exists, even though human-readable routing surfaces are present.

## Next Actions by Priority

1. **P0 — `workspace-hub`:** add missing operator map/registry; remove active broken legacy links and root report-fragment noise.
2. **P0 — `aceengineer-website`:** add `docs/registry/module-routing.yaml`.
3. **P1 — `digitalmodel`:** fix broken README data-needs link and remove tracked temp test artifact.
4. **P2 — `assetutilities`:** maintain current green routing state and continue freshness checks.

## Freshness Result

The report timestamp was refreshed locally at `/mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md`. No new cron jobs were scheduled. No legacy `.agent-os` / product-doc references are recommended as routing surfaces.
