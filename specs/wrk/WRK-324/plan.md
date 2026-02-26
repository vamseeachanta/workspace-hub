# WRK-324 Plan: Representative OrcaFlex Run Scripts

> Route C spec for `.claude/work-queue/pending/WRK-324.md`

## Problem
Representative OrcaFlex examples lacked executable run scripts, reducing reproducibility and preventing automated QA/reporting workflows.

## Implementation Plan
1. Select six representative models across riser, vessel, FOWT, lay-table, and sweep workflows.
2. Create `run_orcaflex.py` in each target folder.
3. Standardize OrcFxAPI bootstrap with `ORCAFLEX_API_PATH` support.
4. Implement static/dynamic execution and `.sim` persistence with output summaries.
5. Include workflow-specific notes for lay-table batching and multi-statics sweep loops.

## Deliverables
- Six `run_orcaflex.py` scripts under the targeted modular example folders.

## Validation
- Verify scripts load `master.yml`, emit expected output artifacts, and print key result summaries.

## Cross-Review Log
| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| P1 | 2026-02-24 | Claude | MINOR | Required portable API-path handling called out for all scripts. | yes |
| P2 | 2026-02-26 | Codex | APPROVE | Scripts committed in six representative locations and aligned to goals. | n/a |
| P3 | 2026-02-26 | Gemini | MINOR | Independent CLI review deferred (local CLI timeout); artifact set is internally consistent. | deferred |
