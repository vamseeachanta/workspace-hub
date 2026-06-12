---
name: crossprovider hermes rudder-fallback-criteria-narrow-the-discretion-b
description: Rudder fallback criteria: narrow the discretion boundary
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-design, discretion-boundary]
---

For engineering decisions with fallback logic (e.g., rudder model defaults to Whicker-and-Fehlner but allows simpler fallback "if demonstrably inapplicable"), encode explicit preflight criteria rather than leaving discretion open. Short tie-break rules for "demonstrably inapplicable" prevent judgment drift during implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
