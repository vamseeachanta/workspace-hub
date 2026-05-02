# Plan Review: #2378 — Chunk and Paginate Marine-Engineering Wiki Index

**Reviewer:** Claude Opus 4.6 (cold adversarial, feed5 lane — post-patch re-review)
**Plan under review:** `docs/plans/2026-04-28-issue-2378-plan-draft.md` (after feed4 patch)
**Prior review:** `scripts/review/results/2026-04-28-plan-2378-claude-feed3.md` (MAJOR verdict, 2 MAJOR + 6 MINOR)
**Patch applied by:** feed4 lane (`docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2378-feed4.md`)
**Date:** 2026-04-29
**Verdict:** MINOR

---

## Scope of This Review

This is a fresh adversarial re-review after feed4 applied patches to resolve the two feed3 MAJOR findings. The review:

1. Verifies whether feed4 actually resolved MAJOR-1 (cron scope mismatch) and MAJOR-2 (`_check_index_consistency` over-scope)
2. Re-checks the patched plan for newly introduced factual or scope errors
3. Produces a fresh verdict

---

## Feed3 MAJOR Resolution Verification

### MAJOR-1 (cron scope mismatch): ✅ RESOLVED

**Feed3 finding:** Plan falsely claimed `wiki-ingest-cron.sh` / `wiki-ingest-nightly` covered marine-engineering. The script is hardcoded to `knowledge/wikis/engineering` (line 23).

**Verification (2026-04-29):**
- `wiki-ingest-cron.sh` line 23: `WIKI_ROOT="${REPO_ROOT}/knowledge/wikis/engineering"` — confirmed still engineering-only
- `schedule-tasks.yaml` lines 587-603: `wiki-ingest-nightly` runs `wiki-ingest-cron.sh` with no domain parameter — confirmed engineering-only
- No `wiki-chunk` entry exists in `schedule-tasks.yaml` — confirmed (`grep wiki-chunk` returns empty)
- `scripts/knowledge/wiki-chunk-cron.sh` does NOT exist — confirmed (expected: plan says "Create")

**Patched plan now states (line 23):**
> "Found: `scripts/knowledge/wiki-ingest-cron.sh` — nightly ingest for the **engineering** wiki only (hardcoded `WIKI_ROOT=...engineering` at line 23). No existing nightly cron for marine-engineering. Chunker invocation for marine-engineering must be defined as a new cron entry or standalone script."

**Assessment:** Correct. The false claim is removed. The plan now proposes creating `wiki-chunk-cron.sh` as a standalone script (line 233) with a user-decision flag for the alternative approach. The artifact map (line 108-109), Files-to-Change (lines 233-234), and acceptance criteria (line 277) are all consistent with this corrected scope. MAJOR-1 is genuinely resolved.

---

### MAJOR-2 (`_check_index_consistency` over-scope): ✅ RESOLVED

**Feed3 finding:** Plan falsely claimed `_check_index_consistency` does orphan detection and "Must be updated to follow chunk pages." The function is a trivial 22-line existence + frontmatter check.

**Verification (2026-04-29):**
- `llm_wiki.py` lines 839-861: function checks (1) `index.md` exists, (2) starts with `---`. No source enumeration, no orphan detection, no link validation. Confirmed unchanged from feed3 evidence.

**Patched plan now states (line 21):**
> "Found: `scripts/knowledge/llm_wiki.py` line 839 `def _check_index_consistency(` — lint hook that checks `index.md` existence and frontmatter validity only (22-line function: verifies file exists and starts with `---`). Does NOT do orphan detection or source enumeration. No modification needed for chunking."

**Assessment:** Correct. The false orphan-detection claim is removed. The Files-to-Change table no longer includes a modification to `_check_index_consistency`. The link-preservation contract (line 218) and complexity section (line 319) both correctly state "No `_check_index_consistency` modification needed." MAJOR-2 is genuinely resolved.

---

## Feed3 MINOR Resolution Verification

| ID | Status | Verification |
|---|---|---|
| MINOR-1 (stale `cmd_batch_ingest` line ref) | ✅ Resolved | Plan line 22 now reads: "`cmd_batch_ingest()` defined at line 1248; it calls `_update_index_md()` via `_flush_batch()` at line 1322." Verified: `cmd_batch_ingest` IS at line 1248, `_flush_batch` calls `_update_index_md` at line 1322. Correct. |
| MINOR-2 (false cross-link risk) | ✅ Resolved | Plan line 307 now reads as a Note (not Risk): `wiki-cross-links.py` scans `CONTENT_SUBDIRS = (concepts, entities, standards, workflows)` only. Verified: line 37 of `wiki-cross-links.py` confirms this tuple. `sources/` is excluded. Correct. |
| MINOR-3 (unconditional portal link) | ✅ Resolved | Plan pseudocode line 189 now has conditional: `if portal_path.exists()` → portal link; else → "portal page pending (#2368)". Verified: `portal.md` does NOT exist (ls exits 2). Conditional is appropriate. |
| MINOR-4 (missing portal test) | ✅ Resolved | Plan TDD line 256: `test_portal_link_conditional` added. Test spec covers both presence and absence of `portal.md`. |
| MINOR-5 (untestable cron AC) | ✅ Resolved | Plan AC line 277 now reads: "A cron entry or scripted mechanism (`wiki-chunk-cron.sh` + `wiki-chunk-nightly` scheduled task) exists..." — no longer references the engineering-only `wiki-ingest-nightly`. |
| MINOR-6 (missing source-count guard) | ✅ Resolved | Plan TDD line 257: `test_source_count_excludes_chunks` added. Plan pseudocode line 137-138 adds inline comment documenting `glob("*.md")` excludes `_chunks/`. |

---

## New Findings (Post-Patch)

### MINOR-N1: `wiki-chunk-cron.sh` trigger timing is under-specified

**Location:** Plan lines 233-234, 277, artifact map line 108-109

**Plan proposes:** Create `wiki-chunk-cron.sh` + `wiki-chunk-nightly` scheduled-task entry. The cron script invokes `chunk_wiki_index.py` for domains exceeding threshold.

**Issue:** The plan does not specify **when** `wiki-chunk-nightly` should run relative to `wiki-ingest-nightly` (02:15 UTC). If marine-engineering gets its own ingest cron in the future, the chunk cron must run **after** ingest completes. If it runs concurrently or before, the chunks will be stale. The plan's AC says "post-ingest" (line 277) but the scheduled-task definition doesn't enforce this ordering.

**Current state:** There is no marine-engineering ingest cron at all, so the timing question is about the chunker running standalone. But the plan's pseudocode step 4 (`_update_index_md_chunked_aware`, lines 193-202) implies live ingest appends to chunks — so the nightly chunk cron is a **full-rebuild** mechanism, not an incremental one. This distinction is not clearly documented.

**Impact:** Low. The scheduled-task entry is a new file entry that can be defined at implementation time. But the plan should clarify whether `wiki-chunk-nightly` is:
(a) A full-rebuild cron (re-chunks all sources from scratch), or
(b) A no-op when the live-ingest hook has already maintained chunks incrementally

**Recommendation:** Add a one-line note to the `wiki-chunk-nightly` file-change row clarifying its role: "Full rebuild for schema migrations or recovery; live ingest keeps chunks current incrementally." This also affects `test_lint_passes_post_chunk` — it should test both the full-rebuild path and the incremental path.

---

### MINOR-N2: `page_count` computation inconsistency between Python and potential Bash cron

**Location:** Plan line 108 (`wiki-chunk-cron.sh` creation), cross-reference with `wiki-ingest-cron.sh` lines 162-171

**Context:** The existing `wiki-ingest-cron.sh` has a `_count_wiki_pages` function (lines 162-171) that uses `find "$dir" -name '*.md' -type f` which is **recursive** — it descends into subdirectories. If `wiki-chunk-cron.sh` copies this pattern for marine-engineering, the page count would **include** `_chunks/*.md` files, inflating the count.

Meanwhile, the Python `_update_index_md` (line 1159) uses `sources_dir.glob("*.md")` which is **non-recursive** — correctly excluding `_chunks/`.

**Impact:** This only matters if `wiki-chunk-cron.sh` includes a page-count-drop alert (like the existing engineering cron). The frontmatter `page_count` written by Python would disagree with the bash page count. Not a bug in the plan per se, but a trap for the implementer.

**Recommendation:** Add a note in the Risks section: "If `wiki-chunk-cron.sh` includes page-count alerting (modeled after `wiki-ingest-cron.sh`), the `find`-based count must exclude `_chunks/` to match the Python `glob("*.md")` behavior. Use `find "$dir" -name '*.md' -not -path '*/_chunks/*' -type f` or similar."

---

### MINOR-N3: `force` parameter referenced but not declared in pseudocode

**Location:** Plan pseudocode line 140

**Pseudocode reads:**
```
if len(sources) < threshold and not force:
```

The function signature at line 131 declares `chunk_wiki_index(domain, chunk_size=..., threshold=..., dry_run=False)` — no `force` parameter. The `force` variable is used but never defined. This is a pseudocode error that will confuse an implementer.

**Impact:** Trivial — pseudocode is illustrative. But since the plan is the implementation contract, this inconsistency weakens clarity.

**Recommendation:** Either add `force=False` to the function signature at line 131, or replace `and not force` with `and not dry_run` (if dry_run should bypass threshold), or document what `force` means.

---

### MINOR-N4: Review artifact paths in plan header are stale

**Location:** Plan line 7

**Plan states:**
> `Review artifacts: scripts/review/results/2026-04-28-plan-2378-claude-feed3.md | ...-codex.md | ...-gemini.md (pending)`

**Issue:** The Claude review artifact reference is to `feed3` but the plan has been patched by feed4 and now re-reviewed by feed5. The plan should reference the most recent review artifact. Codex and Gemini remain pending.

**Impact:** Cosmetic — but a reviewer checking the header for the latest review state will find a stale reference.

**Recommendation:** Update to reference `2026-04-29-plan-2378-claude-feed5.md` as the latest Claude review. This is a housekeeping item for whoever next edits the plan.

---

## Evidence Verified (2026-04-29)

| Claim in patched plan | Live state | Match |
|---|---|---|
| `index.md` = 21,622 lines | `wc -l` = 21,622 | ✅ |
| `sources/` = 19,166 files | `ls \| wc -l` = 19,166 | ✅ |
| `_update_index_md` at line 1147 | grep confirmed | ✅ |
| `_check_index_consistency` at line 839, trivial 22-line function | read confirmed (lines 839-861) | ✅ |
| `cmd_batch_ingest` at line 1248, `_flush_batch` → `_update_index_md` at 1322 | read confirmed | ✅ |
| `wiki-ingest-cron.sh` hardcoded to engineering (line 23) | read confirmed | ✅ |
| `schedule-tasks.yaml` has no marine-engineering or wiki-chunk task | grep returns empty | ✅ |
| `portal.md` MISSING | ls exits 2 | ✅ |
| `_chunks/` directory MISSING in all wikis | grep `_chunks` under `knowledge/wikis` returns empty | ✅ |
| `wiki-chunk-cron.sh` does NOT exist | ls exits 2 | ✅ |
| `wiki-cross-links.py` CONTENT_SUBDIRS excludes `sources` | line 37 confirmed: `("concepts", "entities", "standards", "workflows")` | ✅ |
| `sources_dir.glob("*.md")` is non-recursive | Python Path.glob docs + code at line 1159 confirmed | ✅ |
| `_update_index_md` page_count uses `subdir.glob("*.md")` per subdir | lines 1164-1167 confirmed non-recursive | ✅ |

---

## Overlap / Coordination Assessment (unchanged from feed3 but re-verified)

| Sibling | Risk | Status |
|---|---|---|
| #2368 (faceted portal) | HIGH — both touch `index.md` | OPEN, `status:working`, `agent:codex`. `portal.md` still MISSING. Plan correctly handles via conditional. |
| #2372 (source-title aliasing) | LOW — content-only | OPEN |
| #2366 (strengthening scorecard) | LOW — downstream consumer | OPEN |

---

## Template Compliance

| Requirement | Status |
|---|---|
| ≥3 distinct sources | PASS — 10 sources |
| Evidence with tool output | PASS |
| Gaps identified | PASS — 7 gaps with proofs |
| Artifact map | PASS — includes new cron artifacts |
| TDD test list | PASS — 16 tests |
| Acceptance criteria | PASS — corrected for new cron scope |
| Adversarial review summary | PASS — references feed3 + feed4 |
| Risks section | PASS — cross-link risk demoted to Note |
| Pre-empted critiques | PASS — 6 items |

---

## Verdict: MINOR

Both feed3 MAJOR findings are genuinely resolved. All 6 feed3 MINOR findings are resolved. The patched plan is factually accurate against the live codebase as of 2026-04-29.

Four new MINOR findings identified:
- **MINOR-N1:** `wiki-chunk-nightly` trigger timing and full-rebuild vs incremental role unclear
- **MINOR-N2:** `page_count` computation inconsistency trap between Python `glob` and potential Bash `find`
- **MINOR-N3:** `force` parameter referenced but undeclared in pseudocode
- **MINOR-N4:** Review artifact paths in plan header are stale (feed3, not feed5)

None of these are blocking. All can be resolved during implementation or as a pre-implementation plan polish.

**This review is evidence only.** The plan remains **NOT APPROVED** until the user grants explicit approval. This MINOR verdict does not constitute an approval marker or authorization to implement.

---

## Reviewer attestation

- All findings backed by verified file reads from 2026-04-29
- No GitHub mutations made (no comments, labels, PRs, closes, merges)
- No code implemented
- No plan edits made
- No approval markers created
- Adversarial stance applied: actively searched for false claims, scope errors, and newly introduced defects
