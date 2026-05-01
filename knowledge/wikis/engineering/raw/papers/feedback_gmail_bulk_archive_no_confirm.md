> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gmail_bulk_archive_no_confirm.md

---
name: Gmail bulk archive is dialog-free; delete/unsubscribe trigger dialogs
description: Gmail UI bulk-archive of hundreds of conversations has no confirm dialog (reversible); bulk-delete, Empty-Trash, and List-Unsubscribe DO trigger dialogs that break claude-in-chrome
type: feedback
originSessionId: aff40e1f-c80c-4f6d-9797-cba4ecc59a84
---
Gmail UI bulk-archive of hundreds of conversations does **NOT** trigger a confirm dialog (archive is reversible). **Bulk-delete-forever**, **Empty-Trash**, and **List-Unsubscribe-click** DO trigger dialogs (irreversible or external action). Dialogs break claude-in-chrome sessions per that MCP server's system prompt.

**Why:** Confirmed 2026-04-24 during a 180-conversation bulk archive — no dialog appeared, action completed cleanly via claude-in-chrome. Gmail's UX only prompts when the action is destructive (can't be undone from Trash) or calls out to a third-party server (unsubscribe HTTP request).

**How to apply:** When designing Gmail automation via claude-in-chrome, route through the **dialog-free surface:**
- Archive (bulk or single) — safe.
- Apply label via filter-apply-label — safe.
- Move to label — safe.

Avoid, or defer to the user's manual UI run:
- Delete Forever, Empty Trash, Empty Spam — dialog.
- List-Unsubscribe (RFC 8058 one-click) — often dialog + external action.
- Report Spam at scale — may dialog depending on count.

Keep automation on Archive + Filter; destructive cleanup is the user's job.
