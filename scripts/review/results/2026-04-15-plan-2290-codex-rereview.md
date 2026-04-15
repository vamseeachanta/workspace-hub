# Codex second-wave re-review — plan #2290

Reviewer: Codex CLI
Date: 2026-04-15
Issue: #2290
Prompt: `.planning/quick/review-2290-codex-rereview-prompt.md`
Raw log: `.planning/quick/review-2290-codex-rereview.out`
Verdict: APPROVE

1. Verdict: APPROVE

2. Strengths
- The revised plan closes the main first-wave blockers: directory-level inventory before deletion, broader reference-cleanup scope, structural validation, exact finding-key/path-set regression checks, and bounded parent cleanup.
- It now correctly treats 6 of the 7 so-called exact duplicates as compare/merge candidates instead of blind deletes.
- The acceptance criteria and test list are specific enough to catch both content loss and audit-regression false positives.

3. Remaining gaps
- No blocking gaps remain in the plan itself.
- The only soft spot is that implementation judgment will still be required when a diff shows meaningful specialization rather than redundant drift, but the plan now explicitly calls for escalation instead of automatic deletion.

4. Risks
- The main residual risk is bad merge judgment on the 6 non-identical duplicate pairs.
- Hidden references outside the scanned surfaces are still possible, but this is now a bounded implementation risk rather than a planning omission.

5. Missing tests
- No blocking test gap remains.
- Optional extra check: add a fixture asserting preserved auxiliary files retain their relative discoverability from the canonical skill root after moves.

6. Scope creep concerns
- Low.
- The revised plan is now disciplined about limiting work to the 10 target findings and only removing directly emptied parent directories.

7. Weakest assumption and what breaks if false
- Weakest assumption: the surviving canonical copy is the right long-term home for each merged pair.
- If false, the implementation can still pass audit/tests while leaving content in a semantically worse taxonomy location.

8. Most likely implementation failure mode
- A unique auxiliary reference file gets moved or merged incorrectly, leaving the canonical skill structurally present but practically degraded.

9. Most likely test gap
- Structural parsing passes, audit findings clear, but a moved supporting file is no longer where the skill text expects it to be.

10. Future issues suggested
- Separate follow-up for remaining non-target leaf collisions and adjacent-specialization cases.
- Possible future governance issue to add a reusable “supporting-file path integrity” check to the weekly skills audit.

11. Review confidence
- High. The revised plan addresses the prior blocking objections and is approval-ready.

Operational note
- Codex could not write its own artifact because of sandbox `bwrap` failure; this durable artifact was written from Hermes using the captured reviewer output.