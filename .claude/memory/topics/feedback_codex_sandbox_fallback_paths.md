> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_sandbox_fallback_paths.md

---
name: Codex sandbox fallback paths that actually work
description: When Codex's shell wrapper is blocked in sandbox, these read/verify paths still work — document them so Codex reviews don't silently fall back to unverified plan text
type: feedback
---

When Codex's shell/`exec_command` wrapper is blocked by the sandbox (extremely common in `codex exec` review runs), Codex has consistently recovered review-quality grounding via these fallbacks — in preference order observed across 2026-04-23 #2460 r1→r16:

1. **Node REPL (`js_repl`)** — used for local file reads, running `gh` commands, and inspecting tracked artifacts. This is the dominant fallback — shows up in ~70% of blocked-shell review runs today.
2. **GitHub connector** — used for live issue body, labels, comments, PR metadata, and approval-label state. Confirms repo/workspace mapping without any local shell.
3. **Non-login shell retry** — sometimes a single `bash -c` escapes the broken wrapper when the batched shell does not. Low reliability.

**Why:** Without these fallbacks, Codex's recurring pattern is to treat the plan text as authoritative and stop verifying local file claims — a silent-trust failure (git-tracked `feedback_codex_sandbox_write_blocked.md` and `feedback_codex_sandbox_no_execution.md` cover the block, but not the *workable read/verify paths*). When the fallback is exercised explicitly ("I'm switching to the Node REPL to inspect cited files line-for-line"), verdict quality materially improves and MAJOR findings become specific and fixable.

**How to apply:**
- When dispatching `codex exec` for plan review and the live shell wrapper is known-broken in that sandbox, the prompt should explicitly authorize `js_repl` + GitHub connector for read verification — don't assume Codex will choose the fallback on its own.
- Any Codex review that claims MAJOR without citing a `js_repl` read or GH-connector confirmation should be treated as *weakly grounded* — the verdict text may be plan-derived rather than repo-derived.
- Read/verify pattern only. Fallbacks do NOT unblock `git commit` / writes / tests — the write-blocked memory still holds.
