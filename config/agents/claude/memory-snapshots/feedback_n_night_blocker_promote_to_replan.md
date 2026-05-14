---
name: n-night-blocker-promote-to-replan
description: "When a closure-first / overnight agent reports the SAME blocker on the SAME issue 3+ nights in a row, stop re-running and escalate to a design-replan instead of continuing the polling pattern"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a90910bc-8382-4ffe-b9d4-7ccfe69c9ce4
---

When a `/goal`, closure-first batch, or nightly-poll agent reports the **same root-cause blocker** on the **same issue** for **3 or more consecutive nights**, do NOT spawn a 4th-or-Nth attempt. Instead, halt the polling pattern and surface the divergence as a design question: "is this issue's deliverable shaped right for the operating environment?"

**Why:** observed firsthand on #2403 (embeddings model-selection spike) — 5 prior nightly batch agents (2026-04-28, 2026-04-30, 2026-05-01, 2026-05-02, 2026-05-03, 2026-05-04) each posted near-identical "still blocked on `OPENAI_API_KEY` / `VOYAGE_API_KEY` / `ollama`" comments. The 6th invocation (this session, 2026-05-13) hit the same wall. Polling produced 6 comments of cumulative noise but zero deliverable progress, because the issue's acceptance criteria require numeric measurements and no machine in the rotation has the prereqs provisioned. The fix is not a 7th nightly try; it's either (a) provision the prereq once, or (b) replan the spike scope (e.g., drop to BGE-M3-only).

**How to apply:**

1. **On `/goal` preflight**, when reading recent comments on the target issue, scan for prior closure-first/nightly-batch comments with same-root-cause language ("still blocked", "blocker recheck", "no measurement backend"). If you see ≥3 such comments in ≥3 distinct calendar dates, treat this as an **N-night-blocker signal**.

2. **Do NOT spawn an Nth attempt that will hit the same wall.** Instead:
   - Post a single audit comment naming the pattern explicitly ("this is the Nth nightly attempt blocked on the same prereq")
   - Surface 2-3 concrete recovery paths to the user (provision prereq / replan scope / defer)
   - Halt the session

3. **If the user is overnight-absent**, do not unilaterally take risky recovery actions (system installs, credential provisioning). The audit comment IS the deliverable; morning-user opens the issue and sees the pattern named, not a 6th "still blocked" message.

4. **Consider promoting to design issue.** Per `.claude/rules/patterns.md` enforcement gradient: prose rule (do this in skill) → script (CI check) → hook (pre-invoke gate). After 3+ nights, the right escalation is filing a `/spec-phase` or `/discuss-phase` re-examination of the issue's deliverable shape, not another execution attempt.

5. **Cross-link the prior blocker comments** in the audit so the pattern is durable. Don't let each agent re-discover the pattern from scratch.

**Do NOT apply when:**
- The blocker root cause is *different* each night (legitimate progress, just hitting new walls — keep going)
- The user has explicitly directed an Nth attempt with new context (e.g., "I just provisioned the key, retry tonight")
- Fewer than 3 prior identical-root-cause comments exist (could just be 2 unlucky nights)

**Related:**
- `feedback_check_parallel_work` — the parallel-work scan should also detect this serial-blocker pattern (same issue, multiple prior agents, same root cause)
- `feedback_no_shortcuts_knowledge` — the temptation under N-night-blocker is to shortcut (fake numbers, pick a default). Resist.
- `.claude/rules/goal-invocation.md` — `/goal` preflight rule that should probably gain an explicit N-night-blocker check in a future revision
- `feedback_never_offer_to_self_label_plan_approved` — related principle: don't escalate decisions to yourself when the human-in-loop gate is the load-bearing surface. N-night-blocker decisions belong to the user, not to the polling agent.

**Pilot reference:** [#2403](https://github.com/vamseeachanta/workspace-hub/issues/2403) — embeddings model-selection spike, 6 nightly attempts (2026-04-28 → 2026-05-13). 6th invocation (this session) halted at preflight rather than spawning #7-blocked comment.
