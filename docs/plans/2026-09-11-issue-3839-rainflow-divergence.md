# Plan for #3839: rainflow paths that understate stress range

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-09-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3839
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-11-plan-3839-claude.md | ...-codex.md | ...-gemini.md

---

## Scope decision

The issue as filed proposes consolidating seven counting paths onto one. This plan does **not** do that, and the reason is a sequencing constraint rather than a reduction in ambition: retiring an implementation before a correctness gate exists removes the evidence needed to judge what the retired implementation produced, and selecting a survivor is a separate question from removing the defective ones.

This plan therefore delivers the gate, the interim safety measure, and the exposure record. Consolidation follows in a successor issue, which the gate makes safe.

**Deferral does not mean leaving the failing paths callable for damage calculation.** Both reviewers raised that marking failures as expected-fail while the paths stay in service would leave the repository no safer than doing nothing, and could leave it worse by presenting a green suite. A failing path must therefore **refuse damage calculation** as part of this plan, not the successor. Refusal is the interim safety measure; deletion is the successor's work.

The per-path behaviour record that justifies the deferral is committed, not left in a scratch directory — otherwise the argument that consolidation would destroy evidence has no artifact behind it.

---

## Resource Intelligence Summary

### Existing repo code

- Found: seven cycle-counting paths. Four are classes named `RainflowCounter` in four modules; the others are a pyLife wrapper, a PyPI `rainflow` import, and `RainflowFatigue`.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/opp_time_series.py:458` calls `OrcFXAPIObject.RainflowHalfCycles(...)`. The engine's OrcaFlex post-processing route uses OrcaFlex's own rainflow and consumes none of the seven.
- Found: `digitalmodel/src/digitalmodel/signal_processing/signal_analysis/orcaflex/analyzer.py:16` imports `RainflowCounter` from `..core.rainflow` and constructs it at line 46. This is the failing path's live consumer.
- Gap: no test asserts a correctness property on broadband input. Every failing implementation passes the narrow-band case.
- Gap: `opp_time_series_v2.py` has no consumer in `src/` and is unreachable from the engine.

### Standards

| Standard | Status | Source |
|---|---|---|
| ASTM E1049-85(2023) | referenced, not read — paywalled | store.astm.org |

The plan introduces no standards-derived numeric constant, so no `Citation` sidecar is required. The S-N curve tables, which do carry standards-derived constants, are out of scope.

### LLM Wiki pages consulted

No relevant wiki pages. The invariant used here is a property of cycle counting, not a standards-derived value.

### Documents consulted

- Issue #3839 body and its two correcting comments.
- `digitalmodel/tests/structural/fatigue/test_rainflow.py:123` — asserts `max_range == 100.0`, showing the suite does test the right property but only on a signal that does not expose the defect.
- `digitalmodel/src/digitalmodel/solvers/orcaflex/opp.py:29` — imports `opp_time_series`, version 1, establishing the live route.
- `.claude/rules/mechanism-before-publication.md` — the blast-radius claim in the first issue comment was published from imports without tracing reachability and was corrected; that correction is recorded here as the reason the plan leads with the gate rather than with consolidation.

### Gaps identified

- No correctness gate exists for cycle extraction anywhere in the repository.
- Whether any deliverable was produced through a failing path is not established.
- The exposure cannot be dated: `git log` for the affected files returns a single commit.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-09-11 via `gh issue list`):
- `#3839` — OPEN — fix(digitalmodel/fatigue): two of four rainflow paths understate stress range, understating damage

**File existence** (verified 2026-09-11):
- EXISTS: `digitalmodel/src/digitalmodel/signal_processing/signal_analysis/core/rainflow.py`
- EXISTS: `digitalmodel/src/digitalmodel/marine_ops/marine_engineering/calm_buoy_fatigue.py`
- EXISTS: `digitalmodel/src/digitalmodel/structural/fatigue/rainflow.py`
- EXISTS: `digitalmodel/src/digitalmodel/structural/fatigue_apps/rainflow_counting.py`
- EXISTS: `digitalmodel/src/digitalmodel/structural/fatigue_apps/rainflow_counter.py`
- MISSING (new — this plan creates): a shared invariant test module

**Line excerpts** — the live route does not use an in-house counter:

```
opp.py:29:  from digitalmodel.solvers.orcaflex.opp_time_series import OPPTimeSeries
opp_time_series.py:458:  rain_flow_half_cycles = OrcFXAPIObject.RainflowHalfCycles(
```

**Gap proofs**:
- `grep -rn "opp_time_series_v2" digitalmodel/src` → matches only inside `opp_time_series_v2.py` itself → confirms the module is orphaned.

**Reproduction proofs**:

Each path was invoked through its public entry point on four deterministic signals. The invariant is that a correct rainflow count extracts a maximum range equal to the signal's peak-to-valley span, since the largest excursion always appears as a full or half cycle.

```
signal                    span    pylife_4pt  pypi_rainflow   sigproc_astm      calm_buoy  fapps_counting  fapps_counter  struct_fatigue
astm_example               9.0          PASS           PASS       FAIL 6.0       FAIL 7.0            PASS           PASS            PASS
narrow_band_sine         100.0          PASS           PASS           PASS      FAIL 50.0            PASS           PASS            PASS
broadband_random      177.1224          PASS           PASS  FAIL 125.2664  FAIL 106.3779    FAIL 169.556           PASS    FAIL 169.556
residual_dominated    201.2606          PASS           PASS  FAIL 190.6564  FAIL 200.6303   FAIL 200.6303           PASS   FAIL 200.6303
```

Total counted cycles agree across all seven paths on every signal (4.0, 10.5, 1370.0, 20.5), so the divergence is confined to the ranges assigned.

```
$ pytest tests/signal_processing/signal_analysis/ tests/structural/fatigue/test_rainflow.py \
         tests/structural/fatigue_analysis/test_rainflow_counter.py -q
174 passed in 5.28s
```

Input signals, stated exactly so the result is reproducible without the harness:

| Signal | Definition |
|---|---|
| `astm_example` | `[-2, 1, -3, 5, -1, 3, -4, 4, -2]` |
| `narrow_band_sine` | `50·sin(t)`, `t = linspace(0, 10·2π, 640, endpoint=False)` |
| `broadband_random` | `default_rng(20260911).normal(0, 25, 4096)` |
| `residual_dominated` | `linspace(0, 200, 512) + 8·sin(linspace(0, 40π, 512))` |

Each path was called through its public entry point; `_rainflow_algorithm` was **not** called directly, since it takes pre-extracted reversals and an earlier run that did so was discarded as outside its contract. The harness is currently a scratch script; committing it as the per-path behaviour record is acceptance criterion 6.

- Reproduced at: 2026-09-11
- Failure mode observed matches issue claim: **YES for the invariant failures; NO for the blast radius as originally filed.** The engine route is unaffected; the consumers are standalone fatigue scripts, documentation examples and `time_trace_processor.py`. The issue body was corrected by comment and this plan is scoped to the corrected finding.

Distinct sources consulted: 4 — the issue body, the repository source (read, with the mechanism located at `core/rainflow.py:162-164`), the test-suite run above, and `.claude/rules/mechanism-before-publication.md`. The invariant derivation is reasoning rather than a source and is **not** counted. Minimum 3 met.

**Standards-evidence limitation.** The contract is scoped to the project's declared convention, not to a standard. ASTM E1049-85(2023) is paywalled and was not read, so no clause here is presented as a standards requirement. Should the contract later be asserted as ASTM conformance, that assertion requires reading the standard first.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-09-11-issue-3839-rainflow-divergence.md |
| Tests | `digitalmodel/tests/fatigue/test_rainflow_invariants.py` |
| Implementation | `digitalmodel/src/digitalmodel/fatigue/counting_contract.py` |
| Exposure record | `digitalmodel/docs/domains/fatigue/rainflow-path-exposure-2026-09-11.md` |
| Plan review — Claude | scripts/review/results/2026-09-11-plan-3839-claude.md |
| Plan review — Codex | scripts/review/results/2026-09-11-plan-3839-codex.md |
| Plan review — Gemini | scripts/review/results/2026-09-11-plan-3839-gemini.md |

---

## Deliverable

A shared correctness contract for cycle counting, applied as a parametrised test across every counting path in the repository, together with a recorded verdict per path and a documented exposure assessment of the failing paths' consumers.

---

## Pseudocode

```
# The contract is stated against a DECLARED convention, because clause 1 is not
# universal: an implementation that DISCARDS residuals rather than counting them
# as half cycles can correctly omit the global span. Each registered path declares
# its residual policy; clause 1 applies only to retain-residual paths.
#
# Every path measured here declares retain-residual, and the evidence is that
# total counts agree across all seven and end in .5 (10.5, 20.5). The divergence
# is therefore not a convention difference.

function assert_counting_contract(path, signal):
    ranges, means, counts = path.count(signal)
    span = max(signal) - min(signal)
    reversals = turning_points_with_endpoints(signal)   # defined once, in the contract

    # 1. Largest excursion is extracted — retain-residual conventions only.
    #    The global peak and valley are necessarily a reversal pair.
    if path.residual_policy == RETAIN:
        assert max(ranges) == approx(span)

    # 2. Nothing is counted that the signal does not contain.
    assert max(ranges) <= span + tol

    # 3. Count conservation — exact, not approximate. Each reversal participates
    #    in exactly one extracted range, so for a retain-residual count:
    assert 2 * sum(counts) == len(reversals) - 1
    assert every count is a positive multiple of 0.5
    assert no emitted range is zero

    # 4. Exact distribution on at least one hand-checkable signal, because
    #    clauses 1-3 are aggregate and a counter fabricating counts could
    #    satisfy them. See CONTRACT_EXACT below.
```

```
# The hand-counted fixture. Ranges/means/counts are derived by hand from the
# ASTM worked sequence and committed as literals, so the test does not depend
# on any implementation being correct.
CONTRACT_EXACT = {
    "signal":   [-2, 1, -3, 5, -1, 3, -4, 4, -2],
    "expected": [ (range, mean, count), ... ]   # populated during implementation,
                                                # hand-derived and reviewed, never
                                                # captured from a running counter
}
```

```
# Applied across every path, so a new counting path cannot be added ungated.
PATHS = discover_counting_paths()        # explicit registry, not import scanning
for path in PATHS:
    for signal in CONTRACT_SIGNALS:      # includes broadband, which nothing tested
        assert_counting_contract(path.count, signal)
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `digitalmodel/src/digitalmodel/fatigue/counting_contract.py` | the contract, callable by tests and by callers |
| Create | `digitalmodel/tests/fatigue/test_rainflow_invariants.py` | parametrised across every path |
| Create | `digitalmodel/docs/domains/fatigue/rainflow-path-exposure-2026-09-11.md` | per-path verdict and consumer list |
| Modify | failing modules | mark failing paths as not fit for damage calculation, pending the successor issue |
| Update | docs/plans/README.md | add this plan to the index |

---

## TDD Test List

| # | Test | Asserts |
|---|---|---|
| 1 | exact distribution over a passing path, `CONTRACT_EXACT` | emitted `(range, mean, count)` equals the hand-derived table exactly |
| 2 | contract over `pylife_4pt`, four signals | passes all clauses |
| 3 | contract over `pypi_rainflow`, four signals | passes all clauses |
| 4 | contract over `fapps_counter`, four signals | passes all clauses |
| 5 | contract over `sigproc_astm`, broadband | fails; `xfail(strict=True)` with the issue number |
| 6 | contract over `calm_buoy`, narrow-band sine | fails; `xfail(strict=True)` with the issue number |
| 7 | contract over `fapps_counting` and `struct_fatigue`, broadband | fails; `xfail(strict=True)` with the issue number |
| 8 | a counter returning one full-span half cycle and fabricated counts | fails clause 3 — proves clauses 1 and 2 are not sufficient alone |
| 9 | a counter returning the correct count total but wrong ranges | fails clause 1 or 4 |
| 10 | a declared discard-residual counter omitting the span | passes — proves clause 1 is correctly conditional and does not condemn a valid convention |
| 11 | a constant signal | zero span handled without division |
| 12 | a two-point signal | degenerate case handled |
| 13 | each failing path invoked for damage calculation | raises, naming the issue |
| 14 | registry completeness over the known fatigue and signal-processing packages | fails when a counting-named callable in those packages is unregistered |

Tests 5 to 7 use `xfail(strict=True)`, so a repaired path reports as a failure demanding the marker's removal rather than passing silently as `XPASS`.

Tests 8 to 10 are the contract's own tests. Without them the contract is unfalsifiable: 8 and 9 prove it rejects fabrications, and 10 proves it does not condemn a legitimate discard-residual implementation.

Test 14 is scoped to what it can deliver — a callable matching a counting-name pattern within the known packages. A counting implementation under a novel name in an unrelated package escapes it, and the plan does not claim otherwise.

---

## Exposure assessment

The record shall state, per failing path, its consumers and whether any produced a deliverable. Known at planning time:

| Failing path | Consumers |
|---|---|
| `sigproc_astm` | `signal_analysis/orcaflex/analyzer.py:16,46`; `solvers/orcaflex/time_trace_processor.py:253,266,435,438`; `opp_time_series_v2.py:259` and its `OrcaFlexTimeTraceProcessor` use at `:22,128,197,236`; `TimeSeriesAnalyzer` consumers under `tests/.../fatigue_analysis_reference/`; `docs/domains/examples/orcaflex_signal_analysis_example.py` |
| `calm_buoy` | `calm_buoy_fatigue.py:370,571` internal use |
| `fapps_counting`, `struct_fatigue` | to be enumerated from the committed inventory |

The inventory is **call-graph derived, not import-scan derived**. An import scan over `src/` alone understates the exposure: it misses documentation examples, standalone scripts, and modules reachable only through a public entry point.

`opp_time_series_v2.py` is recorded as **"no current `src` importer found"**, not as unreachable. It is constructed by a committed documentation example, and the blanket word "orphaned" in an earlier draft overstated what the evidence supports.

Eight scripts under `scripts/python/digitalmodel/tools/` import `digitalmodel.modules.signal_analysis.orcaflex`, a module path that does not match the current layout. Whether they ran against an earlier layout is **not established** and the exposure record shall say so rather than assume either way.

**Deliverable exposure is explicitly deferred.** Establishing whether an issued result used a failing path requires access to client repositories, which is outside this plan's scope and requires the owner's direction. The record shall name that as an open item rather than resolve it.

---

## Acceptance Criteria

1. A counting contract exists, is callable independently of any test framework, declares its residual-policy condition, and is not trivially satisfiable — proven by tests 8 and 9, and shown not to over-reach by test 10.
2. Every counting path is registered with its declared residual policy and exercised against the contract, with a recorded verdict, including the exact-distribution check on the hand-derived fixture.
3. A counting-named callable in the known fatigue and signal-processing packages cannot be added without registration — proven by test 14.
4. **Every failing path refuses damage calculation**, naming this issue in the error — proven by test 13. A green suite therefore does not mean a failing path is still usable for damage.
5. The exposure record is call-graph derived, lists every failing path with its consumers including documentation examples and scripts, and names the deliverable question as an open item pending owner direction.
6. The per-path behaviour record is committed, so the evidence the deferral argument rests on survives the session.
7. The existing 174 rainflow tests continue to pass.

---

## Adversarial Review Summary

| Wave | Reviewer | Verdict | MAJOR | MINOR |
|---|---|---|---|---|
| r1 | Claude, inline | APPROVE-WITH-CHANGES | 2 | 4 |
| r2 | Codex | REJECT | 4 | 2 |
| r2 | Gemini / agy | UNAVAILABLE — not installed on this host | – | – |

T2 scope requires two providers; Claude and Codex satisfy it, and the Gemini lane is recorded UNAVAILABLE per the existing `scripts/review/results/` convention rather than blocking.

**Convergent findings**, raised independently by both reviewers and therefore carrying the most weight:

- The invariant was stated as universal and is not. It holds only for a retain-residual convention. Clause 1 is now conditional on a declared policy, test 10 proves it does not condemn a valid discard-residual implementation, and the plan records why the objection does not rescue the measured paths: total counts agree across all seven and end in `.5`, and the mechanism was read from source at `core/rainflow.py:162-164`, where the three-point comparison and the extracted range are both inverted.
- Contract clause 3 was under-specified and unimplementable. It is now an exact count-conservation equality, with a hand-derived exact-distribution fixture added because aggregate clauses alone can be satisfied by fabricated counts.

Further revisions made in r3, applied inline without a further review dispatch:

- Failing paths must refuse damage calculation within this plan rather than the successor. Deferring consolidation while leaving them callable behind a green suite would have left the repository no safer.
- The exposure inventory became call-graph derived. An import scan over `src/` missed `time_trace_processor.py:253,266,435,438` and a committed documentation example.
- "Orphaned" and "unreachable" were withdrawn for `opp_time_series_v2.py` in favour of "no current `src` importer found" — the evidence supports the narrow claim, not the broad one.
- `xfail` is strict, so a repair surfaces rather than passing silently.
- The registry guard's scope was narrowed to what a name-pattern scan can actually deliver.

---

## Risks

| Risk | Mitigation |
|---|---|
| The invariant is wrong, so correct implementations are condemned | Clause 1 is derived from the definition of a reversal rather than from a reference implementation, and three independent paths satisfy it on all four signals. Test 7 proves the contract rejects a degenerate counter. If a reviewer shows a correct counter that fails clause 1, the contract is withdrawn, not the implementations. |
| Marking failures as expected-fail hides them | Criterion 4 requires the exposure record, and each expected-fail carries the issue number so it surfaces in any triage |
| The successor consolidation never happens and expected-fails become permanent | The successor issue is filed before this one closes, and referenced from the expected-fail markers |
| A failing path is repaired rather than retired, and the repair is wrong | The contract gates the repair; a repaired path must pass all clauses on all signals before the marker is removed |

---

## Out of Scope

Selecting the surviving implementation and deleting the others. S-N curves, mean-stress correction, thickness correction. Access to client repositories to establish deliverable exposure.
