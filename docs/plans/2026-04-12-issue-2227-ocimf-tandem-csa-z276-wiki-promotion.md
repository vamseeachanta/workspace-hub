# Plan for #2227: Promote OCIMF Tandem Mooring and CSA Z276 Coverage into LLM-Wikis

> **Status:** draft (v3 — addresses r2 Codex+Claude+Gemini findings; wiki/standards/ sanction unblocked via #2471 decision 2026-04-23)
> **Complexity:** T2
> **Date:** 2026-04-12 (v1) / 2026-04-21 (v2 revision) / 2026-04-23 (v3 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2227
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** `scripts/review/results/2026-04-21-plan-2227-codex.md` (MAJOR, r1) | `scripts/review/results/2026-04-21-plan-2227-gemini.md` (APPROVE, r1) | `scripts/review/results/2026-04-23-plan-2227-claude.md` (MAJOR, r2) | `scripts/review/results/2026-04-23-plan-2227-codex.md` (r2) | `scripts/review/results/2026-04-23-plan-2227-gemini.md` (r2) | `scripts/review/results/2026-04-23-plan-2227-disagreement.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — existing OCIMF MEG4 page, git-tracked (confirmed via `git ls-files`).
- Found: `knowledge/wikis/engineering/wiki/standards/` — directory exists and is git-tracked, containing `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`.
- Found: `knowledge/wikis/marine-engineering/wiki/` — directory is gitignored (`.gitignore:492 /knowledge/wikis/*`; only `!/knowledge/wikis/engineering/` at line 493 and `!/knowledge/wikis/cross-links.md` at line 494 are re-included). Subdirs present: `comparisons/`, `concepts/`, `entities/`, `sources/`, `visualizations/`. NO `standards/` directory, and marine-engineering `CLAUDE.md` schema (lines 6-23) does not list `standards/` as a sanctioned `wiki/` subcategory (literal `standards/` appears only at line 11 under `raw/`).
- Found: `scripts/knowledge/llm_wiki.py` — lint command at `cmd_lint` (line 683) validates frontmatter for `entities/concepts/sources/comparisons/standards/workflows` (line 632). Supports `standards/` in frontmatter check but orphan/link checks only traverse `entities/concepts/sources/comparisons` (line 748).
- Found: `data/document-index/summaries/sha256:5e5f...json`, `...:b576...json`, `...:3aa1...json` — summary artifacts EXIST for all three target doc_keys, with `summary: ""` across all three. **Correction (r2):** `text_preview` content is heterogeneous: OCIMF-TANDEM (`5e5f…`) has `text_preview` length 0 (truly empty); **CSA Z276.1-20 (`b576…`) and CSA Z276.18 (`3aa1…`) each carry a `text_preview` of 1000 characters of CORRUPTED OCR** — the first 200 chars of `b576…` read `"pyorat\npakota\nmakaamaan\nlujana\njakcanut\ntiedocca\nperaan\ncannikka\n…"` (garbled tokens resembling Finnish) and `3aa1…` similarly reads `"monen\nkuunnella\ncannikka\ncamoin\npyctyvat\nvaatteitaan\n…"`. Neither is usable content but neither is empty. Downstream: remediation for CSA is "fix encoding/OCR corruption", not "re-extract from empty state"; OCIMF remediation remains "extract preview content" (currently null).
- User decision on #2471 (2026-04-23 issue comment): `wiki/standards/` sanctioned as a first-class page type; per-code wiki routing (marine-engineering vs naval-architecture vs engineering) deferred to the per-standard owner. #2471 codification plan (schema amendments, lint path, first sanctioned stub) is in-flight on branch `plan/issue-2471-standards-wiki-path-sanction` at commit `17118f381` (v1 flagged P1 issues in r1 cross-review; v2 revision pending on Lane G). This plan cites the stable DECISION, not the in-flight codification; #2227 execution must verify codification state at run time (see Prereq Matrix row).

### Standards
| Standard | Ledger status | doc_key (sha256) | Summary artifact | Content ready? |
|---|---|---|---|---|
| `OCIMF-TANDEM-MOORING` | done | `sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af` | file exists, `summary=""` | **NO** — blocker from #2245 handoff |
| `OCIMF-MEG4-2018` | done | (existing wiki page); no new summary required | n/a for narrow historical update | partial — update only if ledger notes warrant |
| `CSA-Z276.1-20` | done | `sha256:b576ada30e9ccea727ecab10e1f2a0e435613b25147e3bbb2b3f3d2b718766fd` | file exists, `summary=""` | **NO** — blocker |
| `CSA-Z276.18` | done | `sha256:3aa1fdc3e2c73e1f9c3bb476e5eb663a7742518462bf1abefcbe26b7efd87fd4` | file exists, `summary=""` | **NO** — blocker |
| `CSA-Z276.2-19` | done | — | — | **OUT OF SCOPE** (routed to #2283 via #2244 triage) |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — current page, cross-links to MEG3/tandem may be added narrowly.
- `knowledge/wikis/engineering/wiki/index.md` — engineering standards section lists existing `ocimf-meg4` entry; needs row for `ocimf-tandem-mooring`.
- `knowledge/wikis/engineering/wiki/log.md` — promotion log, append-only.
- `knowledge/wikis/marine-engineering/wiki/index.md` — has `## Entities | ## Concepts | ## Sources | ## Comparisons` sections; NO `## Standards` heading.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — schema does NOT sanction `wiki/standards/`; migrating CSA pages here without a schema amendment would silently invent a taxonomy.
- `knowledge/wikis/engineering/CLAUDE.md` — sanctions `wiki/{concepts,entities,sources,standards,workflows}/`.

### Documents consulted
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` — parent approved plan.
- `docs/plans/2026-04-12-issue-2245-acma-summary-classification-unblock.md` — prerequisite; CLOSED 2026-04-13 with `ready_for_2227: false` handoff artifact.
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` — CLOSED 2026-04-11 (completed).
- `docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md` — CLOSED; defines the reuse contract this plan consumes.
- `docs/reports/acma-wiki-unblock-2245-handoff.yaml` — authoritative per-target blocker evidence (DRM + failed pdftotext).
- `scripts/review/results/2026-04-21-plan-2227-codex.md` (MAJOR, v1 reviewed 2026-04-21) — internal `wiki/standards/` contradiction, TDD contract missing, prereq matrix underspecified.
- `scripts/review/results/2026-04-21-plan-2227-gemini.md` (APPROVE, v1) — flags same "FAIL for execution readiness" but approves on scope.
- `scripts/review/results/2026-04-15-plan-2227-claude.md` — earlier: confirmed gitignore + taxonomy blockers.
- Issue #2227 comment thread (2026-04-12 → 2026-04-21): #2244 triage routed broader CSA/API breadth to #2283/#2284/#2285/#2286/#2287; rollback 2026-04-21 15:07 moved label → `status:plan-review`.

### Gaps identified
- Reusable summaries for all three target doc_keys are unusable today; all three have `summary: ""`, and `text_preview` is either empty (OCIMF) or corrupted OCR (CSA x2). The reuse contract (#2207) is not literal about "non-empty" but the promotion spirit requires evidence beyond title.
- `knowledge/wikis/marine-engineering/` is gitignored — promoting CSA pages there would be non-durable without an explicit `.gitignore` exemption or an alternative canonical location.
- Marine-engineering `CLAUDE.md` schema does not list `wiki/standards/` as a sanctioned directory; the #2471 decision (2026-04-23) sanctions the `wiki/standards/` page type but the CLAUDE.md amendment is tracked in the #2471 codification plan, not yet landed. Creating a marine-engineering `wiki/standards/` page before the codification lands would silently broaden schema.
- `llm_wiki.py lint` orphan/link checks do not traverse `standards/` — if the plan relies on lint as a TDD gate, that coverage must be verified explicitly; T13 (new in v3) adds an explicit inbound-link assertion as a harder gate than lint.
- No integration test exists that asserts standards-page presence/frontmatter for a given doc_key; the TDD gate must add or extend one.

<!-- Verification (v3): distinct sources consulted = 17+ (3 ledger entries + 3 summary JSON files [inspected via jq] + 3 gitignore lines [verified 492-494] + 2 wiki CLAUDE.md files + 4 prior plans + 1 handoff yaml + 4 review artifacts inc r2 triad + 1 issue thread + 1 #2471 decision comment + llm_wiki.py lint source). -->

---

## Deliverable

**Branch-conditional deliverable.** This plan has two execution branches; the acceptance criteria and file list are scoped per branch, not pre-committed.

- **Branch A (CONTENT-READY):** OCIMF Tandem Mooring page lands in `knowledge/wikis/engineering/wiki/standards/` (the git-tracked, schema-sanctioned location), plus a narrowly grounded update to `ocimf-meg4.md`. CSA Z276.1 and Z276.18 pages land only after the two prerequisite sub-gates below pass; default is to defer those two pages to a follow-up issue (see Branch B / Prereq Matrix).
- **Branch B (CONTENT-BLOCKED — current state):** No wiki pages are written. Plan execution produces (1) a blocker comment on #2227 citing the specific summary-content gap, (2) a follow-up issue (or reuses #2245 follow-up) for the marine-wiki taxonomy + gitignore decision, and (3) a follow-up issue for re-extraction of the three PDFs on a machine that can read them. Issue #2227 stays blocked until both sub-gates (content + marine taxonomy) clear.

Rationale: v1 pre-committed the CSA pages to `marine-engineering/wiki/standards/` while simultaneously requiring a "stop if conventions don't permit" check — an internal contradiction Codex MAJOR #1 flagged. Branch-conditional deliverable resolves that.

---

## Scope Boundaries

### In scope now (Branch A path, only if content sub-gate passes)
- Create `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` (git-tracked location).
- Narrowly grounded update to `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` citing tandem-mooring cross-reference from ledger notes only.
- Append promotion entry to `knowledge/wikis/engineering/wiki/log.md`; add row to `knowledge/wikis/engineering/wiki/index.md`.

### In scope now (Branch B — current state, no wiki writes)
- Post blocker comment summarizing the content gap on #2227, citing specific previews: OCIMF `5e5f…` preview length 0; CSA `b576…` preview 1000 chars of corrupted OCR (first 200: `"pyorat\npakota\nmakaamaan\n…"`); CSA `3aa1…` preview 1000 chars of corrupted OCR (first 200: `"monen\nkuunnella\ncannikka\n…"`).
- Link or open a **content remediation** follow-up with per-target scope: OCIMF needs preview extraction (currently empty); CSA x2 need encoding/OCR corruption fix (previews exist but corrupted — this is the r2 rescope).
- Confirm the marine-wiki taxonomy follow-up is tracked in #2471 (page-type sanction — DECISION stable; codification in-flight). Per-code wiki routing for CSA remains an open per-standard decision and is not pre-committed by this plan.
- Confirm #2260 metadata-only wiki sweep is distinct from this issue's grounded-content scope.

### Explicitly out of scope
- CSA Z276.2-19 (→ #2283), additional OCIMF (→ #2284), API RP 2SK (→ #2285), SIGTTO (→ #2286), LR/Noble Denton (→ #2287).
- Creating `knowledge/wikis/marine-engineering/wiki/standards/` under current schema/gitignore (requires the taxonomy decision first).
- Re-parsing DRM-protected source PDFs.
- Promoting any CSA page inside this issue unless BOTH the content sub-gate AND the marine taxonomy sub-gate clear within the window of this issue; otherwise defer to follow-up.

---

## Prerequisite Matrix

| Prereq | Current state | Blocker? | Source |
|---|---|---|---|
| #2216 (parent umbrella) | OPEN, `status:plan-review` | Non-blocking for this child — parent tracks umbrella; this issue is bounded | `gh issue view 2216` |
| #2225 (source registration) | CLOSED 2026-04-11, `status:plan-approved` | NOT blocking (completed) | `gh issue view 2225` |
| #2207 (reuse contract) | CLOSED, `status:plan-approved` | NOT blocking (completed) | `gh issue view 2207` |
| #2245 (summary artifacts) | CLOSED 2026-04-13, handoff `ready_for_2227: false` | **Content sub-gate: BLOCKING** — all three `summary=""`; OCIMF `text_preview=""` (length 0); CSA x2 `text_preview` = 1000-char corrupted OCR | `docs/reports/acma-wiki-unblock-2245-handoff.yaml`, `data/document-index/summaries/sha256:{5e5f,b576,3aa1}.json` |
| #2471 `wiki/standards/` page-type sanction (DECISION) | user-approved 2026-04-23 via issue comment | **NOT BLOCKING** — decision is stable; sanctions page-type path shape | `gh issue view 2471` comment 2026-04-23 |
| #2471 codification (schema CLAUDE.md amendments + lint path + pyramid allow-list + per-wiki `.gitignore` re-include) | IN-FLIGHT on `plan/issue-2471-standards-wiki-path-sanction` @ `17118f381`; v1 flagged P1 in r1; v2 pending on Lane G | **BLOCKING for marine-engineering/naval-architecture CSA pages** until landed on main; NOT blocking for engineering wiki (already sanctions `wiki/standards/`) | branch `plan/issue-2471-standards-wiki-path-sanction`, docs/plans/2026-04-23-issue-2471-standards-wiki-path-sanction.md (on branch) |
| marine-wiki `wiki/standards/` CLAUDE.md amendment landed on main | not yet landed (awaits #2471 codification merge) | **BLOCKING for CSA pages** | `knowledge/wikis/marine-engineering/CLAUDE.md` (main) — `wiki/` tree block lists only `entities/concepts/sources/comparisons/visualizations/`; literal `standards/` substring appears only under `raw/` (line 11) |
| marine-wiki gitignore re-include | `/knowledge/wikis/*` ignored; only `engineering/` and `cross-links.md` exempted | **BLOCKING for CSA pages** unless pattern amended via #2471 codification | `.gitignore:492-494` (`/knowledge/wikis/*`, `!/knowledge/wikis/engineering/`, `!/knowledge/wikis/cross-links.md`) |
| engineering wiki `wiki/standards/` already sanctioned | line 7 of `knowledge/wikis/engineering/CLAUDE.md`: `Pages: wiki/{concepts,entities,sources,standards,workflows}/` | **NOT BLOCKING** for OCIMF Tandem (Branch A scope) | `knowledge/wikis/engineering/CLAUDE.md` |

**Classification rule:** OCIMF Tandem page (engineering wiki, git-tracked, engineering CLAUDE.md already sanctions `wiki/standards/`) needs only the content sub-gate (which today fails due to empty OCIMF preview). CSA pages need content sub-gate + #2471 codification landed on main (CLAUDE.md amendment + gitignore re-include) + per-code wiki routing decision. Today the content sub-gate fails for all three AND the #2471 codification has not landed → Branch B for all three. If the content sub-gate passes for OCIMF before #2471 codification lands, Branch A (engineering-only) can proceed independently; CSA remains deferred regardless.

---

## Pseudocode

```text
# Entry gate
# "load prereq matrix" is concrete: read the checked-in JSON/YAML artifacts named
# below, do not parse markdown tables from this plan.
load handoff_yaml = yaml.load("docs/reports/acma-wiki-unblock-2245-handoff.yaml")
load summary_5e5f = json.load("data/document-index/summaries/sha256:5e5f...json")
load summary_b576 = json.load("data/document-index/summaries/sha256:b576...json")
load summary_3aa1 = json.load("data/document-index/summaries/sha256:3aa1...json")

if handoff_yaml.ready_for_2227 is False
   OR summary_5e5f.summary == ""
   OR summary_b576.summary == ""
   OR summary_3aa1.summary == "":
    set CONTENT_SUB_GATE = FAIL
else:
    set CONTENT_SUB_GATE = PASS

# MARINE_TAXONOMY_SUB_GATE: scoped semantic check, NOT a bare substring match.
# Motivation: marine-engineering/CLAUDE.md line 11 contains "standards/" under the
# `raw/` subtree; a naive substring search would false-PASS against the raw/ line.
# Pseudocode must anchor to the `wiki/` block of the Directory Structure code fence.
parse marine_md = "knowledge/wikis/marine-engineering/CLAUDE.md"
extract wiki_block = the code-fenced block under "## Directory Structure" between the
                     `wiki/` line and the closing fence, EXCLUDING the `raw/` subtree
if wiki_block contains a bullet/line matching /^\s*standards\//:
    set TAXONOMY_SCHEMA_OK = True
else:
    set TAXONOMY_SCHEMA_OK = False

# Gitignore re-include: exact-line match against .gitignore (not substring).
gitignore_lines = read(".gitignore").splitlines()
if "!/knowledge/wikis/marine-engineering/" in gitignore_lines
   OR "!/knowledge/wikis/marine-engineering/wiki/standards/" in gitignore_lines
   OR any exact-line pattern that positively re-includes marine wiki/standards/:
    set TAXONOMY_GITIGNORE_OK = True
else:
    set TAXONOMY_GITIGNORE_OK = False

# Also verify #2471 codification has landed on main (not in-flight).
set CODIFICATION_LANDED = git.merge_base_ancestor(
    "origin/main", "plan/issue-2471-standards-wiki-path-sanction")
    AND required files (amended marine CLAUDE.md, amended .gitignore) exist on main HEAD

if TAXONOMY_SCHEMA_OK and TAXONOMY_GITIGNORE_OK and CODIFICATION_LANDED:
    set MARINE_TAXONOMY_SUB_GATE = PASS
else:
    set MARINE_TAXONOMY_SUB_GATE = FAIL

# Route
if CONTENT_SUB_GATE == FAIL:
    execute Branch B
    exit

# CONTENT_SUB_GATE == PASS → do engineering-wiki work regardless of marine state
create knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md:
    frontmatter: title, tags, added, last_updated, sources, domain=marine, cross_links
    body: scope, provenance back-links (doc_key, source_ref, promoted_from=2227)
    content grounded strictly in OCIMF-TANDEM-MOORING ledger entry + summary artifact

modify knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md:
    preserve all existing content
    add bounded tandem-mooring cross-reference ONLY if ledger notes warrant

append engineering wiki/log.md:
    one entry: "## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)"

modify engineering wiki/index.md:
    add row under ## Standards for ocimf-tandem-mooring

# CSA pages
if MARINE_TAXONOMY_SUB_GATE == FAIL:
    skip all CSA work
    record deferral in blocker comment / follow-up issue
else:
    (future; not this issue)
    create CSA pages in sanctioned location
    update marine-engineering wiki/log.md + index.md

# Verification
run uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
assert exit 0 OR only warnings (no errors)
run TDD tests (see §TDD Test List)
```

---

## Files to Change (branch-scoped)

### Branch A (CONTENT_SUB_GATE == PASS) — engineering wiki only
| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | net-new OCIMF guideline page (git-tracked, schema-sanctioned) |
| Modify | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` | narrowly grounded tandem cross-reference only |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | add row under `## Standards` for tandem page |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | append promotion log entry |
| Create | `tests/knowledge/test_ocimf_tandem_promotion.py` | per-standard assertion tests (see §TDD) |

### Branch A — CSA pages deferred (not in this issue's file list)
No file changes for CSA pages under any branch of this issue. CSA promotion is explicitly deferred until the marine-wiki taxonomy + gitignore decision lands in a separate issue.

### Branch B (CONTENT_SUB_GATE == FAIL — current state)
| Action | Path | Reason |
|---|---|---|
| Create | (no file changes; comment-only) | post blocker comment on #2227 |
| Optional | (new GH issue) | marine-wiki taxonomy decision follow-up |
| Optional | (new GH issue) | re-extract 3 DRM PDFs on alt toolchain |

---

## TDD Test List

All tests live at `tests/knowledge/test_ocimf_tandem_promotion.py` (new file) and are run via `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v`. Repo-integrated lint runs via `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering`.

| Test ID | Test name | What it verifies | Runner | Expected outcome | Gates which branch |
|---|---|---|---|---|---|
| T1 | `test_prereq_content_sub_gate` | #2245 handoff `ready_for_2227` is True AND each target's `summary_artifact.summary` is non-empty | pytest | currently FAILS → Branch B today; must PASS before Branch A | entry gate |
| T2 | `test_prereq_marine_taxonomy_sub_gate` | Parse `knowledge/wikis/marine-engineering/CLAUDE.md`; extract the `wiki/` block from the code fence under `## Directory Structure` (EXCLUDING the `raw/` subtree) and assert it contains a line matching regex `^\s*standards/` (path-anchored, not substring). AND `.gitignore` contains an exact line `!/knowledge/wikis/marine-engineering/` OR `!/knowledge/wikis/marine-engineering/wiki/standards/` (exact-line match via splitlines, NOT `grep 'standards/'`). AND verify the #2471 codification is landed on `origin/main` (use `git merge-base --is-ancestor plan/issue-2471-... origin/main` plus file-content check). | pytest | currently FAILS → CSA pages deferred; guards specifically against the r2 false-PASS from substring match on the `raw/standards/` line | CSA sub-branch |
| T3 | `test_ocimf_tandem_page_exists` | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists | pytest (`pathlib.exists()`) | PASS post-Branch A | Branch A |
| T4 | `test_ocimf_tandem_frontmatter_valid` | Page has `title`, `tags`, `added`, `last_updated`, `sources`, `domain=marine` frontmatter via existing `_parse_frontmatter` helper in `scripts/knowledge/llm_wiki.py` | pytest | PASS post-Branch A | Branch A |
| T5 | `test_ocimf_tandem_provenance_fields` | Page body contains `doc_key: sha256:5e5f...`, `source_ref` pointing to ledger entry, and `promoted_from: 2227` | pytest (regex match) | PASS post-Branch A | Branch A |
| T6 | `test_ocimf_tandem_cross_reference_to_meg4` | Page contains a `[[ocimf-meg4]]` or equivalent markdown link back to the MEG4 page | pytest | PASS post-Branch A | Branch A |
| T7 | `test_ocimf_meg4_scope_narrow` | Diff of `ocimf-meg4.md` vs `origin/main` has ≤ **10 lines added** (bound: `N_MAX_ADDED_LINES = 10` — chosen to accommodate a "## Related Standards" header + ≤ 2-item bullet list + one inbound-link sentence; if implementation needs more, that is a scope-creep signal and the plan must be revised), **0 lines removed**, and every added line either (a) sits within a newly-added `## Related Standards` section, or (b) contains the literal string `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]`. | pytest (parses `git diff --unified=0 origin/main -- knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`) | PASS post-Branch A | Branch A |
| T8 | `test_engineering_index_has_tandem_row` | `knowledge/wikis/engineering/wiki/index.md` contains a row with `ocimf-tandem-mooring.md` under Standards section | pytest (regex match in Standards table) | PASS post-Branch A | Branch A |
| T9 | `test_engineering_log_has_promotion_entry` | `knowledge/wikis/engineering/wiki/log.md` contains a `## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)` entry | pytest | PASS post-Branch A | Branch A |
| T10 | `test_no_out_of_scope_pages` | Among **newly-ADDED files only** (use `git diff --name-only --diff-filter=A origin/main..HEAD`), there must be exactly one under `knowledge/wikis/engineering/wiki/standards/` (namely `ocimf-tandem-mooring.md`) and zero anywhere under `knowledge/wikis/marine-engineering/wiki/standards/` or any other wiki's `wiki/standards/` subtree. Newly-added test files under `tests/knowledge/` are explicitly allowed. Modified (not added) files are not counted against this test. | pytest (subprocess to `git diff --name-only --diff-filter=A origin/main..HEAD`) | PASS post-Branch A | Branch A |
| T11 | `test_llm_wiki_lint_engineering_clean` | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 OR only with `warning`/`info` severity | subprocess from pytest | PASS post-Branch A | Branch A |
| T12 | `test_content_has_discriminating_technical_evidence` | OCIMF-Tandem page body (excluding frontmatter + provenance block) is > 200 words AND contains at least **2 of the following discriminating evidence categories**, each independently verifiable against the source ledger entry (not the title): (a) a specific OCIMF clause/section reference in the form `\b[0-9]+(?:\.[0-9]+){1,3}\b` (e.g., `3.2.1`, `4.5`); (b) at least one explicit numeric engineering quantity with SI/imperial unit token (regex: `\b\d+(\.\d+)?\s*(kN|t|m|ft|deg|°|kts|knots|MT|bar|kPa|MPa)\b`); (c) a named specific mooring/hawser/fender configuration or equipment identifier (e.g., `12-point spread`, `submarine hoses`, `Yokohama fender`, `quick-release hook`, `chafe chain`) matched by a curated regex list committed in the test fixture. The previously-proposed trivial terms (`tandem`, `FPSO`, `offloading`, `conventional tanker`, `berthing`) are **excluded from the evidence list** because all appear in the document title and would trivially satisfy a regurgitated body. Rationale documented inline in the test fixture. | pytest | PASS post-Branch A — guards against "empty summary" title regurgitation | Branch A |
| T13 | `test_ocimf_tandem_has_inbound_link` | At least one existing engineering-wiki page (concept, entity, source, or the `ocimf-meg4.md` standards page) contains a markdown link `[[ocimf-tandem-mooring]]` OR `](standards/ocimf-tandem-mooring.md)` OR `](/knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md)`. Hardens the "no orphan promotion" requirement that `llm_wiki.py lint` does not enforce for `standards/` (lint at line 748 only traverses `entities/concepts/sources/comparisons`). | pytest (recursive grep under `knowledge/wikis/engineering/wiki/`) | PASS post-Branch A | Branch A |

**TDD discipline:** Tests T1–T13 are written first on a feature branch; implementation proceeds only to make them pass. T1 is the entry gate — it MUST pass before any other implementation occurs. T12 and T13 together close the "grounding-by-title" failure mode (T12 keeps body content non-regurgitative against the document title; T13 asserts at least one inbound link exists since the lint check skips `standards/`).

---

## Acceptance Criteria

### Cross-branch
- [ ] Adversarial reviews from at least 2 providers captured for v3; any residual MAJOR finding blocks `status:plan-approved`.
- [ ] `tests/knowledge/test_ocimf_tandem_promotion.py` committed with T1–T13 implemented.
- [ ] Prereq matrix in this plan reflects actual `gh issue view` state at execution time (including #2471 codification landed-on-main status).

### Branch A (CONTENT_SUB_GATE == PASS) — engineering wiki
- [ ] T1 passes before any wiki write.
- [ ] T3–T11 all pass after implementation.
- [ ] T12 passes (discriminating-evidence content guard, not title regurgitation).
- [ ] T13 passes (at least one inbound link exists).
- [ ] `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 or warning-only.
- [ ] Parent issue #2216 receives an implementation summary comment.
- [ ] No CSA pages created in this issue.

### Branch B (CONTENT_SUB_GATE == FAIL — current state)
- [ ] T1 fails as expected; blocker comment posted on #2227 explaining the content gap with evidence from `acma-wiki-unblock-2245-handoff.yaml` plus the three summary JSON previews (empty for OCIMF, corrupted-OCR for CSA x2).
- [ ] Marine-wiki taxonomy decision follow-up issue opened (or existing one linked — note #2471 already tracks the page-type sanction; only per-code wiki routing remains open for CSA).
- [ ] Content remediation follow-up issue opened (or existing one linked). **Scope per target:** for OCIMF `5e5f…` → "extract preview content (currently empty)"; for CSA `b576…` + `3aa1…` → "**fix encoding/OCR corruption** on existing 1000-char previews" (NOT "re-extract from empty state" — r2 correction).
- [ ] No wiki files written.

---

## Adversarial Review History

### v1 (2026-04-12, reviewed 2026-04-21)
- **Codex (2026-04-21):** MAJOR — (1) internal contradiction: Scope Boundaries says stop-if-marine-conventions-fail but Artifact Map/Files-to-Change/Acceptance hardcode CSA creation in `marine-engineering/wiki/standards/`; (2) TDD contract missing — "verification list" is a conceptual checklist, not executable tests with runners/commands/harness names; (3) prereq matrix underspecified — plan self-declares `FAIL for execution readiness` but still framed as implementation plan.
- **Gemini (2026-04-21):** APPROVE — noted self-flagged FAIL state but approved on scope; weak review (outranked by Codex MAJOR per issue-planning-mode skill rule).
- **Claude (2026-04-15 overnight):** needs-revision minor — confirmed gitignore + taxonomy blockers.
- **Governance action (2026-04-21 15:07 UTC):** Path C rollback `status:plan-approved` → `status:plan-review`.

### v2 (2026-04-21) — this revision addresses Codex MAJORs as follows

1. **Contradiction resolved:** Plan is now explicitly branch-conditional. Branch A writes ONLY to `knowledge/wikis/engineering/wiki/standards/` (the git-tracked, schema-sanctioned path). CSA pages are explicitly deferred out of this issue until a separate marine-wiki taxonomy/gitignore decision lands. No deliverable is simultaneously "must exist" and "only if conventions allow".
2. **TDD contract concretized:** §TDD Test List names 12 concrete tests (T1–T12), the file they live in (`tests/knowledge/test_ocimf_tandem_promotion.py`), the exact runner commands (`uv run pytest …` + `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering`), and what assertion each makes. T1 (content sub-gate) and T2 (taxonomy sub-gate) operationalize the branch decision.
3. **Prereq matrix pinned:** §Prerequisite Matrix cites current `gh issue view` state (#2225 CLOSED 2026-04-11, #2245 CLOSED 2026-04-13 with `ready_for_2227: false`, #2207 CLOSED, #2216 OPEN plan-review), exact summary artifact paths by sha256 doc_key, and specific blocker evidence. Each row classifies blocker/non-blocker.

### v2 residual open questions (for v2 reviewers)
- Should the marine-wiki taxonomy decision be made inside this issue (widening scope) or as a split follow-up? Current plan: split follow-up to keep #2227 bounded.
- Is T12's 200-word threshold well-chosen, or should it be data-driven from comparable existing standards pages? Current plan: adjust to median-length of existing engineering/standards pages if v2 review prefers.

### v3 (2026-04-23) — this revision addresses r2 Codex+Claude+Gemini findings

**NEW defects from r2 — all addressed in this v3:**

1. **T2 taxonomy sub-gate false-PASS (Claude r2 F2) — FIXED.** v2 T2 wording invited a bare substring/regex match on `standards/` which would false-PASS against `raw/standards/` line 11 of marine CLAUDE.md. v3 T2 now specifies: parse the code-fenced Directory Structure block, extract ONLY the `wiki/` subtree (excluding `raw/`), assert regex `^\s*standards/` matches a line within that extracted block. Gitignore check is now exact-line match via `splitlines()`, not substring. Same path-anchored approach applied to Pseudocode (line-anchored parse of the `wiki/` block; exact-line gitignore check).

2. **§Resource Intelligence line 19 `text_preview: ""` misstatement (Claude r2 F1) — FIXED.** v3 Resource Intelligence now records the actual preview state: OCIMF `5e5f…` text_preview length 0 (truly empty); CSA `b576…` and `3aa1…` each have 1000-char corrupted-OCR previews (first 200 chars quoted inline for each). Branch B follow-up is rescoped: OCIMF → "extract preview content"; CSA x2 → "fix encoding/OCR corruption" (not "re-extract from empty").

3. **T12 word list trivially satisfied by title (Claude r2 F5) — FIXED.** v3 T12 drops all five title-matching terms (`tandem`, `FPSO`, `offloading`, `conventional tanker`, `berthing`). Replaced with three evidence categories, each independently verifiable against the source (not the title): OCIMF clause references (regex `\b[0-9]+(?:\.[0-9]+){1,3}\b`), named engineering quantities with units (regex for SI/imperial units), and specific mooring/hawser/fender configuration identifiers (curated regex list committed in test fixture). Requires 2-of-3 categories present.

**SUSTAINED defects from r1 — now addressed (Lane C r2 flagged as still-open from 2026-04-21):**

4. **T7 undefined `N` — FIXED.** v3 T7 binds `N_MAX_ADDED_LINES = 10`, with explicit rationale (one header + ≤ 2-item bullet list + one inbound-link sentence) and a rule that exceeding this is a scope-creep signal requiring plan revision. Diff is now explicit: `git diff --unified=0 origin/main -- …/ocimf-meg4.md`.

5. **T10 missing `--diff-filter=A` — FIXED.** v3 T10 now uses `git diff --name-only --diff-filter=A origin/main..HEAD` and scopes the check to newly-ADDED files under any wiki's `wiki/standards/` subtree; modified files (index, log) are explicitly excluded.

6. **Gitignore citations off-by-one — FIXED.** v2 cited `.gitignore:491-492`; actual is `.gitignore:492-494` (`/knowledge/wikis/*` at 492, `!/knowledge/wikis/engineering/` at 493, `!/knowledge/wikis/cross-links.md` at 494). v3 Prereq Matrix row and Resource Intelligence now cite 492-494 with all three exact lines quoted.

**NEW v3 additions (prompted by Claude r2 F6, F7, F8, F10):**

7. **Pseudocode "load prereq matrix" operationalized (Claude r2 F8):** v3 pseudocode replaces "load prereq matrix" with concrete file-load pseudo-calls (`yaml.load(handoff.yaml)`, `json.load(…/summaries/sha256:…json)` x3), removing the implementer-choice ambiguity.

8. **#2471 codification-landed sub-check added (v3 structural):** Prereq Matrix gains explicit row for #2471 codification status (in-flight vs landed on origin/main). Pseudocode adds `CODIFICATION_LANDED = git.merge_base_ancestor(...)` check. MARINE_TAXONOMY_SUB_GATE = PASS now requires all three: schema OK AND gitignore OK AND codification landed. Cites user DECISION (stable) separately from in-flight codification.

9. **Branch A acceptance unreachability framing (Claude r2 F7):** v3 Scope Boundaries and Prereq Matrix classification rule are explicit that under current evidence, content sub-gate fails for all three targets → Branch B is the only executable path today. Branch A can proceed for OCIMF independently once its preview extraction lands, without waiting for CSA remediation or #2471 codification.

10. **Lint gate weakness mitigated with T13 (Claude r2 F10):** v3 adds T13 `test_ocimf_tandem_has_inbound_link` — explicit assertion that at least one page in the engineering wiki links back to the new standards page, closing the "orphan under `standards/` passes lint" gap that Claude r2 flagged.

11. **Engineering index `## Standards` section exists (Claude r2 F6):** confirmed at `knowledge/wikis/engineering/wiki/index.md:99` (`## Standards (7 pages)`). v3 Risks section removes the deferred-verification bullet; implementation inserts a row, no section creation needed.

### v3 residual open questions (for v3 reviewers)
- If #2471 codification v2 (Lane G) chooses a `wiki/standards/` routing for CSA that differs from marine-engineering (e.g., routes CSA to naval-architecture instead), this plan's Prereq Matrix CSA row needs a one-line amendment but no structural change — the Branch-B deferral keeps #2227 agnostic to per-code routing.
- T12's 2-of-3 evidence-category threshold is a design choice; if v3 reviewers prefer 3-of-3, swap the conjunction. Either choice is stronger than the v2 title-satisfying list.

---

## Risks and Open Questions

- **Risk (surfaced by Branch B reality):** even the OCIMF Tandem page (engineering wiki, sanctioned path) may have limited body content because the summary artifact has `summary=""`. T12 guards against a near-empty promotion. If T12 cannot pass with current summary content, Branch A is ALSO effectively blocked — revealing that #2245 is a harder blocker than originally scoped.
- **Verified (not a risk):** engineering wiki `index.md` has a `## Standards (7 pages)` section at line 99; Branch A inserts a row under it (no section creation needed).
- **Risk:** `llm_wiki.py lint` orphan/link checks skip `standards/` — a tandem page with no inbound link from any entity/concept page would not trip as orphan. Cross-link discipline is a soft gate, not lint-enforced.
- **Open:** If T12 fails because summary content is too thin, do we still land the page (as a stub with a `status: stub` frontmatter tag and a follow-up issue) or block entirely? Current plan: block and defer — stubs violate the grounding contract.
- **Open:** Should #2227 adopt the metadata-only convention from #2260 as a fallback rather than blocking? That is a user decision; this plan keeps the grounded scope and defers metadata-only scope to #2260's tree.

---

## Complexity: T2

**T2** — multi-file wiki/documentation promotion with bounded evidence-driven content creation, index/log updates in a single wiki domain (engineering), new test file, and strict scope control against adjacent breadth. Branch-conditional execution adds mild complexity but keeps scope bounded.
