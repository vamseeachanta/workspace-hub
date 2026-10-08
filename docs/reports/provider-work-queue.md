# Provider work queue

Generated: 2026-10-08T09:21:17.146700Z
Current week: 2026-W41
Recommended provider order: codex, agy, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 5
- Total routed candidates: 180

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3816 feat(repo): generate authoritative work-surface inventory and adapter coverage report | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:tooling, machine:multi, status:plan-approved, gate:completeness |
| #3838 fix(digitalmodel/orcaflex): three verified model-building integrity defects with silent failure modes | yes | strategy/workflow/architecture language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3843 refactor(orcaflex): consolidate four model generators onto modular_generator | yes | strategy/workflow/architecture language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3592 equality matrix: reclassify harness/scheduler/memory rows — uniform vote mis-grades per-role differences + Windows placeholder data poisons majority | yes | strategy/workflow/architecture language | cat:harness, domain:workstations, machine:dev-primary, status:plan-approved, gate:completeness, lane:claude |
| #3702 bug(equality): equality-matrix-cron writes generated artifacts into the tracked tree, creating a self-sustaining STALE-CHECKOUT deadlock | yes | strategy/workflow/architecture language | bug, cat:harness, domain:workstations, machine:multi, status:plan-approved, gate:completeness |
| #3596 Compliance alert: W30 — 18% (critical) | no | strategy/workflow/architecture language | cat:operations, priority:critical, machine:dev-primary, compliance-alert, domain:harness |
| #3693 Compliance alert: W31 — 0% (critical) | no | strategy/workflow/architecture language | priority:medium, priority:critical, machine:dev-primary, compliance-alert, domain:governance |
| #3794 Compliance alert: W32 — 66% (medium) | no | strategy/workflow/architecture language | priority:medium, priority:critical, compliance-alert |

## codex

- Routing priority: highest
- Execution-ready candidates: 3
- Total routed candidates: 18

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3740 867 issues cannot leave dispatch:ready — nothing advances dispatch state | yes | implementation/test/fix language | priority:high, cat:operations, machine:dev-primary, status:plan-approved, gate:completeness, domain:routing |
| #3839 fix(digitalmodel/fatigue): two of four rainflow paths understate stress range, understating damage | yes | implementation/test/fix language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3787 pytest pays a large fixed startup tax before any test runs — 38s git call, 59MB DB query on collect-only, 487 hidden test files | yes | implementation/test/fix language | bug, status:plan-approved, gate:completeness, lane:claude |
| #3788 bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING | no | implementation/test/fix language | bug, priority:high, cat:operations, machine:dev-primary, status:needs-plan, domain:routing |
| #3821 bug(equality): restore collector idempotency and macOS atomic-publish test portability | no | implementation/test/fix language | bug, priority:high, cat:harness, domain:testing, machine:multi, status:needs-plan |
| #3696 chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | no | implementation/test/fix language | priority:medium, cat:operations, domain:workstations, machine:dev-primary |
| #3792 feat(scheduler): no transaction attestation exists for systemd-user surfaces, so they can only ever declare missing_transaction | no | implementation/test/fix language | enhancement, priority:medium, cat:harness, domain:workstations, status:needs-plan |
| #3842 refactor(fatigue): consolidate seven rainflow counting paths onto one | no | implementation/test/fix language | priority:medium, cat:engineering, domain:marine, lane:claude |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3819 feat(harness): unified ecosystem doctor with stable probe schema | no | research/triage/audit language | enhancement, priority:medium, cat:harness, machine:multi, status:needs-plan, domain:harness |
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | no | research/triage/audit language | cat:harness, machine:dev-primary, domain:harness |

