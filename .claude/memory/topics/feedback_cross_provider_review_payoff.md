> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_cross_provider_review_payoff.md

---
name: cross-provider review yields materially different findings
description: Single-provider review (especially repeat Claude passes) trends toward charitable APPROVE; the planning-skill 2+ provider rule isn't just procedural — second provider often finds non-overlapping defects of equal severity
type: feedback
originSessionId: 2a425341-f5c9-4fd7-b9e7-778c66573cfc
---
When the planning skill mandates 2+ provider adversarial review, treat it as substantive, not bureaucratic. Empirical evidence from 2026-04-17 Thrust A on #2205 children:

| Issue | Claude alone | Codex independent | Overlap |
|---|---|---|---|
| #2207 | 3 MAJOR + 4 MINOR | 4 MAJOR | zero |
| #2209 | 3 MAJOR + 4 MINOR | 4 MAJOR + 1 MINOR | zero |
| #2206 | 5 MAJOR + 3 MINOR | 5 MAJOR + 1 MINOR | zero |

Claude tends toward contract-vs-contract logic (internal consistency, parent-child rule alignment). Codex tends toward contract-vs-shipped-data evidence (sampling real files, comparing prescribed schemas to live ones). Both are necessary; neither alone is sufficient.

**Why:** Three prior Claude reviews on each issue (2026-04-11 implementation review, 2026-04-11 final review, 2026-04-16 overnight) all returned APPROVE / "no issues found" despite the deliverables having 11–14 defects each. Repeat-Claude passes don't catch what fresh-perspective passes catch. The planning skill's reviewer-stance contract (no praise, evidence-required, empty findings = failure) prevents the rubber-stamp pattern only when actually applied — and the strongest defects come from the second provider, not from making one provider try harder.

**How to apply:** When asked to review or audit a plan, deliverable, or contract:
1. Don't accept "Claude already reviewed this" as satisfying cross-provider review — verify Codex/Gemini artifacts exist on disk.
2. When dispatching Codex, use a sharp prompt that explicitly says "your job is NOT to confirm Claude — find what Claude missed."
3. After Codex returns, spot-verify load-bearing claims locally — Codex's GitHub-connector evidence can misread untracked-but-present local files as "absent from repo" (verified twice on 2026-04-17 with `digitalmodel/` and `personal/wiki/index.md`).
4. Even one charitable review in a chain undoes the value of the rest — if any prior review returned "no issues found," treat the whole review history as suspect and re-run.
