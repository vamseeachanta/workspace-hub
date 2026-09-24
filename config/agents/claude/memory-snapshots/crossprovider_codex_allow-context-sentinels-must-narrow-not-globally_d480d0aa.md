---
name: crossprovider codex allow-context-sentinels-must-narrow-not-globally
description: Allow-context sentinels must narrow, not globally suppress rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, allow-contexts, validation-design]
---

When implementing line-level allow contexts (e.g., exemptions for sentinel comments), suppress only the specific matched content, not all deny rules on that line. Whole-line suppression enables smuggling of prohibited content alongside valid exemptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
