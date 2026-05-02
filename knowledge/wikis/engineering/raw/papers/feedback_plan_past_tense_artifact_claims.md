> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_plan_past_tense_artifact_claims.md

---
name: Plans must not describe proposed work as committed
description: When revising plans, describe FIXES as proposed work (future tense), not committed artifacts — Codex caught this twice on #2344 + #2348 where v2/v3 plans claimed scripts/assets "are committed" that never existed in git
type: feedback
originSessionId: 9b439b61-1bc0-4c85-b9a9-727564b48494
---
When revising a plan based on adversarial review, it is tempting to write "committed `render-capability-summary-pdf.sh`" or "vendored Inter WOFF2 at `assets/fonts/inter/`" because those are the fixes the revision is addressing. **Don't.** If the plan is still `draft` or `plan-review`, the artifacts should not yet exist in git — the plan's role is to describe the proposed implementation, not to claim it has been done.

**Why this matters:**
- Downstream reviewers who read the plan text at face value will conclude the artifacts exist and approve without checking.
- Codex-style reviewers who verify against `git show` will catch the misrepresentation and return MAJOR.
- A plan that misrepresents its own implementation state is worse than an unfixed plan: it erodes trust in the whole artifact.

**How to apply:**
- In plan pseudocode / Files to Change / Acceptance: use future or imperative tense ("will create", "add to", "commit when implementing").
- In revision history: describe the DELTA to the plan, not the code ("v2 adds requirement for Inter vendoring" — not "v2 vendors Inter").
- In Claims verified sections of adversarial reviews: always cite actual file state at a specific git ref, not plan text.
- During the plan edit, consciously separate: "what does the plan prescribe?" (prescribed work) from "what is in this commit?" (the plan itself, and nothing else).

**Observed:** Codex round-2 review on #2344 v2 (2026-04-20) returned MAJOR because plan v2 claimed `render-capability-summary-pdf.sh` and vendored Inter WOFF2 were "committed" when `git show 7dc6356ea` returned 404 for both. Similar pattern will apply to #2348 v3 if the same reviser habit carries across.
