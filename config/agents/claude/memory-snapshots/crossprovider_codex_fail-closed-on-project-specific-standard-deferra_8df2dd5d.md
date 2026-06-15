---
name: crossprovider codex fail-closed-on-project-specific-standard-deferra
description: Fail closed on project-specific standard deferrals
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [standards-implementation, defensive-design]
---

When a standard defers a detail to project judgment (e.g., FBE minimum thickness or holiday-detection voltage per ITP), the helper should raise on missing input rather than invent a safe default. This forces explicit project decision-making and prevents silent under-specification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
