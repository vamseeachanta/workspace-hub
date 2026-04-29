# Plan Review: #2378 — Chunk and Paginate Marine-Engineering Wiki Index

**Reviewer:** Claude Opus 4.6 (cold adversarial, feed3 lane)
**Plan under review:** `docs/plans/2026-04-28-issue-2378-plan-draft.md`
**Date:** 2026-04-28
**Verdict:** MAJOR

---

## Summary

The plan is well-structured, follows the template contract, has comprehensive TDD test coverage, and demonstrates strong evidence discipline (10 sources, inline verification). However, it contains two MAJOR defects — one factual error about the nightly cron scope and one over-scoped modification claim about `_check_index_consistency` — plus several MINOR issues that should be corrected before approval.

---

## Findings

### MAJOR-1: `wiki-ingest-cron.sh` is engineering-only — plan claims it covers marine-engineering

**Location:** Plan lines 24, 231, 272; Resource Intel section lines 24-26

**Plan claims:**
- "Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly ingest already calls `llm_wiki.py lint`; chunked output must remain lint-clean." (line 24)
- Files to Change: "Modify `scripts/knowledge/wiki-ingest-cron.sh` — Invoke chunker after ingest, before lint" (line 231)
- Acceptance Criteria: "Nightly cron (`wiki-ingest-nightly`) invokes chunker without breaking existing ingest+lint+commit flow" (line 272)

**Actual state (verified 2026-04-28):**
- `wiki-ingest-cron.sh` line 23: `WIKI_ROOT="${REPO_ROOT}/knowledge/wikis/engineering"` — hardcoded to **engineering**, not marine-engineering.
- `schedule-tasks.yaml` line 587-602: The `wiki-ingest-nightly` task runs `wiki-ingest-cron.sh` with no domain parameter — it only ingests the engineering wiki.
- There is **no existing nightly cron for marine-engineering ingest**.

**Impact:** The plan's claim that "chunk regeneration plugs in here without a new cron" is false. Either:
(a) A new marine-engineering cron script must be created, or
(b) The existing cron must be generalized to accept a `--wiki` parameter, or
(c) The chunker is invoked via a separate mechanism entirely.

This changes the Files-to-Change table, the complexity estimate, and the acceptance criteria.

**Recommendation:** Revise the plan to acknowledge there is no marine-engineering nightly ingest cron. Define how the chunker will be triggered for marine-engineering. If a new cron entry is needed, add it to the artifact map, test list, and acceptance criteria.

---

### MAJOR-2: `_check_index_consistency` does not do orphan detection — plan over-scopes the modification

**Location:** Plan lines 21-22, 229

**Plan claims:**
- "Found: `scripts/knowledge/llm_wiki.py` line 839 `def _check_index_consistency(` — lint hook that checks `wiki/index.md` consistency. Must be updated to follow chunk pages, not just `index.md`." (line 21)
- Files to Change: "Modify `scripts/knowledge/llm_wiki.py` (`_check_index_consistency` line 839) — Recognise `_chunks/` pages; don't flag as orphan" (line 229)

**Actual state (verified 2026-04-28, lines 839-861):**
```python
def _check_index_consistency(wiki_root: Path, issues: list) -> int:
    """Check if index.md exists and has required structure."""
    index_path = wiki_root / "wiki" / "index.md"
    if not index_path.exists():
        issues.append({...})
        return 1
    content = index_path.read_text()
    issue_count = 0
    if not content.startswith("---"):
        issues.append({...})
        issue_count += 1
    return issue_count
```

The function is trivial: it checks (1) `index.md` exists and (2) starts with `---` (frontmatter). It does **not** enumerate source pages, validate links, detect orphans, or traverse any page tree. There is nothing to "follow chunk pages" or to "recognise `_chunks/` pages; don't flag as orphan" — because the function never flags anything as an orphan.

**Impact:** The plan promises a modification to this function that has no meaningful work to do. This is either:
(a) The wrong function — perhaps a different lint function elsewhere does orphan detection, or
(b) The plan is over-scoping: there is no orphan-detection code to update.

If (a), the plan needs to identify the correct function. If (b), this line should be removed from Files-to-Change and the test `test_lint_passes_post_chunk` should be clarified to test what lint actually checks (frontmatter validity post-rewrite, not orphan tolerance).

**Recommendation:** Remove or correct this modification claim. If future orphan detection is desirable, scope it as a separate enhancement, not as "must be updated."

---

### MINOR-1: `cmd_batch_ingest` line reference is stale

**Location:** Plan line 23

**Plan claims:** "Found: `scripts/knowledge/llm_wiki.py` line 1322 — `cmd_batch_ingest()` drives `_update_index_md()`"

**Actual state:** `cmd_batch_ingest` is at line **1248** (verified via grep). The call to `_update_index_md` is at line 1322 (`_flush_batch` → `_update_index_md`), so the claim is partially correct (the call site is at 1322) but the function definition is at 1248. The phrasing is ambiguous — it says "line 1322" as the location of `cmd_batch_ingest()` itself, which is wrong.

**Recommendation:** Clarify: "`cmd_batch_ingest()` defined at line 1248; it calls `_update_index_md()` via `_flush_batch()` at line 1322."

---

### MINOR-2: Cross-link generator risk is overstated / moot

**Location:** Plan line 302

**Plan claims:** "Risk: Wiki cross-link generator (`scripts/knowledge/wiki-cross-links.py`) may not understand chunk pages."

**Actual state (verified 2026-04-28):** `wiki-cross-links.py` line 37 defines: `CONTENT_SUBDIRS = ("concepts", "entities", "standards", "workflows")`. It does **not** scan `sources/` at all. Chunk pages live under `sources/_chunks/`. The cross-link generator will never encounter them.

**Impact:** This is a false risk. It should be demoted to a note or removed. Listing it as an unverified risk weakens reviewer confidence in other risk assessments.

**Recommendation:** Replace with: "Note: `wiki-cross-links.py` only scans `CONTENT_SUBDIRS = (concepts, entities, standards, workflows)` — it never touches `sources/`, so `_chunks/` is invisible to it. No modification needed."

---

### MINOR-3: `render_sources_summary` references `portal.md` unconditionally

**Location:** Plan pseudocode line 185

**Plan renders:** `**Curated facets:** see [portal.md](portal.md) (companion per #2368).`

**Issue:** `portal.md` does not exist yet (verified MISSING). If #2378 lands before #2368, the generated `index.md` will contain a dead link. The Risks section acknowledges this coordination issue (line 300-301) but the pseudocode does not implement the conditional check it describes.

**Recommendation:** Add a conditional in the pseudocode: only emit the portal.md link if the file exists, or emit it with a "coming soon" note. This should also have a test case (currently missing from TDD list).

---

### MINOR-4: Missing TDD test for `portal.md` conditional link

**Location:** TDD Test List (lines 239-254)

No test verifies the behavior when `portal.md` does/does not exist. Given the explicit coordination risk with #2368, this is an oversight.

**Recommendation:** Add: `test_portal_link_conditional` — verifies that the `index.md` summary includes the portal link only when `portal.md` exists, and omits/stubs it otherwise.

---

### MINOR-5: Nightly cron acceptance criterion is untestable as written

**Location:** Acceptance criteria line 272

**Plan states:** "Nightly cron (`wiki-ingest-nightly`) invokes chunker without breaking existing ingest+lint+commit flow"

Given MAJOR-1 (no marine-engineering cron exists), this acceptance criterion cannot be tested against the existing `wiki-ingest-nightly` task. If the plan creates a new cron entry for marine-engineering, the AC should reference the new task, not the existing engineering one.

---

### MINOR-6: `_update_index_md` modification strategy has a subtle counting bug risk

**Location:** Plan pseudocode lines 189-198, actual code lines 1158-1167

The existing `_update_index_md` function counts source pages via `sources_dir.glob("*.md")` (line 1159). After chunking, `sources/_chunks/` will contain `*.md` files. The `glob("*.md")` only matches files in the immediate directory (not subdirectories), so `_chunks/*.md` won't be counted — **this is correct behavior**. However, the plan does not explicitly call this out as a verified safe behavior. A future refactor to `rglob("*.md")` would silently inflate `source_count`.

**Recommendation:** Add a note in the plan documenting that `sources_dir.glob("*.md")` correctly excludes `_chunks/` subdirectory files, and add a guard test: `test_source_count_excludes_chunks` — verifies `source_count` frontmatter does not include chunk pages.

---

### TRIVIAL-1: Concept count 14 vs issue body count

The issue body mentions "small number of entity/concept pages relative to source pages." The plan correctly states 14 concepts and 15 entities (verified). No inconsistency, but worth noting these are live-verified.

---

### TRIVIAL-2: Changelog table lists frontmatter `page_count` 19,189 → 19,197 as "+8 pages" but source count went +4

The +8 is correct (page_count includes entities + concepts + sources + comparisons, and concepts went from 12 → 14 (+2), sources +4, plus potentially other subdirs). This is internally consistent but could confuse reviewers who expect page_count delta = source_count delta. A parenthetical note would help.

---

## Overlap / Coordination Risk Assessment

### #2368 (faceted portal pages) — HIGH
- **Status:** OPEN, `status:plan-approved`, `status:working`, `agent:codex` (verified 2026-04-28)
- **Conflict surface:** Both #2378 and #2368 modify `knowledge/wikis/marine-engineering/wiki/index.md`
- The plan correctly identifies this risk and proposes a "shared navigation anchor block" mitigation
- **Finding:** The pseudocode (lines 164-186) does NOT implement this mitigation — it does a raw `replace_block_between("## Sources", ...)` with no detection of portal artifacts
- **Recommendation:** The pseudocode should include a pre-check for portal artifacts before rewriting

### #2372 (source-title aliasing) — LOW
- **Status:** OPEN (verified)
- No conflict — aliasing changes content, not structure
- Plan correctly assesses this as expected-noisy-diff risk

### #2366 (strengthening scorecard) — LOW
- **Status:** OPEN (verified)
- Downstream consumer only — no conflict

### #2205 (operating model) — NONE
- **Status:** CLOSED (verified)
- Parent issue, no active code conflict

### `index.md` / `portal.md` surfaces
- `portal.md`: MISSING (verified) — #2368 in flight but not landed
- `index.md`: 21,622 lines (verified) — both #2378 and #2368 touch this file
- Risk is well-identified but mitigation is not implemented in pseudocode

---

## Template Compliance

| Template requirement | Status |
|---|---|
| ≥3 distinct sources | PASS — 10 sources cited |
| Evidence section with tool output | PASS — inline verification present |
| Gaps identified | PASS — 7 gaps listed with proofs |
| Artifact map | PASS |
| TDD test list | PASS (14 tests) with MINOR-4 gap |
| Acceptance criteria | PASS with MINOR-5 untestable criterion |
| Adversarial review summary | PENDING (expected — this review populates it) |
| Risks section | PASS with MINOR-2 false risk |

---

## Verdict: MAJOR

Two MAJOR findings require plan revision before approval:

1. **MAJOR-1:** The cron integration strategy is based on a false premise (existing cron covers marine-engineering). The plan must define how chunking is triggered for marine-engineering.
2. **MAJOR-2:** The `_check_index_consistency` modification is based on a misunderstanding of what the function does. Remove or correct.

Six MINOR findings should be addressed:
- MINOR-1: Stale `cmd_batch_ingest` line reference
- MINOR-2: False cross-link generator risk
- MINOR-3: Unconditional `portal.md` link in pseudocode
- MINOR-4: Missing TDD test for portal.md conditional
- MINOR-5: Untestable nightly cron AC
- MINOR-6: Missing guard test for source count excluding chunks

---

## Proposed Patch Directives

If the verdict were to be resolved to MINOR, the following edits would be needed in the plan draft:

### Patch 1 (MAJOR-1): Cron scope correction
**Section:** Resource Intel → Existing repo code, line ~24
**Current:** "Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly ingest already calls `llm_wiki.py lint`; chunked output must remain lint-clean."
**Replace with:** "Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly ingest for **engineering** wiki only (hardcoded `WIKI_ROOT=...engineering`). No existing nightly cron for marine-engineering. Chunker invocation for marine-engineering must be defined as a new cron entry or as a manual/scripted step."

**Section:** Files to Change, line ~231
**Current:** "Modify `scripts/knowledge/wiki-ingest-cron.sh` — Invoke chunker after ingest, before lint"
**Replace with:** "Create `scripts/knowledge/wiki-chunk-cron.sh` — Standalone cron script that invokes `chunk_wiki_index.py` for domains exceeding threshold; or extend `wiki-ingest-cron.sh` to accept `--wiki` parameter (scope decision for user)"

**Section:** Acceptance Criteria, line ~272
**Current:** "Nightly cron (`wiki-ingest-nightly`) invokes chunker without breaking existing ingest+lint+commit flow"
**Replace with:** "A cron entry or scripted mechanism exists that invokes the chunker for marine-engineering post-ingest; it does not break the existing engineering ingest+lint+commit flow"

### Patch 2 (MAJOR-2): `_check_index_consistency` scope correction
**Section:** Resource Intel → Existing repo code, line ~21-22
**Current:** "Found: `scripts/knowledge/llm_wiki.py` line 839 `def _check_index_consistency(` — lint hook that checks `wiki/index.md` consistency. Must be updated to follow chunk pages, not just `index.md`."
**Replace with:** "Found: `scripts/knowledge/llm_wiki.py` line 839 `def _check_index_consistency(` — lint hook that checks `index.md` existence and frontmatter validity only. Does NOT do orphan detection or source enumeration. No modification needed for chunking."

**Section:** Files to Change, line ~229
**Remove:** "Modify `scripts/knowledge/llm_wiki.py` (`_check_index_consistency` line 839) — Recognise `_chunks/` pages; don't flag as orphan"

### Patch 3 (MINOR-3/4): Portal.md conditional
**Section:** Pseudocode `render_sources_summary`, line ~185
**Add conditional:** `if portal_path.exists(): emit portal link, else: omit or emit "portal pending (#2368)"`
**Section:** TDD Test List
**Add:** `test_portal_link_conditional | Verifies portal link included only when portal.md exists | run with/without portal.md | link present/absent accordingly`

### Patch 4 (MINOR-6): Source count guard test
**Section:** TDD Test List
**Add:** `test_source_count_excludes_chunks | Verifies source_count frontmatter does not count _chunks/*.md files | run chunker, read frontmatter | source_count == actual sources/*.md count (excludes _chunks/)`

---

## Reviewer attestation

- All MAJOR/MINOR findings are backed by verified file reads or tool output from 2026-04-28
- No GitHub mutations made
- No code implemented
- No approval markers created
