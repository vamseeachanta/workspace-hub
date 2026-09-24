---
name: crossprovider codex temp-file-allocation-hazard-consolidate-allocati
description: Temp file allocation hazard: consolidate allocation in shell conditionals
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-bugs, temp-files, resource-leaks]
---

Shell scripts with fallback paths (python3 vs uv) can accidentally allocate temp files twice if written as `if cmd1 failed; then allocate; fi` + `if [[ -z merged ]]; then allocate again`. Fix: use a single allocation function (sync_make_target_tmp for real, mktemp for dry-run) that all paths call once, not retry-on-fail patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
