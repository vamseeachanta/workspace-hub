# Domain-decision blocked plan review

Use when adversarial plan review returns MAJOR because correctness-critical domain choices are still unresolved.

## Pattern

1. Treat the plan as not approval-ready even if a plan file and review artifacts exist.
2. Patch the plan/header and `docs/plans/README.md` to a conservative state such as `blocked-draft`, `needs-decision`, or equivalent local wording used by the repo.
3. Keep the GitHub issue out of `status:plan-review` unless the repo policy explicitly uses that label for blocked review items; do not apply `status:plan-approved`.
4. Post a short checkpoint comment listing the exact decisions the user must make. Avoid burying decisions in narrative.
5. After the user answers, revise the plan, rerun adversarial review, then implement within the task request or standing authority only if reviewers no longer return blocking MAJOR findings. An explicit planning-only request remains planning-only.

## Good checkpoint shape

- Current state: planning only; no implementation started.
- Evidence: plan path, review artifact paths, commit SHA if relevant.
- Blocker: one sentence naming the decision class.
- Decisions needed: numbered list of domain choices.
- Next action: user replies with decisions; agent patches plan and reruns review.

## Example decision classes

- Engineering coefficient source/table selection.
- Formula/model basis for simplified or explanatory calculations.
- Sign convention, coordinate frame, lever arm, and velocity basis.
- Plot range/step and whether charts are explanatory only.
- Warning/caption policy when values are not design-authoritative.

## Surfacing unresolved domain assumptions

If the user asks to continue toward plan review but does not supply every domain decision, do not invent hidden decisions. You may make the unresolved choices reviewable only when all of the following are true:

1. Each unresolved domain choice is promoted into a clearly named **domain-decision assumption** in the plan.
2. The plan identifies which assumptions need an owner decision. A task request does not answer an unresolved material domain choice; stop affected implementation until that choice is resolved.
3. Implementation remains fail-closed: if required sources, citations, coefficient tables, or model bases cannot be resolved during implementation, work stops and returns to the issue thread rather than substituting invented values.
4. Tests/oracles are framed around citation presence, documented assumptions, and source-backed calculations rather than brittle text-string checks.
5. A focused re-review is run after the patch and returns no blocking MAJOR findings before applying `status:plan-review`.

The decision remains an implementation blocker until resolved. Once resolved and reviewed, continue under the task request or standing authority without a separate user plan-approval checkpoint.

## Publishing after blocker resolution

When required domain decisions are resolved and a re-review wave clears blocking findings:

1. Update the plan header/status and `docs/plans/README.md` row to `plan-review`.
2. Commit only the plan/review artifacts for that issue; leave unrelated plan waves, session logs, and skill edits unstaged.
3. Verify `origin/main` points at the commit before changing GitHub labels.
4. Add `status:plan-review` and post an issue comment that includes:
   - plan path
   - re-review artifact paths and verdicts
   - commit SHA and remote verification
   - explicit boundary: the task request or standing authority defines implementation scope; preserve any planning-only limitation
   - explicit domain-decision assumption / fail-closed statement

## Pitfall

Do not let the existence of review artifacts mechanically trigger `status:plan-review`. Fresh blocking MAJOR findings keep affected implementation blocked. Naming an unresolved domain assumption makes the decision reviewable; it does not resolve it. Continue only within task/standing authority, and seek explicit authorization for consequential actions outside that scope.
