# Provider work queue

Generated: 2026-06-03T09:20:11.119241Z
Current week: 2026-W23
Recommended provider order: gemini, claude, codex

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 34
- Total routed candidates: 172

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2533 feat(repo-portfolio): review and revise mission/objective statements across active repos | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, machine:dev-primary, status:plan-approved, dispatch:ready |
| #2563 Set up Telegram mobile access for Hermes AI control | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, domain:integrations, domain:notification |
| #2628 epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:harness, machine:dev-primary, status:plan-approved |
| #2656 chore(repo-structure): normalize workspace-hub folder/file structure | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:harness, machine:dev-primary, status:plan-approved |
| #2657 chore(provider-session): remediate Hermes llm-wiki spinout path drift | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, cat:harness, domain:session, machine:dev-primary |
| #2665 feat(kanban): provider-credit approval dashboard and dispatch gates | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:ai-config, machine:dev-primary |
| #2686 Catenary solver canonicalization: 8 implementations, 4 numerically diverge, 5 shadows to delete | yes | strategy/workflow/architecture language | bug, priority:high, cat:engineering, cat:bugfix, machine:dev-primary, status:plan-approved |
| #2694 Epic: Cross-domain duplicate-implementation cleanup (catenary, PipeCapacity, cathodic protection, natural-period, hydro-matrix, on-bottom stability) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:bugfix, domain:refactor, machine:dev-primary |

## codex

- Routing priority: high
- Execution-ready candidates: 2
- Total routed candidates: 23

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2813 chore(infra): roll out Codex-under-Claude sandbox fix (#2804) to remaining ecosystem machines | yes | implementation/test/fix language | domain:ai-config, status:plan-approved, gate:completeness, status:completeness-verified |
| #2886 Disposition: bulk-close 48 content-free WRK-XXXX:untitled migration-ghost issues (ops board cleanup, #2878) | yes | implementation/test/fix language | status:plan-approved, gate:completeness |
| #2647 ANNOUNCE: llm-wiki spinout in progress (parallel-session heads-up) | no | implementation/test/fix language | priority:high, domain:notification, machine:dev-primary, dispatch:ready, gate:completeness |
| #2718 audit(hermes): kanban-worker dispatch hazards — parallel-spawn race + silent-hang (#2715-affected) | no | implementation/test/fix language | priority:high, cat:ai-orchestration, cat:harness, domain:ai-config, machine:dev-primary, dispatch:ready |
| #2763 plan(operations): migrate gsd-researcher scheduled AI work through Hermes Agent | no | implementation/test/fix language | enhancement, priority:high, cat:ai-orchestration, cat:operations, cat:harness, domain:automation |
| #2764 fix(operations): harden Hermes session exporter for undated session files | no | implementation/test/fix language | bug, priority:high, cat:operations, cat:harness, domain:ai-orchestration, machine:dev-primary |
| #2880 feat(codex): make yolo-equivalent permission defaults travel across machines | no | existing codex agent label | enhancement, priority:high, cat:harness, domain:ai-config, machine:multi, agent:codex |
| #2484 feat(knowledge): extend staleness-scanner to cover yaml registries and llm-wiki assets (or defer via ADR) | no | implementation/test/fix language | enhancement, priority:medium, cat:harness, machine:dev-primary, dispatch:ready, gate:completeness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 5

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2733 epic: make Hermes agent memory canonical across all AI providers | yes | existing gemini agent label | priority:high, cat:ai-orchestration, machine:dev-primary, agent:gemini, agent:claude, agent:codex |
| #2498 chore(harness): #2364 plan branch drift recovery decision needed | no | research/triage/audit language | priority:medium, cat:harness, machine:dev-primary, dispatch:ready, gate:completeness, domain:harness |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness, machine:dev-primary, dispatch:ready, gate:completeness |
| #2679 R3 — Mooring: Industry practice (Vryhof, Bridon, MIRP, OMAE sessions) | no | research/triage/audit language | priority:medium, cat:engineering, cat:research, machine:dev-primary, dispatch:ready, gate:completeness |
| #2854 gap(memory): Hermes read-back leg missing — consolidated memory never flows back into ~/.hermes/memories (parallel to #2841 Codex) | no | research/triage/audit language | cat:ai-orchestration, domain:knowledge-management-platform |

