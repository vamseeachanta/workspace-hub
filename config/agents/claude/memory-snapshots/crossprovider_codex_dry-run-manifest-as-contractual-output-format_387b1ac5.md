---
name: crossprovider codex dry-run-manifest-as-contractual-output-format
description: Dry-run manifest as contractual output format
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration-verification, dry-run, approval-gating, automation]
---

Fix dry-run output to a parseable format (e.g., `repo=<repo> loc=<dir> files=<count> target=<path> dry_run=true`) so downstream validators can match line counts, capture approved hashes for traceability, and gate approval before apply. Unstructured output breaks validation chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
