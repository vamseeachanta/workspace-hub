# Adversarial review (internal, Claude) — `docs/plans/2026-05-03-issue-2601-llm-wiki-W4C-marine-engineering-audit.md`

> **Issue:** [#2601](https://github.com/vamseeachanta/workspace-hub/issues/2601)
> **Plan:** `docs/plans/2026-05-03-issue-2601-llm-wiki-W4C-marine-engineering-audit.md`
> **Plan status at review:** `draft`
> **Reviewer:** Claude (internal)
> **Date:** 2026-05-03
> **Stance:** Adversarial reviewer — defect-hunting, not charitable reading. Standard 7-clause stance.

---

## Stance contract (adversarial)

I am hunting defects. The plan does not get the benefit of the doubt. Every quantitative claim is checked against live state. Every external anchor is fetched. Every tense-drift, scope-creep, or "will-co-create / reused" hand-wave is flagged. A clean review here means each verifiable assertion was independently reproduced; it does not mean nothing could be improved.

---

## Verification log (live commands run 2026-05-03)

| Check | Command / source | Result | Plan-claim status |
|---|---|---|---|
| Allowlist test | `uv run pytest tests/governance/test_2471_citation_scope.py 2>&1 \| tail -3` | `6 passed in 3.47s` | PASS |
| Wiki total file count | `find knowledge/wikis/marine-engineering/wiki -type f -name "*.md" \| wc -l` | `19199` | matches plan claim of 19,199 |
| Sources subdir count | `find .../wiki/sources -type f -name "*.md" \| wc -l` | `19166` | matches plan claim |
| Concepts subdir count | `find .../wiki/concepts -type f -name "*.md" \| wc -l` | `14` | matches |
| Entities subdir count | `find .../wiki/entities -type f -name "*.md" \| wc -l` | `15` | matches |
| Comparisons subdir count | `find .../wiki/comparisons -type f -name "*.md" \| wc -l` | `1` | matches |
| Visualizations subdir count | `find .../wiki/visualizations -type f -name "*.md" \| wc -l` | `0` | matches |
| Standards subdir on disk | `ls knowledge/wikis/marine-engineering/wiki/standards/` | `No such file or directory` | confirmed missing |
| CLAUDE.md declares standards/ | `grep "wiki/standards" knowledge/wikis/marine-engineering/CLAUDE.md` | `### Standards page extra fields (\`wiki/standards/*.md\`)` plus directory-tree block | confirmed declared |
| Raw seed count | `find .../raw -type f \( -name "*.pdf" -o -name "*.md" \)` | 5 PDFs in `raw/papers/`; 0 elsewhere | matches plan claim of 5 raw seeds |
| Source-stub bodies "empty" | sampled 8 random files (`omae2009-79373.md`, `otc20397.md`, `session-detail-21.md`, `189.md`, `2004-nm-04.md`, `otc8902.md`, `omae2011-50347.md`, `219id.md`) → 25–26 lines each, all frontmatter + auto-ingest metadata table; NO extracted body content | matches plan claim |
| Distribution at 200-file scale | line-count histogram of first 200 source files: 156×26-line, 44×25-line | confirms uniform stub shape |
| Filename-prefix histogram | `ls .../sources \| awk '{print substr($0,1,4)}' \| sort \| uniq -c \| sort -rn \| head -16` | matches plan numbers exactly (omae=6234, otc1=2904, otc2=1370, 2012=690, otc-=643, 14tp=547, 13tp=544, 11tp=541, 2004=463, i07j=341, otc8=254, spe1=145, pape=106, sess=103, i07s=70, snam=68) | every cited prefix count matches live |
| Overview staleness | `head -60 wiki/overview.md` | shows `Source documents: 5 / Entity pages: 8 / Concept pages: 7 / Total wiki pages: 20` | matches plan claim — overview genuinely stale |
| digitalmodel cross-refs | `grep -rl "knowledge/wikis/marine-engineering" digitalmodel/` | 5 fixture YAMLs + 1 test (`test_validation.py`) | matches plan claim of 6 references; none are citation-registry entries |
| Citation-registry wiring | `grep -c "knowledge/wikis/marine-engineering/wiki/" digitalmodel/src/digitalmodel/citations/registry.py` | `0` | matches plan claim |
| ITTC URL liveness + numbering | `WebFetch https://ittc.info/` (homepage) and `WebFetch .../recommended-procedures-and-guidelines/` | URL reachable; **7.5-XX-XX-XX numbering pattern confirmed**; specialist committees Resistance/Propulsion/Seakeeping/Manoeuvring/Stability-in-Waves explicitly named on the procedure index | partially confirms anchor; see MINOR-1 |
| SNAME URL liveness | `WebFetch https://www.sname.org/SNAME/Sections/` and `.../communities/offshore` | both URLs reach a login wall; "Offshore Section" / "Offshore Symposium" not visible to public WebFetch | see MINOR-2 |
| Stealth-edit hunt | `git status` | only `.claude/state/` housekeeping + 4 unrelated planning artifacts in untracked; **zero edits to `knowledge/wikis/marine-engineering/`**; **zero `docs/audits/` files**; **zero `tests/knowledge/test_marine_engineering_audit_artifact.py`** | audit-only nature confirmed |
| Past-tense drift sweep | `grep -n "MISSING (this plan creates)\|will be co-created\|future-tense" plan` | line 187, 188, 194, 249, 293 — all uses are correctly future-oriented | clean |
| Issue #2601 status | `gh issue view 2601` | OPEN, title matches plan, labels include `priority:high`, `domain:marine`, `domain:knowledge-management`, `cat:documentation` | matches |

---

## Findings

### MAJOR — none

### MINOR-1: ITTC sub-discipline list as an anchor partially exceeds what the cited URL surfaces

**Where:** plan line 57; pseudocode line 245; acceptance-criterion line 326.

**Plan asserts** that ITTC Specialist Committees define sub-disciplines including "Ocean Engineering, Stability in Waves, Manoeuvring, Seakeeping, Resistance, Propulsion, CFD/Numerical, Cavitation, Ice (each is a falsifiable English-named anchor with an ITTC procedure number, e.g., 7.5-02-07-03.x)."

**What I verified:** WebFetch on `https://ittc.info/` and the linked recommended-procedures-and-guidelines index confirms the 7.5-XX-XX-XX numbering pattern AND confirms five of the eight cited committees by name (Resistance, Propulsion, Seakeeping, Manoeuvring, Stability in Waves). It does **not** surface "Ocean Engineering," "CFD/Numerical," "Cavitation," or "Ice" on the index page WebFetch returned. These committees do exist at ITTC (well-attested in the literature), but the plan's anchor URL doesn't make them mechanically falsifiable from the cited surface alone. The TDD enforcement regex (`7\.5-0[0-9]-[0-9]{2}-[0-9]{2}`) covers the numbering, so this is a documentation-citation gap not an enforcement gap, but the audit deliverable will be more defensible if the ITTC anchor citation per row reaches the specific committee page (e.g., `7.5-02-07-` family for Ocean Engineering) rather than the index. Equivalent rigor to W1-C's ISO 19900-series anchors (which cite a specific part number per row).

**Severity rationale (MINOR not MAJOR):** the plan's TDD regex (`7\.5-0[0-9]-[0-9]{2}-[0-9]{2}`) is itself sufficient to enforce verifiability at execute time; this just sharpens the audit's source attribution. The plan's risk-section line 358 already acknowledges renumbering risk and offers SNAME as a fallback anchor.

**Suggested edit (one line):** in the Resource-Intelligence "LLM Wiki pages consulted" entry for ITTC, replace the bare `https://ittc.info/` with the recommended-procedures index URL (`https://ittc.info/downloads/quality-systems-manual/recommended-procedures-and-guidelines/`) so that downstream agents fetching the anchor land on the page that actually exposes the 7.5-XX-XX-XX tree.

---

### MINOR-2: SNAME Offshore Section URL hits a public login wall

**Where:** plan line 58; pseudocode line 253; acceptance-criterion line 328.

**Plan asserts** `https://www.sname.org/SNAME/Sections/` as a "second taxonomy anchor" and uses the literal `SNAME Offshore Section` as one of four valid rationale anchors enforced by `test_audit_rationales_cite_required_anchors`.

**What I verified:** both candidate URLs (`/SNAME/Sections/` and `/communities/offshore`) reach a SNAME login interface; the public surface does NOT expose an "Offshore Section" or "Offshore Symposium" listing. The Offshore Symposium proceedings are real (the plan correctly observes 1,632 of the source stubs are Offshore Symposium TPC files) but the *URL anchor* the plan uses to make the literal "SNAME Offshore Section" falsifiable is not publicly fetchable. A reviewer or future automated detector following the cited URL would not be able to confirm the section exists from that URL.

**Severity rationale (MINOR not MAJOR):** the literal-string anchor (`SNAME Offshore Section`) is enforceable at the audit-deliverable level by the TDD test independent of URL reachability, and the conference-paper-count signal (1,632 files) is locally observable. This is a citation-quality issue, not a correctness issue. The TDD test checks the literal in the rationale string, not the URL.

**Suggested edit:** either (a) drop the `https://www.sname.org/SNAME/Sections/` URL from the plan and rely on the locally-observable Offshore Symposium TPC file-count plus the literal-string TDD assertion, or (b) cite a fetchable surface (e.g., a SNAME Offshore Symposium proceedings page or the conference's Wikipedia article) so the anchor is not behind a paywall/login.

---

### MINOR-3: `docs/audits/` co-creation hand-off between W1-C (#2588) and W4-C (this plan) is implicit, not enforced

**Where:** plan line 194 ("`docs/audits/` directory will be co-created by W1-C plan #2588 and reused here"), line 293 ("Create (or reuse) `docs/audits/`...; W4-C reuses if extant, or creates if W1-C lands later").

**Concern:** both W1-C (#2588) and W4-C (#2601) declare `docs/audits/` as MISSING-this-plan-creates. Whichever lands second will encounter a directory that already exists and will need a directory-already-exists tolerance. The plan handles this in prose ("reuse if extant") but the TDD test at line 316 (`test_audit_no_wiki_writes`) does not check that this plan does not modify any file under `docs/audits/` *other than its own deliverable*. If W1-C lands first and seeds a top-level `docs/audits/README.md`, this plan's commit will not collide, but if the seeding pattern includes a per-domain template, there's a small risk of over-write.

This is a low-probability execution-time wart, not a defect in the plan logic. It's only worth flagging because the same observation would apply if a third audit (e.g., naval-architecture) is dispatched in the same overnight wave.

**Severity rationale (MINOR not MAJOR):** mitigated in prose; only a real risk if W1-C and W4-C land within the same minute and a third audit is also racing for the same directory. Convention "create top-level once, append per-domain" is sufficient.

**Suggested edit (optional):** add to acceptance criteria: `docs/audits/` may pre-exist (created by sibling audit plan); this plan only creates `docs/audits/2026-05-03-marine-engineering-wiki-gap-audit.md` and does not modify any other file in `docs/audits/`.

---

### MINOR-4: Drift tolerance ±5 at 19K scale is documented as "equivalent rigor" to W1-C's ±2 at 520-file scale; that framing is defensible but understates the cardinal-axis count

**Where:** plan line 357 ("equivalent rigor to W1-C's ±2 at 520-file scale"), pseudocode line 282.

**Concern raised in the prompt:** at 19,200 scale, ±5 = 0.026% (vs W1-C's ±2 / 520 = 0.4%). On a single-axis percentage basis, this audit is stricter, not weaker. **However**, marine-engineering has more *cardinal axes of drift* than engineering — the audit table cites file counts in 6 subdirs (comparisons/concepts/entities/sources/visualizations/root) plus ≥8 prefix buckets plus 4 raw subdirs = roughly 18 independent counts. With ±5 per cell and ~18 cells, the expected aggregate drift tolerance is ~90 files (vs W1-C's ~13 with ±2 × ~7 cells). On an aggregate-budget basis the marine plan tolerates ~7× more drift than W1-C did. This is still tiny in proportion to 19,166 (~0.5%) but it is genuinely weaker than a strict per-axis-percentage equivalence reading would suggest.

The pseudocode uses *absolute ±5 per cited count* which is what the test actually enforces, so the framing in line 357 is accurate at the per-cell level but slightly oversold as "equivalent rigor" once you count cells.

**Severity rationale (MINOR not MAJOR):** the *tightest* potential drift signal — total-file count or sources-subdir count — is bounded at ±5 absolute = 0.026% at 19,166 scale, well inside the wave-2 ingest cron's typical batch size (which lands hundreds of files per pass when active). The asymmetry only matters if a partial-batch-failure mid-audit lands ~30 files into one prefix bucket but not others; that's the realistic failure mode. The plan's mitigation (audit re-run on drift exceeding tolerance) handles this correctly.

**Suggested edit (optional):** in the risk note at line 357, append: "aggregate drift across ~18 cited cells = ±90 files at the test boundary; ingest cron typically lands batches large enough to exceed this in a single pass — verify cron quiescence before audit landing".

---

### MINOR-5: Adversarial-Review-Summary table uses "TBD" for all three rows and "TBD" / "N/A — none yet" for the overall result and revisions sections

**Where:** plan lines 340–348.

This is correct for a `draft` status plan (the row is filled at `plan-review` time after fan-out). Flagged here only as a positive: the plan does *not* prefill these with charitable values, which is the failure mode the past-tense-drift rule is guarding against. No action needed.

---

## Past-tense / charitable-language sweep

Searched plan body for verbs that would imply work was already done:

- "will be co-created" (line 194, 293) — correctly future tense.
- "MISSING (this plan creates)" (lines 187, 188) — correctly future tense.
- "no child issues will be opened by this plan" (line 332) — correctly bounds future work.
- "TBD — plan is in `draft`" (line 344) — explicit, no fake claim of completion.
- Acceptance criteria use unchecked `[ ]` boxes throughout — no premature checkmarks.

**Verdict on tense drift:** clean.

## Stealth-edit / scope-creep sweep

`git status` shows zero modifications to `knowledge/wikis/marine-engineering/`, zero new `docs/audits/` files, zero new test files at the path this plan declares it will create. The audit-only declaration in the plan is consistent with on-disk state. Untracked files in working tree are unrelated planning artifacts (`docs/plans/2026-05-02-issue-2580-...`, `docs/plans/2026-05-02-label-taxonomy-gap.md`, sibling review files) plus `.claude/state/` housekeeping.

**Verdict on stealth edits:** clean.

## Adversarial pattern hunt (additional probes that did not produce findings)

- Conference-prefix histogram: every cited count (omae=6234, otc1=2904, etc.) reproduces exactly. No fabrication.
- Curated-vs-stub ratio (30 : 19,166 = ~1:639) is arithmetically correct.
- "959× understatement" claim for stale overview: actual = 19,199, overview-cited = 20, ratio = 959.95 — claim accurate to the integer rounding stated in the plan (line 178 says "959×", line 63 says "960×"; minor internal inconsistency by 1 between the two phrasings, not worth a separate finding).
- The plan correctly identifies that `raw/` cannot be the audit baseline (only 5 seeds vs 19,166 wiki sources because the 19,166 came from `/mnt/ace/docs/conferences/...` external corpora) and pivots to ITTC + SNAME as the verifiable taxonomy. The methodology pivot rationale survives scrutiny — verified via inspection of frontmatter `path:` field on multiple sampled stubs which all point at `/mnt/ace/docs/conferences/...`, not `raw/`.
- The "no marine wiki page wired into citation registry" claim verified: `grep -c "knowledge/wikis/marine-engineering/wiki/" digitalmodel/src/digitalmodel/citations/registry.py` returns 0.
- Sub-discipline coverage gap (Seakeeping / station-keeping / DP / fatigue / metocean named as missing): cross-checked against the 14 concepts on disk. The plan's list of absent sub-disciplines (line 30, line 65) is accurate — none of the 14 concept files cover Seakeeping (RAOs, motions, wave-frequency response), DP/spread-mooring station-keeping, jacket/topsides/hull fatigue, intact/damaged stability of floating units, or wave-environment characterization.

---

## Verdict

**MINOR** — 5 minor findings, 0 major.

The plan is fundamentally sound: every quantitative claim reproduced live, the audit-only scope is enforced both in prose and on disk, the TDD test list maps cleanly to acceptance criteria, the methodology pivot to ITTC anchors is correct given that `raw/` is only 5 seeds, and tense discipline is clean. The minor findings are citation-quality (URL anchors on the surface page rather than the deeper page that actually exposes the taxonomy), one drift-budget framing nit, and one execution-time co-creation observation. Each is fixable with a sub-line edit and none alters the plan's structural decisions.

The plan's biggest risk — that it produces a 19,166-file mapping exercise with weak discipline-attribution — is correctly mitigated by anchoring rationales to ITTC procedure numbers and the literal-string SNAME anchor, *both enforced by `test_audit_rationales_cite_required_anchors`*. That test is the load-bearing piece of this audit; it is well-designed.

## Counts

- MAJOR_COUNT: 0
- MINOR_COUNT: 5
