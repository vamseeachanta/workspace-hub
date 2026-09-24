---
name: crossprovider gemini three-valued-outcome-semantics-for-deterministic
description: Three-valued outcome semantics for deterministic matching
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-integration, design-pattern, enum-semantics, matching]
---

When designing deterministic matching operations with multiple outcomes (exact match, no match, multiple matches), explicitly model all three states as enum values rather than raising exceptions or returning None. This pattern (e.g., LINKED/UNLINKED/AMBIGUOUS) is more composable and testable than exception-based paths.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
