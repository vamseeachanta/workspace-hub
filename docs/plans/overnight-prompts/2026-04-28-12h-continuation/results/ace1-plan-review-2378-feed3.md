# Lane feed3 Result — Issue #2378 Plan Review Hardener

**Classification:** `COMPLETED_WITH_RESULT`
**Machine:** ace-linux-1
**Lane:** feed3 (follow-up, 12h overnight continuation)
**Timestamp:** 2026-04-28T06:00:00Z

---

## Files written

| File | Action | Purpose |
|---|---|---|
| `scripts/review/results/2026-04-28-plan-2378-claude-feed3.md` | Created | Cold adversarial review artifact with MAJOR verdict, 2 MAJOR + 6 MINOR + 2 TRIVIAL findings |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-2378-feed3.md` | Created | This result summary |

## Verdict: MAJOR

The plan draft requires revision before it can advance to `status:plan-review`.

### MAJOR findings (2)

1. **Cron scope mismatch (MAJOR-1):** `wiki-ingest-cron.sh` is hardcoded to the `engineering` wiki (line 23: `WIKI_ROOT=...engineering`). The `wiki-ingest-nightly` scheduled task only invokes this script. There is **no existing nightly cron for marine-engineering**. The plan incorrectly claims the chunker "plugs in" to the existing cron and proposes modifying `wiki-ingest-cron.sh` to invoke the chunker — but this script never touches marine-engineering data. The plan must define a new trigger mechanism.

2. **`_check_index_consistency` over-scope (MAJOR-2):** The function (lines 839-861) is trivial — it only checks `index.md` exists and starts with `---`. It does NOT enumerate source pages, validate links, or detect orphans. The plan claims it "Must be updated to follow chunk pages" and proposes modifying it to "Recognise `_chunks/` pages; don't flag as orphan" — but the function never flags anything as orphan. This modification claim is based on a misreading of the code.

### MINOR findings (6)

| ID | Finding |
|---|---|
| MINOR-1 | `cmd_batch_ingest` line reference: plan says "line 1322" but function definition is at line 1248; line 1322 is the call site inside `_flush_batch` |
| MINOR-2 | Cross-link generator risk is moot: `wiki-cross-links.py` scans `CONTENT_SUBDIRS = (concepts, entities, standards, workflows)` — never touches `sources/` or `_chunks/` |
| MINOR-3 | Pseudocode emits `portal.md` link unconditionally, but `portal.md` does not exist (#2368 not landed); risk of dead link |
| MINOR-4 | No TDD test for conditional portal.md link behavior |
| MINOR-5 | Acceptance criterion "nightly cron invokes chunker" is untestable given MAJOR-1 |
| MINOR-6 | No guard test verifying `source_count` frontmatter excludes `_chunks/*.md` files (existing `glob("*.md")` is safe but undocumented) |

### Evidence verified (all 2026-04-28)

| Claim | Verified |
|---|---|
| `index.md` = 21,622 lines | YES (`wc -l`) |
| `sources/` = 19,166 files | YES (`ls \| wc -l`) |
| `_update_index_md` at line 1147 | YES (grep) |
| `_check_index_consistency` at line 839 | YES (grep + read: trivial 22-line function) |
| `cmd_batch_ingest` at line 1248 (not 1322) | YES (grep) |
| `wiki-ingest-cron.sh` hardcoded to engineering | YES (read line 23) |
| `schedule-tasks.yaml` has no marine-engineering task | YES (grep) |
| `portal.md` MISSING | YES (ls exits 2) |
| `_chunks/` directory MISSING | YES (ls exits 2) |
| `wiki-cross-links.py` CONTENT_SUBDIRS excludes `sources` | YES (read line 37) |
| #2378 OPEN, no status: labels | YES (gh issue view) |
| #2368 OPEN, status:plan-approved + status:working + agent:codex | YES (gh issue view --json) |
| #2372 OPEN | YES |
| #2366 OPEN | YES |
| #2205 CLOSED | YES |
| Concepts: 14, Entities: 15 | YES (ls \| wc -l) |

---

## Next human-safe actions

None of these have been executed by this lane.

### 1. Review the detailed review artifact
```bash
cat scripts/review/results/2026-04-28-plan-2378-claude-feed3.md
```

### 2. Apply proposed patches to the plan draft
The review artifact contains 4 specific patch directives that would resolve both MAJOR and key MINOR findings. To apply:
- Edit `docs/plans/2026-04-28-issue-2378-plan-draft.md` following the patch directives in the review artifact's "Proposed Patch Directives" section
- Re-run evidence verification on edited sections

### 3. Decide on cron strategy (required for MAJOR-1 resolution)
Choose one of:
- (a) Create a standalone `scripts/knowledge/wiki-chunk-cron.sh` for marine-engineering
- (b) Generalize `wiki-ingest-cron.sh` to accept `--wiki <domain>` parameter
- (c) Make the chunker self-triggered (e.g., post-ingest hook inside `_update_index_md`)

### 4. Decide on #2368 sequencing (recommended before approval)
Since #2368 is actively being implemented (`status:working`, `agent:codex`):
- If #2368 will land soon: wait, then revise #2378 plan with portal artifact detection
- If #2368 will take time: proceed but ensure the pseudocode includes a portal.md existence check

### 5. After plan revision, route to cross-review
```bash
# DO NOT run — human decision required:
# scripts/review/cross-review.sh docs/plans/2026-04-28-issue-2378-plan-draft.md 2378
```

### 6. After review passes, label for user approval
```bash
# DO NOT run — human-gated:
# gh issue edit 2378 --add-label status:plan-review
```

---

## Lane status

- **Started:** 2026-04-28T05:30:00Z
- **Completed:** 2026-04-28T06:00:00Z
- **Outcome:** Cold adversarial review completed with MAJOR verdict. Two MAJOR defects identified with specific patch directives. Plan requires revision before advancing to `status:plan-review`.
- **No GitHub mutations made.** No code implemented. No approval markers created. No issue comments posted.
