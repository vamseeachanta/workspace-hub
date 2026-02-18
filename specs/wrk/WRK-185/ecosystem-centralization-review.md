---
title: "WRK-185 Ecosystem Centralization Review"
description: "Current-state audit and simplification plan for work items and specs across all agents"
version: "1.1"
module: governance
session:
  id: "wrk-185-review"
  agent: "codex"
review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
status: "in-review"
progress: 92
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
6. Skills centralization previously drifted and is now corrected: `audit_skill_symlink_policy.sh` currently reports `issue_count=0`.

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

1. Validate and integrate `scripts/operations/compliance/validate_work_queue_schema.sh`:
- validates required frontmatter in pending/working/blocked.
- fails on missing fields for new/edited WRK items.
2. Validate and integrate `scripts/operations/compliance/audit_wrk_location.sh`:
- reports any `WRK-*.md` outside `.claude/work-queue/`.
3. Add CI warn-mode for both checks.
4. Validate and integrate `scripts/operations/compliance/audit_skill_symlink_policy.sh` and include in governance wrapper.
5. Remediate existing status-directory drift using:
- `scripts/operations/compliance/normalize_work_queue_metadata.sh --mode apply --relocate true`

### Phase 2 - Path Consolidation (Wave-Based)

1. **Wave 1 (small corpus): `worldenergydata` only**
- Dry-run first:
  - `scripts/operations/compliance/migrate_specs_to_workspace.sh --repos worldenergydata`
- Capture migration manifest:
- source path, destination path, file count, full-file checksum parity.
- Apply only after approval:
  - `scripts/operations/compliance/migrate_specs_to_workspace.sh --apply --repos worldenergydata`
2. **Wave 2 (large corpus): `digitalmodel`**
- Run only after Wave 1 passes all promotion gates.
- Split execution into bounded batches by subtree, not one-shot 5k+ move.
- Batch contract: max 500 files per batch, one commit per batch, mandatory checkpoint before next batch.
3. Leave `specs/README.md` pointer stubs in migrated repos.
4. Update affected WRK `spec_ref` values to centralized paths.
5. Post-migration integrity checks:
- `rg` scan for broken local spec references.
- parity check (source count == destination count for scope).
- no net-new files under child repo `specs/` except pointer README.

### Phase 3 - Enforcement (Ecosystem)

1. Switch CI from warn-mode to blocking mode for:
- WRK location violations
- WRK schema violations
- child-repo skill files that are not propagated links
- non-centralized new specs in child repos
2. Keep exception list file for legacy frozen artifacts only.
3. Exception list governance:
- Location: `config/governance/spec-location-exceptions.yaml`
- Required fields: `path`, `owner`, `reason`, `expires_at`, `approved_by`
- Expired exceptions fail governance checks.

## Dependencies and Ownership

| Area | Owner | Inputs | Output |
|------|-------|--------|--------|
| WRK schema gate | workspace-hub | `.claude/work-queue/*` | `/tmp/validate_work_queue_schema.json` |
| WRK location gate | workspace-hub | repo filesystem | `/tmp/audit_wrk_location.json` |
| Skills link-only gate | workspace-hub | child `.claude/skills` trees | `/tmp/audit_skill_symlink_policy.json` |
| Spec location gate | workspace-hub | child `specs/` trees | `/tmp/audit_spec_location.json` |
| Spec migration | repo owner + workspace-hub | selected repo `specs/` | `specs/repos/<repo>/...` + pointer README |

## Runtime Prerequisites

1. Shell + tooling baseline:
- `bash`, `find`, `cp`, `mv`, `rm`, `awk`, `sed`, `rg`, `jq`, `python3`
2. CI baseline:
- Linux runner with git history available (`fetch-depth: 0`)
3. Governance config artifacts:
- `config/governance/wrk-schema.yaml`
- `config/governance/spec-location-exceptions.yaml`

## Script Interface Contracts

1. `validate_work_queue_schema.sh`
- Inputs: `--mode`, `--scope`, `--base-ref`, `--report`
- Exit: `0` pass, non-zero when `--mode gate` and issues found
- Output JSON: `{mode,scope,base_ref,checked_files,issue_count,issues[]}`
2. `audit_wrk_location.sh`
- Inputs: `--mode`, `--report`
- Exit: `0` pass, non-zero when `--mode gate` and misplaced WRK exists
- Output JSON: `{issue_count,issues[]}`
3. `audit_skill_symlink_policy.sh`
- Inputs: `--mode`, `--report`
- Exit: `0` pass, non-zero when `--mode gate` and non-link skills exist
- Output JSON: `{checked_repos,issue_count,issues[]}`
4. `audit_spec_location.sh`
- Inputs: `--mode`, `--scope`, `--base-ref`, `--report`
- Exit: `0` pass, non-zero when `--mode gate` and violations found
- Output JSON: `{issue_count,issues[]}`
5. `check_governance.sh`
- Inputs: `--mode`, `--scope`, `--base-ref`
- Exit: `0` only when all child checks pass; aggregates failures instead of early exit

## Migration Verification Contract

1. Dry-run and apply both produce a deterministic manifest under `reports/compliance/`:
- `batch_id`, `repo`, `source`, `destination`, `checksum`, `status`
2. Apply is valid only when:
- source/destination counts match,
- checksums match for all moved files in batch,
- no collisions reported.
3. Rollback command for each batch is documented with commit SHA in the manifest.

## Rollback and Recovery

1. Every migration wave runs on a dedicated branch.
2. Dry-run manifest is required before apply.
3. Apply rollback trigger conditions:
- broken references detected in post-check,
- destination count mismatch,
- governance gate regression.
4. Rollback procedure:
- revert migration commit for wave branch,
- restore from pre-apply git state,
- record incident in WRK update before retry.

## Promotion Gates (Warn -> Gate)

Move from `warn` to `gate` for broader scope only when all are true:

1. `check_governance.sh --mode gate --scope changed` passes for 5 consecutive CI runs.
2. Wave 1 migration completes with parity and no broken-reference findings.
3. Exception file has valid owners and non-expired dates.
4. Cross-review verdict is at least `MINOR` from two providers, no `MAJOR` unresolved.

## Cross-Review Convergence Rule

1. Maintain `specs/wrk/WRK-185/review-delta.md` with:
- prior finding,
- exact spec change,
- status (`open|resolved|deferred`).
2. Re-run review only after all open P1 findings are marked resolved.
3. Promotion gate considers normalized verdicts (`APPROVE|MINOR|MAJOR|NO_OUTPUT|ERROR`) rather than raw prose.

## Acceptance Criteria

- [ ] Zero `WRK-*.md` outside `.claude/work-queue` (excluding review artifacts).
- [ ] 100% active WRK items pass schema validation.
- [ ] 100% child-repo `SKILL.md` files are propagated links (no local skill ownership in child repos).
- [ ] No new specs added under child repo `specs/` paths (except approved exceptions).
- [ ] Wave 1 (`worldenergydata`) migrated with manifest + pointer stub + parity checks.
- [ ] Wave 2 (`digitalmodel`) migration plan approved as batched execution (not one-shot).
- [ ] `check_governance.sh --mode gate --scope changed` passes in CI with zero issues.
- [ ] Exception policy file exists with owner/expiry enforcement.
- [x] Governance artifacts created: `wrk-schema.yaml` and `spec-location-exceptions.yaml`.

## Commands

```bash
scripts/operations/compliance/audit_contract_drift.sh
scripts/operations/compliance/validate_agent_contract.sh
scripts/operations/compliance/check_governance.sh --mode warn --scope all
scripts/operations/compliance/check_governance.sh --mode gate --scope changed
scripts/operations/compliance/audit_skill_symlink_policy.sh --mode warn
scripts/operations/compliance/migrate_specs_to_workspace.sh --repos worldenergydata
scripts/operations/compliance/migrate_specs_to_workspace.sh --apply --repos worldenergydata
cat config/governance/wrk-schema.yaml
cat config/governance/spec-location-exceptions.yaml
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
4. Governance hardening complete for changed scope:
- `check_governance.sh --mode gate --scope changed` => `issue_count=0` for schema, wrk location, skills symlink, and spec location.
