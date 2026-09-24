---
name: crossprovider gemini numerical-bisection-for-dnv-st-f101-collapse-pre
description: Numerical bisection for DNV-ST-F101 collapse pressure cubic interaction equation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [dnv, pipeline-engineering, numerical-methods, pressure-checks]
---

DNV-ST-F101 collapse pressure (Eq. 5.9) is solved via bisection over a cubic interaction equation rather than closed form. Initial bracket: [0, 1.5*max(p_el, p_p)]; if the bracket doesn't bracket the root, expand to 3x. Tolerance tuned to 1e-6 * max(p_el, p_p, 1.0). This approach avoids algebraic complexity and numerical instability in the interaction term.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
