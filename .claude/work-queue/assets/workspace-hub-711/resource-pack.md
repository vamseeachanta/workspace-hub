# Resource Pack: WRK-686

## Problem Context
Currently, different agents (Claude, Codex, Gemini) produce HTML artifacts (Plan/Implementation Reviews) with varying styles, headers, and structures. This lack of uniformity makes it difficult for users to quickly scan and approve work. We need a single, "workspace-hub" standard.

## Relevant Documents/Data
- `scripts/work-queue/generate-html-review.py`: The tool that generates HTML from Markdown.
- `WRK-671/review.html`: Modern sectioned card layout (Gemini).
- `WRK-669/review.html`: Table-heavy data layout (Claude).
- `assets/WRK-682/implementation-review.html`: Code-centric review (Gemini).

## Constraints
- Must be a single CSS file used by all new HTML artifacts.
- Must include a clear, consistent header with task metadata (ID, title, status).
- Must have a standard "Final Verdict" badge (APPROVE, REJECT, NO_OUTPUT).
- Must include integrated "APPROVE / REJECT" action instructions (and placeholder buttons).

## Assumptions
- `generate-html-review.py` can be updated to use a template or inject standard CSS.
- The standard layout should work for both Plan Reviews and Implementation Reviews.

## Open Questions
- Should we use a templating engine (like Jinja2) or keep it simple with string replacement in Python?
- Where is the best canonical location for the shared CSS? (`assets/shared/orchestrator-standard.css`).

## Domain Notes
- This is a UX/Standardization task to improve user experience during multi-agent gate reviews.
- The final CSS should be professional, clean, and highly scannable.
