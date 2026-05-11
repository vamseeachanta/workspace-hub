# Claude self-review — digitalmodel PR #599 (issue #515 Approach A)

**Reviewer:** Claude (author of the work — disclosed self-review for transparency)
**Date:** 2026-05-11
**PR:** https://github.com/vamseeachanta/digitalmodel/pull/599
**Verdict:** **MINOR** — work is well-scoped and tested, but the cumulative diff carries 4 honest weaknesses worth surfacing to a reviewer.

---

## Disclosure

This is a self-review by the implementing agent. Per `route:B` cross-review policy, Codex + Gemini reviews run in parallel and are the load-bearing external signal. This self-review exists to:

1. Provide a fresh-context structured walkthrough of the cumulative diff (the author's own narrative can mask which trade-offs are decisions vs. accidents).
2. Pre-surface known weaknesses so external reviewers know what's being defended vs. what's being apologized for.
3. Document any "intentional MINOR debt" so the user can decide whether to require iter 8.

---

## Strengths (4)

### S1 — Verdict-diff discipline preserved baseline across the highest-risk iteration

Iteration 4 (OQ-4 `values_equal` fix) captured 51 passing baseline, applied the fix, captured 75 passing post-fix, and confirmed BEFORE ⊆ AFTER before committing. The commit message records the diff inline. This is the canonical pattern for `feedback_attestation_enables_contradiction_detection` and the fact that the high-risk iteration shipped zero regression is direct evidence the discipline works.

### S2 — Reconciliation test caught real drift on first run

`test_skip_list_reconciliation.py` failed initially because the taxonomy doc used `DefaultViewDistortionX/Y/Z` shorthand while the code listed each axis separately. The fix expanded the doc rather than softening the test — preserving the assertion strength. This is exactly the silent-drift class of bug the mechanism exists to surface.

### S3 — Conditional classifications instead of flat ones

OQ-1 and OQ-2 both close as *conditional* C3 classifications (WindType-conditional, builder-track-conditional) with decision-table sub-sections in the taxonomy doc. Flat classifications would have either over-claimed ("always C3") or under-classified ("always C6 unless documented"); conditional shape matches engineering reality where property emission depends on model context.

### S4 — OQ-3 scaffold queues work for licensed-win-1 without polluting dev-primary

`pytest.importorskip("OrcFxAPI")` at module top + `@pytest.mark.solver` marker means the whole module either runs or skips cleanly. No per-test branching, no env-var checks scattered across functions. The `_EXPECTED_OVERRIDES` dict with rationale-string invariant + matching-key-in-_DEFAULTS invariant catches both incomplete and stale overrides.

---

## Weaknesses surfaced for review (4 MINOR, 0 MAJOR)

### W1 — MINOR: `test_allowed_diff_props_classified` uses a 10% soft threshold

`tests/solvers/orcaflex/test_skip_list_reconciliation.py::test_allowed_diff_props_classified` allows up to 10% of `ALLOWED_DIFF_PROPS` to be unclassified before failing. This was deliberate — `ALLOWED_DIFF_PROPS` has 50+ entries and the taxonomy can't catch up in iter 3. The risk: a future taxonomy author lets drift creep up to ~5 properties (below threshold) and the test silently tolerates it.

**Defense:** Iter 5 (OQ-1/OQ-2) tightened the C3 sub-policy tables; threshold should be tightened to `max(2, len(ALLOWED_DIFF_PROPS) // 20)` in a follow-up. Tracked under #517 close-out.

### W2 — MINOR: Registry has no SPM-buoy proof plan reference, points to #2472 plan

`MODEL_CLAIM_REGISTRY.yaml::c05_single_point_mooring` references `workspace-hub/docs/plans/2026-04-23-issue-2472-calm-spm-buoy.md` as `proof_plan`, but the actual SPM family proof is not enumerated in that #2472 plan body (which focuses on CALM buoys). The reference is forward-looking but currently dangling.

**Defense:** Pending entries are inventory, not claims, so the dangling reference doesn't *over*-claim. But a reviewer could legitimately ask for a separate placeholder issue or a "TBD" sentinel rather than pretending a plan exists.

### W3 — MINOR: OQ-3 test depends on bare `OrcFxAPI.OrcaFlexError` exception class

`test_environment_defaults_vs_orcfxapi.py::test_default_matches_or_is_documented_override` catches `OrcFxAPI.OrcaFlexError` to handle mode-gated property access. If OrcFxAPI uses a different exception class name in a future version (e.g. `OrcFxError` or a typed hierarchy), the catch falls through and the test fails noisily on what should be a graceful skip.

**Defense:** This is the actual exception OrcFxAPI raises today, verified by the surrounding test suite (`tests/solvers/orcaflex/test_load_orcaflex_files.py` and similar). Future-proofing here would require speculative defensive code per the "no error handling for impossible scenarios" rule.

### W4 — MINOR: Claim-boundary doc §5.3 silent-substitution register is informational, not enforced

`SEMANTIC_EQUIVALENCE_CLAIM_BOUNDARY.md` §5.3 lists 21 silent-substitution properties from `_DEFAULTS`. The list is informational — there's no test asserting that user-facing spec-loading docs carry the recommended warning. If someone removes the warning from the user docs, the claim-boundary doc still says "user docs warn about this" without it being true.

**Defense:** This is by design — the warning's *location* (user-facing spec-loading docs) is outside `#515`'s scope. A future iteration could add an enforcement test that grepping user docs finds the warning string. Tracked as follow-up.

---

## Acknowledged out-of-scope deferred work

These are intentionally NOT in PR #599 and would expand scope beyond Approach A:

- **OQ-3 actual verification run** — requires licensed-win-1; queued by the scaffold.
- **L2 promotion for any family** — requires OrcFxAPI statics runs on licensed-win-1.
- **L3 attainability** — explicitly forbidden on generic track per claim-boundary §2.1.
- **Reverse-extraction scope expansion** — separate concern, already closed under #520 (commit `63c1cbdd`).
- **Wiki cross-link to #2476 cross-solver contract** — wiki page lands separately, then bidirectional link.

---

## Verdict reasoning

The 4 weaknesses are all *bounded MINOR*: each has a defensible rationale, none changes the claim-boundary semantics, none would block merge if the user agrees with the trade-offs. No MAJOR findings.

If the external reviews (Codex / Gemini) surface findings beyond W1–W4, those represent genuinely new perspective and should be weighted accordingly. If they surface only the same findings (or weaker variants), the route:B cross-review gate is satisfied by convergence.
