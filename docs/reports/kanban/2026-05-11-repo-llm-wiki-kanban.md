# llm-wiki Kanban Boards

Generated: 2026-05-11

Open issues: **36**

## Lane counts

| Value | Count |
| --- | ---: |
| Planning Needed | 17 |
| Ready / Plan Approved | 12 |
| Decision / User Input | 4 |
| Plan Review / Cross-Review | 3 |

## Domain board index

- [domain:knowledge-management](2026-05-11-repo-llm-wiki-domain-domain-knowledge-management-kanban.md) — 19 issues
- [cat:engineering](2026-05-11-repo-llm-wiki-domain-cat-engineering-kanban.md) — 10 issues
- [cat:data](2026-05-11-repo-llm-wiki-domain-cat-data-kanban.md) — 2 issues
- [cat:documentation](2026-05-11-repo-llm-wiki-domain-cat-documentation-kanban.md) — 2 issues
- [domain:knowledge](2026-05-11-repo-llm-wiki-domain-domain-knowledge-kanban.md) — 2 issues
- [domain:maritime-law](2026-05-11-repo-llm-wiki-domain-domain-maritime-law-kanban.md) — 1 issues

## Standing gates for this repo

- Decision gate: unresolved user choices stay in Decision / User Input or Plan Review lanes.
- Structure gate: planned file placement must match repo routing docs and existing package layout.
- Test/CI gate: every implementation card names tests/build/CI checks before execution and records results before closeout.
- Cross-review gate: plans and artifacts are reviewed by at least one non-implementing provider before closeout; engineering-critical work scales to multi-provider review.

## Issue board (all open issues)

| Issue | Lane | Domain | AI provider / review owner | Machine | Labels |
| --- | --- | --- | --- | --- | --- |
| [#14 feat(llm-wiki): plan curated SESA LNG corpus extraction from Elements](https://github.com/vamseeachanta/llm-wiki/issues/14) | Decision / User Input | domain:knowledge-management | Claude + Gemini/Codex cross-review | ace-linux-1 control surface | priority:medium, status:plan-approved, status:blocked, cat:data-pipeline, domain:knowledge-management, domain:marine |
| [#19 feat(llm-wiki): plan offshore raw-source family wiki backfill candidates from /mnt/ace-data](https://github.com/vamseeachanta/llm-wiki/issues/19) | Decision / User Input | domain:knowledge-management | Claude + Gemini/Codex cross-review | ace-linux-1 control surface | priority:medium, status:plan-approved, status:blocked, cat:data-pipeline, domain:knowledge-management, domain:document-intelligence, llm-wiki |
| [#25 feat(knowledge): execute Batch Pack 1 to promote API/standards-portal metadata into thin wiki domains](https://github.com/vamseeachanta/llm-wiki/issues/25) | Decision / User Input | domain:knowledge-management | Codex | ace-linux-1 control surface | enhancement, priority:high, status:plan-approved, status:blocked, cat:documentation, domain:knowledge-management, agent:codex |
| [#26 feat(knowledge): execute Batch Pack 4 for non-ACMA standards summary promotion](https://github.com/vamseeachanta/llm-wiki/issues/26) | Decision / User Input | domain:knowledge-management | Codex | ace-linux-1 control surface | enhancement, priority:high, status:plan-approved, status:blocked, cat:data-pipeline, domain:knowledge-management, agent:codex |
| [#40 Research: reservoir engineering literature — local /mnt/ace + online; ingest to llm-wiki](https://github.com/vamseeachanta/llm-wiki/issues/40) | Plan Review / Cross-Review | domain:knowledge-management | Claude + Gemini/Codex cross-review | ace-linux-1 control surface | documentation, enhancement, status:plan-review |
| [#41 feat(llm-wiki): implement maritime-law standards routing for conventions](https://github.com/vamseeachanta/llm-wiki/issues/41) | Plan Review / Cross-Review | domain:knowledge-management | Claude + Gemini/Codex cross-review | ace-linux-1 control surface | status:plan-review, cat:documentation, domain:knowledge-management |
| [#42 feat(llm-wiki): implement LNG-projects standards routing](https://github.com/vamseeachanta/llm-wiki/issues/42) | Plan Review / Cross-Review | domain:knowledge-management | Claude + Gemini/Codex cross-review | ace-linux-1 control surface | status:plan-review, cat:documentation, domain:knowledge-management |
| [#1 WRK-1245: Full corpus intelligence extraction — summaries, data, methodologies, test cases from 426K documents](https://github.com/vamseeachanta/llm-wiki/issues/1) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:engineering, status:plan-approved |
| [#2 WRK-1246: Assess deep extraction yield across text-extractable corpus — tables, charts, equations](https://github.com/vamseeachanta/llm-wiki/issues/2) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:engineering, status:plan-approved |
| [#3 WRK-1253: Batch deep extraction — XLS/XLSX files (11,741 docs, 93% table yield)](https://github.com/vamseeachanta/llm-wiki/issues/3) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:low, cat:engineering, status:plan-approved |
| [#4 WRK-1255: Batch deep extraction — large standards PDFs >1MB (1,500 machine-readable)](https://github.com/vamseeachanta/llm-wiki/issues/4) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:engineering, status:plan-approved |
| [#5 WRK-1257: Chart image extraction — extract actual images from PDFs, not just metadata](https://github.com/vamseeachanta/llm-wiki/issues/5) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:medium, cat:engineering, status:plan-approved |
| [#6 WRK-1292: Enrich research briefs with key equations and worked examples from downloaded PDFs](https://github.com/vamseeachanta/llm-wiki/issues/6) | Ready / Plan Approved | cat:data | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:medium, cat:data, status:plan-approved |
| [#7 WRK-1295: Batch LLM summaries — ace_standards + workspace_spec (4,685 docs, Phase 1 of WRK-1245)](https://github.com/vamseeachanta/llm-wiki/issues/7) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:engineering, status:plan-approved |
| [#8 WRK-1296: Batch deep extraction — ace-linux-1 machine-readable PDFs (154K docs, local disk)](https://github.com/vamseeachanta/llm-wiki/issues/8) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:engineering, status:plan-approved |
| [#9 WRK-1297: Batch deep extraction — ace-linux-2 machine-readable PDFs (125K docs, local NTFS)](https://github.com/vamseeachanta/llm-wiki/issues/9) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:engineering, status:plan-approved |
| [#10 WRK-1298: OCR pipeline — ace-linux-2 scanned PDFs (39K docs, GPU-accelerated)](https://github.com/vamseeachanta/llm-wiki/issues/10) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:medium, cat:engineering, status:plan-approved |
| [#11 WRK-1299: OCR pipeline — ace-linux-1 scanned PDFs (53K docs)](https://github.com/vamseeachanta/llm-wiki/issues/11) | Ready / Plan Approved | cat:engineering | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:medium, cat:engineering, status:plan-approved |
| [#12 WRK-280: ABS standards acquisition: create folder + download CP Guidance Notes](https://github.com/vamseeachanta/llm-wiki/issues/12) | Ready / Plan Approved | cat:data | Codex for bounded edits; Claude for orchestration | ace-linux-1 | enhancement, wrk-item, priority:high, cat:data, status:plan-approved |
| [#13 epic(knowledge): llm-wiki strengthening roadmap and execution waves](https://github.com/vamseeachanta/llm-wiki/issues/13) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:high, cat:documentation, domain:knowledge-management |
| [#20 feat(llm-wiki): backfill engineering-wiki reverse cross-links to Tier C riser/pipeline pages](https://github.com/vamseeachanta/llm-wiki/issues/20) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | priority:low, cat:documentation, domain:knowledge-management |
| [#21 feat(llm-wiki): regenerate cross-links.md across 8 wikis after Tier C page additions](https://github.com/vamseeachanta/llm-wiki/issues/21) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | priority:low, cat:documentation, domain:knowledge-management |
| [#23 feat(knowledge): update wiki CLAUDE.md files to declare doc_key in L3 frontmatter required-set](https://github.com/vamseeachanta/llm-wiki/issues/23) | Planning Needed | cat:documentation | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:documentation |
| [#24 Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering wiki/standards/](https://github.com/vamseeachanta/llm-wiki/issues/24) | Planning Needed | cat:documentation | Codex | ace-linux-1 | enhancement, priority:medium, cat:documentation, agent:codex |
| [#27 docs(knowledge): add standard uplink/back-navigation block to wiki index pages](https://github.com/vamseeachanta/llm-wiki/issues/27) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:low, cat:documentation, domain:knowledge-management |
| [#28 feat(knowledge): chunk and paginate the canonical marine-engineering wiki index](https://github.com/vamseeachanta/llm-wiki/issues/28) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:high, cat:documentation, domain:knowledge-management |
| [#29 feat(knowledge): add canonical source-title aliasing for wiki source pages](https://github.com/vamseeachanta/llm-wiki/issues/29) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:high, cat:documentation, domain:knowledge-management |
| [#30 feat(knowledge): backfill promotion provenance on pre-existing wiki pages](https://github.com/vamseeachanta/llm-wiki/issues/30) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:documentation, domain:knowledge-management |
| [#31 feat(knowledge): promote design-code registry into standards overviews and repo-target backlinks](https://github.com/vamseeachanta/llm-wiki/issues/31) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:documentation, domain:knowledge-management |
| [#32 feat: career-learnings seed migration — pipeline integrity, OrcaFlex VIV, FEA, CFD, energy economics](https://github.com/vamseeachanta/llm-wiki/issues/32) | Planning Needed | domain:knowledge | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, domain:knowledge |
| [#33 WRK-1126: Add maritime law domain: skill, data, public cases, liabilities](https://github.com/vamseeachanta/llm-wiki/issues/33) | Planning Needed | domain:maritime-law | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, cat:knowledge-domain, domain:maritime-law |
| [#34 feat: engineering wiki — ingest remaining high-value sources (skills metadata, closed issues)](https://github.com/vamseeachanta/llm-wiki/issues/34) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, domain:knowledge-management |
| [#35 feat: engineering wiki cross-link discovery with domain wikis](https://github.com/vamseeachanta/llm-wiki/issues/35) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, domain:knowledge-management |
| [#36 feat: cross-wiki link discovery and infrastructure](https://github.com/vamseeachanta/llm-wiki/issues/36) | Planning Needed | domain:knowledge | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:medium, domain:knowledge |
| [#38 feat(knowledge): normalize WRK completions into structured seeds and wiki-candidate corpus](https://github.com/vamseeachanta/llm-wiki/issues/38) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, priority:high, cat:data-pipeline, cat:harness, domain:knowledge-management |
| [#39 feat: engineering wiki — ingest skill metadata as wiki pages](https://github.com/vamseeachanta/llm-wiki/issues/39) | Planning Needed | domain:knowledge-management | Claude planner; Gemini research support | ace-linux-1 | enhancement, cat:harness, domain:knowledge-management |
