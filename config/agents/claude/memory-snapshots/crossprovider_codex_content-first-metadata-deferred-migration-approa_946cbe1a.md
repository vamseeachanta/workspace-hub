---
name: crossprovider codex content-first-metadata-deferred-migration-approa
description: Content-first, metadata-deferred migration approach
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration-strategy, data-integrity]
---

Prioritize byte-identical content transfer (verified via sha256sum) while explicitly deferring mode/timestamp/unicode normalization issues to later waves. Reduces complexity per wave and allows incremental hardening.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
