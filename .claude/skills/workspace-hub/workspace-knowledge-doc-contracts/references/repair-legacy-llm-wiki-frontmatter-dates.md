# Archived Skill: `repair-legacy-llm-wiki-frontmatter-dates`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/repair-legacy-llm-wiki-frontmatter-dates`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/repair-legacy-llm-wiki-frontmatter-dates`
Consolidation date: 2026-04-29

---

---
name: repair-legacy-llm-wiki-frontmatter-dates
description: Diagnose and repair legacy llm-wiki source pages that have ingested timestamps but are missing required added/last_updated frontmatter dates.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-16
---

# Repair legacy llm-wiki frontmatter dates

Use when pyramid DT-1 fails because old `wiki/sources/*.md` pages have `ingested:` but lack required `added` and `last_updated`.

## Root cause
Older `scripts/knowledge/llm_wiki.py` batch-ingest builds created source pages with:
- `title`
- `slug`
- `domain`
- `ingested`
- `tags`

but omitted schema-required:
- `added`
- `last_updated`

Later schema/lint logic required those fields, so resumed batch-ingest runs kept skipping legacy pages via checkpoint and never repaired them.

## Fix pattern
1. Add a regression test first:
   - create a legacy source page with `ingested:` but no `added`/`last_updated`
   - create a matching checkpoint entry so batch-ingest would normally skip it
   - rerun `batch-ingest`
   - assert the page now contains `added` and `last_updated`
2. Implement an in-place repair helper that:
   - parses frontmatter
   - detects missing `added` / `last_updated`
   - derives the repair date from `ingested[:10]` when valid, otherwise uses current date
   - inserts missing keys before `ingested:` or `tags:`
   - preserves the rest of the page body unchanged
3. In `cmd_batch_ingest`, before skipping checkpointed slugs, call the repair helper on the existing page.
4. Track and report `Repaired:` in the batch summary.
5. After code fix, run a one-off repo repair over `knowledge/wikis/*/wiki/sources/*.md` using the same helper to burn down existing schema debt.

## Verification
- `uv run pytest scripts/knowledge/tests/test_llm_wiki.py scripts/knowledge/tests/test_phase4_tools.py -q`
- `uv run scripts/knowledge/pyramid-conformance-check.py --json`
- Expect DT-1 to move from large failure count to zero missing required frontmatter for repaired source pages.

## Commit strategy
When the repair touches thousands of wiki pages, keep history understandable:
1. commit code/test fixes separately
2. commit bulk wiki frontmatter repair separately

This makes review and rollback safer because the runtime/tooling fix is isolated from the mass content rewrite.

## Git staging caveat
Some wiki paths may be ignored by repo `.gitignore` rules. If the repaired pages are intentionally tracked, stage them explicitly with force, e.g.:
- `git add -f knowledge/wikis/<domain>/wiki/sources`

Verify the cached diff/stat before committing the bulk repair.

## Notes
- Prefer in-place frontmatter repair over full page regeneration so hand-edited bodies remain untouched.
- Use the original `ingested` date as the backfilled `added`/`last_updated` when possible to preserve provenance.
- After the one-off repair, rerun the conformance checker immediately to confirm the debt was actually burned down rather than just patched in code.
