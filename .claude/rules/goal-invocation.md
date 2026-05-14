# /goal invocation contract — agent rule

**When a session is about to invoke `/goal` (or the `planning-goal` / `planning-code-goal` skill), first fetch the canonical /goal use-case catalog at [issue #2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) and the latest weekly picklist comment.**

**Why:** `/goal` is the highest-leverage multi-day planning command we have. Without consulting the catalog + weekly comment, invocations drift toward whatever the current chat suggests, which (a) ignores the weekly token-budget allocation, (b) risks duplicating in-flight `/goal` work in another session, and (c) loses the catalog's "anti-pattern" warnings against shapes that have failed before.

**How to apply:**

1. **Before** running `/goal`, `Skill planning-goal`, or `Skill planning-code-goal`:
   - `gh issue view 2695 --repo vamseeachanta/workspace-hub --json body`
   - `gh issue view 2695 --repo vamseeachanta/workspace-hub --comments | tail -200`

2. **Validate** against the catalog:
   - Match to entries 1-23 (generic) or 24-30 (ecosystem-tuned)
   - If no match: name the gap to the user; do NOT silently invoke
   - If match exists but entry is on this week's SKIPPED list: surface and ask whether to override or defer

3. **Check the gate**: `/goal` invocation requires `status:plan-approved` per `feedback_never_offer_to_self_label_plan_approved`. Verify the label is set BEFORE invoking. Never self-approve.

4. **Check runner allocation**: if the weekly picklist names a specific runner (claude / codex / hermes / gemini) and the current session is a *different* runner, surface the mismatch before proceeding (`feedback_multi_agent_commit_serialization`).

4.5. **Brain/hands delegation check** (added per design doc D7): if the catalog entry is `[execution-heavy]` or `[bidirectional]` AND the proposed work has reached planning-complete state (plan exists, `status:plan-approved` is set), surface the option of delegating execution to Hermes (which routes to Claude Code or Codex per cost/quota) instead of running Claude main session end-to-end. The three quota pools (Anthropic Max base, Anthropic Max overage, OpenAI) are consumed *additively*; brain-only invocation wastes layers 3a/3b.

5. **After** invocation completes, post a comment on the catalog issue noting which entry was used and any catalog-vs-reality divergence — feeds the next refresh.

**Do NOT apply when:** the user explicitly overrides ("ignore the catalog this time, just plan X"), OR the catalog issue is unreachable (offline / gh CLI broken). In the unreachable case, surface the gap and proceed with standard `planning-goal` skill flow, noting in the resulting plan that catalog validation was skipped.

**Cross-runtime note:** This rule binds Claude only (it lives in `.claude/rules/`). Codex and Hermes dispatch prompts must include the catalog issue number explicitly — they read the issue body directly via `gh issue view`.

**Pilot reference:** [issue #2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) (the catalog) — bootstrap state as of 2026-05-13: 23 generic + 7 ecosystem-tuned entries, brain/hands tagged; refresh cadence weekly; weekly picklist posted as fresh comments.

**Related:**
- Design doc: `docs/governance/2026-05-13-goal-use-case-catalog-design.md` (D1-D7)
- Hermes upgrade audit: [#2696](https://github.com/vamseeachanta/workspace-hub/issues/2696) — verifies routing-layer assumptions for Step 4.5
- Cross-review depth rule: `feedback_always_adversarial_review_scale_depth`
