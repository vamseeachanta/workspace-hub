> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-14
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_webfetch_first_for_linkedin.md

---
name: WebFetch first for LinkedIn recon
description: For field-dev-code-recon and similar LinkedIn-source workflows, try WebFetch before launching browser automation — LinkedIn returns og:description metadata that often satisfies the extraction phase entirely
type: feedback
originSessionId: 7cf1f734-ba62-4ca7-abbd-07eca59c938a
---
For external-content recon workflows that pull from LinkedIn (`field-dev-code-recon`, `extract-learnings-to-issues`, etc.), default to WebFetch first. Browser automation (`mcp__claude-in-chrome__*`) is the documented fallback in those skills, but on 2026-05-04 the FOWT recon (Mark Prentice post 7455555454048452609-vusy) returned a complete technical summary from WebFetch alone — author affiliation, hashtags, all standards keywords, comment metadata — without needing to dismiss the sign-in dialog or call `read_page` / `get_page_text`.

**Why:** WebFetch parses LinkedIn's og:description meta-tag which contains the full post body for public posts. It's faster, doesn't open a tab, doesn't require the chrome MCP toolset to be loaded via ToolSearch, and doesn't risk the sign-in dialog blocking session events.

**How to apply:** When a recon skill says "browser_navigate" or "use Chrome to dismiss sign-in", call WebFetch first with a structured extraction prompt. If WebFetch returns gated content (e.g., "log in to view"), then fall back to browser automation. This saves one ToolSearch + tabs_context + navigate + read_page round trip — typically 4 tool calls collapsed to 1.

**Caveat:** This applies to PUBLIC LinkedIn posts only. Articles behind LinkedIn's "members-only" gate still require browser automation. The shape of the WebFetch return tells you which case you're in: structured technical content = public, "Sign in to view this post" = gated.
