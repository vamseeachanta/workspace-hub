# Mooring-buoy code review and inline disposition

Issue: [digitalmodel 2093](https://github.com/vamseeachanta/digitalmodel/issues/2093). The user approved the reviewed revision-3 plan. This record preserves provider disagreement; it does not claim unanimous approval.

## Codex independent defect hunt

Verdict: **REQUEST_CHANGES**, two reproduced MAJOR findings.

1. The case contract omitted native readback of current profile, line-type stiffness/mass/drag, clump and attachment data, anchor coordinates and buoy damping/hydrodynamic coefficients. Main expanded the pinned contract using source properties and checked-in native C07 property names. Selected nested cylinder properties require exact values and list lengths while permitting unrelated export metadata. RED: one failure/three passes; GREEN: four passes. No physical coefficient or solver setting was changed.
2. The parent accepted a minimal child success report without completed stages, input verification or numeric arrays. A fake-only reproduction demonstrated the false pass. Main added `model_proof.py`, mandatory source hashing and independent parent validation of completeness, finite arrays, all six histories, exact main-stage coverage, manifest identity and corresponding saved/reloaded results. Missing-module RED preceded 15 passing proof tests. An additional native-export hash mismatch test was RED, then repaired by hashing the retained export independently. Fake children exercise real Windows containment; no native licence is used by these tests.

## Claude review

[Actual Claude response and reviewed hashes](2026-09-11-digitalmodel-2093-claude-code-review.md): **MAJOR**, one bounded Haiku call, exit zero. Main checked each finding against local source:

| Finding | Disposition and evidence |
| --- | --- |
| JSON float spelling causes equivalent contract mismatch | Not reproduced. Both parsed structures pass through the same JSON encoder; source exponent spelling is absent by comparison time. Type-sensitive serialization deliberately rejects boolean substitution. Manifest generation and verification tests pass. |
| `isinstance(count, bool) or count != 1` accepts True | Incorrect Boolean reasoning: its first operand is true and raises. Parent additionally requires exact integer type. |
| Readback permits nonfinite values | `numbers()` validates every extracted static/dynamic array with `math.isfinite` before comparison; nonfinite tests pass. New independent parent validation also rejects NaN, booleans and incomplete arrays. Exact numeric equality does not promise bitwise distinction of signed zero. |
| Time-grid tolerance ignores a future case | This is one pinned case. `histories()` first rejects any period contract other than the approved grid. No widened tolerance is supported or silently accepted. |
| Manifest can substitute comparison policy | Whole-contract type-sensitive equality rejects changed or missing fields; the native probe and parent require exact readback. `_tree` is an input hook scan, not the place for comparison policy. |
| Case-fold identities collide | Duplicate resolved, case-folded identities explicitly raise; conservative rejection on Linux is not acceptance of a collision. |
| Symlink escape passes | Resolved paths must remain relative to resolved bundle root. Resolution occurs before the containment check. |
| Duplicate export objects overwrite | `verify_export()` explicitly raises on duplicate names before assignment. |
| Cleanup race | No reproduction or viable post-drain spawn is supplied. Suspended roots enter a non-breakaway job before resume; cleanup observes root exit and whole-job zero activity before closing. Query/termination uncertainty fails and prevents readback. Existing fake-process/descendant tests pass. |
| Required-results test has no results field | The qualification contract contains `results`; the run manifest embeds that entire contract. The cited test passes. |

No round-three provider fanout was performed. Main applied the reproduced fixes inline and rechecked integration. The final focused run passed **178 tests in 19.36 seconds**, including all smoke contracts, model preparation/probe/proof/containment checks and GeneralBuilder regressions. This is offline software evidence; native acceptance is recorded separately after the bounded run.

## Remaining boundaries

The contract describes the selected mooring case only. Exact result readback is storage fidelity, not numerical or physical validation. Source defaults, arbitrary example damping, reference incompatibilities, strength basis and deployment qualification remain explicit report limitations. No repeated solve or convergence campaign is authorized by this review disposition.

The generalizable incomplete-parent-proof defect has been promoted to the existing [proof completeness audit 2085](https://github.com/vamseeachanta/digitalmodel/issues/2085#issuecomment-5640611414), rather than remaining only in this review record.

Final reporting artifact review found one MINOR UTF-8 encoding issue in the HTML/Markdown reports, corrected inline and reverified. No false native completion, count contradiction or broken local report link was found. The sole attempt failed at licence checkout before loading; retained JSON records zero completed solves.
