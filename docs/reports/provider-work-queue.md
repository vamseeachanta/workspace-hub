# Provider work queue

Generated: 2026-04-20T13:20:06.765998Z
Current week: 2026-W17
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 10
- Total routed candidates: 152

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2342 fix(gtm): publish detail pages for Demos 1-4 to aceengineer.com (currently 404) | yes | strategy/workflow/architecture language | priority:high, cat:business, domain:gtm, status:plan-approved |
| #2152 test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:operations, cat:harness, status:plan-approved |
| #2206 feat(knowledge): validate single-source-of-truth pyramid conformance across intelligence assets and execution workflows | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved |
| #2207 feat(doc-intel): define standards/codes provenance + reuse contract for llm-wiki promotion | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:data-pipeline, cat:documentation, status:plan-approved |
| #2209 chore(knowledge): define durable-vs-transient knowledge boundary across wikis, issues, registries, and session artifacts | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved |
| #2320 chore(skills): mine session logs for dead-skill candidates — usage-signal input to #2280 weekly audit | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:skills, domain:skills, status:plan-approved |
| #2322 chore(rules): promote binary-checkable .claude/rules/*.md prose to Level 2 scripts per enforcement gradient | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:harness, domain:agent-discipline, status:plan-approved |
| #2323 feat(review): single-command cross-AI plan-review fan-out (Claude + Codex + Gemini) with disagreement capture | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:ai-orchestration, domain:ai-orchestration, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 47

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2343 fix(gtm): demo gallery links only to Demo 5 — wire remaining 4 detail-page links | yes | implementation/test/fix language | priority:high, domain:gtm, status:plan-approved |
| #2149 feat(knowledge): generate seeded intelligence accessibility registry from existing inventories | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2157 feat(operations): implement native PowerShell probe collector for Windows readiness bundles | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2158 feat(operations): add Git Bash launcher and path-normalization bridge for Windows evidence writer | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2161 feat(knowledge): ingest provider-session ecosystem audit reads into seeded accessibility registry | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2162 feat(schema): define machine/path alias schema for seeded accessibility registry entries | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2163 feat(operations): add Windows Task Scheduler invocation harness for readiness evidence runs | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2164 test(operations): build cygpath/native-path fixture suite for Windows launcher bridge | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 1

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |

