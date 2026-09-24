---
name: crossprovider codex mock-capture-must-be-unambiguous
description: Mock capture must be unambiguous
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, mocks, fidelity]
---

Echo-based argv logging cannot reliably distinguish empty arguments or shell-sensitive content. Use NUL-delimited capture, explicit element count, or binary encoding to establish byte-preserving forwarding and guard against false-pass on dangerous content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
