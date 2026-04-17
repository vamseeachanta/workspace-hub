# Adversarial Review: #2209 Durable vs Transient Knowledge Boundary

> **Reviewer:** Claude (adversarial stance, per planning-skill reviewer-stance contract)
> **Date:** 2026-04-17
> **Deliverable under review:** `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (created 2026-04-11)
> **Plan under review:** `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md`
> **Prior reviews consulted:** `2026-04-11-issue-2209-claude-review.md`, `2026-04-11-issue-2209-final-review.md`, `2026-04-16-plan-2209-claude-overnight.md` — all Claude.

## Stance declaration

Same stance as the #2207 sibling review: assume defects until proven otherwise; no praise; no restatement; evidence required for every finding. Prior reviews returned APPROVE / "no issues found"; per the planning-skill reviewer-stance contract those are suspect.

## Verdict: **MAJOR** — not approval-ready

One MAJOR finding against parent-policy compliance, one MAJOR misclassification that breaks an audit-trail invariant the planning skill itself depends on, plus the same MAJOR cross-provider review process gap as #2207.

---

## Finding 1 — MAJOR: Section 4.4 invents a new pyramid layer that the parent operating model forbids

**Claim under review (Section 4.4):** Weekly review artifacts are classified as "**Layer:** Between L5 and L6 — Recurring operational evidence." Section 5.1 then routes via "Recurring-operational (weekly review output)." Glossary defines "Recurring-operational artifact" as a distinct class.

**Conflicting parent rule (#2205 Section 2, ownership invariant):** "Every artifact in the intelligence ecosystem belongs to exactly one layer. If an artifact appears to serve two layers, it must be split or assigned to the layer that owns its primary concern. Ambiguous cases are resolved by the **most-durable-owner rule**: assign to the lowest-numbered layer whose ownership definition covers the artifact's primary purpose."

**Conflicting parent rule (#2205 Section 10, child guardrails):** Child issues "must NOT redefine ... The pyramid layers, ownership model, or flow rules."

**Why this is a defect:** The parent operating model has six numbered layers (L1–L6) and an explicit rule that every artifact lives in exactly one. #2209 introduces a hybrid layer ("between L5 and L6") and a third classification ("recurring-operational") that does not appear in the parent. This is precisely the redefinition the parent's conflict-resolution clause forbids without an amendment to #2205. The most-durable-owner rule could solve the weekly-review classification within the existing layers (L5 if execution-evidence dominates; L3 if synthesized findings dominate), but the contract instead invents a new category.

Section 11 item 6 acknowledges this is "a pragmatic classification, not a formal new layer" — but Section 4.4, Section 5.1, Section 6.1 (rows 7–8: "Recurring-operational" as bridge endpoint), and the glossary all treat it as a formal class. The contract simultaneously denies and uses the new layer.

**Required fix:** Either (a) propose an amendment to #2205 to add a formal layer for recurring-operational artifacts, then proceed once the amendment is approved; or (b) reclassify weekly review artifacts under existing layers (most likely L5 for individual outputs, with promoted findings flowing to L3 per the standard L5→L3 path), removing the "recurring-operational" category from the contract entirely.

---

## Finding 2 — MAJOR: `.planning/plan-approved/NNN.md` is misclassified, breaking the planning skill's audit trail

**Claim under review (Section 4.5):** "Plan approval markers (`.planning/plan-approved/`) — Issue lifetime — Delete after issue closure."

**Conflicting authority (`issue-planning-mode/SKILL.md:103`):** "`.planning/plan-approved/NNN.md` marker is authoritative local evidence that approval happened."

**Conflicting authority (`issue-planning-mode/SKILL.md:115`):** Approval markers are listed in the precedence order *above* `docs/plans/README.md` for determining whether plan approval really occurred. The skill explicitly uses these markers to detect approval-state drift after fresh adversarial review evidence rolls back a plan-approved label.

**Why this is a defect:** The contract classifies these markers as transient L6 with retention "issue lifetime" (delete after closure). But the planning skill treats them as audit evidence whose absence can flip an issue's effective state. Deleting them at issue closure means:
- Post-mortem audits of *who approved what when* lose their canonical local witness.
- The skill's "fresh-review rollback rule" (SKILL.md:210-227) cannot inspect prior approval state for closed-but-revisited issues.
- The skill's status-precedence rule (SKILL.md:99-110) explicitly relies on `.planning/plan-approved/` as a tier-2 authority — a tier whose contents the contract proposes to discard.

The contract treats these files as session scratch (L6) when they function as governance audit artifacts (closer to L5 or even durable governance evidence).

**Required fix:** Either (a) reclassify `.planning/plan-approved/*.md` as L5 audit evidence with retention "permanent for closed issues" or "retain until issue is archived," or (b) coordinate with `issue-planning-mode/SKILL.md` to remove the markers' role as approval evidence (which would require a separate skill amendment). (a) preserves the planning workflow; (b) requires changing how approval is verified across the harness.

---

## Finding 3 — MINOR: Two distinct senses of "transient" are used interchangeably

**Claim under review (Section 4.2):** GitHub issues, plans, and reviews are "Layer: L5 — Execution state ... **Durability:** Transient with respect to domain knowledge."

**Conflicting/overlapping claim (Section 4.5):** Session/handoff/scratchpad artifacts are "Layer: L6 — Transient session."

**Conflicting summary (Section 5.2 hard rules):** "A plan file under `docs/plans/` | Transient (L5)" and "A review result under `scripts/review/results/` | Transient (L5)" — using "Transient" without qualifier even though L5 is "Execution state" and L6 is "Transient session."

**Why this is a defect:** The contract uses "transient" both as the parent's L6 layer name *and* as a property of L5 artifacts ("transient with respect to domain knowledge"). A reader cannot tell whether "transient" in Section 5.2 means "L6 layer" or "the L5 transient-with-respect-to-knowledge property." Implementation tooling (e.g., the cleanup script in Section 12 row 5) needs to know which to delete on retention; today the contract permits two readings.

**Required fix:** Reserve "transient" for the L6 layer name. Use a different word (e.g., "execution-bound," "issue-scoped," "non-canonical") for L5's domain-knowledge property. Audit Section 5.2 hard rules and the glossary for consistency.

---

## Finding 4 — MINOR: Retention rules are normative in form but admittedly advisory in effect

**Claim under review (Section 8.1):** Detailed retention table — 30 days for handoffs, 14 days for `.planning/`, 7 days for session signals, 90 days for review results, etc.

**Self-undermining claim (Section 11 item 1):** "This policy defines retention periods but does not implement the cleanup automation. Until a transient-artifact cleanup script exists, **retention is advisory only**. Risk: transient artifacts accumulate indefinitely, blurring the boundary by sheer volume."

**Why this is a defect:** A document marked "Status: Normative" prescribing day-counts that the same document admits won't be enforced creates a de-facto false norm. Reviewers and conformance checkers (#2206) that try to enforce these rules will produce false positives against the actual ecosystem state, where nothing is being cleaned up.

**Required fix:** Either (a) tag retention rules as "advisory pending #2237 transient-artifact cleanup workflow" so #2206 doesn't enforce them prematurely, or (b) defer the retention table to a follow-on issue once the cleanup mechanism exists. Option (a) preserves intent; (b) keeps the contract honest about what is enforceable today.

---

## Finding 5 — MINOR: Promotion criteria are AND-conjunctive and may force under-promotion

**Claim under review (Section 7.1):** "A transient artifact deserves promotion to durable knowledge (L3) when **ALL** of the following are true: Reusability, Verification, Non-redundancy, Source traceability, Stability."

**Stress-test:** A finding that is reusable, verified, novel, and traceable but represents a still-evolving area (fails the "not expected to change within 30 days" stability test) is blocked from promotion. Domain knowledge in active engineering fields (e.g., emerging mooring failure modes) is exactly the kind of finding that deserves wiki capture *because* it's current, not despite being unstable.

**Why this is a defect:** Conservative under-promotion is a real failure mode for the engineering wiki — empirically observable in this repo, where the engineering wiki index is 121 lines vs. marine-engineering's 21,605 (see #2034 backlog). Adding a hard stability gate makes that asymmetry harder to close.

**Required fix:** Either (a) demote stability from a hard criterion to a soft signal ("flag unstable findings with an `under-revision` tag rather than blocking promotion"), or (b) explicitly state that the conjunctive rule is intentional and that under-promotion is preferred to over-promotion, accepting the slow-wiki tradeoff.

---

## Finding 6 — MINOR: 30-day handoff retention conflicts with audit needs for the same window

**Claim under review (Section 8.1):** "Session handoffs (`docs/handoffs/`) — 30 days — Archive or delete."

**Why this is a defect:** Many issues take longer than 30 days from open to closed. Handoffs from earlier sessions on the same work stream often get deleted while the issue is still open and the audit trail is still load-bearing. Section 8.3 expiration signal "associated issue is closed for > 30 days" suggests retention should be tied to issue lifecycle, but Section 8.1's flat 30-day rule does not honor that signal.

**Required fix:** Tie handoff retention to the associated issue's lifecycle (e.g., "retain until associated issue is closed for 30 days") rather than a flat 30-day window. This requires handoffs to carry an issue reference — already proposed in Section 10.1 row 1 ("Add `## Expiration` section with issue reference").

---

## Finding 7 — MAJOR (process): Cross-provider adversarial review is absent

**Same as #2207 Finding 7.** Three Claude reviews, zero Codex/Gemini. Planning skill Step 3 mandates 2+ providers. The 2026-04-16 overnight review's "no issues found" pattern is suspect by skill rule. Codex review on this issue is now in flight in parallel with this review.

---

## Verified claims

- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` exists. Section 4.4 cite is valid.
- `#2205` Section 2 ownership invariant text is reproduced accurately above.
- `issue-planning-mode/SKILL.md` lines 103, 115, 210-227 confirm `.planning/plan-approved/` markers are authoritative local audit evidence.
- The contract's relationship table to #2207 (Section 3) does not overlap with the provenance contract — non-overlap rule honored.
- Section 5.2 hard rules are internally consistent within their own scope (no contradictions among the rules themselves).

## Recommendation

Stay at `status:plan-review`. Findings 1, 2, and 7 are MAJOR and must be resolved before approval. Findings 3–6 should be addressed or explicitly deferred with rationale. Recommend a single coordinated revision pass across #2207, #2209, and #2206 once the #2206 review is also complete.
