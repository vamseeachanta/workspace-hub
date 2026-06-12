---
name: crossprovider gemini child-issue-dependency-boundaries-prevent-scope-
description: Child issue dependency boundaries prevent scope creep
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [planning, scope-boundaries]
---

When a child issue depends on a prerequisite (e.g., #335 depends on #334 disclosure schema), make the dependency explicit in the plan and do NOT attempt to implement the prerequisite's work. Clearly mark what's 'in this issue only' vs 'deferred to sibling/parent'. Scope violations get caught in adversarial review.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
