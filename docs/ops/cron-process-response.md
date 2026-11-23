# Cron Process Response Runbook

Use this runbook when a scheduled task appears duplicated, stale, blocked, or
long-running. Investigation is read-only until the operator approves an exact
process group and action.

## 1. Capture a bounded snapshot

Filter a single `ps` snapshot by the known task command. Do not traverse the
workspace, mounted drives, or `/proc` trees.

```bash
ps -eo pid,ppid,pgid,sid,etimes,stat,wchan:24,args --sort=-etimes \
  | awk 'NR==1 || /scripts\/cron-repository-sync.sh|scripts\/sync\/sync-ecosystem.sh/'
```

For general incident notes, preserve this exact field contract:

```text
ps -eo pid,ppid,pgid,sid,etimes,stat,wchan:24,args
```

Report the snapshot timestamp, PID, PPID, PGID, SID, elapsed seconds, process
state, wait channel, full command, and bounded descendants. Never reuse PIDs
from an earlier report as an action command.

## 2. Establish task identity

Match the exact script and expected workspace ownership. Do not infer that an
unrelated Python process is an import-timing probe. A reported import-timing
process requires a current command line containing an exact expected form such
as `python -X importtime` or the named `import-timing` wrapper. A probe command
that merely contains those search terms is not the target.

The task-owned runtime record under `.claude/state/cron-runtime/<task>/` is
supporting evidence. Validate its child PID and process start token before
trusting it; PID reuse classifies as stale evidence.

## 3. Select a safe process group

The cron daemon and its `/usr/sbin/CRON` children can share a daemon process
group. Never signal the cron daemon's shared process group. The safe candidate
is the isolated task session/process group whose leader is the cron-launched
shell or runtime supervisor. Verify every member immediately before proposing
action.

Present the proposed graceful command without running it:

```text
kill -TERM -- -<PGID>
```

The angle-bracket value must come from a fresh snapshot. The operator must
approve that exact PGID and signal.

## 4. Graceful termination sequence

After approval:

1. Take another fresh snapshot and abort if PID, PGID, SID, command, or start
   identity differs.
2. Send TERM only to the approved isolated process group.
3. Wait a bounded interval while continuing read-only checks.
4. Verify that the group is absent and inspect task-specific lock/runtime state.
5. Inspect repository locks and worktree state before allowing another mutating
   run.

No automated SIGKILL is permitted. Escalation requires a separate user approval
based on a new snapshot and an explanation of the risk of interrupting the
observed command. Documentation of escalation policy must not include a
copy-paste KILL command.

## 5. Scheduler reconciliation

Do not hand-edit a managed crontab entry. Compare the installed line to
`config/scheduled-tasks/schedule-tasks.yaml`, preview the transactional cutover,
and preserve or fail closed on entries whose ownership is not established by an
explicit fingerprint. Applying a cutover remains a separate operator action.
