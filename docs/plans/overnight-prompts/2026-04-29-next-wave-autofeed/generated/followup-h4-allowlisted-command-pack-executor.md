# Follow-up draft (H4) — Allowlisted comment-only command-pack auto-executor

> **Status:** DRAFT. Not filed. Per #2557 report's duplicate-of analysis, H4 is "new issue, coordinate with [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519)". Verify before filing.

## Title (if filed as new issue)

`feat(govern): allowlisted comment-only command-pack auto-executor`

## Body

### Summary

A nightly cron-driven executor that runs ONLY allowlisted GitHub commands from operator-prepared command packs (e.g. `lane-monitor-latest.md` produces `github-command-pack.md` files at every overnight run). Allowlist is hard: only `gh issue comment …` and `gh pr comment …` invocations pass; everything else is rejected.

### Why this is bounded

- New script `scripts/govern/exec-safe-command-pack.sh` with a hard allowlist.
- One cron line.
- No new data source; consumes existing operator-prepared `.md` files in `docs/plans/overnight-prompts/*/results/`.
- Mutation-class packs (label changes, issue close, PR merge, git push) remain owner-only.

### Allowlist contract

```
Permitted (pass through to bash):
  gh issue comment <NNNN> --body-file <path>
  gh pr comment <NNNN> --body-file <path>

Rejected (fail-closed; log + skip):
  Any line containing: --add-label, --remove-label, --label
  Any line containing: gh issue close, gh issue reopen
  Any line containing: gh pr merge, gh pr close, gh pr edit
  Any line containing: git push, git tag, git branch -D, git reset --hard
  Any inline shell metacharacter that could escape (`, $(, ;, &&, ||) outside the body-file path
  Any unquoted variable expansion in the command line
```

### Implementation sketch

```bash
#!/usr/bin/env bash
# scripts/govern/exec-safe-command-pack.sh <command-pack.md>
set -euo pipefail
PACK="$1"
LOG="${EXEC_PACK_LOG:-state/exec-pack-$(date -u +%Y%m%dT%H%M%SZ).log}"

allow_re='^gh (issue|pr) comment [0-9]+ --body-file [A-Za-z0-9_./-]+$'

while IFS= read -r line; do
  # Skip blanks, code fences, comments, prose
  [[ -z "${line// /}" || "$line" =~ ^# || "$line" =~ ^\` || "$line" =~ ^[A-Za-z] ]] && continue
  if [[ "$line" =~ $allow_re ]]; then
    echo "[ALLOW] $line" | tee -a "$LOG"
    bash -c "$line"
  else
    echo "[DENY ] $line" | tee -a "$LOG"
  fi
done < "$PACK"
```

### Acceptance criteria

- [ ] `scripts/govern/exec-safe-command-pack.sh` exists with the allowlist regex hard-coded.
- [ ] Test fixture: a 6-command pack (3 allowed + 3 denied) — script must allow all 3 + deny all 3 with no false positives.
- [ ] Cron entry runs nightly against the most recent `*/results/*-command-pack.md` files.
- [ ] All allow/deny decisions logged to `state/exec-pack-*.log` with timestamps.
- [ ] No state mutation outside `gh issue comment` / `gh pr comment`.

## Duplicate-of check (2026-04-29)

- [#2519](https://github.com/vamseeachanta/workspace-hub/issues/2519) — `feat(hermes): orchestrate AI provider usage and workstation dispatch` — OPEN, `priority:critical`. Hermes-orchestration umbrella; H4's executor would slot under that. **Coordinate with #2519's plan — file H4 as a sibling issue if #2519's scope is "lane management" rather than "comment automation", otherwise fold into #2519.**
- [#2523](https://github.com/vamseeachanta/workspace-hub/issues/2523) / [#2524](https://github.com/vamseeachanta/workspace-hub/issues/2524) / [#2525](https://github.com/vamseeachanta/workspace-hub/issues/2525) — orchestration-adjacent issues. Verify none already covers comment-pack execution.
- No issue currently scopes "comment-only execution with hard allowlist".

Verdict: AMBIGUOUS — `#2519` may absorb. **Recommended action: comment on #2519 with the H4 sketch and ask whether it should be filed as a sub-issue or absorbed.**
