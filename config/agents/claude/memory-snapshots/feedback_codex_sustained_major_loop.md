---
name: Codex sustained-MAJOR loop signature
description: When Codex returns MAJOR for 3+ consecutive revisions while Claude+Gemini converge to MINOR, the revision cycle is the #2045/#2289 anti-pattern; surface for user decision rather than auto-cycle past revision 3
type: feedback
originSessionId: e04329da-9917-4fcf-a605-7fed457336e0
---
When three adversarial reviewers disagree across multiple revisions in this specific pattern — **Codex sustains MAJOR, Claude + Gemini converge to MINOR by revision 2-3** — stop auto-cycling after revision 3 or 4 and surface the consensus-vs-minority decision to the user.

**Why:** Observed in #2045 (24-rereview loop) and #2289 (6-revision policy-plan cycle, 2026-04-21). In both, Codex's findings were concrete and fixable each round but kept shifting targets — fixing v-n's Codex MAJOR produced new v-(n+1) Codex MAJORs, often on unrelated edges of the plan's policy surface. Claude and Gemini settled to MINOR early (typically by v2-v3). Auto-cycling past revision 3 burns ~30-60 min per cycle without reducing finding severity.

**How to apply:**
1. Track per-provider verdicts across revisions. If Codex has been MAJOR for 3+ consecutive while Claude+Gemini are MINOR by v3, declare the pattern.
2. Surface to user with options: (a) accept 2/3 MINOR consensus with Codex MAJOR documented as implementation-time inputs, (b) scope-narrow the plan to reduce the policy surface Codex can target (worked for #2289 at v4 — policy-only scope cut most findings), (c) stop at current state and park.
3. Do NOT promise bounded cycles then break the commitment. If you say "one more cycle" and Codex still MAJOR, surface — don't do "one more more cycle."
4. The #2289 middle-path precedent — advance to `status:plan-review` with Codex minority-MAJOR documented for implementation-time refinement — is defensible when Codex findings are scope-edge rather than structural.
5. Codex's findings are often still worth reading — current-state drift, approval-over-revert precedence, enforcement-path safe-list loopholes — but reading ≠ cycling.
