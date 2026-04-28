# Provider work queue

Generated: 2026-04-28T13:20:11.958185Z
Current week: 2026-W18
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 1
- Total routed candidates: 155

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2229 feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live | yes | existing claude agent label | enhancement, priority:medium, cat:harness, status:working, machine:licensed-win-1, agent:claude |
| #2431 Compliance alert: W17 — 20% (critical) | no | strategy/workflow/architecture language | priority:high, priority:critical, compliance-alert |
| #2519 feat(hermes): orchestrate AI provider usage and workstation dispatch | no | strategy/workflow/architecture language | enhancement, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations |
| #2520 fix(workstations): repair and gate ace-linux-2 GitHub auth before delegation | no | strategy/workflow/architecture language | bug, cat:ai-orchestration, cat:harness, priority:critical, domain:ai-orchestration, domain:workstations |
| #2219 chore(sync): resolve main branch divergence — 9 local vs 134 origin commits | no | strategy/workflow/architecture language | priority:high, cat:engineering |
| #2254 fix(provider-telemetry): improve Claude and Gemini quota observability for exact weekly targeting | no | strategy/workflow/architecture language | bug, priority:high, cat:harness, domain:agent-cost-tracking |
| #2291 fix(cron-health): harden failure detection and align task evidence contracts | no | strategy/workflow/architecture language | bug, priority:high, cat:operations, cat:harness |
| #2301 bug(hermes): classify and recover from openai-codex transport/challenge failures | no | strategy/workflow/architecture language | bug, priority:high, cat:ai-orchestration, cat:harness |

## codex

- Routing priority: highest
- Execution-ready candidates: 19
- Total routed candidates: 43

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, status:working, machine:dev-secondary |
| #2289 Plan rollback/recovery for enforcement bypasses detected after commit or push | yes | existing codex agent label | priority:high, cat:harness, domain:workflow, status:working, agent:codex, status:plan-approved |
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | existing codex agent label | priority:high, cat:engineering, domain:gtm, status:working, agent:codex, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2369 feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

