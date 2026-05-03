# Adversarial Review — Plan #2613 (W5-D Standards Routing Sanction META)

- **Plan path:** `docs/plans/2026-05-03-issue-2613-llm-wiki-W5D-standards-routing-sanction.md`
- **Issue:** [#2613](https://github.com/vamseeachanta/workspace-hub/issues/2613) (OPEN)
- **Reviewer:** Claude (adversarial, internal r1)
- **Stance:** 7-clause defect-hunting
- **Date:** 2026-05-03
- **Verdict:** **MINOR**
- **MAJOR_COUNT:** 0
- **MINOR_COUNT:** 4

---

## Verification Performed

### 1. Allowlist regression test (`test_2471_citation_scope.py`)

```
$ uv run pytest tests/governance/test_2471_citation_scope.py 2>&1 | tail -3
tests/governance/test_2471_citation_scope.py ......                      [100%]
============================== 6 passed in 0.29s ===============================
```

**6/6 passed.** No allowlist regression. The plan does not over-cite #2471. Plan-relative scope clauses ("Workspace-hub #2471", "scoped strictly to CSA Z276", etc.) sit inside the allowlist proximity windows.

### 2. Per-wiki decision matrix accuracy

| Plan claim | Verification | Result |
|---|---|---|
| asset-management/CLAUDE.md L23 + L42-49 declares `wiki/standards/` schema | Read confirms L23 lists `standards/` in directory tree; L42-49 defines "Standards page extra fields" with `code_id`/`publisher`/`revision`/`jurisdiction`/`supersedes` | **VERIFIED** |
| marine-engineering/CLAUDE.md declares `wiki/standards/` | L23 confirms `standards/  # Standards pages (publisher-agnostic; code_id, publisher, revision required)` | **VERIFIED** |
| `knowledge/wikis/marine-engineering/wiki/standards/` missing on disk | `ls` confirms only `comparisons concepts entities index.md log.md overview.md sources visualizations` — **no `standards/`** | **VERIFIED** |
| maritime-law/CLAUDE.md does NOT declare `wiki/standards/` | Read confirms — defers to marine-engineering schema; explicit "Domain Scope" maritime-law-only with no standards subdir | **VERIFIED** |
| lng-projects/CLAUDE.md exists | `ls` confirms `CLAUDE.md`, `raw`, `wiki` subdirs | **VERIFIED** |
| All 10 wikis enumerated in matrix | `ls knowledge/wikis/` returns 10 entries: acma-projects, asset-management, engineering, engineering-standards, health-reports, lng-projects, marine-engineering, maritime-law, naval-architecture, personal | **VERIFIED** (matrix exhaustive) |

### 3. Memory text verbatim quotation

**Memory L14:** `The principle applies to: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope.`

**Plan L89:** `> The principle applies to: marine-engineering, engineering, naval-architecture. Maritime-law, personal, health-reports are out of scope.`

**Match: VERBATIM.** Plan correctly quotes the load-bearing scope clause.

### 4. META status confirmation

- Plan modifies NO files: confirmed by absence of changeset; "Files to Change" table explicitly tags every row with `(umbrella issue authorizes)` or `(this plan does NOT authorize)`.
- Plan opens NO issue: confirmed; L10 explicitly states "No GitHub issue will be created, no commit will land, no wiki will be modified by this plan."
- The actual GitHub issue #2613 IS created (verified via `gh issue view 2613`) — but it is the issue THIS plan addresses, not an issue this plan creates. The umbrella sanction issue is the proposed downstream artifact.

**META status: CONFIRMED.**

---

## Findings

### MINOR-1: Pseudocode/Acceptance contradiction on test enforcement mode

**Where:** L153-154 (Pseudocode comment) vs. L255 (Open Question recommendation).

**Defect:** The pseudocode comment block reads "the test is added in disabled / xfail mode in this plan and only becomes enforcing after the umbrella sanction issue lands the codifying CLAUDE.md edits." But the Open Question §"test enforcement timing" recommends "hard-enforcing — the umbrella sanction issue lands BOTH the CLAUDE.md edits AND the test in the same PR, so the test cannot fail spuriously." These are mutually exclusive design statements within the same plan.

**Impact:** A reviewer scanning the pseudocode will draft the test in xfail mode; a reviewer scanning the Open Questions will draft it as hard-enforcing. The downstream umbrella-issue implementer will land one of the two and fail to satisfy the other reading of the plan. Neither is wrong, but the plan must commit.

**Fix:** Update the pseudocode comment to reflect the recommendation (hard-enforcing landed atomically with CLAUDE.md edits). Or, equivalently, soften the Open-Question recommendation to "if the umbrella PR cannot land both atomically, fall back to xfail; otherwise hard-enforce." Pick one.

---

### MINOR-2: Test pseudocode requires the umbrella issue number to be hardcoded into the test before umbrella-issue creation — chicken/egg risk reframed

**Where:** L155-159 (`SANCTIONED_VIA_ISSUE = {"engineering-standards": "<umbrella-issue-number>", ...}`) and L173-176 (`if not has_proximate_token(plan_path, match, f"#{SANCTIONED_VIA_ISSUE[wiki]}"):`).

**Defect:** The test enforces a specific issue number (umbrella-issue-number), not a generic "any sanction-issue citation". This means the test cannot be written until the umbrella issue exists, AND the test cannot tolerate later policy migration to a different sanction issue without re-edit. The plan's "Risks and Open Questions" L250 acknowledges the chicken-and-egg ordering for CLAUDE.md "Sanctioned-by" references but does not flag the same problem in the test extension. The test inherits the same ordering constraint AND adds a brittleness multiplier (every later sanction migration requires test edit).

**Impact:** Low operational risk because the umbrella issue's PR can land both the issue-number-aware test extension and the CLAUDE.md edits atomically. But it IS a "shape-only" criticism for the test as drafted in this plan: the pseudocode hard-codes a sentinel `<umbrella-issue-number>` placeholder that any reviewer will read as "this is shape-only until issue creation." That is correct, but the plan should explicitly acknowledge this is a placeholder, not a contract.

**Fix options:**
1. Document the placeholder explicitly in the pseudocode comment.
2. Generalize the contract to "any plan citing `wiki/standards/` for a non-principle wiki must include some `#<NNNN>` reference within ±5 lines AND that issue's title must contain `sanction` per a one-time `gh issue view` lookup at test time" — too brittle for unit tests.
3. Easier: enforce only "any `#<NNNN>` reference within ±5 lines" — accept ANY sanction citation, not the specific umbrella one. The provenance trail is then human-curated rather than test-enforced.

Option 3 is the cleanest. The test becomes shape-only on the issue-number axis but still catches the high-value defect (out-of-principle wiki cited without ANY sanction-issue context).

---

### MINOR-3: Per-wiki vs umbrella recommendation has a subtle bundling problem

**Where:** L246, L251 ("Risk: proliferation of sanction issues" + "Open Question: ONE umbrella sanction issue").

**Defect:** The plan recommends ONE umbrella issue covering {engineering-standards, asset-management} (codify) PLUS {lng-projects, acma-projects} (user-decision-required) PLUS reaffirmation of {maritime-law, personal, health-reports}. That bundles two qualitatively distinct decision types:

- **Codify** (engineering-standards, asset-management) — already W3-C-re-anchored, decision is rubber-stamping.
- **User-decision** (lng-projects, acma-projects) — auto-init schema, no precedent, requires de-novo user assent.

If the user assents to umbrella-as-recommended and later wants to reverse the lng-projects/acma-projects decision, the umbrella-issue audit trail conflates "we decided lng-projects in" with "we decided engineering-standards in" as one act of approval. Per-wiki issues would preserve granular audit trail.

The plan acknowledges this at L246 as a mitigation ("per-wiki granularity is recoverable later via in-issue checkboxes") — which is true at the GH-issue checkbox level but loses the durability of per-issue commit traceability. Reverting one wiki's decision in an umbrella-bundled scheme means re-opening the umbrella with a partial-revert commit, which is harder to read than `git log` on a per-wiki issue branch.

**Impact:** This is a real adversarial concern — bundling decisions of different evidentiary weight is precisely what review-friendliness sacrifices for. The plan's defense ("decisions are coupled" L251) is partially true (the routing principle is one concept) but partially false (lng-projects vs engineering-standards have different evidence bases).

**Fix:** Either (a) split the umbrella into a 2-issue structure: one for "codify already-W3C-re-anchored wikis" + one for "user-decision wikis lng-projects/acma-projects", OR (b) explicitly call out in the umbrella-issue body that "approval of this issue equals approval of all 4 codify+conditional sub-decisions; granular reversal requires a follow-up." The latter is cheaper.

---

### MINOR-4: aces-#4 cross-repo brittleness mitigation is callout-shaped, not durable-shaped

**Where:** L247 ("Mitigation: ... the umbrella issue body must include a `Reconcile-with: aces-#4 Phase 1 outcome` callout so the codification doesn't silently drift.")

**Defect:** A "Reconcile-with" callout in an issue body is not a durable enforcement mechanism. It is prose. If aces-#4 Phase 1 lands a contradicting routing decision in aceengineer-strategy, nothing in workspace-hub will alert. The callout depends on (a) a human reading the umbrella issue, (b) noticing aces-#4 has progressed, (c) manually reconciling. The plan acknowledges aces-#4 is in a separate repo (cross-repo brittleness) but its mitigation is the same pattern that the brittleness exists because of.

A more durable mitigation would be: a CI check that fetches aces-#4 status (gh API call) and fails the test suite if aces-#4 has Phase-1-completed status without a corresponding workspace-hub reconcile commit. That is heavier; the plan explicitly is T1 and avoids tooling. Acceptable for T1 — but the plan should NAME this trade-off explicitly: "the mitigation is prose-only; durable cross-repo reconcile tooling is out of scope for T1 and would be a follow-on."

**Fix:** Add a one-line explicit acknowledgment that the prose-callout is the trade-off, not the contract.

---

## Strengths (counter-weighting)

1. **Future-tense compliance is high.** The handful of past-tense matches (`landed`, `created`, `added`) are either (a) inside the verbatim memory quote block (L93, L95), (b) describe future-conditional state ("will land", "once approved"), or (c) describe pre-existing artifacts (`#2596 already landed`, `aces-#4 created 2026-04-25` — these are facts, not plan claims). No past-tense drift detected.
2. **Adversarial-stance disclosure is present.** Plan explicitly enumerates risks (L246-255) including the adversarial framings I would otherwise have to infer.
3. **Allowlist test passes** — no #2471 over-citation regression introduced.
4. **Memory verbatim quotation is exact.**
5. **Per-wiki matrix is exhaustive** (10/10 wikis enumerated).
6. **Source count exceeds minimum** (8 distinct sources vs ≥3 required).
7. **META status is unambiguous.** L10 + Files-to-Change table both explicitly disclaim file modification authority. The plan correctly defers all file edits to the umbrella sanction issue.
8. **Audit-vs-implementation distinction is well-handled.** This is a governance META plan, T1, no code paths — and the deliverable shape (text-only plan + future test extension shape + future CLAUDE.md edits) matches T1 complexity.

---

## Verdict Justification

**MINOR (4 findings).**

No MAJOR defects. No factual errors. No past-tense drift. No memory mis-quotation. No matrix inaccuracy. The 4 MINOR findings are:

1. Internal contradiction on test xfail vs hard-enforce mode (resolvable by picking one).
2. Test pseudocode hardcodes umbrella-issue-number placeholder — easier-to-defend if generalized to "any `#NNNN` within ±5 lines."
3. Umbrella-vs-per-wiki bundles two decision types (codify vs user-decision) that have different evidentiary weight; needs explicit acknowledgment OR a 2-issue split.
4. aces-#4 cross-repo mitigation is prose-only; should explicitly acknowledge the trade-off rather than present "Reconcile-with callout" as a durable mitigation.

None of these block plan-approval; all are improvements that strengthen the umbrella issue's downstream implementation. Plan is APPROVE-MINOR-eligible after the author addresses (1) at minimum (the contradiction is the only finding that creates a downstream forking-path defect).

---

## Recommended Revisions Before status:plan-approved

- **MINOR-1 (must fix):** Resolve the xfail vs hard-enforce contradiction. Pick one and update the conflicting site.
- **MINOR-2 (should fix):** Generalize the test contract to require ANY `#NNNN` reference within ±5 lines, OR explicitly note the placeholder is shape-only.
- **MINOR-3 (should fix):** Add explicit reviewer-friendly acknowledgment that umbrella-approval bundles codify + user-decision evidentiary types.
- **MINOR-4 (nice-to-have):** Add a one-line "the prose callout is the trade-off; cross-repo reconcile tooling is out-of-scope for T1" disclosure to the aces-#4 risk row.
