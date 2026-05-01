---
name: hermes-local-configuration
version: 1.0.0
category: devops
description: Class-level Hermes local configuration and setup workflows, including config audit gotchas and Windows installation.
tags: [hermes, configuration, windows, setup]
---

# Hermes Local Configuration

## When to Use
Use when configuring or troubleshooting local Hermes installations, portable config keys, migrated settings, or Windows setup.

## Class-Level Workflow
1. Load the canonical `hermes-agent` skill for current commands before changing Hermes itself.
2. Separate portable baseline config from machine-specific paths/secrets.
3. Audit custom config keys after migrations so stale keys do not silently no-op.
4. On Windows, verify shell, Python, terminal, and path assumptions explicitly.

## Consolidated Session Learnings

Narrow skills absorbed during the 2026-04-29 umbrella consolidation are preserved under `references/`.
## Absorbed Narrow Skills (2026-04-29)

### `hermes-config-audit-gotchas`

- Former skill demoted to `references/hermes-config-audit-gotchas.md`.
- Preserved insight: Audit Hermes custom config keys and migrated skill settings safely, with verified command behavior and stale-path checks.

### `hermes-windows-setup`

- Former skill demoted to `references/hermes-windows-setup.md`.
- Preserved insight: Install and configure a repo-centric Hermes agent workspace on Windows. Covers prerequisites, repo cloning, Python/uv environment, skills system, memory bridge, and multi-agent coordination — the Windows equivalent of the Linux workspace-hub pattern.
