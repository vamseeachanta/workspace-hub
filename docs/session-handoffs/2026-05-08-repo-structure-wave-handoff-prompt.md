# Repo Structure Refactor Wave — Fresh Session Handoff Prompt

Date captured: 2026-05-08T06:15:57-05:00
Prepared from: `/mnt/local-analysis/workspace-hub`

## Copy/paste prompt for the fresh session

```text
Resume the repo-by-repo folder/file structure normalization wave for the workspace-hub tier-1 ecosystem.

User intent:
- Work through repo by repo using the approved GitHub issues.
- Make the repo-structure experience consistent between repos.
- Revisit/revise previous repo work if a later repo exposes a better shared pattern.
- Record each repo's test-suite baseline and ensure the baseline stays stable.
- Surface decisions/blockers as needed.
- Follow repo ecosystem workflows and hard gates.

Mandatory skills/workflows to load before acting:
- github-issue-lifecycle-operations, especially `references/gh-work-execution.md` and `references/gh-work-execution-checklist.md`
- workspace-hub/repo-structure
- workspace-hub/worktree-branch-sync-hygiene
- software-development/test-driven-development
- _internal/meta/discipline-refactor and/or _internal/meta/repo-cleanup only when structural moves/cleanup are being considered

Hard gates:
- Execute only issues that are live `status:plan-approved`.
- Before implementation in a checkout, ensure `.planning/plan-approved/<issue>.md` exists locally with neutral operator/user approval wording and is included in the implementation transaction.
- Use TDD for checker/script behavior: write a failing test first, observe RED, then implement GREEN.
- Do not do broad source/docs/generated-output moves in Phase 1. The approved plans authorize bounded contract/checker/tests/docs/enforcement wiring only unless later explicit approval expands scope.
- Do not delete or relocate tracked generated-looking artifacts until they are classified as unauthorized generated artifact, durable evidence, or temporary durable exception with metadata/follow-up.
- Closeout is transactional: validate, commit, push, issue comment, label cleanup/closure, branch/worktree disposition, and clean-state proof in the same window. Do not close first and clean later.

Approved issue queue and current state at handoff:
1. assetutilities — `vamseeachanta/assetutilities#78`
   - URL: https://github.com/vamseeachanta/assetutilities/issues/78
   - Labels: `enhancement`, `status:plan-approved`
   - Repo path: `/mnt/local-analysis/workspace-hub/assetutilities`
   - Git state at handoff: `main`, `HEAD=b4c3a47`, `origin/main=b4c3a47`, only untracked `.planning/plan-approved/78.md` created by this session.
   - Execution-start GitHub comment already posted: https://github.com/vamseeachanta/assetutilities/issues/78#issuecomment-4405946727
   - Baseline full-suite attempt: `uv run python -m pytest tests -q` was started and then interrupted by the user pause (`exit_code=130`, output `[Command interrupted]`). Treat baseline as NOT RECORDED yet; rerun from scratch in the fresh session.
   - Recommended next step: continue this repo first. Record test baseline, then TDD the repo-structure checker.

2. workspace-hub — `vamseeachanta/workspace-hub#2656`
   - URL: https://github.com/vamseeachanta/workspace-hub/issues/2656
   - Labels: `enhancement`, `priority:high`, `cat:engineering`, `cat:harness`, `domain:repo-organization`, `status:plan-approved`
   - Repo path: `/mnt/local-analysis/workspace-hub`
   - Git state at handoff: `main`, `HEAD=916743102`, `origin/main=916743102`
   - Dirty state already existed before this handoff and must be classified before any repo-structure execution:
     - modified `.claude/skills/_internal/meta/repo-cleanup/SKILL.md`
     - modified `.claude/skills/coordination/provider-session-learning-transfer/SKILL.md`
     - modified `.claude/state/session-signals/2026-05-08.jsonl`
     - modified `config/workflow-tips/tip-history.yaml`
     - modified `logs/orchestrator/hermes/skill-patches.jsonl`
     - untracked `.claude/skills/_internal/meta/repo-cleanup/references/ci-readiness-closeout-hygiene.md`
     - untracked `logs/quality/memory-health-20260508.md`
   - Do not sweep these into repo-structure commits without classification/authorization.

3. worldenergydata — `vamseeachanta/worldenergydata#394`
   - URL: https://github.com/vamseeachanta/worldenergydata/issues/394
   - Labels: `enhancement`, `priority:high`, `cat:engineering`, `status:plan-approved`
   - Repo path: `/mnt/local-analysis/workspace-hub/worldenergydata`
   - Git state at handoff: `main`, `HEAD=ef38cb69`, `origin/main=ef38cb69`, clean.

4. assethold — `vamseeachanta/assethold#49`
   - URL: https://github.com/vamseeachanta/assethold/issues/49
   - Labels: `enhancement`, `cat:engineering`, `priority:high`, `status:plan-approved`
   - Repo path: `/mnt/local-analysis/workspace-hub/assethold`
   - Git state at handoff: `main`, `HEAD=096071b`, `origin/main=096071b`, clean.

5. aceengineer-website — `vamseeachanta/aceengineer-website#13`
   - URL: https://github.com/vamseeachanta/aceengineer-website/issues/13
   - Labels: `enhancement`, `priority:high`, `status:plan-approved`
   - Repo path: `/mnt/local-analysis/workspace-hub/aceengineer-website`
   - Git state at handoff: `main`, `HEAD=df75720`, `origin/main=df75720`, clean.

6. aceengineer-strategy — `vamseeachanta/aceengineer-strategy#19`
   - URL: https://github.com/vamseeachanta/aceengineer-strategy/issues/19
   - Labels: `strategy`, `status:plan-approved`
   - Repo path: `/mnt/local-analysis/workspace-hub/aceengineer-strategy`
   - Git state at handoff: `main`, `HEAD=9057555`, `origin/main=9057555`, clean.

Suggested execution order:
1. Continue `assetutilities#78` because execution has already started and only the approval marker is uncommitted.
2. Move to clean repos in this order unless user changes priority: `worldenergydata#394`, `assethold#49`, `aceengineer-website#13`, `aceengineer-strategy#19`.
3. Handle `workspace-hub#2656` after classifying/isolating the existing root dirt, or use a clean worktree if immediate execution is necessary.

For each repo:
1. `cd <repo>` and re-verify `gh issue view <issue> --json state,labels,title,url` includes `status:plan-approved`.
2. Read local `AGENTS.md`/`CLAUDE.md` and the approved plan under `docs/plans/`.
3. Ensure/create `.planning/plan-approved/<issue>.md` with neutral user-approved wording.
4. Record baseline:
   - `git status --short --branch`
   - `git rev-parse --short HEAD origin/main`
   - primary test command from `AGENTS.md` or repo config.
   - If full suite is too slow, run a bounded baseline first but clearly label it as targeted/bounded, not full-suite.
5. Post/maintain GitHub progress comments at major steps.
6. TDD Phase 1 artifacts:
   - human-readable `docs/standards/repo-structure.md` or repo-equivalent standard
   - machine-readable `config/repo_structure.yml`
   - checker `scripts/maintenance/verify_repo_structure.py` or repo-equivalent
   - tests under `tests/repo_structure/`
   - pre-commit/CI wiring if existing surfaces support it
7. Keep checker behavior consistent across repos. If a better shared pattern emerges, revisit prior repos deliberately and document the reason.
8. Acceptance proof before each closeout:
   - RED/GREEN evidence for checker tests
   - targeted repo-structure checker pass/fail behavior
   - baseline test-suite unchanged or explicitly documented environment/baseline blocker
   - deterministic classification of generated-output/root exceptions
   - no unapproved file moves/deletions
9. Commit/push per repo and close only with full evidence.

Important current-session facts not to lose:
- The only action inside `assetutilities` before handoff was creating `.planning/plan-approved/78.md`, posting the execution-start comment, checking PyYAML availability (`yaml True`), and starting then interrupting the full pytest baseline.
- No repo-structure implementation code/tests/docs have been written yet.
- No commits or pushes were made for this wave in the current session.
- Parallel work is ongoing elsewhere, so re-fetch/re-check state before making assumptions.
```

## Local handoff file status

This handoff was prepared as a docs/session handoff artifact. Fresh sessions must still verify whether it is committed/pushed before relying on it, because final exit cleanup may occur after this prompt was drafted.

## Quick verification commands for next session

```bash
cd /mnt/local-analysis/workspace-hub

git status --short --branch

gh issue view 2656 --repo vamseeachanta/workspace-hub --json state,labels,title,url
for spec in \
  assetutilities:78:vamseeachanta/assetutilities \
  worldenergydata:394:vamseeachanta/worldenergydata \
  assethold:49:vamseeachanta/assethold \
  aceengineer-website:13:vamseeachanta/aceengineer-website \
  aceengineer-strategy:19:vamseeachanta/aceengineer-strategy; do
  repo_dir=${spec%%:*}; rest=${spec#*:}; issue=${rest%%:*}; gh_repo=${rest#*:}
  echo "## $repo_dir #$issue"
  (cd "/mnt/local-analysis/workspace-hub/$repo_dir" && git status --short --branch && git rev-parse --short HEAD origin/main)
  gh issue view "$issue" --repo "$gh_repo" --json state,labels,title,url --jq '{state,title,url,labels:[.labels[].name]}'
done
```
