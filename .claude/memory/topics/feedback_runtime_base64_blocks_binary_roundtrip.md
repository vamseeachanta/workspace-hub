> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-17
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_runtime_base64_blocks_binary_roundtrip.md

---
name: runtime-base64-blocks-binary-roundtrip-via-js-tool-results
description: "claude-in-chrome javascript_tool results have base64-encoded data filtered by the runtime — canvas.toDataURL() / fetch().then(blob).text() etc. return \"[BLOCKED: Base64 encoded data]\" sentinels, not the actual base64. Plan binary-capture workflows around this constraint."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d178d601-ec8f-43a1-b9c4-b79d2e69b17f
---

On 2026-05-16, attempting to extract video frames via JavaScript's `canvas.toDataURL('image/jpeg')` inside `mcp__claude-in-chrome__javascript_tool` returned `"head": "[BLOCKED: Base64 encoded data]"` even though `base64Len: 56319` and `prefix: "data:image/jpeg;base64,/9j/..."` made it past — the runtime's anti-prompt-injection filter strips the actual base64 body from the tool result before the agent sees it. The page-side code ran fine; the agent just can't roundtrip the data.

**Why:** Base64 strings in tool results are a known prompt-injection vector (an attacker could hide instructions inside what looks like image data, or use them to exfiltrate context). The runtime filter strips them as a defense-in-depth measure. Sensible default.

**How to apply:** For workflows that need to capture binary data (video frames, image extracts, file blobs) from a Chrome MCP session:

- **Don't:** rely on a `canvas.toDataURL()` → JS tool result → Bash `base64 -d` pipeline. The base64 will not reach Bash. Same applies to `fetch(url).then(r => r.text())` on blob URLs and similar patterns.
- **Do (Option A — download path):** `mcp__claude-in-chrome__gif_creator` with `download: true` puts a GIF in `/home/vamsee/Downloads/`. Requires explicit user confirmation per the safety rules around every-download-needs-approval.
- **Do (Option B — save_to_disk path):** `mcp__claude-in-chrome__computer` with `action: "screenshot"` or `action: "zoom"` and `save_to_disk: true`. Verify the resulting paths — in the 2026-05-16 session, the tool result did NOT echo the saved path back, and only `~/.hermes/cache/screenshots/browser_screenshot_<uuid>.png` was reliably populated for other sessions. May not work for the current MCP tool version; test with a single capture before committing to a multi-frame workflow.
- **Do (Option C — written-description path):** Skip the binary roundtrip entirely and produce a structured written description (storyboard, frame-by-frame table, narrative). For replication-of-an-idiom use cases, the written artifact is often more useful than the binaries because it describes the *pattern* the implementer needs to copy, not the surface art the implementer doesn't need.

**Reference:** 2026-05-16 Lloyd's drilling-sequence animation capture session, [[project_llm_wiki_external_post_ingest_workflow]]. The Option C path produced `/mnt/ace/vendor-pdfs/lloyds-maritime-institute/2026-05-15-drilling-sequence-animation/storyboard.md` — a richer replication brief than a frame dump would have been. The 14 in-session screenshots are visible to the user in conversation history of that session as a non-redistributable visual record; they were not saved to disk.

Cross-reference: [[feedback_claude_in_chrome_session_scoped]] (Chrome MCP binds main session) and [[feedback_gif_creator_as_proof_pattern]] (gif_creator captures action sequences as GIFs).
