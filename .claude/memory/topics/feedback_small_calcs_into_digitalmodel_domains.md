> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-09
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_small_calcs_into_digitalmodel_domains.md

---
name: feedback_small_calcs_into_digitalmodel_domains
description: "Small one-off engineering calcs must land in the relevant digitalmodel domain module (reusable), not just as standalone scripts/briefs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 010d8dff-f3e4-406b-a7d5-01b8f6200ff4
---

2026-06-19 directive: when solving small engineering calculations (e.g. Collide PE Problem-of-the-Day quantitative ones — productivity index, OOIP volumetrics), **always add the calculation to the relevant `digitalmodel` repo domain module**, not only as a standalone YAML/brief.

**Why:** these small works should "connect like dots into workflows and then the flywheel concept." A calc dropped only in a `docs/` brief is a dead end; the same calc as a reusable function in the right domain (reservoir/production/drilling/etc.) becomes a building block that Deckhand domain-workflows and the GTM content→outreach flywheel can compose.

**How to apply:**
- Put the calc in the matching `src/digitalmodel/<domain>/` module (small pure function + a tiny test). Reservoir/well-performance calcs → the reservoir/production domain; volumetrics → reservoir; etc.
- The Collide brief / `docs/collide_pe` solution then *references or imports* that domain function rather than re-deriving it inline.
- Conceptual/definition problems (viscosity, corrosion, LWD) have no calc — those stay as briefs only.

Links: [[project_collide_pe_solver_program]] (Epic #836). Pairs with the Deckhand domain-workflow pattern (#837) which runs digitalmodel `compute_roots` entrypoints, and the [[project_content_outreach_flywheel]].
