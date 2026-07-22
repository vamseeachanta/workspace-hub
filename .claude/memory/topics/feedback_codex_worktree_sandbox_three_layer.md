> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_worktree_sandbox_three_layer.md

---
name: feedback_codex_worktree_sandbox_three_layer
description: "Running Codex-via-broker in a git worktree needs THREE aligned sandbox fixes, not one; from the"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b651e067-4f81-4661-af7c-942d6716908f
---

Dispatching Codex (via the `codex-companion.mjs` broker) to implement in an **isolated git worktree** off `origin/main` required three independent fixes that each blocked silently. Discovered live during the #2802 Codex-under-Claude pilot (2026-05-26, PR #2820). Extends [[feedback_codex_sandbox_write_blocked]] (the #2804/#2809 userns fix).

**Why:** the handoff assumed a worktree "just works" once created. It created fine, but Codex blocked three times in a row — each a different layer. The Codex `sandbox_mode=workspace-write` model wants ONE contiguous writable root; git worktrees deliberately split metadata across the parent repo. The two are architecturally at odds.

**How to apply — all three are required:**
1. **`--cwd <worktree>` on the broker `task` command** (NOT a `cd` inside the prompt, NOT `--cd` which isn't a flag and leaks into the prompt). The broker derives the sandbox workspace root from cwd via `git rev-parse --show-toplevel`; a worktree is its own toplevel, so `--cwd` re-roots the sandbox writable set onto it. Without it, the sandbox roots at wherever you invoked the broker (often the dirty main repo).
2. **`[sandbox_workspace_write].writable_roots = ["<main-repo>/.git"]` in `~/.codex/config.toml`.** A worktree's `.git` is a gitlink file pointing to `<main-repo>/.git/worktrees/<name>`; shared objects/refs live in the main `.git`. Both are OUTSIDE the worktree root, so `git commit` fails `index.lock: Read-only file system` even though file writes succeed. Granting the shared `.git` fixes it (blast-radius tradeoff: the shared object db becomes writable to the sandbox).
3. **Restart the broker's shared app-server after editing config.** The broker keeps a long-lived `serve` + `codex app-server` per workspace root (`ensureBrokerSession` reuses a live socket) that reads `config.toml` ONCE at spawn. A live config edit is a silent no-op until you kill the `serve` tree (scoped to that workspace's `/tmp/cxc-*` session) so a fresh app-server re-reads it.

**Also:** broker jobs are namespaced by workspace root — `status`/`result` for a worktree-rooted job need `--cwd <worktree>` too, or they return empty.

**Cleaner alternative considered:** a standalone clone (self-contained `.git` inside the sandbox root) sidesteps all of this; the user chose the writable-roots grant to keep the literal worktree. For future worktree dispatches, prefer documenting this in the #2804 route docs or teaching the installer to add the grant. Codex behaved perfectly throughout — blocked cleanly each time, zero improvising. [[feedback_worktree_gitlink_pollution]]

**RESOLVED 2026-05-26 (#2822, PR pending):** built `scripts/install/codex-dispatch-prep.sh` — a guarded helper that prepares a write-isolated clone as the broker `--cwd` root (chose the clone route, Option A, over the worktree+grant route). **Critical nuance Codex plan-review caught + local repro confirmed:** `git clone --local` is *self-contained* (no external `alternates`) but NOT *write-isolated* — it HARDLINKS objects, so the clone's `.git/objects/<x>` shares an INODE with the source; a write-capable sandbox can corrupt the source repo's objects. Default to `git clone --no-hardlinks` (distinct inodes, ~object-store copy cost) for write dispatch; `--local` only for read-only. "Self-contained ≠ write-isolated" generalizes to ANY sandbox+clone pattern, not just Codex. Route doc `docs/reports/2026-05-26-codex-under-claude-pilot.md` §"Isolated dispatch" now documents both the clone route and the worktree fallback.
