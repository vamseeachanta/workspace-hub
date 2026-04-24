# Adversarial Review — Issue #279 Plan (WRK-129 OrcaFlex Reporting Standardization)

**Reviewer stance:** adversarial / defect-hunter
**Review date:** 2026-04-24
**Plan under review:** `docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md`
**Intel consulted:** `/tmp/orca-batch-2026-04-24/intel-279.md`
**Issue body consulted:** `/tmp/orca-batch-2026-04-24/issue-279-body.txt`
**Live-code verification:** directory listings + grep against `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/` and `digitalmodel/src/digitalmodel/orcaflex/reporting/` on 2026-04-24.

---

## Verdict

**REQUEST_CHANGES** — 3 MAJOR, 5 MINOR. Plan cannot ship as-is.

Rationale: the plan correctly identifies the vessel gap and legacy tradeoff (the two marquee defects the intel warned about), but it (a) omits a spec-mandated deliverable (golden HTML examples at a hard-coded docs path), (b) ignores the `docs/modules/` vs `docs/domains/` rename-risk the batch brief explicitly required, and (c) ships spurious TDD items based on an already-refuted premise (the "boundary_conditions not wired" gap). These are not rhetorical nits — they will either produce failing acceptance checks or waste review/CI budget on fabricated tests.

---

## Defect checklist

| # | Check | Status |
|---|---|---|
| 1 | Plan acknowledges existing 2823-line framework (NOT framed greenfield) | PASS |
| 2 | Legacy `digitalmodel/orcaflex/reporting/` path: deprecate/merge/coexist tradeoff explicit | PASS |
| 3 | Vessel renderer scoping (the main intel gap) | PASS with MINOR gap (M2) |
| 4 | `docs/modules/` → `docs/domains/` directory-rename risk (task brief: same failure mode as #510) | **FAIL (MAJOR-1)** |
| 5 | Spec's golden-HTML-example deliverable at `docs/modules/orcaflex/reporting/examples/` | **FAIL (MAJOR-2)** |
| 6 | TDD items grounded in live code (no fabricated tests) | **FAIL (MAJOR-3)** |
| 7 | Dispatch-map pseudocode matches current shape | FAIL (MINOR-1) |
| 8 | `from_dict()` offline path elevated to acceptance (spec P-requirement) | FAIL (MINOR-2) |
| 9 | `structure_types/` empty-package decision bounded | PASS |
| 10 | XSS/SRI L2 enforcement guards added | PASS |
| 11 | Per-type snapshot fixtures scoped | PASS |
| 12 | `#282` (OrcaWave) scope boundary stated | PASS |
| 13 | Intel source-count footnote accurate | FAIL (MINOR-3) |
| 14 | Complexity T2 justified against gap set | PASS |
| 15 | Adversarial-review artifacts pre-declared at Artifact Map | PASS |
| 16 | Risks section names the "re-cross-review against as-shipped" action | PASS |
| 17 | Acceptance Criteria gate "Plotly 2.26.0 wheel installed" vs SRI pin drift | FAIL (MINOR-4) |
| 18 | Plan cites the Codex-iter-14 APPROVE / Gemini-NO_OUTPUT-x14 lineage & mitigates | FAIL (MINOR-5) |

---

## Specific defects

### MAJOR-1 — `docs/modules/` rename-risk ignored (repeat of #510 failure mode)

The batch brief explicitly required the plan to address the `docs/modules/` → `docs/domains/` directory rename risk. The plan contains **zero** references to `docs/modules/`, `docs/domains/`, or rename risk. Verified:

```
grep -n "docs/modules\|docs/domains" docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md
# (no matches)
```

Yet the issue body hard-codes the path five times (issue-279-body.txt lines 870, 876, 945, 1155, 1318), including in an acceptance criterion:

> line 945: "≥ 2 example HTML reports committed to `docs/modules/orcaflex/reporting/examples/`"

If `docs/modules/` is on the rename slate (as the brief implies — same failure mode as #510), then this plan will either (a) commit examples to a soon-to-be-stale path, or (b) silently drop the deliverable. Plan must name the risk, cite the current state of the rename decision, and specify whether examples land at `docs/modules/...` or `docs/domains/...`.

**Required fix:** add a dedicated Risk bullet and, in Files to Change, bind the examples path to a single canonical variable / decision so the rename doesn't race.

### MAJOR-2 — Spec-mandated golden HTML examples deliverable missing from Artifact Map, Files to Change, and Acceptance Criteria

Issue body Acceptance Criterion (line 945): *"≥ 2 example HTML reports committed to `docs/modules/orcaflex/reporting/examples/`"*. Also referenced at line 876 ("Commit golden HTML files for riser and mooring examples") and line 1155 ("Golden HTML baselines").

The plan's Artifact Map (lines 82–98), Files to Change (lines 176–195), and Acceptance Criteria (lines 222–233) do not include any `docs/modules/orcaflex/reporting/examples/*.html` entry. The "per-type snapshot fixtures" at `digitalmodel/tests/.../fixtures/` are a different artifact — they are pytest snapshots, not the committed example HTML the spec requires as a user-facing deliverable.

**Required fix:** add an Artifact Map row, a Files-to-Change row, and an acceptance-criterion checkbox for at least two committed `.html` golden reports. Resolve jointly with MAJOR-1 on path binding.

### MAJOR-3 — Fabricated TDD item: `test_boundary_conditions_wired_in_aggregator`

Plan line 214 lists: *"test_boundary_conditions_wired_in_aggregator | `boundary_conditions_extractor` called by `aggregator.extract_all()`"*. This is rooted in Gap #8 ("wiring audit ... import path into `aggregator.py` unverified") which the intel itself only flagged as TODO. **Live-repo verification refutes it:**

```
grep -n "boundary_conditions_extractor" digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/aggregator.py
# aggregator.py:24:from .boundary_conditions_extractor import extract_boundary_conditions
```

The extractor is imported at the top of the aggregator. A test asserting "it is wired" is either a no-op (if it just checks the import) or is testing behaviour the plan has no stated reason to believe broken. Plan should either:
- Drop the test + drop Gap #8 from the Gaps list, OR
- Specify the *observable defect* that makes the wiring-test non-trivial (e.g., "call-count in `aggregator.extract_all()` not yet asserted under FPSO fixture").

As-written, this is a spurious green test inflating TDD volume on a false premise.

### MINOR-1 — Dispatch pseudocode misrepresents current shape

Plan lines 140–147 show:
```
renderer_map = {"pipeline": PipelineRenderer, "riser": RiserRenderer, ...}
```
Live `report_generator.py` uses an `if/elif` ladder (verified lines 61–74). Adding vessel is therefore either (a) append an `elif` branch (minimal), or (b) refactor to a dict (the plan's apparent intent). The plan does not call out this refactor, does not add a regression test for dispatch-parity across the refactor, and does not surface it as a risk for reviewer diff scope. Either call the refactor out explicitly or fix the pseudocode to match the append-`elif` path.

### MINOR-2 — `from_dict()` offline-construction path not promoted to acceptance

Issue body (and intel Gap #6) treat OrcFxAPI-free construction as a P-level requirement — fixtures must be constructable without a live OrcFxAPI license. Plan only tests this for `VesselExtract` (TDD row `test_vessel_from_dict_no_orcfxapi`, line 208) and buries it in a single Risk bullet. Acceptance Criteria (lines 222–233) contains no checkbox for "all 11 Pydantic models in `models/` constructable from `dict` without OrcFxAPI handle, proven by test" — which is what the spec actually demands across the framework, not just vessel.

### MINOR-3 — Intel source-count footnote inaccurate

Plan line 76: *"Source count: issue body + pod intel + batch-design plan + intensive-plan + legacy module listing = 5 distinct sources."* But the Resource Intelligence Summary also cites `#282` (line 41) and WRK-125/127/045/046/064 (line 42). Count is ≥ 6 plus the issue-reference cluster. Either fix the footnote or remove it; if the 5-source bar is a policy minimum, inflating it silently is worse than under-reporting.

### MINOR-4 — SRI pin-drift guard protects only the `PLOTLY_JS_VERSION` constant, not the SRI hash itself

`report_generator.py` pins both `PLOTLY_JS_VERSION = "2.26.0"` AND a `PLOTLY_JS_SRI` hash (line 44 comment: "Update PLOTLY_JS_VERSION and PLOTLY_JS_SRI when upgrading"). The plan's `check-plotly-sri-pin.sh` pseudocode (lines 158–161) compares `PLOTLY_JS_VERSION` vs. the wheel version, which catches wheel↔version drift but NOT SRI-hash↔version drift. If a dev bumps `PLOTLY_JS_VERSION` to `2.27.0` and forgets to update `PLOTLY_JS_SRI`, this guard passes silently and the CDN script tag fails integrity-check at the browser. Guard scope must include recomputing/verifying the SRI for the declared version.

### MINOR-5 — Spec lineage not mitigated

Plan line 37 notes *"Codex APPROVE iter 14, Gemini NO_OUTPUT x14"* and Risks bullet (line 258) says re-cross-review is *"prudent before close"*. But the plan does not wire re-cross-review into Acceptance Criteria or schedule it. `NO_OUTPUT x14` is a suspicious signal (tool failure vs. actual no-output ambiguity) and a single-reviewer APPROVE does not match this repo's triple-provider gate policy. Acceptance should explicitly require fresh Claude + Codex + Gemini reviews against the as-shipped code before `status:plan-approved` — not file it under "prudent".

---

## Justification summary

- Plan gets the **framing** right (T2 completion, not T3 greenfield) and **correctly identifies** the two central defects the intel flagged (vessel + legacy tradeoff).
- Plan **misses** two brief-mandated checks (docs-path rename + golden-HTML examples) that are spec-load-bearing, not cosmetic.
- Plan **imports one unverified intel claim as a TDD test**, which the user's own "commit attestation narrow scope" / "gh-connector evidence needs local verify" memory specifically warns against.
- Minor defects center on pseudocode-vs-reality drift (dispatch), scope of enforcement guards (SRI), and ungated acceptance items (`from_dict`, re-cross-review).

Fix MAJOR-1 through MAJOR-3 and the plan is approvable at T2. MINORs can be addressed in the same revision pass without scope creep.

---

## Forbidden-behaviour self-check

- No charitable re-reading; every defect cites a file+line or a grep result.
- No new scope invented — all findings map to either (a) the brief's explicit #279-specific checks, (b) the issue body's own acceptance criteria, or (c) live-code contradiction of plan claims.
- Verdict is `REQUEST_CHANGES`, not `APPROVE_WITH_NITS`, because MAJOR-1/2 would fail an acceptance-criterion audit at close and MAJOR-3 would waste reviewer cycles on a test that cannot meaningfully fail.
