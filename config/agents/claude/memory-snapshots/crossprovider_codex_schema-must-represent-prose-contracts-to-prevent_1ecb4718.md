---
name: crossprovider codex schema-must-represent-prose-contracts-to-prevent
description: Schema must represent prose contracts to prevent bypass vectors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-enforcement, prose-contracts, bypass-vectors]
---

When narrative requirements describe isolation or role boundaries (e.g., 'primary evidence only,' 'solver binding,' 'nonacceptance propagation'), those requirements must be representable as schema fields with enum values. Prose-only contracts create bypass loopholes even when intent is explicit—a consumer following the schema can satisfy it while violating the narrative requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
