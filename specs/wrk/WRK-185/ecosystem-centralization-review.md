---
title: "WRK-185 Ecosystem Centralization Review"
description: "Current-state audit and simplification plan for work items and specs across all agents"
version: "1.0"
module: governance
session:
  id: "wrk-185-review"
  agent: "codex"
review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
status: "draft"
progress: 85
created: "2026-02-17"
updated: "2026-02-17"
priority: "high"
tags: [work-queue, specs, governance, agent-contract]
links:
  spec: "specs/wrk/WRK-185/ecosystem-centralization-review.md"
  branch: ""
---

# WRK-185 Ecosystem Centralization Review

## Summary

This review checks whether work items and specs are manageable and consistent for all agents. Current state is partially centralized, but operationally inconsistent.

## Current-State Findings

### Work Items

1. Canonical queue is active and functional at `.claude/work-queue/`.
2. Current location audit reports no misplaced `WRK-*.md` files outside `.claude/work-queue/`.
3. Active WRK metadata quality is uneven:
- Missing `plan_reviewed` on many active items
- Missing `plan_approved` on many active items
- Some active items missing `provider`, `complexity`, `created_at`, or `target_repos`
4. Status-directory drift exists (for example `status: working|done|on-hold` under `pending/`).

### Specs

1. Central spec paths exist but are nearly empty:
- `specs/wrk/` has only bootstrap files plus this WRK-185 spec.
- `specs/repos/` has only bootstrap files.
2. Repo-local spec sprawl is severe:
- `digitalmodel/specs` has 5543 files
- `worldenergydata/specs` has 293 files
- many other repos still maintain local `specs/`
3. Root `specs/modules/` includes many random-name files (low discoverability, poor routing for agents).

## Why This Is Hard for Agents

1. Multiple possible sources of truth increase routing ambiguity.
2. Inconsistent frontmatter reduces automation reliability.
3. Non-deterministic naming makes retrieval and reuse weaker.
4. Policies are documented, but enforcement is incomplete.
5. Session flow had a gate gap: execution allowed medium/complex items without `plan_reviewed: true` (now fixed in wrapper guards).
6. Skills centralization is not true today: `audit_skill_symlink_policy.sh` reports 189 local child-repo `SKILL.md` files.

## Target Operating Model (Manageable for All Agents)

1. **Single queue**: only `.claude/work-queue` may contain `WRK-*.md`.
2. **Single route for route-C specs**: `specs/wrk/WRK-<id>/<slug>.md`.
3. **Single route for repo/domain design docs**: `specs/repos/<repo>/<slug>.md`.
4. **Strict naming**:
- WRK specs: `specs/wrk/WRK-<id>/<kebab-topic>.md`
- Repo specs: `specs/repos/<repo>/<kebab-topic>.md`
5. **Schema compliance gate** on active WRK items (required fields + enums).

## Improvement Plan

### Phase 1 - Hygiene Gates (Immediate)

1. Add `scripts/operations/compliance/validate_work_queue_schema.sh`:
- validates required frontmatter in pending/working/blocked.
- fails on missing fields for new/edited WRK items.
2. Add `scripts/operations/compliance/audit_wrk_location.sh`:
- reports any `WRK-*.md` outside `.claude/work-queue/`.
3. Add CI warn-mode for both checks.
4. Add `scripts/operations/compliance/audit_skill_symlink_policy.sh` and include in governance wrapper.

### Phase 2 - Path Consolidation (Pilot)

1. Pilot migration for `digitalmodel` + `worldenergydata` specs using:
- `scripts/operations/compliance/migrate_specs_to_workspace.sh --apply --repos ...`
2. Leave `specs/README.md` pointer stubs in migrated repos.
3. Update any WRK `spec_ref` to centralized paths.

### Phase 3 - Enforcement (Ecosystem)

1. Switch CI from warn-mode to blocking mode for:
- WRK location violations
- WRK schema violations
- child-repo skill files that are not propagated links
- non-centralized new specs in child repos
2. Keep exception list file for legacy frozen artifacts only.

## Acceptance Criteria

- [ ] Zero `WRK-*.md` outside `.claude/work-queue` (excluding review artifacts).
- [ ] 100% active WRK items pass schema validation.
- [ ] 100% child-repo `SKILL.md` files are propagated links (no local skill ownership in child repos).
- [ ] No new specs added under child repo `specs/` paths.
- [ ] Pilot repos fully mapped to `specs/repos/<repo>/` with pointer stubs.
- [ ] CI checks exist and are documented for all agents.

## Commands

```bash
scripts/operations/compliance/audit_contract_drift.sh
scripts/operations/compliance/validate_agent_contract.sh
scripts/operations/compliance/check_governance.sh --mode warn --scope all
scripts/operations/compliance/audit_skill_symlink_policy.sh --mode warn
scripts/operations/compliance/migrate_specs_to_workspace.sh --repos digitalmodel,worldenergydata
```

## Execution Notes (2026-02-17)

1. Governance normalization executed:
- `scripts/operations/compliance/normalize_work_queue_metadata.sh --mode apply --relocate true`
2. Governance gate result after normalization:
- `check_governance.sh --mode gate --scope changed` => schema `0`, wrk-location `0`, skills-symlink `0`
3. Cross-review rerun:
- Claude: `REQUEST_CHANGES` (`scripts/review/results/20260217T193049Z-ecosystem-centralization-review.md-plan-claude.md`)
- Codex: `REQUEST_CHANGES` (`scripts/review/results/20260217T193049Z-ecosystem-centralization-review.md-plan-codex.md`)
- Gemini: `NO_OUTPUT/TIMEOUT` during run (`scripts/review/results/20260217T193306Z-ecosystem-centralization-review.md-plan-gemini.md`)
