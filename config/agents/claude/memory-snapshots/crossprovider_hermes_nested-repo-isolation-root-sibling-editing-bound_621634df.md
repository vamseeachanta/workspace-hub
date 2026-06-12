---
name: crossprovider hermes nested-repo-isolation-root-sibling-editing-bound
description: Nested repo isolation: root/sibling editing boundaries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-structure, governance, architecture]
---

Root workspace-hub must not edit nested tier-1 repos; nested repos must not edit siblings or root. Enforced by repo-structure Iron Law; prevents cross-cutting changes that diverge from per-repo governance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
