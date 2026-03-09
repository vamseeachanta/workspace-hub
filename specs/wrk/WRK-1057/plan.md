# WRK-1057 Plan — repo-health.sh dashboard

## Mission
Single command shows health of every workspace-hub repo: git state, branch,
last commit, and last test result.

## Implementation Steps (Route A)
1. Iterate repos: parse .gitmodules path= entries + hub root
2. Per-repo: branch, dirty flag, ahead/behind vs origin, last commit (all timeout 5s)
3. Test result: read logs/tests/<repo>-last.txt; degrade to "unknown" if absent
4. Output: ANSI colour table (green/yellow/red) + --json flag; [[ -t 1 ]] guard
5. /today integration: section script (collapsible); wired into daily_today.sh

## Tests/Evals
| test | scenario | expected |
|------|----------|----------|
| clean repo | no dirty files, test=pass | green row |
| dirty repo | uncommitted changes | red row |
| missing test log | no logs/tests/ dir | yellow/unknown, no crash |
| --json flag | scripting use | valid JSON array |
| slow repo (digitalmodel) | large pack files | completes within timeout |

## Out of Scope
Remote fetch (no network calls in health check; stale ahead/behind is acceptable)
