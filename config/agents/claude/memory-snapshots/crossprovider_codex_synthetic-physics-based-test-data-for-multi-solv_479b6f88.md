---
name: crossprovider codex synthetic-physics-based-test-data-for-multi-solv
description: Synthetic physics-based test data for multi-solver frameworks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, physics, mocks, multi-solver, benchmark]
---

When real solvers unavailable, generate approximate physics-based coefficients (RAOs, added mass, damping) with small controlled inter-solver variation (< 1% bias) to test consensus logic without live dependencies. Used in Unit Box benchmark: derived resonance frequencies, damping ratios, and frequency responses analytically, then applied solver-specific biases to simulate independent solver outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
