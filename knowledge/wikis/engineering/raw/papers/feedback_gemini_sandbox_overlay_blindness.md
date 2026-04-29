> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gemini_sandbox_overlay_blindness.md

---
name: Gemini sandbox overlay blindness — discount file-existence claims in MAJOR verdicts
description: Feedback 2026-04-23 — Gemini's cross-review sandbox cannot see the sparse-checkout workspace-hub overlay; file-missing findings are false-positive at rates of 1-16 per plan and must be verified against `git ls-files` before action.
type: feedback
originSessionId: 3415d1dc-e37e-4069-a1eb-a2a3a2c2ca83
---
Gemini's cross-review sandbox (via `scripts/review/submit-to-gemini.sh` or `plan-review-fanout.sh`) sees only its own `/tmp` cwd, not the sparse-checkout overlay rooted at `/mnt/local-analysis/workspace-hub`. Any "file X is missing" or "path Y does not exist" finding in Gemini's review output is presumptively a false-positive until verified locally with `ls` or `git ls-files`.

**Why:** Observed systemic pattern across a single batch (2026-04-23) where Gemini ran cross-reviews on 8 distinct plans via 5 parallel agent lanes. Every single lane reported Gemini false-positive file-missing claims:
- Lane A #2476: 16 false missing-file findings (the full plan's cited path set)
- Lane B1 #2369: 1 (`scripts/knowledge/registry-freshness-check.py`)
- Lane B2 #2373: 10 (10 ace-shard files) + 7 (engineering standards pages) = 17
- Lane C #2105/#2216/#2227: 6-7 per plan = ~20 total
Plus zero true-positives on the file-existence axis. The pattern is deterministic, not noise.

**How to apply:**
- When processing a Gemini MAJOR verdict: scan for findings of the form "X is missing / does not exist / cannot be found". Verify each with `ls -la X` or `git ls-files | grep -F X` before treating as a real defect.
- If Gemini MAJOR is grounded SOLELY in file-existence false-positives, the verdict can be downgraded. Surface the rebuttal explicitly so the user is not misled.
- Gemini's non-existence findings (contradiction, unexecutable commands, schema mismatches, logic errors) are credible and should be treated normally. Don't blanket-dismiss Gemini.
- This is DISTINCT from the Codex sandbox issue (`feedback_codex_sandbox_no_execution`, `feedback_codex_sandbox_fallback_paths`) — Codex blocks execution but CAN read files via GitHub connector; Gemini blocks file reads entirely.
- Do not try to fix this in the plan prose (Lane A #2476 tried — fails). The mitigation is either (a) a preprocessing step that passes `git ls-files` to Gemini's prompt, (b) routing Gemini through a sandboxed harness that mounts the repo, or (c) accepting Gemini contributes only contradiction/logic findings, not file-existence evidence.
- Related: Lane A's rebuttal file pattern at `scripts/review/results/YYYY-MM-DD-plan-NNNN-gemini-rebuttal.md` is the canonical format for documenting these false-positives alongside the raw Gemini output.
