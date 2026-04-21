# Provider work queue

Generated: 2026-04-21T01:20:06.327103Z
Current week: 2026-W17
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 15
- Total routed candidates: 158

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2348 triage: promote #1707/#1708/#1709 from review-backlog — live scanner has ToS/rate-limit exposure | yes | strategy/workflow/architecture language | bug, priority:high, domain:gtm, status:plan-approved |
| #2402 feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier) | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:data-pipeline, domain:document-intelligence, status:plan-review, status:plan-approved |
| #2408 feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:ai-orchestration, cat:harness, domain:release-management, status:plan-approved |
| #2206 feat(knowledge): validate single-source-of-truth pyramid conformance across intelligence assets and execution workflows | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved |
| #2207 feat(doc-intel): define standards/codes provenance + reuse contract for llm-wiki promotion | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:data-pipeline, cat:documentation, status:plan-approved |
| #2209 chore(knowledge): define durable-vs-transient knowledge boundary across wikis, issues, registries, and session artifacts | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved |
| #2320 chore(skills): mine session logs for dead-skill candidates — usage-signal input to #2280 weekly audit | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:skills, domain:skills, status:plan-approved |
| #2322 chore(rules): promote binary-checkable .claude/rules/*.md prose to Level 2 scripts per enforcement gradient | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:agent-discipline, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 40

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2161 feat(knowledge): ingest provider-session ecosystem audit reads into seeded accessibility registry | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2162 feat(schema): define machine/path alias schema for seeded accessibility registry entries | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2163 feat(operations): add Windows Task Scheduler invocation harness for readiness evidence runs | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2164 test(operations): build cygpath/native-path fixture suite for Windows launcher bridge | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2167 test(knowledge): build session-read coherence golden fixture suite for alias, symbolic, and missing-path cases | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2169 feat(operations): define Windows licensed-tool probe adapter contract for readiness bundles | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2171 test(reporting): add end-to-end weekly publication smoke scenarios for latest/history bundle assembly | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2173 feat(knowledge): wire provider-session ecosystem audit into weekly registry build manifest and publication bundle | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 2

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2346 feat(gtm): prospect-data customized-demo pipeline — 48hr turnaround + pre-staged vessel templates | yes | research/triage/audit language | priority:high, cat:engineering, domain:gtm, status:plan-approved |
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |

