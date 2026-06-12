---
name: crossprovider gemini single-source-of-truth-for-specs-reduces-multi-a
description: Single source of truth for specs reduces multi-agent routing ambiguity
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [specs, architecture, agent-contract]
---

When specs exist in both repo-local and centralized trees, agents become uncertain about which to read. This breaks automation reliability and increases cognitive load. Centralization to `specs/repos/<repo>/<path>` with pointer stubs in local trees eliminates ambiguity.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
