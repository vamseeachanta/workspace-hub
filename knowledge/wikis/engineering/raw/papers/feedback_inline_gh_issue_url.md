> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_inline_gh_issue_url.md

---
name: Inline GitHub issue URLs
description: Always render GitHub issue numbers as Markdown hyperlinks inline (e.g., [#2103](https://github.com/vamseeachanta/workspace-hub/issues/2103)) rather than bare `#NNNN`, in all chat output and posted comments
type: feedback
originSessionId: 1f830606-5e48-4de3-be9d-be12d66cd189
---
When referencing GitHub issues in chat output or comments posted via `gh`, always include the full URL as a Markdown hyperlink alongside the `#NNNN` shortform.

**Why:** the user clicks issue references frequently to drill into context; bare `#NNNN` tokens require manual URL construction or in-tool jump and break flow. User asked explicitly on 2026-04-25 mid-session: "always show hyperlinks along with gh issue #NNNN".

**How to apply:**
- Chat output: render as `[#2103](https://github.com/vamseeachanta/workspace-hub/issues/2103)` on every first occurrence within a section. Subsequent references in the same close paragraph may stay short.
- Tables: include the URL in the cell, not just `#NNNN`.
- `gh issue comment` bodies: keep the existing `#NNNN` short form there — GitHub auto-links those, full URLs would be redundant.
- Cross-repo issues: same pattern with the cross-repo path (`org/repo#NNNN` → full URL).
- Applies to all repos under workspace-hub (vamseeachanta/workspace-hub is the default).
