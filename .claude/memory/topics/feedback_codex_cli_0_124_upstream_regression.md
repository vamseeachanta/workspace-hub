> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codex_cli_0_124_upstream_regression.md

---
name: codex-cli 0.124.0 upstream stdin-hang blocks all cross-reviews
description: Feedback 2026-04-24 — codex-cli 0.124.0 installed 2026-04-23 15:06 blocks all `codex exec` invocations with "Reading additional input from stdin..." regardless of stdin redirection. Not patchable in workspace scripts. Workaround: pin/downgrade to 0.123.0. Tracked in #2479.
type: feedback
originSessionId: 3415d1dc-e37e-4069-a1eb-a2a3a2c2ca83
---
codex-cli 0.124.0 introduced an upstream stdin-detection regression that causes every `codex exec` invocation to hang on "Reading additional input from stdin..." (exit 124 after timeout), regardless of our wrapper's stdin redirection.

**Why it matters:** Every `scripts/review/cross-review.sh` / `scripts/review/submit-to-codex.sh` / `scripts/review/plan-review-fanout.sh` call silently degrades to 2-provider review (Claude + Gemini only). Do NOT trust "consensus MAJOR" signals when Codex is UNAVAILABLE — the third provider carries unique defect-detection signal per `feedback_cross_provider_review_payoff`.

**Scope of failure:** Reproduces on plans as small as 90 bytes (NOT size-dependent as earlier batch analysis suggested). Install timestamp `2026-04-23 15:06:20` matches first-failure day exactly. Tested blocking paths:
- `</dev/null`
- `exec 0<&-`
- `setsid`
- `script(1)` tty faking

None of these defeat the upstream detection logic.

**Downgrade does NOT help from Claude Code's Bash tool** (verified 2026-04-24 session continuation). Tested 0.124.0, 0.123.0, and 0.122.0 — all three hang. 0.123/0.124 print the "Reading additional input from stdin..." banner; 0.122.0 hangs silently. Consistent with Claude Code's Bash tool providing a non-closeable stdin layer that does not propagate EOF to the codex subprocess, regardless of `</dev/null`, `exec 0<&-`, `setsid`. **The downgrade may still restore Codex in a plain user terminal** — it is untested from outside Claude Code in this session. Tell the user: "run `npm install -g @openai/codex@0.123.0` from your own terminal and validate `codex exec "ping" </dev/null` responds before relying on it."

**How to apply:**
- If user asks "why is Codex UNAVAILABLE" or "can we re-run the Codex review": point to #2479 and offer the downgrade (`npm install -g @openai/codex@0.123.0`) as the immediate practical workaround **for a plain user terminal**. Do NOT attempt to validate the downgrade from a Claude Code Bash tool session — stdin propagation is the confound.
- In adversarial review prompts, explicitly frame Codex as "currently expected UNAVAILABLE — 2-provider consensus is the best we can do until upstream fix or downgrade."
- Do NOT mark a plan "ready for approval" based solely on Codex UNAVAILABLE + Claude+Gemini clean — surface the 2-provider limitation and let user decide.
- The related wrapper-flag fix (`--no-interactive` removal at `plan-review-fanout.sh:82`, commit 257b47dd9 on `fix/codex-stdin-hang`) is CORRECT but INSUFFICIENT on its own. It prevents rc=2 flag errors but does not fix the stdin hang.
- #2406 stays closed-as-superseded. Its `</dev/null` fix was correct for codex-cli 0.121.0 at close time. Current regression is a distinct upstream event tracked in #2479.
- When Lane F-style infra work needs to happen under parallel-agent git contention, use an isolated worktree (as Lane F did at `/mnt/local-analysis/worktrees/lane-f-codex-fix/`) — avoids main-workspace FUSE lock races.
