---
name: crossprovider codex filesystem-based-enablement-for-multi-boundary-c
description: Filesystem-based enablement for multi-boundary CI orchestration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-design, multi-repo, orchestration, enablement]
---

When CI spans a hub-level orchestrator and per-repo workflows, use file presence (e.g., existence of config/script) as the enablement flag, not metadata-only. Metadata flags in hub manifests cannot disable repo-local workflows unless each repo reads the same source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
