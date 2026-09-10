# Mechanism before publication — agent rule

**Before publishing a causal claim about why a tool, solver, or library misbehaved — in a
report, an issue, a client deliverable, or a commit message — do two things first: (1) read
the tool's own source for the code path you are blaming, and (2) read the tool's own output
for a quantity that would confirm or refute you. A mechanism that is merely consistent with
the symptom is not a finding; it is a hypothesis, and it must be labelled as one until the
source or the output settles it.**

**Why:** a plausible mechanism is *more* dangerous than no mechanism, because it stops the
investigation. It reads as understanding, it survives review by anyone who shares the same
priors, and it propagates into the fix. The wrong mechanism produces the wrong fix.

The incident: a VOF ship-resistance case gained 10 % of its domain volume as water. The
published explanation was that the outlet boundary model computed its correction from the
wrong wave celerity, because the model is a shallow-water formulation and the case is deep
water. Every part of that is true and none of it was the cause. Reading
`shallowWaterAbsorption.C` showed `setVelocity` forcing `U_x = U_y = 0` across the entire
patch — no mean outflow at all, for either phase, at any depth. With a fixed-velocity inlet,
the domain fills. The regime mismatch causes large *reflection*; reflection is not mass gain.
One file read, and the deep-water reasoning collapses.

The second half is worse. `interFoam` prints `Phase-1 volume fraction` on **every timestep**.
Five runs across a multi-week campaign printed it, and the controlled pair was sitting in the
logs the whole time:

    waveVelocity outlet             0.813428 -> 0.89796    +10.4 %
    outletPhaseMeanVelocity outlet  0.813729 -> 0.813738   +0.001 %

An issue had been filed proposing to *build* a mass-conservation gate. The gate's measurement
already existed, unread, in the first line of every log.

**How to apply:**

1. **Blaming a code path obligates reading it.** Named a library function, a boundary
   condition, a scheme, a flag as the cause? Open its source and find the lines that would
   produce the behaviour. If you cannot point at them, you have a hypothesis. Vendored and
   system-installed sources are on disk — for OpenFOAM, `$FOAM_SRC`; for a Python package,
   the installed path. This is a file read, not a research project.

2. **Before building a diagnostic, grep the existing output for it.** Solvers, compilers,
   test runners and schedulers print far more than anyone reads. Ask what quantity would
   settle the question, then `grep` a log you already have for it. Only build the measurement
   after establishing it is genuinely absent.

3. **Prefer the controlled pair already in hand.** Long campaigns accumulate runs that differ
   in one setting. Two existing logs that bracket the variable beat a new run, and they cost
   a grep.

4. **Label hypotheses as hypotheses, in the artifact.** "The limiter is most active where the
   mesh is stretched, which is where the wave dies — this is a hypothesis, not a finding, and
   it is testable by X" is publishable. The same sentence without its last clause is not.

5. **Correct in place, and name the correction.** When a published mechanism turns out wrong,
   say which claim was wrong and what replaced it, rather than silently amending. Readers who
   acted on the first version need to know. This applies to issue bodies (add a correcting
   comment), report revisions (a named correction in the text), and commit messages.

**Do NOT apply when:** the claim is already sourced to the tool's own documentation or a
published paper that states the mechanism directly, OR you are describing an observation
rather than a cause ("the volume fraction rose 10 %" needs no source reading; "it rose
because X" does).

**Related:** `feedback_metric_moved_work_did_not_happen` (assert on the artifact, not a
correlated signal) is this rule's mirror image — that one is about trusting a measurement
that proves nothing; this one is about not reading a measurement that proves everything.
`feedback_absence_of_signal_reads_as_success` covers the third case.

**Incident reference:** a client hull-resistance CFD campaign, 2026-09-03.
[digitalmodel #2041](https://github.com/vamseeachanta/digitalmodel/issues/2041) was filed on
the wrong mechanism and corrected by comment the same day;
[#2043](https://github.com/vamseeachanta/digitalmodel/issues/2043) is the same source read
applied to shared library code.
