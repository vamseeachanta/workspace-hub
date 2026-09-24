---
name: crossprovider codex compliance-gate-patterns-with-case-sensitivity-a
description: Compliance gate patterns with case sensitivity and error-swallowing create exploitable false passes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-testing, compliance-gates, pattern-matching, false-positive-risk]
---

HTML network-dependency gate checked only lowercase `http`, `<script`, `<img`, `@import`, `url()`, missing `<SCRIPT>`, `<IFRAME>`, `<LINK>`, `<object>`, meta refresh, uppercase `URL()`. Legal/leakage scanners using `|| true` treat rg exit 2 (permission/search errors) identically to 'no matches.' Both patterns silently pass when checks fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
