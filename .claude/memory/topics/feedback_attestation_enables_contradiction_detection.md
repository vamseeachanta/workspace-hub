> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_attestation_enables_contradiction_detection.md

---
name: attestation enables plan-vs-reality contradiction detection
description: Cross-review attestation (#2405) is more than Class-B noise suppression — it unlocks a new adversarial-review mode where reviewers cite plan-vs-live-state contradictions as defects
type: feedback
originSessionId: 4bae6403-8b91-4ee7-9adf-a7410cea0dc0
---
Cross-review attestation (implemented in #2405, commit `965ced541`) turned out to be more valuable than I scoped: it does not merely silence Class-B "unverified claims" findings — it unlocks a new class of precise defect detection where adversarial reviewers actively cite **plan-prose-vs-attested-reality contradictions** as concrete defects.

**Why:** Live validation on 2026-04-20 dispatched the preserved #2392 plan through the updated `submit-to-codex.sh`. Codex returned MAJOR with 6 defects, **zero** Class-B "unverified" findings. Three of those 6 defects were unreachable before attestation:

- Plan claims 4 registry YAMLs `EXIST`; attestation marks all `MISSING`.
- Plan header says `Status: plan-review` for #2392; attestation says issue `CLOSED`.
- Plan cites its own adversarial-review artifacts as references; attestation marks them `MISSING`.

Before attestation, adversarial reviewers had two failure modes — rubber-stamp APPROVE (optimistic reading) or blanket "unverified claims" MAJOR (defensive reading). Neither located real defects. Attestation enables a third mode — **defect detection via contradiction** — that was the real adversarial-review goal all along.

**How to apply:**

- When drafting future plans (especially doc-intel, workflow, or anything citing live repo state), keep plan prose honest about current state. Attested reviewers WILL catch stale paths, stale statuses, and phantom cross-references — these show up as MAJOR.
- When revising plans that failed MAJOR review, prioritize fixing attestation-surfaced findings first — they are objective contradictions. Subjective design feedback comes second.
- When validating new infrastructure (not just this one), run a single cheap end-to-end live test before committing to a heavy dispatch wave. 87s of one Codex call proved the #2405 infrastructure works; reasoning from code alone could not have reached the same confidence.
- A MAJOR verdict from an attested reviewer is now much more informative than before. Treat it as structured diff between plan intent and repo reality, not as a signal to redesign.

Validation artifact: `scripts/review/results/2026-04-20-validation-2405-via-plan-2392-codex.md` (commit `c85657584`).
