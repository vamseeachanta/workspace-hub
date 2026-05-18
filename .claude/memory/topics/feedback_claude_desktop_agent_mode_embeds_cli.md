> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_claude_desktop_agent_mode_embeds_cli.md

---
name: Claude Desktop Agent Mode embeds Claude Code CLI
description: Claude Desktop's Agent Mode is a Claude Code CLI child process; Bash tool calls flow through cowork-vm-service.js sandbox
type: feedback
originSessionId: 18bce6d9-ceec-4424-a580-1ffee5eb430f
---
When the user runs Claude in **Agent Mode inside Claude Desktop** (not the bare `claude` CLI in a terminal), the harness is a child `claude` process spawned by Claude Desktop's Electron main, with all tool I/O routed through `cowork-vm-service.js`.

**Why:** verified 2026-05-03 on ace-linux-1 via `pgrep -af claude-desktop`. The PID tree showed `/usr/lib/claude-desktop/node_modules/electron/dist/electron .../cowork-vm-service.js` as parent, and a `/home/vamsee/.config/Claude/claude-code/<version>/claude --model ... --permission-prompt-tool stdio` as child. The CLI binary lives under `~/.config/Claude/claude-code/<version>/`, NOT at `/usr/bin/claude` — so a system-wide `claude` upgrade does not touch the Agent-Mode runtime.

**How to apply:**

1. To upgrade the Agent-Mode CLI runtime, upgrade Claude Desktop itself (`sudo apt upgrade claude-desktop`) — the desktop app pins its embedded CLI version under `~/.config/Claude/claude-code/<version>/`.
2. Bash tool failures inside Agent Mode that don't reproduce in bare-CLI sessions are likely `cowork-vm-service` sandboxing issues — check that service's process state, not the user's shell config.
3. The `--add-dir /usr/lib/claude-desktop/.../app.asar` arg in the embedded CLI invocation means the Agent has read access to the Electron app bundle by default — useful when debugging the desktop app from inside it.
4. Self-test pattern: if a Bash command succeeds in Agent Mode, the desktop runtime + cowork service + embedded CLI are all healthy. The session itself is the smoke test.
