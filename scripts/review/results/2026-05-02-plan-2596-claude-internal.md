# Adversarial Review — #2596 W3-C #2471 erratum plan (Claude internal)

**Plan:** `docs/plans/2026-05-02-issue-2596-llm-wiki-W3C-2471-erratum.md`
**Issue:** [#2596](https://github.com/vamseeachanta/workspace-hub/issues/2596)
**Reviewer:** Claude (adversarial, internal)
**Date:** 2026-05-02
**Verdict:** **MAJOR**

## Stance contract

Standard 7-clause adversarial stance. This is a META plan correcting other plans, so this review focuses on three high-leverage axes:

1. Faithfulness of the proposed amendments to actual memory + issue text.
2. Whether the proposed regression test prevents recurrence or is shape-only.
3. Whether the asset-management routing-scope conclusion is well-grounded.

---

## Verification of factual claims (quote vs. source)

### V1. Memory quote — partially faithful, ONE STALE STATEMENT

Plan L75-78 quotes `project_wiki_standards_path_decision.md`:

> The principle applies to: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope.
>
> **Workspace-hub #2471** is OPEN with title "feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract" — scoped **strictly to CSA Z276**, not the general substrate. Earlier framing in this memory described it as a general codification; that framing is stale.

Cross-checked against `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_standards_path_decision.md` lines 14, 19. **VERBATIM CORRECT.**

Plan parenthetical L79 acknowledges that #2471 is now CLOSED (memory says OPEN). Good defensive caveat.

### V2. #2471 actual scope — VERIFIED CSA-only

`gh issue view 2471 --json body` body Scope section:
> - Decide the canonical durable destination for **CSA Z276 pages**.
> - Update the relevant wiki schema/routing guidance if needed.
> - Specify git-tracking/durability expectations for the selected path.

The Why section also says "**CSA has a blocker family separate from OCIMF**". The acceptance-criteria first item is "sanctioned **CSA durable destination** is documented." There is no language authorizing routing for arbitrary publishers. Plan's central thesis — that #2471 is CSA-Z276-only — **is correct.**

### V3. W1-A over-citation count — CORRECT but framing slightly off

`grep -n "#2471\|2471 sanction\|2471-..." docs/plans/2026-05-02-issue-2586-...md` returned 5 matches at lines 9, 61, 73, 147, 225. The plan's classification:

| Line | Plan classification | Verified |
|---|---|---|
| L9 | OVER-CITATION (path-sanction in frontmatter) | YES |
| L61 | FACTUALLY WRONG ("now generalizes") | YES — text says exactly "principle now generalizes" — direct contradiction with memory |
| L73 | OK (statement of fact) | YES |
| L147 | OK (frontmatter, not path) | YES |
| L225 | OK (frontmatter required-key) | YES |

Plan's frontmatter says "5 distinct citations" and Files-to-Change says "5 distinct sources". Both are accurate. **OK.**

### V4. W1-B over-citation count — UNDERCOUNTED

Plan claims "11 distinct lines" at L18. Actual `grep` returns matches on lines: 25, 41, 57, 60, 84, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 254, 274. That's 17 matches. Excluding the legitimate frontmatter-contract refs (L41, L84, L254, L274) leaves **13 over-citation lines**. The "Per File" table at L143 acknowledges "13 distinct lines need amendment" — so the plan body is internally inconsistent (Resource Intel says 11; per-file table says 13). **MINOR-1.**

### V5. W2-A/B/C revision-cleanliness — W2-C IS NOT CLEAN

The plan claims at L19-21 that W2-A, W2-B, W2-C are "ALREADY revised" and provides the canonical replacement language. Verified for W2-A (`#2590`) at L10, L68, L292: now properly anchored to local CLAUDE.md schema. W2-B (`#2591`) at L13, L68: properly demoted. **W2-C (`#2592`) is NOT clean:**

- L66: `#2471 — CLOSED, "..." — sanctioned wiki/standards/<code-id>.md routing principle.` — same surface form as the W1-A/B over-citation
- L81: table header `| Page tier (per #2471) |` — uses #2471 as the categorization authority for arbitrary publishers
- L128: `#2471 — CLOSED — "..." — sanctions wiki/standards/<code-id>.md routing principle.` — repeated same form

These are exactly the pattern the plan flags as defective in W1-A/W1-B. The plan's "ALREADY revised" claim for W2-C is **wrong** — and worse, the proposed regression test would silently let W2-C continue to ship unchanged. **MAJOR-1: scope of erratum is too narrow** — must include W2-C in the amendment list, OR explicitly justify why W2-C's surface form is acceptable while W1-A/B's identical surface form is not.

### V6. Regression test efficacy — EASILY BYPASSED

The proposed offending_patterns:
1. `r"#2471.{0,80}generaliz"` — only catches the literal string "generaliz" within 80 chars
2. `r"#2471-sanctioned\s+`?wiki/standards/"` — requires the hyphenated form `#2471-sanctioned`
3. `r"#2471-routed\s+standards\s+page"` — requires the hyphenated row form

**Bypasses a contributor could write that pass all three:**
- "#2471 governs the canonical durable destination for all standards pages"
- "Per #2471, every code-identified page lives at `wiki/standards/<code-id>.md`"
- "Path-sanction: #2471"  (the exact W1-A L9 form — passes pattern 2 because the form is `#2471` not `#2471-sanctioned`)
- `| #2471 standards page |` (drop the hyphen-routed)
- "sanctioned `wiki/standards/<code-id>.md` routing principle" attributed to #2471 — exactly the W2-C form at L66, L128

Pattern 1 is also inverted — catching the literal "generaliz" only catches the rare honest-mistake form. The W1-A L61 string ("principle now generalizes") IS caught by pattern 1, but contributors writing fresh prose would more naturally say "applies broadly", "extends to", "covers all", etc.

**Test is shape-only.** It would pass on the W1-A L9 form (the very over-citation the plan is trying to eliminate). **MAJOR-2.**

A stronger contract: forbid any `#2471` reference outside an explicit allowlist of contexts. E.g., assert that every `#2471` mention either (a) appears within N lines of `CSA-Z276` / `CSA-only` / `does NOT generalize` / `scoped strictly` / `frontmatter` / `code_id` / `calc-citation-contract`, or (b) is a literal issue-title quote line. Inverting the polarity (allowlist instead of blocklist) is the durable shape.

### V7. Asset-management routing OPEN-QUESTION conclusion — INCORRECT

Plan claims the routing principle ({marine-engineering, engineering, naval-architecture}) excludes asset-management, so `wiki/standards/` placements in W1-B are ungrounded and should be flagged as OPEN QUESTION pending a separate sanction issue.

**The plan's resource intelligence missed the local CLAUDE.md.** `knowledge/wikis/asset-management/CLAUDE.md` (verified 2026-05-02):
- L11: `standards/  # Standards documents (API, DNV, ISO, etc.)` (raw)
- L23: `standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)` (wiki — this is the local sanction)
- L42-49: explicit "Standards page extra fields" section requiring `code_id`/`publisher`/`revision`

The asset-management wiki has its OWN local sanctioning authority for `wiki/standards/<code-id>.md` routing — same shape as engineering-standards. The directory `knowledge/wikis/asset-management/wiki/standards/` already exists.

The principle in memory is a workspace-wide statement; each wiki carries its own local CLAUDE.md sanction. The W1-A revisions (and the W2-A pattern) re-anchored to local CLAUDE.md schema precisely because that's the durable authority. The same logic applies to W1-B: re-anchor to `knowledge/wikis/asset-management/CLAUDE.md` directory schema, not flag as OPEN QUESTION.

The plan's Mitigation also creates a false constraint: it says "the rest of W1-B (concept-page scaffold, IAM Competency capture under wiki/concepts/, scope-boundary disclaimer) is unaffected" — but the OPEN-QUESTION framing actively blocks the 10 standards pages, which is the bulk of W1-B's scaffolding work. **MAJOR-3.**

The W1-B amendment should mirror the W1-A amendment exactly: re-anchor the path-sanction citations to `knowledge/wikis/asset-management/CLAUDE.md` directory schema + calc-citation-contract rule 2; the only legitimate caveat is that W1-B has no wave-2 organizational precedent yet (W2-A is engineering-standards-specific, not asset-management).

### V8. Forward-amendment vs history-rewrite — VERIFIED

Plan L129: "These edits AMEND files already on `main`. They are NOT a history rewrite. The original commits stand; the amendment is a NEW commit that changes the current file contents." Files-to-Change at L173-175 uses Modify (Edit), not overwrite. Top-of-file note added rather than rewriting. Git blame is preserved at the body level (only the changed lines re-blame to the amendment commit). **OK.**

### V9. Provenance-note intrusiveness — TOLERABLE

Plan adds a top-of-file W3-C provenance note to both W1-A and W1-B. This is mildly intrusive but improves auditability for future readers. The note is informative without being alarmist. **Minor concern only — kept as a minor since the alternative (silent edit) is worse.**

---

## Other findings

### MINOR-2: Regression test artifact path
Plan creates `tests/docs/test_2471_citation_scope.py`. Existing layout has `tests/knowledge/`, `tests/scripts/`, etc. — `tests/docs/` does not exist yet. Adding a new top-level test directory for one test is awkward; consider `tests/governance/` or `tests/plans/` if the intent is plan-file linting (closer to the artifact under test).

### MINOR-3: Three-commit decomposition is brittle
Acceptance-criteria L235 says "One commit per amended plan file (3 commits total: W1-A amendment, W1-B amendment, README + test)." But landing the test BEFORE the W1-A and W1-B amendments will fail the test (the over-citations still exist on main); landing it AFTER them in a separate commit creates a transient state where the regression-test commit's CI run may pass only because the prior commits already did the work. Suggest landing the test plus W1-A and W1-B amendments together in a single commit, or land test+W1-A+W1-B as one commit and the README index update as a second.

### MINOR-4: Regression test list does not include W2-C
The Acceptance Criteria has `test_w1a_amendment_landed` and `test_w1b_amendment_landed` but no `test_w2c_amendment_landed`. Coupled with MAJOR-1, the plan should either (a) add W2-C to the amendment list with its own `test_w2c_amendment_landed`, or (b) explicitly carve out W2-C in the test rationale.

### MINOR-5: Over-citation count drift between Resource Intel and Per-File table
L18 says "11 distinct lines" for W1-B; L143 Per-File table preamble says "13 distinct lines." Pick one and reconcile both numbers in the plan body.

### MINOR-6: Codex review may need to be skipped
Adversarial Review Summary at L244 acknowledges Codex may be SKIPPED per #2479 (sandbox stdin-hang). Memory feedback `feedback_codex_cli_0_124_upstream_regression.md` confirms this is still in effect. OK to defer, but the plan should make explicit which substitute (single-author r3? Gemini-only consensus?) covers the fallback path.

---

## Summary table

| Finding | Severity | Description |
|---|---|---|
| MAJOR-1 | MAJOR | W2-C (#2592) plan still has the same #2471-as-routing-principle over-citation pattern at L66, L81, L128 — plan claims W2-C is "ALREADY revised" and excludes it from the erratum scope. Erratum scope must include W2-C, or explicitly justify the asymmetry. |
| MAJOR-2 | MAJOR | Regression test regex is shape-only — easily bypassed by paraphrase ("#2471 governs...", "Per #2471, every code-identified page..."). Polarity should invert from blocklist to allowlist (forbid #2471 references outside explicit acknowledgement contexts). |
| MAJOR-3 | MAJOR | Asset-management OPEN-QUESTION framing is ungrounded — `knowledge/wikis/asset-management/CLAUDE.md` already sanctions `wiki/standards/<code-id>.md` routing locally with the same `code_id`/`publisher`/`revision` schema. Plan missed this local sanction in resource intelligence and creates a false blocker for W1-B's 10 standards pages. |
| MINOR-1 | MINOR | Internal inconsistency: Resource Intel says W1-B has 11 over-citation lines; Per-File table says 13. |
| MINOR-2 | MINOR | New test path `tests/docs/` is a one-test directory; consider `tests/governance/` or `tests/plans/`. |
| MINOR-3 | MINOR | 3-commit decomposition can produce a transient state where the regression test passes for the wrong reason. |
| MINOR-4 | MINOR | TDD list lacks `test_w2c_amendment_landed`; coupled with MAJOR-1. |
| MINOR-5 | MINOR | Over-citation count drift (11 vs 13). |
| MINOR-6 | MINOR | Codex-skipped fallback path (single-author r3 vs. Gemini-only) not specified. |

---

## Recommendation

**MAJOR.** The plan's central thesis is correct (#2471 is CSA-Z276-only, W1-A and W1-B over-cite it as a generalized path-sanction). But three load-bearing claims are incorrect:

1. W2-C is NOT already clean — three lines remain to be amended
2. The regression test is too weak to prevent recurrence
3. Asset-management has its own local sanction; W1-B does not need an OPEN QUESTION

These are not paper cuts — each one would let the same defect reappear in a future wave. The plan should be revised before approval.

The forward-amendment mechanism (in-place Edit + provenance note) is sound. The verbatim-quote handling is faithful. The CSA-Z276-scope thesis is verified. So the corrections are tractable: extend the scope to W2-C, invert the regression-test polarity, replace W1-B's OPEN-QUESTION framing with the same local-CLAUDE.md re-anchor pattern as W1-A.

---

## Verdict

**MAJOR_COUNT: 3**
**MINOR_COUNT: 6**
