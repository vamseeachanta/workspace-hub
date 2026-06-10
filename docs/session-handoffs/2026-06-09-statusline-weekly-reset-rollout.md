# Session handoff — statusline weekly-usage/reset rollout: ace-linux-1 root-cause fix, #3021, ace-linux-2 done, Windows prompt (2026-06-09)

## Summary

User reported the statusline invisible on ace-linux-1. Root cause was **two-layered**:

1. **Stale checkout, not config**: local workspace-hub main was **174 commits behind
   origin/main**, still running the pre-#2954 script that dies under `set -euo pipefail`
   when the branch has no issue digits (`issue_num=$(... grep ...)` exits 1 → blank line,
   no diagnostic). Every feature the user asked for (weekly usage %, days-to-reset) was
   already merged (#2992/#3004, #2893/#3009) — just not on disk here.
   Fix: `git merge --ff-only origin/main` (clean, 0 ahead → strictly safe).
2. **One real feature gap**, fixed this session as PR
   [#3021](https://github.com/vamseeachanta/workspace-hub/pull/3021) (**MERGED**,
   squash `73b20271c`): the `C:` segment showed weekly % from session JSON
   `rate_limits.seven_day.used_percentage` but never a `·N.Nd` countdown, because
   `reset_days()` only reads the agent-quota files where claude is permanently
   `source: unavailable`. Now `days_until_iso()` (extracted helper) computes the
   countdown from the session JSON's `resets_at` — gated on `used_percentage` being
   present so % and countdown always come from the same snapshot — falling back to
   quota files unchanged.

Cross-review (T1, Codex adversarial): **MINOR**, 2 findings, both fixed in `c35fd6625`
(same-snapshot gating above; removed a fail-open `|| true` test assertion inherited from
#3004 and replaced it with a real regression test). Suite 14/14 bats green
(`tests/statusline/`), shellcheck clean.

## State

| Machine | State | Evidence |
|---|---|---|
| ace-linux-1 | **LIVE** — main at origin (incl. #3021); renders `C:63%·2.9d\|O:61%·1.5d\|G:100%` from non-git cwd, exit 0 | smoke run 2026-06-09 |
| ace-linux-2 | **LIVE** — ff'd to `7a0ae8142` (contains #3021); renders `C:63%·2.6d\|O:60%·1.2d` from `/tmp`, exit 0; jq+python3 present | ssh run 2026-06-09 |
| ace-linux-2 gap | `WORKSPACE_HUB` unset — `.bashrc` lacks the a1 hookup (`source HUB/config/shell/bashrc-snippets.sh`, a1 `.bashrc:138`). Sessions launched OUTSIDE any git repo can't resolve the statusline script. Agent-append to remote `~/.bashrc` is classifier-blocked (persistence) — **user action** | denial 2026-06-09 |
| Windows (D:\workspace-hub) | **PENDING** — run the prompt below | — |

## Verification invariants (unchanged from #2957, plus one)

- Pipe minimal JSON from a NON-git cwd; Claude Code hides statusline errors (non-zero
  exit = invisible line, no diagnostic).
- Trust Codex quota only when `source: "app-server-live"`.
- **NEW**: check checkout freshness first — `git rev-list --count --left-right
  origin/main...HEAD`. A behind-count in the hundreds means the machine is running
  pre-fix tooling regardless of what is merged.

## Windows rollout prompt (paste into Claude Code on the Windows machine)

```text
Sync this machine's Claude Code statusline with workspace-hub origin/main.
Context: the statusline now shows weekly AI usage % and days-to-weekly-reset
per provider (PRs #2954 pipefail guards, #2992/#3004 reset countdown, #2893/#3009
combined GSD wrapper, #3021 Claude countdown from session rate_limits JSON — all
MERGED). ace-linux-1 and ace-linux-2 are done; this machine is the last.
Handoff doc: docs/session-handoffs/2026-06-09-statusline-weekly-reset-rollout.md.
Work read-only against git: update the local checkout, settings, and env —
do NOT commit or push anything.

1. LOCATE the workspace-hub repo (expected D:\workspace-hub). Call it HUB.

2. UPDATE: cd HUB, git fetch origin, then report behind/ahead vs origin/main
   (git rev-list --count --left-right origin/main...HEAD). If clean and 0 ahead,
   git merge --ff-only origin/main. If untracked files block the merge, move
   them to %TEMP% (do not delete) and retry. If ahead or dirty, STOP and report
   instead of forcing. ace-linux-1 was silently 174 commits behind — staleness
   here is the root cause of a blank statusline, so this step is the fix.
   Verify after update: grep -c "days_until_iso" .claude/statusline-command.sh
   must return >= 2 (the #3021 feature; older versions return 0).

3. DEPENDENCIES (the script hard-requires these inside Git Bash):
   - bash: confirm Claude Code can spawn it (Git for Windows).
   - jq: REQUIRED — without it every field extraction fails and the statusline
     is blank. Check `bash -lc "command -v jq"`. If missing, install (winget
     install jqlang.jq or place jq.exe on PATH) and re-check from bash.
   - python3: needed only for the ·N.Nd reset countdown (ISO timestamp parsing).
     Check `bash -lc "command -v python3"`. On Windows `python` often exists but
     `python3` does not; if so the statusline still renders, just without
     countdowns — report it, and if a python3 shim is easy (python3.exe copy or
     App Execution Alias), note the option rather than hacking one in.

4. SETTINGS: ensure %USERPROFILE%\.claude\settings.json has this statusLine
   block (preserve all other keys):
   "statusLine": { "type": "command", "padding": 0, "command":
     "bash \"${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel)}/.claude/statusline-command.sh\"" }
   If bash is not on PATH for Claude Code subprocesses, use the full path to
   bash.exe and keep HUB in forward slashes (D:/workspace-hub).

5. ENV: set user environment variable WORKSPACE_HUB to the HUB path in
   forward-slash form (D:/workspace-hub) — sessions can start outside any git
   repo, where the git-toplevel fallback fails and only this variable saves
   resolution. (setx WORKSPACE_HUB D:/workspace-hub — setx takes effect in NEW
   processes only; restart Claude Code afterward.)

6. TEST exactly as Claude Code invokes it, from BOTH a non-git directory
   (cd C:\) and from inside HUB — both MUST exit 0 and print one line.
   Claude Code hides statusline errors entirely (non-zero exit = invisible
   line, no diagnostic), so do not skip the non-git case:
   echo '{"model":{"display_name":"X"},"workspace":{"current_dir":"C:/"},"cost":{"total_cost_usd":0.5},"context_window":{"used_percentage":30},"rate_limits":{"seven_day":{"used_percentage":37,"resets_at":"2026-06-12T18:00:00Z"}}}' | bash D:/workspace-hub/.claude/statusline-command.sh; echo "exit=$?"
   Expected segment: C:63%·N.Nd (countdown present only if python3 resolved in
   step 3; C:63% without a fabricated suffix is correct when python3 is absent).

7. REPORT one table: HUB path | behind/ahead before update | ff result |
   days_until_iso marker count | jq / python3 availability | settings block
   present/added | WORKSPACE_HUB value | both statusline tests (output + exit).
   List anything not completed and why. Do not commit, push, or create any
   scheduled task.
```

## ace-linux-2 follow-up (user, one command)

```
ssh ace-linux-2 'printf "\n# workspace-hub shell snippets (mirrors ace-linux-1)\n[ -f /mnt/local-analysis/workspace-hub/config/shell/bashrc-snippets.sh ] && source /mnt/local-analysis/workspace-hub/config/shell/bashrc-snippets.sh\n" >> ~/.bashrc'
```

Then verify: `ssh ace-linux-2 'bash -lc "echo $WORKSPACE_HUB"'` →
`/mnt/local-analysis/workspace-hub`.

## Dirty-state exceptions / residue

- `/tmp/wshub-untracked-backup-2026-06-09/` (ace-linux-1): 7 locally-generated
  artifacts (session-signals JSONLs, wiki-health reports, equality-matrix HTML) that
  blocked the 174-commit fast-forward; origin's tracked versions are canonical.
  Deletable after a few days.
- `/tmp/pr3021.diff`, `/tmp/pr3021-codex-review.md`, `/tmp/pr3021-codex-stdout.log`
  (ace-linux-1): cross-review evidence, summarized in the PR #3021 comment. Deletable.
- Pre-push gate: pushes from ace-linux-1 still require `--no-verify` (check-all
  sibling-layout blocker, tracked in memory; unrelated to content). User authorized it
  for this session's pushes.

## No-external-action status

PR #3021 opened by this session, merged by the user (2026-06-09T20:54Z); review comment
posted on the PR. No crons, schedulers, or settings changed on any machine. The one
attempted env change (a2 `~/.bashrc` append) was classifier-denied and routed to the
user (see follow-up above).

## Next steps

1. Windows machine: paste the prompt above (the only PENDING machine).
2. ace-linux-2: run the one-command `.bashrc` hookup above.
3. (Standing, unrelated) check-all sibling-layout pre-push blocker remains OPEN.
