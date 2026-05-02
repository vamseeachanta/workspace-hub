# Lane feed4 Result — Issue #2378 Plan Draft Patch Hardener

**Classification:** `COMPLETED_WITH_RESULT`
**Machine:** ace-linux-1
**Lane:** feed4 (follow-up, 12h overnight continuation)
**Timestamp:** 2026-04-28T07:15:00Z

---

## Files changed

| File | Action | Purpose |
|---|---|---|
| `docs/plans/2026-04-28-issue-2378-plan-draft.md` | Modified | Patched plan draft to resolve feed3 MAJOR and MINOR findings |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2378-feed4.md` | Created | This result summary |

---

## Findings resolved

### MAJOR findings resolved (2/2)

1. **MAJOR-1 — Cron scope correction:** Replaced false claim that `wiki-ingest-cron.sh` / `wiki-ingest-nightly` covers marine-engineering. Plan now states verified fact: `wiki-ingest-cron.sh` is hardcoded to `knowledge/wikis/engineering`; no existing marine-engineering nightly cron exists. Plan proposes creating `scripts/knowledge/wiki-chunk-cron.sh` as a standalone marine-engineering chunking trigger with a new `wiki-chunk-nightly` scheduled-task entry. Alternative (generalizing `wiki-ingest-cron.sh` to accept `--wiki`) is flagged as an explicit user decision, not assumed. Artifact map, Files-to-Change table, acceptance criteria, and complexity wording all updated.

2. **MAJOR-2 — `_check_index_consistency` scope correction:** Replaced false orphan-detection claim with verified fact that `_check_index_consistency` only checks `index.md` existence and frontmatter prefix (22-line function). Removed the Files-to-Change row that claimed the function must recognize `_chunks/` pages. Updated link-preservation contract and complexity wording to no longer depend on nonexistent orphan detection.

### MINOR findings resolved (6/6)

| ID | Resolution |
|---|---|
| MINOR-1 | Corrected `cmd_batch_ingest` reference: "defined at line 1248; calls `_update_index_md()` via `_flush_batch()` at line 1322" |
| MINOR-2 | Replaced false `wiki-cross-links.py` risk with verified note: cross-link generator scans `CONTENT_SUBDIRS = (concepts, entities, standards, workflows)` only; never touches `sources/` or `_chunks/` |
| MINOR-3 | Updated `render_sources_summary` pseudocode with conditional: emits portal link only if `portal.md` exists; otherwise emits "portal page pending (#2368)" |
| MINOR-4 | Added TDD row: `test_portal_link_conditional` — verifies portal link included only when `portal.md` exists |
| MINOR-5 | Acceptance criterion updated from "nightly cron (wiki-ingest-nightly) invokes chunker" to "A cron entry or scripted mechanism (wiki-chunk-cron.sh + wiki-chunk-nightly) exists for marine-engineering; does not break existing engineering flow" |
| MINOR-6 | Added TDD row: `test_source_count_excludes_chunks` — verifies `source_count` frontmatter excludes `_chunks/*.md`. Added inline pseudocode comment that `glob("*.md")` excludes `_chunks/` by construction. |

### Additional edits

- Updated review artifacts header line to reference `scripts/review/results/2026-04-28-plan-2378-claude-feed3.md`
- Updated Adversarial Review Summary table: Claude row now shows "MAJOR → addressed by plan patch (feed4)" with review path
- Updated overall result: "MAJOR findings addressed by feed4 plan patch. Awaiting fresh cross-review to confirm resolution. Plan is NOT approved."
- Added `wiki-chunk-cron.sh` and `wiki-chunk-nightly` entries to artifact map
- Test count updated from 14 to 16 in complexity section

---

## Verification performed

### Old false claims — confirmed REMOVED (5 grep checks, all zero matches)

| Pattern searched | Result |
|---|---|
| `plugs in here without a new cron` | ✅ Not found |
| `Must be updated to follow chunk pages` | ✅ Not found |
| `don't flag as orphan` | ✅ Not found |
| `may not understand chunk pages` | ✅ Not found |
| `nightly ingest already calls` | ✅ Not found |

### New correct claims — confirmed PRESENT (8 grep checks, all matched)

| Pattern searched | Matches |
|---|---|
| `hardcoded.*engineering.*No existing nightly cron` | 1 match (line 23) |
| `existence and frontmatter validity only` | 1 match (line 21) |
| `portal page pending` | 1 match (line 189) |
| `test_portal_link_conditional` | 1 match (line 256) |
| `test_source_count_excludes_chunks` | 2 matches (lines 138, 257) |
| `wiki-chunk-cron.sh` | 4 matches (lines 108, 233, 234, 277) |
| `CONTENT_SUBDIRS.*concepts.*entities.*standards.*workflows` | 1 match (line 307) |
| `MAJOR.*addressed by.*feed4` | 2 matches (lines 286, 290) |

---

## Remaining next step

**Fresh cross-review after plan patch.** The plan draft now addresses all feed3 findings but has not been re-reviewed. The recommended human-safe next action is:

1. Read the patched plan: `docs/plans/2026-04-28-issue-2378-plan-draft.md`
2. Decide on the cron strategy user choice (standalone `wiki-chunk-cron.sh` vs. generalizing `wiki-ingest-cron.sh`)
3. Route to fresh cross-review (Claude + Codex + Gemini) against the patched draft
4. After review passes, label `#2378` with `status:plan-review` for user approval

---

## Confirmation

- ✅ No GitHub mutations made (no issue comments, no label changes, no pushes)
- ✅ No code implementation performed
- ✅ No approval markers created
- ✅ Plan status remains "PLAN DRAFT — NOT APPROVED"
- ✅ Only allowed files written: plan draft (modified) + this result summary (created)
