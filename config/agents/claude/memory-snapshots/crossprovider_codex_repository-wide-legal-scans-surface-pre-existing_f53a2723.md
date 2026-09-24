---
name: crossprovider codex repository-wide-legal-scans-surface-pre-existing
description: Repository-wide legal scans surface pre-existing violations unrelated to current diff; use targeted scans instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [legal-scan, efficiency, codex-pattern]
---

Full `legal-sanity-scan` on large repos catches legacy violations (like `/mnt/ace/` paths) that have nothing to do with the current change set. Use targeted scans on only the diff files. Full scans are noise for review signal.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
