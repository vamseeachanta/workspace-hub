# Adversarial review — plan #2602 W4-D engineering wiki pipeline sub-domain expansion

**Plan:** `docs/plans/2026-05-03-issue-2602-llm-wiki-W4D-engineering-pipeline-expansion.md`
**Issue:** [#2602](https://github.com/vamseeachanta/workspace-hub/issues/2602) (OPEN)
**Reviewer:** Claude (internal, single-author per `feedback_permission_gate_blocks_cross_review.md`)
**Date:** 2026-05-03
**Stance:** standard 7-clause adversarial — defect-hunting, not charitable reading

---

## Verdict

**MINOR** — plan is well-grounded, follows the W3-D shape closely, includes the W3-C #2471 erratum discipline, and the verifications all pass. Two MINOR defects identified (one factual claim error, one bounded test-logic risk) and four NIT-level observations. No P1 (MAJOR) defects.

- MAJOR_COUNT: 0
- MINOR_COUNT: 2
- NIT_COUNT: 4

---

## Verification log

| # | Check | Result |
|---|---|---|
| 1 | Read full plan (431 lines) | done |
| 2 | `uv run pytest tests/governance/test_2471_citation_scope.py` | **6 passed in 2.83s** — allowlist polarity holds with W4-D plan in tree |
| 3 | `find knowledge/wikis/engineering/wiki -iname "*pipeline*" -type f` | returns exactly 2 files: `concepts/pipeline-integrity-assessment.md` + `workflows/orcawave-to-orcaflex-pipeline.md` — plan's 2-existing-pages claim is **accurate**; homonym disambiguation justified |
| 4 | Boundary-discipline regex test logic — could legitimate `pipeline-end-expansion-spool-design.md` trip it? | bounded risk; see MINOR-2 |
| 5 | W3-D sibling shape parity (`head -10` of #2597 plan) | confirmed: same H1 / Status / Complexity T2 / Issue / Review-artifacts header structure |
| 6 | `test_no_2471_path_sanction_citation` — duplicate of governance allowlist? | no — complementary; see NIT-1 |
| 7 | Cited issues #2540 / #2588 / #2596 / #2597 / #2589 (+ #2602) state/title check | **all 6 match plan claims** verbatim (CLOSED/OPEN + exact titles) |
| 8 | Forward-reference marker resilience | distinct `W4-codify` tag (vs W3-D's `W3-B`) — see NIT-2 |
| 9 | HDD onshore + riser-pipeline interface deferral legitimacy | both are legitimately scoped out, with explicit deferral language and Open Questions; **not stealth scope creep** |
| 10 | Past-tense drift hunt | clean — plan uses **future tense throughout**; explicitly cites `feedback_plan_past_tense_artifact_claims.md` |

---

## MINOR findings

### MINOR-1 — digitalmodel cross-ref baseline claim is factually wrong

**Location:** plan lines 188–190.

**Claim under review:**
> `grep -rE "knowledge/wikis/engineering" digitalmodel/src/ digitalmodel/scripts/ digitalmodel/tests/ 2>&1 | wc -l`
> Expected: 0 (matches the W3-D baseline).

**Actual on-disk state (verified 2026-05-03):**
```
$ grep -rE "knowledge/wikis/engineering" digitalmodel/src/ digitalmodel/scripts/ digitalmodel/tests/ 2>&1 | wc -l
3
$ grep -rE "knowledge/wikis/engineering" digitalmodel/src/ digitalmodel/scripts/ digitalmodel/tests/
digitalmodel/src/digitalmodel/citations/registry.py:    "wiki_path": "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"
digitalmodel/tests/citations/test_schema.py:REAL_DNV_PAGE = "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"
digitalmodel/tests/citations/test_schema.py:    c = Citation(**_valid_kwargs(wiki_path="knowledge/wikis/engineering/wiki/standards/does-not-exist.md")) # noqa
```

The expected count is **3, not 0**. The 3 hits are all citation-schema scaffolding (`citations/registry.py` mapping for DNV-OS-E301 + 2 test fixtures), not concept-page cross-refs, so the plan's broader argument ("adding concept pages will not by itself create calc-side citations") is intact — but the precise zero-cross-ref claim is wrong.

**Why MINOR not NIT:** the plan asserts "matches the W3-D baseline" — if W3-D claims zero and verification under W4-D shows three, either (a) W3-D's baseline number is also stale or (b) commits have landed since W3-D claimed zero. Either way, a parallel-plan reviewer pulling this evidence forward will inherit the defect. Numerical claims in resource-intel sections are load-bearing under planning workflow review; this one fails verification.

**Required fix:** restate as "Expected: 3 (citations-schema scaffolding for `dnv-os-e301.md`, not concept-page references). Adding these concept pages will not by itself increment this count; calc-side adoption follows up under the citation contract." Or rerun grep at execution time and adjust prose.

---

### MINOR-2 — section-dominance test risks false-positive on legitimate riser-pipeline interface mentions

**Location:** plan lines 352, 360–361, 411.

**Test logic under review (`test_no_scope_creep_into_riser_mooring_umbilical`):**
> Tokenise each page into top-level (H2) sections; for each section, count `riser|SCR|TTR|mooring|umbilical` keyword hits vs. `pipeline|flowline|pipelay|S-lay|J-lay|reel-lay|on-bottom|free-span|buckling|spool|PLET|trawl|coating` hits. Fail if any section's non-pipeline keyword count exceeds the pipeline keyword count. Whitelist: `## Scope` / `## Out of Scope`.

**Concern:** `concepts/pipeline-end-expansion-spool-design.md` is the page most exposed to legitimate riser-pipeline-interface mentions:

- Plan line 99 + 117 + 328: this page covers PLET, mid-line tee, expansion spool, **sleeper interaction**.
- A PLET is the **interface point with an SCR** (steel catenary riser flowline tie-in). Honest discussion of PLET design ("the PLET hosts the SCR-flowline tie-in flange and absorbs both spool-side end-expansion and riser-side hang-off load") will trip the test if SCR appears outside `## Scope` / `## Out of Scope`.
- Per the section-dominance rule, the page would need its tie-in discussion confined to a Scope/Out-of-Scope callout, OR balanced with enough pipeline-side keywords (`spool`, `pipelay`, etc.) per section. The latter is feasible in body sections but adds linguistic friction.
- The plan's own "Open Question" lines 411 + 419 acknowledges this risk and defers a dedicated `riser-pipeline-interface.md` page to a follow-up batch — consistent with the defect, not a hidden contradiction.

**Why MINOR not NIT:** the test exists to be tight, and the planned mitigation (whitelist for boundary callouts) is genuinely sufficient — **but** the implementer of the spool-design page needs to know in advance that the body sections cannot freely use `SCR` even when describing pipeline-side hardware. Implementation-time discovery of this constraint is a known cause of test-thrash.

**Required fix (preferred):** add an Open Question or implementation note to the spool-design row in the Files-to-Change table making the constraint explicit: "Note: PLET-as-SCR-tie-in discussion must be confined to `## Scope` or to sentences that include explicit pipeline-side keywords (`spool`, `pipelay`, `flowline`) within the same section to satisfy `test_no_scope_creep_into_riser_mooring_umbilical`."

**Alternative (not preferred):** add `flowline-tie-in` to the pipeline-positive keyword list. Less surgical; widens the keyword-positive set and weakens the homonym discipline elsewhere.

---

## NIT-level observations

### NIT-1 — `test_no_2471_path_sanction_citation` is complementary, NOT duplicative

The per-plan test scopes the W3-C erratum check **down to this plan + the 10 new pages + the test file itself**, with the additional invariant that any `#2471` mention must sit inside a documented "NOT a path-sanction" boundary callout. The governance allowlist test at `tests/governance/test_2471_citation_scope.py` operates on `docs/plans/2026-05-02-*.md` (note the date glob). W4-D dates 2026-05-03, so the governance test will not auto-cover the new plan unless its glob expands. The per-plan test is **the only enforcement** for this plan's date.

**Implication:** the plan should explicitly raise the glob-mismatch as a follow-up note OR the implementer should propose a tiny governance-test glob expansion (`2026-05-0*` instead of `2026-05-02-*`) when this plan's PR lands. Not a defect of the plan itself — surfacing for downstream awareness.

### NIT-2 — forward-reference marker tag `W4-codify` is correctly distinct from W3-D's `W3-B`

Plan line 413 explicitly notes: "The marker tag `W4-codify` is intentionally distinct from W3-D's `W3-B` tag so a future plan can run a tag-specific deletion sweep without ambiguity." This is the right call — W3-B is a specific GitHub-issue tag; using a generic `W4-codify` (literal name, not issue) avoids future tag-collision when W3-B is/was discharged separately. Marker resilience holds.

### NIT-3 — page count claim has a small consistency wobble

Plan line 15: "105 markdown files on disk; `index.md` frontmatter `page_count` reads **83**". Both numbers are verified accurate against `grep page_count knowledge/wikis/engineering/wiki/index.md` (= 83). The 22-file delta between disk count and frontmatter is explained by uncatalogued/in-flight pages (consistent with parallel plans #2559 OCIMF-tandem and #2597 W3-D riser staging additions to a not-yet-regenerated index). Accuracy of the page_count "≥93" floor in `test_index_page_count_bumped` is intact regardless.

### NIT-4 — `/mnt/ace/saipem/` subdirectory enumeration is partial

Plan line 82 + 145 lists Saipem subdirs as `general/{cp, engg, flexible, reports, slwr, spoolbase, yt_docs}`. Actual on-disk listing also contains `rov_access` and `yml_modular_example` siblings under `general/`. Not material — the plan correctly says "subdirs" (not "all subdirs"), and the listed directories are the pipeline-relevant ones. Surfacing only because the plan-style is otherwise meticulous about exhaustive enumeration.

---

## Adversarial pattern hunt

| Pattern | Found? | Notes |
|---|---|---|
| Past-tense artifact-claim drift (`feedback_plan_past_tense_artifact_claims.md`) | NO | plan uses future tense throughout; explicitly cites the rule |
| `#2471` over-citation as generalized path-sanction (#2596 erratum) | NO | plan explicitly disclaims and adds a per-plan test |
| Stealth scope-creep (sub-topics not declared up-front) | NO | HDD-crossing + riser-pipeline-interface explicitly declared as Open Questions / deferred follow-ups |
| Hyphen-path Python-import poisoning (`feedback_llm_wiki_hyphen_module_path_pattern.md`) | NO | this plan touches no Python module paths under `llm-wiki/` |
| Forward-reference marker collision with sibling plan | NO | `W4-codify` distinct from W3-D's `W3-B` |
| Hard-coded `page_count` literal that parallel plans will invalidate | NO | acceptance bullet uses `≥93` floor + execution-time re-derivation |
| Naive secret-scan FP cascade trigger | NO | no secret-shaped strings introduced |
| Plan-vs-live-state contradiction | YES (one) | digitalmodel cross-ref count claim — see MINOR-1 |
| Test-name homonym with another plan's test | NO | tests carry pipeline-specific suffixes |
| Source-count minimum (≥3) | YES — exceeded | 12 distinct sources cited per plan footnote line 210–223 |

---

## Final disposition

The plan is well-engineered, exhibits strong evidence-density, follows the W3-D-revised shape verbatim including the section-dominance + positive-topic-dominance + forward-reference-marker triad, and adheres to the W3-C #2471 erratum discipline. The two MINOR defects are bounded and addressable in a single revision pass.

Recommend: **MINOR — revise and resubmit for approval.** Required revisions:
- Fix MINOR-1: correct the digitalmodel cross-ref baseline claim (3 not 0; clarify nature of hits).
- Fix MINOR-2: add an implementer-facing note on the spool-design page row about confining SCR-tie-in mentions to whitelisted sections OR balancing keywords per section.

Optional revisions (NITs): expand governance test glob, consider partial-enumeration phrasing.

After revisions, the plan is APPROVE-eligible.
