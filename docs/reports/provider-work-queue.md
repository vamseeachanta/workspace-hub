# Provider work queue

Generated: 2026-04-17T13:20:08.384485Z
Current week: 2026-W16
Recommended provider order: codex, gemini, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 3
- Total routed candidates: 142

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2152 test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:operations, cat:harness, status:plan-approved |
| #2309 Add summary_file_exists field (decouple existence from content-quality, follow-up to #1878) | yes | strategy/workflow/architecture language | priority:low, cat:document-intelligence, status:plan-approved |
| #2070 Guard Claude state sync against oversized session-signal files | yes | strategy/workflow/architecture language | status:plan-approved |
| #2251 Compliance alert: W16 — 0% (critical) | no | strategy/workflow/architecture language | priority:medium, priority:critical, compliance-alert |
| #2066 fix(knowledge): build-knowledge-index ingest multiline learned-patterns with stable IDs | no | existing claude agent label | bug, priority:high, cat:harness, domain:knowledge-management, agent:claude |
| #2067 feat(knowledge): wire .planning/research into engineering wiki nightly ingest | no | existing claude agent label | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:claude |
| #2112 data(field-dev): backfill SubseaIQ equipment counts to unblock cost benchmarking | no | existing claude agent label | enhancement, priority:high, cat:engineering, agent:claude |
| #2219 chore(sync): resolve main branch divergence — 9 local vs 134 origin commits | no | strategy/workflow/architecture language | priority:high, cat:engineering |

## codex

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 55

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2149 feat(knowledge): generate seeded intelligence accessibility registry from existing inventories | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2157 feat(operations): implement native PowerShell probe collector for Windows readiness bundles | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2158 feat(operations): add Git Bash launcher and path-normalization bridge for Windows evidence writer | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2161 feat(knowledge): ingest provider-session ecosystem audit reads into seeded accessibility registry | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2162 feat(schema): define machine/path alias schema for seeded accessibility registry entries | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2163 feat(operations): add Windows Task Scheduler invocation harness for readiness evidence runs | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2164 test(operations): build cygpath/native-path fixture suite for Windows launcher bridge | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2167 test(knowledge): build session-read coherence golden fixture suite for alias, symbolic, and missing-path cases | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 3

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2295 WRK: 2025 TX franchise No Tax Due + PIR — SKEstates and AceEngineer | no | research/triage/audit language | enhancement, priority:high, cat:personal-finance, domain:tax-preparation |
| #2123 feat(llm-wiki): add llm-wiki search to OrcaFlex/OrcaWave agent skill invocation | no | research/triage/audit language |  |
| #2125 feat(llm-wiki): auto-refresh ingestion on new Orcina releases | no | research/triage/audit language |  |

