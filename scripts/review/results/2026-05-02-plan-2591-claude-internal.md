# Adversarial Review — Plan #2591 (W2-B ASME bounded summary promotion) — r1

> **Reviewer:** Claude (single-author internal review)
> **Date:** 2026-05-02
> **Plan under review:** `docs/plans/2026-05-02-issue-2591-llm-wiki-W2B-engineering-standards-asme.md`
> **GitHub issue:** [#2591](https://github.com/vamseeachanta/workspace-hub/issues/2591)
> **Provenance — cross-review unavailable:**
> - Codex: BLOCKED — `codex-cli 0.124.0` upstream stdin-hang regression (memory `feedback_codex_cli_0_124_upstream_regression.md`); #2479 filed; downgrade to 0.123.0 not yet authorized in this session
> - Codex (alt path): also blocked by sandbox no-execution constraint per memory `feedback_codex_sandbox_no_execution.md`
> - Gemini: cross-review.sh dispatch path requires permissions not granted to a planning-only session per memory `feedback_permission_gate_blocks_cross_review.md`
> - Single-author fallback per `feedback_permission_gate_blocks_cross_review.md`; provenance recorded transparently below
> **Verdict:** **MAJOR**
> **Counts:** MAJOR=4, MINOR=5

Stance: defects until proven otherwise. Every finding cites file/section and quotes the plan claim. Sources verified live where possible; web searches treated as assertions to verify.

---

## MAJOR findings

### MAJOR-1 — #2471 sanction-scope overreach (path-routing claim is unsupported)

**Plan claim** (line 9, frontmatter):
> `> **Path sanction:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) (CLOSED) — `wiki/standards/<code-id>.md` routing`

**Plan claim** (line 64, project memory consulted section):
> `project_wiki_standards_path_decision.md — wiki/standards/<code-id>.md is the sanctioned path; #2471 codified it for CSA Z276 and the principle generalizes here.`

**Plan claim** (line 280, Risks naming):
> `the naming follows the wiki/standards/<publisher>-<code-id> shape sanctioned by #2471's CSA Z276 precedent.`

**Verification (live)**:
- `gh issue view 2471 --json body` → title is *"feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract"*. Body: *"Decide and codify the sanctioned durable-wiki routing/schema for CSA Z276 pages..."*. Scope-statement explicitly: *"Decide the canonical durable destination for **CSA Z276 pages**."* Issue is CLOSED.
- Memory file `project_wiki_standards_path_decision.md` (verbatim quote, line ~26 of memory):
  > *"**Workspace-hub #2471** is OPEN with title 'feat(knowledge): decide sanctioned CSA Z276 wiki routing and durability contract' — scoped **strictly to CSA Z276**, not the general substrate. Earlier framing in this memory described it as a general codification; that framing is stale."*
  > *"**Codification plan** (filename `docs/plans/2026-04-23-issue-2471-standards-wiki-path-sanction.md` referenced in earlier memory body) **does not exist** in the repo."*
  > *"**General offshore/marine standards substrate** (DNV-OS-E301, API RP 2SK, ISO/ABS) is now scoped to aceengineer-strategy issue **aces-#4**..."*
- `.claude/rules/calc-citation-contract.md` line 10: *"Citation target: a wiki page with **#2471 frontmatter** (`code_id`, `publisher`, `revision`)."* The rule cites #2471 only for the **frontmatter schema** (code_id/publisher/revision triple), NOT for the path-routing contract.

**Defect**: The plan triple-asserts that #2471 sanctions a generalized `wiki/standards/<code-id>.md` path-routing pattern for ASME (and by implication arbitrary publishers). **This is wrong.** #2471's actual sanctioned scope is CSA Z276 only. The "principle generalizes" hand-wave on line 64 directly contradicts the load-bearing memory finding (verified 2026-04-25): *"the principle holds, but workspace-hub #2471 is scoped strictly to CSA Z276; general offshore/marine substrate populate is now scoped to aceengineer-strategy aces-#4."*

The plan also conflates two distinct things #2471 is cited for: (a) the path-routing decision (CSA-only), and (b) the frontmatter schema (`code_id`/`publisher`/`revision` — calc-citation-contract rule item 2). The rule's #2471 reference is solely about (b).

**Why MAJOR**: this is the same error class as the W1-A precedent (#2586) likely carries. Memory `project_wiki_standards_path_decision.md` exists *specifically* to prevent this kind of over-citation. Approving the plan as-written would create a second precedent commit citing #2471 outside its closed scope, hardening the misreading. The CLAUDE.md schema at `knowledge/wikis/engineering-standards/CLAUDE.md` already authorizes a `standards/` subtree on its own merit — plan should cite **that** as the sanctioning authority, not #2471.

**Required revision**: re-anchor the path sanction citation. Replace `#2471` with one or more of: (a) the engineering-standards wiki's own `CLAUDE.md` directory schema (which already allocates `wiki/standards/` with `code_id, publisher, revision required`), (b) calc-citation-contract.md rule 2 for the frontmatter schema, and (c) the W1-A plan #2586 as in-progress organizational precedent. State explicitly that #2471's path-routing decision was CSA-specific; cite memory for the limit. Optionally: open a follow-up issue to formally codify a publisher-agnostic standards-routing decision (the gap aces-#4 was supposed to close, but aces- is a different repo).

---

### MAJOR-2 — Ledger-empty claim is structurally true but rhetorically misleads (two ASME pointers exist outside the ledger)

**Plan claim** (line 27):
> *"zero ASME entries exist in the standards-transfer ledger today (verified: `grep -i ASME data/document-index/standards-transfer-ledger.yaml` returns empty); the ASME corpus has never been catalogued there."*

**Verification**:
- `grep -i "ASME" data/document-index/standards-transfer-ledger.yaml` → exit code 1, no output. Ledger has zero ASME rows. **Confirmed empty.**
- However: line 58 of the plan says *"`online-resource-registry.yaml` — contains only `asme_jomae_omae` (journal/proceedings entry)"* — so an ASME pointer DOES exist, in a sibling registry.

**Defect**: This is not a fabrication, but the framing *"the ASME corpus has never been catalogued there"* is rhetorically slack. "There" is the standards-transfer ledger (true zero rows). The reader risks generalizing to "ASME has zero index presence in workspace-hub", which is false — the journal-side pointer exists in `online-resource-registry.yaml`. Plan acknowledges this on line 58 but does not connect the dots.

**Why MAJOR (escalated from MINOR)**: this is the type of past-tense / hidden-assumption drift `feedback_plan_past_tense_artifact_claims.md` warns about — the gap claim is technically true but the surrounding prose hides a non-empty sibling. A plan reviewer skimming Resource Intel could approve under the impression that "no ASME presence anywhere" — that impression is wrong, and any cross-reference work in implementation will trip over `asme_jomae_omae`.

**Required revision**: rewrite line 27 to: *"the standards-transfer ledger has zero ASME rows (verified by grep); a single ASME journal/proceedings entry (`asme_jomae_omae`) exists in `online-resource-registry.yaml` — code-level catalog presence is zero."*

---

### MAJOR-3 — ASME copyright posture: plan's mitigation is plausible but specifically *not* publicly evidenced

**Plan claim** (line 276):
> *"**ASME enforcement is famously aggressive** — DMCA takedowns and litigation against verbatim re-publishers are common (publicly documented; cf. ASME v. Hydrolevel and follow-on enforcement posture)."*

**Verification (WebSearch)**:
- Search "ASME copyright enforcement DMCA standards republishing lawsuit" returned only ASME's own publishing/copyright policy pages — no specific DMCA-takedown news, no specific lawsuit precedent. Search finds: *"Failure to obtain permission before reprinting any material is a violation of the copyright laws of the United States"* — boilerplate, not enforcement record.
- *ASME v. Hydrolevel* is a real Supreme Court case (1982) — but it was about **antitrust liability for ASME's interpretation of code language being used to harm a competitor**, NOT about copyright enforcement against republishers. The plan miscites the case.

**Defect**: the *"famously aggressive"* claim drives the entire word-budget mitigation thesis (≤500 words, denylist, structural whitelist), but the publicly documented evidence the plan cites is wrong (Hydrolevel is antitrust, not copyright enforcement). The mitigation may still be sound on first principles (ASME's copyright posture IS strict per their own published policies), but the plan's grounding for the harder posture vs. the W1-A API precedent is built on a miscited case.

**Why MAJOR**: a reviewer asked to validate "is the bounded-summary mitigation sufficient for ASME?" cannot triangulate against the cited precedent. If a future contributor pushes back ("API and ASME have similar copyright postures, why is ASME mitigation tighter?"), the plan's rebuttal collapses — Hydrolevel won't support it.

**Required revision**: replace the Hydrolevel citation with either (a) ASME's actual published copyright policy page (https://www.asme.org/publications-submissions/publishing-information/legal-policies/copyright-terms-and-conditions — found in WebSearch), (b) the ASME terms-of-use page, or (c) drop the "famously aggressive" claim and rest the mitigation on equal-treatment-as-W1-A grounds. Do NOT keep "ASME v. Hydrolevel" as a copyright-enforcement citation — it's an antitrust case.

**Secondary observation**: even with the mitigation tightened, an honest reviewer should ask: is the only *truly* safe path zero text + frontmatter only (the api-17e.md stub pattern)? The plan's `revision: "public-metadata-required-before-citation-use"` escape hatch is the safe-by-default mode; the bounded-summary mode is opt-in for codes where the on-disk PDF edition is verifiable. The plan should state this trade-off explicitly: "every page that doesn't have an authoritatively pinnable revision MUST default to the api-17e stub pattern." Currently the plan implies the bounded summary is the default and the stub is an exception.

---

### MAJOR-4 — On-disk edition vs publisher-current is even worse than the plan admits

**Plan claim** (line 110):
> `ASME B31.3 currently active edition: 2022`

**Verification (WebSearch on B31.3 current)**:
- Multiple results reference **2024/2026 cycle** updates: *"For the 2024/2026 cycle, the most critical update involves the calculation of Stress Intensification Factors (SIFs). The code has moved away from the simplified Appendix D charts, now referencing ASME B31J as the mandatory method"*. Title also: *"ASME B31.3 Guide (**2026 Edition**): Process Piping Design & SIF Changes"*.
- Plan says current is 2022 (verified date 2026-05-02). On-disk PDF is **2012**.
- True lag: on-disk 2012 → publisher current 2026 ≈ **14 years**, with a load-bearing methodology change (Appendix D charts → mandatory B31J SIFs) intervening. Plan's stated lag was 2022−2012 = 10 years. The actual lag is 14 years AND crosses a methodology rupture.

**Defect**: the plan's `publisher_current_edition` field will be set to 2022 (per line 110 evidence), which itself is one cycle stale. Worse, downstream calc callers reading the wiki page will see a `revision: "2012"` pin — the SIF-method change in the 2026 cycle means a B31.3-citing calc with the 2012 revision is using a method *the publisher has now retired*. The risk-class label "Stale-edition citation by downstream callers is a known limitation, not a bug" (line 278) is too lenient when the gap straddles a deprecated methodology.

**Why MAJOR**: a regulator-defensible engineering-output citation (the explicit goal of `.claude/rules/calc-citation-contract.md`) cannot rest on a 14-year-stale revision pinned across a methodology change. The fail-closed citation contract (#2481 D2) catches missing/mismatched, but it does NOT catch "frontmatter says 2012 and that's correct vs. on-disk file but the standard's method has been retired."

**Required revision**: (a) update the `publisher_current_edition` evidence to 2024/2026 cycle, (b) for B31.3 specifically, body MUST include an advisory that the SIF method changed at the 2024/2026 cycle (1 sentence, no quoting), (c) consider downgrading B31.3 to the api-17e stub pattern (`revision: "public-metadata-required-before-citation-use"`) until a current PDF lands in `/mnt/ace`, OR explicitly accept the methodology-stale risk in the per-page frontmatter via a new `methodology_status: "stale-as-of-publisher-cycle"` field.

---

## MINOR findings

### MINOR-1 — BPVC VIII Div 1 + Div 2 = 2 of 10 slots is defensible but should be argued, not asserted

**Plan claim** (lines 286-287, top-10 list items 5+6 + Open Question line 294):
> *"BPVC Section VIII Div 1 (2010) — Pressure-vessel construction (33 ASME VIII internal hits, shared with Div 2)"*
> *"BPVC Section VIII Div 2 (2010) — Alternative-rules pressure vessels"*
> *"Open: **Granularity of BPVC Section VIII** — propose `asme-bpvc-viii-1` and `asme-bpvc-viii-2` as separate pages (consumes 2 of the 10 slots). Alternative: a single `asme-bpvc-viii` parent page..."*

**Defect**: the 33 internal-reference hits are aggregated to "ASME VIII" without disaggregating Div 1 vs Div 2 calls. So the *frequency* argument for Div 2 specifically is unverified. Div 1 (mandatory rules, broadly used) and Div 2 (alternative rules, narrower applicability — typically high-pressure / fatigue-cyclic vessels) have meaningfully different downstream caller profiles. The plan flags this as Open but the proposal already commits 2 of 10 slots to the split.

**Why MINOR (not MAJOR)**: the plan correctly flags this as a reviewer decision point. But the framing biases the reviewer toward approval of the 2-page split by listing both in the table.

**Required revision**: add disaggregated grep (`grep -c "DIV.?2\|Div\s*2"` of the digitalmodel callers) to the Resource Intel evidence to either justify or retract the Div 2 slot. If hits are <5, swap Div 2 for B16.20 or B31.1 per the listed alternatives.

### MINOR-2 — `wiki_path` validation missing from acceptance criteria

The Citation schema's `_validate_wiki_path` (verified at `digitalmodel/src/digitalmodel/citations/schema.py` line ~70) requires the wiki_path to start with `knowledge/wikis/`. Acceptance criterion line 248 hard-codes `wiki_path='knowledge/wikis/engineering-standards/wiki/standards/<id>.md'`. This is correct, but the plan does not assert that the constructed Citation will pass `validate_citation(...)` (the *resolution* step, requires repo_root and reads frontmatter). The accept-test stops at construction, which only triggers `CitationValidationError`, not `CitationResolutionError`. The contract claims fail-closed at calc-time per #2481 D2.

**Required revision**: add an acceptance criterion that runs `from digitalmodel.citations.schema import Citation, validate_citation; validate_citation(c, repo_root=Path('.'))` for at least the Citation in the worked example (B31.3) and asserts no `CitationResolutionError`.

### MINOR-3 — Index update commits to "page_count = X" but X is undefined and depends on landing order with W1-A

**Plan claim** (line 211):
> *"Modify `knowledge/wikis/engineering-standards/wiki/index.md` — Append/extend "## Standards" section with 10 new rows; bump `page_count` (jointly with W1-A; final value depends on landing order)."*

**Verification**: index currently shows `page_count=5` (line 30 of index.md). W1-A and W2-B both target +10 rows each, so final stable state is 5 + 10 + 10 = 25. Whichever lands second has a merge-conflict risk on the `page_count` integer.

**Required revision**: state the merge-conflict mitigation explicitly. Either (a) require a serialization checkpoint between W1-A and W2-B implementation, (b) use a sentinel (`page_count: auto`) and let the wiki-ingest job recompute, or (c) accept the merge conflict and document the resolution recipe in the plan.

### MINOR-4 — RAW_TELLTALE_PHRASES list ≤15 entries — no evidence the on-disk PDFs actually carry these phrases

**Plan claim** (line 236):
> *"`RAW_TELLTALE_PHRASES` will be a small, narrowly-scoped list (≤15 entries) drawn from ASME publication front-matter conventions — e.g. 'American Society of Mechanical Engineers', 'Two Park Avenue', 'New York, NY 10016', 'Reproduction or translation of any part of this work'..."*

**Defect**: the plan asserts these are "ASME publication front-matter conventions" but does not cite a verification step. ASME's actual address is 150 W 47th St 28th Fl, New York since 2017 (their offices moved); "Two Park Avenue" was the prior address. Older PDFs (2010-2013) likely DO have "Two Park Avenue", but anyone validating the denylist by sampling the on-disk PDFs first must either confirm this or substitute. The narrow `feedback_naive_secret_scan_false_positive_cascade.md` warning applies in reverse here: a too-narrow phrase set risks false-NEGATIVE (a copyright excerpt slips through because the cover page used different boilerplate). This is the harder failure mode.

**Required revision**: change "≤15 entries" to "extracted by sampling the cover/copyright page of at least 3 of the 10 on-disk PDFs (B31.3-2012, BPVC VIII-1-2010, B16.5-2013) and capturing the actual front-matter phrasing observed". Add an implementation-time check that this sampling step happens before the denylist is locked.

### MINOR-5 — FFS-1 exclusion is justified but the cross-wiki inconsistency is not flagged as a real systemic issue

**Plan claim** (line 295, Open Q):
> *"**FFS-1 unification** — the existing joint API 579-1 / ASME FFS-1 page lives in `engineering/wiki/standards/`, not the target `engineering-standards/wiki/standards/`. Should W2-B (a) leave it alone (current proposal), (b) retro-move it, or (c) create a thin pointer page in the target wiki linking to the existing one? Flag for reviewer; the current proposal is (a)."*

**Verification**:
- `knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` EXISTS, is well-formed, has substantial content (frontmatter + scope + assessment levels + damage mechanisms table — read the head of the file).
- `knowledge/wikis/engineering-standards/wiki/standards/` has only `api-17e.md`.
- Two wikis with overlapping `standards/` subtrees, populated by different patterns (engineering = richer prose, engineering-standards = bounded stub), no cross-link, no superseding decision.

**Defect**: the plan documents the conflict but treats it as a per-page deferral. This is actually a systemic issue: the engineering-wiki and engineering-standards-wiki host overlapping/inconsistent standards content, and there is no decision about which is canonical. Approving this plan creates 10 more pages in engineering-standards-wiki, hardening the de-facto split without ever forcing the canonicality decision.

**Why MINOR (not MAJOR)**: the deferral itself is reasonable for W2-B's scope. But the *implication* — that W2-B is a precedent for "engineering-standards is where ASME bounded-summary lives" — bakes in the split. The follow-up needs to be a real issue, not a flag.

**Required revision**: add a Files-to-Change row creating a follow-up issue (or commit to filing one within the same PR) titled approximately "decide canonical wiki for cross-publisher standards (engineering vs engineering-standards) — supersede or merge". Cite this issue in W2-B's Open Q line 295.

---

## Adversarial pattern hunt — explicit findings

| Pattern | Found? | Where |
|---|---|---|
| Past-tense artifact claims (`feedback_plan_past_tense_artifact_claims.md`) | NO | line 63 explicitly states future tense; verified by reading lines 27/82-87 — all "EXISTS"/"MISSING" framing maps to verifiable on-disk state, not claimed-completed work |
| Hollow tests (asserts pass-by-construction) | PARTIAL | `test_no_overlap_with_engineering_wiki_ffs1` (line 234) — checks that ASME pages don't link to the engineering-wiki FFS page. This is hollow: pages are LLM-authored to NOT contain that link, so the test is confirming the author followed instructions. Not a true regression guard. **Fix**: drop or replace with a positive test (assert the FFS page IS reachable from somewhere). |
| Hidden assumption — "10 is enough" | YES | line 281-292 — top-10 selection biases on digitalmodel hit-frequency, but does not consider Phase 2 reach (assethold, dgs-engineering) callers. If those repos cite ASME B16.20 / B16.34 / B16.47 / BPVC V (NDE), the top-10 picked here is locally optimal but globally short-sighted. **Fix**: add cross-repo grep evidence (or explicitly state W2-B is digitalmodel-only). |
| Hidden assumption — "W1-A pattern is settled" | YES | The plan inherits W1-A heavily but W1-A is itself OPEN (#2586 not yet implemented, line 79). Inheritance from an unlanded sibling means W2-B may need to track W1-A's review revisions in lockstep. **Fix**: add an acceptance criterion: "W1-A approved before W2-B implementation begins, OR explicit user approval to fork the patterns." |
| Mock-vs-live divergence (`feedback_mock_vs_live_invocation_divergence.md`) | NO | tests are file-content based, not invocation-based; not applicable. |
| Naive secret-scan FP (`feedback_naive_secret_scan_false_positive_cascade.md`) | RELATED | denylist phrasing risk; covered in MINOR-4. |
| Plan over-citing #2471 | YES | covered in MAJOR-1. |

---

## Verdict

**MAJOR (4 findings + 5 MINOR)**.

Two of the MAJOR findings (MAJOR-1 #2471 sanction-scope, MAJOR-3 ASME copyright posture miscitation) require source-of-authority changes before approval. MAJOR-2 (ledger-empty rhetorical drift) and MAJOR-4 (publisher-current cycle update + methodology change) require evidence updates and a per-page methodology-status field. The MINORs are tractable revisions.

**Recommended next steps**:
1. Plan author: address MAJOR-1 by re-anchoring path-sanction citation to the engineering-standards CLAUDE.md schema + W1-A as in-progress precedent, NOT #2471. Add explicit memory-citation acknowledging #2471 is CSA-only.
2. Plan author: address MAJOR-3 by replacing Hydrolevel citation with ASME's published copyright policy URLs (already surfaced in WebSearch).
3. Plan author: address MAJOR-4 by updating the publisher-current evidence to 2024/2026 cycle and adding methodology-status field for B31.3.
4. Plan author: address MAJOR-2 by acknowledging `asme_jomae_omae` registry entry.
5. Reviewer (user): note the W1-A (#2586) likely carries the same MAJOR-1 over-citation pattern — flag for that plan's review too.
6. Re-review (r2) after revisions land.

---

## Sources cited

- [ASME B31.3 Guide (2026 Edition): EPCLand](https://epcland.com/asme-b31-3-process-piping-design/) — Web-evidence for 2024/2026 cycle + B31J SIF methodology change.
- [B31.3 — Process Piping (ASME catalog)](https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping)
- [Copyright Terms and Conditions — ASME](https://www.asme.org/publications-submissions/publishing-information/legal-policies/copyright-terms-and-conditions) — replacement citation for MAJOR-3.
- [Use of ASME Copyrighted Information](https://www.asme.org/codes-standards/find-codes-standards/use-of-asme-copyrighted-information)
- Live: `gh issue view 2471` body verbatim quoted in MAJOR-1.
- Live: `/home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_wiki_standards_path_decision.md` quoted in MAJOR-1.
- Live: `.claude/rules/calc-citation-contract.md` line 10 quoted in MAJOR-1.
- Live: `digitalmodel/src/digitalmodel/citations/schema.py` line ~70 (wiki_path validator) referenced in MINOR-2.
- Live: `find /mnt/ace/O&G-Standards/ASME -maxdepth 4 ... | wc -l` → 88 (matches plan).
- Live: 10/10 priority on-disk PDF presence verified by `ls` per code subfolder.
- Live: `grep -i ASME data/document-index/standards-transfer-ledger.yaml` → exit 1 (matches plan).
- Live: `knowledge/wikis/engineering/wiki/standards/api-579-ffs.md` exists and is well-formed; `engineering-standards/wiki/standards/` contains only `api-17e.md`.
