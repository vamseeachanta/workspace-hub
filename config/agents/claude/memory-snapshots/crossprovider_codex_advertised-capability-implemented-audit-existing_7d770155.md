---
name: crossprovider codex advertised-capability-implemented-audit-existing
description: Advertised capability ≠ implemented; audit existing code first
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, scoping, risk]
---

Before planning new work, verify what code actually does vs. what it advertises. Router APIs often advertise provider names that import nonexistent modules; reference-only implementations (hard-coded county lists, legacy URLs) are not production capability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
