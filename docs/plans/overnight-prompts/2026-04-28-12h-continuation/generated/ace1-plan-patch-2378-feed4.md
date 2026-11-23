# Follow-up lane feed4 — Issue #2378 plan draft patch hardener

You are running unattended on `ace-linux-1` from `/mnt/local-analysis/workspace-hub` before the 2026-04-29 09:45 CDT stop target.

## Mission
Patch the existing #2378 plan draft to address the completed feed3 adversarial review findings. This is **planning-only** work: do not implement code, do not run or launch implementation lanes, do not mutate GitHub, do not create approval markers, do not label issues, do not merge/close/push/force-push/hard reset.

## Inputs to read first
- Plan draft: `docs/plans/2026-04-28-issue-2378-plan-draft.md`
- Feed3 review artifact: `scripts/review/results/2026-04-28-plan-2378-claude-feed3.md`
- Feed3 result summary: `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-2378-feed3.md`

## Allowed writes
- `docs/plans/2026-04-28-issue-2378-plan-draft.md`
- `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2378-feed4.md`

## Required plan edits
Apply the feed3 proposed patch directives exactly enough to resolve both MAJOR findings and the easy MINOR findings:

1. Cron scope correction
   - Replace claims that existing `wiki-ingest-nightly` / `wiki-ingest-cron.sh` already covers marine-engineering.
   - State the verified fact: `wiki-ingest-cron.sh` is hardcoded to `knowledge/wikis/engineering`; no existing marine-engineering nightly cron exists.
   - Choose a bounded plan strategy: prefer creating `scripts/knowledge/wiki-chunk-cron.sh` as a standalone marine-engineering chunking trigger, and update artifact map/files/AC/complexity accordingly. If you think generalizing `wiki-ingest-cron.sh` is safer, record it as an explicit user decision, not an implementation assumption.

2. `_check_index_consistency` scope correction
   - Replace the false orphan-detection claim with the verified fact that `_check_index_consistency` only checks `index.md` existence and frontmatter prefix.
   - Remove the file-change row that says `_check_index_consistency` must recognize `_chunks/` pages.
   - Update link-preservation/complexity wording so it no longer depends on nonexistent orphan detection.

3. Portal conditional
   - Update `render_sources_summary` pseudocode so it emits the `portal.md` link only if the file exists, or emits a clearly non-linking pending note.
   - Add a TDD row for `test_portal_link_conditional`.

4. Source-count guard
   - Add a TDD row for `test_source_count_excludes_chunks`.
   - Add a short note that `sources_dir.glob("*.md")` excludes `_chunks/*.md` by construction and the guard test prevents accidental future `rglob` regressions.

5. Cross-link risk correction
   - Replace the false `wiki-cross-links.py` risk with a note that the cross-link generator only scans concepts/entities/standards/workflows and does not touch `sources/` or `_chunks/`.

6. Review summary update
   - Update the Adversarial Review Summary row for Claude to reference `scripts/review/results/2026-04-28-plan-2378-claude-feed3.md`, verdict MAJOR resolved-by-plan-patch (or MAJOR addressed, awaiting fresh cross-review). Do not mark the overall plan approved.

## Verification before stopping
- Re-read the patched sections and ensure the old false claims are gone.
- Run only safe text checks (e.g. grep) if useful. Do not run implementation tests.
- Write `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2378-feed4.md` with:
  - Classification: `COMPLETED_WITH_RESULT` or `BLOCKED`
  - Files changed
  - Bullet list of findings resolved
  - Remaining human-safe next step (likely fresh cross-review after plan patch)
  - Confirmation: no GitHub mutations, no code implementation, no approval marker.
