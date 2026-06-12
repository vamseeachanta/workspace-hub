---
name: crossprovider codex cov-normalized-convergence-excludes-mean-for-zer
description: CoV-normalized convergence excludes mean for zero-mean signals
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [statistics, convergence-analysis, signal-processing, hydrodynamics]
---

For zero-mean hydrodynamic responses, coefficient-of-variation (CoV) convergence checks should exclude mean—it varies naturally across seeds and is not a meaningful indicator. Normalize CoV by amplitude reference (e.g., mean RMS) and check only std, rms, abs_max, abs_min instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
