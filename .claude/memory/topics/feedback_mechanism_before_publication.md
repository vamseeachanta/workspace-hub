> Git-tracked snapshot from Claude auto-memory. Captured: 2026-09-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_mechanism_before_publication.md

---
name: feedback-mechanism-before-publication
description: Before publishing WHY a tool misbehaved, read its source and grep its existing output — a mechanism merely consistent with the symptom is a hypothesis
metadata:
  type: feedback
---

Before publishing a causal claim about why a solver, library or tool misbehaved, read the
source for the path you are blaming **and** grep output you already have for the quantity that
would settle it. A mechanism that is merely consistent with the symptom is a hypothesis, and
must be labelled one in the artifact.

**Why:** a plausible mechanism is more dangerous than none, because it ends the investigation
and produces the wrong fix. B1552, 2026-09-03: a VOF case gained 10 % domain volume; I
published that the shallow-water outlet model was computing from the wrong celerity in deep
water. True, sourced, consistent — and not the cause. `shallowWaterAbsorption.C`'s
`setVelocity` forces `U_x = U_y = 0` across the entire patch, so there is no mean outflow at
any depth; the regime mismatch causes reflection, and reflection is not mass gain. One file
read collapsed the reasoning.

Worse: `interFoam` prints `Phase-1 volume fraction` every timestep. Five runs printed it for
weeks, the controlled pair (`waveVelocity` +10.4 % vs `outletPhaseMeanVelocity` +0.001 %) sat
unread, and I filed an issue proposing to **build** that gate.

**How to apply:** blaming a code path obligates opening it — installed sources are on disk
(`$FOAM_SRC`, the site-packages path), so it is a file read, not a project. Before building a
diagnostic, grep an existing log for it. Prefer a controlled pair of runs you already have
over a new run. Label hypotheses as hypotheses *with the test that would settle them*. When a
published mechanism turns out wrong, correct it in place and name the correction — readers
acted on the first version.

Mirror image of [[feedback-metric-moved-work-did-not-happen]] (trusting a measurement that
proves nothing); see also [[feedback-absence-of-signal-reads-as-success]].
Full rule: `workspace-hub/.claude/rules/mechanism-before-publication.md`.
