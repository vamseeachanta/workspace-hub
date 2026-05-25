# Tier-1 Indexing Freshness Report

Generated: 2026-05-25T03:39:18-05:00
Working directory: `/mnt/local-analysis/workspace-hub`
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`

No new cron jobs were scheduled.

## Overall Status

Portfolio status: **red**

Material drift: **no material drift detected at the status level** versus the corrected late-May baseline. The previous checked-in/latest report content was stale all-red for `digitalmodel` and `assetutilities`; this refresh corrects that generated-report drift while preserving the same portfolio blockers.

## Status Summary

| Repo | Status | Exact broken or missing surfaces | Trusted-path noise | Concise next action |
|---|---:|---|---|---|
| `workspace-hub` | **red** | Missing `docs/maps/workspace-hub-operator-map.md`; missing `docs/registry/module-routing.yaml`; broken active references in `docs/README.md:300-303` to retired product-doc paths; stale legacy mention at `docs/README.md:264` | 74 sampled cache/runtime/log entries under trusted paths | Add current operator map and module registry; replace retired routing links in `docs/README.md`; clean or exclude runtime/cache/log noise from trusted indexes |
| `digitalmodel` | **yellow** | Broken `README.md:73 -> specs/data-needs.yaml`; stale repo-local routing text at `docs/maps/digitalmodel-operator-map.md:9` points to `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`, which is absent repo-local but present in workspace-level maps | 91 sampled `__pycache__/` entries under trusted paths | Fix/remove the missing data-needs link; clarify the OrcaWave/OrcaFlex historical map as workspace-level context or add a repo-local target; clean cache noise |
| `assetutilities` | **yellow** | None detected across required canonical surfaces | 12 sampled `__pycache__/` entries under trusted source paths | Keep current surfaces; clean generated cache noise or exclude it from routing/index scans |
| `aceengineer-website` | **red** | Missing `docs/registry/module-routing.yaml` | 4 sampled `__pycache__/` entries under tests | Add current machine-readable routing registry or document its canonical alternative; clean cache noise |

## Canonical Surface Inventory

### `workspace-hub`

Path inspected: `/mnt/local-analysis/workspace-hub`

Present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`

Missing:
- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

Broken/stale evidence:
- `docs/README.md:264` — stale legacy configuration tree mention
- `docs/README.md:300 -> ../.agent-os/product/mission.md`
- `docs/README.md:301 -> ../.agent-os/product/tech-stack.md`
- `docs/README.md:302 -> ../.agent-os/product/roadmap.md`
- `docs/README.md:303 -> ../.agent-os/product/decisions.md`

Trusted-path noise evidence, sampled:
- `docs/plans/agent-swarm-audits/2026-05-10/logs/`
- `docs/plans/claude-ops-2026-04-09/results/backups/`
- `docs/plans/machine-prompts/2026-04-27/execution/orchestration-readiness-interactive-session.log`
- `docs/sessions/bulk-comment-2026-05-18T193334Z.log`
- `src/__pycache__/`
- `tests/__pycache__/`

Status rationale: red because required current routing surfaces are missing and stale/broken active references remain in the docs entry point.

### `digitalmodel`

Path inspected: `/mnt/local-analysis/digitalmodel` using sibling checkout fallback because nested `/mnt/local-analysis/workspace-hub/digitalmodel` is absent.

Present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing:
- none

Broken/stale evidence:
- `README.md:73 -> specs/data-needs.yaml` — target absent
- `docs/maps/digitalmodel-operator-map.md:9` references `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; target is absent repo-local at `/mnt/local-analysis/digitalmodel/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`, while a similarly named workspace-level map exists at `/mnt/local-analysis/workspace-hub/docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

Trusted-path noise evidence, sampled:
- `src/digitalmodel/__pycache__/`
- `src/digitalmodel/hydrodynamics/__pycache__/`
- `src/digitalmodel/infrastructure/__pycache__/`
- `src/digitalmodel/marine_ops/__pycache__/`

Status rationale: yellow because required surfaces exist, but one active README link and one routing-authority reference remain stale/ambiguous, and generated cache noise remains in trusted paths.

### `assetutilities`

Path inspected: `/mnt/local-analysis/assetutilities` using sibling checkout fallback because nested `/mnt/local-analysis/workspace-hub/assetutilities` is absent.

Present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

Missing:
- none

Broken/stale evidence:
- none detected across the canonical surfaces inspected

Trusted-path noise evidence, sampled:
- `src/assetutilities/__pycache__/`
- `src/assetutilities/common/__pycache__/`
- `src/assetutilities/modules/__pycache__/`
- `src/assetutilities/modules/yml_utilities/__pycache__/`

Status rationale: yellow because routing surfaces are present and current enough for placement/retrieval, but trusted-path cache noise still weakens index hygiene.

### `aceengineer-website`

Path inspected: `/mnt/local-analysis/aceengineer-website` using sibling checkout fallback because nested `/mnt/local-analysis/workspace-hub/aceengineer-website` is absent.

Present:
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

Missing:
- `docs/registry/module-routing.yaml`

Broken/stale evidence:
- none detected across present canonical surfaces

Trusted-path noise evidence, sampled:
- `tests/__pycache__/`
- `tests/docs/__pycache__/`
- `tests/python/__pycache__/`
- `tests/repo_structure/__pycache__/`

Status rationale: red because the current machine-readable routing registry is absent.

## 2026-04-22 Tier-1 Indexing Scorecard Assumption Check

Result: **assumptions partially hold, but the scorecard remains historical context and needs detail-level revision against live repo surfaces.**

Still holds:
- Portfolio readiness remains blocked by missing current routing surfaces in `workspace-hub` and `aceengineer-website`.
- `workspace-hub` remains the control-plane repo but has routing/index hygiene risk.
- `digitalmodel` remains structurally strong and has the best source/test/docs routing footprint among the tier-1 repos.
- Machine-readable routing is still incomplete portfolio-wide until every applicable repo exposes `docs/registry/module-routing.yaml` or a documented current equivalent.

Needs revision:
- `digitalmodel` and `assetutilities` should not be treated as all-red: both currently have the required canonical surface set.
- Older broken-link counts for `assetutilities` should not be reused unless reproduced by a false-positive-filtered scan.
- Any old all-red or retired product-doc framing should be superseded by the current canonical surfaces and the live evidence in this report.

## Concise Next Actions

1. `workspace-hub`: create or refresh `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace stale broken references in `docs/README.md`; clean or exclude trusted-path runtime/cache/log noise.
2. `aceengineer-website`: create `docs/registry/module-routing.yaml` or document a current machine-readable routing equivalent.
3. `digitalmodel`: fix `README.md:73 -> specs/data-needs.yaml`; clarify or repair the OrcaWave/OrcaFlex map reference in `docs/maps/digitalmodel-operator-map.md:9`; clean cache noise.
4. `assetutilities`: clean cache noise or exclude generated cache paths from routing/index scans.
5. Freshness automation: no scheduling change; patch the generator separately, under the normal issue/TDD workflow, if it continues to produce stale all-red output from path assumptions.
