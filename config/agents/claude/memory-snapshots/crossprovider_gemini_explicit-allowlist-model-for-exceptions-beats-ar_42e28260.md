---
name: crossprovider gemini explicit-allowlist-model-for-exceptions-beats-ar
description: Explicit allowlist model for exceptions beats arbitrary exclusions
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [exception-policy, testability, rule-design, compliance]
---

When defining rules (e.g., 'bare python3 is forbidden'), enumerate allowed exception categories positively—bootstrap contexts, external-repo inspection, text-only mentions—rather than treating exemptions as arbitrary. Positive categories are testable and prevent category creep.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
