---
name: project-statusline-fix-rollout-pending
description: "Statusline blank-render (#2954) + stale Codex quota (#2956) fixes MERGED; rollout to non-ace-linux-1 machines pending via combined handoff prompt"
metadata: 
  node_type: memory
  type: project
  originSessionId: cec38a63-0fc5-425a-8f4a-67e96f5760ee
---

Two telemetry fixes MERGED to workspace-hub main 2026-06-04; **other machines PENDING** — single combined cross-OS rollout prompt lives in `docs/session-handoffs/2026-06-04-statusline-pipefail-fix-rollout.md` (updated by PR #2957; original #2955).

1. **Statusline blank** (PR #2954): `.claude/statusline-command.sh` under `set -euo pipefail` died silently on unguarded `grep`/`rev-list '@{u}'` substitutions when cwd was non-git or branch had no issue digits. 3rd instance of the pipefail-optional-match defect class (see [[feedback_prepush_hooks_sigpipe_and_sibling_layout]]).
2. **Codex usage stale** (PR #2956): `query-codex-usage.sh` only mined `~/.codex/sessions/*.jsonl` — freezes across weekly window rollovers (snapshot said 21% used/resets Jun 7 while live was 1%/Jun 11; statusline O:79% vs true O:99%). Fix = live-first `codex app-server` JSON-RPC `account/rateLimits/read` (stdin must stay open ~3s — immediate EOF kills the server pre-response), fallback session-parse → manual; `providers.sh` gate now accepts `app-server-live`.

Diagnostic invariants: test statusline scripts by piping minimal JSON from a NON-GIT cwd (errors are hidden — non-zero exit = invisible line); trust Codex quota only when `source: "app-server-live"`. Auto-sync pushes branches mid-flight here — "cannot lock ref"/"Everything up-to-date" on your own first push = race artifact; verify via `ls-remote` SHA equality (per [[feedback_autosync_silent_pusher]]).
