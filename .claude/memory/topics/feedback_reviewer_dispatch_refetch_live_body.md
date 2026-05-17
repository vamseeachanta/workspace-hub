> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-17
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_reviewer_dispatch_refetch_live_body.md

---
name: feedback_reviewer_dispatch_refetch_live_body
description: "Before dispatching any provider review (Codex / Gemini / Claude subagent), refetch the live artifact body; never reuse a prior /tmp/<prompt>.txt from an earlier dispatch round."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 214b6592-b65b-480f-accf-16e6a9761175
---

When dispatching a cross-review (codex exec, gemini -p, submit-to-*.sh, or Agent subagent for review) against a GitHub issue body or plan file, refetch the live current content immediately before each dispatch. Never reuse a `prompt.txt` or rendered file from a previous round.

**Why:** workspace-hub#2719 Phase 8 (2026-05-16): I dispatched a Gemini r2 rerun against `/tmp/gemini-r3-prompt.txt`, which was a copy of `/tmp/codex-r2-prompt.txt` from the pre-r3-reshape round. The issue body had already been replaced via `gh issue edit --body-file` with the reshape that absorbed r1+r2 findings. Gemini's review returned MAJOR with 5 findings, **all of which had already been fixed** by the r3 inline patches + Phase 1-7 implementation (target: bootstrap-machine.sh hallucination AC, Hermes-SOUL-has-zero-references claim, Codex SOUL dead-code, etc.). The verdict was valid for stale input but invalid for the as-built state. Re-running against current input would have cost another quota cycle for what is now convergent-validation-only evidence.

This is a sibling pattern to:
- [[feedback_plan_past_tense_artifact_claims]] — plans describing proposed work as already-committed artifacts trick reviewers
- [[feedback_codex_needs_pushed_artifact]] — Codex sandbox can't read local files; the artifact must be pushed
- [[feedback_r1_review_trust_hazard]] — independently verify reviewer-asserted gaps before applying fixes

**How to apply:**

1. **Refetch immediately before dispatch**, even within the same session:
   ```bash
   gh issue view "$N" --repo "$REPO" --json title,body \
     -q '.title + "\n\n" + .body' \
     > "/tmp/issue-${N}-live-body-$(date +%Y%m%dT%H%M%SZ).md"
   ```
2. **Use a timestamped filename** so cached versions from earlier rounds are visually distinct. Never overwrite an existing prompt file.
3. **For plan-file reviews**, refresh from disk: `cp docs/plans/<plan>.md /tmp/plan-${SHA}-$(date +...).md` so each dispatch records what was reviewed.
4. **If the dispatch returns "discovers" issues you know are already fixed**, your first check is *was the input stale?*, NOT *was the verdict wrong?*. Verify the prompt body matches the live state before treating findings as actionable.
5. **In follow-up review comments**, cite the timestamped input file (or quote first 3 lines of the prompt body) so audit can verify what was actually reviewed.

**Do NOT apply when:** dispatching a fresh round on an artifact that hasn't changed since the last review (rare; typically the artifact moves between reviews). When in doubt, refetch.

**Verification (2026-05-16):**
- Stale prompt fingerprint: `head -3 /tmp/gemini-r3-prompt.txt` showed "Cross-provider analysis (2026-05-15) surfaced four structural defects"
- Live issue body fingerprint: motivation section reshaped to "## Motivation (reshaped per F1, F2)"
- These don't match → stale → review verdict is invalid for as-built state
