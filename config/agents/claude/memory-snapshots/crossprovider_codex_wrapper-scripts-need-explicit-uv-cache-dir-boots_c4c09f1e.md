---
name: crossprovider codex wrapper-scripts-need-explicit-uv-cache-dir-boots
description: Wrapper scripts need explicit UV_CACHE_DIR bootstrap
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [uv, shell-wrapper, python-runtime]
---

Scripts using `uv run` in shebang/wrapper must export `UV_CACHE_DIR` to a writable repo-local path and create the directory before invoking uv, matching `generate-index.py` pattern. Omitting this causes `Permission denied` on cache initialization in sandboxed environments. WRK-1130 and WRK-1132 both hit this.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
