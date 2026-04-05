# Overnight 3-Terminal Execution Plan — 2026-04-04

## Issue-to-Terminal Mapping

| Issue | Title                                          | Terminal | Agent  | Branch     |
|------:|-----------------------------------------------|----------|--------|------------|
| #1814 | API RP 2GEO alpha method -> geotechnical      | T1       | Claude | main       |
| #1824 | Test coverage uplift 2.95% -> 20%             | T2       | Codex  | feat/1824  |
| #1862 | Index 38,526 conference papers                | T3       | Gemini | main       |
| #1863 | Migrate DDE remote literature (14.6 GB)       | T3       | Gemini | main       |

Note: #1821 is CLOSED (already completed). Dropped from this batch.

## Git Contention Map

```
Terminal 1 writes: digitalmodel/src/digitalmodel/geotechnical/
                   digitalmodel/tests/geotechnical/
                   workspace-hub data/document-index/standards-transfer-ledger.yaml (single edit)

Terminal 2 writes: digitalmodel/tests/structural/
                   digitalmodel/tests/hydrodynamics/
                   digitalmodel/tests/pipeline/
                   digitalmodel/tests/naval_architecture/
                   digitalmodel/tests/cathodic_protection/
                   (ON BRANCH feat/1824-test-uplift — no main contention)

Terminal 3 writes: workspace-hub data/document-index/conference-*
                   workspace-hub data/document-index/dde-*
                   workspace-hub data/document-index/mounted-source-registry.yaml
                   workspace-hub scripts/data/document-index/
                   /mnt/ace/docs/literature/dde/ (external mount)

Zero overlap. T1 and T2 both touch digitalmodel but on different branches.
T3 only touches workspace-hub data/ paths not used by T1.
```

## Execution Order

All 3 terminals can start simultaneously.

- T1 (Claude): ~2-3 hours. 5 tasks: test assertions, validation, composite API, ledger update, GH comment.
- T2 (Codex): ~4-6 hours. 7 tasks across 5 domains. Runs on branch to avoid T1 contention.
- T3 (Gemini): ~6-8 hours. Part A conference indexing (~3h), Part B DDE migration (~4h network I/O).

## What You'll Have by Morning

From Terminal 1 (#1814):
  * Dark-intel worked examples wired as test assertions for API RP 2GEO
  * Input range validation on geotechnical pile functions
  * Composite pile_capacity.py with multi-layer clay support
  * Standards-transfer-ledger updated (API-RP-2GEO -> implemented)

From Terminal 2 (#1824):
  * Branch feat/1824-test-uplift with skeleton tests for 5+ domains
  * Structural, hydrodynamics, pipeline, naval arch, CP test suites
  * Estimated 200-500 new tests across skeleton packages
  * Ready for review and merge to main

From Terminal 3 (#1862 + #1863):
  * Complete conference-index-batch.jsonl (38,526 files cataloged)
  * Phase A metadata extraction for OTC, OMAE, DOT PDFs
  * 14.6 GB DDE literature migrated to /mnt/ace/docs/literature/dde/
  * Migration report and source registry updated

Issues addressed: #1814, #1824, #1862, #1863
Morning merge: git merge feat/1824-test-uplift into digitalmodel main

## Prompt Files

- Terminal 1: docs/plans/overnight-prompts/2026-04-04/terminal-1-geotechnical-promotion.md
- Terminal 2: docs/plans/overnight-prompts/2026-04-04/terminal-2-test-coverage-uplift.md
- Terminal 3: docs/plans/overnight-prompts/2026-04-04/terminal-3-conference-index-dde-migrate.md
