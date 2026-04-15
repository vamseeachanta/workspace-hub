# Provider work queue

Generated: 2026-04-15T01:20:07.381059Z
Current week: 2026-W16
Recommended provider order: gemini, codex, claude

Execution-ready means the issue already carries `status:plan-approved` or an explicit agent label.

## claude

- Routing priority: high
- Execution-ready candidates: 17
- Total routed candidates: 137

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2055 feat(field-dev): subsea cost benchmarking from SubseaIQ equipment counts | yes | existing claude agent label | enhancement, priority:high, cat:engineering, wip:ace-linux-1, dark-intelligence, agent:claude |
| #2269 feat(openfoam): standardize ESI v2312 baseline workflow and validation | yes | strategy/workflow/architecture language | enhancement, priority:high, cat:engineering, cat:documentation, machine:dev-secondary, status:plan-approved |
| #2046 Audit compliance of strict issue planning workflow after rollout | yes | strategy/workflow/architecture language | priority:medium, cat:ai-orchestration, cat:operations, status:plan-approved |
| #2105 chore(knowledge): define freshness cadences and staleness signals for intelligence assets | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved |
| #2129 chore(harness): automate issue-state drift and redundancy audit across GitHub + analysis artifacts | yes | existing claude agent label | enhancement, priority:medium, cat:ai-orchestration, cat:harness, agent:claude, status:plan-approved |
| #2152 test(reporting): add golden fixture corpus for weekly review run artifacts and validator coverage | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:operations, cat:harness, status:plan-approved |
| #2206 feat(knowledge): validate single-source-of-truth pyramid conformance across intelligence assets and execution workflows | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved |
| #2207 feat(doc-intel): define standards/codes provenance + reuse contract for llm-wiki promotion | yes | strategy/workflow/architecture language | enhancement, priority:medium, cat:data-pipeline, cat:documentation, status:plan-approved |

## codex

- Routing priority: highest
- Execution-ready candidates: 1
- Total routed candidates: 57

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2227 feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis | yes | existing codex agent label | enhancement, priority:medium, cat:documentation, agent:codex, status:plan-approved |
| #2118 chore(gtm): run all 5 demos end-to-end and validate HTML reports | no | implementation/test/fix language | priority:high, cat:engineering, domain:gtm |
| #2037 feat(gtm): manim mooring layout / force explainer animation | no | implementation/test/fix language | enhancement, priority:medium, cat:business, domain:gtm |
| #2038 feat(gtm): manim installation sequence / operability envelope animation | no | implementation/test/fix language | enhancement, priority:medium, cat:business, domain:gtm |
| #2149 feat(knowledge): generate seeded intelligence accessibility registry from existing inventories | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |
| #2157 feat(operations): implement native PowerShell probe collector for Windows readiness bundles | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2158 feat(operations): add Git Bash launcher and path-normalization bridge for Windows evidence writer | no | implementation/test/fix language | enhancement, priority:medium, cat:operations, cat:harness |
| #2161 feat(knowledge): ingest provider-session ecosystem audit reads into seeded accessibility registry | no | implementation/test/fix language | enhancement, priority:medium, cat:documentation, cat:harness |

## gemini

- Routing priority: highest
- Execution-ready candidates: 0
- Total routed candidates: 6

| Issue | Ready | Why routed here | Labels |
|---|---|---|---|
| #2116 feat(gtm): aceengineer.com demo gallery page — embed GIFs + report links | no | research/triage/audit language | enhancement, priority:high, cat:business, domain:gtm |
| #2039 feat: engineering wiki — ingest remaining high-value sources (skills metadata, closed issues) | no | research/triage/audit language | enhancement, priority:medium, domain:knowledge-management |
| #2041 chore: add LaTeX to manim-env for MathTex rendering | no | research/triage/audit language | enhancement, priority:low |
| #2042 feat: engineering wiki — ingest skill metadata as wiki pages | no | research/triage/audit language | enhancement, cat:harness, domain:knowledge-management |
| #2123 feat(llm-wiki): add llm-wiki search to OrcaFlex/OrcaWave agent skill invocation | no | research/triage/audit language |  |
| #2125 feat(llm-wiki): auto-refresh ingestion on new Orcina releases | no | research/triage/audit language |  |

