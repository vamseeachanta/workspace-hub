---
name: crossprovider codex dirty-generated-output-blocks-clean-sync-on-behi
description: Dirty generated output blocks clean sync on behind repos
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [git, sync, merge-safety, generated-output]
---

When a repo is behind upstream and has dirty generated output (benchmarks, charts, cache), syncing mixes stale local artifacts with incoming work. Stash or revert generated outputs before pulling to keep sync clean. Generated files should not block upstream integration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
