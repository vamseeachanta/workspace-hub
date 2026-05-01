> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_claude_in_chrome_session_scoped.md

---
name: claude-in-chrome MCP tools are main-session-scoped
description: mcp__claude-in-chrome__* tools bind to the main Claude Code session's tab group; subagents cannot inherit the Chrome session
type: feedback
originSessionId: aff40e1f-c80c-4f6d-9797-cba4ecc59a84
---
`mcp__claude-in-chrome__*` tools are bound to the **main Claude Code session's tab group.** Subagents spawned via the Agent tool (Task tool) cannot inherit the Chrome session. All browser automation must happen in the main session.

**Why:** MCP server connections are per-session. Subagents receive their own restricted `allowed_tools` list; claude-in-chrome tools don't transfer across the boundary. Discovered while planning the 2026-04-24 parallel-subagent workflow for the Gmail sweep — the original plan to dispatch browser work to subagents had to be re-architected once this constraint surfaced.

**How to apply:** Partition multi-agent browser work into two lanes:
- **Main session** = browser execution (MCP-bound, claude-in-chrome tool calls).
- **Subagents** = read-only research, artifact preparation, plan drafting — producing outputs that inform the main session's browser actions.

Never assume a subagent can drive Chrome. If a plan delegates a browser step to a subagent, flag it as a defect during adversarial review. The same constraint likely applies to other per-session MCP servers (gmail, drive, etc.) — treat session-scoped tools as main-only until proven otherwise.
