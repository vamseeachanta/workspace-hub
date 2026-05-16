> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-16
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_chatgpt_share_dom_duplication.md

---
name: ChatGPT share DOM duplicates message nodes
description: chatgpt.com/s/<id> renders each turn twice in DOM; dedupe by innerText equality before counting turns
type: feedback
originSessionId: 4fdf61aa-7eb0-4a94-a255-234a564a14f8
---
ChatGPT shared-link pages (`chatgpt.com/s/<id>`) render each message twice in the DOM — once for the accessibility tree, once for visible display. `document.querySelectorAll('[data-message-author-role]')` returns N×2 nodes for what is actually N messages.

**Why:** got a "2 messages" count for what was actually a single assistant response on 2026-05-10 SolidWorks→Blender extraction. Initial pipeline assessment was misled until I verified `m1 === m2` (both 2,636 chars, identical text).

**How to apply:**
- When scraping a ChatGPT share via claude-in-chrome, dedupe DOM nodes by `innerText` equality before treating them as separate turns.
- Public shares typically omit the user's prompt entirely — don't assume `role=user` nodes will be present; the share may carry only the assistant response.
- `get_page_text` returns just the footer disclaimer on these pages; the article extractor doesn't reach into the message components. Use `javascript_tool` with `[data-message-author-role]` selector directly.
- For multi-turn shares, count distinct turns via `[...new Set(Array.from(nodes).map(n => n.innerText))].length`.
