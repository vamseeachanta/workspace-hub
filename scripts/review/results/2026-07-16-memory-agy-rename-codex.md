## Verdict
MAJOR

## Findings numbered with cited paths/claims
1. [`.claude/memory/topics/feedback_agy_replaces_gemini_cli.md`] new topic overstates unverified AGY invocation semantics. Current live evidence only establishes `agy` is not found on `ace-win-2`, `scripts/review/submit-to-agy.sh` exists, and legacy `gemini` auth fails. Claims like `agy --print "<prompt>" --print-timeout 240s --dangerously-skip-permissions`, “AGY ignores stdin,” and “wrapper input below its configured byte cap” need a cited local wrapper inspection or prior verified artifact. As written, this converts unstated assumptions into durable memory.

2. [`docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md`] the “Review artifacts” header now lists `scripts/review/results/2026-07-16-plan-3555-r3-agy.md` as “next independent review.” That path is not evidence yet and AGY is explicitly absent on `ace-win-2`. Mixing planned future output into a review-artifacts evidence field is a stale-evidence hazard.

3. [`docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md`] and [`docs/session-handoffs/2026-07-16-goal-statusline-pilot-exit.md`] retain “all six findings are patched / addresses all six findings” while this diff only updates provider naming and blocker text. If the six fixes are not independently present in the same tracked state, this is an unsupported review-clearance claim.

4. [`.claude/memory/KNOWLEDGE.md`] says AGY is “the Gemini-backed delegation/review surface for new work” while also saying `agy` was missing on `ace-win-2`. This is acceptable only if the contract is “preferred surface once installed”; otherwise it can be read as operationally available. The safer memory wording should make availability conditional per machine.

5. [`.claude/memory/topics/feedback_agy_replaces_gemini_cli.md`] cites `docs/plans/2026-06-18-issue-3207-agy-headless-dispatch.md` and `docs/session-handoffs/2026-06-14-agy-gemini-statusline-rollout.md` as evidence, but the supplied diff does not show those files exist or contain the claimed CLI semantics. For durable memory, evidence references must be retrievable and specifically support the operational contract.

## Blockers
- Do not land durable memory claims about AGY CLI flags/stdin behavior until verified from `scripts/review/submit-to-agy.sh` or an existing reviewed artifact.
- Remove or clearly mark nonexistent `r3-agy.md` as a planned target, not a review artifact.
- Reconcile or substantiate the “all six findings patched” claims before presenting this as updated planning evidence.