# Provider work queue

Generated: 2026-05-15T17:20:11.028931Z
Current week: 2026-W20
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved`. agent:* labels are routing hints only and do not grant execution approval.

## claude

- Routing priority: high
- Execution-ready candidates: 16
- Total routed candidates: 173

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2533 feat(repo-portfolio): review and revise mission/objective statements across active repos | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:repo-organization, status:plan-approved |
| #2563 Set up Telegram mobile access for Hermes AI control | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, domain:integrations, domain:notification |
| #2628 epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:harness, domain:testing, status:plan-approved |
| #2656 chore(repo-structure): normalize workspace-hub folder/file structure | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:harness, domain:repo-organization, status:plan-approved |
| #2657 chore(provider-session): remediate Hermes llm-wiki spinout path drift | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, cat:harness, status:plan-approved |
| #2665 feat(kanban): provider-credit approval dashboard and dispatch gates | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:agent-cost-tracking, status:plan-approved |
| #2685 Citation pilot contradiction: rule names orcaflex/mooring_design.py but file emits no Citation | yes | strategy/workflow/architecture language | bug, priority:high, cat:engineering, cat:knowledge-domain, status:plan-approved |
| #2686 Catenary solver canonicalization: 8 implementations, 4 numerically diverge, 5 shadows to delete | yes | strategy/workflow/architecture language | bug, priority:high, cat:engineering, cat:bugfix, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 4
- Total routed candidates: 24

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:blocked, agent:codex |
| #2403 feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large | yes | existing codex agent label | enhancement, priority:medium, cat:data-pipeline, cat:research, domain:document-intelligence, status:working |
| #2550 chore(security): codify public repo interaction-limit renewal in scheduled tasks | yes | existing codex agent label | enhancement, priority:medium, cat:operations, domain:automation, domain:security, agent:codex |
| #2327 digitalmodel: CadQuery spike for parametric offshore geometry generation | yes | existing codex agent label | priority:low, cat:engineering, cat:research, status:working, agent:codex, status:plan-approved |
| #2472 feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2474 feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2647 ANNOUNCE: llm-wiki spinout in progress (parallel-session heads-up) | no | implementation/test/fix language | priority:high |
| #2718 audit(hermes): kanban-worker dispatch hazards — parallel-spawn race + silent-hang (#2715-affected) | no | implementation/test/fix language | priority:high, cat:ai-orchestration, cat:harness, domain:agent-cost-tracking |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 3

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2498 chore(harness): #2364 plan branch drift recovery decision needed | no | research/triage/audit language | priority:medium, cat:harness |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |
| #2679 R3 — Mooring: Industry practice (Vryhof, Bridon, MIRP, OMAE sessions) | no | research/triage/audit language | priority:medium, cat:engineering, cat:research |

