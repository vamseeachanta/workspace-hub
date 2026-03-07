# WRK-1017 Stage 6 Compact Review Bundle

Authoritative source: `.claude/work-queue/pending/WRK-1017.md`
Purpose: compact Stage 6 review proxy for provider-constrained plan review. This bundle summarizes the active plan contract and rollout mechanics without historical revision detail.
Non-authoritative: yes. The authoritative plan remains the WRK file above.
Review rule: this compact bundle is a review accelerator, not a replacement for the authoritative WRK. Stage 6 sign-off remains against the authoritative WRK plus `.claude/work-queue/assets/WRK-1017/ac-test-matrix.md`.

## Current Status
- Stage 5 baseline is approved and published.
- Stage 6 cross-review is in progress and may continue autonomously.
- Stage 7 is the next required human checkpoint.
- If Phase 1B hard-gate rollout clears before Phase 2 packaging is finished, the WRK remains open until Stage 7 packaging is complete.

## Locked Decisions
- Preserve the full Stage 5 target flow:
  - create one common draft
  - user approves common draft in a live human-in-the-loop review
  - independent Claude, Codex, and Gemini planning passes
  - combine and rate model plans
  - user approves combined plan
- Reviews remain human-in-the-loop; do not automate the review conversation or approval capture.
- Assistive terminal orchestration is allowed after common-draft approval, but review remains manual.
- Stage 6 may reconcile and rerun autonomously until Stage 7.
- Stage 7 must show on screen the changes made since the approved Stage 5 baseline.

## Core Problem
Stage 5 is supposed to be a blocking interactive agent-user plan review. In practice, agents can reach Stage 6 without machine-checked Stage 5 evidence. The fix must make the Stage 5 gate executable and fail closed across the official workflow entrypoints.

## Core Scope
Files in scope:
- workflow contracts:
  - `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
  - `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
  - `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- runtime/checker path:
  - `scripts/work-queue/verify-gate-evidence.py`
  - `scripts/work-queue/stage5-gate-config.yaml`
  - `scripts/work-queue/bootstrap-stage5-gate.sh`
  - `scripts/work-queue/backfill-stage-evidence.py`
  - `scripts/work-queue/update-stage-evidence.py`
  - `scripts/work-queue/log-user-review-browser-open.sh`
  - `scripts/work-queue/log-user-review-publish.sh`
  - `scripts/agents/plan.sh`
  - `scripts/agents/lib/workflow-guards.sh`
  - `scripts/review/cross-review.sh`
  - `scripts/work-queue/claim-item.sh`
  - `scripts/work-queue/close-item.sh`
- templates/evidence contracts:
  - `specs/templates/stage5-evidence-contract.yaml`
  - `specs/templates/stage-evidence-template.yaml`
  - `specs/templates/user-review-common-draft-template.yaml`
  - `specs/templates/user-review-plan-draft-template.yaml`
  - `specs/templates/user-review-browser-open-template.yaml`
  - `specs/templates/user-review-publish-template.yaml`
  - `specs/templates/stage5-migration-exemption-template.yaml`
  - `specs/templates/plan-quality-eval-template.yaml`
- renderer/test support:
  - `scripts/work-queue/generate-html-review.py`
  - `tests/unit/test_verify_gate_evidence.py`
  - `tests/unit/test_generate_html_review.py`
  - `scripts/agents/tests/test-plan-gate.sh`
  - `tests/work-queue/test-lifecycle-gates.sh`
  - `scripts/work-queue/tests/test-user-review-evidence-writers.sh`
  - `.github/workflows/baseline-check.yml`
  - `scripts/hooks/pre-commit`

## Evidence Model
Required Stage 5 artifact set:
- `user-review-common-draft.yaml`
- `user-review-plan-draft.yaml`
- `user-review-browser-open.yaml`
- `user-review-publish.yaml`

Required identity/provenance:
- `user-review-common-draft.yaml`:
  - `wrk_id`
  - `stage`
  - `review_checkpoint`
  - `review_cycle_id`
  - `draft_commit`
  - `approval_decision`
  - `reviewed_at`
  - `reviewed_by`
  - `capture_method`
  - `generated_at_commit`
  - `generated_by_script` iff `capture_method: script`
- `user-review-plan-draft.yaml`:
  - `wrk_id`
  - `stage`
  - `review_checkpoint`
  - `review_cycle_id`
  - `approval_decision`
  - `approved_draft_commit`
  - `reviewed_at`
  - `reviewed_by`
  - `capture_method`
  - `generated_at_commit`
  - `generated_by_script` iff `capture_method: script`
  - degraded mode also requires `approved_by`, `approval_scope`, `missing_providers`
- `user-review-browser-open.yaml` events:
  - `wrk_id` (required; checker validates cross-artifact equality for replay-abuse detection)
  - `stage`
  - `review_checkpoint`
  - `review_cycle_id`
  - `html_ref`
  - `opened_at`
  - `reviewer`
  - `opened_in_default_browser`
  - `generated_by_script`
  - `generated_at_commit`
- `user-review-publish.yaml` events:
  - `wrk_id` (required; checker validates cross-artifact equality for replay-abuse detection)
  - `stage`
  - `review_checkpoint`
  - `review_cycle_id`
  - `documents`
  - `published_at`
  - `reviewer`
  - `generated_by_script`
  - `generated_at_commit`
  - `published_draft_commit` (canonical field; legacy `commit` is accepted as bootstrap/backfill input only and normalized to `published_draft_commit` during validated backfill writes — guarded activation rejects artifacts that still carry only `commit` without backfill normalization)

Decision-table semantics:
- canonical enum values are `approve_as_is`, `revise_and_rerun`, `reject`, `no_response`
- common-draft `revise_and_rerun` loops from the common-draft checkpoint
- combined-plan `revise_and_rerun` loops from combine/rating, not from a forced new three-provider pass
- `reject` blocks the current checkpoint and does not auto-restart planning
- `no_response` remains blocked and is never inferred as approval
- `review_cycle_id` must match across all Stage 5 evidence for the same review attempt; mixed-cycle artifacts fail closed

Degraded-mode trigger:
- one explicit provider launch/auth/quota failure triggers degraded-mode eligibility immediately
- a bounded no-response timeout of `60s` from provider launch to first response token or structured error also triggers degraded-mode eligibility
- degraded mode still requires explicit user approval captured in machine-checkable evidence

Stage 5 checkpoint identity:
- `review_checkpoint: common_draft`
- `review_checkpoint: combined_plan`

Published baseline authority:
- authoritative Stage 5 baseline = last `plan_draft + combined_plan` publish event in `user-review-publish.yaml`
- `user-review-plan-draft.yaml` must record that same commit in `approved_draft_commit`
- mismatch is fail-closed
- authoritative combined-plan publish event discriminator = `stage: plan_draft` plus `review_checkpoint: combined_plan`

## Trust Model
Approval artifacts may be human-authored, but only through controlled live-review capture.

Allowed manual capture path:
- orchestrator-managed live review only
- created from canonical template
- saved to canonical evidence path
- `capture_method: manual_live_review`
- must match browser-open evidence for the same `review_checkpoint`
- must match the approved-and-published draft commit in `user-review-publish.yaml`

Not allowed:
- ad hoc after-the-fact YAML edits counted as valid approval evidence
- free-text notes substituting for required fields
- local post-publish YAML edits counting until a new approved publish exists

## Canonical Ownership And Precedence
- `specs/templates/stage5-evidence-contract.yaml` owns cross-artifact schema/version invariants.
- per-artifact templates own field-level schema.
- `scripts/work-queue/verify-gate-evidence.py` owns executable predicate semantics and state precedence.
- `scripts/work-queue/stage5-gate-config.yaml` owns activation/cutover policy only.
- `scripts/work-queue/stage5-gate-config.yaml` also owns the central operational guard settings:
  - `checker_timeout_seconds`
  - `emergency_bypass_until`
  - `emergency_bypass_reason`
  - `emergency_bypass_approved_by`
  - `human_authority_allowlist`
- per-WRK marker/exemption artifacts own WRK-specific migration state subject to checker precedence.
- wrappers, CI, hooks, and skill docs consume these rules and must not redefine them.

## Activation And Cutover
Canonical activation-state enum in `stage5-gate-config.yaml`:
- `disabled`
- `canary_plan_cross_review`
- `canary_claim_close`
- `full`

Same activation enum must be consumed by:
- runtime wrappers
- CI
- hooks

Cutover compatibility:
- before activation, bootstrap/checker inspection may read legacy artifact versions only for reporting/backfill/exemption determination
- during canary/full activation, guarded entrypoints accept only:
  - current contract version, or
  - legacy artifacts validated through backfill/exemption rules
- unmigrated legacy artifacts fail closed when activation is live

Guard timeout and emergency bypass:
- guarded callers use a maximum wall-clock checker timeout of `30s`
- timeout value is sourced from `stage5-gate-config.yaml`
- emergency bypass is controlled only through `stage5-gate-config.yaml`
- bypass requires `emergency_bypass_until`, `emergency_bypass_reason`, and `emergency_bypass_approved_by`
- bypass approval authority is human-only and bypass events are auditable operational overrides, not evidence success
- allowlisted human authority comes from `human_authority_allowlist`; unknown or agent-like identities fail closed

## Migration And Legacy Rules
Legacy runtime predicate:
- determine legacy from the WRK file first-introduced git commit vs `gate_activation_commit`
- `created_at` is informational only
- `stage5-first-gated.yaml` stabilizes later reruns if already present
- non-legacy WRKs get no exemption path
- once `stage5-first-gated.yaml` exists, it becomes the authoritative source for later reruns; git-history classification is bootstrap fallback only

Legacy remediation matrix:
- missing `user-review-common-draft.yaml` or `user-review-plan-draft.yaml`:
  - no automatic reconstruction
  - compliant path is fresh live review capture or approved migration exemption
- missing `user-review-browser-open.yaml` or `user-review-publish.yaml`:
  - deterministic backfill allowed only through canonical bootstrap/migration path when immutable facts are unambiguous
  - otherwise rerun or approved migration exemption
- missing approval artifacts plus first-gated marker:
  - still non-compliant

Conflicting migration-state precedence:
- current-contract evidence validated by the canonical checker wins over legacy/backfill signals
- approved migration exemptions resolve legacy ambiguity but never override current-contract predicate failure
- first-gated markers stabilize legacy classification only; they never satisfy missing approval evidence
- partial publish evidence or later manual artifacts cannot override a conflicting approved published baseline without a new valid publish event

Migration exemption approval:
- exemption artifacts are created from `specs/templates/stage5-migration-exemption-template.yaml`
- minimum approval fields include `wrk_id`, `approved_by`, `approved_at`, `approval_scope`, and `rationale`
- `approved_by` must be a human authority value, never an agent identity

Bootstrap-incomplete rule:
- missing `stage-evidence.yaml` means `bootstrap_incomplete`
- owner: orchestrator
- first repair action: `scripts/work-queue/backfill-stage-evidence.py` using `specs/templates/stage-evidence-template.yaml`
- if deterministic recovery fails, item stays `no_go` until fresh review capture or approved migration exemption
- first live rollout remains blocked until every bootstrap-incomplete WRK is either repaired or explicitly out of the rollout set

## Stage 6 To Stage 7
Stage 6 disposition source:
- canonical artifact: `.claude/work-queue/assets/WRK-<id>/evidence/stage-evidence.yaml`
- canonical section: `stage6_review_dispositions`
- required fields:
  - `latest_run_id`
  - `baseline_commit`
  - per-provider entries with `verdict`, `review_ref`, `disposition`, `rationale`
- canonical writer: `scripts/work-queue/update-stage-evidence.py`
- `scripts/review/cross-review.sh` is a raw-review producer only
- the renderer is read-only and consumes `stage6_review_dispositions`; it does not author reconciliation state
- **Stage 6 disposition write locking**: `update-stage-evidence.py` Stage 6 disposition writes use the same `lockfile + atomic rename` strategy as Stage 5 evidence writes. Lock scope covers the full `stage6_review_dispositions` section write; lock acquisition failure is exit `2`; stale-lock cleanup follows the same heuristic (recorded PID no longer live + age exceeds timeout). At least one concurrent-writer test is required (Phase 1B).

Stage 7 readiness:
- blocked unless latest Stage 6 review set has no unresolved `REQUEST_CHANGES`, or each remaining `REQUEST_CHANGES` has an explicit disposition in `stage6_review_dispositions`
- **Baseline commit equality rule (fail-closed)**: `stage6_review_dispositions.baseline_commit` must equal the authoritative Stage 5 published baseline commit from `user-review-publish.yaml` (last `plan_draft + combined_plan` event). A mismatch blocks Stage 7 — reconciliation and delta rendering must share the same baseline.
- Stage 7 renderer must consume `stage6_review_dispositions` plus the approved Stage 5 baseline commit
- fail closed if the approved Stage 5 baseline commit cannot be resolved
- render an explicit `No Changes Since Stage 5` section when the final-plan package is a valid no-op delta
- render a non-empty `Changes Since Stage 5` section when the final-plan package differs from the approved baseline

## Wrapper Contract
Guarded wrappers in scope:
- `plan.sh`
- `cross-review.sh`
- `claim-item.sh`
- `close-item.sh`

Canonical checker modes:
- `check`: read-only verification mode for wrappers and validators
- `bootstrap`: dry-run inventory/reporting mode
- `first-gated`: the only write-enabled mode, limited to controlled `stage5-first-gated.yaml` creation
- all modes share one stdout/stderr and exit-code contract
- shell wrappers and downstream validators must call `check`; they must not call write-enabled modes

Wrapper rules:
- call checker only through `uv run --no-project python scripts/work-queue/verify-gate-evidence.py <mode> ...`
- exit `0`: may continue
- exit `1`: predicate failure, block
- exit `2`: infrastructure/path failure, block
- wrappers may prefix context on stderr
- wrappers must preserve checker diagnostics and exit-code meaning
- wrappers may not impose a shorter git-history timeout than the checker
- official Python entrypoints run through `uv run --no-project python`; no bare `python3` fallback for guarded logic

## Phase Model
Authoritative phases:
- `Phase 1A`: diagnosis and inventory
- `Phase 1B`: gate engine delivery, guarded entrypoint rollout, and hardening
- `Phase 2`: Stage 7 packaging

Milestones are not phases:
- `pre_rollout`
- `first_live_rollout`
- `hard_gate_delivered`
- `fully_stage5_hardened`
- `stage7_packaging`

## Executable Phase Breakdown
Phase 1A:
- outputs (ALL required before Phase 1B rollout begins):
  - confirmed investigation answers (`root-cause-replay.md` + `## Investigation Answers` in WRK)
  - prerequisite inventory complete (browser-open/publish writer scripts, templates)
  - bootstrap dry-run inventory interface and go/no-go report contract frozen
  - AC-to-test matrix frozen for execution (`ac-test-matrix.md`)
  - `stage5-gate-config.yaml` initial schema committed
  - canonical checker core algorithm implemented in `verify-gate-evidence.py`
  - deterministic timeout/circuit-breaker behavior for live git lookups (8s bound)
  - concrete locking strategy for append-only evidence and first-gated writes
  - first guarded entrypoint (`scripts/agents/plan.sh`) wired to canonical checker
  - core negative/positive gate tests passing
- exit checklist:
  - `ac-test-matrix.md` is the authoritative row-level phase-tag source
  - no contradiction remains between the matrix, authoritative WRK, and compact bundle
  - Phase 1A is NOT the minimum delivered gate milestone; Phase 1B hard-gate delivery is
- blockers:
  - missing prerequisite scripts/templates
  - unresolved bootstrap-incomplete WRKs
  - unclear bypass replay path

Phase 1B:
- outputs:
  - canonical checker contract
  - schema/version alignment
  - migration/backfill rules
  - guarded official entrypoints
  - releasable `hard_gate_delivered` milestone
- blockers:
  - bootstrap `no_go`
  - compatibility failures
  - unexpected live traps
  - checker `exit 2`

Phase 2:
- outputs:
  - `Changes Since Stage 5` review section
  - Stage 7-ready final-plan package
  - renderer tests
- blockers:
  - missing Stage 6 disposition data
  - unresolved baseline mismatch
  - renderer delta failure

## Activation Order
1. `bootstrap-stage5-gate.sh --dry-run`
2. canonical checker fixture validation in read-only mode
3. guard `plan.sh`
4. guard `cross-review.sh`
5. guard `claim-item.sh`
6. guard `close-item.sh`

Stop conditions after each step:
- bootstrap stays `no_go`
- targeted tests fail
- compatibility defect appears
- unexpected `exit 2`

Rollback owner:
- orchestrator

Rollback method:
- revert only the latest entrypoint-guard patch once activation has started
- keep checker/schema work in place for diagnosis

## Merge vs Activate Boundary
- Phase 1 checker/schema code may merge before live activation if activation remains controlled by `stage5-gate-config.yaml`.
- `hard_gate_delivered` is the first milestone that may activate for live use.
- Phase 2 may merge later without blocking Phase 1 activation.
- WRK closure and Stage 7 review remain blocked until Phase 2 is complete.
- This is a release/closure dependency, not discretionary follow-up work.
- hooks and CI read the same activation state from `stage5-gate-config.yaml`; they do not use a separate enablement path

## Blocking Closure Checklist
Must ship for Stage 5 hard gate:
- canonical checker
- schema/templates
- activation config
- migration policy
- wrapper contract
- guarded official entrypoints

Must ship before live activation:
- bootstrap report green or explicit no-go exclusions
- cutover compatibility rule
- backfill/exemption path
- targeted rollout tests
- rollback note

Must ship before WRK closure:
- `fully_stage5_hardened`
- Stage 6 disposition enforcement
- Stage 7 `Changes Since Stage 5` rendering
- required CI/hook backstops

## Highest-Risk Coverage Summary
- stale/baseline evidence logic: `tests/unit/test_verify_gate_evidence.py`
- guarded entrypoint behavior and wrapper propagation: `scripts/agents/tests/test-plan-gate.sh`
- lifecycle behavior across claim/close: `tests/work-queue/test-lifecycle-gates.sh`
- Stage 6 disposition -> Stage 7 delta rendering: `tests/unit/test_generate_html_review.py`
- wrapper/config skew and adversarial evidence failure modes: `tests/unit/test_verify_gate_evidence.py`
- canary boundary behavior between `canary_plan_cross_review` and `canary_claim_close`: dedicated integration coverage
- deterministic harness strategy for timeout/concurrency cases:
  - stubbed git command for the `8s` timeout path
  - stubbed reviewer command for the `60s` no-response path
  - fixture lockfiles for stale-lock and contention behavior
  - bounded subprocess coordination for concurrent writes
- mandatory edge cases still required from the authoritative WRK:
  - malformed or missing config must fail closed with exit `2`
  - evidence replay abuse must fail closed
  - all decision-table branches must be tested
  - degraded-mode and manual-edit paths must be tested
  - bounded `8s` git-history timeout behavior must be tested
  - bounded `60s` provider no-response behavior must be tested
  - concurrent write and clock-skew cases must be tested

## AC/Test Authority
Detailed traceability artifact already exists:
- `.claude/work-queue/assets/WRK-1017/ac-test-matrix.md`

The compact bundle does not reproduce the full matrix. The matrix remains authoritative for row-level AC-to-test mapping.

## Automation Assertion Semantics (AC-18, AC-23, AC-24)
ACs that rely on CI/hook automation as their primary coverage tier must enforce the following specific assertions (not just script presence):

- **AC-18 (TDD order)**: `baseline-check.yml` asserts that unit test jobs (`test_verify_gate_evidence.py`, `test_generate_html_review.py`) must pass before implementation-level jobs are marked green. TDD order is a process gate enforced by CI job dependency ordering.
- **AC-23 (decision-table semantics)**: `pre-commit` hook verifies that the canonical decision enum values (`approve_as_is`, `revise_and_rerun`, `reject`, `no_response`) are present in `verify-gate-evidence.py` source via `grep -q "approve_as_is"`. Non-canonical aliases must not appear in persisted evidence or checker source.
- **AC-24 (root-cause documentation)**: `baseline-check.yml` asserts `test -f .claude/work-queue/assets/WRK-1017/evidence/root-cause-replay.md` and that the authoritative WRK contains a `## Investigation Answers` section. These are file-presence + content-structure checks, not free-form prose validation.
