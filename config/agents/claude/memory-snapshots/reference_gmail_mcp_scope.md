---
name: Gmail MCP OAuth scope is read+compose only
description: The claude_ai_Gmail MCP lacks gmail.modify scope — cannot label/unlabel threads or delete; plan unsubscribe/archive work around this
type: reference
originSessionId: 512141a1-fd1b-4872-bcc8-66a1e93059d6
---
The `mcp__claude_ai_Gmail__*` MCP (claude_ai_Gmail namespace) is authorized with read + compose scopes only. Discovered 2026-04-20 during ACE inbox triage.

**Verbs that work:**
- `search_threads` — list inbox, query with Gmail search syntax
- `get_thread` — fetch thread + message bodies (plaintextBody field populated)
- `list_labels` — read user-defined + system labels
- `create_draft` — create draft email (not send)
- `create_label` — create new user label

**Verbs that fail with "Request had insufficient authentication scopes":**
- `unlabel_thread` — cannot remove INBOX (= archive) or any other label
- Probably `label_thread` as well (same scope family — untested but likely fails)
- `unlabel_message`, `label_message` — same category

**Implication for triage work:**
- Reading + classification + drafting replies: all possible via MCP
- Archiving, deleting, labeling: NOT possible via MCP
- Workarounds: (a) claude-in-chrome browser (slow, JS-dialog hazards), (b) user does bulk action in Gmail UI via a handed-off search query (`from:a.com OR from:b.com`), (c) re-authorize MCP with `gmail.modify` scope (out-of-band user action)

**How to apply:** Plan Gmail triage sessions with this asymmetry in mind. Do read + classify + draft via MCP autonomously; hand archive/unsubscribe actions back to the user as a search query rather than attempting browser automation unless the user specifically asks for it.
