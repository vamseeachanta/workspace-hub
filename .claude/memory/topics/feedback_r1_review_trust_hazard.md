> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_r1_review_trust_hazard.md

---
name: r1-review-trust-hazard
description: "before applying an r1-review fix asserting that something is missing, independently verify the asserted gap by reading the relevant source — reviewers have constrained retrieval"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 88b3956a-7a96-4346-9dbe-674f5fb0b4e9
---

Before applying an r1-review "fix" that asserts a gap or missing behavior, independently verify the asserted gap by reading the relevant source. Don't trust the reviewer's claim of absence — reviewers have constrained retrieval (sandbox limits, GitHub-connector vs. local-shell asymmetry, partial file reads).

**Why:** 2026-05-15 Plan C ([#2710](https://github.com/vamseeachanta/workspace-hub/issues/2710)) cascading-false-premise incident. r1 Codex review asserted "missing-file validation gap contradicts AC — submit-job.sh only checks empty INPUT_FILE." The r1 revision (agent-drafted, my-committed) trusted that finding and ADDED a wrapper-layer `[[ -f "${REPO_ROOT}/${INPUT_FILE}" ]]` check. r2 Claude review then caught it: `submit-job.sh:18-23` has had the existence check since commit `71a53898b` (the original queue-infrastructure commit). The r1 "fix" introduced a duplicate-validation block that VIOLATED the issue's own AC 5 ("No duplicate validation logic — both layers funnel into submit-job.sh"). One missed file-read at r0 corrupted everything downstream until r2 catch.

**How to apply:** Before applying any r1 fix that says "the codebase lacks X" or "the codebase doesn't validate Y":

1. Read the asserted-missing surface yourself. `grep -rn` for the missing behavior across all callers + the cited file's full contents (not just the lines the reviewer cited).
2. If the behavior IS already present, the r1 finding is a false positive. Do NOT add the proposed fix; instead, post a counter-finding on the review artifact explaining the existing implementation.
3. If the behavior is genuinely absent in the cited surface but present elsewhere, document the location and decide whether the centralization vs. duplication tradeoff justifies the fix.
4. Specifically watch for reviewers' "selective quote" patterns — r2 Plan C caught that r1 had selectively quoted `submit-job.sh:8-16`, ending precisely one line before the existing check at `:18-23`. The quote was technically accurate but misleading by omission.

**Cross-reference:**
- [[feedback_cross_provider_review_payoff]] — when r1 (Codex) and r2 (Claude/another provider) disagree on whether a thing exists, the second provider's grounded-read should be authoritative. This memory complements that one: actively verify, don't passively trust.
- [[feedback_codex_sandbox_fallback_paths]] — Codex sandbox limitations explain why r1 reviewers sometimes assert "missing" when they really mean "couldn't reach."
- [[feedback_subagent_write_phantom]] — independent-verify pattern applied to subagent Write claims; this is the analog for review-claim verification.

Applies to Codex, Gemini, Claude reviewers — any provider whose sandbox/retrieval may miss content the local repo has.
