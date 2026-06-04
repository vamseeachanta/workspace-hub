# Session handoff — statusline blank-render fix + cross-machine rollout (2026-06-04)

## Summary

Diagnosed and fixed the invisible Claude Code statusline on `ace-linux-1`. Root cause:
`.claude/statusline-command.sh` runs under `set -euo pipefail`; two unguarded command
substitutions killed the script with no output whenever the session cwd was outside a
git repo (e.g. `/mnt/local-analysis`) or the branch had no issue number (e.g. `main`):

- `issue_num=$(echo "$branch" | grep -oE '[0-9]{3,5}' | head -1)` — grep exits 1 on no match
- `lr=$(git rev-list --count --left-right '@{u}...HEAD' 2>/dev/null)` — fails with no upstream

Claude Code hides statusline command errors entirely (non-zero exit → blank line, no
diagnostic), so the failure was silent. Third instance of the
pipefail-kills-optional-match defect class in this ecosystem (review-gate SIGPIPE
`e0c1e9767`, verification-queue CRLF, now statusline).

## State

| Item | State | Evidence |
|---|---|---|
| Fix (`\|\| true` guards ×2) | **MERGED to main** | PR [#2954](https://github.com/vamseeachanta/workspace-hub/pull/2954), commit `500ebba28`, merged 2026-06-04T12:38Z |
| ace-linux-1 | LIVE (working-tree copy matches merged file) | tested non-git cwd + repo cwd, both exit 0 |
| Other machines | **PENDING** — run the rollout prompt below | — |

## Verification method (do not skip the non-git-cwd case)

```bash
echo '{"model":{"display_name":"X"},"workspace":{"current_dir":"<dir>"},"cost":{"total_cost_usd":0}}' \
  | bash "$WORKSPACE_HUB/.claude/statusline-command.sh"; echo "EXIT=$?"
```

Must exit 0 and print one line from BOTH a non-git directory (`/tmp`, `C:\`) and inside
the repo. The non-git-cwd case is the regression that made the statusline blank.

## Cross-machine rollout prompt (paste into Claude Code on each machine, any OS)

```text
Fix and standardize my Claude Code statusline on this machine (workspace-hub PR #2954 context):

1. LOCATE the workspace-hub repo for this OS (Linux: /mnt/local-analysis/workspace-hub or
   ~/workspace-hub; Windows: D:\workspace-hub; otherwise search common roots). Use that
   path as HUB below.

2. UPDATE the script: git fetch origin, then get .claude/statusline-command.sh from
   origin/main (it contains the "|| true" guards on the `issue_num=$(... grep ...)` line
   and the `lr=$(... rev-list '@{u}...HEAD' ...)` line — PR #2954, merged 2026-06-04).
   Do NOT edit the file by hand and do NOT commit anything — just get the canonical
   version on disk.

3. SETTINGS: ensure ~/.claude/settings.json (or %USERPROFILE%\.claude\settings.json) has:
   "statusLine": { "type": "command", "padding": 0, "command":
     "bash \"${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}/.claude/statusline-command.sh\"" }
   On Windows, confirm Git Bash is available to Claude Code; if `bash` isn't on PATH for
   the statusline subprocess, use the full path to Git Bash's bash.exe and HUB in
   forward-slash form. Preserve all other settings keys.

4. ENV: ensure WORKSPACE_HUB is set persistently to HUB (Linux/macOS: shell profile;
   Windows: user environment variable), since sessions may start outside any git repo.

5. TEST exactly as Claude Code invokes it — pipe minimal JSON into the script and check
   exit code, from BOTH a non-git directory (e.g. /tmp or C:\) and from inside HUB:
   echo '{"model":{"display_name":"X"},"workspace":{"current_dir":"<that dir>"},"cost":{"total_cost_usd":0}}' | bash HUB/.claude/statusline-command.sh
   Both runs MUST exit 0 and print a one-line status. The non-git-cwd case is the
   regression that previously made the statusline blank — do not skip it.

6. REPORT a table: repo path | file at guarded version yes/no (git log -1 for the file) |
   settings block present/added | WORKSPACE_HUB value | both test results. Make no other
   changes; do not push or commit anything.
```

## Dirty-state exceptions (expected residue on ace-linux-1)

- Main checkout remains on in-flight branch `fix/track-fleet-skills-2925-portable` with
  its pre-existing #2925 dirty files (config/ai-tools/*, docs/reports/*, logs/*) — not
  this session's work; untouched.
- `.claude/statusline-command.sh` working-tree edit on that branch is byte-identical to
  the merged origin/main version; reconciles on the branch's next rebase. Do not revert —
  it is the live statusline for current sessions.

## Known follow-on (not blocking)

- `C:-%` (Claude quota unknown) in the rendered line is pre-existing:
  `config/ai-tools/agent-quota-latest.json` lacks a `claude.week_pct` entry; the real
  session JSON normally fills it via `rate_limits.seven_day`. Separate concern from this fix.

## No-external-action status

No issues created/closed; PR #2954 created by this session and merged by the user.
No cron, settings, or env changes made on this machine.
