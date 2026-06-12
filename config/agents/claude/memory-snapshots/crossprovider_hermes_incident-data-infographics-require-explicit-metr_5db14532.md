---
name: crossprovider hermes incident-data-infographics-require-explicit-metr
description: Incident-data infographics require explicit metric contracts and control-row exclusion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-visualization, incident-data, provenance]
---

When building risk infographics from incident databases, must enforce: matched incident IDs across data joins, exclusion of control/non-incident rows (e.g., NI002, NI010), timestamp + provenance + caveats, and HTML+JSON default (not PNG/PDF) for binary-bloat avoidance and reviewability in git.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
