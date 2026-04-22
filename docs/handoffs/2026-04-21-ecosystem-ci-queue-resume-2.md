# Resume handoff — Ecosystem CI queue (session 6, #2442 near-approval)

## Quick prompt for next session

```
Resume ecosystem CI queue from
docs/handoffs/2026-04-21-ecosystem-ci-queue-resume-2.md

Issue #2442 plan is at v5 with 5 cross-review waves complete.
Wave 5: Claude APPROVE, Codex MAJOR, Gemini MAJOR.
Two mechanical fixes remain before all-clear:

1. REOPEN #2442 — it was closed by a parallel session by mistake.
   CI is still red (10/10 failure on assethold main).
   Run: gh issue reopen 2442

2. Fix acceptance criteria text contradiction — still says
   "actions/checkout@v4 sibling checkout" but pseudocode + Files to
   Change correctly say "git clone --depth 1". Edit the acceptance
   criteria line in docs/plans/2026-04-21-issue-2442-assethold-python-tests.md
   to replace "Sibling-repo checkout step (actions/checkout@v4 for
   vamseeachanta/assetutilities into ../assetutilities)" with
   "Sibling-repo clone step (git clone --depth 1
   https://github.com/vamseeachanta/assetutilities.git ../assetutilities)"

3. Commit as v6, run Wave 6 cross-review:
   bash scripts/review/cross-review.sh \
     docs/plans/2026-04-21-issue-2442-assethold-python-tests.md all --type plan

4. If no MAJOR: post summary comment on #2442 with plan SHA + verdicts,
   confirm status:plan-review, message user for approval.

5. WAIT for user to set status:plan-approved. Do NOT self-approve.

6. After approval: execute P1 (7 YAML/action fixes) + P2 (3 install +
   3 clone steps) as separate commits direct to assethold main.

7. After #2442 execution verified, proceed to:
   - #2433 (worldenergydata) — already status:plan-approved, execute
   - #2437 (workspace-hub prune) — already status:plan-approved, execute
   - #2441 (digitalmodel pylife) — status:plan-review, check verdicts
   - #2443 (achantas-data) — status:plan-review, check verdicts
   - #2444 (aceengineer-admin) — status:plan-review, check verdicts

Do NOT self-approve any plan.
Do NOT clone assethold from stale samdansk2 fork.
Do NOT restore scripts/agents/ or scripts/work-queue/ trees.
```

## Review wave history for #2442

| Wave | Claude | Codex | Gemini | Key fix |
|------|--------|-------|--------|---------|
| 1 | MAJOR | MAJOR | MAJOR | assetutilities sibling dep, codecov, YAML proof |
| 2 | MAJOR | MAJOR | APPROVE | stale uv-sync wording, preconditions verified |
| 3 | MAJOR | MAJOR | APPROVE | execution-strategy contradiction |
| 4 | MAJOR | MAJOR | APPROVE | checkout path blocker (actions/checkout rejects ../) |
| 5 | APPROVE | MAJOR | MAJOR | #2442 closed by mistake + acceptance criteria text |

## Commits this session

| SHA | Description |
|-----|-------------|
| fe5f216e5 | plan v2 — uv sync to system install, phase gates |
| 0c39f0605 | plan v3 — preconditions, ref:main risk, Unicode |
| 333f2b4c6 | plan v4 — execution-strategy contradiction |
| 069afceaa | plan v5 — checkout path blocker, P3 follow-on |
| 35dc74124 | resume handoff v1 |
| 61e2b3073 | Wave 2-4 review artifacts |
