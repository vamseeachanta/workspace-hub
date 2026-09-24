---
name: crossprovider codex git-tracked-assumption-does-not-apply-to-registr
description: Git-tracked assumption does not apply to registry-derived or mount-sourced metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, security, trust-boundary]
---

Plans assume 'git-tracked → trusted' globally but then read from shared mounts, registry-derived metadata, or external API results. This is an undefended trust boundary. Specify validation/sanitization for all non-git-tracked sources, including registry paths, mount-sourced metadata, and external inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
