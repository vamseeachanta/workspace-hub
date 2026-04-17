# Session exit handoff — session-log ecosystem follow-up issues 2332-2333

Date/time: 2026-04-17 09:43 CDT
Repo: `vamseeachanta/workspace-hub`

## What was completed

This session reviewed the current provider-session ecosystem audit, checked existing GitHub coverage to avoid duplicates, and created two future follow-on issues for gaps that were still not explicitly tracked.

## GitHub issues created

- #2332 — `chore(harness): drive provider-audit bare-python3 debt to canonical uv-run runtimes`
- #2333 — `feat(validation): classify transient worktree and scratch-path session reads separately from actionable repo drift`

## Why these two issues were created

### #2332
The provider-session audit still shows significant cross-provider bare-`python3` usage:
- Hermes: 1,705
- Claude: 698
- Codex: 319
- Gemini: 291

This is a recurring runtime-policy leak visible across the whole ecosystem and is not yet captured as a focused provider-audit-driven issue.

### #2333
The provider-session audit still mixes durable repo drift with transient/session-local path noise:
- Hermes missing external reads under `/mnt/local-analysis/worktrees/...`
- Claude missing external reads under `/tmp/...`
- other scratch/machine-local paths that should not compete with canonical stale-path debt in the same topline remediation bucket

This follow-on issue is meant to sharpen unresolved-read reporting so weekly triage stays focused on durable ecosystem fixes.

## Existing related issues intentionally reused instead of duplicated

The session checked and reused the existing issue tree around:
- weekly ecosystem review and scorecard: #2089, #2122, #2138, #2144, #2173
- unresolved-read / registry drift pipeline: #2161, #2167, #2168, #2174, #2179, #2185, #2192, #2197
- stale-reference cleanup already underway: #2213, #2214, #2310, #2311, #2312
- older cross-platform python/bash cleanup context: #48

## Recommended next move

1. Treat #2332 as the direct follow-on if you want the highest-ROI execution-policy cleanup from current session logs.
2. Treat #2333 as the direct follow-on if you want cleaner unresolved-read signal before more remediation work is scheduled.
3. If continuing issue creation from session-log evidence, the next logical layer would be issue linking/commenting from #2332/#2333 back into the weekly-review and unresolved-read parent chain.

## Repo state on exit

Working tree was already dirty before this session and was intentionally not cleaned.

Notable repo-tracked change created in this session:
- `docs/handoffs/session-2026-04-17-session-log-ecosystem-followups-exit.md`

The working tree also contains many unrelated modified/untracked files from prior work, including `.claude/state/*`, `config/ai-tools/*`, `docs/plans/*`, `docs/reports/*`, `scripts/review/results/*`, wiki files, and other handoff artifacts.

## Exit readiness

This thread is documented.
The future follow-on issues exist on GitHub and were verified after creation:
- #2332
- #2333

No implementation or cleanup was performed beyond issue creation and handoff documentation.