> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_adversarial_review_stance.md

---
name: adversarial_review_stance
description: Every review prompt (plan, code, artifact) must force adversarial reviewer stance — not charitable reading. Rubber-stamp reviews cost more downstream than cold ones.
type: feedback
originSessionId: b2b95e53-5dd7-4b33-9904-f2fa343e5b01
---
Every review prompt sent to any reviewer (Claude, Codex, Gemini, human) MUST force an adversarial stance: actively hunt for defects, default to non-approval, demand evidence per finding, forbid praise and restatement. Charitable reviews that endorse without hunting produce rework that is much more expensive than a cold review.

**Why:** User feedback 2026-04-17 on GH #2323 — "Make all the reviews adversarial in nature. Helps maximize productivity." Empirical support: in that same session, all 5 plans I drafted got MAJOR from Codex+Gemini while my own Claude review gave MINOR for 4 of them — the adversarial prompt surfaced blockers that a charitable pass would have missed.

**How to apply:**
- Any time you write a review prompt (plan review, code review, artifact audit, PR feedback), include all six clauses: adversarial framing, anti-praise, bias toward non-approval, evidence-per-finding, source-skepticism, empty-review-is-failure.
- When delegating review to another agent (Codex, Gemini, subagent), use the canonical stance contract — see `scripts/review/plan-review-prompt.md` (once #2323 lands) or the stance section in `.claude/skills/coordination/cross-review-policy/SKILL.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` Step 3.
- If a review comes back APPROVE without a check-list of what was verified, treat it as suspect and rerun with a stronger prompt.
- Don't soften prompts to keep cost down — the downstream rework cost dominates the review cost.
