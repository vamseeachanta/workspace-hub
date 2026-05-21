# Issue #2767 Plan — chore(data-layout): unionise preexisting data folders with content dedup

## Metadata
- **Issue:** #2767
- **Layer:** Data layer disposition
- **Status target:** `status:plan-review` after adversarial review; implementation requires explicit user approval and `status:plan-approved`.
- **Prepared:** 2026-05-21
- **Execution class:** parallel-worktree after approval

## Resource Intel
- GitHub issue #2767: `chore(data-layout): unionise preexisting data folders with content dedup`.
- Parent/dependency chain: #2767 depends on #2731 data-repo contracts and #2732 mount taxonomy; #2769 is the high-pressure ACMA child case.
- Workspace hard gates: issue → resource intel → plan → adversarial review → `status:plan-review` → USER APPROVES → `status:plan-approved` → TDD implementation → close.
- User update: private `llm-wiki` posture allows fuller ACMA/client data capture with key-information abstractions; public-safe constraints still apply to public repos/docs.

## Problem
Multiple preexisting-before-repo-move folders exist under `/mnt/ace`; unreviewed movement/deletion risks data loss, but ignoring them preserves disk pressure and ambiguity.

## Scope
### Owned paths
- Inventory scripts/manifests under repo-controlled docs/scripts
- Dry-run dedup/union reports
- Disposition decision records

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
- Tests for inventory parser/classifier using synthetic folder trees.
- Tests for dedup decision matrix generation with keep/archive/delete/merge states.
- Dry-run command tests that never mutate source paths.

## Acceptance Criteria
- Produces canonical inventory of preexisting folders and equivalence classes.
- Provides reviewed disposition plan before any data movement.
- Every proposed destructive action has backup, rollback, and verification evidence.

## Adversarial Review Hardening
- Split execution into Phase A metadata-only discovery and Phase B policy-backed disposition. Phase B is blocked on #2731/#2732 contracts.
- Phase A may produce only non-destructive recommendation classes. `delete`, `archive`, and `merge` are proposed dispositions in reports only, never executed actions in this issue.
- Repo-tracked summaries must be redacted/public-safe: no literal client names, raw `/mnt/ace/...` paths, sensitive filenames, reconstructable directory trees, or correlatable evidence unless explicitly approved.
- Full/private evidence artifacts must be stored separately from repo-tracked summaries. Repo summaries cite redacted evidence IDs and source posture/classification.
- No keep/archive/delete/merge recommendation from names/paths/size alone. Require content hashes or explicit duplicate-class evidence, with symlink/hardlink/bind-mount handling.
- Inventory jobs require mount-health guardrails: bounded reads, timeouts, low-priority I/O where appropriate, disk pressure checks, and no writes to the pressured mount.
- Tests must cover exact duplicate trees, partial overlaps, unique-only folders, empty dirs, inaccessible paths, redaction behavior, symlinks/hardlinks, and dry-run guarantee that no filesystem mutation calls occur.
- Before RED starts, execution preflight must verify live `status:plan-approved` and local `.planning/plan-approved/2767.md`.

## Rollback
- Revert the implementation commit(s) on the issue branch/main.
- Restore prior schema/config/docs from git history.
- For any approved future data operation, require a pre-op manifest and rollback/copy-back command before execution.

## Adversarial Review Targets
- Verify dependency order is enforceable and does not duplicate adjacent issues.
- Check that tests fail before implementation and prove the artifact contract.
- Check no data-destruction path is hidden in documentation-only wording.
- Check public/private boundary language is consistent with current private llm-wiki posture.
