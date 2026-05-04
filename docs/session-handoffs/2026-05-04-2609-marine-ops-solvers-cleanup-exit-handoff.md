# Session Handoff: 2026-05-04 — #2609 marine_ops + solvers cleanup

**Session ID:** f0b82690-86aa-4409-8f19-0896e0cba0cb
**Exit reason:** Documenting and exiting per user direction. Bash environment became unresponsive at exit time (likely after `kill -9 321981` took out a parent shell process); state captured from conversation history rather than live snapshot.
**Date:** 2026-05-04
**Parent umbrella:** [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609)
**Closed parent issue:** [vamseeachanta/workspace-hub#2580](https://github.com/vamseeachanta/workspace-hub/issues/2580)

## Headline

Marine_ops + solvers/orcaflex sub-issue triage executed across two parallel waves; 16 sub-issues filed; 1 ecosystem-wide artifact patch landed; 1 contamination incident detected and recovered. F103 wiki landing in-flight at exit time — push was running through the workspace-hub tier-1 pre-push test gate (`run-all-tests.sh --repo assetutilities`), which typically takes 5–10 min.

## What landed (durable)

### Plans committed to workspace-hub
- `docs/plans/2026-05-02-issue-2580-digitalmodel-collect-ignore-test-fixes.md` (327 lines, r2) — closed parent issue's plan
- `docs/plans/2026-05-02-issue-2580-quality-gates-followups.md` — discovery doc for the 244+ failure umbrella
- `docs/plans/2026-05-02-label-taxonomy-gap.md` — workspace-hub label additions
- `docs/plans/2026-05-03-2609-marine-ops-triage.md` (r2, 17 KB / 155 lines, committed `714640353`) — 8-cluster bucket plan
- `docs/plans/2026-05-03-2609-solvers-orcaflex-triage.md` (r1, 27 KB / 310 lines, committed `714640353`) — 9-cluster bucket plan
- `docs/plans/2026-05-03-digitalmodel-546-qg-cli-full-log-artifact.md` (327 lines, committed `ced1542fc`) — QG CLI patch plan

### digitalmodel PRs merged
- [vamseeachanta/digitalmodel#544](https://github.com/vamseeachanta/digitalmodel/pull/544) — yml_utilities print → logger.info() + caplog tests
- [vamseeachanta/digitalmodel#545](https://github.com/vamseeachanta/digitalmodel/pull/545) — FIXTURE_PROVENANCE.md
- [vamseeachanta/digitalmodel#547](https://github.com/vamseeachanta/digitalmodel/pull/547) — Quality Gates CLI uploads full pytest log as artifact (load-bearing — unblocks every future triage)
- [vamseeachanta/digitalmodel#572](https://github.com/vamseeachanta/digitalmodel/pull/572) — bare-command CLI invocations replaced with `sys.executable -m` + `list_cli_commands` import path corrected (closed [vamseeachanta/digitalmodel#570](https://github.com/vamseeachanta/digitalmodel/issues/570) + [vamseeachanta/digitalmodel#571](https://github.com/vamseeachanta/digitalmodel/issues/571))

### digitalmodel sub-issues filed (one bucket each)
- R2 catenary: [vamseeachanta/digitalmodel#554](https://github.com/vamseeachanta/digitalmodel/issues/554) — ~21 tests
- R4 chain DB: [vamseeachanta/digitalmodel#555](https://github.com/vamseeachanta/digitalmodel/issues/555) — ~8 tests (including non-legacy free-rider)
- R6 individuals: [vamseeachanta/digitalmodel#556](https://github.com/vamseeachanta/digitalmodel/issues/556)–[vamseeachanta/digitalmodel#565](https://github.com/vamseeachanta/digitalmodel/issues/565) — 10 tests filed individually per "keep gap" direction
- R1+R5+R7+R8 batched: [vamseeachanta/digitalmodel#566](https://github.com/vamseeachanta/digitalmodel/issues/566) — 11 tests
- S1 PATH cluster: [vamseeachanta/digitalmodel#570](https://github.com/vamseeachanta/digitalmodel/issues/570) — CLOSED via #572 merge
- mis-bucketed test: [vamseeachanta/digitalmodel#571](https://github.com/vamseeachanta/digitalmodel/issues/571) — CLOSED via #572 merge
- F103 wiki tracking: [vamseeachanta/workspace-hub#2627](https://github.com/vamseeachanta/workspace-hub/issues/2627) — open, blocking R3

### workspace-hub label taxonomy
- `tracker` (#FBCA04)
- `domain:digitalmodel` (#c5def5)
- `status:needs-plan` (#FBCA04)
Applied to [vamseeachanta/workspace-hub#2585](https://github.com/vamseeachanta/workspace-hub/issues/2585) and [vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609).

### Memory entries
- `feedback_qg_maxfail_undercounts.md` — Quality Gates CI's "20 failed" is the `--maxfail=20` ceiling, true count was 244+; never trust without local repro
- `feedback_subagent_write_phantom.md` — subagent Write success doesn't guarantee file landing; main session must independently `ls`. **NOT git-tracked under workspace-hub yet** — local-only on this machine. Cross-machine promotion needed.

## What's in-flight at exit

### F103 wiki PR (Lane 2 clean re-do) — PUSH FAILED, NEEDS MANUAL RECOVERY
- **Local commit:** `aaaefd9e4` on branch `wiki/2627-dnv-rp-f103-clean` (clean: 1 file, 85 insertions, plan-gate PASS)
- **File on disk:** content recovered to `/tmp/dnv-rp-f103-recovered.md` (8048 bytes, 85 lines) — defensive backup; primary copy at `knowledge/wikis/engineering-standards/wiki/standards/dnv-rp-f103.md`
- **Push status:** **FAILED** — both push attempts (background tasks `bjc8pxh4q` and `b2oireh4f`) ended with exit code 1. Tier-1 pre-push hook (`scripts/testing/run-all-tests.sh --repo assetutilities`) likely failed during the test gate. Branch was NOT pushed to origin.
- **PR creation:** **NOT FIRED** — push didn't land, chained `gh pr create` never ran.
- **Recovery in next session:**
  1. `git -C /mnt/local-analysis/workspace-hub log --oneline wiki/2627-dnv-rp-f103-clean -3` to confirm local commit `aaaefd9e4` survives
  2. Inspect the failed push output: `cat /tmp/claude-1000/-mnt-local-analysis-workspace-hub/f0b82690-86aa-4409-8f19-0896e0cba0cb/tasks/b2oireh4f.output` to see whether tier-1 tests failed or it was a hook-config issue
  3. If tier-1 tests are genuinely red on assetutilities (unrelated to this F103 wiki PR), the right path is to investigate that separately, then retry push. Per `feedback_pre_push_hook_no_verify_for_preservation.md`, NEVER `--no-verify` to bypass the gate
  4. If hook had a transient issue, simply retry: `git -C /mnt/local-analysis/workspace-hub push origin wiki/2627-dnv-rp-f103-clean -u`
  5. After push succeeds, open the PR with the body draft preserved in this conversation's commit-creation step (or reconstruct from the closed [vamseeachanta/workspace-hub#2633](https://github.com/vamseeachanta/workspace-hub/pull/2633) body for reference)
- **Background task IDs:** `bjc8pxh4q` FAILED, `b2oireh4f` FAILED, monitor `b0jb8bsc5` still armed (will exit when push process gone). May want to TaskStop the monitor or just let it time out.

### Contaminated PR
- [vamseeachanta/workspace-hub#2633](https://github.com/vamseeachanta/workspace-hub/pull/2633) — **CLOSED 2026-05-04** with audit comment. Branch `wiki/2627-dnv-rp-f103` retained on origin for forensics. Contained:
  - Commit `bfc7ee667` (F103 wiki + 4-5 unrelated state files mixed in)
  - Commit `d2b2ce1ed` (parallel session's `docs(plans): #2628 domain-divided CI plan` that landed on the wrong branch)
  - Plus working-tree dirty files in PR diff

## Coverage tally

[vamseeachanta/workspace-hub#2609](https://github.com/vamseeachanta/workspace-hub/issues/2609) (244+ failures umbrella):

| Bucket | Total | Tracked | Notes |
|---|---|---|---|
| marine_ops | 77 | 50 (R2/R4/R6/R1+R5+R7+R8) + 16 BLOCKED on R3 | 11 unallocated residue |
| solvers/orcaflex | 42 | 22 cleared by #572 + 1 by #571; remaining ~19 in S2/S3/S4/S5/E1/E2 not yet filed | |
| hydrodynamics | 28 (25 FAILED + 3 ERROR) | 0 | no triage yet |
| infrastructure | 56 (20 FAILED + 36 ERROR) | 0 | no triage yet (likely Redis/SQL fixture deps) |
| field_development | 16 | 0 | no triage yet |
| reservoir/contracts/other | ~9 | partial (1 in R8) | |

**Net cleared by merged PRs:** 23 tests on digitalmodel main (#572 = 22 PATH + 1 import) + 10 tests via #544 yml_utilities = ~33 of 244+. Plus #547 (full-log artifact) is a force-multiplier on every future triage.

## What blocks what

- **R3 (16 tests):** BLOCKED on F103 wiki landing on workspace-hub main. Once `wiki/2627-dnv-rp-f103-clean` PR merges, file the R3 sub-issue against digitalmodel and proceed.
- **Buckets with no triage yet** (hydrodynamics 28, infrastructure 56, field_development 16): not blocked by anything; awaiting triage agent dispatch in next session.
- **244+ failure umbrella close-out:** distant. Each bucket needs sub-issue creation + PRs. Use the merged #547 full-log artifact as the canonical evidence source; per memory `feedback_qg_maxfail_undercounts.md`, do NOT re-run `--maxfail=20`-truncated CI artifacts as triage source.

## Session-specific lessons (worth re-reading next session)

1. **Subagent Write phantom failures occurred TWICE this session.** Pattern: agent reports `Write` success, file not on disk. Recovery cost ~2 turns each. Fix codified in `feedback_subagent_write_phantom.md` — every plan-creating subagent prompt MUST require ls-after-Write evidence in its report; main session MUST independently `ls` before referencing in downstream turns or commits.

2. **Branch contamination from parallel sessions.** Lane 2's `wiki/2627-dnv-rp-f103` branch picked up:
   - The agent's own dirty working tree (`.claude/state/`, `config/ai-tools/*` — no disciplined `git add <specific-path>`)
   - A parallel session's `docs(plans): #2628` commit that landed on the wrong branch
   - Recovery: close PR, recover content via `git show <SHA>:<path>`, fresh branch off main, **specific-path staging only**, new clean PR.
   - Worth memorializing: `feedback_agent_dirty_tree_contamination.md` proposed but not written. Pattern: never `git add -A` or `git commit -a` in agent prompts; always `git add <explicit-path>`.

3. **PR CI failure interpretation pattern (now demonstrated 4×):** `Run Quality Gates: FAILURE` on a digitalmodel PR is almost always pre-existing main breakage (244+ broken) NOT introduced by the PR. Verify via the new full-log artifact (#547 deliverable): compare PR's failed nodeids against main's known set + check pass count delta. If delta is +0 and nodeids match main, merge is safe per `feedback_commit_attestation_narrow_scope.md`. PRs #544, #545, #547, #572 all merged green-equivalent under this rule.

4. **Adversarial-stance investigation pays off both ways.** Marine_ops triage refuted its 1-3-cluster prior (8 distinct clusters); solvers/orcaflex triage CONFIRMED its 26-in-one-file prior (live-tested PATH-propagation). The correct rule: force defect-hunting per `feedback_adversarial_review_stance.md`; the stance is bias toward live evidence, not toward "always heterogeneous".

## Recommended fresh-session prompt

```
Resume the #2609 marine_ops + solvers cleanup. Read the handoff at
docs/session-handoffs/2026-05-04-2609-marine-ops-solvers-cleanup-exit-handoff.md
fully before any action.

Concrete continuation tasks (in suggested order):
1. Verify whether the F103 wiki PR landed (look for an open PR on
   workspace-hub with title containing "F103" or branch
   "wiki/2627-dnv-rp-f103-clean"). If it landed and merged, file
   the R3 sub-issue against digitalmodel.
2. If F103 push didn't complete, check `git log` and `git ls-remote
   origin "refs/heads/wiki/2627-dnv-rp-f103-clean"` to determine state;
   re-push if needed (the local commit `aaaefd9e4` should still exist).
3. Dispatch triage agents on the 3 untriaged buckets:
   hydrodynamics (28), infrastructure (56), field_development (16).
   Use the post-#547 CI artifact as evidence source; if any failures
   require deeper traceback than the artifact provides, run a local
   repro per memory `feedback_qg_maxfail_undercounts.md`.
4. Promote `feedback_subagent_write_phantom.md` from local-only to
   workspace-hub `.claude/memory/topics/` so other machines inherit
   the rule.

Constraints (memory rules):
- Issues belong to the repo where the code lands (digitalmodel for
  source/test fixes; workspace-hub for wiki/plans/cross-repo).
- Never `--no-verify` on commit; push --no-verify only for
  preservation per memory `feedback_pre_push_hook_no_verify_for_preservation.md`.
- Every subagent that Writes a file MUST include ls-after-Write
  evidence per `feedback_subagent_write_phantom.md`.
- Never `git add -A` or `git commit -a` in agent prompts; specific
  paths only per the contamination lesson above.
- Per `.claude/rules/calc-citation-contract.md`, calc modules using
  standards-derived constants need a wiki page citation target.
```

## Background task IDs (for forensics)

- `bjc8pxh4q` — original commit + push + PR chain. Marked failed (push hung).
- `b2oireh4f` — push retry. State unknown at exit.
- `b0jb8bsc5` — Monitor watching for branch on origin.

Inspect via `cat /tmp/claude-1000/-mnt-local-analysis-workspace-hub/f0b82690-86aa-4409-8f19-0896e0cba0cb/tasks/<task-id>.output`.
