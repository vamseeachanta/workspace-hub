---
name: crossprovider codex github-direct-call-authority-must-be-uniform-acr
description: GitHub direct-call authority must be uniform across all sites
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-authority, environment-isolation, consistency]
---

When a fixed-host/isolated-environment contract applies to GitHub operations, every direct call to `gh` must enforce it consistently. The reviewed codebase had `verify_private_repo()`, `bootstrap_contract_cli`, and a separate registry checker each calling `gh repo view` with different isolation levels—some without `--hostname github.com` or isolated `env=`. Inconsistency exposes privacy authority to ambient CLI state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
