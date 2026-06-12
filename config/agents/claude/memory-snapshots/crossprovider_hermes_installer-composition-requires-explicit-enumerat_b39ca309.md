---
name: crossprovider hermes installer-composition-requires-explicit-enumerat
description: Installer composition requires explicit enumeration of current state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [installer-design, hook-composition, scope-clarity]
---

Rewriting hooks/installers without explicit inventory of current behaviors (appended sections, enforcement chains, guard order) risks silent regression. 'Avoid append-only drift' without specifying target composition is under-specified; must list what to preserve, what to remove, and why.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
