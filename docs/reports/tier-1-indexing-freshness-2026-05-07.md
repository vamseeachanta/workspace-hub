# Tier-1 Indexing Freshness Audit — Latest

Date/time: 2026-05-07T03:36:08-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website` under `/mnt/local-analysis/workspace-hub`.
Mode: scheduled local-only audit; no cron jobs created; legacy `.agent-os` patterns are reported only as stale residue, not recommended as routing surfaces.

## Executive Summary

Per-repo status: workspace-hub: RED, digitalmodel: YELLOW, assetutilities: YELLOW, aceengineer-website: RED.
Freshness delta: **no material drift detected; timestamp and current evidence refreshed**.

The 2026-04-22 scorecard assumption of **partial readiness only** still holds. Detailed assumptions remain revised: `digitalmodel` and `assetutilities` now expose current repo-local operator maps plus `docs/registry/module-routing.yaml`, while `workspace-hub` and `aceengineer-website` remain below the desired routing/index contract because canonical routing or registry surfaces are incomplete. Runtime/cache noise continues to weaken retrieval trust across trusted paths.

## Status Table

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | RED | missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`; broken links: `docs/README.md -> ../.agent-os/product/decisions.md`, `docs/README.md -> ../.agent-os/product/mission.md`, `docs/README.md -> ../.agent-os/product/roadmap.md`, `docs/README.md -> ../.agent-os/product/tech-stack.md`; stale legacy refs in canonical surfaces | Create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace stale docs entry-point links; separate curated routing from raw inventory/root noise. |
| `digitalmodel` | YELLOW | broken links: `README.md -> specs/data-needs.yaml`, `docs/maps/digitalmodel-operator-map.md -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; stale registry refs: `README.md references `specs/data-needs.yaml` (missing)` | Fix the broken `README.md` local reference and clean runtime cache from trusted paths; keep operator map and registry synchronized. |
| `assetutilities` | YELLOW | none in required canonical surfaces | Clean runtime/cache artifacts under trusted paths; keep `docs/maps/assetutilities-operator-map.md` and `docs/registry/module-routing.yaml` synchronized. |
| `aceengineer-website` | RED | missing: `docs/registry/module-routing.yaml` | Add `docs/registry/module-routing.yaml`; keep docs entry/operator map free of legacy routing patterns; clean cache artifacts. |

## Per-Repo Findings

### workspace-hub — RED

**Present canonical surfaces**
- `AGENTS.md`
- `README.md`
- `docs/README.md`

**Missing canonical surfaces**
- `docs/maps/workspace-hub-operator-map.md`
- `docs/registry/module-routing.yaml`

**Broken/stale references in inspected canonical surfaces**
- `docs/README.md -> ../.agent-os/product/decisions.md`
- `docs/README.md -> ../.agent-os/product/mission.md`
- `docs/README.md -> ../.agent-os/product/roadmap.md`
- `docs/README.md -> ../.agent-os/product/tech-stack.md`
- Stale legacy `.agent-os` references detected in canonical surfaces (reported as residue only, not recommended):
  - `docs/README.md:263: ├── .agent-os/              # Agent OS configuration`
  - `docs/README.md:299: - [Mission & Vision](../.agent-os/product/mission.md)`
  - `docs/README.md:300: - [Technical Stack](../.agent-os/product/tech-stack.md)`
  - `docs/README.md:301: - [Development Roadmap](../.agent-os/product/roadmap.md)`
  - `docs/README.md:302: - [Product Decisions](../.agent-os/product/decisions.md)`

**Registry references**
- `docs/registry/module-routing.yaml`: missing
- Historical `specs/module-registry.yaml`: present; not treated as canonical for this audit.
- No stale/missing registry references detected in inspected canonical surfaces or current registry.

**Trusted-path backup/cache/runtime noise**
- `docs/plans/overnight-prompts/2026-04-28-elements-wave/logs`
- `scripts/__pycache__`
- `scripts/ai/__pycache__`
- `scripts/ai/tests/__pycache__`
- `scripts/analysis/__pycache__`
- `scripts/animations/__pycache__`
- `scripts/animations/scenes/__pycache__`
- `scripts/automation/__pycache__`
- `scripts/calculations/__pycache__`
- `scripts/ci_health/__pycache__`
- `scripts/coordination/routing/logs`
- `scripts/cron/__pycache__`
- `scripts/cron/tests/__pycache__`
- `scripts/data/__pycache__`
- `scripts/data/dagster-eval/__pycache__`
- `scripts/data/doc_intelligence/__pycache__`
- `scripts/data/doc_intelligence/promoters/__pycache__`
- `scripts/data/doc_intelligence/tests/__pycache__`
- `scripts/data/document-index/__pycache__`
- `scripts/data/document-index/tests/__pycache__`

**Workspace-hub root/index noise affecting routing trust**
- `docs/CONTENT_INDEX.md`: 30,086 lines (2,863,174 bytes); raw inventory only, not curated routing authority.
- root noise: `.baseline-cache`
- root noise: `.cache`
- root noise: `.mypy_cache`
- root noise: `.nightly-results`
- root noise: `.pytest_cache`
- root noise: `.ruff_cache`
- root noise: `.swarm`
- root noise: `.sync-reports`
- root noise: `.tmp-build-commit.py`
- root noise: `.tmp-inspect-2348`
- root noise: `.uv-cache`
- root noise: `.venv`
- root noise: `.venv-manim`
- root noise: `.venv-test`
- root noise: `ace_cfp_sending_kit_2026-04-09.md`
- root noise: `daily_gmail_action_digest_2026-04-09.md`
- root noise: `dist`
- root noise: `docs-reorg-assessment.md`
- root noise: `draft_ace_api_cfp_note.md`
- root noise: `draft_skestates_1099_followup_email.md`
- root noise: `draft_skestates_hoa_transfer_email.md`
- root noise: `draft_skestates_pest_exteriors_followup.md`
- root noise: `final_skestates_1099_followup_email.md`
- root noise: `final_skestates_hoa_transfer_email.md`
- root noise: `final_skestates_pest_exteriors_followup.md`
- root noise: `generated`
- root noise: `gmail_copy_paste_packet_2026-04-09.md`
- root noise: `gmail_operator_packet_2026-04-09.md`
- root noise: `gmail_presend_checklist_2026-04-09.md`
- root noise: `gmail_sendready_status_2026-04-09.md`
- ... 3 additional root-noise paths omitted.

**Git status notes (pre-existing/local, first 12 lines)**
- ` M config/ai-tools/agent-capability-radar.html`
- ` M docs/reports/tier-1-indexing-freshness-latest.md`
- `?? docs/reports/tier-1-indexing-freshness-2026-05-07.md`

### digitalmodel — YELLOW

**Present canonical surfaces**
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/digitalmodel-operator-map.md`
- `docs/registry/module-routing.yaml`

**Missing canonical surfaces**
- None detected.

**Broken/stale references in inspected canonical surfaces**
- `README.md -> specs/data-needs.yaml`
- `docs/maps/digitalmodel-operator-map.md -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

**Registry references**
- `docs/registry/module-routing.yaml`: present
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.
- README.md references `specs/data-needs.yaml` (missing)

**Trusted-path backup/cache/runtime noise**
- `docs/domains/orcaflex/examples/qa/__pycache__`
- `docs/domains/orcawave/L01_aqwa_benchmark/__pycache__`
- `docs/guides/legacy/apirp2rd/COD/API-STD-2RD/Rev1/logs`
- `docs/guides/legacy/apirp2rd/COD/API-STD-2RD/Rev2/logs`
- `docs/legacy/apirp2rd/COD/API-STD-2RD/Rev1/logs`
- `docs/legacy/apirp2rd/COD/API-STD-2RD/Rev2/logs`
- `src/digitalmodel/__pycache__`
- `src/digitalmodel/infrastructure/__pycache__`
- `src/digitalmodel/infrastructure/base_configs/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/config/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/marine/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/marine/ship/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/pipeline_solvers/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/buckling/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/elements/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/fea/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/stress/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/utils/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/viv/__pycache__`
- `src/digitalmodel/infrastructure/calculations/__pycache__`
- ... 13 additional trusted-path noise paths omitted from this compact report.

**Root/runtime noise**
- `.benchmarks`
- `.hypothesis`
- `.mypy_cache`
- `.pytest_cache`
- `.ruff_cache`
- `.swarm`
- `.venv`
- `build`
- `dist`
- `logs`
- `reports`

**Git status notes (pre-existing/local, first 12 lines)**
- Clean or no git status output.

### assetutilities — YELLOW

**Present canonical surfaces**
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/assetutilities-operator-map.md`
- `docs/registry/module-routing.yaml`

**Missing canonical surfaces**
- None detected.

**Broken/stale references in inspected canonical surfaces**
- No broken local Markdown/code-span links detected in required canonical surfaces.

**Registry references**
- `docs/registry/module-routing.yaml`: present
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.
- No stale/missing registry references detected in inspected canonical surfaces or current registry.

**Trusted-path backup/cache/runtime noise**
- `src/assetutilities/__pycache__`
- `src/assetutilities/agent_os/cli/__pycache__`
- `src/assetutilities/agent_os/commands/__pycache__`
- `src/assetutilities/agent_os/commands/cli_components/__pycache__`
- `src/assetutilities/agent_os/commands/context/__pycache__`
- `src/assetutilities/agent_os/commands/docs/__pycache__`
- `src/assetutilities/agent_os/commands/specs/__pycache__`
- `src/assetutilities/agent_os/commands/templates/__pycache__`
- `src/assetutilities/agent_os/integration/__pycache__`
- `src/assetutilities/calculations/__pycache__`
- `src/assetutilities/common/__pycache__`
- `src/assetutilities/common/download_data/__pycache__`
- `src/assetutilities/common/readers/__pycache__`
- `src/assetutilities/common/visualization/__pycache__`
- `src/assetutilities/common/webscraping/__pycache__`
- `src/assetutilities/constants/__pycache__`
- `src/assetutilities/devtools/__pycache__`
- `src/assetutilities/modules/__pycache__`
- `src/assetutilities/modules/csv_utilities/__pycache__`
- `src/assetutilities/modules/data_exploration/__pycache__`
- `src/assetutilities/modules/excel_utilities/__pycache__`

**Root/runtime noise**
- `.benchmarks`
- `.mypy_cache`
- `.pytest_cache`
- `.ruff_cache`
- `.swarm`
- `.sync-reports`
- `.venv`
- `build`
- `dist`
- `htmlcov`
- `logs`
- `reports`

**Git status notes (pre-existing/local, first 12 lines)**
- `?? .planning/`
- `?? docs/plans/`

### aceengineer-website — RED

**Present canonical surfaces**
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

**Missing canonical surfaces**
- `docs/registry/module-routing.yaml`

**Broken/stale references in inspected canonical surfaces**
- No broken local Markdown/code-span links detected in required canonical surfaces.
- Broader noncanonical docs/content still contain legacy `.agent-os` residue (not treated as current canonical routing surfaces): `docs/AI_AGENT_ORCHESTRATION.md`, `docs/modules/README.md`, `docs/modules/agent-os/enhanced-create-specs-migration-guide.md`, `docs/modules/agent-os/enhanced-create-specs-setup.md`, `docs/modules/agent-os/enhanced-create-specs-troubleshooting.md`.

**Registry references**
- `docs/registry/module-routing.yaml`: missing
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.
- No stale/missing registry references detected in inspected canonical surfaces or current registry.

**Trusted-path backup/cache/runtime noise**
- `scripts/__pycache__`
- `tests/__pycache__`
- `tests/python/__pycache__`

**Root/runtime noise**
- `.benchmarks`
- `.pytest_cache`
- `.venv`
- `dist`
- `logs`
- `reports`

**Git status notes (pre-existing/local, first 12 lines)**
- Clean or no git status output.

## 2026-04-22 Scorecard Assumption Check

- Baseline verdict still valid: **partial readiness only**; do not treat tier-1 routing as fully green.
- Detailed assumptions remain revised from the original 2026-04-22 snapshot: `digitalmodel` and `assetutilities` are stronger because each now has `docs/README.md`, `docs/maps/<repo>-operator-map.md`, and `docs/registry/module-routing.yaml`.
- `workspace-hub` remains below the desired control-plane standard: missing repo-local operator map and canonical module-routing registry, stale legacy links in `docs/README.md`, and root/index/runtime noise that weakens routing trust.
- `aceengineer-website` remains below the desired durable routing standard: `docs/README.md` and operator map exist, but canonical `docs/registry/module-routing.yaml` is still absent.
- Runtime/cache noise across trusted paths remains a recurring hygiene issue; it does not change repo mission assumptions but does weaken retrieval trust and should be cleaned separately from routing-surface creation.

## Concise Next Actions

1. `workspace-hub`: add `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace stale docs entry-point links; split curated routing from raw inventory/noise.
2. `aceengineer-website`: add `docs/registry/module-routing.yaml`; keep `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md` free of legacy routing patterns; clean cache artifacts.
3. `digitalmodel`: fix `README.md -> specs/data-needs.yaml`; clean `__pycache__` and other runtime artifacts from trusted paths.
4. `assetutilities`: clean `__pycache__` and runtime folders from trusted paths; keep operator map and registry synchronized with source/test movement.

No new cron jobs were scheduled by this audit.
