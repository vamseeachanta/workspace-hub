---
name: crossprovider codex fail-closed-checkout-freshness-dirty-behind-age-
description: Fail-closed checkout freshness: dirty | behind | age-unknown → stale
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, freshness-guard, provenance]
---

Provenance tracking uses fail-closed logic: if dirty=True, behind_main not in (0,'0'), age is None/'unknown'/non-numeric, or age outside [0,12]h range, mark the checkout stale. Negative age (future mtime from clock skew) also fails closed, not open.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
