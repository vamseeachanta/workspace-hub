---
name: crossprovider codex path-scoped-commits-prevent-multi-agent-sweep-co
description: Path-scoped commits prevent multi-agent sweep contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, multi-agent, commit-hygiene]
---

When multiple agents or multiple phases touch different files but only a subset should be committed, use pathspec form (`git commit -m "..." -- <file1> <file2>`) rather than broad git add/commit. This prevents one agent's cleanup or trial changes from accidentally landing in another's commit. Load-bearing in parallel-agent workflows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
