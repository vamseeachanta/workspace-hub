# Interrupted engineering-report closeout checkpoint

Use this reference when an approved issue execution is interrupted before generated engineering/report artifacts are committed and closed.

## Durable lesson

A focused green test run is not enough to close an engineering report issue when the deliverables include regenerated Markdown/HTML/DOCX/PDF/CSV/JSON/provenance/manifest artifacts. If the session is interrupted by context compaction or tool-budget exhaustion, turn the final response into a restart checkpoint and explicitly keep the issue open.

## Restart checkpoint shape

Include only observed evidence:

- worktree path and branch state
- issue state/label gate if already observed
- dirty and untracked files already observed
- targeted tests already run and exact pass/fail summary
- generated artifacts that were actually verified vs artifacts still pending
- suspected blockers discovered from source/artifact inspection
- exact next checkpoint sequence for the next session

Do not claim any of the following unless verified in the current or preserved tool evidence:

- artifacts regenerated into final repo boundaries
- DOCX/PDF open and contain expected text
- HTML controls/charts/schematics match the current approved default values
- implementation uses the approved source route rather than a simplified fallback
- adversarial review passed
- commit/push/issue comments/closeout happened

## Engineering-report-specific resume sequence

1. Re-run `git status --short --branch` in the implementation repo and classify unrelated dirt before staging.
2. Inspect the changed calculation/report source for source-route truthfulness: tests must fail if the approved workbook/source adapter is unavailable or replaced by a hardcoded simplified formula.
3. Clean stale generated-artifact language before publishing, especially superseded defaults, removed chart concepts, resultants/heatmaps, or phrases that contradict the approved plan.
4. Regenerate every required artifact surface into the correct Git boundary: implementation repo outputs vs project/client repo deliverables.
5. Verify cross-surface content, not just file existence: Markdown text, HTML IDs/controls/defaults, DOCX extracted text, PDF extracted text, CSV row counts, JSON/provenance/manifest links.
6. Run targeted tests plus artifact validators.
7. Run adversarial review focused on numerical/source correctness and artifact drift.
8. Commit only intended files, push, post final issue/parent issue comments, then close only if acceptance criteria map to proof.

## Common pitfall

Do not let report strings say “approved workbook route” while the actual model still uses inline placeholder/reference coefficient functions. Either connect the calculation to the approved source adapter with fail-closed tests, or truthfully narrow the report/issue contract before closeout.
