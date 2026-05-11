# workspace-hub — domain:knowledge-management Kanban Board

Generated: 2026-05-11

Open issues: **20**

## Lane counts

| Value | Count |
| --- | ---: |
| Planning Needed | 18 |
| Plan Review / Cross-Review | 1 |
| Triage / Intake | 1 |

## Execution ownership defaults

| AI provider route | Machine route | Issue count |
| --- | --- | ---: |
| Claude planner; Gemini research support | ace-linux-1 | 9 |
| Codex | ace-linux-1 | 7 |
| Claude | ace-linux-1 | 2 |
| Claude + Gemini/Codex cross-review | ace-linux-1 control surface | 1 |
| Gemini research; Claude synthesis | ace-linux-1 | 1 |

## Issues

| Issue | Lane | Domain | AI provider / review owner | Machine | Labels |
| --- | --- | --- | --- | --- | --- |
| [#2632 META: rebind 3 llm-wiki plan-approved issues stuck on missing approval markers (#2368/#2124/#2125)](https://github.com/vamseeachanta/workspace-hub/issues/2632) | Plan Review / Cross-Review | domain:knowledge-management | Claude + Gemini/Codex cross-review | ace-linux-1 control surface | priority:medium, cat:knowledge-domain, domain:knowledge-management, status:plan-review |
| [#2293 fix(wiki-ingest): make nightly ingest idempotent and push-status truthful](https://github.com/vamseeachanta/workspace-hub/issues/2293) | Triage / Intake | domain:knowledge-management | Gemini research; Claude synthesis | ace-linux-1 | bug, priority:medium, cat:harness, domain:knowledge-management |
| [#102 WRK-1331: GitHub Issue body template renderer (update-github-issue.py)](https://github.com/vamseeachanta/workspace-hub/issues/102) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:codex |
| [#103 WRK-1332: Archive synthesis + knowledge backfill (synthesize-archive.py)](https://github.com/vamseeachanta/workspace-hub/issues/103) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:codex |
| [#104 WRK-1333: Wire Issue updater into stage lifecycle (replace HTML gen)](https://github.com/vamseeachanta/workspace-hub/issues/104) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:codex |
| [#105 WRK-1334: Delete HTML infrastructure (generator, sub-skills, files)](https://github.com/vamseeachanta/workspace-hub/issues/105) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:codex |
| [#106 WRK-1335: Patch archive-item.sh for ongoing GitHub Issue creation](https://github.com/vamseeachanta/workspace-hub/issues/106) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:codex |
| [#107 WRK-1336: Bulk review 38 existing open issues + roadmap update](https://github.com/vamseeachanta/workspace-hub/issues/107) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:codex |
| [#2040 feat: cronize engineering wiki incremental ingest](https://github.com/vamseeachanta/workspace-hub/issues/2040) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, cat:harness, domain:knowledge-management |
| [#2067 feat(knowledge): wire .planning/research into engineering wiki nightly ingest](https://github.com/vamseeachanta/workspace-hub/issues/2067) | Planning Needed | domain:knowledge-management | Claude | ace-linux-1 | enhancement, priority:high, cat:harness, domain:knowledge-management, agent:claude |
| [#2068 feat(knowledge): add cross-link JSONL package for wiki-to-standard and wiki-to-module intelligence](https://github.com/vamseeachanta/workspace-hub/issues/2068) | Planning Needed | domain:knowledge-management | Claude | ace-linux-1 | enhancement, priority:medium, cat:harness, domain:knowledge-management, agent:claude |
| [#2123 feat(llm-wiki): add llm-wiki search to OrcaFlex/OrcaWave agent skill invocation](https://github.com/vamseeachanta/workspace-hub/issues/2123) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:low, cat:harness, domain:knowledge-management |
| [#2141 Add fixture-backed tests for llm-wiki ingest and search scripts](https://github.com/vamseeachanta/workspace-hub/issues/2141) | Planning Needed | domain:knowledge-management | Codex | ace-linux-1 | priority:medium, cat:harness, domain:knowledge-management, agent:codex |
| [#2370 feat(knowledge): build closed-issue promotion ledger for engineering wiki ingest](https://github.com/vamseeachanta/workspace-hub/issues/2370) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:high, cat:data-pipeline, domain:knowledge-management |
| [#2374 feat(knowledge): build transient-promotion candidate queue from handoffs and review artifacts](https://github.com/vamseeachanta/workspace-hub/issues/2374) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:high, cat:data-pipeline, cat:harness, domain:knowledge-management |
| [#2382 feat(conformance): add promotion audit-trail checker for L5/L6→L3 wiki promotions](https://github.com/vamseeachanta/workspace-hub/issues/2382) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:data-pipeline, cat:harness, domain:knowledge-management |
| [#2383 feat(conformance): implement GUARD-1 invented-layer detector for intelligence/governance docs](https://github.com/vamseeachanta/workspace-hub/issues/2383) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:harness, domain:knowledge-management |
| [#2384 feat(governance): add promotion-aware recurring-run output pruner](https://github.com/vamseeachanta/workspace-hub/issues/2384) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:harness, domain:knowledge-management |
| [#2470 feat(acma-codes): produce readable source-grounded summaries for OCIMF/CSA wiki promotion](https://github.com/vamseeachanta/workspace-hub/issues/2470) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:data-pipeline, cat:documentation, domain:knowledge-management |
| [#2485 feat(enforcement): mechanical linter + ledger for llm-wiki → GTM boundary (enforces #2482 policy)](https://github.com/vamseeachanta/workspace-hub/issues/2485) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:harness, domain:knowledge-management |
