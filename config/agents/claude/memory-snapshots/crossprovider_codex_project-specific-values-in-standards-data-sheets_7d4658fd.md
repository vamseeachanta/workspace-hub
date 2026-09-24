---
name: crossprovider codex project-specific-values-in-standards-data-sheets
description: Project-specific values in standards data sheets must fail closed, not fabricate defaults
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, design-pattern, validation, safety]
---

When a standard's data sheet defers a value to project specifications (e.g., FBE minimum thickness, FBE holiday detection voltage in DNV-RP-F106), the helper must require that input and raise if missing, rather than inventing a default. Fails-closed design prevents silent misspecification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
