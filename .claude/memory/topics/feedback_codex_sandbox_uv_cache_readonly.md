> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-06
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_sandbox_uv_cache_readonly.md

---
name: feedback-codex-sandbox-uv-cache-readonly
description: "Under the Codex-under-Claude sandbox, `uv run` fails because ~/.cache/uv is read-only; use .venv/bin/python or UV_CACHE_DIR=/tmp"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 980c06c6-7a70-4602-bfbc-32addeb44f9a
---

When `codex exec -s workspace-write` runs nested under Claude, `uv run ...` fails on first use because the default uv cache `~/.cache/uv` (`/home/vamsee/.cache/uv`) is **read-only** in the sandbox.

**Why:** the bwrap sandbox mounts the home cache read-only; uv tries to initialize/write there and aborts before running the command.

**How to apply:** for smoke-running repo code inside a codex task, either (a) call the repo venv directly — `.venv/bin/python ...` (with `PYTHONPATH='src:../<dep>/src'` if the repo expects it), or (b) redirect the cache — `UV_CACHE_DIR=/tmp/uv-cache uv run ...`. Pre-bake this into codex dispatch prompts that need to execute examples/tests. Related: [[feedback_codex_exec_cwd_is_sandbox_root]], [[feedback_codex_sandbox_write_blocked]], [[feedback_delegate_heavy_work_to_codex_for_tokens]].
