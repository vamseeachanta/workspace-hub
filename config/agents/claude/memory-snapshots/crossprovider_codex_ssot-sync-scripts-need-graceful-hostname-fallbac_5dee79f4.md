---
name: crossprovider codex ssot-sync-scripts-need-graceful-hostname-fallbac
description: SSoT sync scripts need graceful hostname fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration-management, sync-tools, robustness]
---

A sync tool that hard-fails when the current hostname isn't in the registry breaks on fresh machines, containers, renamed hosts. Pattern: registry-first when `--machine` is explicit, but graceful fallback to workspace-hub derivation for unknown hostnames.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
