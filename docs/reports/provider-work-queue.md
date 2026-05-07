# Provider work queue

Generated: 2026-05-07T17:20:09.919448Z
Current week: 2026-W19
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 5
- Total routed candidates: 166

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2533 feat(repo-portfolio): review and revise mission/objective statements across active repos | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:repo-organization, status:plan-approved |
| #2563 Set up Telegram mobile access for Hermes AI control | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, domain:integrations, domain:notification |
| #2628 epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:harness, domain:testing, status:plan-approved |
| #2229 feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live | yes | existing claude agent label | enhancement, priority:medium, cat:harness, status:working, machine:licensed-win-1, agent:claude |
| #2552 docs(security): external contributor and unsolicited paid-help response runbook | yes | strategy/workflow/architecture language | documentation, priority:medium, cat:documentation, domain:security, status:plan-approved |
| #2431 Compliance alert: W17 — 20% (critical) | no | strategy/workflow/architecture language | priority:high, priority:critical, compliance-alert |
| #2517 Compliance alert: W18 — 42% (high) | no | strategy/workflow/architecture language | priority:high, priority:medium, priority:critical, compliance-alert |
| #2519 feat(hermes): orchestrate AI provider usage and workstation dispatch | no | strategy/workflow/architecture language | enhancement, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations |

## codex

- Routing priority: highest
- Execution-ready candidates: 6
- Total routed candidates: 31

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |
| #2523 feat(workstations): add reusable Hermes preflight readiness checker | yes | implementation/test/fix language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:ai-orchestration, domain:workstations |
| #2403 feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large | yes | existing codex agent label | enhancement, priority:medium, cat:data-pipeline, cat:research, domain:document-intelligence, status:working |
| #2550 chore(security): codify public repo interaction-limit renewal in scheduled tasks | yes | implementation/test/fix language | enhancement, priority:medium, cat:operations, domain:automation, domain:security, status:plan-approved |
| #2327 digitalmodel: CadQuery spike for parametric offshore geometry generation | yes | existing codex agent label | priority:low, cat:engineering, cat:research, status:working, agent:codex, status:plan-approved |
| #2472 feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2474 feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 3

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2498 chore(harness): #2364 plan branch drift recovery decision needed | no | research/triage/audit language | priority:medium, cat:harness |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

