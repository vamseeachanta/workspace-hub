---
name: crossprovider codex overly-broad-filesystem-searches-slow-exploratio
description: Overly broad filesystem searches slow exploration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [filesystem-efficiency, tool-selection, session-discovery]
---

Avoid tools like `rg --files` or `find /` on large mounts during session discovery. Narrow to specific repo roots or likely paths (e.g., `/mnt/ace`, current git checkout) before running broad searches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
