# Provider work queue

Generated: 2026-04-25T17:20:09.513239Z
Current week: 2026-W17
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 19
- Total routed candidates: 168

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2348 triage: promote #1707/#1708/#1709 from review-backlog — live scanner has ToS/rate-limit exposure | yes | strategy/workflow/architecture language | bug, priority:high, domain:gtm, status:plan-approved |
| #2364 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:plan-approved |
| #2368 feat(knowledge): generate faceted portal pages for large LLM-wiki domains | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, domain:knowledge-management, status:plan-approved |
| #2369 feat(knowledge): execute Batch Pack 2 to promote indexed conference summaries into wiki topic stubs | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved |
| #2373 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management, status:plan-approved |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:plan-approved |
| #2433 chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (#329-#333) | yes | strategy/workflow/architecture language | priority:high, cat:infrastructure, status:plan-approved |
| #2461 chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, cat:maintenance, domain:repo-organization, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 4
- Total routed candidates: 30

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2462 feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex | yes | implementation/test/fix language | enhancement, priority:high, cat:engineering, cat:documentation, domain:repo-organization, status:plan-approved |
| #2227 feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis | yes | existing codex agent label | enhancement, priority:medium, cat:documentation, agent:codex, status:plan-approved |
| #2458 feat(canonical-spec): promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness | yes | implementation/test/fix language | enhancement, priority:medium, cat:engineering, domain:marine, machine:dev-primary, status:plan-approved |
| #2464 chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise | yes | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness, domain:repo-organization, status:plan-approved |
| #2472 feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2474 feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2194 feat(reporting): emit cross-tool reporter delta artifacts against previous weekly baseline | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2195 test(reporting): add publication recovery state-machine transition suite for staged/gated/recoverable flows | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |

