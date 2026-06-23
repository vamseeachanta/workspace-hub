> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_exec_cpu_starved_in_claude_sandbox.md

---
name: feedback-codex-exec-cpu-starved-in-claude-sandbox
description: "codex exec nested under Claude is CPU-starved/slow in this sandbox (≈5% CPU; a heavy refactor wrote nothing for a very long time) — route heavy AUTHORING to Claude subagents, use Codex for independent REVIEW only (and its exec output is buffer-lossy)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 71a79ff0-329a-44b2-9bb9-df290e7e5916
---

`codex exec` launched nested under a Claude Code session is **CPU-starved in this sandbox** — measured ~5% CPU; a heavy demo_02 refactor (`codex exec -s workspace-write`) wrote **zero source after a very long time** and had to be killed (2026-06-01). A demo_05 reproduction independently measured **97s wall for a ~1.4s job** under the same sandbox.

**How to apply (delegation routing — "route by strength, work as a team"):**
- **Heavy AUTHORING → Claude subagents** (fast here; a sliced 1367-line refactor finished cleanly via a Claude `Agent`), NOT `codex exec`.
- **Codex → independent ADVERSARIAL REVIEW** (its strength: surfaced the kanban-board-emptied finding + a silent catalog-fallback). But `codex exec` stdout is **buffer-lossy** — the streamed ranked findings get truncated; only the final tail is captured. So treat a Codex review as a SIGNAL, and run a Claude separate-reviewer (fresh context, ≠ author) for the COMPLETE gate, seeded with Codex's partial findings.
- `codex exec` also can't run `pytest`/`uv` in read-only mode (read-only `~/.cache/uv`); use `UV_CACHE_DIR=/tmp/...` or run tests on the Claude side.
- Killing a stalled run: `pkill -f "codex exec ..."` **matches your own shell** (self-kill, exit 144) — kill by PID instead (`pgrep -f openai/codex | xargs kill`), and even that can signal the parent shell; verify after in a fresh command.
- Pairs with [[feedback_delegate_heavy_work_to_codex_for_tokens]] (still route to Codex for token economy WHEN it can run — here it can't author at speed) and [[feedback_externalize_all_config_to_yaml]] (the work this came up on). Supersedes the optimistic read of [[feedback_codex_sandbox_write_blocked]] "FIXED" — writes are *permitted* (AppArmor) but *too slow to be useful* for authoring in this sandbox.
