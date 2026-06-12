---
name: crossprovider hermes parent-dependency-status-must-be-explicit-in-can
description: Parent-dependency status must be explicit in canonical-plan Resource Intelligence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, dependencies, grounded-surfaces]
---

Plans citing parent issues (#335 depends on #334) must declare pending vs. implemented status upfront. Don't assume parent work landed; if unimplemented, treat outputs as future artifact dependencies, not existing surfaces.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
