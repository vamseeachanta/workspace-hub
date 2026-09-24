---
name: crossprovider gemini remote-resource-degradation-requires-explicit-fa
description: Remote resource degradation requires explicit fallback and TTL handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [remote-resources, resilience, degradation, mount-handling]
---

When external/mounted resources may be unavailable, registry records should define: fallback_posture (e.g., use indexed metadata), degradation_rule (e.g., do not blind-duplicate), cached_evidence_ttl (e.g., 7d), and explicit source_unavailable status in tracking. Prevents silent partial failures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
