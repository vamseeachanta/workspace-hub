# Issue #2769 Plan — chore(data-disposition): plan disposition of /mnt/ace/acma-projects.preexisting-* 1.8 TB pre-move backup

## Metadata
- **Issue:** #2769
- **Layer:** Data layer urgent disposition
- **Status target:** `status:plan-review` after adversarial review; implementation requires explicit user approval and `status:plan-approved`.
- **Prepared:** 2026-05-21
- **Execution class:** parallel-worktree after approval

## Resource Intel
- GitHub issue #2769: `chore(data-disposition): plan disposition of /mnt/ace/acma-projects.preexisting-* 1.8 TB pre-move backup`.
- Parent/dependency chain: #2769 is a child/special case of #2767 and adjacent to completed #2745 freeze; depends on #2731/#2732 for final location policy.
- Workspace hard gates: issue → resource intel → plan → adversarial review → `status:plan-review` → USER APPROVES → `status:plan-approved` → TDD implementation → close.
- User update: private `llm-wiki` posture allows fuller ACMA/client data capture with key-information abstractions; public-safe constraints still apply to public repos/docs.

## Problem
The ACMA pre-move backup is reportedly ~1.8 TB on a 95%-full mount. It needs focused disposition planning before any storage-changing operation.

## Scope
### Owned paths
- ACMA backup inventory report
- Non-destructive comparison manifest
- Approved disposition runbook, if later authorized

### Read-only paths
- `docs/standards/`
- `docs/plans/`
- Related issue comments and existing reports under `docs/reports/` and `scripts/review/results/`

### Forbidden paths / operations
- No destructive `/mnt/ace` move/delete/compression until an approved execution issue explicitly authorizes the exact action.
- No secrets, credentials, gateway tokens, or local `.env` writes.
- No `status:plan-approved` label application by an agent.

## Implementation Strategy After Approval
1. Re-read issue, plan, comments, and current branch state.
2. Create/use isolated worktree under `/mnt/local-analysis/agent-worktrees/`.
3. RED: add failing tests/fixtures/checks for the target behavior.
4. GREEN: implement the smallest repo-side contract change.
5. REFACTOR: tighten docs/schema/CLI behavior without widening scope.
6. Verify with targeted tests and relevant validators.
7. Post issue comment with commit SHA, tests, evidence, blockers, and closeout recommendation.

## TDD / Verification Plan
- Tests for backup-vs-active comparison manifest parsing.
- Tests for disk-pressure threshold gating and “no destructive op without approval”.
- Dry-run verification commands captured as artifacts.

## Acceptance Criteria
- Confirms whether the 1.8 TB backup is redundant, unique, or partially unique.
- Recommends archive/dedup/delete/retain with evidence and risk rating.
- Does not compress/move/delete data until exact command is approved.

## Adversarial Review Hardening
- Split into metadata-only discovery first; final archive/dedup/delete recommendation is blocked on #2767 shared inventory contract plus #2731/#2732 location/mount policy.
- Preflight health gate is mandatory before any deep scan: disk usage, mount responsiveness, load, timeout settings, bounded-read strategy, and target comparison path must be captured.
- Forbid unbounded recursive scans as the first step. Use staged sampling/manifest strategy with low-priority I/O and abort thresholds for a 95%-full mount.
- Use a two-tier evidence model: private/full literal path/file evidence vs repo-safe redacted summary. Repo-tracked artifacts cite redacted evidence IDs, not literal backup contents/paths.
- Redundancy classifications must be deterministic: counts, fingerprint basis, hash/sample-hash thresholds, unique-only set policy, and inaccessible-file handling.
- Future destructive recommendations must include exact command, rollback source, verification command, risk rating, and explicit user signoff checkpoint. The plan does not pre-authorize compression, move, or delete.
- Tests must cover fully redundant backup, partially unique backup, inaccessible active tree, high/low disk-pressure gating, redaction of dry-run artifacts, and approval gate preventing destructive command execution.
- Before RED starts, execution preflight must verify live `status:plan-approved` and local `.planning/plan-approved/2769.md`.

## Rollback
- Revert the implementation commit(s) on the issue branch/main.
- Restore prior schema/config/docs from git history.
- For any approved future data operation, require a pre-op manifest and rollback/copy-back command before execution.

## Adversarial Review Targets
- Verify dependency order is enforceable and does not duplicate adjacent issues.
- Check that tests fail before implementation and prove the artifact contract.
- Check no data-destruction path is hidden in documentation-only wording.
- Check public/private boundary language is consistent with current private llm-wiki posture.
