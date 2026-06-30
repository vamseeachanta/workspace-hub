> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_insights_tabular_not_prose.md

---
name: feedback-insights-tabular-not-prose
description: "User preference 2026-05-25 — render Explanatory-style insight blocks (and key takeaways generally) as TABLES, not prose bullet lists. Applies to the ★ Insight ─ blocks the Explanatory output style emits."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e9bcfa5b-c1dc-4596-834b-bda6539efc25
---

User directive 2026-05-25: "insight is prose. display a tabular format."

**What it means:** when emitting the Explanatory output style's `★ Insight ─` blocks
(or any "key points / takeaways" summary), format the content as a **table**, not as
prose sentences or bullet points. The user processes the dense comparative material
faster in tabular form.

**How to apply:**
- Keep the `★ Insight ───` / `─────` delimiter lines (style requirement) but put a
  compact markdown table between them instead of prose bullets.
- Pick columns that fit the point — e.g. `Aspect | Detail`, `Claim | Evidence`,
  `Before | After`, `Option | Tradeoff`. Two or three columns, a few rows.
- Same for ad-hoc "here's the key insight" moments: prefer a small table over a paragraph.
- General pattern consistent with [[feedback_html_default_artifact]] (the user favors
  scannable, structured presentation over prose for dense technical content).

**Do NOT apply when:** the insight is a single short sentence where a table adds overhead,
or when the content is genuinely narrative (a sequence/story) that a table would distort.
