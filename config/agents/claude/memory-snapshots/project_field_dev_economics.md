---
name: Field-dev economics decline curve (#2054)
description: Status of the decline curve implementation for EconomicsInput/economics.py in digitalmodel
type: project
originSessionId: 864ecd8d-441f-4724-b1c9-ea28e0e595a1
---
Decline curve support (exponential/hyperbolic/harmonic/LINEAR-legacy) is fully implemented
and pushed to `digitalmodel` main as of 2026-04-10.

**Why:** Issue #2054 required replacing the flat-plateau + linear-decline production profile
with proper Arps decline curves while preserving backward compatibility.

**State:** DONE — two post-review fixes committed in `813baeeb`:
- `decline_rate` default changed `0.0 → None` (sentinel prevents silent type mutation)
- `b_factor` upper bound widened to `<= 1` (b=1 is physically valid harmonic limit)

**Known follow-ups (filed as GH issues in workspace-hub):**
- #2076 — bug: string `decline_type` bypasses EUR auto-derive (coercion ordering)
- #2079 — feat: configurable `reservoir_recovery_factor` on `EconomicsInput`
- #2081 — feat: `decline_sensitivity()` sweep — NPV vs decline rate

**How to apply:** When working on economics.py, check these issues before adding new features.
The EUR auto-derive (bisection on cumulative exponential) is the trickiest piece — test
`TestEURDeclineParameterization` in `tests/field_development/test_economics.py`.
