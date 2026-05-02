# Plan for LLM-Wiki Completeness W3-C: #2471 Sanction-Scope Erratum (Forward-Amend W1-A and W1-B)

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2596
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Trigger:** W2 adversarial-review wave (#2590 / #2591 / #2592) surfaced a systemic over-citation of [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) as a generalized path-sanction; same defect persists in already-committed W1-A (#2586) and W1-B (#2587) plans on `main`.
> **Review artifacts:** scripts/review/results/2026-05-02-plan-W3-2471-erratum-claude.md | …-codex.md | …-gemini.md (to be produced)

---

## Resource Intelligence Summary

### Existing repo code

- `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — W1-A plan (engineering-standards/API). Currently on `main` at `status:plan-review`. Cites #2471 as a path-sanction in its frontmatter and Files-to-Change rationale (5 distinct citations).
- `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` — W1-B plan (asset-management). Currently on `main` at `status:plan-review`. Cites #2471 as a path-sanction in 11 distinct lines, all routing asset-management standards pages under `wiki/standards/`.
- `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` — W2-A; ALREADY revised in W2 commit; provides the canonical replacement language pattern (line 10 "Path sanction (DNV)" header anchors to engineering-standards `CLAUDE.md` schema + calc-citation-contract rule 2 + #2586 organizational precedent; #2471 demoted to historical-origin-of-frontmatter-triple footnote).
- `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md` — W2-B; ALREADY revised; line 9 "Path sanction (re-anchored after r1 review)" pattern.
- `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` — W2-C; ALREADY revised; flagged maritime-law as out-of-principle-scope, defaulted to `wiki/concepts/`.
- `.claude/rules/calc-citation-contract.md` rule 2 — sanctions the frontmatter triple `code_id`/`publisher`/`revision`. Cites #2471 only as the historical origin of those fields, not as a path-routing rule.
- `knowledge/wikis/engineering-standards/CLAUDE.md` — local directory schema for the engineering-standards wiki; the actual sanctioning authority for `wiki/standards/<code-id>.md` routing within that wiki.

### Standards
Not applicable — this is a documentation/governance correction, not a standards-implementation issue.

### LLM Wiki pages consulted
Not applicable — no wiki content is touched by this plan.

### Documents consulted
- `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_standards_path_decision.md` — load-bearing memory, quoted verbatim in Evidence below.
- `docs/plans/README.md` — index of plans; entries for #2586 (line 206), #2587 (line 207), #2590-#2593 (lines 210-213) all marked `plan-review` with notes about the #2471 systemic finding from W2.
- `docs/plans/_template-issue-plan.md` — followed for this plan structure.
- W2 plans (#2590, #2591, #2592) — provide tested replacement language patterns, used as templates here.

### Gaps identified
- W1-A and W1-B plans are committed to `main` with the over-citation; no forward-amendment landed yet.
- No explicit asset-management decision exists about whether `wiki/standards/<code-id>.md` routing applies to that wiki; memory restricts the principle to {marine-engineering, engineering, naval-architecture}.
- No automated guardrail prevents future plans from over-citing #2471 the same way; this plan adds one minimal regression test.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-02 via `gh issue view`):
- `#2471` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"
- `#2540` — OPEN — "epic(llm-wiki): overnight Elements corpus planning wave after #2536"
- `#2586` — OPEN, labels include `status:plan-review`, `priority:medium`, `cat:documentation`, `domain:knowledge-management`, `domain:standards`
- `#2587` — OPEN, labels include `status:plan-review`, `priority:medium`, `cat:documentation`, `domain:knowledge-management`, `domain:asset-integrity`

**File existence** (`ls -la` 2026-05-02):
- EXISTS: `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md`
- EXISTS: `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md`
- EXISTS: `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` (W2-A — already revised, NOT touched by this plan)
- EXISTS: `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md` (W2-B — already revised, NOT touched)
- EXISTS: `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` (W2-C — already revised, NOT touched)
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/README.md`
- MISSING (this plan creates): `tests/docs/test_2471_citation_scope.py`

**#2471 issue body excerpt** (`gh issue view 2471 --json body`):
> Decide and codify the sanctioned durable-wiki routing/schema for CSA Z276 pages before CSA coverage is promoted from ACMA/standards metadata into LLM-wiki content.
>
> ## Scope
> - Decide the canonical durable destination for CSA Z276 pages.
> - Update the relevant wiki schema/routing guidance if needed.

The #2471 scope statement names CSA Z276 specifically; it does not authorize a generalized `wiki/standards/<code-id>.md` routing for arbitrary publishers.

**`.claude/rules/calc-citation-contract.md` rule 2** (verbatim):
> Citation target: a wiki page with #2471 frontmatter (`code_id`, `publisher`, `revision`). Forward-adopt these fields if the specific page you need doesn't yet carry them.

The rule cites #2471 only as the origin of the frontmatter triple — not as a path-routing rule.

**Memory `project_wiki_standards_path_decision.md`** (load-bearing — verbatim, 2026-04-25 verification block):
> The principle applies to: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope.
>
> **Workspace-hub #2471** is OPEN with title "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — scoped **strictly to CSA Z276**, not the general substrate. Earlier framing in this memory described it as a general codification; that framing is stale.

(Note: as of 2026-05-02 #2471 is CLOSED, not OPEN as the memory states — but the scope-statement remains CSA-Z276-only.)

**W1-A #2471 citation count** (`grep -n "#2471\|2471 sanction" docs/plans/2026-05-02-issue-2586-...md`):
- L9: `> **Path sanction:** [#2471](...) (CLOSED) — `wiki/standards/<code-id>.md` routing` ← OVER-CITATION
- L61: `\`project_wiki_standards_path_decision.md\` — `wiki/standards/<code-id>.md` is the sanctioned path; #2471 codified it for CSA Z276 and the principle now generalizes.` ← FACTUALLY WRONG ("now generalizes" contradicts memory)
- L73: `\`#2471\` — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"` ← OK (statement of fact)
- L147: `…each carrying #2471-compliant frontmatter…` ← OK (refers to frontmatter triple, which is the rule-2 sanction)
- L225: `| \`test_frontmatter_has_code_id\` | required key per #2471 | …` ← OK (frontmatter, not path)

**W1-B #2471 citation count** (`grep -n "#2471\|2471 sanction" docs/plans/2026-05-02-issue-2587-...md`):
- L25: `…Will be added under \`wiki/standards/iso-55000.md\` … per #2471-sanctioned \`wiki/standards/<code-id>.md\` routing.` ← OVER-CITATION
- L41: `…not a code-with-revision under #2471 contract.` ← OK (frontmatter contract)
- L57: `…\`wiki/standards/\` routing rule (#2471) — both load-bearing.` ← OVER-CITATION
- L60: `Issue **#2471** (CLOSED) — sanctioned \`wiki/standards/<code-id>.md\` routing for code-identified pages…` ← OVER-CITATION
- L84: `\`#2471\` — CLOSED — …` ← OK (factual)
- L220-229: 10 lines of `… | #2471-routed standards page |` ← OVER-CITATION (10 instances)
- L254: `…carry the #2471-required fields | …` ← OK (frontmatter)
- L274: `…carry \`code_id\`, \`publisher\`, \`revision\` frontmatter per #2471 sanction…` ← OK (frontmatter)

**Critical gap (W1-B specific):** asset-management is not in the principle's scope per memory ({marine-engineering, engineering, naval-architecture} only). W1-B's routing of ISO 55000-family pages under `wiki/standards/` therefore lacks BOTH #2471 sanction AND the principle-level sanction. A separate decision is required.

Source count: **5 distinct sources** consulted (issue body of #2471; calc-citation-contract.md rule 2; project_wiki_standards_path_decision.md memory; W1-A plan file; W1-B plan file) — exceeds 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2596-llm-wiki-W3C-2471-erratum.md` |
| Tests | `tests/docs/test_2471_citation_scope.py` |
| Plan to amend (W1-A) | `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` |
| Plan to amend (W1-B) | `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` |
| Plan index update | `docs/plans/README.md` |
| Plan review — Claude | `scripts/review/results/2026-05-02-plan-W3-2471-erratum-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-02-plan-W3-2471-erratum-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-02-plan-W3-2471-erratum-gemini.md` |

---

## Deliverable

A pair of forward-amendment commits to W1-A (#2586) and W1-B (#2587) plan files that re-anchor every #2471 path-sanction citation to the correct local authority (engineering-standards `CLAUDE.md` directory schema for W1-A; an open-question flag for W1-B since asset-management is out of the principle's scope), preserving git blame via in-place edits and adding a minimal regression test that future plans cannot reintroduce the same over-citation.

---

## Forward-Amendment Plan (Per File)

### Constraint: forward-only

These edits AMEND files already on `main`. They are NOT a history rewrite. The original commits stand; the amendment is a NEW commit that changes the current file contents and adds an in-line provenance note ("Originally cited #2471 as path-sanction; corrected per W3-C erratum 2026-05-02 — actual sanction is local CLAUDE.md schema."). All future-tense rules of the plan template still apply: the amended language must describe the corrected state as the going-forward truth, not as a past artifact.

### W1-A (`docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md`)

| Line | Current | Proposed (mirrors W2-A pattern) |
|---|---|---|
| L9 (frontmatter `Path sanction:`) | `> **Path sanction:** [#2471](...) (CLOSED) — \`wiki/standards/<code-id>.md\` routing` | `> **Path sanction (API):** Local sanctioning authority is \`knowledge/wikis/engineering-standards/CLAUDE.md\` directory schema (defines \`wiki/standards/<code-id>.md\` routing for engineering-standards domain). Frontmatter contract per \`.claude/rules/calc-citation-contract.md\` rule 2 (\`code_id\`/\`publisher\`/\`revision\`). **Note:** [#2471](...) (CLOSED) codified the path-routing decision **for CSA-Z276 specifically** (verified per memory \`project_wiki_standards_path_decision.md\`); it is NOT a general-standards path sanction and is cited here only as the historical origin of the frontmatter triple. **(Amended 2026-05-02 per W3-C erratum.)**` |
| L61 (Resource Intel — memory ref) | `…#2471 codified it for CSA Z276 and the principle now generalizes.` | `…#2471 codified the path-routing decision **for CSA Z276 specifically**; per memory \`project_wiki_standards_path_decision.md\` the routing principle generalizes only to {marine-engineering, engineering, naval-architecture} via each wiki's local CLAUDE.md schema, not via #2471 itself. (Amended 2026-05-02 per W3-C.)` |
| L147 (Deliverable — `#2471-compliant frontmatter`) | unchanged | (NO CHANGE — refers to the frontmatter triple, which IS the calc-citation-contract rule-2 sanction; #2471 is the historical origin.) |
| L225 (TDD — `required key per #2471`) | unchanged | (NO CHANGE — same reason.) |
| Top-of-file note | none | Add a single-line note after the existing header block: `> _This plan was amended on 2026-05-02 (W3-C erratum) to correct an over-citation of #2471 as a generalized path-sanction. The frontmatter-contract citations to #2471 are unchanged; the path-sanction has been re-anchored to the local engineering-standards \`CLAUDE.md\` schema._` |

### W1-B (`docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md`)

W1-B is more invasive: 13 distinct lines need amendment AND asset-management is **not** in the routing principle's scope, so the proposed `wiki/standards/` paths lack any current sanction.

| Line | Current | Proposed |
|---|---|---|
| L25 (Standards table — ISO 55000 row) | `Will be added under \`wiki/standards/iso-55000.md\` … per #2471-sanctioned \`wiki/standards/<code-id>.md\` routing.` | `**OPEN QUESTION (W3-C erratum 2026-05-02):** asset-management is NOT in the routing principle's scope per memory \`project_wiki_standards_path_decision.md\` ({marine-engineering, engineering, naval-architecture} only). Default routing for ISO 55000 family is therefore deferred to \`wiki/concepts/\` pending an explicit asset-management sanction issue (proposed follow-up). #2471 is CSA-Z276-only and does not authorize the routing here.` |
| L57 (load-bearing rules) | `\`wiki/standards/\` routing rule (#2471) — both load-bearing.` | `frontmatter contract (#2471 — origin of \`code_id\`/\`publisher\`/\`revision\` triple) — load-bearing for any standards-page that ships. **Note (W3-C):** there is no #2471 path-routing rule for asset-management; that decision is deferred.` |
| L60 (issue summary) | `Issue **#2471** (CLOSED) — sanctioned \`wiki/standards/<code-id>.md\` routing for code-identified pages…` | `Issue **#2471** (CLOSED) — sanctioned the \`code_id\`/\`publisher\`/\`revision\` frontmatter triple via the calc-citation-contract; the path-routing decision was scoped strictly to CSA-Z276 per memory \`project_wiki_standards_path_decision.md\`. (Corrected 2026-05-02 per W3-C erratum.)` |
| L220-229 (Files-to-Change rows — 10 standards pages) | `Create \| knowledge/wikis/asset-management/wiki/standards/<code>.md \| #2471-routed standards page` (×10) | Each row's "Reason" column changed to `Standards page (frontmatter contract per \`.claude/rules/calc-citation-contract.md\` rule 2). **Path placement is OPEN** pending asset-management routing decision (W3-C follow-up); default candidate is \`wiki/standards/\` mirroring engineering-standards but NOT yet sanctioned for this wiki.` |
| L41 (`under #2471 contract`) | unchanged | (NO CHANGE — refers to frontmatter-contract scope.) |
| L84, L254, L274 | unchanged | (NO CHANGE — refer to frontmatter triple, which is correctly sanctioned by calc-citation-contract rule 2.) |
| Top-of-file note | none | `> _This plan was amended on 2026-05-02 (W3-C erratum). Original draft cited #2471 as a path-sanction for asset-management standards pages. Per memory \`project_wiki_standards_path_decision.md\`, asset-management is OUTSIDE the routing principle's scope and #2471 is CSA-Z276-only. Path placement is now an OPEN QUESTION; frontmatter-contract citations are unchanged._` |

### `docs/plans/README.md`

Add a Note suffix to the existing rows for #2586 and #2587 (lines 206 and 207 respectively):
- 2586 row: append `; amended 2026-05-02 per W3-C erratum (#2471 path-sanction over-citation corrected; frontmatter citations unchanged).`
- 2587 row: append `; amended 2026-05-02 per W3-C erratum (#2471 path-sanction citations corrected; asset-management routing flagged as OPEN since the principle's scope excludes it).`

Add a new W3-C row in the appropriate date-sorted position with note: `Erratum plan retro-correcting systemic #2471 path-sanction over-citation in W1-A and W1-B; minimal regression test under \`tests/docs/test_2471_citation_scope.py\`.`

### Issue comments

Post a single comment to each of #2586 and #2587 with text:
> Plan amended 2026-05-02 per W3-C erratum (`docs/plans/2026-05-02-issue-2596-llm-wiki-W3C-2471-erratum.md`). Original draft over-cited #2471 as a generalized path-sanction; #2471 is scoped strictly to CSA-Z276 per memory `project_wiki_standards_path_decision.md`. Frontmatter-contract citations to #2471 remain valid (per `.claude/rules/calc-citation-contract.md` rule 2). [Asset-management-specific addendum for #2587:] this wiki is also outside the routing principle's scope, so the `wiki/standards/` path placement is now an OPEN QUESTION pending a separate sanction issue.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` | Forward-amend #2471 path-sanction over-citations to local CLAUDE.md schema + calc-citation-contract rule 2; add top-of-file W3-C provenance note. |
| Modify | `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` | Same as W1-A AND flag asset-management as outside the routing principle's scope; convert `wiki/standards/` placements to OPEN-QUESTION status. |
| Modify | `docs/plans/README.md` | Append amendment notes to #2586 and #2587 rows; add W3-C row. |
| Create | `tests/docs/test_2471_citation_scope.py` | Regression test enforcing that no plan in `docs/plans/2026-05-02-*.md` claims #2471 sanctions a generalized path-routing pattern. |
| Comment | GitHub issue #2586 | Announce amendment with link to W3-C plan. |
| Comment | GitHub issue #2587 | Announce amendment + asset-management OPEN-QUESTION flag. |

---

## Pseudocode

T1 — trivial. See "Forward-Amendment Plan" table above for exact replacement language.

The only non-trivial artifact is the regression test:
```
function test_2471_citation_scope():
    glob plans = docs/plans/2026-05-02-*.md
    for each plan_path in plans:
        text = read(plan_path)
        # Forbid any phrasing that asserts #2471 generalizes path-routing
        # beyond CSA-Z276. Allowed contexts: explicit acknowledgement-of-scope
        # ("CSA-Z276-specific", "CSA-only", "does not generalize", "scoped strictly")
        # or frontmatter-only references ("#2471-compliant frontmatter",
        # "#2471 contract", "code_id per #2471").
        offending_patterns = [
            r"#2471.{0,80}generaliz",        # claims generalization
            r"#2471-sanctioned\s+`?wiki/standards/", # path-routing claim
            r"#2471-routed\s+standards\s+page",      # row-level overcitation
        ]
        # Carve out the explicit acknowledgement contexts.
        # Strip lines containing "CSA-Z276-specific", "CSA-only",
        # "does NOT generalize", "scoped strictly", or "amended ... W3-C".
        filtered_text = strip_acknowledgement_lines(text)
        for pattern in offending_patterns:
            assert no match in filtered_text, f"#2471 over-citation in {plan_path}"
```

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_no_generalized_2471_path_sanction_in_plans` | No plan claims #2471 generalizes path-routing | All `docs/plans/2026-05-02-*.md` files | All files pass; offending lines (if any) listed in failure message |
| `test_w1a_amendment_landed` | W1-A plan contains the W3-C provenance note | `docs/plans/2026-05-02-issue-2586-...md` | Substring `W3-C erratum` present |
| `test_w1b_amendment_landed` | W1-B plan contains the W3-C provenance note AND the asset-management-out-of-scope flag | `docs/plans/2026-05-02-issue-2587-...md` | Substring `W3-C erratum` AND `asset-management is NOT in the routing principle's scope` (or near-equivalent) present |
| `test_acknowledgement_carveout_works` | Carve-out logic doesn't false-positive on legitimate scope-acknowledgement language | Synthetic input with phrase "#2471 is CSA-Z276-specific and does NOT generalize" | Test passes (no offending match) |

---

## Acceptance Criteria

- [ ] W1-A plan amended in-place; git blame preserved; top-of-file W3-C note added.
- [ ] W1-B plan amended in-place; asset-management flagged as outside-principle-scope; top-of-file W3-C note added.
- [ ] `docs/plans/README.md` updated with amendment notes on rows 206 and 207, and new W3-C row.
- [ ] `tests/docs/test_2471_citation_scope.py` created and passes: `uv run pytest tests/docs/test_2471_citation_scope.py -v`
- [ ] No regression: `uv run pytest tests/docs/` passes.
- [ ] Issue #2586 has an amendment-announcement comment.
- [ ] Issue #2587 has an amendment-announcement comment that explicitly raises the asset-management OPEN QUESTION.
- [ ] (Optional, deferred — see Open Questions) New GitHub issue opened for "decide asset-management wiki standards-page routing".
- [ ] Review artifacts posted to `scripts/review/results/2026-05-02-plan-W3-2471-erratum-{claude,codex,gemini}.md`.
- [ ] One commit per amended plan file (3 commits total: W1-A amendment, W1-B amendment, README + test).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | _pending_ | _to be filled after Step 4 of issue-planning-mode_ |
| Codex | _pending_ | _to be filled — may be SKIPPED per #2479 if regression unfixed_ |
| Gemini | _pending_ | _to be filled_ |

**Overall result:** _pending_

---

## Risks and Open Questions

- **Risk:** Amending committed plans confuses reviewers who rely on a static plan-as-of-merge contract. **Mitigation:** the amendment is an in-place EDIT (preserves git blame); each plan body retains an explicit provenance note ("Originally cited #2471 as path-sanction; corrected per W3-C erratum 2026-05-02 — actual sanction is local CLAUDE.md schema"). The original draft is recoverable from git history. The amendment's own commit will reference this W3-C plan in its message.
- **Risk:** The regression test's regex carve-out for legitimate acknowledgement language is fragile and could either false-positive on novel scope-correct phrasing or false-negative on a creative new over-citation. **Mitigation:** carve-out keys on a small fixed phrase set (`CSA-Z276-specific`, `CSA-only`, `does NOT generalize`, `scoped strictly`, `W3-C erratum`); evolutions require test update, which is a feature (forces reviewer attention).
- **Risk:** W1-B's asset-management routing is left as an OPEN QUESTION rather than resolved. Downstream W1-B implementation cannot proceed past path-placement decisions until the question is answered. **Mitigation:** the OPEN QUESTION blocks only Files-to-Change row finalisation; the rest of W1-B (concept-page scaffold, IAM Competency capture under `wiki/concepts/`, scope-boundary disclaimer) is unaffected.
- **Risk:** Future plans may continue to over-cite #2471 by paraphrase that the regex misses. **Mitigation:** the test catches the three highest-frequency surface forms observed in W1-A/W1-B; future audit cycles can extend the pattern set.
- **Open Question:** Should this plan also propose opening a new GitHub issue for "decide asset-management wiki standards-page routing"? **Recommendation: yes** — defer to user during approval. The new issue would be the formal sanction venue currently missing for asset-management; without it, W1-B's `wiki/standards/` placements are ungrounded. Suggested title: `feat(knowledge): sanction asset-management wiki standards-page routing (ISO 55000 family + IRMP standards)`. Suggested labels: `priority:medium`, `cat:documentation`, `domain:knowledge-management`, `domain:asset-integrity`.

---

## Complexity: T1

**T1** — surgical text edits to two committed plan files plus a minimal index-file update, one new ~30-line pytest, and two GitHub issue comments. No code paths affected. No wiki content touched. No new tooling. No standards work.
