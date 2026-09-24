---
name: crossprovider codex reuse-existing-verification-machinery-before-reb
description: Reuse existing verification machinery before rebuilding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-reuse, security-gates, architecture]
---

Check production for existing verification primitives (e.g., `_verified_label_event`, actor-authority checks, timeline parsing) before building new gate machinery. Generalizing proven code is lower-risk than parallel reimplementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
