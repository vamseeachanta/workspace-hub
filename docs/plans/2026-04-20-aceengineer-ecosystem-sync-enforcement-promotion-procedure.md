# Ecosystem Sync — Promotion Procedure for Enforcement Fix 07e7e7d07

Date: 2026-04-20
Target fix: `07e7e7d07` — `fix(enforcement): avoid plan-gate false negative with many markers`
Purpose: promote the verified enforcement reliability fix into `main` before more plan-gated implementation work depends on the old behavior.

## Recommendation
Promote `07e7e7d07` into `main` as a narrow enforcement fix before broader ecosystem-sync rollout work.

Why this is the best next move:
- it addresses a verified blocker, not speculative cleanup
- it has targeted regression coverage in `tests/hooks/test-require-plan-approval.sh`
- it reduces governance false negatives for future approved work across workspace-hub

## Preconditions
- Run from the main checkout: `/mnt/local-analysis/workspace-hub`
- Working tree should be clean or intentionally understood
- No hook bypass
- No bundling with unrelated feature commits unless explicitly intended

## Safe promotion sequence

### 1. Verify main checkout state
```bash
cd /mnt/local-analysis/workspace-hub
git status --short --branch
git branch --show-current
git fetch origin --prune
git pull --ff-only origin main
```

Expected:
- current branch is `main`
- pull succeeds cleanly

### 2. Inspect the target fix before applying it
```bash
git show --stat 07e7e7d07
git show 07e7e7d07 -- tests/hooks/test-require-plan-approval.sh scripts/enforcement/require-plan-approval.sh
```

Expected focus:
- only the enforcement script and targeted regression test are involved

### 3. Cherry-pick the fix onto main
```bash
git cherry-pick 07e7e7d07
```

If there is a conflict:
```bash
git status
# resolve only the enforcement-related files
git add <resolved-files>
git cherry-pick --continue
```

If the cherry-pick should be abandoned:
```bash
git cherry-pick --abort
```

### 4. Re-run the targeted enforcement validation
```bash
bash tests/hooks/test-require-plan-approval.sh
```

Expected:
- the hook regression test passes

### 5. Sanity-check repo status
```bash
git status --short --branch
git log --oneline -3
```

Expected:
- only the cherry-picked enforcement commit is new on `main`

### 6. Push the narrow fix
```bash
git push origin main
```

### 7. Post-promotion verification
Recommended checks after push:
```bash
git rev-parse HEAD
git ls-remote --heads origin main
```

Optional governance note:
- reference `docs/plans/2026-04-20-aceengineer-ecosystem-sync-enforcement-fix-note.md`
- state that the promotion is a repo-wide enforcement reliability correction, not an ecosystem-sync feature rollout

## Stop conditions
Stop and do not continue to broader rollout if any of these occur:
- `git pull --ff-only origin main` fails
- cherry-pick conflicts extend beyond the enforcement files and test
- `bash tests/hooks/test-require-plan-approval.sh` fails after cherry-pick
- unrelated dirty state on main would be mixed into the promotion

## After successful promotion
Recommended next sequence:
1. create the 3 review-derived hardening issues using `docs/plans/2026-04-20-aceengineer-ecosystem-sync-gh-create-commands.sh`
2. move to Stage 2 execution on `ace-linux-1` main checkout
3. use these handoff artifacts as gates:
   - `docs/plans/2026-04-20-aceengineer-ecosystem-sync-stage2-authorization.md`
   - `docs/plans/2026-04-20-aceengineer-ecosystem-sync-deploy-readiness-checklist.md`
   - `docs/plans/2026-04-20-aceengineer-ecosystem-sync-operator-runbook.md`
