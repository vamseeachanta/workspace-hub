---
name: crossprovider codex dual-gate-privacy-validation-generic-scan-insuff
description: Dual-gate privacy validation: generic scan insufficient for identifier denylists
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [testing, privacy, methodology]
---

Generic legal/diff scans catch dataset boundaries and common leak patterns but cannot cover batch-specific exact-identifier denylists. Each batch implementation needs an independent, batch-specific exact-identifier denylist check run in parallel with generic gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
