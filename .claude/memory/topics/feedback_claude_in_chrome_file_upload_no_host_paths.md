> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-05
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_claude_in_chrome_file_upload_no_host_paths.md

---
name: feedback_claude_in_chrome_file_upload_no_host_paths
description: claude-in-chrome file_upload runtime rejects host filesystem paths despite its schema; user must pick files in the native picker
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 418eae65-b0b5-4afd-ba31-d1663bc3b6ab
---

`mcp__claude-in-chrome__file_upload` schema still says "absolute file paths on the local machine" (param `paths`), but the **runtime rejects host paths**: "file_upload no longer accepts host filesystem paths. The MCP controller must read the file and pass its contents via the `files` parameter" — and no `files` param is exposed. `upload_image` only handles previously-captured browser screenshots, not arbitrary local files.

**Why:** browser automation runs in a sandbox that can't read `/mnt/...` directly (same reason `save_to_disk` screenshots land somewhere Bash can't find).

**How to apply:** for any browser file upload of a local artifact (YouTube/Drive/form), don't promise programmatic upload — drive the page to the upload dialog, then have the **user click "Select files" / the native picker** themselves (Ctrl+L pastes a full path in the Linux picker). Claude can still fill all surrounding metadata + click the final action. Worked for SkEstates YouTube uploads 2026-05-27. Related: YouTube account switch uses `studio.youtube.com/?authuser=N` (skestatesinc = authuser=1, same index as Gmail `/u/1/`); short/vertical clips auto-classify as Shorts. See [[feedback_claude_in_chrome_session_scoped]].
