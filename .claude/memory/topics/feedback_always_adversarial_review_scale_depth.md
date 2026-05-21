> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_always_adversarial_review_scale_depth.md

---
name: Always adversarial review; scale depth not presence
description: Never offer to skip adversarial review based on T-class or scope; instead scale the review's depth, breadth, and provider count to the work
type: feedback
originSessionId: 182f4d6d-50f2-4629-b01b-4e9187fd0af1
---
Adversarial review is never optional. It is **always** performed before user approval. What scales with scope is the **level** of review, not its **presence**.

**Why:** I had been offering "T1-light → adversarial review optional" as a shortcut for trivial documentation work. User correction 2026-05-09 (issue #2659 plan-review gate): every plan goes through adversarial review; the dial is depth, not on/off. Skipping reviews on small items still produces drift — Codex/Gemini have caught non-overlapping defects on items the implementing agent classified as "obviously fine" (per `feedback_cross_provider_review_payoff.md`). The cost of a short review on a T1 is small; the cost of a missed defect compounds because trivial-classed items are the ones that ship without a second look.

**How to apply:**

1. **Never present "skip review" as an option** in approval-gate framing. Do not write "for T1 docs, adversarial review is procedurally optional" or any equivalent. The choice surfaced to the user is *what kind* of review, not *whether*.
2. **Scale review depth to scope.** Suggested gradient:
   - **T1 (trivial: docs, single-file edit, no runtime claim):** one provider, focused prompt scoped to the actual risk surface (license/firewall, cross-link integrity, schema compliance). Short turn-around.
   - **T2 (standard: multi-file change, has runtime path):** Codex + Gemini, full adversarial-stance prompts, attestation block, full risk-table coverage. Standard `submit-to-codex.sh` + `submit-to-gemini.sh` flow.
   - **T3 (complex: cross-repo, engineering calc, infrastructure):** Codex + Gemini + a third Claude pass (code-reviewer agent), explicit Reproduction Evidence required, attestation, longer prompts that demand verified-check items.
3. **Reviewer-stance contract still applies at every level.** Even the T1 single-provider review must use the adversarial framing from the `issue-planning-mode` skill: "assume defects until proven otherwise, no praise, no restatement, cite file paths, return APPROVE only after verifying."
4. **Do not reduce a review prompt to a checkbox.** A short review is still a real review — the prompt names the risk surface, the reviewer has to find or rule out actual defects.
5. **If a provider is unavailable** (Codex 0.124.0 stdin-hang per `feedback_codex_cli_0_124_upstream_regression.md`, Gemini 429, etc.), record the failure explicitly and proceed with available providers. Do not silently downgrade to "no review."
6. **Cross-reference:** `feedback_adversarial_review_stance.md` (defect-hunting framing), `feedback_cross_provider_review_payoff.md` (Codex/Claude non-overlap), `feedback_codex_sustained_major_loop.md` (when to break out of MAJOR loops with consensus surfacing).

**Concrete consequence for #2659:** the "(a) direct-approve / (b) adversarial review first" choice I offered was wrong-shaped. The right framing was "do you want T1-scoped single-provider review or T2-style full Codex+Gemini?" — both are reviews, neither is a skip. User chose adversarial review explicitly, which I now treat as the floor for any plan-review issue, not a branch.
