# Tier-1 Indexing Freshness Audit — Latest

Date/time: 2026-05-06T03:33:30-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website` under `/mnt/local-analysis/workspace-hub`.
Mode: scheduled local-only audit; no cron jobs created; legacy `.agent-os` patterns are reported only as stale residue, not recommended as routing surfaces.

## Executive Summary

Per-repo status: workspace-hub: RED, digitalmodel: YELLOW, assetutilities: YELLOW, aceengineer-website: RED.
Freshness delta: **material drift detected**. The timestamp and current evidence were refreshed. Compared with the latest recalled prior audit, the major status colors are unchanged, but `aceengineer-website` no longer shows stale legacy product-doc references in the inspected canonical surfaces; legacy residue still exists elsewhere in broader docs/content.

The 2026-04-22 scorecard assumption of **partial readiness only** still holds, but the detailed assumptions remain revised: `digitalmodel` and `assetutilities` now have current repo-local operator maps and `docs/registry/module-routing.yaml`; `workspace-hub` and `aceengineer-website` remain the main red surfaces because current canonical routing/registry surfaces are still incomplete.

## Status Table

| Repo | Status | Exact broken or missing surfaces | Concise next actions |
|---|---:|---|---|
| `workspace-hub` | RED | missing: `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`; broken links: `docs/README.md -> ../.agent-os/product/decisions.md`, `docs/README.md -> ../.agent-os/product/mission.md`, `docs/README.md -> ../.agent-os/product/roadmap.md`, `docs/README.md -> ../.agent-os/product/tech-stack.md`; stale legacy refs in canonical surfaces | Create/refresh repo-local operator map and canonical registry; replace stale docs entry-point links; reduce root/index/cache noise. |
| `digitalmodel` | YELLOW | broken links: `digitalmodel/README.md -> specs/data-needs.yaml` | Fix README broken registry/data-needs link; clean runtime cache from trusted paths; review untracked test artifact. |
| `assetutilities` | YELLOW | none in required canonical surfaces | Clean runtime/cache artifacts under trusted paths and keep operator map + module-routing registry synchronized. |
| `aceengineer-website` | RED | missing: `docs/registry/module-routing.yaml` | Add canonical module-routing registry; keep docs entry/operator map free of legacy routing patterns; clean cache artifacts. |

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
- Stale legacy product-doc references detected (reported as residue only):
  - `docs/README.md:263: ├── .agent-os/              # Agent OS configuration`
  - `docs/README.md:299: - [Mission & Vision](../.agent-os/product/mission.md)`
  - `docs/README.md:300: - [Technical Stack](../.agent-os/product/tech-stack.md)`
  - `docs/README.md:301: - [Development Roadmap](../.agent-os/product/roadmap.md)`
  - `docs/README.md:302: - [Product Decisions](../.agent-os/product/decisions.md)`

**Registry references**
- `docs/registry/module-routing.yaml`: missing
- Historical `specs/module-registry.yaml`: present; not treated as canonical for this audit.

**Trusted-path noise**
- `scripts/ai/__pycache__`
- `scripts/ai/tests/__pycache__`
- `scripts/analysis/__pycache__`
- `scripts/animations/__pycache__`
- `scripts/animations/scenes/__pycache__`
- `scripts/automation/__pycache__`
- `scripts/calculations/__pycache__`
- `scripts/ci_health/__pycache__`
- `scripts/cron/__pycache__`
- `scripts/cron/tests/__pycache__`
- `scripts/data/dagster-eval/__pycache__`
- `scripts/data/doc_intelligence/__pycache__`
- `scripts/data/doc_intelligence/parsers/__pycache__`
- `scripts/data/doc_intelligence/promoters/__pycache__`
- `scripts/data/doc_intelligence/tests/__pycache__`
- `scripts/data/document-index/__pycache__`
- `scripts/data/document-index/tests/__pycache__`
- `scripts/data/llm-wiki/__pycache__`
- `scripts/data/llm-wiki/tests/__pycache__`
- `src/__pycache__`
- ... 61 additional noise paths omitted from this compact report.

**Root/runtime/index noise**
- `.baseline-cache`
- `.benchmarks`
- `.cache`
- `.mypy_cache`
- `.pytest_cache`
- `.ruff_cache`
- `.swarm`
- `.sync-reports`
- `.worktrees`
- `MEMORY.md`
- `ace_cfp_sending_kit_2026-04-09.md`
- `daily_gmail_action_digest_2026-04-09.md`
- `dist`
- `docs-reorg-assessment.md`
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
- ... 14 additional root-noise paths omitted.

**Git status notes (pre-existing/local)**
- `M config/ai-tools/agent-capability-radar.html`
- ` M knowledge/wikis/asset-management/wiki/standards/api-579-1.md`
- ` M knowledge/wikis/asset-management/wiki/standards/dnv-rp-g101.md`
- ` M knowledge/wikis/asset-management/wiki/standards/iso-55001.md`
- ` M knowledge/wikis/cross-links.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/api-rp-16q.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/api-rp-17b.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-b401.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f103.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f105.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-h103.md`
- ` M knowledge/wikis/engineering-standards/wiki/standards/iso-19900.md`

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
- `digitalmodel/README.md -> specs/data-needs.yaml`

**Registry references**
- `docs/registry/module-routing.yaml`: present
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.

**Trusted-path noise**
- `digitalmodel/src/digitalmodel/infrastructure/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_configs/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/benchmarks/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/config/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/fatigue/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/marine/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/marine/ship/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/pipeline_solvers/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/structural/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/structural/buckling/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/structural/elements/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/structural/fea/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/structural/stress/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/structural/utils/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/base_solvers/viv/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/calculations/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/common/__pycache__`
- `digitalmodel/src/digitalmodel/infrastructure/config/__pycache__`
- ... 62 additional noise paths omitted from this compact report.

**Root/runtime/index noise**
- `digitalmodel/.benchmarks`
- `digitalmodel/.mypy_cache`
- `digitalmodel/.pytest_cache`
- `digitalmodel/.ruff_cache`
- `digitalmodel/.swarm`
- `digitalmodel/build`
- `digitalmodel/dist`
- `digitalmodel/logs`
- `digitalmodel/reports`

**Git status notes (pre-existing/local)**
- `?? .planning/plan-approved/509.md`
- `?? .planning/plan-approved/512.md`
- `?? .planning/plan-approved/514.md`
- `?? .planning/plan-approved/517.md`
- `?? .planning/plan-approved/518.md`
- `?? .planning/plan-approved/519.md`
- `?? .planning/plan-approved/522.md`
- `?? .planning/plan-approved/523.md`
- `?? .planning/plan-approved/529.md`
- `?? .planning/plan-approved/530.md`
- `?? .planning/plan-approved/531.md`
- `?? .planning/plan-approved/534.md`
- ... 8 additional status lines omitted.

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
- No broken local Markdown links detected in required canonical surfaces.

**Registry references**
- `docs/registry/module-routing.yaml`: present
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.

**Trusted-path noise**
- `assetutilities/src/assetutilities/__pycache__`
- `assetutilities/src/assetutilities/agent_os/cli/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/cli_components/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/context/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/docs/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/specs/__pycache__`
- `assetutilities/src/assetutilities/agent_os/commands/templates/__pycache__`
- `assetutilities/src/assetutilities/agent_os/integration/__pycache__`
- `assetutilities/src/assetutilities/calculations/__pycache__`
- `assetutilities/src/assetutilities/common/__pycache__`
- `assetutilities/src/assetutilities/common/download_data/__pycache__`
- `assetutilities/src/assetutilities/common/readers/__pycache__`
- `assetutilities/src/assetutilities/common/visualization/__pycache__`
- `assetutilities/src/assetutilities/common/webscraping/__pycache__`
- `assetutilities/src/assetutilities/constants/__pycache__`
- `assetutilities/src/assetutilities/devtools/__pycache__`
- `assetutilities/src/assetutilities/modules/__pycache__`
- `assetutilities/src/assetutilities/modules/csv_utilities/__pycache__`
- `assetutilities/src/assetutilities/modules/data_exploration/__pycache__`
- ... 40 additional noise paths omitted from this compact report.

**Root/runtime/index noise**
- `assetutilities/.agent-runtime`
- `assetutilities/.ai`
- `assetutilities/.benchmarks`
- `assetutilities/.command-backups`
- `assetutilities/.common`
- `assetutilities/.common-commands`
- `assetutilities/.mypy_cache`
- `assetutilities/.pytest_cache`
- `assetutilities/.ruff_cache`
- `assetutilities/.slash-commands`
- `assetutilities/.swarm`
- `assetutilities/.sync-reports`
- `assetutilities/build`
- `assetutilities/dist`
- `assetutilities/logs`
- `assetutilities/reports`

**Git status notes (pre-existing/local)**
- `?? docs/plans/2026-05-05-issue-19-monthly-branch-and-multiuser-merge.md`
- `?? docs/plans/2026-05-05-issue-28-loguru-migration.md`
- `?? docs/plans/2026-05-05-issue-29-engine-registry-pattern.md`
- `?? docs/plans/2026-05-05-issue-30-ai-agents-config.md`
- `?? docs/plans/2026-05-05-issue-31-acma-source-files-sync-vs-copy.md`
- `?? docs/plans/2026-05-05-issue-32-environment-poetry-vs-uv.md`
- `?? docs/plans/2026-05-05-issue-33-consolidate-data-linux.md`
- `?? docs/plans/2026-05-05-issue-35-consolidate-repos.md`
- `?? docs/plans/2026-05-05-issue-36-consolidate-hardware.md`
- `?? docs/plans/2026-05-05-issue-37-scalability-process-people.md`
- `?? docs/plans/2026-05-05-issue-38-knowledge-management-obsidian.md`
- `?? docs/plans/2026-05-05-issue-39-email-cleanup.md`
- ... 8 additional status lines omitted.

### aceengineer-website — RED

**Present canonical surfaces**
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/maps/aceengineer-website-operator-map.md`

**Missing canonical surfaces**
- `docs/registry/module-routing.yaml`

**Broken/stale references in inspected canonical surfaces**
- No broken local Markdown links detected in required canonical surfaces.
- Broader noncanonical docs/content still contain legacy `.agent-os` residue (examples: `docs/AI_AGENT_ORCHESTRATION.md`, `docs/modules/README.md`, `content/blog/PHASE_2_TIER_1_COVERAGE_EXPANSION.md`), but those are not treated as current canonical routing surfaces.

**Registry references**
- `docs/registry/module-routing.yaml`: missing
- Historical `specs/module-registry.yaml`: not present; not treated as canonical for this audit.

**Trusted-path noise**
- `aceengineer-website/scripts/__pycache__`
- `aceengineer-website/tests/__pycache__`
- `aceengineer-website/tests/python/__pycache__`

**Root/runtime/index noise**
- `aceengineer-website/.benchmarks`
- `aceengineer-website/.pytest_cache`
- `aceengineer-website/dist`
- `aceengineer-website/logs`
- `aceengineer-website/reports`

## 2026-04-22 Scorecard Assumption Check

- Baseline verdict still valid: **partial readiness only**; do not treat tier-1 routing as fully green.
- Detailed assumptions need the same revision noted in the latest prior audit: `digitalmodel` and `assetutilities` are stronger than the original 2026-04-22 snapshot because they now expose repo-wide `docs/maps/<repo>-operator-map.md` and `docs/registry/module-routing.yaml`.
- `workspace-hub` remains below the desired control-plane standard: missing repo-local operator map and canonical module-routing registry, with root/index/runtime noise that weakens routing trust.
- `aceengineer-website` remains below the desired durable routing standard: operator map exists, but canonical registry is absent; no stale legacy product-doc links were detected in the inspected canonical surfaces during this run.
- Runtime/cache noise across trusted paths remains a recurring hygiene issue; it does not change repo mission assumptions but does weaken retrieval trust.

## Concise Next Actions

1. `workspace-hub`: add `docs/maps/workspace-hub-operator-map.md` and `docs/registry/module-routing.yaml`; then replace stale docs entry-point links and split curated routing from raw inventory/noise.
2. `aceengineer-website`: add `docs/registry/module-routing.yaml`; keep `docs/README.md` and `docs/maps/aceengineer-website-operator-map.md` free of legacy routing patterns, and clean broader noncanonical legacy residue opportunistically.
3. `digitalmodel`: fix the broken `README.md` local link(s), clean `__pycache__` from docs/src/scripts/tests, and decide whether the untracked naval-architecture test belongs in the repo.
4. `assetutilities`: clean `__pycache__` and other runtime folders from trusted paths; keep `docs/maps/assetutilities-operator-map.md` and `docs/registry/module-routing.yaml` in sync with source/test movement.

No new cron jobs were scheduled by this audit.

