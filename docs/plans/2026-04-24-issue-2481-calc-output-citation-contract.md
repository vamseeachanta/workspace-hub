# Plan for #2481: calculation-output citation contract

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2481
> **Review artifacts:** (pending — not yet submitted to cross-review)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/marine-engineering/wiki/` — 19K+ promoted pages including standards references (target of citations)
- Found: `scripts/data/llm-wiki/search-wiki.py` — retrieval primitive that calc modules will call
- Found: `digitalmodel/` submodule — hosts engineering calc pipelines (pilot candidate lives here)
- Gap: no schema file exists at `docs/standards/calc-output-citation.md`
- Gap: no calc pipeline currently emits citations in its output
- Gap: no `.claude/rules/calc-citation-contract.md` rule file

### Standards
| Standard | Status | Source |
|---|---|---|
| API RP 2SK (mooring) | candidate pilot (citations) | data/document-index/standards-transfer-ledger.yaml |
| DNV-OS-E301 (position mooring) | candidate pilot (citations) | standards-transfer-ledger.yaml |
| frontmatter schema | locked per #2471 | docs/plans/2026-04-23-issue-2471-wiki-standards-path.md |

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/standards/` — destination wiki subtree for cited clauses (per #2471 routing decision)
- `knowledge/wikis/engineering/wiki/concepts/` — source of methodology pages

### Documents consulted
- `#2238` — closed-issue citation guardrail (covers durable docs, NOT calc outputs)
- `#2471` — standards `code_id`/`publisher`/`revision` frontmatter (this plan's schema inherits from it)
- `#2400` — MCP wiki_search (retrieval API that citation validator will use)
- `#2365` — design-code registry promotion (target set of citable codes)
- `#2390` — epic roadmap (confirms no overlapping ownership for this contract)

### Gaps identified
- No citation schema for calc outputs anywhere in the repo portfolio
- No validator that checks cited `wiki_path` resolves at calc time
- No adoption rule agents can read to emit consistent citations
- No example output that downstream reviewers can reference

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via `gh issue view`):
- `#2471` — OPEN — canonical CSA Z276 wiki routing and durability contract
- `#2238` — OPEN — closed-issue citation guardrail
- `#2365` — OPEN — design-code registry promotion
- `#2400` — OPEN — MCP server doc_key/wiki_search/registry
- `#2390` — OPEN — epic roadmap

**File existence** (`ls` 2026-04-24):
- EXISTS: knowledge/wikis/marine-engineering/wiki/
- EXISTS: scripts/data/llm-wiki/search-wiki.py
- MISSING (this plan creates): docs/standards/calc-output-citation.md
- MISSING (this plan creates): .claude/rules/calc-citation-contract.md
- MISSING (this plan creates): digitalmodel pilot calc citation emission

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-2481-calc-output-citation-contract.md |
| Schema doc | docs/standards/calc-output-citation.md |
| Rule file | .claude/rules/calc-citation-contract.md |
| Pilot implementation | digitalmodel/src/digitalmodel/... (exact path chosen during impl) |
| Pilot tests | digitalmodel/tests/... |
| Sample output | docs/reports/2026-04-24-calc-citation-sample.md |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-2481-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-2481-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-2481-gemini.md |

---

## Deliverable

A documented citation schema, an adoption rule, a pilot digitalmodel calc that emits wiki-backed citations in its output, and tests that verify each cited `wiki_path` resolves to an existing wiki page at calc time.

---

## Pseudocode

```
schema definition (docs/standards/calc-output-citation.md):
    citation = {
        code_id:    str,   # matches frontmatter in wiki page (#2471)
        publisher:  str,   # e.g., "API", "DNV", "ISO"
        revision:   str,   # publisher revision label
        section:    str,   # clause/section/figure identifier
        wiki_path:  str,   # repo-relative knowledge/wikis/... path
        note:       str,   # optional free text (e.g., "used factor from Table 3")
    }
    output block = {
        result: <existing calc result>,
        citations: [citation, ...],
    }

pilot calc emits:
    for each standards-derived input in calc:
        resolve citation via wiki page frontmatter lookup
        append citation to output.citations
    validate every citation.wiki_path exists before returning
    if any missing: raise CitationResolutionError(wiki_path, code_id)

rule file (.claude/rules/calc-citation-contract.md):
    when a calc module uses a standards-derived constant or formula:
        emit a citation matching the schema
        wiki_path MUST point to a page whose frontmatter code_id/publisher/revision match

tests:
    test_schema_validates_well_formed_citation
    test_schema_rejects_missing_required_field
    test_pilot_calc_emits_expected_citations_for_known_input
    test_pilot_calc_raises_on_broken_wiki_path
    test_pilot_calc_sample_output_has_at_least_one_citation
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/standards/calc-output-citation.md | schema + examples |
| Create | .claude/rules/calc-citation-contract.md | adoption rule for agents |
| Create | digitalmodel/src/... (pilot file chosen during impl) | pilot emission |
| Create | digitalmodel/tests/... | pilot TDD tests |
| Create | docs/reports/2026-04-24-calc-citation-sample.md | worked example |
| Modify | knowledge/wikis/marine-engineering/wiki/standards/*.md (pilot citations target) | ensure target pages have required frontmatter |
| Update | docs/plans/README.md | add index row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_schema_accepts_well_formed_citation | happy path validation | full citation dict | True |
| test_schema_rejects_missing_code_id | required field enforcement | citation without code_id | ValidationError |
| test_schema_rejects_relative_wiki_path_outside_wiki_tree | security | wiki_path="../../etc/passwd" | ValidationError |
| test_pilot_calc_emits_citation_for_standards_constant | integration | known mooring input | output contains ≥1 citation with expected code_id |
| test_pilot_calc_raises_on_missing_wiki_page | fail-closed | citation points to non-existent wiki_path | CitationResolutionError |
| test_pilot_calc_sample_matches_golden_output | regression | fixture input | output matches committed golden file |

---

## Acceptance Criteria

- [ ] Schema doc committed with worked examples covering ≥2 publishers
- [ ] Rule file committed under `.claude/rules/`
- [ ] Pilot digitalmodel calc emits citations for at least one standards-derived constant
- [ ] Tests verify every cited wiki_path resolves at calc time (no broken citations)
- [ ] Sample output doc reviewed against a real engineering standard by domain subject-matter holder
- [ ] `uv run pytest digitalmodel/tests/<pilot path>` passes in a clean checkout
- [ ] No regression in existing digitalmodel suite

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | not yet dispatched |
| Codex | PENDING | codex-cli 0.124.0 regression (#2479) currently blocks `codex exec` |
| Gemini | PENDING | not yet dispatched |

**Overall result:** PENDING — plan surfaced for user-first review per explicit request.

---

## Decisions (locked 2026-04-24 by user)

The 3 open questions from v1 are resolved. Implementation proceeds against these answers without requiring re-approval (plan scope unchanged; gray areas closed).

| # | Question | Decision | Rationale |
|---|---|---|---|
| D1 | Pilot module: mooring load-factor vs fatigue-stress-range? | **mooring load-factor** | Clean standards-dependency trail (API RP 2SK, DNV-OS-E301, ISO 19901-7 — all required, not discretionary). Single-coefficient output is easier to prove the citation pattern with than fatigue arrays. Mooring is the most wiki-covered domain (40 entries at `knowledge/seeds/`), lower risk of missing-wiki-page blockers. |
| D2 | Validation: fail-closed at calc time vs warn-at-report-render? | **fail-closed at calc time** | Professional-practice outputs should not silently ship without provenance. Consistency with `knowledge/_archive/` ingest-exclusion (landed via #2482) and future #2485 ledger pattern. Missing citation is a correctness signal. |
| D3 | wiki_path resolution: direct file read vs MCP wiki_search (#2400)? | **direct file read, with migration-to-MCP note** | #2400 not yet shipped; coupling to unreleased infra adds a blocking dependency. Direct read is simpler, faster, and sufficient for the pilot's correctness goal (verify page exists, verify frontmatter matches `code_id`). Resolver is isolated inside a validator function — swap later without schema change. |

**D2 operational note:** `CitationResolutionError` must include the citation's `code_id` in its message so operators can retarget the citation (not disable it) when a wiki page moves or is archived.

**D3 migration note:** once #2400 lands, the validator function's internal resolver can switch from `pathlib.Path(wiki_path).exists()` to MCP `wiki_search` without touching the citation schema or the calc pipeline. Separate follow-up issue at that point.

## Residual risks (scope-bounded; no open decisions)

- **Risk:** cited wiki pages may lack frontmatter populated by #2471 when this ships. Mitigation: depend on #2471 landing first, or populate frontmatter for the specific pages the pilot needs.
- **Risk:** citation emission in calc output may break downstream consumers expecting plain numeric result. Mitigation: put citations in a sidecar block, not in the primary result payload (already in §Pseudocode).
- **Risk (D2-specific):** wiki page rename/move breaks calcs downstream. Mitigation: `CitationResolutionError` message carries `code_id` so operators retarget, not disable.

---

## Complexity: T3

Cross-repo work (workspace-hub schema + `.claude/rules` + digitalmodel pilot), multiple new files, coupling to #2471 frontmatter, and governance doc review required.
