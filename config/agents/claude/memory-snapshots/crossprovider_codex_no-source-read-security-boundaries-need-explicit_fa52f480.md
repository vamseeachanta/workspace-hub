---
name: crossprovider codex no-source-read-security-boundaries-need-explicit
description: No-source-read security boundaries need explicit, consistent wording to avoid internal contradictions
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [security, privacy, boundaries, plan-consistency]
---

Distinguish clearly between 'allowed: read only these two repo-tracked safe inputs' and 'forbidden: source-corpus/raw/binary/payload reads.' Plan text and test assertions must not contradict (e.g., plan says 'consume tracked text' while tests say 'no text reads'). Wording consistency prevents ambiguous implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
