---
name: crossprovider codex fixture-parametrization-required-for-hostile-pro
description: Fixture parametrization required for hostile-producer testing with side effects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, git-shallow, edge-cases]
---

Looping over hostile identities with shared mutable fixtures (e.g., shallow clones unshallowed by prior iterations) causes false positives that hide actual vulnerabilities. Each hostile case must use an independent fixture instance so rejection reasons are testable, not artifacts of prior-iteration side effects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
