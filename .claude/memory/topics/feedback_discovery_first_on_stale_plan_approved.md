> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_discovery_first_on_stale_plan_approved.md

---
name: discovery-first-on-stale-plan-approved
description: "Before executing a long-standing status:plan-approved issue, run a discovery pass against the codebase first — prior commits may have silently completed most or all of the scope. Skipping discovery wastes effort and risks duplicate-write conflicts."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 72238262-9b25-493d-9731-fc22b67185aa
---

# Discovery-first on stale plan-approved issues

**Rule:** When you pick up a `status:plan-approved` issue that was approved more than ~7 days ago, do a discovery pass against the codebase **before** writing any code. Specifically:

1. Read the issue's acceptance criteria and named candidates.
2. Inventory the target directory (`ls`, `git ls-files`).
3. Read 1–2 existing comparable artifacts to learn the prevailing schema/style.
4. For each named candidate from the acceptance criteria, check whether a matching artifact already exists.
5. Only AFTER discovery, decide: execute the full plan, execute a narrowed gap, or close as already-complete.

**Why:** A `status:plan-approved` label is a contract about *intent*, not about *current state*. Between approval and dispatch, the corpus moves — parallel sessions, batched commits in adjacent issues, or rolling refactors can land work that overlaps the plan. Two consecutive issues in the 2026-05-15 session demonstrated this:

- **llm-wiki #41** (maritime-law standards routing): plan-approved scope = SOLAS+MARPOL+MLC+ISM Code routing. Discovery pass found 25 standards pages already landed by iter-25/-26 bootstrap (2026-05-09). The actual gap was 1 file (ISM Code). Saved ~95% of planned work.
- **llm-wiki #42** (lng-projects standards routing): plan-approved scope = CSA-Z276+NFPA 59A+IGC Code routing. Discovery pass found 10 standards pages already landed by iter-23/-24/-28 bootstrap arc. The actual gap was **zero**. Closed as already-complete with full attestation.

In both cases, the prior bootstrap commits were part of `docs(multi):` cross-wiki audit-driven batches — exactly the kind of work that doesn't show up under the issue tree because it's authored elsewhere and incidentally satisfies the issue's scope.

**How to apply:**

- Discovery first, write second. Use the same disciplined steps every time: read acceptance criteria → inventory → read 1-2 comparables → cross-check named candidates → decide.
- If discovery reveals the work is fully or substantially done: close the issue with an "already-complete" comment that attests each acceptance criterion against the existing on-disk state, AND cite the prior commit SHAs that landed the work. This builds an audit trail showing the issue was discharged by verification rather than execution.
- If discovery reveals a narrow gap: scope your write down to just that gap. Don't expand to "complete what's there" — the rest is already there.
- If discovery reveals nothing was done: execute the full plan as approved.
- **Trust the corpus over the issue tree.** A 2-week-old plan-approved issue with no recent activity is more likely overlapping than orphan.

**Anti-pattern to avoid:** "The label says plan-approved → execute the plan." This pattern wastes effort, risks duplicate-write conflicts (multiple ISM Code pages with divergent frontmatter), and pollutes the corpus with rework-flavored commits.

**Variant — external-source policy verification (added 2026-05-17):**

For permission-request style issues (e.g., "send reuse-permission email to publisher X"), the same discovery-first principle applies, but the verification target is the *publisher's own published policy*, not prior commits in the repo.

Before drafting a reuse/permission-request email for a public-corpus destination (CC-BY-4.0, MIT, etc.), do a 2-3 minute WebFetch sweep of the publisher's publishing-policy page + terms-of-use page first. A clear public-domain or open-license statement can resolve some or all rows without an email at all.

llm-wiki [#98](https://github.com/vamseeachanta/llm-wiki/issues/98) example (KGS reuse-permission email, 2026-05-17): 5 rows queued for email confirmation; pre-draft fetch of KGS [Publishing Policy](https://www.kgs.ku.edu/Publications/pubPolicy.html) (`"All KGS publications are public domain and therefore can be reproduced without permission"`) + [Terms of Use](https://www.kgs.ku.edu/General/copyright.html) resolved 3 of 5 rows (LA Bulletin A19-A21) via direct policy citation. Email narrowed to 2 rows (A22 Open-File Reports archive + A23 Magellan LAS data, where the general policy might not blanket-apply because of per-document or data-vs-publication distinctions). Saved ~60% of the originally-approved email scope; cut KGS staff time; stronger audit trail.

**Crucial follow-on rule:** Per [[never-offer-to-self-label-plan-approved]], surface the policy finding to the user via `AskUserQuestion` before changing scope — don't unilaterally skip the email. The user-approval gate is frozen at the moment of approval; new discoveries that narrow scope are still scope changes.

**Related:**
- [[plan-past-tense-artifact-claims]] — same root cause from the planning side (plans describing proposed work as committed artifacts)
- [[commit-attestation-narrow-scope]] — close-narrative attestation should cite specific files + criteria, not generic "complete"
- [[gh-issue-close-silent-comment-drop]] — when an issue auto-closes via `Closes #N` trailer before your `gh issue close --comment` runs, use reopen → comment → close to recover the narrative
