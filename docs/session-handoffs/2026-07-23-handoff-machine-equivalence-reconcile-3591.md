# Session handoff — machine-equivalence reconcile + readiness green on dev-secondary (2026-07-22 → 23)

Session ran on **dev-secondary (ace-linux-2)**. All work committed and pushed to `vamseeachanta/workspace-hub` main; no PRs left open by this session. Issue [#3591](https://github.com/vamseeachanta/workspace-hub/issues/3591) opened, fully landed, and closed.

## What landed (chronological)

| Commit | What |
|---|---|
| `b8fc39ba0` | dev-secondary local state + auto-memory churn committed (cleared measured-path dirty → equality collector `dirty:false`) |
| `ed4962bb5` | model-registry 2.3.0: `openai_primary` → `gpt-5.6-sol` tracking live `~/.codex/config.toml` (R-MODEL-DRIFT, #3038 contract) |
| `36c42db2d` | github-repo-management: authored When-to-Use; scanner-allow sentinels (owner-approved #3591); `ssh_dir_access` example REMEDIATED (dedicated deploy key) not suppressed; R-SKILLS greened |
| `762fa1d8a` | role-aware `providers_baseline` — harness dim moved to cold conformance; thin hosts (gpu-claw, ace-win-1) declare gemini/hermes absent |
| — | scheduler analog was built here but DROPPED mid-rebase: dev-primary landed the superset as [#3592](https://github.com/vamseeachanta/workspace-hub/issues/3592) `612cf423f` (scheduler+memory cold dims, schema-v5 Windows placeholder gate, schtasks probe). Upstream adopted. |
| `e318dd5ac` | #3591 items 3+4: fence-aware loose-heading scan in check-skill-index-coherence.py; R-SKILLS fleet-cadence clause demoted to advisory (per-box session-signals freshness still fails) |
| `8a0c0969e` | gpu-claw `scheduler_baseline.repo_sync` → `not-required` (owner decision; flip back if repo-sync ever installed there) |

Also: reconcile-ecosystem `--apply` fixed 76 AUTO-SAFE hygiene items across siblings (2026-07-22); au + assethold clones switched from stale June branches to fresh main (that alone fixed R-PRECOMMIT).

## Verified end state

- **Harness readiness dev-secondary: 24/24 pass** (`.claude/state/harness-readiness-ace-linux-2.yaml`).
- **Equality matrix** (https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html):
  - `harness` CONFORMS on all 5 active boxes; `scheduler` CONFORMS on dev-primary/dev-secondary/gpu-claw; Harness-equivalence group rollup on Linux dev boxes = EXPECTED-DIFF (python_cmd only).
  - ace-win-1/2 scheduler+memory cells = MISSING-EVIDENCE **by design** until their weekly ps1 collectors re-run at schema 5 (#3592 migration gate). No action needed; do not "fix".
- Tests: 115 pass in test_build_equality_matrix.py; 25 pass across coherence + R-SKILLS files.

## Watch items / next steps

1. **Peer boxes' R-MODEL-DRIFT**: registry now says `gpt-5.6-sol`. Any box whose `~/.codex/config.toml` still says `gpt-5.5` will flag drift until its codex config updates. Expected to self-heal via codex updates; if a box flags, check its config, not the registry.
2. **ace-win-1/2 schema-5 collections**: MISSING-EVIDENCE scheduler/memory cells clear on their next collector runs. If still MISSING-EVIDENCE after the next weekly Windows run, check the ps1 rollout.
3. **ace-win-1/2 memory BELOW-BASELINE** (observed pre-schema-5): re-check after schema-5 evidence lands; baselines in harness-config.yaml may need an owner look (win-1 declared absent, win-2 present).
4. **gpu-claw**: if repo-sync is ever installed, flip `scheduler_baseline.repo_sync` back to `required` (comment marks the spot).
5. **R-SKILLS advisory**: on quiet fleet weeks the OK line shows "(advisory: no skills committed fleet-wide in 7 days)" — by design, not a defect.

## Dirty-state exceptions on this box (intentional, not for cleanup)

- 4 backed-up local report HTMLs in session scratchpad (`wh-untracked-backup-2026-07-22/`) + retained autostash `pre-sync` entries in wh stash list — recoverable copies from the reconcile's conflict resolution; safe to drop once confident nothing was lost.
- digitalmodel clone: 1 unpushed commit + behind-by-81 + dirty — the LIVE compute clone, deliberately untouched (see memory `digitalmodel-compute-clone-is-live`).
- Stashes in 5 sibling repos + guarded worktrees: surfaced by reconcile as NEEDS-APPROVAL, left for owner judgment.

## Key traps confirmed this session (also in auto-memory `equality-stale-checkout-loop`)

- `refresh-equality-matrix.sh`'s pull hook (kanban-autoload) can take ~40 min on this box.
- If autostash-pop conflicts, the equality collect still runs on the CONFLICTED tree → publishes a `dirty:true` STALE snapshot. Resolve conflicts (take origin's generated files) then re-run `equality-matrix-cron.sh` alone.
- `publish-equality.sh` pushes from a sparse worktree → local main ends up behind its own publish commit; `git checkout HEAD -- <generated>` then `pull --ff-only`.
- Parallel-work: dev-primary implemented the scheduler treatment within hours of this session building the same thing — sweep `git log origin/main` + open issues BEFORE implementing follow-ons.
