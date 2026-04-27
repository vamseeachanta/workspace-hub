# Provider work queue

Generated: 2026-04-27T05:20:08.340267Z
Current week: 2026-W18
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 25
- Total routed candidates: 170

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:documentation, machine:dev-secondary, status:plan-approved |
| #2289 Plan rollback/recovery for enforcement bypasses detected after commit or push | yes | strategy/workflow/architecture language | priority:high, cat:harness, domain:workflow, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:plan-approved |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:plan-approved |
| #2369 feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:plan-approved |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 4
- Total routed candidates: 27

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2462 feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex | yes | implementation/test/fix language | enhancement, priority:high, cat:engineering, cat:documentation, domain:repo-organization, status:plan-approved |
| #2227 feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis | yes | existing codex agent label | enhancement, priority:medium, cat:documentation, agent:codex, status:plan-approved |
| #2458 feat(canonical-spec): promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness | yes | implementation/test/fix language | enhancement, priority:medium, cat:engineering, domain:marine, machine:dev-primary, status:plan-approved |
| #2464 chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise | yes | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness, domain:repo-organization, status:plan-approved |
| #2472 feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2474 feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2215 feat(analysis): add migration-debt trend snapshots to provider-session audit | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness, domain:reporting |
| #2221 feat(daily-report): refresh stale data sources and complete reflect pipeline | no | implementation/test/fix language | priority:medium, cat:ai-orchestration |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 3

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2501 chore(planning): #2105 governance-lock — handoff vs live-state discrepancy | no | research/triage/audit language | priority:medium, cat:documentation, cat:harness |

