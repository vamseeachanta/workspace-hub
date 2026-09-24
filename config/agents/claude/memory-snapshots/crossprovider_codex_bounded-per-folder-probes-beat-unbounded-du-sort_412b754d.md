---
name: crossprovider codex bounded-per-folder-probes-beat-unbounded-du-sort
description: Bounded per-folder probes beat unbounded du|sort on large filesystems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem-ops, performance, shell-patterns]
---

When surveying large trees with du, use bounded probes per folder rather than du | sort on the whole tree. One slow subtree can block results indefinitely. Parallel, timeout-bounded probes per folder + report timeout misses are faster and more usable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
