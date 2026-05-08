# Tier-1 Indexing Freshness Audit — Latest

Date/time: 2026-05-08T03:38:14-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website` under `/mnt/local-analysis/workspace-hub`.
Mode: scheduled local-only audit; no cron jobs created; legacy `.agent-os` patterns are reported only as stale residue, not recommended as routing surfaces.

## Executive Summary

Per-repo status: workspace-hub: RED, digitalmodel: YELLOW, assetutilities: YELLOW, aceengineer-website: RED.
Freshness delta: **no status-level material drift detected; timestamp and current evidence refreshed. Current scan also surfaces two missing `workspace-hub` README script references that were not listed in the previous compact report.**

The 2026-04-22 scorecard assumption of **partial readiness only** still holds. Detailed assumptions remain revised from the original snapshot: `digitalmodel` and `assetutilities` now expose current repo-local operator maps plus `docs/registry/module-routing.yaml`, while `workspace-hub` and `aceengineer-website` remain below the desired routing/index contract because canonical routing or registry surfaces are incomplete. Runtime/cache/root noise continues to weaken retrieval trust across trusted paths.

## Status Table

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | RED | missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`; broken refs: `README.md -> ./scripts/ai-review/gemini-review-manager.sh`, `README.md -> ./scripts/ai-review/review-manager.sh`, `docs/README.md -> ../.agent-os/product/mission.md`, `docs/README.md -> ../.agent-os/product/tech-stack.md`, `docs/README.md -> ../.agent-os/product/roadmap.md`, `docs/README.md -> ../.agent-os/product/decisions.md`; stale legacy refs in canonical surfaces | Create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace stale docs entry-point links; separate curated routing from raw inventory/root noise. |
| `digitalmodel` | YELLOW | broken refs: `README.md -> specs/data-needs.yaml`, `docs/maps/digitalmodel-operator-map.md -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` | Fix broken `README.md -> specs/data-needs.yaml` and stale operator-map reference; clean runtime/cache artifacts; keep map and registry synchronized. |
| `assetutilities` | YELLOW | none in required canonical surfaces | Clean runtime/cache artifacts in trusted paths; keep `docs/maps/assetutilities-operator-map.md` and `docs/registry/module-routing.yaml` synchronized. |
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
- `README.md -> ./scripts/ai-review/gemini-review-manager.sh`
- `README.md -> ./scripts/ai-review/review-manager.sh`
- `docs/README.md -> ../.agent-os/product/mission.md`
- `docs/README.md -> ../.agent-os/product/tech-stack.md`
- `docs/README.md -> ../.agent-os/product/roadmap.md`
- `docs/README.md -> ../.agent-os/product/decisions.md`
- Stale legacy `.agent-os` references detected in canonical surfaces (reported as residue only, not recommended):
  - `docs/README.md:263: ├── .agent-os/              # Agent OS configuration`
  - `docs/README.md:299: - [Mission & Vision](../.agent-os/product/mission.md)`
  - `docs/README.md:300: - [Technical Stack](../.agent-os/product/tech-stack.md)`
  - `docs/README.md:301: - [Development Roadmap](../.agent-os/product/roadmap.md)`
  - `docs/README.md:302: - [Product Decisions](../.agent-os/product/decisions.md)`

**Registry references**
- `docs/registry/module-routing.yaml`: missing
- Historical `specs/module-registry.yaml`: present; not treated as canonical for this audit.
- Registry/data-routing reference lines in inspected canonical surfaces:
  - `docs/README.md:118: | **Design code registry** | [data/design-codes/code-registry.yaml](../data/design-codes/code-registry.yaml) | ~30 engineering codes |`
  - `docs/README.md:125: - [Intelligence accessibility registry](../data/document-index/intelligence-accessibility-registry.yaml) records major intelligence surfaces and machine-reachability metadata.`

**Trusted-path backup/cache/runtime noise**
- `src/ace/__pycache__`
- `src/config/__pycache__`
- `src/digitalmodel/subsea/pipeline/free_span/__pycache__`
- `src/geometry/__pycache__`
- `src/knowledge_graph/__pycache__`
- `src/models/__pycache__`
- `src/solvers/__pycache__`
- `src/utilities/__pycache__`
- `src/workspace_hub/math/__pycache__`
- `src/workspace_hub/workstations/__pycache__`
- `src/__pycache__`
- `scripts/ai/tests/__pycache__`
- `scripts/ai/__pycache__`
- `scripts/analysis/__pycache__`
- `scripts/animations/scenes/__pycache__`
- `scripts/animations/__pycache__`
- `scripts/automation/__pycache__`
- `scripts/calculations/__pycache__`
- `scripts/ci_health/__pycache__`
- `scripts/coordination/routing/logs`
- `scripts/cron/tests/__pycache__`
- `scripts/cron/__pycache__`
- `scripts/data/dagster-eval/__pycache__`
- `scripts/data/document-index/__pycache__`
- `scripts/data/document-index/tests/__pycache__`
- ... 56 additional trusted-path noise paths omitted from this compact report.

**Root/runtime noise affecting routing trust**
- `.baseline-cache`
- `.cache`
- `.mypy_cache`
- `.nightly-results`
- `.pytest_cache`
- `.ruff_cache`
- `.swarm`
- `.sync-reports`
- `.uv-cache`
- `.venv`
- `.venv-manim`
- `.venv-test`
- `claude_smoke.log`
- `daily_gmail_action_digest_2026-04-09.md`
- `dist`
- `draft_ace_api_cfp_note.md`
- `draft_skestates_1099_followup_email.md`
- `draft_skestates_hoa_transfer_email.md`
- `draft_skestates_pest_exteriors_followup.md`
- `final_skestates_1099_followup_email.md`
- `final_skestates_hoa_transfer_email.md`
- `final_skestates_pest_exteriors_followup.md`
- `generated`
- `gmail_copy_paste_packet_2026-04-09.md`
- `gmail_operator_packet_2026-04-09.md`
- `gmail_presend_checklist_2026-04-09.md`
- `gmail_sendready_status_2026-04-09.md`
- `gmail_thread_reply_map_2026-04-09.md`
- `issue-1839-gh-comment.md`
- `issue-1839-impl.diff`
- ... 13 additional root-noise paths omitted.
- `docs/CONTENT_INDEX.md`: 30,086 lines (2,863,174 bytes); raw inventory only, not curated routing authority.

**Git status notes (pre-existing/local, first 12 lines)**
- `M config/ai-tools/agent-capability-radar.html`
- ` M docs/reports/tier-1-indexing-freshness-latest.md`

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
- Registry/data-routing reference lines in inspected canonical surfaces:
  - `AGENTS.md:12: Routing: docs/README.md | docs/maps/digitalmodel-operator-map.md | docs/registry/module-routing.yaml`
  - `README.md:56: For repo-wide current-state navigation, see [docs/maps/digitalmodel-operator-map.md](docs/maps/digitalmodel-operator-map.md). The canonical machine-readable routing registry is [do`
  - `README.md:72: - [docs/registry/module-routing.yaml](docs/registry/module-routing.yaml) -- Canonical machine-readable module routing registry`
  - `README.md:73: - [specs/data-needs.yaml](specs/data-needs.yaml) -- Data dependency lifecycle tracker`
  - `docs/README.md:15: | [docs/registry/module-routing.yaml](registry/module-routing.yaml) | Canonical machine-readable module routing registry |`
  - `docs/README.md:37: - `docs/registry/module-routing.yaml``
  - `docs/maps/digitalmodel-operator-map.md:55: - Use `docs/registry/module-routing.yaml` for machine-readable resolution.`

**Trusted-path backup/cache/runtime noise**
- `src/digitalmodel/infrastructure/base_configs/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/config/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/marine/ship/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/marine/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/pipeline_solvers/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/buckling/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/elements/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/fea/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/stress/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/utils/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/structural/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/viv/__pycache__`
- `src/digitalmodel/infrastructure/base_solvers/__pycache__`
- `src/digitalmodel/infrastructure/calculations/__pycache__`
- `src/digitalmodel/infrastructure/common/__pycache__`
- `src/digitalmodel/infrastructure/config/__pycache__`
- `src/digitalmodel/infrastructure/core/__pycache__`
- `src/digitalmodel/infrastructure/persistence/__pycache__`
- `src/digitalmodel/infrastructure/transformation/__pycache__`
- `src/digitalmodel/infrastructure/utils/visualization/__pycache__`
- `src/digitalmodel/infrastructure/utils/__pycache__`
- `src/digitalmodel/infrastructure/validation/__pycache__`
- ... 57 additional trusted-path noise paths omitted from this compact report.

**Root/runtime noise affecting routing trust**
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
- `?? .planning/quick/review-596-claude.out`
- `?? .planning/quick/review-596-codex.out`
- `?? .planning/quick/review-596-gemini.out`
- `?? .planning/quick/review-596-plan-prompt.md`
- `?? docs/plans/2026-05-07-issue-596-repo-structure-normalization.md`
- `?? scripts/review/results/2026-05-07-plan-596-claude.md`
- `?? scripts/review/results/2026-05-07-plan-596-codex.md`
- `?? scripts/review/results/2026-05-07-plan-596-final-rereview-synthesis.md`
- `?? scripts/review/results/2026-05-07-plan-596-fresh-reviewer1.md`
- `?? scripts/review/results/2026-05-07-plan-596-fresh-reviewer2.md`
- `?? scripts/review/results/2026-05-07-plan-596-fresh-reviewer3.md`
- `?? scripts/review/results/2026-05-07-plan-596-gemini.md`

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
- Registry/data-routing reference lines in inspected canonical surfaces:
  - `AGENTS.md:12: Canonical routing: docs/README.md, docs/maps/assetutilities-operator-map.md, docs/registry/module-routing.yaml, MODULE_STRUCTURE.md`
  - `README.md:16: | `docs/registry/module-routing.yaml` | Machine-readable module routing registry. |`
  - `docs/README.md:6: `docs/registry/module-routing.yaml`.`
  - `docs/README.md:14: | unit conversion | `src/assetutilities/units/`, `src/assetutilities/constants/` | `tests/unit/test_quantity.py`, `tests/unit/test_registry.py`, `tests/unit/test_constants.py` | `d`
  - `docs/README.md:29: - `docs/registry/module-routing.yaml``
  - `docs/maps/assetutilities-operator-map.md:4: human-readable companion to `docs/registry/module-routing.yaml`.`
  - `docs/registry/module-routing.yaml:10: registry: docs/registry/module-routing.yaml`

**Trusted-path backup/cache/runtime noise**
- `src/assetutilities/agent_os/cli/__pycache__`
- `src/assetutilities/agent_os/commands/cli_components/__pycache__`
- `src/assetutilities/agent_os/commands/context/__pycache__`
- `src/assetutilities/agent_os/commands/docs/__pycache__`
- `src/assetutilities/agent_os/commands/specs/__pycache__`
- `src/assetutilities/agent_os/commands/templates/__pycache__`
- `src/assetutilities/agent_os/commands/__pycache__`
- `src/assetutilities/agent_os/integration/__pycache__`
- `src/assetutilities/calculations/__pycache__`
- `src/assetutilities/common/download_data/__pycache__`
- `src/assetutilities/common/readers/__pycache__`
- `src/assetutilities/common/visualization/__pycache__`
- `src/assetutilities/common/webscraping/__pycache__`
- `src/assetutilities/common/__pycache__`
- `src/assetutilities/constants/__pycache__`
- `src/assetutilities/devtools/__pycache__`
- `src/assetutilities/modules/csv_utilities/__pycache__`
- `src/assetutilities/modules/data_exploration/__pycache__`
- `src/assetutilities/modules/excel_utilities/__pycache__`
- `src/assetutilities/modules/test_utilities/__pycache__`
- `src/assetutilities/modules/yml_utilities/__pycache__`
- `src/assetutilities/modules/zip_utilities/__pycache__`
- `src/assetutilities/modules/__pycache__`
- `src/assetutilities/tests/calculations/__pycache__`
- `src/assetutilities/tests/test_data/visualization/logs`
- ... 50 additional trusted-path noise paths omitted from this compact report.

**Root/runtime noise affecting routing trust**
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
- Clean or no git status output.

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
- Broader noncanonical docs/content still contain legacy `.agent-os` residue (not treated as current canonical routing surfaces): `docs/AI_AGENT_ORCHESTRATION.md`, `docs/modules/README.md`, `docs/modules/agent-os/enhanced-create-specs-migration-guide.md`, `docs/modules/agent-os/enhanced-create-specs-setup.md`, `docs/modules/agent-os/enhanced-create-specs-troubleshooting.md`, `docs/modules/agent-os/enhanced-create-specs-user-guide.md`.

**Registry references**
- `docs/registry/module-routing.yaml`: missing
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.
- No registry/data-routing reference lines detected in inspected canonical surfaces.

**Trusted-path backup/cache/runtime noise**
- `scripts/__pycache__`
- `tests/docs/__pycache__`
- `tests/python/__pycache__`
- `tests/__pycache__`

**Root/runtime noise affecting routing trust**
- `.pytest_cache`
- `.venv`
- `dist`
- `logs`
- `node_modules`
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

1. `workspace-hub`: Create `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; replace stale docs entry-point links; separate curated routing from raw inventory/root noise.
2. `digitalmodel`: Fix broken `README.md -> specs/data-needs.yaml` and stale operator-map reference; clean runtime/cache artifacts; keep map and registry synchronized.
3. `assetutilities`: Clean runtime/cache artifacts in trusted paths; keep `docs/maps/assetutilities-operator-map.md` and `docs/registry/module-routing.yaml` synchronized.
4. `aceengineer-website`: Add `docs/registry/module-routing.yaml`; keep docs entry/operator map free of legacy routing patterns; clean cache artifacts.

No new cron jobs were scheduled by this audit.
