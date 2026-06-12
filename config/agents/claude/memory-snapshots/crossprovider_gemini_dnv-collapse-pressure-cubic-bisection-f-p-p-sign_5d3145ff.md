---
name: crossprovider gemini dnv-collapse-pressure-cubic-bisection-f-p-p-sign
description: DNV collapse pressure cubic bisection: f(p_p) sign flip guarantees root
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [dnv-st-f101, collapse-pressure, numerical-methods]
---

The cubic p_c³ - p_el*p_c² - (p_p² + C)*p_c + p_el*p_p² = 0 has f(0) > 0 and f(p_p) ≤ 0. This sign flip (when f_o ≥ 0) guarantees a root in [ε, p_p]. Bisect for 120 iterations to 1e-9 tolerance. Robust for all ovality values.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
