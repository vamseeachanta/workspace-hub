# OrcaWave/OrcaFlex Approved Next-Wave Exit Handoff

Date: 2026-04-24T09:01:33Z
Operator: Hermes
Stream: OrcaWave/OrcaFlex semantic-proof next wave after digitalmodel PR #528

## Executive state

The next logical OrcaWave/OrcaFlex semantic-proof wave is now approval-ready for execution under two approved plans:

1. #2475 — licensed OrcaWave/OrcaFlex native load-run proof protocol
   - Issue: https://github.com/vamseeachanta/workspace-hub/issues/2475
   - Plan: `docs/plans/2026-04-23-issue-2475-licensed-load-run-proof-protocol.md`
   - Approval marker: `.planning/plan-approved/2475.md`
   - Label state: `status:plan-approved`

2. #2476 — llm-wiki canonical semantic-equivalence contract and fixture cookbook
   - Issue: https://github.com/vamseeachanta/workspace-hub/issues/2476
   - Plan: `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md`
   - Approval marker: `.planning/plan-approved/2476.md`
   - Label state: `status:plan-approved`

Approval commit:
- `5339798ef docs(plan): approve OrcaWave OrcaFlex next-wave plans`
- `HEAD` and `origin/main` both verified at `5339798ef`.

## What was completed in this session

1. Confirmed first wave was merged/closed before continuing:
   - digitalmodel PR #528 is merged.
   - #2455/#2456/#2457 are closed.
   - stale `status:plan-approved` labels were removed from those closed issues in the previous step.

2. Created next-wave planning issues:
   - #2472 CALM/SPM buoy OrcaFlex semantic proof
   - #2473 OrcaWave-to-OrcaFlex hydrodynamic handoff semantic proof
   - #2474 OrcaFlex native reverse-parser equivalence proof
   - #2475 licensed native load-run proof protocol
   - #2476 llm-wiki semantic-equivalence contract/cookbook

3. Drafted canonical plans for #2475 and #2476.

4. Ran adversarial review fanout for #2475 and #2476.
   - The plan-local findings were incorporated into v3 of each plan.
   - Codex/Gemini review-runner failures were classified separately rather than silently treated as plan failure.

5. Created #2477 for the review-runner bug:
   - Issue: https://github.com/vamseeachanta/workspace-hub/issues/2477
   - Title: `fix(review-runner): update Codex exec invocation and harden plan-review path packaging`
   - State: open
   - Labels: `bug`, `priority:high`, `cat:harness`

6. User explicitly waived the broken Codex/Gemini review-runner issue for the #2475/#2476 pair and approved based on remaining review evidence.

7. Recorded approval in all required surfaces:
   - GitHub labels: `status:plan-approved` on #2475 and #2476
   - GitHub comments on #2475 and #2476 documenting the waiver
   - local approval markers under `.planning/plan-approved/`
   - plan headers updated to plan-approved
   - `docs/plans/README.md` rows updated to plan-approved
   - commit pushed to origin/main

## Important waiver boundary

The waiver is narrow:

- Applies only to #2475 and #2476.
- Does not close #2477.
- Does not generally waive Codex/Gemini review-runner failures for future issues.
- Does not authorize bypassing implementation-stage adversarial review after #2475/#2476 work is done.

Issue #2477 should remain active because the plan-review fanout currently has at least two known problems:

1. Codex invocation bug:
   - current fanout attempted `codex exec --no-interactive`
   - installed Codex rejects that flag
   - result: `UNAVAILABLE` review artifacts

2. Gemini path-packaging fragility:
   - Gemini reviews run from `/tmp` and can produce false file-existence MAJORs against repo-relative paths
   - future plan-review packaging should provide reliable inline evidence or a verified accessible repo root

## Current repo state

Verified:

```text
HEAD:        5339798ef
origin/main: 5339798ef
latest commit: docs(plan): approve OrcaWave OrcaFlex next-wave plans
```

The approval artifacts for #2475/#2476 are committed and pushed.

There are many unrelated dirty files in workspace-hub from other concurrent/session automation, mostly under:

- `.claude/`
- `config/agents/`
- `config/ai-tools/`
- `docs/reports/provider-*`
- `logs/orchestrator/`
- `knowledge/wikis/cross-links.md`

These were not part of the #2475/#2476 approval action and should not be swept into this stream accidentally.

## Next recommended execution order

### Step 1 — Execute #2476 first

Reason: #2476 creates the semantic-equivalence contract and fixture cookbook that should guide all following fixture/proof work.

Approved deliverables:

- `knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md`
- `knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md`
- update `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md`
- update `knowledge/wikis/engineering/wiki/index.md`
- update `knowledge/wikis/engineering/wiki/log.md`

Key constraints:

- Docs/wiki-only issue.
- Do not touch `digitalmodel/src/**` or `digitalmodel/tests/**`.
- Must preserve distinction: deterministic semantic proof is not licensed solver load/run proof.

### Step 2 — Execute #2475 second

Reason: #2475 defines licensed-machine proof protocol after the semantic contract is available.

Approved deliverables:

- `docs/solver/orcawave-orcaflex-native-load-run-proof-protocol.md`
- `docs/plans/licensed-win-1-semantic-proof-load-run-prompt.md`
- `docs/solver/templates/semantic-proof-evidence-manifest.yaml`
- update `docs/plans/licensed-win-1-execution-guide.md`

Key constraints:

- Protocol/prompt/docs issue, not solver code implementation.
- No `scripts/solver/process-queue.py` or `queue/job-schema.yaml` changes unless a separate approved follow-up expands scope.
- The licensed-machine prompt manually authors the richer evidence manifest; queue `result.yaml` remains supporting evidence only.
- No actual licensed-machine execution should happen until the protocol/prompt artifacts are implemented and reviewed.

### Step 3 — Keep #2477 as follow-up hardening

#2477 is not a blocker for #2475/#2476 because the user waived the broken runner for this pair, but it is still important before future plan-review waves.

Recommended #2477 fix scope:

- remove/update unsupported Codex `--no-interactive` invocation
- add a regression test/dry-run proving Codex prompt dispatch no longer passes unsupported flags
- harden Gemini packaging so repo-relative evidence is visible or fully inlined
- preserve `UNAVAILABLE` artifacts for genuine provider failures

## Do not do on restart

- Do not re-ask for approval on #2475/#2476; they are approved.
- Do not treat the review-runner waiver as global.
- Do not execute #2472/#2473/#2474 yet; they are open follow-up issues but do not have approved plans from this session.
- Do not close #2477.
- Do not sweep unrelated dirty `.claude/`, `config/`, `logs/`, or provider report files into this stream.

## Fast verification commands

```bash
cd /mnt/local-analysis/workspace-hub

git rev-parse --short HEAD
git rev-parse --short origin/main

gh issue view 2475 --json number,state,labels,url,title
gh issue view 2476 --json number,state,labels,url,title
gh issue view 2477 --json number,state,labels,url,title

test -f .planning/plan-approved/2475.md
test -f .planning/plan-approved/2476.md

git show --stat --oneline 5339798ef
```

## Suggested restart prompt

Continue the OrcaWave/OrcaFlex semantic-proof stream. Start with approved issue #2476, using plan `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` and approval marker `.planning/plan-approved/2476.md`. Keep scope docs/wiki-only. Do not touch digitalmodel source/tests. After #2476 is implemented and reviewed, execute #2475 using `docs/plans/2026-04-23-issue-2475-licensed-load-run-proof-protocol.md`. #2477 remains open as review-runner hardening and the waiver for #2475/#2476 is narrow only.
