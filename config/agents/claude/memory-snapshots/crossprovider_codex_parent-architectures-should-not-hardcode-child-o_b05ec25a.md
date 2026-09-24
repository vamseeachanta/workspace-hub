---
name: crossprovider codex parent-architectures-should-not-hardcode-child-o
description: Parent architectures should not hardcode child-owned external identifiers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, scope-boundaries, multi-tier-systems]
---

When a parent-level architecture document hardcodes external namespaces (e.g., Hugging Face org names, dataset targets) owned by a child-stage preflight or publisher, it oversteps scope and forces later implementers to either violate the parent contract or publish under unverified identifiers. Use templated representations with explicit `requires_verified_preflight` flags.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
