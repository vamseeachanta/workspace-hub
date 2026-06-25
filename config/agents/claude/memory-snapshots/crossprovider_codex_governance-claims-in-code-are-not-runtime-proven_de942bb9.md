---
name: crossprovider codex governance-claims-in-code-are-not-runtime-proven
description: Governance claims in code are not runtime-proven without comprehensive instrumentation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [testing, verification, governance]
---

Hardcoded governance fields (e.g., `raw_source_read: false`) don't prove actual runtime behavior. Monkeypatching one read API (e.g., `Path.read_text`) doesn't catch other read patterns (`open()`, `read_bytes()`, etc.). Governance proofs require either comprehensive API instrumentation or proof-by-construction that the code path never touches the resource.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
