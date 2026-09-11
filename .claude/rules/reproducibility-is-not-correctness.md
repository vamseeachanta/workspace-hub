# Reproducibility is not correctness — agent rule

**When to apply:** writing or reviewing any test that guards a generated artifact — an input
deck, a config, a rendered report, a computed series — and any claim that such an artifact is
"covered" or "validated" by its test suite.

**Why:** a test that pins an artifact to the thing that produced it proves the producer is
deterministic. It proves nothing about whether the artifact is right. Both are useful; only
one is validation, and the two are routinely confused because a green suite reads the same
either way.

Two independent instances surfaced in one repository on one day, 2026-09-11:

- **Three Ansys example decks** were guarded by tests asserting the committed `.inp`
  byte-matches its generator's output. The guards were green. On the first run ever performed,
  one deck over-predicted peak stress by **3.8x** from an over-constraint that resisted its own
  thermal expansion, and a second had **never solved at all** — singular, because the element
  silently ignored the foundation stiffness it was given. A third defect in the same deck made
  the applied load a function of mesh density. ([digitalmodel#2094](https://github.com/vamseeachanta/digitalmodel/issues/2094))
- **Seven cycle-counting paths** were covered by 174 passing tests. A differential comparison
  against a peak-to-valley invariant found **four of the seven understate stress range**, in a
  direction that makes fatigue damage non-conservative. ([workspace-hub#3839](https://github.com/vamseeachanta/workspace-hub/issues/3839))

The shape is identical. Each suite asserted a relationship **between artifacts inside the
system** — deck against generator, output against previous output, implementation against
itself — and never a relationship between an artifact and a truth **outside** it.

**How to apply:**

1. **Name the comparator, and name its class.** Every artifact encoding physics or a
   calculation carries at least one assertion against something the producing system did not
   make. Classes, strongest first:

   | Class | Comparator | Drifts? |
   |---|---|---|
   | `closed-form` | Published analytical solution | No |
   | `measured` | Physical experiment | No |
   | `cross-solver` | An independent implementation, correlated | No, if both archived |
   | `conservation` | An invariant the result must satisfy | No |
   | `archived-run` | A prior run of the same code | **Yes** |
   | `none` | Nothing | — |

   `archived-run` is a regression guard, not evidence of correctness. An artifact whose only
   comparator is `archived-run` shall say so, in the artifact.

2. **Prefer the conservation check — it is nearly free and it catches whole classes.** A
   single reaction-sum line in each of the three decks above would have made every one of the
   three defects self-announcing: a large spurious reaction at the over-constrained node, an
   applied resultant 4.88 percent below the intended load, a near-zero reaction against an
   800 kN applied load. Equilibrium, mass balance, energy balance, count conservation,
   round-trip identity — ask what must be true regardless of the answer, and assert that first.

3. **Fix the tolerance before the run, not after.** "A tolerance stated at implementation" is a
   tolerance chosen once the discrepancy is visible, which launders the defect into the
   baseline permanently.

4. **Reject an assertion that cannot fail.** "Within its limit, or a stated exceedance" is
   satisfied by every real number. A skip on both branches is satisfied by every host. Read
   each assertion and ask what input would make it fail; if none would, it certifies nothing.

5. **A golden captured from code just changed proves self-consistency only.** Capturing one is
   correct practice, and it is not sufficient on its own. Pair the capture with a comparator
   from class 1, or label the golden `archived-run` and state the absence.

6. **Record the run configuration with the value.** A number reproduces only under the
   conditions that produced it. Solver version, argv, core count, parallel mode, platform, and
   the producing code's commit — otherwise a later mismatch reads as a regression, or a real
   regression reads as a configuration difference.

**Do NOT apply when:** the artifact encodes no physics and no calculation — a fixture whose
only contract is its own shape, a snapshot test of formatting, a serialisation round-trip.
Determinism is the whole requirement there, and a byte-match guard is the right tool.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose now. Level 2
candidate: a check that every committed golden directory carries a provenance record naming a
comparator class, failing when the class is absent and warning when it is `archived-run` or
`none`.

**Related:** [`mechanism-before-publication.md`](mechanism-before-publication.md) — its mirror
image. That rule is about publishing a cause you have not verified; this one is about trusting
a measurement that verifies nothing. [`patterns.md`](patterns.md).
