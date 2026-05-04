# Provider work queue

Generated: 2026-05-04T02:25:26.680270Z
Current week: 2026-W19
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 6
- Total routed candidates: 162

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2479 fix(review): Codex stdin-hang regression post-#2406 closure (size-dependent) | yes | strategy/workflow/architecture language | bug, priority:high, cat:harness, domain:knowledge-management, status:plan-approved |
| #2532 fix(ci): repair PR review/stage-prompt guard environment failures | yes | strategy/workflow/architecture language | bug, priority:high, cat:harness, domain:review, status:plan-approved |
| #2533 feat(repo-portfolio): review and revise mission/objective statements across active repos | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:repo-organization, status:plan-approved |
| #2563 Set up Telegram mobile access for Hermes AI control | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:operations, domain:integrations, domain:notification |
| #2229 feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live | yes | existing claude agent label | enhancement, priority:medium, cat:harness, status:working, machine:licensed-win-1, agent:claude |
| #2552 docs(security): external contributor and unsolicited paid-help response runbook | yes | strategy/workflow/architecture language | documentation, priority:medium, cat:documentation, domain:security, status:plan-approved |
| #2431 Compliance alert: W17 — 20% (critical) | no | strategy/workflow/architecture language | priority:high, priority:critical, compliance-alert |
| #2517 Compliance alert: W18 — 42% (high) | no | strategy/workflow/architecture language | priority:high, priority:medium, priority:critical, compliance-alert |

## codex

- Routing priority: highest
- Execution-ready candidates: 13
- Total routed candidates: 36

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | existing codex agent label | priority:high, cat:engineering, domain:gtm, status:working, agent:codex, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |
| #2523 feat(workstations): add reusable Hermes preflight readiness checker | yes | implementation/test/fix language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:ai-orchestration, domain:workstations |
| #2270 feat(blender): standardize headless baseline workflow and smoke render validation | yes | existing codex agent label | enhancement, priority:medium, cat:engineering, cat:documentation, status:working, machine:dev-secondary |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

