# Plan — workspace-hub#2542: Doris University training corpus, bounded extraction

> **Status:** plan-review (NOT plan-approved)
> **Author:** Terminal 2 of overnight Elements wave 2026-04-28 (Claude planning-only)
> **Issue:** [#2542](https://github.com/vamseeachanta/workspace-hub/issues/2542)
> **Umbrella:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540)
> **Upstream done:** #2526 (ingest), #2534 (retention gate), #2535 (metadata index), #2536 (first-pass extraction)
> **Tense convention:** Future tense for all proposed work. No artifact in this plan is built yet.

## 1. Scope

### 1.1 In scope

This plan will define a **bounded first-tranche extraction** of the Doris University training corpus into the `engineering` LLM-wiki, using only Doris-authored artifacts that carry no third-party IP or licensed-standard text.

The first tranche will cover 18 artifacts grouped as:
- 8 canonical curriculum decks (Modules 1.00, 1.01, 1.02, 1.03 — current versions only)
- 4 Doris-authored embedded calculations (`Embedded Charts/`)
- 5 Doris-authored Lunch and Learn PDFs (`ADMIN-FORM-02 - * Lunch and Learn ...`)
- 1 syllabus snapshot for taxonomy validation

Each artifact will be converted to wiki text content (slide text + speaker notes for .pptx; text-layer extract for .pdf; structured table extract for .xls/.xlsx). Embedded vendor figures will not be copied into git/wiki raw folders; they will remain metadata-referenced from the source pages.

For each Doris-authored calculation that references a published standard (API 17E, API 17G, etc.), this plan will require the corresponding `wiki/standards/<code-id>.md` page to exist with #2471 frontmatter (`code_id`, `publisher`, `revision`) **before** the calc's wiki concept page is emitted. This satisfies the calc-output citation contract (`.claude/rules/calc-citation-contract.md`) and the #2481 fail-closed rule.

### 1.2 Out of scope

- Extraction of any vendor-derivative reference PDF under `*/References/` (API, ISO, IEC, BS EN, FMC, Duco, OTC papers, Subsea Engineering Handbook). Routing for these is **citation-only** via `wiki/standards/<code-id>.md`, not source extraction. (#2482 deny-list)
- Extraction of the client-IP training packs in `DE Presentations/{SONANGOL,ENI,DSME,Operator}/`, `ENI Training/` (root), `Stat Presentations/`, `draft presentations/Operator Training/`. These will be deferred to a separate IP-screening child issue.
- Extraction of project-residue decks (`FieldLayout/`, `FreeSpan/`, `Flexible Pipe/`).
- Extraction of training media (`*.vob`, `*.ifo`, `*.bup`, `*.mp4`, `*.bmp`, `*.db`).
- Cleanup, deletion, or release of any source data. Retention remains gated by #2534 until 2026-05-28.
- Any modification of `/mnt/ace/`.
- Self-approval. The user-in-loop gate is load-bearing per `.claude/memory/topics/feedback_never_offer_to_self_label_plan_approved.md`.

### 1.3 Non-goals (explicit)

- Will **not** copy any raw bulk file into git or wiki raw folders.
- Will **not** mutate the existing `wiki/sources/elements-doris-university.md` catalog page beyond adding cross-references.
- Will **not** create the entire `wiki/standards/` substrate; only the standards pages strictly needed by the four calc artifacts in tranche 1.

## 2. Resource intelligence

### 2.1 Source of record

| Asset | Path | Notes |
|---|---|---|
| Raw corpus | `/mnt/ace/doris/training` | Read-only; source-of-record per #2526 ingest |
| Retained staging | `/mnt/ace/doris/training/_from_elements/` | Provenance, do not delete (#2534) |
| Existing metadata page | `knowledge/wikis/engineering/wiki/sources/elements-doris-university.md` | Created by #2535 batch-ingest 2026-04-28 19:24 UTC |
| Candidate TSV | `.planning/intel/elements-to-llm-wiki/deep-extraction-candidates.tsv` | 322 doris-university rows |
| Domain summary | `.planning/intel/elements-to-llm-wiki/elements-wiki-domain-summary.md` | 564 files, 11.06 GB |
| Wiki schema | `knowledge/wikis/engineering/SCHEMA.md` | source → entity/concept → index → log |
| Wiki source classes | `knowledge/wikis/engineering/SOURCE_INVENTORY.md` | This corpus is a new Class 9 (Elements ingest) |

### 2.2 Tooling already present

| Tool | Path | Use |
|---|---|---|
| LLM wiki CLI | `scripts/knowledge/llm_wiki.py` | `ingest`, `batch-ingest`, `status`, `lint` |
| Citation schema | `digitalmodel/src/digitalmodel/citations/schema.py` | Calc-citation pilot per #2481 |
| Calc-citation rule | `.claude/rules/calc-citation-contract.md` | Mandatory for calc concept pages |
| Frontmatter contract | #2471 (referenced by `wiki/standards/<code-id>.md`) | `code_id`, `publisher`, `revision` |

### 2.3 Adjacent intel

| Artifact | Path | Why relevant |
|---|---|---|
| Taxonomy | `.planning/intel/elements-overnight-wave/doris-university-taxonomy.md` | Group A–K classification of 564 files; this plan's reasoning basis |
| First-tranche TSV | `.planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv` | The 18 artifacts this plan will extract |
| #2536 deep-extraction report | `.planning/intel/elements-deep-extraction/elements-deep-extraction-report.md` | Tooling pattern to follow (per master-plan.md) |

### 2.4 Anti-references (do NOT pull from)

- `knowledge/wikis/*/wiki/sources/` for vendor-derivative content — denied per #2482.
- The `draft presentations/` subtree for any of the canonical decks — those are working duplicates; canonical sibling at root takes precedence.

## 3. Artifact map

### 3.1 New planning artifacts (this plan; already written by Terminal 2)

| Path | Purpose |
|---|---|
| `.planning/intel/elements-overnight-wave/doris-university-taxonomy.md` | Taxonomy of all 564 files into Groups A–K with routing decisions |
| `.planning/intel/elements-overnight-wave/doris-university-first-tranche.tsv` | 18-row tranche-1 extraction list (priority/topic/content_kind/bytes/path/rationale/method/target/risk) |
| `docs/plans/2026-04-28-issue-2542-elements-doris-university-training-plan.md` | This plan |
| `docs/plans/overnight-prompts/2026-04-28-elements-wave/results/terminal-2-doris-university.md` | Terminal-2 result summary |

### 3.2 Wiki pages this plan will create when executed (NOT yet created)

Planned source pages under `knowledge/wikis/engineering/wiki/sources/`:

| Page | Backed by tranche-1 row(s) |
|---|---|
| `doris-university-module-1-00-subsea-production-systems-overview.md` | Row 1 |
| `doris-university-module-1-01-production-control-systems.md` | Rows 2, 3 |
| `doris-university-module-1-02-umbilical-systems.md` | Rows 4, 5, 6 |
| `doris-university-module-1-03-installation-workover-control.md` | Rows 7, 8 |
| `doris-university-lunch-and-learn-control-systems.md` | Rows 13, 14 |
| `doris-university-lunch-and-learn-umbilical-systems.md` | Rows 15, 16, 17 |
| `doris-university-syllabus-snapshot.md` | Row 18 |

Planned concept pages under `knowledge/wikis/engineering/wiki/concepts/`:

| Page | Backed by tranche-1 row(s) | Calc-citation needed |
|---|---|---|
| `subsea-production-system-overview.md` | Row 1 | No |
| `subsea-production-control-system.md` | Rows 2, 3 | No |
| `subsea-umbilical-system.md` | Rows 4, 5, 6 | No |
| `installation-workover-control-system.md` | Rows 7, 8 | No |
| `methanol-injection-analysis.md` | Row 9 | Yes — verify formula references; cite if standards-derived |
| `umbilical-tube-sizing-api-17e.md` | Row 10 | **Yes — API 17E required** |
| `hydrostatic-pressure-depth.md` | Row 11 | Conditional — cite if seawater density traced to standard |
| `subsea-accumulator-sizing.md` | Row 12 | **Yes — likely API 17G or API 16D** |

Planned standards pages under `knowledge/wikis/engineering/wiki/standards/` (only those required by tranche-1 calcs):

| Page | Trigger |
|---|---|
| `api-17e.md` | Required by `umbilical-tube-sizing-api-17e.md` (Row 10) |
| `api-17g.md` or `api-16d.md` | Conditional — required by `subsea-accumulator-sizing.md` (Row 12) once formula source is read |

Each standards page will carry #2471 frontmatter (`code_id`, `publisher`, `revision`) and serve only as the resolver target for `Citation` instances; the page body is **not** vendor-derivative content (which would violate #2482) — it is a publisher/revision/scope summary the citation resolver can match against.

Updates to the existing index/log per `SCHEMA.md`:

| File | Change |
|---|---|
| `wiki/index.md` | Append new pages to Sources + Concepts tables |
| `wiki/log.md` | Append `[2026-MM-DD] ingest \| Doris University tranche 1` block |
| `wiki/sources/elements-doris-university.md` | Append "Tranche 1 children" cross-link section |

### 3.3 Files this plan will NOT touch

- `docs/plans/README.md` (forbidden by Terminal 2 prompt)
- `scripts/**` (forbidden — extraction script changes belong in a separate issue if needed; #2536 already shipped a usable extractor)
- `.gitignore` (forbidden)
- Any Terminal 1/3/4 plan/result/intel paths
- Any pre-existing dirty provider scorecard/report files
- `/mnt/ace/**` (read-only)

## 4. Execution sequence (for the future approved phase, not this terminal)

1. **Pre-flight Hermes check**: `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'`. If any cleanup loop is active, work on a feature branch in a worktree per `feedback_hermes_active_preflight_check.md`.
2. **Dirty-tree guard**: refuse to start if working tree contains unstaged provider scorecard files; require a clean checkpoint.
3. **Module enumeration audit**: scan the candidate TSV for any `1\.0[4-9]` paths missed by the top-by-size cut. Update tranche-1 if a Module 1.04 canonical deck exists. (Risk #1 in taxonomy.)
4. **Hash-verify duplicates**: for each tranche-1 path, sha256 against the matching `draft presentations/...` sibling. If identical, log the duplicate; if different, keep both candidates and ask for adversarial review.
5. **Standards-page precondition**: for Rows 10 and 12, create `wiki/standards/api-17e.md` (and `api-17g.md` or `api-16d.md` if confirmed) with #2471 frontmatter **before** the corresponding concept page is emitted. Fail-closed: if the standards page cannot be created (publisher/revision unknown), skip the calc concept page and log a follow-up.
6. **Per-row extraction loop** (one row at a time, atomic commit per row):
    a. Probe content (text-layer presence for .pdf; OCR fallback only on probe-failure).
    b. Convert (libreoffice for .pptx/.doc; pdftotext for .pdf; openpyxl for .xls/.xlsx).
    c. Build source page in `wiki/sources/...` with frontmatter per `SCHEMA.md`.
    d. Build/extend concept page in `wiki/concepts/...` (multiple rows may share a concept page).
    e. For calc rows: emit `Citation` instance, validate against the standards page; raise `CitationResolutionError` with `code_id` if resolution fails (per #2481 D2).
    f. Update `wiki/index.md` and `wiki/log.md`.
    g. `git add` only the new wiki pages + index + log; commit with `feat(llm-wiki): doris-university tranche-1 row N` message; push.
7. **Post-extraction lint**: `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering`. Fix orphans/broken refs before opening a PR.
8. **Comment summary on #2542** with row-by-row results (extracted / skipped / blocked) and a recommendation for tranche-2 scope.

This sequence is the **planned execution shape**, not work to be done by Terminal 2.

## 5. TDD / validation strategy

Per `superpowers:test-driven-development` and the wiki SCHEMA, the executing phase will write tests **before** any extractor change is committed. For tranche 1 the existing `scripts/knowledge/llm_wiki.py` is sufficient, so no new code is required and TDD applies to the **post-conditions** rather than to a new module:

| Validation | Tool | Pass criterion |
|---|---|---|
| Source page exists for each tranche-1 group | `find knowledge/wikis/engineering/wiki/sources/ -name 'doris-university-*.md'` | All 7 source pages present |
| Concept page exists for each backed concept | `find knowledge/wikis/engineering/wiki/concepts/ -name '<slug>.md'` | All 8 concept pages present |
| Standards-page precondition holds for calc rows | grep `code_id` in `wiki/standards/api-17e.md` (and any other emitted standards page) | Frontmatter parses, `code_id`/`publisher`/`revision` non-empty |
| Citation resolves at calc time | Pilot resolver `digitalmodel/src/digitalmodel/citations/schema.py` | `CitationResolutionError` not raised for any tranche-1 calc |
| Wiki index updated | grep new page paths in `wiki/index.md` | Each new page listed with summary + last_updated |
| Log entry appended | grep `[2026-MM-DD] ingest \| Doris University tranche 1` in `wiki/log.md` | Single log block present |
| No raw bulk in git | `git ls-files knowledge/wikis/engineering/raw/` | No new files added |
| No cross-terminal write | `git diff --name-only` against allowed-write list | Empty intersection with Terminal 1/3/4 paths |
| Lint clean | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` | Exit 0, zero orphan/broken-ref findings on new pages |

Verification before close per `superpowers:verification-before-completion`: each row's commit message must cite the row number; the closing comment on #2542 must list the 9-row table above with PASS/FAIL/SKIP, not assertions of success.

## 6. Acceptance criteria

Mirroring the issue body:

- [x] **Taxonomy groups training artifacts into coherent engineering/training themes** — written to `.planning/intel/elements-overnight-wave/doris-university-taxonomy.md` (Groups A–K).
- [x] **Proposed tranche is bounded to ≤25 artifacts** — 18 artifacts in `doris-university-first-tranche.tsv`.
- [x] **Plan separates reusable training knowledge from project/client-specific content** — Group A/B/C in tranche, Group F (client packs) and Group G (project residue) explicitly held.
- [x] **Raw-data policy and #2534 retention boundary are explicit** — Section 1.2, Section 4 step 1.
- [x] **Issue is left at plan-review, not self-approved** — see Section 8.

The first three criteria are met by Terminal 2's planning artifacts. The last two are met by this plan's structure and Section 8.

For the **future executing phase** (not Terminal 2), additional acceptance criteria:

- [ ] All 18 tranche-1 rows extracted or each non-extraction has a recorded reason in the comment.
- [ ] Wiki lint exits 0 on the new pages.
- [ ] Each calc concept page resolves its Citation against an existing `wiki/standards/<code-id>.md`.
- [ ] No raw bulk files added to `knowledge/wikis/engineering/raw/`.

## 7. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Module 1.04+ exists but is missed by top-by-size cut | Medium | Tranche 1 incomplete | Section 4 step 3 enumerates all `1\.0[0-9]` paths from TSV before extraction |
| 2 | `draft presentations/` siblings differ from canonical (not just byte-identical duplicates) | Medium | Conflicting wiki entries | Section 4 step 4 sha256 verification |
| 3 | Standards page `wiki/standards/api-17e.md` missing | High (does not exist today) | Calc concept page cannot emit (fail-closed per #2481 D2) | Section 4 step 5 creates the standards page first |
| 4 | Vendor-derivative content accidentally extracted from a `References/` subfolder | Low (tranche TSV is curated) | #2482 deny-list violation | Tranche TSV is exhaustive; extractor must reject any path matching `*/References/*` |
| 5 | Client-IP leakage from a deck mistakenly classified as Group A | Low (tranche TSV reviewed manually) | IP/legal exposure | Tranche TSV restricted to `1.0?` and `ADMIN-FORM-02` paths and one `Superceeded/` syllabus |
| 6 | Hermes cleanup loop or another agent commits to `main` mid-extraction | Medium (recurring per memory) | Lost work, mislabeled commits | Section 4 step 1 preflight; if Hermes active, work on feature branch in worktree |
| 7 | Embedded figures inflate git size if extracted to `wiki/raw/` | Medium | Crosses the "no raw bulk" line | Plan extracts text + speaker notes only; figures stay metadata-referenced |
| 8 | OCR triggered on a large .pdf inflates extraction time and cost | Low | Token/budget overrun | Probe-then-OCR pattern; OCR budget cap per row |
| 9 | A row's commit pushes during a parallel-agent push, races on git lock | Low–Medium | `[rejected]` push, retry confusion | Per-row commit serialization; reflog as ground truth per `feedback_reflog_as_ground_truth.md`; auto-sync may resolve silently per `feedback_autosync_silent_pusher.md` |

## 8. Approval boundary

This plan is **plan-review**, not plan-approved. Self-approval is forbidden by `feedback_never_offer_to_self_label_plan_approved.md` and by the issue-planning workflow gate.

Next action belongs to a human reviewer:

1. Read this plan, the taxonomy, and the tranche TSV.
2. Run adversarial review (recommended: cross-provider, given recent payoff per `feedback_cross_provider_review_payoff.md`; with the codex-cli 0.124.0 stdin-hang regression unresolved per `feedback_codex_cli_0_124_upstream_regression.md`, prefer Claude internal r3 fallback or downgrade to codex-cli 0.123.0 first).
3. Either label `status:plan-approved` (which authorizes the executing phase to begin) or comment requested changes and keep the issue at `status:plan-review`.

Terminal 2 will not add either label.

## 9. References

- Issue: workspace-hub#2542
- Umbrella: workspace-hub#2540
- Upstream: #2526 (ingest), #2534 (retention), #2535 (metadata index), #2536 (first-pass extraction)
- Calc-citation contract: `.claude/rules/calc-citation-contract.md`
- Citation schema pilot: `digitalmodel/src/digitalmodel/citations/schema.py`
- Wiki schema: `knowledge/wikis/engineering/SCHEMA.md`
- Wiki source classes: `knowledge/wikis/engineering/SOURCE_INVENTORY.md`
- Existing source page (#2535): `knowledge/wikis/engineering/wiki/sources/elements-doris-university.md`
- Vendor-derivative deny-list: vamseeachanta/aceengineer-strategy#15 governance tracker (referenced from #2482)
- LLM-wiki CLI: `scripts/knowledge/llm_wiki.py`

## Adversarial Review Resolution Addendum (2026-04-29)

This addendum is authoritative over earlier pseudocode if there is any conflict.

### TDD is test-first, not post-condition-only
- Implementation must begin by adding failing validation tests/checks for page schema, source path allowlists, extraction allowlists, no raw assets, no unresolved standards citations, and no copied full-text training material.
- Post-generation checks alone are insufficient and must not be treated as TDD compliance.

### Metadata-first curated extraction
- Replace any broad instruction that each artifact will be converted to full wiki text content.
- Tranche-1 output is metadata-first plus curated, authored summaries only.
- Per-artifact IP screening is required before any slide text, speaker notes, calculation text, figures, or standard-derived excerpts are summarized.
- Default prohibited: full deck text, copied figures, standard excerpts/clauses, screenshots, and OCR-derived text.

### Standards namespace and citation resolver
- Standards pages must target `knowledge/wikis/engineering-standards/wiki/standards/` as the canonical namespace, not `knowledge/wikis/engineering/wiki/standards/`.
- Engineering/training concept pages may cross-link to engineering-standards pages.
- A standards stub may only be created from public publisher metadata with revision/source/date fields; if revision metadata is unknown, fail closed and leave an unresolved citation note.

### OCR out of scope for tranche 1
- OCR fallback is explicitly out of scope for this tranche unless separately approved per artifact.
- Text-layer failures should result in metadata-only treatment, not OCR.

