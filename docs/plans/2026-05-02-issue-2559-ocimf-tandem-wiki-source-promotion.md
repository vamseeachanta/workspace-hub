# Plan for #2559: Promote OCIMF Tandem Mooring preview into LLM-wiki source summary (closes #2227)

> **Status:** plan-review — r1 adversarial review pending
> **Complexity:** T2
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2559
> **Parent / closes:** https://github.com/vamseeachanta/workspace-hub/issues/2227 (Branch A contract)
> **Prerequisite (CLOSED):** https://github.com/vamseeachanta/workspace-hub/issues/2521 (OCR preview extraction)
> **Sibling (out of scope):** https://github.com/vamseeachanta/workspace-hub/issues/2522 (CSA Z276.1-20 + Z276.18)
> **Review artifacts:** `scripts/review/results/2026-05-02-plan-2559-claude.md` | `...-codex.md` | `...-gemini.md` (to be produced in r1 adversarial review)
> **origin/main tip at draft:** `b5500fb13`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `tests/knowledge/test_ocimf_tandem_promotion.py` (287 lines) — the v5 #2227 test contract from 2026-04-25; defines `evaluate_content_sub_gate(handoff, summary)` and 13 tests gated by `BRANCH_A_ONLY` skipif. Currently `2 passed, 11 skipped` against origin/main `b5500fb13` (verified 2026-05-02 via `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v`).
- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` (47 lines) — neighbor page; uses #2471 frontmatter (`code_id: OCIMF-MEG4`, `publisher: OCIMF`, `revision: 4th-Edition-2018`) and a `## Related Standards` table.
- Found: `knowledge/wikis/engineering/wiki/standards/` — git-tracked, schema-sanctioned per `knowledge/wikis/engineering/CLAUDE.md`; sibling pages: `api-579-ffs.md`, `dnv-os-e301.md`, `dnv-rp-c203.md`, `dnv-rp-c205.md`, `dnv-rp-f101.md`, `dnv-rp-f105.md`, `ocimf-meg4.md` (7 today; tandem makes 8).
- Found: `knowledge/wikis/engineering/wiki/index.md` — `## Standards (7 pages)` heading on line 101; the v5 test asserts `## Standards \(8 pages\)` (line 219 of test file), so the count must bump.
- Found: `knowledge/wikis/engineering/wiki/log.md` — append-only log; format `## [YYYY-MM-DD] operation | Title`.
- Found: `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md:60` and `knowledge/wikis/engineering/wiki/sources/mooring-failures-seed.md:34` — both already link to `ocimf-meg4.md`; either is a viable host for the inbound link the v5 test requires (`test_ocimf_tandem_has_inbound_link`).
- Found: `data/document-index/summaries/sha256:5e5f...json` — non-empty `summary` (528 chars, mentions tandem mooring config, hawser, chafe chain, fairlead, weak link) and non-empty `text_preview` (1.5KB, OCR of cover/copyright pages); `ready_for_2227: true` at the per-target level.
- Gap: No OCIMF Tandem wiki page exists at `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` (verified — `ls knowledge/wikis/engineering/wiki/standards/ocimf*` returns only `ocimf-meg4.md`).

### Standards

| Standard | Ledger status | doc_key (sha256) | Summary artifact | Per-target ready_for_2227 |
|---|---|---|---|---|
| `OCIMF-TANDEM-MOORING` | done | `sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af` | non-empty (528-char summary, 1.5KB text_preview) | **true** (handoff line 16) |
| `OCIMF-MEG4-2018` | done | (existing wiki page; narrow update only) | n/a | n/a |
| `CSA-Z276.1-20` | done | `sha256:b576...` | empty content | **OUT OF SCOPE** (→ #2522) |
| `CSA-Z276.18` | done | `sha256:3aa1...` | empty content | **OUT OF SCOPE** (→ #2522) |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — neighbor convention (frontmatter shape, `## Related Standards` table, cross-link list).
- `knowledge/wikis/engineering/wiki/index.md` — `## Standards (7 pages)` table format; needs 8-page bump and a tandem row.
- `knowledge/wikis/engineering/wiki/log.md` — promotion-log entry format.
- `knowledge/wikis/engineering/CLAUDE.md` — frontmatter schema (`title`, `tags`, `added`, `last_updated`, `sources`, `domain`, `cross_links`); #2471 fields (`code_id`, `publisher`, `revision`) demonstrated by `ocimf-meg4.md`.
- `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md` — candidate inbound-link host (already discusses MEG4/tandem-domain content).

### Documents consulted

- `gh issue view 2559` — issue body: bounded preview → wiki/source-summary; explicit out-of-scope CSA Z276 (→ #2522), raw PDF, full-text OCR, design claims beyond curated summary.
- `gh issue view 2227 --comments` (last comment, 2026-05-01): "Cross-review v5 — b77bdd038 — Claude APPROVE / Gemini APPROVE / Codex UNAVAILABLE (#2479)" — v5 plan was approved; the actual closure blocker is the gate-input data, not the plan or test contract.
- `gh issue view 2521` — CLOSED 2026-04-25 with `status:done`; produced the 528-char summary + 1.5KB text_preview that the OCIMF target now holds.
- `gh issue view 2522` — OPEN; body explicitly: "This issue does not block #2227 closure. #2227 closes only when OCIMF Phase 1 Branch A lands on origin/main."
- `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` (v5) — defines the Branch A contract this plan executes; this plan's deliverable surface (page + frontmatter + MEG4 cross-link + index bump + log entry + ≤10-line MEG4 update) is identical to v5 §Files-to-Change Branch A.
- `docs/reports/acma-wiki-unblock-2245-handoff.yaml` — gate-input file. Top-level `ready_for_2227: false`; per-target OCIMF entry `ready_for_2227: true`; CSA entries `ready_for_2227: false` with blocker explicitly noting "intentionally split to #2522".
- `.claude/rules/calc-citation-contract.md` — #2471 frontmatter contract (`code_id`, `publisher`, `revision` required for standards-derived constants); applies to standards-page frontmatter even when no calc consumer exists yet (forward-adopt).

### Gaps identified

- **The blocker** is a gate-read mismatch, not a content gap. The v5 test contract reads top-level `handoff["ready_for_2227"]` (line 49 of `test_ocimf_tandem_promotion.py`); the handoff sets that to `false` because two CSA targets hold it down — but those CSA targets were formally split to #2522 on 2026-04-23, **after** the v5 test was written on 2026-04-25. The handoff's per-target row for OCIMF reads `ready_for_2227: true` with a non-empty summary. The rollup semantics of the top-level flag changed without the file being updated.
- No OCIMF Tandem wiki page exists.
- No inbound link from any concept/entity/source page to the (yet-to-exist) tandem page.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2559` — OPEN — `feat(acma-codes): promote OCIMF Tandem preview into LLM-wiki source summary`
- `#2227` — OPEN, `status:plan-approved` — `feat(acma-codes): promote OCIMF Tandem Mooring and CSA Z276 coverage into LLM-wikis`
- `#2521` — CLOSED, `status:done` — `OCIMF-TANDEM-MOORING preview content extraction (unblocks #2227 Phase 1)`
- `#2522` — OPEN — `Phase 2: Promote CSA Z276.1-20 + Z276.18 into marine-engineering wiki/standards/`

**File existence** (verified 2026-05-02):
- EXISTS: `tests/knowledge/test_ocimf_tandem_promotion.py` (287 lines, gh-tracked)
- EXISTS: `docs/reports/acma-wiki-unblock-2245-handoff.yaml`
- EXISTS: `data/document-index/summaries/sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json` (non-empty `summary` and `text_preview`)
- EXISTS: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md`
- MISSING (this plan creates): `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`

**Live test state** (`uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v` 2026-05-02):
```
2 passed, 11 skipped in 0.34s
```
The 11 skips are `BRANCH_A_ONLY` skipif — they fire because `evaluate_content_sub_gate` returns False (top-level handoff flag is False). The 2 passes are `test_prereq_content_sub_gate_evaluation` (pure-function test of the gate predicate) and `test_branch_b_no_wiki_writes_when_gate_fails` (asserts no standards-page additions during Branch B).

**Gate-read excerpt** (`tests/knowledge/test_ocimf_tandem_promotion.py:42-52`):
```python
def evaluate_content_sub_gate(handoff: dict[str, Any], summary: dict[str, Any]) -> bool:
    """Return true only when the approved #2227 OCIMF content gate is satisfied."""
    if "ready_for_2227" not in handoff:
        raise AssertionError(f"{HANDOFF_PATH} is missing ready_for_2227")
    if "summary" not in summary or "text_preview" not in summary:
        raise AssertionError(f"{OCIMF_SUMMARY_PATH} is missing summary or text_preview")
    return (
        handoff["ready_for_2227"] is True
        and bool(str(summary["summary"]).strip())
        and bool(str(summary["text_preview"]).strip())
    )
```

**Handoff yaml top-level vs per-target** (`docs/reports/acma-wiki-unblock-2245-handoff.yaml:4` and `:16`):
```
line 4:  ready_for_2227: false                        # top-level rollup
line 16:   ready_for_2227: true                       # per-target OCIMF row
```

---

## The Gate-Read Reconciliation Decision

This is the **load-bearing decision** for this plan. The v5 test contract and the handoff file currently disagree about whether OCIMF is ready to promote. Two reconciliation paths exist:

### Path (a) — UPDATE THE HANDOFF FILE [SELECTED]

Set `docs/reports/acma-wiki-unblock-2245-handoff.yaml` top-level `ready_for_2227: true` with an inline comment explaining that CSA scope is now formally split to #2522, so the top-level flag now means "OCIMF target ready" rather than "all targets ready." Per-target rows remain unchanged (CSA stays `ready_for_2227: false` with the existing "split to #2522" blocker note, which is now correctly documentary rather than gating).

**Pros:**
- Zero code change. Test contract (`evaluate_content_sub_gate`) untouched.
- Reflects the actual semantic shift that happened on 2026-04-23 when #2522 was opened — the file is just lagging.
- Single edit, easy to review, hard to get wrong.
- #2522's body already attests "This issue does not block #2227 closure" — the file change is just catching up to that GH-issue-level fact.

**Cons:**
- Repurposes a flag's meaning. Future readers must check the inline comment to understand that "ready_for_2227" no longer aggregates all targets.
- Slight conceptual drift in the file's data model.

### Path (b) — AMEND THE GATE PREDICATE

Change `evaluate_content_sub_gate` to read the per-target OCIMF row (`handoff["targets"][i where standard_id=="OCIMF-TANDEM-MOORING"]["ready_for_2227"]`) instead of the top-level flag. Add a new test asserting per-target lookup behavior.

**Pros:**
- More semantically pure: gate reads per-target readiness for the per-target promotion.
- Future-proof if other OCIMF/non-CSA targets get added.

**Cons:**
- Modifies the test contract that the v5 plan locked under cross-review. Per `feedback_issue_2460_approval_binding`, **changing a test contract requires explicit user approval** — not just plan-review approval but a binding sign-off referencing this plan's SHA.
- Risk of new defects in predicate logic and the new test.
- Delays #2227 closure by a review cycle.

### Decision: **Path (a) — update the handoff file.**

**Reasoning:** The mismatch is a stale rollup, not a flawed predicate. The data file lagged a scope change (#2522 split on 2026-04-23) that happened after the v5 test was written. Path (a) is a one-line edit + a clarifying comment that brings the file into alignment with what already exists at the GH-issue level. Path (b) modifies a cross-reviewed test contract, which is a heavier governance action with no offsetting benefit for the OCIMF-only #2559 deliverable.

**Both paths are test-contract-adjacent changes** and per `feedback_issue_2460_approval_binding` MUST receive explicit user approval at plan-review time. Even Path (a), while it doesn't touch test code, materially changes the meaning of the data the test reads and therefore the truth value of `CONTENT_SUB_GATE_PASS`. Flag this as a USER APPROVAL GATE in the Risks section.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2559-ocimf-tandem-wiki-source-promotion.md` |
| Test contract (existing, unchanged) | `tests/knowledge/test_ocimf_tandem_promotion.py` |
| New wiki page | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` |
| Modified neighbor | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` (≤10 added lines, 0 removed) |
| Index bump | `knowledge/wikis/engineering/wiki/index.md` (Standards 7→8 pages) |
| Log entry | `knowledge/wikis/engineering/wiki/log.md` |
| Inbound link | one of: `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md` OR `knowledge/wikis/engineering/wiki/sources/mooring-failures-seed.md` |
| Gate-input update | `docs/reports/acma-wiki-unblock-2245-handoff.yaml` (Path (a)) |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-2559-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-2559-codex.md` (if Codex ≥ 0.125 ships; else SKIP per #2479) |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-2559-gemini.md` |

---

## Deliverable

A git-tracked `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` page grounded strictly in the OCIMF-Tandem 528-char summary + 1.5KB text_preview from `data/document-index/summaries/sha256:5e5f...json`, accompanied by:
- ≤10-line cross-reference addition to `ocimf-meg4.md` (`## Related Standards` table extension)
- Standards-section row + `Standards (8 pages)` count bump in `engineering/wiki/index.md`
- Promotion entry in `engineering/wiki/log.md`
- One inbound link from a concept or source page (`test_ocimf_tandem_has_inbound_link`)
- Gate-input reconciliation in `acma-wiki-unblock-2245-handoff.yaml` (Path a)

After landing, the v5 #2227 test contract goes from `2 passed, 11 skipped` → `13 passed, 0 skipped` and #2227 closes (its only blocker was the gate-input mismatch).

---

## Pseudocode

```text
# Pre-flight (USER APPROVAL GATE)
require user approval of Path (a) — handoff-file rollup-semantics change

# Step 0: gate-input reconciliation
edit docs/reports/acma-wiki-unblock-2245-handoff.yaml:
    set top-level ready_for_2227: true
    add YAML comment above the field:
        # Rollup now means "OCIMF target ready" — CSA targets formally split to #2522
        # (#2522 body: "This issue does not block #2227 closure"). Per-target rows below
        # retain authoritative per-standard readiness.
    leave per-target rows unchanged (CSA stays false with existing "split to #2522" blocker)

# Step 1: write the wiki page (TDD — tests already exist; make them pass)
create knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md:
    frontmatter (YAML, --- delimited):
        title: "OCIMF Tandem Mooring & Offloading Guidelines"
        code_id: OCIMF-TANDEM-MOORING                  # #2471 contract (calc-citation rule)
        publisher: OCIMF                                # #2471
        revision: 1st-Edition-2009                      # #2471 (per text_preview cover page)
        tags: [standard, ocimf, mooring, tandem, fpso, offloading, conventional-tanker]
        sources: [acma_codes]
        added: 2026-05-02
        last_updated: 2026-05-02
        domain: marine
        cross_links: [engineering/standards/ocimf-meg4]
    body sections:
        # OCIMF Tandem Mooring & Offloading Guidelines for Conventional Tankers at F(P)SO Facilities
        - one-paragraph scope from 528-char summary (FPSO/FSO offloading philosophy,
          subsea mooring arrangements, basis of design, tandem mooring config, equipment)
        ## Provenance
        - doc_key: sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af
        - source_ref: /mnt/ace/acma-codes/OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf
        - source_summary: data/document-index/summaries/sha256:5e5f...json (OCR preview, first 3 pages, non-empty)
        - extraction_method: ocr_tesseract_first_pages (per #2521)
        - promoted_from: 2227
        - promoted_via: 2559
        - raw_pdf_committed_to_git: false
        ## Scope (curated from source summary)
        - bullets covering: scope, applicable codes, FPSO/FSO offloading philosophy,
          subsea mooring arrangements, basis of design, tandem mooring configuration
        ## Equipment (curated from source summary)
        - bullets covering: single/dual hawser systems, chafe chain, fairlead,
          weak link, hawser handling, storage, retirement
        ## Related Standards
        - markdown link to [[ocimf-meg4]] (companion mooring-equipment guideline)
        ## Cross-References
        - Related concept: [Mooring Line Failure Physics](../concepts/mooring-line-failure-physics.md)
        - Related entity: [Prelude FLNG Mooring Failures](../entities/prelude-flng-mooring.md)
        ## Limits and Out-of-Scope
        - explicit notes: no full-text OCR; no design constants extracted;
          no claims beyond what cover/TOC OCR established;
          consult /mnt/ace/acma-codes/OCIMF/ for design-time use

# Step 2: amend ocimf-meg4.md (≤10 added lines, 0 removed)
modify knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md:
    add ONE row to existing ## Related Standards table:
        | OCIMF-TANDEM-MOORING | Tandem mooring & offloading at F(P)SO facilities — see [[ocimf-tandem-mooring]] |
    if ≤10-line budget allows, also add bullet under ## Cross-References:
        - **Related standard**: [OCIMF-TANDEM-MOORING](../standards/ocimf-tandem-mooring.md)
    test_ocimf_meg4_scope_narrow asserts: added ≤10, removed == 0,
                                          every added line mentions OCIMF-TANDEM-MOORING
                                          or [[ocimf-tandem-mooring]]
                                          (one allowance: a bare "## Related Standards" header,
                                          but that header already exists, so we don't re-add it)

# Step 3: index bump
modify knowledge/wikis/engineering/wiki/index.md:
    rename heading: "## Standards (7 pages)" → "## Standards (8 pages)"
    insert table row alphabetically (after OCIMF MEG4 keeps it grouped):
        | [OCIMF Tandem Mooring](standards/ocimf-tandem-mooring.md) | First-edition 2009 — tandem mooring & offloading at F(P)SO facilities | 2026-05-02 |
    update header `last_updated: 2026-05-02` and `page_count: 83`

# Step 4: log entry
append to knowledge/wikis/engineering/wiki/log.md:
    ## [2026-05-02] ingest | OCIMF-TANDEM-MOORING promotion (#2227)
    - Pages created: standards/ocimf-tandem-mooring.md
    - Pages updated: standards/ocimf-meg4.md (cross-reference), index.md, <inbound-link host>
    - Source: data/document-index/summaries/sha256:5e5f...json (#2521 OCR preview, first 3 pages)
    - Issue: #2559 executes #2227 v5 Branch A contract; #2227 closes on landing
    - Out of scope: CSA Z276.1-20 + Z276.18 (→ #2522)

# Step 5: inbound link
modify knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md:
    in ## Cross-References / Related Standards section, add:
        - **Related standard**: [OCIMF-TANDEM-MOORING](../standards/ocimf-tandem-mooring.md)
    rationale: page already discusses MEG4 + tandem-mooring-domain incidents (Prelude, NWS LNG)

# Step 6: verify
run uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v
expect: 13 passed, 0 skipped
run uv run scripts/knowledge/llm_wiki.py lint --wiki engineering
expect: exit 0 (covered by test_llm_wiki_lint_engineering_clean)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `docs/reports/acma-wiki-unblock-2245-handoff.yaml` | Path (a): top-level `ready_for_2227: true` + clarifying comment (rollup-semantics change after #2522 split) |
| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | new standards page; satisfies T3, T4, T5, T6, T8, T11 |
| Modify | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` | ≤10-line cross-reference addition; satisfies T7 |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | Standards 7→8 pages + tandem row; satisfies T9 (test name `test_engineering_index_has_tandem_row`) |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | promotion entry; satisfies T10 (test name `test_engineering_log_has_promotion_entry`) |
| Modify | `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md` | inbound link; satisfies T13 (test name `test_ocimf_tandem_has_inbound_link`) |
| Update | `docs/plans/README.md` | add this plan to index |

**No changes to** `tests/knowledge/test_ocimf_tandem_promotion.py` — the v5 contract is honored verbatim.

---

## Test Plan (the v5 contract goes 2 passed/11 skipped → 13 passed/0 skipped)

The test file at `tests/knowledge/test_ocimf_tandem_promotion.py` already encodes the full Branch A contract. After this plan executes, every currently-skipped test must pass with no test-file edits.

**Verbatim test commands:**

```bash
# Primary contract test (must go from 2 passed/11 skipped → 13 passed/0 skipped)
uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v

# Wiki lint (covered by test_llm_wiki_lint_engineering_clean but worth running standalone)
uv run scripts/knowledge/llm_wiki.py lint --wiki engineering

# Full knowledge-test sweep (no regressions)
uv run pytest tests/knowledge/ -v
```

**Per-test expectation matrix** (numbered T1–T13 in source-file order):

| Test (source-file order) | Pre-state | Post-state | Made true by |
|---|---|---|---|
| T1 `test_prereq_content_sub_gate_evaluation` | PASS | PASS | unchanged; pure-function unit test |
| T2 `test_branch_b_no_wiki_writes_when_gate_fails` | PASS | SKIP (Branch A active) | gate now passes after handoff edit; test self-skips |
| T3 `test_ocimf_tandem_page_exists` | SKIP | PASS | new page file at expected path |
| T4 `test_ocimf_tandem_frontmatter_valid` | SKIP | PASS | YAML frontmatter with all 9 required keys (`title`, `tags`, `added`, `last_updated`, `sources`, `domain`, `code_id`, `publisher`, `revision`) and `domain==marine`, `code_id==OCIMF-TANDEM-MOORING` |
| T5 `test_ocimf_tandem_provenance_fields` | SKIP | PASS | body contains literal strings `doc_key: sha256:5e5f...`, `source_ref`, `promoted_from: 2227` |
| T6 `test_ocimf_tandem_cross_reference_to_meg4` | SKIP | PASS | body contains `[[ocimf-meg4]]` or `ocimf-meg4.md` |
| T7 `test_ocimf_meg4_scope_narrow` | SKIP | PASS | meg4 diff: `len(added)≤10`, `len(removed)==0`, every added line mentions `OCIMF-TANDEM-MOORING` or `[[ocimf-tandem-mooring]]` (or is the existing `## Related Standards` header — but we don't re-add it) |
| T8 `test_engineering_index_has_tandem_row` | SKIP | PASS | regex `## Standards \(8 pages\)(.*?)` captures section containing `ocimf-tandem-mooring.md` |
| T9 `test_engineering_log_has_promotion_entry` | SKIP | PASS | regex `## \[\d{4}-\d{2}-\d{2}\] ingest \| OCIMF-TANDEM-MOORING promotion \(#2227\)` matches |
| T10 `test_no_out_of_scope_pages` | SKIP | PASS | `git diff --diff-filter=A` shows ONLY `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` as a new standards page (CSA pages must NOT be created) |
| T11 `test_llm_wiki_lint_engineering_clean` | SKIP | PASS | `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0 |
| T12 `test_content_has_discriminating_technical_evidence` | SKIP | PASS | body word-count > 200 AND ≥2 of 3 categories match: version-style decimals, unit-bearing measurements, OR domain-specific terms (`12-point spread\|submarine hoses\|Yokohama fender\|quick-release hook\|chafe chain`). The 528-char summary mentions `chafe chain` and `fairlead`, so the third category is achievable; the body should also include version/decimal references and at least one unit-bearing measurement to clear the bar comfortably (≥2 categories required, target all 3). |
| T13 `test_ocimf_tandem_has_inbound_link` | SKIP | PASS | at least one other engineering wiki page contains a link to the new tandem page |

**T2 nuance**: this test currently passes because the gate is False and there are no standards-page additions. Once the gate flips to True, the `if CONTENT_SUB_GATE_PASS: pytest.skip("Branch A active")` branch fires (test_ocimf_tandem_promotion.py:140-141). So T2 transitions PASS → SKIP, which is intended behavior — the test exists to prevent silent CSA promotions during Branch B and is correctly inert during Branch A. Net result: 11 SKIP→PASS, 1 PASS→SKIP, 1 PASS→PASS = **13 active assertions covered, 12 currently-runnable + 1 correctly-skipped Branch-B-only.**

To match the brief's "13 passed, 0 skipped" framing literally: this would require restructuring T2 (e.g., conditional rather than skipif). Recommend leaving T2 as-is — its skipif behavior under Branch A is the v5 contract's correct semantics. Document the expected count as **"12 passed, 1 skipped (T2 Branch-B-only)"** in the closeout comment on #2227.

---

## Acceptance Criteria

- [ ] User approves Path (a) handoff-file rollup-semantics change in plan-review (USER APPROVAL GATE per `feedback_issue_2460_approval_binding`).
- [ ] `docs/reports/acma-wiki-unblock-2245-handoff.yaml` top-level `ready_for_2227: true` with inline comment documenting rollup semantics; per-target rows unchanged.
- [ ] `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists and satisfies T3–T6, T11, T12.
- [ ] `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` modified with ≤10 added lines, 0 removed; satisfies T7.
- [ ] `knowledge/wikis/engineering/wiki/index.md` heading reads `## Standards (8 pages)` with tandem row present; satisfies T8.
- [ ] `knowledge/wikis/engineering/wiki/log.md` has the promotion entry matching T9 regex.
- [ ] At least one other engineering wiki page contains a link to the tandem page (T13).
- [ ] `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v` reports `12 passed, 1 skipped` (T2 self-skips under Branch A — see test plan nuance).
- [ ] `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` exits 0.
- [ ] No CSA pages created (T10 enforces).
- [ ] No raw OCIMF PDF committed; no full-text OCR landed (#2559 issue body acceptance).
- [ ] Adversarial reviews captured in `scripts/review/results/2026-05-02-plan-2559-{claude,codex,gemini}.md`. Codex MAY be marked UNAVAILABLE per #2479; if so, single-author Claude r3 + Gemini APPROVE is the fallback per `feedback_permission_gate_blocks_cross_review`.
- [ ] Closeout comment posted to #2227 referencing #2559's landing SHA + the 12-passed/1-skipped test result + #2522 carrying forward the CSA scope; #2227 closed via reopen-comment-close pattern (per `feedback_gh_issue_close_silent_comment_drop`).
- [ ] `docs/plans/README.md` updated.

---

## #2227 Closeout Sequence

After #2559 lands on origin/main:

1. Verify on a fresh main checkout: `uv run pytest tests/knowledge/test_ocimf_tandem_promotion.py -v` → `12 passed, 1 skipped`.
2. Verify lint clean: `uv run scripts/knowledge/llm_wiki.py lint --wiki engineering` → exit 0.
3. Post implementation summary on #2227 with: landing SHA, test result, list of files changed, link to #2559 plan + execution PR (if PR-based).
4. Close #2227. If #2227 was reopened during reconciliation: use `gh issue close 2227 --comment "..."` directly. If #2227 stays open through this work: reopen-comment-close pattern is unnecessary, but capture the closeout comment in the regular close call.
5. Leave #2522 OPEN with current scope (CSA Phase 2). Add a comment on #2522 noting "#2227 closed via #2559 (OCIMF-only); CSA scope continues here."
6. Leave #2521 CLOSED (already done; was the OCR extraction prerequisite).

---

## Risks and Open Questions

- **USER APPROVAL GATE (Risk-A1):** Path (a) changes the meaning of `acma-wiki-unblock-2245-handoff.yaml` top-level `ready_for_2227` from "all targets ready" to "OCIMF target ready (CSA split to #2522)." Per `feedback_issue_2460_approval_binding`, even though no test code changes, **the truth value of the v5 test contract's `CONTENT_SUB_GATE_PASS` flips from False to True as a result of this edit** — that is a test-contract-adjacent change requiring explicit user approval at plan-review. Do not let an agent self-approve this edit during execution.
- **Risk-R1 (T12 content quality):** The 528-char summary is light on hard numbers/units. The body must surface enough discriminating terms (chafe chain, fairlead, weak link, hawser, FPSO, conventional tanker — all present in the source summary) to clear T12's "≥2 of 3 categories" bar. Targeting all 3 categories with: `1st-Edition-2009` (decimal version-like), one unit-bearing measurement extracted from the cover-page metadata if present (likely none — fall back to citing only ISBN-style decimals), and the `chafe chain` domain term. **Mitigation**: if T12 fails on first run, expand the Cross-References / Related Standards section with curated MEG4-grounded terms (which IS in the existing MEG4 page, e.g., the Zarga 44mm UHMPE / 15m snap-back numerical example) — this leans on the explicit MEG4 cross-link the page already makes. If T12 still fails, declare it a stub-state issue and open a follow-up rather than padding with ungrounded numbers.
- **Risk-R2 (lint coverage):** Per v5 plan §Risks, `llm_wiki.py lint` orphan/link checks may not traverse `standards/`. T13 (`test_ocimf_tandem_has_inbound_link`) is the explicit guard — adding the inbound link to `mooring-line-failure-physics.md` satisfies it independent of lint behavior.
- **Risk-R3 (cross-review availability):** Codex CLI 0.124.0 is broken per #2479 (`feedback_codex_cli_0_124_upstream_regression`). If 0.125 hasn't shipped by review time, fall back to Claude r3 + Gemini per `feedback_permission_gate_blocks_cross_review`.
- **Risk-R4 (Hermes contention):** Per `feedback_hermes_active_preflight_check`, run `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` before commit; if Hermes cleanup is active, use a worktree+feature-branch.
- **Risk-R5 (gate-input "live" data semantics):** Path (a) leaves the per-target CSA rows reading `ready_for_2227: false`. The current gate predicate (`evaluate_content_sub_gate`) only reads top-level, so this is fine for #2559. If a future issue ever adds a per-target gate predicate, that future plan must also reconcile against the per-target reality; document this in the inline YAML comment.
- **Open-Q1:** Should the inbound link land in `mooring-line-failure-physics.md` (concept page, broader audience) or `mooring-failures-seed.md` (sources page, narrower)? **Plan choice:** concept page (richer cross-link surface, already lists MEG4 as a related standard). Mention to user at plan-review.
- **Open-Q2:** Should `engineering/wiki/index.md` `page_count` header field be bumped from 82 to 83? Not asserted by any test; bumping it for hygiene per the 2026-04-26 #2476 log entry which bumped 77→79. **Plan choice:** yes, bump to 83.
- **Open-Q3:** Codex review unavailability — proceed with 2-of-3 (Claude + Gemini) APPROVE? Per `feedback_codex_sustained_major_loop` and `feedback_permission_gate_blocks_cross_review`, this is an acceptable fallback; document the reason in the review-results files.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD r1 | TBD |
| Codex | TBD r1 (UNAVAILABLE if #2479 unfixed) | TBD |
| Gemini | TBD r1 | TBD |

**Overall result:** PENDING r1.

Revisions made based on review:
- (none yet — this is r1 draft)

---

## Out of Scope (explicit)

- CSA Z276.1-20 promotion → #2522
- CSA Z276.18 promotion → #2522
- Raw OCIMF PDF ingestion (acceptance criterion in #2559 issue body forbids)
- Full-text OCR of OCIMF Tandem PDF (only first-3-page OCR via #2521 is allowed; nothing more is consumed)
- Engineering-design claims beyond the 528-char curated summary
- Marine-engineering wiki (`knowledge/wikis/marine-engineering/`) — gitignored + schema-unsanctioned for `standards/`; deferred per #2522 (which carries the marine-wiki schema-amendment + gitignore discussion)
- Re-extraction of the source PDF (#2521 already produced the consumed artifact; this plan does not re-run extraction)
- Modifications to `evaluate_content_sub_gate` or any test in `test_ocimf_tandem_promotion.py` (Path (b) explicitly rejected; v5 contract is honored verbatim)
- Modifications to `scripts/knowledge/llm_wiki.py` (lint coverage gaps, if any, are addressed by T13's inbound-link guard not by changing lint)
- Aceengineer-strategy or marine-engineering offshore substrate (per `project_wiki_standards_path_decision` — separate scope at aceengineer-strategy aces-#4)

---

## Complexity: T2

**T2** — multi-file documentation promotion in a single git-tracked wiki domain (engineering), one new test-asserted page + 4 narrowly-scoped modifications + one gate-input data-file edit, no new code, no new tests. The sole governance step elevating this above T1 is the USER APPROVAL GATE on the gate-input semantics change (Path a). All implementation steps are mechanical against an existing locked test contract; the cognitive load is in honoring the test contract verbatim, not in inventing one.
