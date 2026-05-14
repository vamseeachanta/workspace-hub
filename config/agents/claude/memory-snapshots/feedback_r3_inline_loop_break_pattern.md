---
name: r3-inline-loop-break-pattern
description: "When r1 and r2 cross-review both surface MAJOR with DIFFERENT defects each round (not same defects recurring), apply r3 patches inline in main session — do NOT dispatch r3 cross-review. This breaks the sustained-MAJOR anti-pattern early. Used 2026-05-13 on plans"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37c4fd1d-3784-4903-a5ea-5fe997dd7044
---

**When cross-review keeps finding NEW defects each round (rather than the same defects recurring), the plan is genuinely improving with each pass — but each pass also introduces fresh defects from the revision itself. Break the loop at r3 with main-session inline patches; do NOT dispatch r3 cross-review.**

**Why:** 2026-05-13 — Plans [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685) and [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694) went through r1 + r2 cross-review:
- r1 surfaced N original defects (well-grounded)
- r2 revision fixed all r1 defects but introduced 2-4 NEW defects (e.g., `self.repo_root` AttributeError because the revision added a kwarg reference without adding the field)
- Multi-provider convergence on the new defects (codex+claude+gemini all caught r2's `self.repo_root` issue)

This pattern is DIFFERENT from the sustained-MAJOR anti-pattern in `feedback_codex_sustained_major_loop`:
- Anti-pattern: same defects flagged 3+ times across rounds (#2510 hit r14)
- Plan-evolution pattern: each round finds NEW defects from the prior round's revision

But continuing to r3, r4, r5 risks the anti-pattern. The break is:
1. After r2, apply the r2 defects as **main-session inline patches** (not subagent — too risky for code-shaped fixes)
2. Mark plan with explicit `r3 (4 r2 defects patched inline; sustained-MAJOR loop break per feedback_codex_sustained_major_loop)` status block
3. Label `status:plan-approved` directly (user-approved gate; do NOT auto-toggle)
4. Document the loop-break rationale in the issue comment so future readers understand why no r3 review was dispatched

**How to apply:**

1. **Spot the inflection point**: r2 review still MAJOR but findings are different from r1.
2. **Surface to user**: present 3 options — (a) r3 patch inline, (b) park plan, (c) r3 review (warn about loop risk).
3. **If user picks (a)**: main session applies fixes. Read each defect from r2 artifacts (`scripts/review/results/2026-05-13-plan-{NUM}-{provider}.md`). For each, edit the plan section. Don't introduce new framings — preserve r2 structure, only fix the specific bugs.
4. **Convergent multi-provider findings get priority** — if all three providers flagged the same defect (like #2685's `self.repo_root`), it's load-bearing. Patch first.
5. **Single-provider findings need judgment** — Gemini's overlay-blind FPs (per `feedback_gemini_sandbox_overlay_blindness`) are ignorable; Codex-only findings against actual code-tree state are usually valid.
6. **Do NOT iterate**: after r3 inline, label plan-approved. Future-r4 work shifts to *execution-time* fix-during-coding.

**Red flags to escalate (DO dispatch another review):**
- r2 surfaces a regulatory hazard the revision didn't catch (e.g., #2694's units-contract gap is borderline — Claude r2 found it because it's the silent-verdict-flip class)
- r2 surfaces a numerical-falseness defect (calc returns wrong number) — verify with Python recomputation, then patch + maybe re-review
- The r2 patches themselves require touching code (not just plan prose) — escalate to user

**Implementation tip:** in r3-applied status block, list each r2 defect by provider+round so traceability is clear:
```
> r3 patches: ...
>  - Replace self.repo_root → kwarg (codex+claude+gemini r2 F1)
>  - Fix CitationResolutionError keyword-only (codex r2 F2 / gemini r2 F3)
>  ...
```

**Related memory:**
- [[feedback_codex_sustained_major_loop]] — the anti-pattern this breaks early
- [[feedback_gemini_sandbox_overlay_blindness]] — ignore Gemini file-existence FPs
- [[feedback_cross_provider_review_payoff]] — Codex finds non-overlapping defects vs Claude
- [[feedback_never_offer_to_self_label_plan_approved]] — user gate on plan-approved is preserved even with inline-break
