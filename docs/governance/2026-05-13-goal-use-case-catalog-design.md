# /goal use-case catalog — design

**Date:** 2026-05-13
**Status:** design ready for review; implementation plan deferred to `writing-plans` skill
**Issue:** [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695)
**Related:** [#2675](https://github.com/vamseeachanta/workspace-hub/issues/2675) (provider role matrix — adjacent, not duplicate), [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089) (weekly Hermes parity sweep), [#2399](https://github.com/vamseeachanta/workspace-hub/issues/2399), [#2549](https://github.com/vamseeachanta/workspace-hub/issues/2549)

## Why this exists

`/goal` (and the underlying `planning-goal` / `planning-code-goal` skills) is the highest-leverage multi-day planning command this ecosystem has. It works across Claude Code, Codex CLI, and Hermes — but invocation today is *ad hoc*. Two failure modes appear in session history:

1. **Drift toward whatever the current chat suggests** — `/goal` gets invoked on shapes that don't reward it (one-line fixes, trivial reads), burning planning-context tokens without the multi-step payoff.
2. **No memory of which shapes paid off** — high-ROI patterns like "cross-provider review apparatus config" or "marine recompute campaign" recur quarterly but aren't catalogued, so each invocation reinvents the framing.

This catalog fixes both by:
- Listing the work patterns where `/goal` earns its keep (Tier 1 generic from external source + Tier 2 ecosystem-tuned for our domains)
- Wiring a thin rule that makes Claude consult the catalog before invoking
- Posting a weekly picklist comment that turns the catalog into operational planning input — so when token quotas reset Monday, the queue is ready

## Design decisions (with rationale)

### D1. Single GH issue is the canonical surface
**Decision:** The catalog lives in one GitHub issue (#2695). Tier 1 + Tier 2 in the body; weekly picklists in comments.
**Why:** Claude reads `.claude/rules/` automatically, but Codex and Hermes don't. A GH issue is the only durable surface all three agent runtimes can consume identically via `gh issue view`. Cross-runtime canonical-ness > Claude-private convenience.
**Alternatives rejected:**
- *In-repo file in `docs/governance/`*: needs separate Codex/Hermes hookup wiring; Hermes dispatch prompts already include issue numbers natively.
- *Two surfaces (issue + skill mirror)*: doubles maintenance for negligible benefit; risks drift.

### D2. Tier 1 generic + Tier 2 ecosystem-tuned
**Decision:** Tier 1 (1-23) is the verbatim list from the source tweet. Tier 2 (24-30) is 7 categories biased toward our domains: marine engineering, calc citation, cross-provider AI review, knowledge wiki coverage, repo governance, headless ops, domain knowledge sweeps.
**Why:** Tier 1 alone is too generic for our work — it skews toward web/SaaS patterns. Tier 2 alone loses the calibration value of comparing to a known-good external reference. Splitting preserves both signals.
**Format choice:** Tier 1 uses just titles (matches source). Tier 2 adds "looks like" + "anti-pattern" lines because, unlike Tier 1, our entries need to be specific enough that Codex/Hermes won't mis-classify when consulting the issue cold.

### D3. Weekly picklist as fresh comments (not body edits)
**Decision:** Each Monday, post a fresh comment to the issue with 3-5 catalog entries selected for this week, drawn from open issues at `status:plan-approved`. Comment template specified in the issue body.
**Why:**
- Comments preserve a chronological history of what we *intended* vs. what actually ran — six months of comment-vs-commit gap is the strongest possible signal about catalog drift.
- Body edits would lose this history.
- The `SKIPPED` section in the template surfaces the "aspirationally listed, never run" failure mode that would otherwise stay invisible and bloat the catalog forever.

**Hard cap at 5 items per week.** Token budgets across Claude/Codex/Gemini/Hermes only support 3-5 multi-day `/goal` invocations realistically. Listing more guarantees nothing runs.

### D4. Thin rule at `.claude/rules/goal-invocation.md` enforces consultation
**Decision:** ~40-line rule file. Modeled on `.claude/rules/calc-citation-contract.md`. Tells Claude to fetch issue #2695 body + latest comment before invoking `/goal`. Adds a post-invocation comment-back step to feed the next refresh.
**Why:** A rule without enforcement is theatre. The rule lives in `.claude/rules/` (auto-loaded by Claude per CLAUDE.md) rather than in `docs/governance/` because Claude's the runtime that auto-loads. Codex and Hermes get the issue # in dispatch prompts and read directly — no `.claude/rules/` symmetry needed.
**Escape valves:** The rule has explicit "Do NOT apply when" clauses for explicit user override and unreachable-issue cases. Without these, the rule would get bypassed with `--no-verify` weekly. Pattern adopted from `calc-citation-contract.md`.

### D5. Refresh cadence is weekly, aligned to token-quota windows
**Decision:** Weekly picklist comment. Catalog body refresh is on-demand (when new patterns emerge), not on a clock.
**Why:** Anthropic/OpenAI/Gemini token allocations reset weekly on different DOWs. The picklist needs to be ready Monday so the week's planning work fits the available envelope. Monthly would miss multiple quota windows; on-demand-only loses the discipline.
**Future option:** Hook the weekly comment into the existing Hermes parity sweep under [#2089](https://github.com/vamseeachanta/workspace-hub/issues/2089). Deferred — premature automation; let manual cadence prove the format first.

### D6. Full planning-workflow rigor (Steps A-H)
**Decision:** Treat this meta-issue per the workspace-hub planning workflow: file issue → design doc (this) → formal plan (next) → adversarial review → status:plan-approved → implementation.
**Why:** Self-consistency. The rule this issue creates says "validate /goal invocations against the catalog issue." If we bypassed the workflow to file the catalog itself, we'd be designing a rule we'd already broken on day one. The opposite — applying our own discipline to filing the discipline — signals the contract is real.

## Artifact list

| # | Artifact | Path | Status |
|---|---|---|---|
| 1 | Catalog issue | [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695) | filed 2026-05-13 |
| 2 | Design doc (this) | `docs/governance/2026-05-13-goal-use-case-catalog-design.md` | draft for user review |
| 3 | Formal plan | `docs/plans/2026-05-13-issue-2695-goal-use-case-catalog-plan.md` | deferred to `writing-plans` skill |
| 4 | Rule file | `.claude/rules/goal-invocation.md` | post-`status:plan-approved` implementation |
| 5 | Rule index update | `.claude/rules/README.md` | post-`status:plan-approved` implementation |
| 6 | First weekly comment | comment on #2695 | post-`status:plan-approved` implementation |

## Non-goals (deliberately out of scope)

- **A new orchestrator or CLI** — `/goal` is an existing skill; this catalog wraps it, not replaces it.
- **Replacing #2675's provider role matrix** — that issue answers "which agent does what work"; this issue answers "which work shapes fit /goal." Both should ship and cross-reference.
- **Replacing #2089's weekly parity sweep** — different scope; the picklist comment may eventually fold into #2089 but doesn't have to.
- **Cost/quota model** — proper modeling of token economics is a follow-up; the picklist surfaces the question without solving it.
- **Auto-population of the weekly comment** — manual for v1; cron-driven follow-up considered for v2 once the manual rhythm is proven.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Catalog drifts from reality (entries listed but never used) | `SKIPPED` section in weekly comment surfaces non-use; quarterly review trims Tier 2 |
| Multiple agents race on the same `/goal` candidate | Weekly comment includes explicit `runner:` field; rule step 4 makes Claude check before invoking |
| Rule consultation is skipped under time pressure | Explicit user-override clause in the rule preserves escape valve, prevents `--no-verify`-style bypass culture |
| Issue # changes (e.g., transferred to another repo) | Rule file hardcodes the issue #; one-line edit fixes it; trade-off accepted for simplicity over indirection |
| Codex/Hermes dispatch prompts forget to include issue # | Codex/Hermes dispatch templates updated as part of implementation Step G |

## Implementation sequence (handed to `writing-plans` skill)

Following workspace-hub planning workflow:
- Step A — File issue (DONE — #2695)
- Step B — Write design doc (THIS — to commit after user review)
- Step C — User reviews design doc
- Step D — Invoke `writing-plans` skill → produces `docs/plans/2026-05-13-issue-2695-goal-use-case-catalog-plan.md`
- Step E — Plan adversarial review at T1 (single-author r3 fits scope — doc-only change, small surface, no provider integration risk)
- Step F — `status:plan-review` → user approves → `status:plan-approved`
- Step G — Implementation:
  - Add `.claude/rules/goal-invocation.md`
  - Edit `.claude/rules/README.md` to list it
  - Update Codex/Hermes dispatch prompt templates to include the catalog issue # (if any exist; verify scope first)
  - Post bootstrap weekly comment for week-of 2026-05-13
- Step H — Close-out comment on #2695 with commit links + bootstrap status

## Open questions for the user

None blocking. The design is internally consistent and matches workspace-hub conventions. Section approvals during brainstorming covered:
- Issue structure (Section 1) ✓
- Tier 2 categories (Section 2) ✓
- Weekly comment format (Section 3) ✓
- Rule file content (Section 4) ✓
- Files and commit plan (Section 5) ✓

If anything in this written form differs from what was discussed, surface it now before Step D.
