# Provider work queue

Generated: 2026-09-26T09:21:14.769281Z
Current week: 2026-W39
Recommended provider order: codex, agy, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 9
- Total routed candidates: 178

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3816 feat(repo): generate authoritative work-surface inventory and adapter coverage report | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:tooling, machine:multi, status:plan-approved, gate:completeness |
| #3838 fix(digitalmodel/orcaflex): three verified model-building integrity defects with silent failure modes | yes | strategy/workflow/architecture language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3843 refactor(orcaflex): consolidate four model generators onto modular_generator | yes | strategy/workflow/architecture language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3566 fix(agent-ux): make keyboard and context-menu text paste equivalent in Codex CLI | yes | strategy/workflow/architecture language | bug, priority:medium, cat:harness, machine:multi, status:plan-approved, type:follow-up |
| #3568 epic(agent-ux): cross-machine input interaction parity | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:workstations, machine:multi, status:plan-approved |
| #3573 feat(ai-orchestration): replace gemini with agy as the third worker/reviewer provider ecosystem-wide | yes | strategy/workflow/architecture language | enhancement, cat:harness, machine:multi, status:plan-approved, gate:completeness, lane:claude |
| #3578 fix(review): submit-to-codex.sh hangs — codex exec exit 124 'Reading additional input from stdin' despite #3294 mitigation | yes | strategy/workflow/architecture language | cat:harness, machine:dev-primary, status:plan-approved, gate:completeness, domain:harness |
| #3592 equality matrix: reclassify harness/scheduler/memory rows — uniform vote mis-grades per-role differences + Windows placeholder data poisons majority | yes | strategy/workflow/architecture language | cat:harness, domain:workstations, machine:dev-primary, status:plan-approved, gate:completeness, lane:claude |

## codex

- Routing priority: highest
- Execution-ready candidates: 4
- Total routed candidates: 20

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3740 867 issues cannot leave dispatch:ready — nothing advances dispatch state | yes | implementation/test/fix language | priority:high, cat:operations, machine:dev-primary, status:plan-approved, gate:completeness, domain:routing |
| #3839 fix(digitalmodel/fatigue): two of four rainflow paths understate stress range, understating damage | yes | implementation/test/fix language | priority:high, cat:engineering, domain:marine, status:plan-approved, gate:completeness, lane:claude |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | yes | implementation/test/fix language | cat:operations, domain:workstations, machine:dev-primary, status:plan-approved, gate:completeness, lane:claude |
| #3787 pytest pays a large fixed startup tax before any test runs — 38s git call, 59MB DB query on collect-only, 487 hidden test files | yes | implementation/test/fix language | bug, status:plan-approved, gate:completeness, lane:claude |
| #3788 bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING | no | implementation/test/fix language | bug, priority:high, cat:operations, machine:dev-primary, status:needs-plan, domain:routing |
| #3821 bug(equality): restore collector idempotency and macOS atomic-publish test portability | no | implementation/test/fix language | bug, priority:high, cat:harness, domain:testing, machine:multi, status:needs-plan |
| #3585 phone-media: EXIF-date organizer + cross-phone dedupe | no | implementation/test/fix language | priority:medium, cat:data, machine:dev-primary, domain:family |
| #3696 chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | no | implementation/test/fix language | priority:medium, cat:operations, domain:workstations, machine:dev-primary |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3819 feat(harness): unified ecosystem doctor with stable probe schema | no | research/triage/audit language | enhancement, priority:medium, cat:harness, machine:multi, status:needs-plan, domain:harness |
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | no | research/triage/audit language | cat:harness, machine:dev-primary, domain:harness |

