---
name: crossprovider hermes public-safe-artifact-boundaries-exclude-agent-in
description: Public-safe artifact boundaries exclude agent instruction surfaces
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-safety, artifact-filtering, scope-boundary]
---

CLAUDE.md, AGENTS.md, and agent-control surfaces must be explicitly filtered from public graphs; can leak via malformed frontmatter or edge references. Validate committed artifacts against source-boundary rules (semantic filtering), not just schema conformance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
