# Plan for LLM-Wiki Completeness W3-C: #2471 Sanction-Scope Erratum (Forward-Amend W1-A, W1-B, and W2-C)

> **Status:** plan-review (revised after r1 review)
> **Complexity:** T1
> **Date:** 2026-05-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2596
> **Parent epic:** [#2540](https://github.com/vamseeachanta/workspace-hub/issues/2540) — overnight Elements corpus planning wave
> **Trigger:** W2 adversarial-review wave (#2590 / #2591 / #2592) surfaced a systemic over-citation of [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) as a generalized path-sanction; same defect persists in already-committed W1-A (#2586) and W1-B (#2587) plans on `main`, and (per r1 review of this erratum, MAJOR-1) three residual lines of W2-C (#2592) also exhibit the same surface form.
> **Review artifacts:** scripts/review/results/2026-05-02-plan-2596-claude-internal.md | Codex UNAVAILABLE (codex-cli 0.124.0 stdin-hang #2479) | Gemini UNAVAILABLE (sandbox path resolution failure)

---

## Resource Intelligence Summary

### Existing repo code

- `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` — W1-A plan (engineering-standards/API). Currently on `main` at `status:plan-review`. Cites #2471 as a path-sanction in its frontmatter and Files-to-Change rationale (5 distinct citations).
- `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` — W1-B plan (asset-management). Currently on `main` at `status:plan-review`. Cites #2471 as a path-sanction in 13 distinct lines (corrected per r1 review MINOR-1/MINOR-5; earlier "11" framing was incorrect), all routing asset-management standards pages under `wiki/standards/`.
- `docs/plans/2026-05-02-issue-2590-llm-wiki-W2A-engineering-standards-dnv.md` — W2-A; ALREADY revised in W2 commit; provides the canonical replacement language pattern (line 10 "Path sanction (DNV)" header anchors to engineering-standards `CLAUDE.md` schema + calc-citation-contract rule 2 + #2586 organizational precedent; #2471 demoted to historical-origin-of-frontmatter-triple footnote).
- `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md` — W2-B; ALREADY revised; line 9 "Path sanction (re-anchored after r1 review)" pattern.
- `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` — W2-C; **partially revised** in W2 commit (flagged maritime-law as out-of-principle-scope, defaulted concept-page placement to `wiki/concepts/`), **but three lines retain the same #2471-as-routing-principle over-citation pattern** (L66, L81, L128 — see Evidence). Per r1 review (MAJOR-1), W2-C is included in this erratum's amendment list.
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

**Local sanction for W1-B (corrected per r1 review MAJOR-3):** the asset-management wiki carries its OWN local sanctioning authority for `wiki/standards/<code-id>.md` routing. `knowledge/wikis/asset-management/CLAUDE.md` (verified 2026-05-02):
- L11: `standards/  # Standards documents (API, DNV, ISO, etc.)` (raw)
- L23: `standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)` (wiki — local sanction)
- L42-49: explicit "Standards page extra fields" section requiring `code_id`/`publisher`/`revision`

The directory `knowledge/wikis/asset-management/wiki/standards/` already exists. The workspace-wide memory principle ({marine-engineering, engineering, naval-architecture}) applies at the principle level, but each wiki carries its own local CLAUDE.md sanction; W1-A's revision pattern re-anchored to local CLAUDE.md schema precisely because that's the durable authority. **The same logic applies to W1-B**: re-anchor to `knowledge/wikis/asset-management/CLAUDE.md` directory schema + calc-citation-contract rule 2; no OPEN QUESTION is required.

**W2-C residual over-citations (per r1 review MAJOR-1):**
- L66: `#2471 — CLOSED, "..." — sanctioned wiki/standards/<code-id>.md routing principle.` ← OVER-CITATION (same surface form as W1-A/W1-B)
- L81: `| Page tier (per #2471) |` ← OVER-CITATION (uses #2471 as categorization authority for arbitrary publishers)
- L128: `#2471 — CLOSED — "..." — sanctions wiki/standards/<code-id>.md routing principle.` ← OVER-CITATION

These three lines must be amended in the same pass; otherwise the erratum scope is internally inconsistent (would let W2-C ship with the very pattern the plan flags as defective).

**Asset-management `wiki/standards/<code-id>.md` line count (corrected per r1 review MINOR-1, MINOR-5):** the `grep` returns 17 matches at lines 25, 41, 57, 60, 84, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 254, 274. Excluding the legitimate frontmatter-contract refs (L41, L84, L254, L274) leaves **13 over-citation lines** in W1-B. The earlier "11 distinct lines" framing was incorrect; both the Resource-Intel paragraph and Per-File table now consistently report 13.

Source count: **6 distinct sources** consulted (issue body of #2471; calc-citation-contract.md rule 2; project_wiki_standards_path_decision.md memory; W1-A plan file; W1-B plan file; **`knowledge/wikis/asset-management/CLAUDE.md`** local schema added per r1 review) — exceeds 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-02-issue-2596-llm-wiki-W3C-2471-erratum.md` |
| Tests | `tests/governance/test_2471_citation_scope.py` (per r1 review MINOR-2 — co-located with other governance/plan-linting tests) |
| Plan to amend (W1-A) | `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` |
| Plan to amend (W1-B) | `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` |
| Plan to amend (W2-C) | `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` (added per r1 review MAJOR-1) |
| Plan index update | `docs/plans/README.md` |
| Plan review — Claude (internal r1) | `scripts/review/results/2026-05-02-plan-2596-claude-internal.md` |
| Plan review — Codex | UNAVAILABLE — codex-cli 0.124.0 stdin-hang regression (#2479) |
| Plan review — Gemini | UNAVAILABLE — gemini sandbox path resolution failure |

---

## Deliverable

A trio of forward-amendment commits to W1-A (#2586), W1-B (#2587), and W2-C (#2592) plan files that re-anchor every #2471 path-sanction citation to the correct local authority (engineering-standards `CLAUDE.md` directory schema for W1-A; **asset-management `CLAUDE.md` directory schema for W1-B** per r1 review MAJOR-3; concept-page reanchor for W2-C per r1 review MAJOR-1), preserving git blame via in-place edits and adding a minimal regression test (with **inverted allowlist polarity** per r1 review MAJOR-2) that future plans cannot reintroduce the same over-citation.

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

**Per r1 review MAJOR-3 (verbatim recommended fix):** "The W1-B amendment should mirror the W1-A amendment exactly: re-anchor the path-sanction citations to `knowledge/wikis/asset-management/CLAUDE.md` directory schema + calc-citation-contract rule 2; the only legitimate caveat is that W1-B has no wave-2 organizational precedent yet (W2-A is engineering-standards-specific, not asset-management)."

W1-B has 13 distinct over-citation lines (corrected per r1 MINOR-1/MINOR-5). The asset-management wiki carries its OWN local sanctioning authority for `wiki/standards/<code-id>.md` routing via `knowledge/wikis/asset-management/CLAUDE.md` L23 + L42-49, so the path placements are NOT ungrounded — they are sanctioned at the local-CLAUDE.md level, identical in shape to the engineering-standards wiki sanction. No OPEN QUESTION is required.

| Line | Current | Proposed (mirrors W1-A pattern) |
|---|---|---|
| L25 (Standards table — ISO 55000 row) | `Will be added under \`wiki/standards/iso-55000.md\` … per #2471-sanctioned \`wiki/standards/<code-id>.md\` routing.` | `Will be added under \`wiki/standards/iso-55000.md\` per local sanctioning authority \`knowledge/wikis/asset-management/CLAUDE.md\` directory schema (defines \`wiki/standards/<code-id>.md\` routing for the asset-management wiki; L23 + L42-49). Frontmatter contract per \`.claude/rules/calc-citation-contract.md\` rule 2 (\`code_id\`/\`publisher\`/\`revision\`). [#2471](...) is CSA-Z276-specific per memory \`project_wiki_standards_path_decision.md\` and does NOT generalize as a path-routing rule; cited here only as the historical origin of the frontmatter triple. (Amended 2026-05-02 per W3-C erratum.)` |
| L57 (load-bearing rules) | `\`wiki/standards/\` routing rule (#2471) — both load-bearing.` | `local \`wiki/standards/<code-id>.md\` routing per \`knowledge/wikis/asset-management/CLAUDE.md\` directory schema + frontmatter contract (#2471 — origin of \`code_id\`/\`publisher\`/\`revision\` triple) — both load-bearing. (Amended 2026-05-02 per W3-C erratum: removed the false claim that #2471 is the routing-rule sanction; #2471 is CSA-Z276-specific.)` |
| L60 (issue summary) | `Issue **#2471** (CLOSED) — sanctioned \`wiki/standards/<code-id>.md\` routing for code-identified pages…` | `Issue **#2471** (CLOSED) — sanctioned the \`code_id\`/\`publisher\`/\`revision\` frontmatter triple via the calc-citation-contract; the path-routing decision was scoped strictly to CSA-Z276 per memory \`project_wiki_standards_path_decision.md\`. The \`wiki/standards/<code-id>.md\` routing for the asset-management wiki is sanctioned locally via \`knowledge/wikis/asset-management/CLAUDE.md\` directory schema. (Corrected 2026-05-02 per W3-C erratum.)` |
| L220-229 (Files-to-Change rows — 10 standards pages) | `Create \| knowledge/wikis/asset-management/wiki/standards/<code>.md \| #2471-routed standards page` (×10) | Each row's "Reason" column changed to `Standards page (path placement per \`knowledge/wikis/asset-management/CLAUDE.md\` directory schema; frontmatter contract per \`.claude/rules/calc-citation-contract.md\` rule 2 — \`code_id\`/\`publisher\`/\`revision\`).` |
| L41 (`under #2471 contract`) | unchanged | (NO CHANGE — refers to frontmatter-contract scope.) |
| L84, L254, L274 | unchanged | (NO CHANGE — refer to frontmatter triple, which is correctly sanctioned by calc-citation-contract rule 2.) |
| Top-of-file note | none | `> _This plan was amended on 2026-05-02 (W3-C erratum). Original draft cited #2471 as a generalized path-sanction for asset-management standards pages. Per memory \`project_wiki_standards_path_decision.md\`, #2471 is scoped strictly to CSA-Z276; the asset-management wiki's own local sanctioning authority is \`knowledge/wikis/asset-management/CLAUDE.md\` directory schema (L23 + L42-49). Path-sanction citations have been re-anchored to that local authority + calc-citation-contract rule 2; frontmatter-contract citations to #2471 are unchanged._` |

### W2-C (`docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md`) — added per r1 review MAJOR-1

W2-C was partially revised in the W2 commit (concept-page placement defaulted to `wiki/concepts/` for maritime-law), but three lines retain the same surface form the plan flags as defective. These must be amended in this same erratum.

| Line | Current | Proposed |
|---|---|---|
| L66 (sources) | `#2471 — CLOSED, "..." — sanctioned \`wiki/standards/<code-id>.md\` routing principle.` | `#2471 — CLOSED, "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — sanctioned \`wiki/standards/<code-id>.md\` routing **for CSA-Z276 specifically** per memory \`project_wiki_standards_path_decision.md\`; **does NOT generalize** to maritime-law publishers (IMO/ILO). Cited here only as historical origin of the \`code_id\`/\`publisher\`/\`revision\` frontmatter triple via the calc-citation-contract. (Amended 2026-05-02 per W3-C erratum.)` |
| L81 (table header) | `\| Page tier (per #2471) \|` | `\| Page tier (per local wiki schema; #2471 NOT applicable — CSA-Z276-specific) \|` |
| L128 (sources, repeated) | `#2471 — CLOSED — "..." — sanctions \`wiki/standards/<code-id>.md\` routing principle.` | `#2471 — CLOSED — "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — sanctions the path-routing decision **for CSA-Z276 specifically**; the principle does NOT generalize across publishers. (Amended 2026-05-02 per W3-C erratum.)` |
| Top-of-file note | none | `> _This plan was amended on 2026-05-02 (W3-C erratum). Three residual lines (L66/L81/L128) used #2471 as a generalized routing-principle citation; #2471 is CSA-Z276-specific per memory \`project_wiki_standards_path_decision.md\`. Maritime-law concept-page placement under \`wiki/concepts/\` is unchanged._` |

### `docs/plans/README.md`

Add a Note suffix to the existing rows for #2586, #2587, and #2592:
- 2586 row: append `; amended 2026-05-02 per W3-C erratum (#2471 path-sanction over-citation corrected; frontmatter citations unchanged).`
- 2587 row: append `; amended 2026-05-02 per W3-C erratum (#2471 path-sanction citations re-anchored to local \`knowledge/wikis/asset-management/CLAUDE.md\` directory schema; frontmatter citations unchanged).`
- 2592 row: append `; amended 2026-05-02 per W3-C erratum (3 residual #2471 generalization lines at L66/L81/L128 corrected; concept-page placement unchanged).`

Add a new W3-C row in the appropriate date-sorted position with note: `Erratum plan retro-correcting systemic #2471 path-sanction over-citation in W1-A, W1-B, and W2-C; minimal allowlist-polarity regression test under \`tests/governance/test_2471_citation_scope.py\`.`

### Issue comments

Post a single comment to each of #2586, #2587, and #2592 with text:
> Plan amended 2026-05-02 per W3-C erratum (`docs/plans/2026-05-02-issue-2596-llm-wiki-W3C-2471-erratum.md`). Original draft over-cited #2471 as a generalized path-sanction; #2471 is scoped strictly to CSA-Z276 per memory `project_wiki_standards_path_decision.md`. Frontmatter-contract citations to #2471 remain valid (per `.claude/rules/calc-citation-contract.md` rule 2). [Asset-management-specific addendum for #2587:] path-sanction citations have been re-anchored to the local sanctioning authority `knowledge/wikis/asset-management/CLAUDE.md` directory schema (L23 + L42-49); no OPEN QUESTION required. [W2-C addendum for #2592:] three residual lines (L66/L81/L128) cited #2471 as the routing-principle authority; corrected to scope-explicit phrasing.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `docs/plans/2026-05-02-issue-2586-llm-wiki-W1A-engineering-standards-api.md` | Forward-amend #2471 path-sanction over-citations to local CLAUDE.md schema + calc-citation-contract rule 2; add top-of-file W3-C provenance note. |
| Modify | `docs/plans/2026-05-02-issue-2587-llm-wiki-W1B-asset-management-audit.md` | Same as W1-A pattern, re-anchored to `knowledge/wikis/asset-management/CLAUDE.md` directory schema (per r1 review MAJOR-3 — local sanctioning authority exists; no OPEN QUESTION needed). |
| Modify | `docs/plans/2026-05-02-issue-2592-llm-wiki-W2C-maritime-law-expansion.md` | Forward-amend 3 residual over-citation lines (L66/L81/L128) to scope-explicit phrasing (per r1 review MAJOR-1 — these lines retain the same defective surface form W1-A/B exhibit). |
| Modify | `docs/plans/README.md` | Append amendment notes to #2586, #2587, #2592 rows; add W3-C row. |
| Create | `tests/governance/test_2471_citation_scope.py` | Regression test enforcing #2471-citation allowlist (per r1 review MAJOR-2 — inverted polarity from blocklist to allowlist) across all `docs/plans/2026-05-02-*.md`. Path under `tests/governance/` per r1 review MINOR-2 (closer to artifact under test than `tests/docs/`). |
| Comment | GitHub issue #2586 | Announce amendment with link to W3-C plan. |
| Comment | GitHub issue #2587 | Announce amendment with re-anchored local-CLAUDE.md sanction. |
| Comment | GitHub issue #2592 | Announce W2-C residual-line amendment. |

---

## Pseudocode

T1 — trivial. See "Forward-Amendment Plan" table above for exact replacement language.

The only non-trivial artifact is the regression test. Per r1 review MAJOR-2 (verbatim recommended fix): "A stronger contract: forbid any `#2471` reference outside an explicit allowlist of contexts. E.g., assert that every `#2471` mention either (a) appears within N lines of `CSA-Z276` / `CSA-only` / `does NOT generalize` / `scoped strictly` / `frontmatter` / `code_id` / `calc-citation-contract`, or (b) is a literal issue-title quote line. Inverting the polarity (allowlist instead of blocklist) is the durable shape."

```
function test_2471_citation_scope():
    glob plans = docs/plans/2026-05-02-*.md
    ALLOWLIST_TOKENS = [
        "CSA-Z276",                     # explicit CSA scope
        "CSA-only",                     # explicit CSA scope
        "CSA Z276",                     # space variant
        "does NOT generalize",          # explicit non-generalization
        "scoped strictly",              # explicit scope statement
        "frontmatter",                  # frontmatter-only reference
        "code_id",                      # frontmatter triple field
        "publisher",                    # frontmatter triple field
        "revision",                     # frontmatter triple field
        "calc-citation-contract",       # rule-2 origin reference
        "historical origin",            # demoted-to-history phrasing
        "W3-C erratum",                 # provenance note
        "feat(knowledge): decide sanctioned CSA Z276",  # literal issue title
    ]
    PROXIMITY_LINES = 3   # within N lines of #2471 mention
    for each plan_path in plans:
        lines = read_lines(plan_path)
        for i, line in enumerate(lines):
            if "#2471" not in line:
                continue
            # Build proximity window (this line ± PROXIMITY_LINES).
            window = lines[max(0, i-PROXIMITY_LINES):i+PROXIMITY_LINES+1]
            window_text = "\n".join(window)
            # ALLOW if any allowlist token appears in the proximity window.
            if any(token in window_text for token in ALLOWLIST_TOKENS):
                continue
            # ALLOW if the line is a literal hyperlink-only mention with no claim.
            if is_bare_link_only(line):  # matches `[#2471](url)` with no path/sanction prose nearby
                continue
            FAIL: f"Bare #2471 reference at {plan_path}:{i+1} — must include scope token within ±{PROXIMITY_LINES} lines (CSA-Z276 / frontmatter / code_id / calc-citation-contract / etc.) or be a literal issue-title quote."
```

This allowlist polarity catches all the bypasses the r1 review identified:
- "#2471 governs the canonical durable destination for all standards pages" → FAIL (no allowlist token nearby)
- "Per #2471, every code-identified page lives at `wiki/standards/<code-id>.md`" → FAIL (no allowlist token nearby unless `code_id` matches; "code-identified" does not match `code_id` substring; verified the test would catch this; if `code_id` substring incidentally matches in a future variant, the test author should add stricter delimiters)
- "Path-sanction: #2471" → FAIL (no allowlist token nearby)
- `| #2471 standards page |` → FAIL (no allowlist token nearby)
- "sanctioned `wiki/standards/<code-id>.md` routing principle" attributed to #2471 (W2-C L66/L128 form) → FAIL (no scope token nearby)

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_2471_citation_scope_allowlist` | Every `#2471` mention in `docs/plans/2026-05-02-*.md` has an allowlist scope token within ±3 lines (allowlist polarity per r1 MAJOR-2) | All `docs/plans/2026-05-02-*.md` files | All `#2471` mentions pass the allowlist proximity check; offending lines listed in failure message with file:line and the surrounding window |
| `test_w1a_amendment_landed` | W1-A plan contains the W3-C provenance note + local-CLAUDE.md re-anchor | `docs/plans/2026-05-02-issue-2586-...md` | Substring `W3-C erratum` AND `engineering-standards/CLAUDE.md` present |
| `test_w1b_amendment_landed` | W1-B plan contains the W3-C provenance note + local-CLAUDE.md re-anchor (per r1 MAJOR-3 — replaces former OPEN-QUESTION assertion) | `docs/plans/2026-05-02-issue-2587-...md` | Substring `W3-C erratum` AND `knowledge/wikis/asset-management/CLAUDE.md` present |
| `test_w2c_amendment_landed` | W2-C plan contains the W3-C provenance note and the 3 residual lines (L66/L81/L128) no longer cite #2471 as a generalized routing principle (per r1 MAJOR-1 + MINOR-4) | `docs/plans/2026-05-02-issue-2592-...md` | Substring `W3-C erratum` present AND no occurrence of `sanctioned \`wiki/standards/<code-id>.md\` routing principle.` immediately after `#2471` |
| `test_allowlist_proximity_works` | Allowlist proximity logic doesn't false-positive on legitimate scope-acknowledgement language | Synthetic input with phrase "#2471 is CSA-Z276-specific and does NOT generalize" | Test passes (allowlist token within proximity window) |
| `test_allowlist_catches_bypass_paraphrases` | Allowlist polarity catches the r1-review-identified bypass forms | Synthetic inputs: "#2471 governs the canonical durable destination", "Path-sanction: #2471" with no scope tokens nearby | Test FAILS (caught) |

---

## Acceptance Criteria

- [ ] W1-A plan amended in-place; git blame preserved; top-of-file W3-C note added.
- [ ] W1-B plan amended in-place; path-sanction citations re-anchored to `knowledge/wikis/asset-management/CLAUDE.md` directory schema (per r1 review MAJOR-3); top-of-file W3-C note added.
- [ ] W2-C plan amended in-place: 3 residual lines (L66/L81/L128) corrected to scope-explicit phrasing (per r1 review MAJOR-1); top-of-file W3-C note added.
- [ ] `docs/plans/README.md` updated with amendment notes on rows for #2586, #2587, #2592, and new W3-C row added.
- [ ] `tests/governance/test_2471_citation_scope.py` created (per r1 review MINOR-2 — `tests/governance/` co-locates with other plan-linting tests) and passes: `uv run pytest tests/governance/test_2471_citation_scope.py -v`
- [ ] No regression: `uv run pytest tests/governance/` passes.
- [ ] Issue #2586 has an amendment-announcement comment.
- [ ] Issue #2587 has an amendment-announcement comment with the local-CLAUDE.md sanction reference.
- [ ] Issue #2592 has an amendment-announcement comment for the 3 residual-line fix.
- [ ] Review artifact posted to `scripts/review/results/2026-05-02-plan-2596-claude-internal.md` (single-author Claude internal r1 — Codex unavailable per #2479; Gemini sandbox path resolution failure).
- [ ] **Commit decomposition (per r1 review MINOR-3 — corrected to avoid transient regression-pass-for-wrong-reason):** ONE commit lands the test alongside the 3 plan amendments (test will fail without the amendments; passes only after amendments are in the same tree). A SECOND commit lands the README index update.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (internal) | MAJOR → revised | 3 MAJOR + 6 MINOR — all addressed inline |
| Codex | UNAVAILABLE | codex-cli 0.124.0 stdin-hang regression (#2479) |
| Gemini | UNAVAILABLE | gemini sandbox path resolution failure |

**Overall result:** PASS-after-revision (3 MAJOR + 6 MINOR fixes applied 2026-05-02)

**Revisions made based on review:**
- MAJOR-1: Extended erratum scope to include W2-C (#2592); added L66/L81/L128 amendment table; added `test_w2c_amendment_landed` to TDD list and acceptance criteria.
- MAJOR-2: Inverted regression-test polarity from blocklist to allowlist (proximity-based scope-token check around every `#2471` mention); added explicit bypass-form coverage and a new `test_allowlist_catches_bypass_paraphrases` test.
- MAJOR-3: Replaced W1-B OPEN-QUESTION framing with local-CLAUDE.md re-anchor (`knowledge/wikis/asset-management/CLAUDE.md` L23 + L42-49 sanctions `wiki/standards/<code-id>.md` routing locally); removed false blocker for W1-B's 10 standards pages.
- MINOR-1 + MINOR-5: Reconciled over-citation count to 13 in both Resource-Intel paragraph and Per-File table preamble.
- MINOR-2: Moved test to `tests/governance/test_2471_citation_scope.py` (co-located with other plan-linting tests).
- MINOR-3: Corrected commit decomposition to one commit for test+amendments, second for README — avoids transient state where test passes for wrong reason.
- MINOR-4: Added `test_w2c_amendment_landed` paired with MAJOR-1 scope extension.
- MINOR-6: Made fallback-path explicit (single-author Claude internal r1 per memory `feedback_permission_gate_blocks_cross_review.md`).

**Provenance:** Single-author Claude review per memory `feedback_permission_gate_blocks_cross_review.md`. Round 1.

---

## Risks and Open Questions

- **Risk:** Amending committed plans confuses reviewers who rely on a static plan-as-of-merge contract. **Mitigation:** the amendment is an in-place EDIT (preserves git blame); each plan body retains an explicit provenance note ("Originally cited #2471 as path-sanction; corrected per W3-C erratum 2026-05-02 — actual sanction is local CLAUDE.md schema"). The original draft is recoverable from git history. The amendment's own commit will reference this W3-C plan in its message.
- **Risk:** The regression test's allowlist proximity check could false-positive on novel scope-correct phrasing that uses synonyms outside the token list, or false-negative on a creative new over-citation that incidentally has a token in the proximity window. **Mitigation:** allowlist token set is fixed and conservative (CSA-Z276, frontmatter, code_id, calc-citation-contract, etc.); the proximity window is small (±3 lines); evolutions require test update which is a feature (forces reviewer attention). The polarity inversion (per r1 review MAJOR-2) catches the bypass forms the original blocklist would have missed: bare `#2471` references, paraphrases like "governs the canonical durable destination", and the W2-C `routing principle` form.
- **Risk:** Future plans may continue to over-cite #2471 by paraphrase that the allowlist misses. **Mitigation:** the test now uses a polarity that requires opt-in scope-context, not opt-out blocklist matching; any bare `#2471` mention without a scope token within ±3 lines fails — this is the durable shape per r1 review MAJOR-2.
- **(Resolved per r1 review MAJOR-3)** Earlier framing flagged W1-B's asset-management `wiki/standards/` placements as ungrounded. This was incorrect: `knowledge/wikis/asset-management/CLAUDE.md` (L23 + L42-49) sanctions the routing locally with the same `code_id`/`publisher`/`revision` schema. W1-B is now re-anchored to that local authority; the OPEN QUESTION is closed and no follow-up sanction issue is required. **Open Question (residual, deferred):** the workspace-wide memory principle in `project_wiki_standards_path_decision.md` could optionally be expanded from {marine-engineering, engineering, naval-architecture} to enumerate asset-management explicitly — this is a memory-update follow-up, not a blocker for W1-B implementation. Defer to user during approval.

---

## Complexity: T1

**T1** — surgical text edits to three committed plan files (W1-A, W1-B, W2-C) plus a minimal index-file update, one new ~50-line pytest with allowlist-polarity proximity check (per r1 review MAJOR-2), and three GitHub issue comments. No code paths affected. No wiki content touched. No new tooling. No standards work.
