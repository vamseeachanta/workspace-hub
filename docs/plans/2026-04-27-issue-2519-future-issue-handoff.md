# Issue #2519 Future-Issue Handoff

Date: 2026-04-27
Parent issue: #2519 — https://github.com/vamseeachanta/workspace-hub/issues/2519
Prompt-pack commit: `3e136a524` — `docs(orchestration): add continuous machine prompts`

## Purpose

Capture the future GitHub issues created after the two-machine Hermes/Codex orchestration prompt pack was committed. These issues turn the current manual workflow into durable, automatable follow-up work.

## Created future issues

| Issue | Title | Purpose | Priority |
|---:|---|---|---|
| #2523 | [feat(workstations): add reusable Hermes preflight readiness checker](https://github.com/vamseeachanta/workspace-hub/issues/2523) | Convert the manual `ace-linux-2` readiness/auth/tool probe into a reusable checker that emits redacted JSON/markdown reports. | High |
| #2524 | [feat(orchestration): add machine-aware dispatch ledger and reconciler](https://github.com/vamseeachanta/workspace-hub/issues/2524) | Add a durable lane ledger and reconciliation loop for issue/provider/model/workstation/worktree/evidence state. | High |
| #2525 | [feat(provider-usage): codex expiring-credit burn-down controller](https://github.com/vamseeachanta/workspace-hub/issues/2525) | Convert user-visible Codex expiry/remaining-credit urgency plus provider telemetry into safe, useful, plan-gated Codex-first work lanes. | High |

All three issues were created with labels:

- `enhancement`
- `priority:high`
- `cat:ai-orchestration`
- `cat:harness`
- `domain:ai-orchestration`
- `domain:workstations`
- `domain:agent-cost-tracking`

## Relationship to existing issues

- #2519 remains the parent feature for Hermes provider/workstation orchestration.
- #2520 remains the immediate blocker for repairing/gating `ace-linux-2` GitHub auth.
- #2504 already covers dispatch-ledger trust contract and lease lifecycle. #2524 should reuse or extend #2504 rather than duplicating it.
- #1838 already covers broader AI credit utilization governance. #2525 narrows that into an operational Codex-expiring-credit controller for the current orchestration flow.

## Current operating posture

Until #2520 is resolved:

1. `ace-linux-1` remains the control plane and GitHub mutation authority.
2. `ace-linux-2` may run Hermes/Codex only through a login shell:
   ```bash
   ssh ace-linux-2 'bash -lc "<command>"'
   ```
3. `ace-linux-2` should write local result artifacts for `ace-linux-1` to post when GitHub mutation is needed.
4. Implementation dispatch still requires `status:plan-approved` plus any local plan-approved marker gate; planning/review/prompt generation is safe before approval.

## Recommended next sequence

1. Use the committed machine prompts under `docs/plans/machine-prompts/2026-04-27/` for the immediate Codex burn-down window.
2. Resolve #2520 so `ace-linux-2` can safely perform GitHub mutation when needed.
3. Plan #2523 to make future workstation readiness checks repeatable.
4. Plan #2524 to make continuous/parallel dispatch durable across context compaction and terminal restarts.
5. Plan #2525 after or alongside #2524 so provider-urgency routing writes to the same ledger.

## Exit state

This is a documentation/coordination handoff only. No additional long-running workers were launched while creating these future issues.
