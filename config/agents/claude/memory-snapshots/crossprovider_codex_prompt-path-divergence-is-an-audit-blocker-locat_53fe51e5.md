---
name: crossprovider codex prompt-path-divergence-is-an-audit-blocker-locat
description: Prompt path divergence is an audit blocker; locate actual checkout first
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [audit, path-resolution, llm-wiki]
---

Codex planning sessions receive prompt paths (workspace-hub/llm-wiki) that often don't exist locally; actual checkout may be elsewhere (/mnt/local-analysis/llm-wiki). Locate actual repo checkout via `git rev-parse --show-toplevel` or `find` before treating inventory/path claims as fact.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
