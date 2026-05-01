---
name: Gmail mutation goes via MCP scope-bump, not browser automation
description: Architecture decision for #2423 — pursue OAuth gmail.modify scope-bump on the claude_ai_Gmail MCP rather than claude-in-chrome browser automation
type: project
originSessionId: 86f98111-f1b8-4906-ac30-8773ca0b3031
---
For Gmail-side mutation (archive, label, delete) needed by [#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423), the chosen path is **OAuth scope-bump on the existing claude_ai_Gmail MCP integration**, not `claude-in-chrome` browser automation.

**Why:** User decision 2026-04-27. Two stated reasons:
1. **Consistency** — the read+compose path already runs through MCP; keeping mutation on the same surface avoids splitting the Gmail interface across two transports.
2. **Avoid compute-intensive extension credits** — `claude-in-chrome` consumes more compute per operation than MCP, and Gmail mutation is high-volume (potentially thousands of operations during inbox cleanup).

**How to apply:**
- For any Gmail mutation work (label, unlabel, archive via INBOX-removal, delete), assume the MCP path is the target. Do not propose `claude-in-chrome` as a primary path.
- The user-action gate is: re-authorize the claude_ai_Gmail MCP integration in the Anthropic account UI to grant `gmail.modify` (or stronger).
- Until that re-auth lands, mutation work blocks. Hand the user a search query and let them act in the Gmail UI (per `reference_gmail_mcp_scope.md`).
- `claude-in-chrome` remains the right tool for *interactive* Gmail tasks where the user is present (filter installation, account settings UI, dialogs that block automation per `feedback_gmail_bulk_archive_no_confirm.md`). It is not the right tool for batch mutation.

**Tracking issue:** filed 2026-04-27 as a standalone issue (the user-re-auth dependency is human, not engineering, so it warrants its own visible gate in the issue graph).
