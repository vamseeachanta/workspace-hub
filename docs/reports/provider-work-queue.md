# Provider work queue

Generated: 2026-05-05T21:20:08.204931Z
Current week: 2026-W19
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 4
- Total routed candidates: 163

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2533 feat(repo-portfolio): review and revise mission/objective statements across active repos | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:repo-organization, status:plan-approved |
| #2563 Set up Telegram mobile access for Hermes AI control | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, domain:integrations, domain:notification |
| #2628 epic(digitalmodel-ci): domain-divided CI architecture replacing maxfail-masking pattern | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:harness, domain:testing, status:plan-approved |
| #2552 docs(security): external contributor and unsolicited paid-help response runbook | yes | strategy/workflow/architecture language | documentation, priority:medium, cat:documentation, domain:security, status:plan-approved |
| #2431 Compliance alert: W17 — 20% (critical) | no | strategy/workflow/architecture language | priority:high, priority:critical, compliance-alert |
| #2517 Compliance alert: W18 — 42% (high) | no | strategy/workflow/architecture language | priority:high, priority:medium, priority:critical, compliance-alert |
| #2519 feat(hermes): orchestrate AI provider usage and workstation dispatch | no | strategy/workflow/architecture language | enhancement, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations |
| #2520 fix(workstations): repair and gate ace-linux-2 GitHub auth before delegation | no | strategy/workflow/architecture language | bug, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations |

## codex

- Routing priority: highest
- Execution-ready candidates: 11
- Total routed candidates: 35

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | existing codex agent label | priority:high, cat:engineering, domain:gtm, status:working, agent:codex, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |
| #2523 feat(workstations): add reusable Hermes preflight readiness checker | yes | implementation/test/fix language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:ai-orchestration, domain:workstations |
| #2403 feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large | yes | existing codex agent label | enhancement, priority:medium, cat:data-pipeline, cat:research, domain:document-intelligence, status:working |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

