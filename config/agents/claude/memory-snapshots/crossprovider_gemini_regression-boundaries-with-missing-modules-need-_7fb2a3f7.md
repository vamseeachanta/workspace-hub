---
name: crossprovider gemini regression-boundaries-with-missing-modules-need-
description: Regression boundaries with missing modules need wrapper-vs-retarget decision upfront
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, refactoring, regression-boundaries]
---

When a test imports a missing module (e.g., `proxy_comparison.py` absent), decide early whether to restore the surface (wrapper), retarget to an existing replacement (retarget), or deprecate it. Ambiguity leaves orphan tests that block compatibility. worldenergydata #342 shows this is non-trivial.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
