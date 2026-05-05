# Tier-1 Indexing Freshness Audit — Latest

Generated: 2026-05-05T03:37:40-05:00
Generated UTC: 2026-05-05T08:37:40Z

Working directory: `/mnt/local-analysis/workspace-hub`

Baseline authority: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`

Required canonical routing surfaces per tier-1 repo:

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/<repo>-operator-map.md`
- `docs/registry/module-routing.yaml`

Raw/generated inventory such as `docs/CONTENT_INDEX.md` remains discovery-only and is not treated as trusted routing authority. Legacy product-doc reference patterns are not used or recommended as routing surfaces.

## Executive Summary

Portfolio status: **red**

No material drift detected since the prior freshness pass: the report timestamp was refreshed, no new cron jobs were scheduled, and the current gaps/noise remain consistent with the prior known state.

The 2026-04-22 tier-1 indexing scorecard assumptions **still hold directionally, with targeted revisions**: `workspace-hub` remains the strongest control-plane repo but still has routing/index hygiene gaps; `digitalmodel` and `assetutilities` have materially improved canonical surfaces; `aceengineer-website` remains incomplete until its canonical machine-readable registry exists.

## Per-Repo Status

| Repo | Status | Summary |
| --- | --- | --- |
| `workspace-hub` | **red** | missing `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`; 4 broken active reference(s); 5 active legacy-residue line(s); 4 tracked / 0 untracked cache-runtime-noise item(s); 5 tracked root/index noise item(s) |
| `digitalmodel` | **yellow** | 2 broken active reference(s); 1 tracked / 0 untracked cache-runtime-noise item(s) |
| `assetutilities` | **green** | required canonical surfaces present; no broken active canonical links or trusted-path backup/cache/runtime noise detected |
| `aceengineer-website` | **red** | missing `docs/registry/module-routing.yaml`; 2 active legacy-residue line(s) |

## Exact Findings

### `workspace-hub` — red

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`

Missing canonical surfaces:
- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Machine-readable registry references:
- `specs/module-registry.yaml` (tracked; non-canonical/supplementary)

Broken/stale references in active canonical surfaces:
- broken: `docs/README.md:299 -> ../.agent-os/product/mission.md`
- broken: `docs/README.md:300 -> ../.agent-os/product/tech-stack.md`
- broken: `docs/README.md:301 -> ../.agent-os/product/roadmap.md`
- broken: `docs/README.md:302 -> ../.agent-os/product/decisions.md`
- stale legacy residue: `docs/README.md:263 contains retired product-doc/legacy residue`
- stale legacy residue: `docs/README.md:299 contains retired product-doc/legacy residue`
- stale legacy residue: `docs/README.md:300 contains retired product-doc/legacy residue`
- stale legacy residue: `docs/README.md:301 contains retired product-doc/legacy residue`
- stale legacy residue: `docs/README.md:302 contains retired product-doc/legacy residue`

Noise/hygiene drift:
- tracked runtime/temp artifact: 4
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-4-woodfibre.pid`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-3-doris-codes.pid`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-2-doris-university.pid`
  - `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs/terminal-1-sesa.pid`
- tracked workspace root/index noise weakening routing trust:
  - `**Complexity:**`
  - `**Date:**`
  - `**Issue:**`
  - `**Review`
  - `**Status:**`

Concise next actions:
1. Add/restore `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`.
2. Replace or retire active broken legacy navigation in `docs/README.md` with current canonical routing surfaces.
3. Remove or quarantine tracked root report-fragment files and tracked runtime artifacts from trusted scan paths.

2026-04-22 scorecard assumption check:
- **Still holds.** It remains the richest control-plane repo, but missing map/registry surfaces plus root/index hygiene issues still limit deterministic routing trust.

### `digitalmodel` — yellow

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing canonical surfaces:
- None detected.

Machine-readable registry references:
- `docs/registry/module-routing.yaml` (tracked; canonical)

Broken/stale references in active canonical surfaces:
- broken: `README.md:73 -> specs/data-needs.yaml`
- broken: `docs/maps/digitalmodel-operator-map.md:9 -> `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md``

Noise/hygiene drift:
- tracked runtime/temp artifact: 1
  - `tests/workflows/integration/conftest.py.tmp.142657.1759122346612`

Concise next actions:
1. Repair or retire the broken `README.md` reference to the missing data-needs file.
2. Repair or retire the operator-map reference to the missing specialized operator map, or create that map if still intended.
3. Remove the tracked temporary test artifact and keep cache/runtime noise out of trusted scan paths.

2026-04-22 scorecard assumption check:
- **Needs positive revision, but not green.** Required repo-wide routing surfaces are present; remaining issues are localized broken-link/map-reference cleanup plus cache/temp hygiene.

### `assetutilities` — green

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing canonical surfaces:
- None detected.

Machine-readable registry references:
- `docs/registry/module-routing.yaml` (tracked; canonical)

Broken/stale references in active canonical surfaces:
- None detected.
- Resolved wildcard routing patterns checked as present:
  - `README.md:19 -> `docs/sub_*``
  - `docs/README.md:13 -> `tests/unit/test_common_*.py``
  - `docs/README.md:16 -> `src/assetutilities/common/data*.py``
  - `docs/README.md:17 -> `src/assetutilities/common/visualization*.py``
  - `docs/README.md:17 -> `tests/unit/test_visualization*.py``
  - `docs/README.md:42 -> `tests/modules/**/results/``
  - `docs/maps/assetutilities-operator-map.md:12 -> `tests/unit/test_common_*.py``
  - `docs/maps/assetutilities-operator-map.md:16 -> `tests/unit/test_traceability*.py``

Noise/hygiene drift:
- No backup/cache/runtime noise detected under trusted scan paths in this pass.

Concise next actions:
1. Keep required canonical routing surfaces synchronized.
2. Continue keeping cache/runtime noise out of trusted scan paths.
3. Continue verifying wildcard routing patterns resolve as modules/tests evolve.

2026-04-22 scorecard assumption check:
- **Needs positive revision.** Required canonical surfaces are present, wildcard routing references resolve, and no trusted-path backup/cache/runtime noise was detected in this pass.

### `aceengineer-website` — red

Present canonical surfaces:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Missing canonical surfaces:
- `docs/registry/module-routing.yaml`

Machine-readable registry references:
- None detected.

Broken/stale references in active canonical surfaces:
- stale legacy residue: `docs/README.md:32 contains retired product-doc/legacy residue`
- stale legacy residue: `docs/maps/aceengineer-website-operator-map.md:29 contains retired product-doc/legacy residue`
- Resolved wildcard routing patterns checked as present:
  - `AGENTS.md:20 -> `content/*.html``
  - `AGENTS.md:23 -> `tests/js/*calculator*.test.js``
  - `README.md:24 -> `content/**``
  - `README.md:28 -> `content/**``
  - `README.md:107 -> `content/**``
  - `docs/maps/aceengineer-website-operator-map.md:11 -> `content/*.html``
  - `docs/maps/aceengineer-website-operator-map.md:15 -> `tests/js/*calculator*.test.js``

Noise/hygiene drift:
- No backup/cache/runtime noise detected under trusted scan paths in this pass.

Concise next actions:
1. Add `docs/registry/module-routing.yaml` as the canonical machine-readable routing registry.
2. Keep human-readable routing surfaces synchronized with site source paths.
3. Qualify or clean historical legacy residue outside canonical surfaces so broad search cannot confuse workers.

2026-04-22 scorecard assumption check:
- **Still holds with stricter registry interpretation.** Human-readable routing is present, but the repo remains incomplete until the canonical registry exists.

## 2026-04-22 Scorecard Assumptions

Status: **still hold directionally, with targeted positive revisions**

- **Still holds:** overall tier-1 readiness is partial; the portfolio is not green for deterministic code placement/retrieval.
- **Still holds:** `workspace-hub` remains control-plane rich but needs curated operator-map/registry completion and root/index cleanup.
- **Needs positive revision:** `digitalmodel` now has the required docs entry point, operator map, and canonical registry; it is yellow for localized cleanup.
- **Needs positive revision:** `assetutilities` has required canonical surfaces, resolving wildcard references, and no detected trusted-path backup/cache/runtime noise in this pass.
- **Needs stricter registry interpretation:** `aceengineer-website` remains red until `docs/registry/module-routing.yaml` exists.

## Next Actions by Priority

1. **P0 — `workspace-hub`:** add/restore missing canonical operator map and registry; remove active broken legacy navigation and tracked root report-fragment noise.
2. **P0 — `aceengineer-website`:** add the canonical `docs/registry/module-routing.yaml`.
3. **P1 — `digitalmodel`:** fix the broken README/operator-map references and remove the tracked temporary test artifact/cache noise.
4. **P2 — `assetutilities`:** maintain current green routing state and keep cache/runtime noise out of trusted scan paths.

## Run Notes

- No new cron jobs were scheduled.
- This pass updated only the local latest report path requested by the scheduled job.
- The audit intentionally treats broad raw inventories as discovery-only and uses only current canonical routing surfaces for status.
