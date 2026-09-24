---
name: crossprovider codex bidirectional-case-normalization-for-forbidden-p
description: Bidirectional case normalization for forbidden-pattern matching
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-validation, security-checks]
---

When validating text against a list of forbidden patterns (filesystem paths, identifiers), lowercase both the text being checked AND every item in the forbidden list before matching. Mixed-case variants (e.g., `C:\Client\source.pdf` vs `c:\client\source.pdf`) bypass case-insensitive comparisons if only the text is normalized.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
