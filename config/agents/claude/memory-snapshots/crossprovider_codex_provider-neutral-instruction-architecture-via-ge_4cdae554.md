---
name: crossprovider codex provider-neutral-instruction-architecture-via-ge
description: Provider-neutral instruction architecture via generated adapters
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, ai-instructions, patterns]
---

Canonical contract (AGENTS.md) stays provider-agnostic; provider-specific adapters (CLAUDE.md, etc.) are generated from templates. Solves single-source-of-truth while keeping provider binding local and validated via contract/drift audit scripts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
