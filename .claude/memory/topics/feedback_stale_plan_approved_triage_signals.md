> Git-tracked snapshot from Claude auto-memory. Captured: 2026-09-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_stale_plan_approved_triage_signals.md

---
name: feedback_stale_plan_approved_triage_signals
description: "Triaging a stale plan-approved backlog: reopen-history separates deliberate from forgotten; an issue-number citation in code is BIDIRECTIONAL and must be read, not counted"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-10T22:23:23.797Z
---

**`status:plan-approved` records an AUTHORIZATION, not a claim about the tree.**
Nothing about the label decays when the work quietly lands via another PR, so a
decision made in April reads identically to one made yesterday. 2026-08-10,
digitalmodel: 18 of ~20 pre-June `plan-approved` issues were **already
complete**. Dispatching lanes against them would not merely waste tokens — an
agent told to "add a pytest suite for jumper_lift.py (81 tests)" that finds 81
passing tests will most likely write a duplicate suite or rewrite working tests
to match a three-month-old plan.

**How to triage, cheapest first:**

1. **Reopen history separates deliberate from forgotten.** One call:
   `gh api "repos/<owner>/<repo>/issues/<N>/timeline" --paginate --jq '[.[]|select(.event=="reopened")]|length'`
   A **reopened** issue is open *on purpose* — an audit or re-verification sweep
   — and must never be closed on completion evidence. A **never-closed** one
   merely hasn't been examined. In digitalmodel 6 of 66 were reopened
   (2026-07-18 model-generation sweep).

2. **⚠ An issue-number citation in code is BIDIRECTIONAL.** I gave subagents
   "a fix commenting its own issue number is near-conclusive completion
   evidence." **It inverts.** Verified at
   `src/digitalmodel/subsea/capping_stack/__init__.py:15`:
   `Deferred follow-on (see issue #490): transient flowing-well solver … and
   #484 tree-module integration.` — two issues cited to mark work NOT done.
   `grep -l` throws away the sentence, which is where the direction lives.
   **Read the citing line**: "fixed in", "guard added per #N" → done;
   "Deferred (see #N)", "TODO #N", "pending #N" → the opposite.

3. **Sibling cohorts settle in one shot.** Issues created the same day by the
   same program usually share a fate. A cluster of 10 `fix(marine_ops):` issues
   from 2026-05-03 was closed by ONE targeted run (117 passed, 0 failed) after
   two siblings were found complete.

4. **Adjacent packages mimic the deliverable.** `src/digitalmodel/tug/` looks
   exactly like the towing module issue #487 asks for; `towline.py:3` reads
   `"""Towline load and line-safety analysis (issue #1197)."""` — different
   program. Read the module docstring's own attribution before crediting a path
   match.

**Completion rate does NOT generalise across cohorts.** Test-fix batches were
18/20 complete; the API-17x "implement module X" batch was **0/18** — every one
shipped a deliberately bounded core with remaining acceptance criteria listed as
*Deferred* in its own `__init__.py`. Real, tested, and short of the checklist.
Those want their ACs trimmed to what shipped plus follow-on issues — not closing,
not implementing.

**⚠ `gh issue list` defaults to `--limit 30`.** I reported the backlog as "31"
then "30"; it is **93**. A capped query returning exactly the cap is
indistinguishable from a complete answer. The tell was available: the count
barely moved after closing ten issues. Always pass `--limit 100` and sanity-check
that the total responds to your own changes.

See [[feedback_discovery_first_on_stale_plan_approved]] for the parent rule and
[[feedback_verify_subagent_line_citations_not_just_claims]] for why the citing
line must be opened rather than counted.
