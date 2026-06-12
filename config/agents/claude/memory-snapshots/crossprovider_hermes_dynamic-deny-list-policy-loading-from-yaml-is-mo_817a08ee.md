---
name: crossprovider hermes dynamic-deny-list-policy-loading-from-yaml-is-mo
description: Dynamic deny-list policy loading from YAML is more maintainable than hardcoded patterns
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [legal-policy, security, testing, maintainability]
---

Tests with hardcoded blacklist literals require code changes to evolve security policies. Instead, load deny-list patterns from `.legal-deny-list.yaml` at test runtime; policies apply to all test cases uniformly. Enables policy evolution without test rewrites.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
