---
name: crossprovider codex stage-1-discovery-rules-out-recovery-before-repl
description: Stage 1 discovery rules out recovery before replacement
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue-stages, discovery, artifact-recovery]
---

When a WRK's prerequisite artifact is missing, Stage 1 should verify whether it ever existed (git history, local mounts, asset directories) before deciding to build a replacement. Don't assume missing = never was; recover from known sources first.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
