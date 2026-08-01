# Provider work queue

Generated: 2026-08-01T01:21:12.440934Z
Current week: 2026-W31
Recommended provider order: codex, agy, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 18
- Total routed candidates: 179

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3500 bug(pre-push): equivalence-state publish loops full tier-1 suite forever — remote ref never created, every push gated as new-branch RUN_ALL (sub-case of #3198) | yes | strategy/workflow/architecture language | bug, priority:high, cat:harness, machine:dev-primary, status:plan-approved, gate:completeness |
| #3549 feat(ops): registry-driven Linux connection helpers with TDD | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:tooling, domain:workstations, domain:security, status:plan-approved |
| #3440 Harden generated HTML against JSON script-tag breakout | yes | strategy/workflow/architecture language | bug, priority:medium, cat:harness, domain:security, domain:workflow, status:plan-approved |
| #3482 design(repo-health): safe worktree lifecycle with leases and recoverable quarantine | yes | strategy/workflow/architecture language | priority:medium, cat:tooling, domain:testing, status:plan-approved, gate:completeness, lane:codex |
| #3524 [WRK] bug(workstations): RDP microphone input not negotiated from ACMA-WS014 to ACMA-HOU-RDS02 | yes | strategy/workflow/architecture language | bug, priority:medium, cat:operations, domain:workstations, machine:multi, status:plan-approved |
| #3525 [WRK] Investigate safe remote Claude job dispatch to ACMA-WS014 | yes | strategy/workflow/architecture language | priority:medium, cat:harness, domain:workstations, wrk-item, status:plan-approved, gate:completeness |
| #3566 fix(agent-ux): make keyboard and context-menu text paste equivalent in Codex CLI | yes | strategy/workflow/architecture language | bug, priority:medium, cat:harness, machine:multi, status:plan-approved, type:follow-up |
| #3568 epic(agent-ux): cross-machine input interaction parity | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:workstations, machine:multi, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 5
- Total routed candidates: 20

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3516 bug(equivalence): ref blobs keyed by role — same-role boxes (ace-win-1/2) will clobber each other; role detection hardcoded to 2 hosts (gpu-claw published as unknown.json) | yes | implementation/test/fix language | bug, priority:high, cat:harness, domain:workstations, machine:multi, status:plan-approved |
| #3472 feat(operations): add pressure-aware daily OS maintenance cleanup | yes | implementation/test/fix language | priority:medium, cat:tooling, domain:testing, machine:dev-primary, status:plan-approved, gate:completeness |
| #3532 fix(memory): reserve cross-provider runtime budget for operational feedback | yes | implementation/test/fix language | enhancement, cat:harness, status:plan-approved, gate:completeness, lane:claude, domain:ai |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | yes | implementation/test/fix language | bug, cat:harness, domain:workstations, machine:multi, status:plan-approved, gate:completeness |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | yes | implementation/test/fix language | cat:operations, domain:workstations, status:plan-approved, gate:completeness, lane:claude |
| #3585 phone-media: EXIF-date organizer + cross-phone dedupe | no | implementation/test/fix language | priority:medium, cat:data, machine:dev-primary, domain:family |
| #3696 chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | no | implementation/test/fix language | priority:medium, cat:operations, domain:workstations, machine:dev-primary |
| #3594 chore(registry): gpu-claw entry stale after 2026-07-22 relocation+onboarding — notes say clone pending / uv NOT installed; both now false | no | implementation/test/fix language | bug, priority:low, cat:operations, domain:workstations, machine:multi, lane:claude |

## agy

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 1

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | no | research/triage/audit language | cat:harness |

