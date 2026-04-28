# Provider work queue

Generated: 2026-04-28T05:20:17.257717Z
Current week: 2026-W18
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 7
- Total routed candidates: 156

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:documentation, machine:dev-secondary, status:plan-approved |
| #2289 Plan rollback/recovery for enforcement bypasses detected after commit or push | yes | strategy/workflow/architecture language | priority:high, cat:harness, domain:workflow, status:plan-approved |
| #2229 feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live | yes | existing claude agent label | enhancement, priority:medium, cat:harness, machine:licensed-win-1, agent:claude, status:plan-approved |
| #2270 feat(blender): standardize headless baseline workflow and smoke render validation | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:engineering, cat:documentation, machine:dev-secondary, status:plan-approved |
| #2271 feat(ecosystem): harden shared-skill propagation for engineering portability | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, machine:multi, status:plan-approved |
| #2272 test(portability): add repeatable OpenFOAM and Blender smoke verification | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:engineering, cat:harness, machine:multi, status:plan-approved |
| #2327 digitalmodel: CadQuery spike for parametric offshore geometry generation | yes | strategy/workflow/architecture language | priority:low, cat:engineering, cat:research, status:plan-approved |
| #2431 Compliance alert: W17 — 20% (critical) | no | strategy/workflow/architecture language | priority:high, priority:critical, compliance-alert |

## codex

- Routing priority: highest
- Execution-ready candidates: 18
- Total routed candidates: 41

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | existing codex agent label | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:working, agent:codex |
| #2369 feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:working, agent:codex |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | existing codex agent label | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:working, agent:codex |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | existing codex agent label | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:working |
| #2433 chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (#329-#333) | yes | existing codex agent label | priority:high, cat:infrastructure, status:working, agent:codex, status:plan-approved |
| #2462 feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex | yes | existing codex agent label | enhancement, priority:high, cat:engineering, cat:documentation, domain:repo-organization, status:working |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 3

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

