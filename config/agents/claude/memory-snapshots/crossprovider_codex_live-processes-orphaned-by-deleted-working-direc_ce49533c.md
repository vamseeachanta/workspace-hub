---
name: crossprovider codex live-processes-orphaned-by-deleted-working-direc
description: Live processes orphaned by deleted working directory remain mapped
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [filesystem, process-management, cleanup, fleet-operations]
---

When a process's cwd is deleted while running (e.g., during cleanup), the process becomes orphaned with filesystem pages still mapped in /proc/*/maps as (deleted), preventing reclamation even after restoration. Detect via /proc/*/maps inspection; the orphaned process must exit or be killed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
