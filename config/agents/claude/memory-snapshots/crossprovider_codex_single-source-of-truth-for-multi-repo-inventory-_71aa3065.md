---
name: crossprovider codex single-source-of-truth-for-multi-repo-inventory-
description: Single source of truth for multi-repo inventory — reconcile early
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [configuration-management, harness-design]
---

When the same repo list appears in multiple files (harness-config.yaml, check-all.sh, etc.), unify to one canonical source and have scripts read from it. Duplicate lists diverge over time and cause hard-to-debug inconsistencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
