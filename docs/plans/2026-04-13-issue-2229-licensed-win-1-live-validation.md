# Plan for #2229: validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2229
> **Review artifacts:** `scripts/review/results/2026-04-13-plan-2229-subagent.md`, `scripts/review/results/2026-04-14-plan-2229-codex.md`, `scripts/review/results/2026-04-14-plan-2229-gemini.md`, `scripts/review/results/2026-04-15-plan-2229-claude.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/handoffs/session-2026-04-11-windows-claude-parity-exit.md` explicitly records why #2229 was created: replace the bootstrap readiness artifact with live Windows evidence and validate real Task Scheduler execution on `licensed-win-1`.
- Found: `scripts/windows/setup-scheduler-tasks.ps1` is the canonical Windows scheduler setup surface and already documents/creates `MemoryBridgeSync`.
- Found: `.claude/state/harness-readiness-licensed-win-1.yaml` is the tracked readiness proof target referenced by the issue and by test fixtures.
- Found: `scripts/readiness/compare-harness-state.sh` and `scripts/readiness/harness-config.yaml` are part of the current readiness proof path for Windows parity.
- Found: `scripts/memory/bridge-hermes-claude.sh` is the existing cross-platform memory bridge used by the parity work.
- Found: `tests/work-queue/test-weekly-hermes-parity-review.sh` already contains fixture expectations for the Windows readiness artifact path and report semantics.
- Gap: no canonical local plan artifact exists in `docs/plans/` for #2229 even though the GitHub issue is already in `status:plan-review`.

### Standards
N/A — harness / Windows parity / operations task

### Documents consulted
- GitHub issue #2229 — scope and acceptance criteria for live Windows validation.
- `docs/handoffs/session-2026-04-11-windows-claude-parity-exit.md` — creation rationale and prerequisite repo-side work.
- `docs/plans/2026-04-12-issue-2239-automate-weekly-hermes-cross-machine-parity-review.md` — adjacent parity workflow plan that already defines the Windows evidence contract.
- `tests/work-queue/test-weekly-hermes-parity-review.sh` — existing expectations for `.claude/state/harness-readiness-licensed-win-1.yaml`.
- `tests/work-queue/test-harness-readiness.sh` — current readiness script validation surface.
- `config/workstations/registry.yaml` — canonical workstation identity for `licensed-win-1`.

### Gaps identified
- Need explicit Task Scheduler evidence requirements: registration state, last run result/time, and at least one scheduler-observed execution proof for the two tasks in scope.
- Need explicit `MemoryBridgeSync` success/failure evidence for the scheduled/commit path, not just generic file refresh.
- Need a bounded v1 decision on whether reboot persistence is required now or explicitly deferred.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2229-licensed-win-1-live-validation.md` |
| Windows scheduler setup | `scripts/windows/setup-scheduler-tasks.ps1` |
| Readiness config | `scripts/readiness/harness-config.yaml` |
| Readiness comparison | `scripts/readiness/compare-harness-state.sh` |
| Memory bridge | `scripts/memory/bridge-hermes-claude.sh` |
| Proof artifact | `.claude/state/harness-readiness-licensed-win-1.yaml` |
| Existing parity tests | `tests/work-queue/test-weekly-hermes-parity-review.sh`, `tests/work-queue/test-harness-readiness.sh` |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A bounded live-validation runbook and execution plan for `licensed-win-1` that replaces the bootstrap readiness artifact with real machine evidence, proves or falsifies `NightlyReadiness` and `MemoryBridgeSync` using concrete Task Scheduler and bridge-path evidence, and records exact repro/log evidence for any remaining Windows-specific failures.

---

## Pseudocode

```text
confirm the current placeholder/proof artifact state for licensed-win-1
on licensed-win-1:
    install or refresh scheduled tasks via setup-scheduler-tasks.ps1
    capture scheduler evidence for NightlyReadiness and MemoryBridgeSync:
        task exists
        task last run time/result
        task action/arguments match expected script path
    run NightlyReadiness manually once
    capture the produced readiness artifact and compare it to the bootstrap placeholder
    run MemoryBridgeSync in the same mode used by the scheduled task (including commit-path expectations where safely verifiable)
    verify repo-tracked memory outputs refresh and capture bridge logs / git side effects
    decide v1 persistence rule:
        if reboot validation is in scope, capture post-reboot evidence
        else explicitly mark reboot persistence deferred
if validation passes:
    replace placeholder artifact with real output and document rerun steps
else:
    preserve artifact/logs and record exact failure mode plus repro steps
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-13-issue-2229-licensed-win-1-live-validation.md` | canonical plan artifact |
| Update (if live run succeeds) | `.claude/state/harness-readiness-licensed-win-1.yaml` | replace placeholder with real evidence |
| Update (if needed) | `scripts/windows/setup-scheduler-tasks.ps1` | only if live behavior differs from current assumptions |
| Update (if needed) | `.claude/docs/new-machine-setup.md` or related docs | capture corrected Windows rerun steps |
| Update | `docs/plans/README.md` | add plan index row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_plan_anchors_to_real_windows_artifact | plan uses the tracked readiness artifact as proof target | plan content | `.claude/state/harness-readiness-licensed-win-1.yaml` referenced |
| test_scheduler_surface_is_canonical | plan uses existing scheduler setup script rather than inventing a new path | plan content | `setup-scheduler-tasks.ps1` referenced |
| test_scheduler_evidence_is_required | plan requires task registration and last-run evidence | plan content | scheduler evidence checklist present |
| test_memory_bridge_commit_path_is_explicit | plan names commit-path / git-side-effect evidence for MemoryBridgeSync | plan content | bridge-path evidence explicitly required |
| test_validation_allows_failure_capture | plan supports concrete failure reporting, not just happy-path success | plan content | explicit fail-path in pseudocode/acceptance |
| test_existing_windows_parity_tests_are_reused | plan reuses existing parity/readiness test surfaces | plan content | test files referenced |
| test_reboot_persistence_scope_is_explicit | plan either requires reboot persistence evidence or explicitly defers it | plan content | clear v1 persistence decision |

---

## Acceptance Criteria

- [ ] Canonical plan file exists for #2229.
- [ ] Plan explicitly defines the live validation sequence for `NightlyReadiness` and `MemoryBridgeSync`.
- [ ] Plan requires concrete Task Scheduler evidence (registration plus last-run proof) for both tasks.
- [ ] Plan defines what counts as success and what evidence must be captured on failure.
- [ ] Plan uses the tracked readiness artifact as the proof target.
- [ ] Plan explicitly states whether reboot-persistence validation is required now or deferred from v1.
- [ ] Plan is ready for adversarial review before any Windows execution is treated as validated.

---

## Adversarial Review Summary

Fresh external adversarial review completed on 2026-04-14/15 and returned blocking findings from Codex, Gemini, and Claude. The issue was correctly rolled back from premature approval to `status:plan-review`, and the stale local approval marker has already been removed.

| Provider | Verdict | Key findings |
|---|---|---|
| Subagent review (2026-04-13) | MAJOR then tightened to approval-ready draft | Initial tightening pass added Task Scheduler evidence, explicit MemoryBridgeSync commit-path evidence, and a bounded reboot-persistence decision. |
| Codex (2026-04-14) | MAJOR | Governance was ahead of review state; acceptance criteria were still plan-centric rather than execution-facing; exact task/evidence contracts, reboot scope, and `MemoryBridgeSync` side effects remained underspecified. |
| Gemini (2026-04-14) | MAJOR | Manual script execution does not prove headless Task Scheduler behavior; plan missed local Windows approval-marker/strict-hook implications, headless push credential risk, and Linux parity verification. |
| Claude (2026-04-15) | MAJOR | Plan still lacked scheduler-triggered execution proof, a full `--commit` side-effect contract, full readiness-artifact structure requirements, and complete `cat:harness` retrieval grounding. |

**Overall result:** MAJOR — not approval-ready. Keep this issue in `status:plan-review` until the execution contract is rewritten and re-reviewed.

Revisions now required from review:
- Require at least one scheduler-triggered execution per task (`NightlyReadiness`, `MemoryBridgeSync`) with captured Task Scheduler evidence, not just manual runs.
- Make the `MemoryBridgeSync --commit` contract explicit: expected changed files, commit/no-op/fail semantics, push expectations, and evidence bundle.
- Tighten success criteria for `.claude/state/harness-readiness-licensed-win-1.yaml` from “non-placeholder” to full expected readiness structure plus scheduler-observed provenance.
- Add the missing harness-specific retrieval sources and reflect their findings in Resource Intelligence.
- Explicitly cover approval-marker/hook behavior on `licensed-win-1`, headless push credentials, and final Linux parity validation.
- Keep plan header/status aligned with live governance state and keep the full cross-provider review set current.

---

## Risks and Open Questions

- **Risk:** live Windows execution may fail for environment-specific reasons that cannot be reproduced from Linux; the plan must value evidence capture as much as success.
- **Risk:** commit-path validation for `MemoryBridgeSync` must avoid unintended side effects while still proving the real path.
- **Open:** reboot persistence is deferred from v1 unless the live validation run shows task registration instability; the first approval-ready implementation may treat one scheduler-observed execution cycle as sufficient.

---

## Complexity: T2

**T2** — bounded multi-surface validation plan spanning one Windows machine, one tracked proof artifact, and a small set of existing readiness/bridge scripts.
