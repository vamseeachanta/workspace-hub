---
name: reference_gmail_create_draft_attachment_limit
description: "Gmail create_draft accepts attachments but agent can't reliably inject files >few KB (base64 hand-transcription corrupts)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 04ba27c8-b50b-472b-bd93-43d4b8689653
---

2026-06-27: The `mcp__claude_ai_Gmail__create_draft` tool's schema has an `attachments[]` field (base64 `content`, mimeType, filename) even though its description says "Creating drafts with attachments is not supported yet" — that line is STALE. A tiny probe (8-byte text, base64 `VGVzdA==`) created a draft successfully, so attachments DO work at the API level.

BUT the agent cannot reliably attach a real file: the tool needs the file's ENTIRE base64 reproduced character-perfect inside the tool call, and the agent has no way to feed file bytes except by emitting them in its own output. Reading the base64 (Read caps ~25k tokens/call; base64 tokenizes ~1 token/char, so a 22 KB PDF ≈ 30k chars needs chunked reads) then hand-concatenating the chunks into the `content` field **corrupts** — a single dropped/duplicated/misaligned chunk → API returns `Invalid value at 'attachments[0].content' (TYPE_BYTES), Base64 decoding failed`. Verified failure on a 22 KB PDF (~30k base64 chars across 3 chunks). A 600 KB PDF (~870k chars) is hopeless.

**Practical rule:** for any attachment beyond a few KB, do NOT try to inject base64 through the tool. Instead either (a) **operator attaches manually** (drag-drop the local file into the draft — works when the user has GUI/box access), or (b) **host the file on a public link** (GitHub Pages / live-shares) and put the URL in the email body. Both are reliable; inline base64 is not. Compressing the PDF (ghostscript `-dPDFSETTINGS=/screen`, drop font embedding `-dEmbedAllFonts=false` → e.g. 628 KB→22 KB) shrinks it but does NOT fix the transcription-fidelity problem. See [[project_howard_day_cfd_landspeed_study]].
