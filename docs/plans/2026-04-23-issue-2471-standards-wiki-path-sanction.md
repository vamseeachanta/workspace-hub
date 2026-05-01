# Plan for #2471: sanction `wiki/standards/` as first-class wiki page type

> **Status:** draft (v3 — addresses r2 findings)
> **Complexity:** T1 (schema + tooling surface, no content generation)
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2471
> **Decision reference:** issue #2471 comment 2026-04-23 — "Add sanctioned wiki/standards/"
> **Tree anchor:** HEAD `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` (2026-04-24) — all line-number citations below are against this commit.

---

## Attested Evidence (live-state inspection 2026-04-24 @ 8c235f5e4)

Plan-time live checks performed against the tree anchor above:

| Check | Command | Result |
|---|---|---|
| HEAD SHA | `git rev-parse HEAD` | `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` |
| `resolve_wiki_path.py` enumerates page types? | `grep -n "standards\\|workflows" scripts/data/llm-wiki/resolve_wiki_path.py` | **NO matches.** File is a root-directory resolver (67 lines); does not enumerate `wiki/<subdir>/` page types. **Excluded from Files-to-Change.** |
| `test_llm_wiki.py` exists? | `ls scripts/knowledge/tests/test_llm_wiki.py` | **EXISTS** (564 lines); contains `test_init_creates_wiki_dirs` pattern at lines ~72-79. **Modify, not create.** |
| Existing files under `knowledge/wikis/engineering/wiki/standards/` | `ls knowledge/wikis/engineering/wiki/standards/` | **7 files pre-exist:** `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`. TEMPLATE.md lands alongside these; `cmd_status` test assertion must account for ≥7 starting count (isolated tempdir test fixture keeps this count at 0). |
| Frontmatter shape of existing standards pages | `sed -n '1,10p'` each file | All 7 use legacy 4-field schema (`title`, `tags`, `sources`, `added`, `last_updated`). **None declare `code_id`, `publisher`, or `revision`.** This is load-bearing for the enforcement-surface decision below. |
| `pyramid-conformance-check.py` required fields | `grep -n "DT1_REQUIRED_FIELDS" scripts/knowledge/pyramid-conformance-check.py` | Line 37: `DT1_REQUIRED_FIELDS = {"title", "tags", "added", "last_updated"}`. All 7 existing standards files **already pass** the current checker. |
| `.gitignore` wiki rules | `sed -n '485,500p' .gitignore` | Lines 490-494: `/knowledge/wikis/*` ignored; only `!/knowledge/wikis/engineering/` and `!/knowledge/wikis/cross-links.md` re-included. |
| Tracking status of wiki CLAUDE.md files | `git ls-files knowledge/wikis/{engineering,marine-engineering,naval-architecture}/CLAUDE.md` | All three paths **tracked** (verified). Despite `/knowledge/wikis/*` being ignored, marine-engineering and naval-architecture CLAUDE.md files were tracked before the ignore rule landed, so `git ls-files` returns them. Amendments to these two files **will commit cleanly**. |
| `llm_wiki.py` INIT_DIRS / cmd_status | `sed -n '40,55p' scripts/knowledge/llm_wiki.py` and `275,285p` | Line 42-52: `INIT_DIRS` list contains `wiki/entities`, `wiki/concepts`, `wiki/sources`, `wiki/comparisons`, `wiki/visualizations`; no `standards` or `workflows`. Line 279: `for sub in ["entities", "concepts", "sources", "comparisons", "visualizations"]` — same. |

---

## Resource Intelligence Summary

### Existing repo code (ls-verified 2026-04-24 @ 8c235f5e4)
- `knowledge/wikis/marine-engineering/CLAUDE.md` — current sanctioned page types: `entities/`, `concepts/`, `sources/`, `comparisons/`, `visualizations/`. Will be amended to add `standards/`.
- `knowledge/wikis/engineering/CLAUDE.md` — **already declares** `wiki/{concepts,entities,sources,standards,workflows}/` on line 7. No amendment required — this wiki is already conformant for `standards/`.
- `knowledge/wikis/naval-architecture/CLAUDE.md` — present and git-tracked; will be amended.
- `knowledge/wikis/maritime-law/CLAUDE.md`, `knowledge/wikis/personal/CLAUDE.md`, `knowledge/wikis/health-reports/CLAUDE.md` — out of scope for #2471 (non-standards wikis); will not be amended.
- `scripts/knowledge/pyramid-conformance-check.py` — frontmatter completeness checker (line 37: `DT1_REQUIRED_FIELDS = {"title", "tags", "added", "last_updated"}`). **Not extended by this plan** — see enforcement-surface decision below.
- `scripts/knowledge/llm_wiki.py` — `INIT_DIRS` constant at lines 42-52 enumerates created directories; currently missing `wiki/standards/`. `cmd_status` loop at line 279 iterates `["entities", "concepts", "sources", "comparisons", "visualizations"]` — missing `standards`. This is the correct surface for the sanction.
- `scripts/knowledge/wiki-ingest-cron.sh` — ingest driver; path-agnostic, no change.
- `scripts/data/llm-wiki/resolve_wiki_path.py` — **does NOT enumerate page types** (grep confirmed); resolves only the wiki root directory. **Excluded from Files-to-Change.**
- `scripts/knowledge/tests/test_llm_wiki.py` — **exists** (564 lines); will be modified to add `standards/` assertions.
- `.gitignore` — lines 490-494: `/knowledge/wikis/*` ignored; `engineering/` re-included. `marine-engineering/CLAUDE.md` and `naval-architecture/CLAUDE.md` are individually tracked (`git ls-files` verified), so amendments commit cleanly.

### Standards (meta — this plan is itself about standards governance)
| Standard / contract | Status | Source |
|---|---|---|
| Workspace issue-planning retrieval contract | active | `docs/plans/README.md` |
| llm-wiki frontmatter/index/log contract | active | `knowledge/wikis/*/CLAUDE.md` |
| Pyramid conformance contract (DT-1) | active; required-field set = `{title, tags, added, last_updated}` | `scripts/knowledge/pyramid-conformance-check.py:37` |
| Enforcement gradient | active | `.claude/rules/patterns.md` |

### Documents consulted
- Issue #2471 body — acceptance criteria sanctioning a durable destination.
- #2471 comment 2026-04-23 — user routing decision "Add sanctioned `wiki/standards/`".
- r1 and r2 adversarial reviews (2026-04-23, 2026-04-24) — findings tracked inline below.
- Issue #2227 — blocked CSA portion; will cite this plan as unblocking artifact.
- Issue #2216 — ACMA-codes umbrella.

---

## Scope

This plan will:
1. Add `standards/` to the sanctioned page-type list for the two wikis that do not yet declare it (marine-engineering, naval-architecture). The engineering wiki already declares `standards/` and will not be amended.
2. Define the frontmatter contract for `wiki/standards/*.md` pages (neutral across publishers — no per-code routing).
3. Extend `llm_wiki.py` so `INIT_DIRS` includes `wiki/standards/`, and `cmd_status`'s counting loop includes `standards`.
4. Produce one sanctioned neutral template at `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` (template-only, publisher-agnostic) to prove the schema end-to-end.
5. Not promote any publisher-specific content (CSA, OCIMF, API, DNV) into `wiki/standards/` — that is #2227's job, unblocked by this sanction. Per decision #2471 ("sanctions path shape, not per-code routing"), this plan will not carry a CSA-specific page.

### Scope decision on `workflows/` (Gemini r2 P3)

v2 bundled `workflows/` into `INIT_DIRS` and `cmd_status` alongside `standards/`. Gemini's r2 review flagged this as scope creep since issue #2471's title names `standards/` only. **v3 narrows scope to `standards/` only.** A follow-up issue will be filed after plan approval tracking the symmetric sanction for `workflows/` (the engineering wiki already declares it at CLAUDE.md line 7, so the sanction is partial-done — follow-up captures the `INIT_DIRS`/`cmd_status` symmetry and whether other wikis opt in). This keeps #2471's diff minimal and the scope fence tight.

## Non-goals

- Will NOT promote CSA/OCIMF/DNV/API content into `wiki/standards/` at scale — deferred to #2227 and future content plans.
- Will NOT hardcode any per-publisher code (e.g., CSA) into the sanction artifacts — the decision explicitly scopes this plan to path shape only.
- Will NOT add `standards/` to non-standards wikis (maritime-law, personal, health-reports).
- Will NOT modify `.gitignore` to re-include `marine-engineering/` or `naval-architecture/` — tracking status is orthogonal to path sanctioning.
- Will NOT restructure `raw/standards/` — unaffected.
- Will NOT change cross-wiki link syntax or frontmatter for existing page types.
- Will NOT modify `scripts/knowledge/pyramid-conformance-check.py` — see enforcement-surface decision below.
- Will NOT extend `pyramid-conformance-check.py`'s `DT1_REQUIRED_FIELDS` to include `code_id`, `publisher`, `revision` in this plan. **Enforcement remains Level-0 prose** (see rationale below). A follow-up issue will be filed tracking the Level-2 script promotion.
- Will NOT backfill `code_id`/`publisher`/`revision` frontmatter into the 7 existing standards files under `knowledge/wikis/engineering/wiki/standards/`. Backfill is per-code metadata work and belongs to content plans (#2227 class), not a schema-sanctioning plan.
- Will NOT include `workflows/` in `INIT_DIRS` or `cmd_status` changes — deferred to follow-up issue (see Scope decision above).
- Will NOT modify `scripts/data/llm-wiki/resolve_wiki_path.py` — grep confirms it does not enumerate page types (it resolves the wiki root directory only).

---

## Enforcement-Surface Decision (resolves r2 P1 #3)

r2 Claude flagged: "new required fields (`code_id`, `publisher`, `revision`) have no Level-2 enforcement surface" per `.claude/rules/patterns.md`.

**Decision: accept Level-0 prose-only enforcement for this plan; file a follow-up issue for Level-2 promotion.**

**Rationale:**
1. **Scope fence integrity.** This plan's load-bearing decision is "path shape, not per-code routing." The three new required fields (`code_id`, `publisher`, `revision`) are per-code metadata. Extending the checker to enforce them requires backfilling 7 existing files with publisher-specific values (`csa-z276`, `api-579-1-asme-ffs-1`, `dnv-rp-c203`, etc.), which is per-code content work by definition. That work belongs in #2227-class plans.
2. **Regression risk of the alternative.** If v3 extended `DT1_REQUIRED_FIELDS` without backfill, the 7 pre-existing standards files (all currently passing the checker per live inspection) would start failing. Backfill-in-same-plan is the only safe alternative, and it is scope creep.
3. **Precedent.** `.claude/rules/patterns.md` explicitly describes Level-0 → Level-2 as a migration path ("Migration path: when a prose rule can be expressed as exit 0/1, write a script"). Filing a follow-up issue is the documented vehicle for this migration.

**Follow-up issue to file** (during the atomic commit, before marking #2471 complete):
- Title: "Extend pyramid-conformance-check.py DT1_REQUIRED_FIELDS to include standards-page fields (code_id, publisher, revision)"
- Body: references #2471, summarizes the 7 files needing backfill, cites `.claude/rules/patterns.md` enforcement gradient, labels `enforcement`, `wiki`, `tech-debt`.
- Capture the issue number in the #2471 completion comment so the gap is traceable.

---

## Files to Change

| File | Change type | Why |
|---|---|---|
| `knowledge/wikis/marine-engineering/CLAUDE.md` | modify | Add `standards/` to sanctioned list + frontmatter schema |
| `knowledge/wikis/naval-architecture/CLAUDE.md` | modify | Same |
| `knowledge/wikis/engineering/CLAUDE.md` | no change | Already declares `wiki/{concepts,entities,sources,standards,workflows}/` at line 7 |
| `scripts/knowledge/llm_wiki.py` | modify | Add `"wiki/standards"` to `INIT_DIRS` (lines 42-52); extend `cmd_status` subdir loop (line 279) to include `"standards"` |
| `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` | create | Neutral (publisher-agnostic) schema-validation template; path already git-tracked |
| `scripts/knowledge/tests/test_llm_wiki.py` | modify | Extend existing `test_init_creates_wiki_dirs` and add `cmd_status`-counts-`standards` test |
| `docs/plans/README.md` | modify | Add row citing this plan (pre-staged text below) |

**Explicitly NOT modified** (decisions resolved at plan time, not deferred):
- `scripts/data/llm-wiki/resolve_wiki_path.py` — grep confirmed no page-type enumeration; file is out of scope.
- `scripts/knowledge/pyramid-conformance-check.py` — Level-0 prose enforcement accepted; Level-2 promotion deferred to follow-up issue.
- 7 existing files under `knowledge/wikis/engineering/wiki/standards/` — backfill deferred to follow-up.

### Pre-staged `docs/plans/README.md` row

```
| 2026-04-24 | #2471 | sanction `wiki/standards/` | `docs/plans/2026-04-24-issue-2471-wiki-standards-sanction.md` | plan-approved |
```

(Exact phrasing and column alignment will match the surrounding rows at execution time.)

## Frontmatter Contract for `wiki/standards/*.md`

Required fields (in addition to base schema):

| Field | Required | Type | Description |
|---|---|---|---|
| `title` | required (enforced L2) | string | Standard name + short-form (e.g., "CSA Z276: LNG — production, storage, and handling") |
| `code_id` | required (L0 prose) | string | Canonical code identifier (e.g., `csa-z276`, `api-17j`, `ocimf-mooring-equipment-guidelines-4e`) |
| `publisher` | required (L0 prose) | string | Publishing body (e.g., `CSA Group`, `API`, `OCIMF`) |
| `revision` | required (L0 prose) | string | Revision/edition/year (e.g., `2023`, `4e`, `1.2`) |
| `jurisdiction` | optional | string | Geographic or regulatory scope (e.g., `Canada`, `international`, `US-federal`) |
| `supersedes` | optional | list | Prior revisions or codes replaced |
| `added` | required (enforced L2) | date | Per existing schema |
| `last_updated` | required (enforced L2) | date | Per existing schema |
| `tags` | required (enforced L2) | list | Per existing schema |
| `sources` | optional | list | Links to `raw/standards/*` source PDFs (canonical form) |

**Enforcement note:** `title`, `added`, `last_updated`, `tags` are enforced today by `pyramid-conformance-check.py:37`. The three new fields `code_id`, `publisher`, `revision` are required by this contract but enforced only at Level 0 (prose) pending the follow-up issue filed per the Enforcement-Surface Decision above.

## TEMPLATE.md placeholder values

TEMPLATE.md will ship with the following exact frontmatter:

```yaml
---
title: "TEMPLATE — Standards Page"
code_id: TEMPLATE
publisher: TEMPLATE
revision: TEMPLATE
tags: [standard, template]
sources: []
added: 2026-04-24
last_updated: 2026-04-24
---
```

Body (after frontmatter):

```
# TEMPLATE — Standards Page

Template for publisher-specific standards pages. Populate per the frontmatter contract declared in `knowledge/wikis/engineering/CLAUDE.md` and `docs/plans/2026-04-24-issue-2471-wiki-standards-sanction.md`. Issue #2227 will add concrete pages (CSA Z276, etc.) under domain wikis once their git-tracking status is resolved.
```

**Why these placeholder values pass `pyramid-conformance-check.py`:** the checker's `DT1_REQUIRED_FIELDS = {"title", "tags", "added", "last_updated"}` (line 37). TEMPLATE.md supplies all four with non-empty values (`"TEMPLATE — Standards Page"`, `[standard, template]`, `2026-04-24`, `2026-04-24`). The three L0-prose-only fields (`code_id`, `publisher`, `revision`) use the literal string `TEMPLATE`, which is a non-empty string but deliberately flagged (by value) as a template sentinel so downstream consumers or a future L2 checker can distinguish template from populated pages.

## Build Sequence

1. Amend `scripts/knowledge/llm_wiki.py`: extend `INIT_DIRS` with `"wiki/standards"` (insert after `"wiki/visualizations"` to preserve diff readability); extend `cmd_status`'s subdir loop list to include `"standards"`.
2. Extend `scripts/knowledge/tests/test_llm_wiki.py`:
   - Add assertion in `test_init_creates_wiki_dirs` (around line 72) that `(wiki_root / "wiki" / "standards").exists()`.
   - Add a new test `test_status_counts_standards_subdir` that runs `cmd_init test-domain`, writes exactly 2 fixture `.md` files (`fixture-a.md`, `fixture-b.md`) into `<tempdir>/test-domain/wiki/standards/`, runs `cmd_status test-domain`, and asserts the returned count dict has `counts["standards"] == 2`. The isolated tempdir fixture guarantees starting count is 0, independent of the 7 pre-existing files under the real engineering wiki.
   - Add a regression assertion `test_status_counts_engineering_wiki_standards` (smoke only, skipped if running in a minimal-fixture CI) that runs `cmd_status engineering` against the real wiki root and asserts `counts["standards"] >= 7` (current real-world count). Guarded by `@pytest.mark.skipif(not ENGINEERING_WIKI_PATH.exists(), ...)`.
3. Amend the two wiki `CLAUDE.md` files (marine-engineering, naval-architecture) with identical `standards/` section insertions (preserve existing ordering). Do NOT touch engineering/CLAUDE.md.
4. Create `knowledge/wikis/engineering/wiki/standards/TEMPLATE.md` with the exact frontmatter and body specified in the "TEMPLATE.md placeholder values" section above.
5. **Validation — run `uv run python scripts/knowledge/pyramid-conformance-check.py` and assert clean exit (exit code 0) covering TEMPLATE.md plus the 7 pre-existing standards files.** Capture the output in the PR description so reviewers can confirm the new template + all existing standards pages still pass.
6. Run `uv run python scripts/knowledge/llm_wiki.py status --wiki engineering` and confirm the output reports `standards` as a count key with value ≥ 8 (7 pre-existing + 1 new TEMPLATE.md).
7. Run `uv run pytest scripts/knowledge/tests/test_llm_wiki.py -v` and confirm all new/amended tests pass.
8. Update `docs/plans/README.md` to add the pre-staged row.
9. File the follow-up issue for Level-2 enforcement promotion (title and body specified in the Enforcement-Surface Decision section).
10. Atomic commit per the standard plan-execution convention; push to a feature branch.

## TDD / Validation List

| Test | Test fixture | Passes when | Failure signal |
|---|---|---|---|
| `test_init_creates_wiki_dirs` (amended) | `cmd_init test-domain` in isolated tempdir `WIKIS_DIR` | `(wiki_root / "wiki" / "standards").exists()` is true | missing dir → schema not sanctioned |
| `test_status_counts_standards_subdir` (new) | Isolated tempdir: `cmd_init test-domain`, then write `fixture-a.md` + `fixture-b.md` to `<tempdir>/test-domain/wiki/standards/` | `cmd_status` returns `counts["standards"] == 2` | KeyError on `"standards"` key, or count mismatch → `cmd_status` loop not extended |
| `test_status_counts_engineering_wiki_standards` (new, smoke/regression) | Real engineering wiki at `knowledge/wikis/engineering/`, run `cmd_status engineering` | `counts["standards"] >= 7` (7 pre-existing + TEMPLATE.md = 8 expected after execution) | Regression — indicates `cmd_status` lost visibility into the existing engineering/standards/ files |
| `pyramid-conformance-check.py` passes on TEMPLATE.md | Real tree after step 4 of Build Sequence | Exit code 0; stdout reports TEMPLATE.md scanned, 0 failing | Exit non-zero → placeholder values not accepted by `DT1_REQUIRED_FIELDS` |
| `pyramid-conformance-check.py` regression on 7 existing standards files | Real tree post-change | Exit code 0 across all 7 files (same as pre-change state) | Exit non-zero → some change regressed previously-passing files |
| `docs/plans/README.md` row exists | Real tree post-step-8 | `grep "2471" docs/plans/README.md` matches | row missing |
| Follow-up issue filed | GitHub | `gh issue view <N>` returns the Level-2-promotion issue created in step 9 | Missing follow-up → enforcement gap untracked |

## Acceptance Criteria Alignment

- [ ] sanctioned `wiki/standards/` durable destination is documented (publisher-neutral) — via `INIT_DIRS`, `cmd_status`, and CLAUDE.md amendments
- [ ] relevant wiki CLAUDE/schema guidance allows the destination explicitly — two CLAUDE.md files amended (engineering already conformant)
- [ ] gitignore/durability expectations are documented — `knowledge/wikis/engineering/` re-included; TEMPLATE stub lands there; domain-wiki tracking out of scope
- [ ] #2227 can split OCIMF and CSA without unresolved routing ambiguity — `wiki/standards/` path sanctioned generically; #2227 plan v2 will cite this plan
- [ ] enforcement-gap traceable — follow-up issue filed and referenced in #2471 completion comment

(Checkboxes unchecked per future-tense-plan convention; execution flips them.)

## Risk & Rollback

- **Risk:** amending two CLAUDE.md files in isolation could introduce drift. *Mitigation:* same paragraph inserted in both, verified by diff.
- **Risk:** `llm_wiki.py` `INIT_DIRS`/`cmd_status` edit could affect existing wikis that ran `cmd_init` before the change. *Mitigation:* `cmd_init` uses `mkdir -p` semantics (idempotent); `cmd_status` edit is additive (new key, no removal).
- **Risk:** downstream consumers of `cmd_status` output (dashboards, other scripts) reading the counts dict may break if they use strict key-set assertions. *Mitigation:* additive keys are generally safe; will grep for other callers of `cmd_status` in the repo before commit and flag in the PR description if any strict-key consumers exist.
- **Risk:** the TEMPLATE.md sentinel value `TEMPLATE` for `code_id`/`publisher`/`revision` could be copy-pasted into real standards pages and not replaced. *Mitigation:* the follow-up Level-2 issue will include a check that rejects the literal string `TEMPLATE` in those fields. Until then, Level-0 prose warning in TEMPLATE.md body and in wiki CLAUDE.md amendments.
- **Risk:** Level-0 prose-only enforcement on `code_id`/`publisher`/`revision` could allow #2227 or future content plans to ship inconsistent values (e.g., `CSA` vs `CSA Group` vs `csa-group` for `publisher`). *Mitigation:* tracked by the follow-up issue; frontmatter contract in engineering CLAUDE.md gives canonical example values so human reviewers can catch drift.
- **Rollback:** single revert per atomic commit; TEMPLATE stub deletion is isolated; follow-up issue can stay open or be closed without reverting the plan.

## Downstream unblocks

- #2227 CSA/OCIMF portions can proceed against `knowledge/wikis/<domain>/wiki/standards/<code>.md` once domain tracking is resolved; #2227 plan v2 will cite this plan.
- Future standards coverage (API, OCIMF, DNV, ISO) has a sanctioned path shape.
- Level-2 enforcement promotion (new follow-up issue) can proceed independently once this plan lands.

## Review History

| Revision | Reviewer | Verdict | Disposition |
|---|---|---|---|
| v1 | r1 (Claude, Gemini) | — | addressed in v2 |
| v2 | r2 Claude | MAJOR (3 P1, 4 P2, 2 P3) | addressed in v3 below |
| v2 | r2 Gemini | MINOR (2 P3) | addressed in v3 below |

### v3 disposition of r2 findings

| r2 finding | Priority | Resolution in v3 |
|---|---|---|
| `resolve_wiki_path.py` row marked "conditional" | P1 (Claude) | Live grep confirmed no page-type enumeration. **Excluded from Files-to-Change**, explicit entry in "Explicitly NOT modified" list. |
| TEMPLATE.md placeholder values unspecified | P1 (Claude) | Exact frontmatter block specified in "TEMPLATE.md placeholder values" section; validation step 5 of Build Sequence asserts clean checker exit. |
| No enforcement surface for `code_id`/`publisher`/`revision` | P1 (Claude) | Enforcement-Surface Decision section locks Option (b): Level-0 prose-only, with follow-up issue filed in Build Sequence step 9. Rationale documented (scope fence + regression risk + migration-path precedent). |
| Line-number citations not SHA-anchored | P2 (Claude) | HEAD SHA `8c235f5e4a02a5ce633f43578b7335e30a53fb4b` recorded in frontmatter ("Tree anchor") and in Attested Evidence block. |
| `test_llm_wiki.py` "modify or create" unresolved | P2 (Claude) | Live `ls` confirmed file exists (564 lines). Files-to-Change row says "modify" (not "modify or create"). |
| Existing files under `wiki/standards/` not asserted | P2 (Claude) | Attested Evidence block lists all 7 pre-existing files; test strategy accounts for non-zero starting count via isolated-tempdir fixture + smoke-regression test against real wiki. |
| Validation row needs test-fixture specification | P2 (Claude) | TDD table rewritten with explicit "Test fixture" column naming who places which files where. |
| `naval-architecture/CLAUDE.md` tracking status not verified | P3 (Claude) | `git ls-files` confirmed tracked despite ignore rule; noted in Attested Evidence block. |
| No coverage of downstream `cmd_status` consumers | P3 (Claude) | Added Risk row explicitly + grep-for-callers mitigation step. |
| `workflows/` scope creep | P3 (Gemini) | **v3 narrows to `standards/` only.** `workflows/` deferred to follow-up issue (see "Scope decision on `workflows/`" section). |
| Missing implementation steps for `resolve_wiki_path.py` | P3 (Gemini) | Resolved by excluding the file (see P1 Claude resolution above). |
