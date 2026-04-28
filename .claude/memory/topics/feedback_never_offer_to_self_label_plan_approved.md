> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_never_offer_to_self_label_plan_approved.md

---
name: Never offer to self-label status:plan-approved
description: When presenting a plan for user approval, provide links + CLI commands only — never offer to run the label-transition command on the user's behalf
type: feedback
originSessionId: 6c81f901-2e10-4f46-90c3-d667fca4b19b
---
Never present "tell me 'approved' and I'll run the CLI command for you" or any equivalent that collapses the user-approval step into a chat response. The plan-approval label transition must always be a discrete action the user takes themselves (CLI paste, web UI click, or explicit chat command they authored).

**Why:** User feedback on 2026-04-21 — "helps users be in control of the planning and awareness of work done. The most important repo phase." Planning is where course-correction is cheapest; rushing the approval gate erodes that safety. CLAUDE.md already codifies this as "USER APPROVES → `status:plan-approved`" + "Batch agents: only act on `status:plan-approved` issues; never self-approve", but the rule extends to *offering* to self-approve on the user's behalf, not just technically executing the transition.

**How to apply:** When presenting round-N review results on a plan, give the user:
- Links to read the plan at a stable commit ref
- Links to the reviewer artifacts
- A CLI one-liner they can paste into their own shell, OR
- Web UI navigation steps

Do NOT offer a fourth "just tell me and I'll do it" option, even as a convenience. The friction of the user taking the explicit action IS the value — it's the moment of deliberate approval, not an obstacle to route around. This applies even when the user has said "continue with recommendation(s)" multiple times in the session — that authorization never extends to the plan-approval label itself.

**Extension — session-handoff prompts (added 2026-04-21):** the same rule applies when drafting session-entry prompts inside GitHub issues meant for future sessions to pick up. Do NOT write prompts that contain phrases like "no user approval needed for items X-Y" or "safe to execute without further approval" or "items 1-2 don't require user approval each time" — even if the investigation verdict is confident (e.g., "INTENTIONAL migration, high confidence"). Pre-approval baked into a handoff prompt is self-approval by proxy: a downstream agent reading it will interpret it as authorization, bypassing the user gate.

Instead, every handoff prompt must:
1. Explicitly say the issue contains investigation context only (no plan, no adversarial review) if that is the case.
2. Require the receiving session to follow the full planning workflow per CLAUDE.md: Resource Intel → Plan → Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved` → Implement.
3. Include the verbatim line: "WAIT FOR USER to set `status:plan-approved` — do NOT self-approve."

**Why this extension:** 2026-04-21 session created #2433 + #2437 with session prompts that pre-empted the approval gate; user caught it ("confirm these gh issues went through adversarial plan reviews?"). The failure mode is subtle because it looks like "efficient handoff" but actually collapses the user-in-loop step across session boundaries. Corrected via AMENDMENT blocks on both issue bodies; originals preserved for audit trail.
