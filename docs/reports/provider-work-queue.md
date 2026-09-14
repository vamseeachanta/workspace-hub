# Provider work queue

Generated: 2026-09-14T09:22:17.508946Z
Current week: 2026-W38
Recommended provider order: agy, codex, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 12
- Total routed candidates: 176

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3549 feat(ops): registry-driven Linux connection helpers with TDD | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:tooling, domain:workstations, domain:security, machine:dev-primary |
| #3816 feat(repo): generate authoritative work-surface inventory and adapter coverage report | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:tooling, machine:multi, status:plan-approved, gate:completeness |
| #3838 fix(digitalmodel/orcaflex): three verified model-building integrity defects with silent failure modes | yes | strategy/workflow/architecture language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3843 refactor(orcaflex): consolidate four model generators onto modular_generator | yes | strategy/workflow/architecture language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3566 fix(agent-ux): make keyboard and context-menu text paste equivalent in Codex CLI | yes | strategy/workflow/architecture language | bug, priority:medium, cat:harness, machine:multi, status:plan-approved, type:follow-up |
| #3568 epic(agent-ux): cross-machine input interaction parity | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:workstations, machine:multi, status:plan-approved |
| #3527 fix(scheduler): reconcile identity inventory after merge-base race | yes | strategy/workflow/architecture language | bug, cat:harness, machine:dev-primary, status:plan-approved, gate:completeness, domain:harness |
| #3544 security(legal): correct and operationalize Phase A authority activation | yes | strategy/workflow/architecture language | cat:operations, machine:dev-primary, status:plan-approved, gate:completeness, lane:codex, domain:governance |

## codex

- Routing priority: highest
- Execution-ready candidates: 6
- Total routed candidates: 22

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3740 867 issues cannot leave dispatch:ready — nothing advances dispatch state | yes | implementation/test/fix language | priority:high, cat:operations, machine:dev-primary, status:plan-approved, gate:completeness, domain:routing |
| #3839 fix(digitalmodel/fatigue): two of four rainflow paths understate stress range, understating damage | yes | implementation/test/fix language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3532 fix(memory): reserve cross-provider runtime budget for operational feedback | yes | implementation/test/fix language | enhancement, cat:harness, machine:dev-primary, status:plan-approved, gate:completeness, lane:claude |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | yes | implementation/test/fix language | bug, cat:harness, domain:workstations, machine:multi, status:plan-approved, gate:completeness |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | yes | implementation/test/fix language | cat:operations, domain:workstations, machine:dev-primary, status:plan-approved, gate:completeness, lane:claude |
| #3787 pytest pays a large fixed startup tax before any test runs — 38s git call, 59MB DB query on collect-only, 487 hidden test files | yes | implementation/test/fix language | bug, status:plan-approved, gate:completeness, lane:claude |
| #3788 bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING | no | implementation/test/fix language | bug, priority:high, cat:operations, machine:dev-primary, status:needs-plan, domain:routing |
| #3821 bug(equality): restore collector idempotency and macOS atomic-publish test portability | no | implementation/test/fix language | bug, priority:high, cat:harness, domain:testing, machine:multi, status:needs-plan |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3819 feat(harness): unified ecosystem doctor with stable probe schema | no | research/triage/audit language | enhancement, priority:medium, cat:harness, machine:multi, status:needs-plan, domain:harness |
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | no | research/triage/audit language | cat:harness, machine:dev-primary, domain:harness |

