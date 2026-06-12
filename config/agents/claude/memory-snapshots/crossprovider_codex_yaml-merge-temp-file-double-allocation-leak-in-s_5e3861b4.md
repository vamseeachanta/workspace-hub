---
name: crossprovider codex yaml-merge-temp-file-double-allocation-leak-in-s
description: YAML merge temp-file double-allocation leak in sync_hermes_yaml_config
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell, tempfile, resource-leak]
---

The sync function allocated `merged` in both python3 and uv code paths, leaking the first temp. Fix: single allocation strategy (`sync_make_target_tmp` for live, `mktemp` for dry-run), verified by counting allocation statements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
