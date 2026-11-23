# Review Artifact Readiness Before Publishing Plan-Review

Use this when a planning wave has multiple review artifact generations, canonical copies, timestamped copies, or provider-unavailable stubs.

## Problem pattern

A plan may look close to approval-ready because the draft has been patched after MAJOR findings, but the durable evidence still says otherwise:
- newest timestamped review artifacts still contain `MAJOR` verdicts;
- non-timestamped/canonical review files are empty or stale;
- Gemini/Codex/Claude artifacts are unavailable stubs rather than approval evidence;
- the plan header still says draft / pending fresh re-review;
- the local branch is behind remote or the worktree is dirty, so plan/review evidence is not reproducible from pushed state.

Do not publish an approval-ready plan comment in this state.

## Required readiness check

Before posting final plan-review comments or moving an issue to `status:plan-review`:

1. List every review artifact for the issue, including timestamped and canonical filenames.
2. Identify the highest-numbered or newest non-empty artifact per provider.
3. Read verdicts from the selected artifacts, not from filenames or stale summaries.
4. Treat provider `UNAVAILABLE` artifacts as evidence of attempted review only, not approval evidence.
5. Reject empty artifacts as non-evidence and do not cite them.
6. Check the plan header/status and adversarial-review section for stale text such as `draft`, `pending re-review`, old round numbers, or unresolved MAJOR language.
7. Confirm local git state is suitable for evidence claims: branch not unexpectedly behind, relevant plan/review files tracked, and no unrelated dirty state being swept into the closeout.

## Decision rule

- If any selected provider artifact still reports `MAJOR`, keep review in progress and do not publish approval-ready comments.
- If all available provider artifacts are clean/minor and unavailable providers are documented with concise stubs, patch the plan to state the current review synthesis and proceed to final plan comment.
- If canonical artifacts are empty but timestamped artifacts are valid, cite timestamped artifacts explicitly and either regenerate or remove the empty canonical artifacts before closeout.

## Final response shape when blocked

Report:
1. current state — not ready / ready;
2. evidence — exact artifact paths and verdicts;
3. gap/blocker — unresolved MAJOR, empty artifact, stale draft header, dirty/behind git state;
4. recommended next action — re-review, patch plan, or publish.
