# Ecosystem Sync — Final Promotion List

Date: 2026-04-20
Source integration worktree:
- path: `/mnt/local-analysis/worktrees/workspace-hub-ecosystem-sync-integration`
- branch: `integration/ecosystem-sync-stage1-stage2-handoff`
- base: `e34093282c673cb163395d452a8e796a01d0959b`

Status summary:
- Wave A integrated and validated
- Wave B integrated and validated
- Wave C integrated and validated
- invocation-path blocker fixed and validated in commit `83abb519e`
- no push performed

## Integrated commit set above base
In exact order currently present in the clean integration worktree:

1. `d82230a10` `fix(enforcement): avoid plan-gate false negative with many markers`
2. `7e299341a` `feat(ecosystem-sync): scaffold package with Signal dataclass`
3. `a19826430` `feat(ecosystem-sync): config loader + 6-repo production config`
4. `9db8b7e59` `feat(ecosystem-sync): state load/save with timestamp-aware change detection`
5. `c36d44a67` `feat(ecosystem-sync): signal 1 — release tag detector + fixtures`
6. `7e73f4b8f` `feat(ecosystem-sync): signal 2 — new case-study / example detector`
7. `f03e1d8d9` `feat(ecosystem-sync): signal 3 — README capability section diff`
8. `5ccf7be24` `feat(ecosystem-sync): signal 5 — labeled closed-issue detector`
9. `6d70dcbb9` `feat(ecosystem-sync): digest renderer + golden tests`
10. `23cdc394d` `feat(ecosystem-sync): issue opener with dedupe + retry-once`
11. `27a2d3a13` `feat(ecosystem-sync): orchestrator with --dry-run and --doctor`
12. `c3df50876` `feat(ecosystem-sync): bash cron entry with flock + one-shot rebase`
13. `2d0e2b0e3` `docs(plans): ecosystem-sync Tasks 7-11 + review handback`
14. `c3b24b336` `docs(plans): ecosystem-sync next-wave handoff bundle`
15. `699619413` `docs(plans): add ecosystem-sync issue creation packets`
16. `eb93a4a9d` `docs(plans): add ecosystem-sync gh issue create commands`
17. `1bd66834b` `docs(plans): add enforcement fix promotion procedure`
18. `5bf99d9c1` `docs(plans): add ecosystem-sync operator command bundle`
19. `a62cc6f17` `docs(plans): align ecosystem-sync issue labels with repo taxonomy`
20. `83abb519e` `fix(ecosystem-sync): invoke orchestrator as module`

## Recommended promotion waves

### Wave A — governance reliability fix
1. `d82230a10` `fix(enforcement): avoid plan-gate false negative with many markers`

Why separate:
- repo-wide governance value
- already validated by `bash tests/hooks/test-require-plan-approval.sh`
- smallest high-value landing unit

### Wave B — Stage 1 ecosystem-sync implementation
1. `7e299341a`
2. `a19826430`
3. `9db8b7e59`
4. `c36d44a67`
5. `7e73f4b8f`
6. `f03e1d8d9`
7. `5ccf7be24`
8. `6d70dcbb9`
9. `23cdc394d`
10. `27a2d3a13`
11. `c3df50876`
12. `83abb519e`

Important note:
- `83abb519e` is part of the production-ready Stage 1 landing set, not optional cleanup. It fixes the verified invocation-path failure found after integration.

### Wave C — operator / handoff docs
1. `2d0e2b0e3`
2. `c3b24b336`
3. `699619413`
4. `eb93a4a9d`
5. `1bd66834b`
6. `5bf99d9c1`
7. `a62cc6f17`

## Explicit exclusions
Do not include:
- `c55d8f4af` `chore(planning): plan-approved marker for ecosystem-sync workstream`

## Validation evidence for current landing candidate
From the clean integration worktree:
- `bash tests/hooks/test-require-plan-approval.sh` → pass
- `bash tests/ecosystem-sync/fixtures/repos/build_fixtures.sh` → builds local fixtures
- `uv run pytest tests/ecosystem-sync -q` → `35 passed`
- `uv run python -m scripts.ecosystem_sync.run --doctor` → pass

## Remaining caveat
The wrapper still cannot be fully validated inside the integration worktree because `.claude/cron/ecosystem-sync.sh` intentionally runs:
- `git pull --ff-only origin main`

That fails in the non-main integration topology, as expected. Final wrapper `--doctor` / `--dry-run` validation still belongs on the real main checkout after promotion.

## Recommended next move
Seek explicit approval for side effects, then land from the clean integration worktree rather than from the dirty main checkout.