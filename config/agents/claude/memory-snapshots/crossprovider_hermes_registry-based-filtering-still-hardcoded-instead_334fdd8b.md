---
name: crossprovider hermes registry-based-filtering-still-hardcoded-instead
description: Registry-based filtering still hardcoded instead of dynamic
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [single-source-of-truth, dynamic-filtering, registry-design]
---

Issue #2775 implementation maintains static candidate lists in template instead of deriving from registry at runtime; if excluded repos (like OGManufacturing) later receive .claude/skills, they're silently excluded. Violates SSoT principle; test coverage may not catch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
