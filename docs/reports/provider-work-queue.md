# Provider work queue

Generated: 2026-07-28T05:21:13.732510Z
Current week: 2026-W31
Recommended provider order: codex, agy, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 26
- Total routed candidates: 182

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3426 feat(governance): deploy completeness closeout contract to worldenergydata | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:harness, domain:workflow, status:plan-approved, gate:completeness |
| #3427 epic: repository-linked algorithm run datasets and decision intelligence | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, tracker, gate:completeness |
| #3428 standard: deterministic run identity and algorithm version contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3429 standard: content-addressed artifact and Hugging Face residency contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3431 standard: curated output and rolling algorithm report contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3432 standard: algorithm-specific metric definition and observation contract | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3433 feature: per-repository Hugging Face projection and staged promotion | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3500 bug(pre-push): equivalence-state publish loops full tier-1 suite forever — remote ref never created, every push gated as new-branch RUN_ALL (sub-case of #3198) | yes | strategy/workflow/architecture language | bug, priority:high, cat:harness, machine:dev-primary, status:plan-review, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 5
- Total routed candidates: 18

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3430 standard: replayable public input and source snapshot contract | yes | implementation/test/fix language | enhancement, priority:high, cat:data, status:plan-approved, type:follow-up, gate:completeness |
| #3472 feat(operations): add pressure-aware daily OS maintenance cleanup | yes | implementation/test/fix language | priority:medium, cat:tooling, domain:testing, machine:dev-primary, status:plan-approved, gate:completeness |
| #3532 fix(memory): reserve cross-provider runtime budget for operational feedback | yes | implementation/test/fix language | enhancement, cat:harness, status:plan-approved, gate:completeness, lane:claude, domain:ai |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | yes | implementation/test/fix language | bug, cat:harness, domain:workstations, machine:multi, status:plan-approved, gate:completeness |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | yes | implementation/test/fix language | cat:operations, domain:workstations, status:plan-approved, gate:completeness, lane:claude |
| #3585 phone-media: EXIF-date organizer + cross-phone dedupe | no | implementation/test/fix language | priority:medium, cat:data, domain:family |
| #3696 chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | no | implementation/test/fix language | priority:medium, cat:operations, domain:workstations |
| #3594 chore(registry): gpu-claw entry stale after 2026-07-22 relocation+onboarding — notes say clone pending / uv NOT installed; both now false | no | implementation/test/fix language | bug, priority:low, cat:operations, domain:workstations, machine:multi, lane:claude |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 0

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|

