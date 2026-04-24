# Provider work queue

Generated: 2026-04-24T05:20:10.092361Z
Current week: 2026-W17
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 12
- Total routed candidates: 169

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2348 triage: promote #1707/#1708/#1709 from review-backlog — live scanner has ToS/rate-limit exposure | yes | strategy/workflow/architecture language | bug, priority:high, domain:gtm, status:plan-approved |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:plan-approved |
| #2433 chore(ci-health): worldenergydata main CI — 22+ collection errors blocking 5 Dependabot PRs (#329-#333) | yes | strategy/workflow/architecture language | priority:high, cat:infrastructure, status:plan-approved |
| #2461 chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:documentation, cat:maintenance, domain:repo-organization, status:plan-approved |
| #2324 chore(memory): curate MEMORY.md index before 200-line truncation — consolidate stale project_* and feedback_* | yes | strategy/workflow/architecture language | priority:medium, cat:maintenance, domain:memory, status:plan-approved |
| #2403 feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:data-pipeline, cat:research, domain:document-intelligence, status:plan-approved |
| #2424 chore(ci-health): cross-repo CI audit — 6 of 7 ecosystem repos have red main CI | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:infrastructure, maintenance, status:plan-approved |
| #2459 follow-up(ci): assethold python-tests still red after smoke unblock — lint/mypy/quality-gate hardening | yes | strategy/workflow/architecture language | priority:medium, cat:infrastructure, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 3
- Total routed candidates: 29

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2462 feat(digitalmodel): repo-wide operator map and canonical routing surfaces beyond OrcaWave/OrcaFlex | yes | implementation/test/fix language | enhancement, priority:high, cat:engineering, cat:documentation, domain:repo-organization, status:plan-approved |
| #2458 feat(canonical-spec): promote named OrcaWave multi-body benchmark fixture for roundtrip and handoff readiness | yes | implementation/test/fix language | enhancement, priority:medium, cat:engineering, domain:marine, machine:dev-primary, status:plan-approved |
| #2464 chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise | yes | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness, domain:repo-organization, status:plan-approved |
| #2472 feat(canonical-spec): validate CALM/SPM buoy OrcaFlex semantic proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2474 feat(canonical-spec): add OrcaFlex native reverse-parser equivalence proof | no | implementation/test/fix language | enhancement, priority:high, cat:engineering, domain:marine, machine:dev-primary |
| #2194 feat(reporting): emit cross-tool reporter delta artifacts against previous weekly baseline | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2195 test(reporting): add publication recovery state-machine transition suite for staged/gated/recoverable flows | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2199 feat(claude): validate hook wiring and backfill session_id parity for historical provider-audit coverage | no | implementation/test/fix language | enhancement, priority:medium, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |

