---
name: crossprovider codex provider-specific-behavior-needs-custom-predicat
description: Provider-specific behavior needs custom predicates per provider
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [provider-logic, configuration, customization, code-review]
---

Each provider (Claude, Codex, Hermes) has different operational constraints and config shapes. Don't copy-paste predicate logic between providers. Example: Hermes workflow:gates only needs active runtime containing gate phrases, NOT Codex's lifecycle-text requirements. Each predicate must validate the provider's actual runtime state, not a generalized format.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
