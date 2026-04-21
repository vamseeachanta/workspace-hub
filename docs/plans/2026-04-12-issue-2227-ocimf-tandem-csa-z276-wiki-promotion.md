# Plan for #2227: Promote OCIMF Tandem Mooring and CSA Z276 Coverage into LLM-Wikis

> **Status:** plan-review (v2)
> **Complexity:** T2
> **Date:** 2026-04-12 (v1) / 2026-04-21 (v2 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2227
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** `scripts/review/results/2026-04-21-plan-2227-codex.md` (MAJOR) | `scripts/review/results/2026-04-21-plan-2227-gemini.md` (APPROVE) | `scripts/review/results/2026-04-21-plan-2227-claude-rev-2.md` (v2 self-review)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — existing OCIMF MEG4 page, git-tracked (confirmed via `git ls-files`).
- Found: `knowledge/wikis/engineering/wiki/standards/` — directory exists and is git-tracked, containing `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md`.
- Found: `knowledge/wikis/marine-engineering/wiki/` — directory is gitignored (`.gitignore:491 /knowledge/wikis/*` with only `engineering/` exempted at line 492). Subdirs present: `comparisons/`, `concepts/`, `entities/`, `sources/`, `visualizations/`. NO `standards/` directory, and marine-engineering `CLAUDE.md` schema (lines 8-23) does not list `standards/` as a sanctioned category.
- Found: `scripts/knowledge/llm_wiki.py` — lint command at `cmd_lint` (line 683) validates frontmatter for `entities/concepts/sources/comparisons/standards/workflows` (line 632). Supports `standards/` in frontmatter check but orphan/link checks only traverse `entities/concepts/sources/comparisons` (line 748).
- Found: `data/document-index/summaries/sha256:5e5f...json`, `...:b576...json`, `...:3aa1...json` — summary artifacts EXIST for all three target doc_keys, but with `summary: ""` and `text_preview: ""` (content empty due to the DRM/extraction blocker logged in #2245 handoff).

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
- Reusable summaries for all three target doc_keys are empty-content today; ledger + summary files exist (schema-satisfied) but content field is `""`. The reuse contract (#2207) is not literal about "non-empty" but the promotion spirit requires evidence beyond title.
- `knowledge/wikis/marine-engineering/` is gitignored — promoting CSA pages there would be non-durable without an explicit `.gitignore` exemption or an alternative canonical location.
- Marine-engineering `CLAUDE.md` schema does not list `wiki/standards/` as a sanctioned directory; creating one silently broadens schema.
- `llm_wiki.py lint` orphan/link checks do not traverse `standards/` — if the plan relies on lint as a TDD gate, that coverage must be verified explicitly.
- No integration test exists that asserts standards-page presence/frontmatter for a given doc_key; the TDD gate must add or extend one.

<!-- Verification: distinct sources consulted = 15+ (3 ledger entries + 3 summary JSON files + 2 gitignore lines + 2 wiki CLAUDE.md files + 4 prior plans + 1 handoff yaml + 3 review artifacts + 1 issue thread + llm_wiki.py lint source). -->

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
- Post blocker comment summarizing the content gap on #2227.
- Open or reuse a marine-wiki taxonomy decision follow-up (does `wiki/standards/` get sanctioned in marine-engineering `CLAUDE.md`, or does CSA content land somewhere else — e.g., `sources/` or a new `codes/` category — or does marine get a `.gitignore` exemption like engineering?).
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
| #2245 (summary artifacts) | CLOSED 2026-04-13, handoff `ready_for_2227: false` | **Content sub-gate: BLOCKING** — summary JSON files exist but `summary=""` | `docs/reports/acma-wiki-unblock-2245-handoff.yaml` |
| marine-wiki `wiki/standards/` taxonomy | undecided; schema + gitignore both reject | **Taxonomy sub-gate: BLOCKING for CSA pages** | `knowledge/wikis/marine-engineering/CLAUDE.md`, `.gitignore:491-492` |
| marine-wiki gitignore | `/knowledge/wikis/*` ignored; only `engineering/` exempted | **BLOCKING for CSA pages** unless pattern amended | `.gitignore:491-492` |

**Classification rule:** OCIMF Tandem page (engineering wiki, git-tracked, schema-sanctioned) needs only the content sub-gate. CSA pages need content + taxonomy + gitignore. Today all three CSA prereqs fail → Branch B.

---

## Pseudocode

```text
# Entry gate
load prereq matrix
if #2245 handoff.ready_for_2227 is False OR any summary_artifact.summary == "":
    set CONTENT_SUB_GATE = FAIL
else:
    set CONTENT_SUB_GATE = PASS

check marine-engineering CLAUDE.md for "standards/" in sanctioned categories
check .gitignore for explicit !knowledge/wikis/marine-engineering or equivalent
if both checks pass:
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
| T2 | `test_prereq_marine_taxonomy_sub_gate` | `marine-engineering/CLAUDE.md` lists `standards/` in sanctioned categories AND `.gitignore` has `!knowledge/wikis/marine-engineering/` (or equivalent) | pytest | currently FAILS → CSA pages deferred | CSA sub-branch |
| T3 | `test_ocimf_tandem_page_exists` | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists | pytest (`pathlib.exists()`) | PASS post-Branch A | Branch A |
| T4 | `test_ocimf_tandem_frontmatter_valid` | Page has `title`, `tags`, `added`, `last_updated`, `sources`, `domain=marine` frontmatter via existing `_parse_frontmatter` helper in `scripts/knowledge/llm_wiki.py` | pytest | PASS post-Branch A | Branch A |
| T5 | `test_ocimf_tandem_provenance_fields` | Page body contains `doc_key: sha256:5e5f...`, `source_ref` pointing to ledger entry, and `promoted_from: 2227` | pytest (regex match) | PASS post-Branch A | Branch A |
| T6 | `test_ocimf_tandem_cross_reference_to_meg4` | Page contains a `[[ocimf-meg4]]` or equivalent markdown link back to the MEG4 page | pytest | PASS post-Branch A | Branch A |
| T7 | `test_ocimf_meg4_scope_narrow` | Diff of `ocimf-meg4.md` has ≤ N lines added, no lines removed, and any additions mention `OCIMF-TANDEM-MOORING` | pytest (uses `git diff`) | PASS post-Branch A | Branch A |
| T8 | `test_engineering_index_has_tandem_row` | `knowledge/wikis/engineering/wiki/index.md` contains a row with `ocimf-tandem-mooring.md` under Standards section | pytest (regex match in Standards table) | PASS post-Branch A | Branch A |
| T9 | `test_engineering_log_has_promotion_entry` | `knowledge/wikis/engineering/wiki/log.md` contains a `## [YYYY-MM-DD] ingest | OCIMF-TANDEM-MOORING promotion (#2227)` entry | pytest | PASS post-Branch A | Branch A |
| T10 | `test_no_out_of_scope_pages` | No new files under `knowledge/wikis/engineering/wiki/standards/` or `marine-engineering/wiki/standards/` other than `ocimf-tandem-mooring.md` on the branch | pytest (git diff `--name-only`) | PASS post-Branch A | Branch A |
| T11 | `test_llm_wiki_lint_engineering_clean` | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 OR only with `warning`/`info` severity | subprocess from pytest | PASS post-Branch A | Branch A |
| T12 | `test_content_not_pure_title_regurgitation` | OCIMF-Tandem page body (excluding frontmatter + provenance block) is > 200 words AND contains at least 3 domain-specific terms from a curated list (tandem, FPSO, offloading, conventional tanker, berthing) | pytest | PASS post-Branch A — guards against "empty summary" regurgitation | Branch A |

**TDD discipline:** Tests T1–T12 are written first on a feature branch; implementation proceeds only to make them pass. T1 is the entry gate — it MUST pass before any other implementation occurs. T12 specifically guards against the null-content failure mode (the #2245 handoff revealed).

---

## Acceptance Criteria

### Cross-branch
- [ ] Adversarial reviews from at least 2 providers captured for v2; any residual MAJOR finding blocks `status:plan-approved`.
- [ ] `tests/knowledge/test_ocimf_tandem_promotion.py` committed with T1–T12 implemented.
- [ ] Prereq matrix in this plan reflects actual `gh issue view` state at execution time.

### Branch A (CONTENT_SUB_GATE == PASS) — engineering wiki
- [ ] T1 passes before any wiki write.
- [ ] T3–T11 all pass after implementation.
- [ ] T12 passes (content quality guard).
- [ ] `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 or warning-only.
- [ ] Parent issue #2216 receives an implementation summary comment.
- [ ] No CSA pages created in this issue.

### Branch B (CONTENT_SUB_GATE == FAIL — current state)
- [ ] T1 fails as expected; blocker comment posted on #2227 explaining the content gap with evidence from `acma-wiki-unblock-2245-handoff.yaml`.
- [ ] Marine-wiki taxonomy decision follow-up issue opened (or existing one linked).
- [ ] PDF re-extraction follow-up issue opened (or existing one linked).
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

---

## Risks and Open Questions

- **Risk (surfaced by Branch B reality):** even the OCIMF Tandem page (engineering wiki, sanctioned path) may have limited body content because the summary artifact has `summary=""`. T12 guards against a near-empty promotion. If T12 cannot pass with current summary content, Branch A is ALSO effectively blocked — revealing that #2245 is a harder blocker than originally scoped.
- **Risk:** engineering wiki `index.md` may not have a `## Standards` section currently (need to check before Branch A); if absent, the plan must also add the section header.
- **Risk:** `llm_wiki.py lint` orphan/link checks skip `standards/` — a tandem page with no inbound link from any entity/concept page would not trip as orphan. Cross-link discipline is a soft gate, not lint-enforced.
- **Open:** If T12 fails because summary content is too thin, do we still land the page (as a stub with a `status: stub` frontmatter tag and a follow-up issue) or block entirely? Current plan: block and defer — stubs violate the grounding contract.
- **Open:** Should #2227 adopt the metadata-only convention from #2260 as a fallback rather than blocking? That is a user decision; this plan keeps the grounded scope and defers metadata-only scope to #2260's tree.

---

## Complexity: T2

**T2** — multi-file wiki/documentation promotion with bounded evidence-driven content creation, index/log updates in a single wiki domain (engineering), new test file, and strict scope control against adjacent breadth. Branch-conditional execution adds mild complexity but keeps scope bounded.
