# Provider work queue

Generated: 2026-07-31T05:21:15.140073Z
Current week: 2026-W31
Recommended provider order: codex, agy, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 22
- Total routed candidates: 178

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3429 standard: content-addressed artifact and Hugging Face residency contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3431 standard: curated output and rolling algorithm report contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3432 standard: algorithm-specific metric definition and observation contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3433 feature: per-repository Hugging Face projection and staged promotion | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3500 bug(pre-push): equivalence-state publish loops full tier-1 suite forever — remote ref never created, every push gated as new-branch RUN_ALL (sub-case of #3198) | yes | strategy/workflow/architecture language | bug, priority:high, cat:harness, machine:dev-primary, status:plan-approved, gate:completeness |
| #3549 feat(ops): registry-driven Linux connection helpers with TDD | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:tooling, domain:workstations, domain:security, status:plan-approved |
| #3440 Harden generated HTML against JSON script-tag breakout | yes | strategy/workflow/architecture language | bug, priority:medium, cat:harness, domain:security, domain:workflow, status:plan-approved |
| #3482 design(repo-health): safe worktree lifecycle with leases and recoverable quarantine | yes | strategy/workflow/architecture language | priority:medium, cat:tooling, domain:testing, status:plan-approved, gate:completeness, lane:codex |

## codex

- Routing priority: highest
- Execution-ready candidates: 6
- Total routed candidates: 21

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3430 standard: replayable public input and source snapshot contract | yes | implementation/test/fix language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3516 bug(equivalence): ref blobs keyed by role — same-role boxes (ace-win-1/2) will clobber each other; role detection hardcoded to 2 hosts (gpu-claw published as unknown.json) | yes | implementation/test/fix language | bug, priority:high, cat:harness, domain:workstations, machine:multi, status:plan-approved |
| #3472 feat(operations): add pressure-aware daily OS maintenance cleanup | yes | implementation/test/fix language | priority:medium, cat:tooling, domain:testing, machine:dev-primary, status:plan-approved, gate:completeness |
| #3532 fix(memory): reserve cross-provider runtime budget for operational feedback | yes | implementation/test/fix language | enhancement, cat:harness, status:plan-approved, gate:completeness, lane:claude, domain:ai |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | yes | implementation/test/fix language | bug, cat:harness, domain:workstations, machine:multi, status:plan-approved, gate:completeness |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | yes | implementation/test/fix language | cat:operations, domain:workstations, status:plan-approved, gate:completeness, lane:claude |
| #3585 phone-media: EXIF-date organizer + cross-phone dedupe | no | implementation/test/fix language | priority:medium, cat:data, domain:family |
| #3696 chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | no | implementation/test/fix language | priority:medium, cat:operations, domain:workstations |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 1

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | no | research/triage/audit language | cat:harness |

