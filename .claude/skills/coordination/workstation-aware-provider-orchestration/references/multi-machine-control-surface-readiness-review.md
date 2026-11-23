# Multi-machine control-surface readiness review pattern

Use this reference when a session tries to run Hermes or provider agents from one control surface across multiple machines.

## Durable lesson

A machine may be reachable and have the expected programs installed, but still be unsafe for dispatch if the readiness producer and dispatch consumer disagree on schema or launch context.

## Review checklist

1. **Topology before launch**
   - Identify each host role: control plane, Linux overflow worker, licensed Windows worker, simulation-only worker, or unknown.
   - Record reachability and the exact launch path: local shell, SSH login shell, remote tmux, WinRM, Telegram gateway, or manual handoff.

2. **Program status in the launch environment**
   - Check tool presence in the same environment that will run work. For SSH workers, prefer `bash -lc` or the exact tmux command path.
   - Capture provider tools (`hermes`, `claude`, `codex`, `gemini`), repo tools (`git`, `gh`, `uv`, `tmux`), and task tools.

3. **Git/repo mutation contract**
   - Emit `dirty`, `ahead`, `behind`, `branch`, `head`, `remote`, and `missing_data` per host/repo.
   - If `gh auth` is unavailable remotely, keep GitHub mutation on the control-plane host even if the remote worker can run code/tests.

4. **Automated dispatch must fail closed**
   - Missing readiness fields are blockers, not implicit safe values.
   - Do not let first-host array order determine routing. Continue scanning usable hosts and explain skipped hosts.
   - Keep local control-plane readiness separate from remote worker readiness; never apply local environment checks to a remote host.

## Typical issue-comment structure

- Current topology: host → role → reachable/control path.
- Program status: installed/authenticated/smoke-tested vs missing/unknown.
- Dispatch eligibility: `READY`, `READY_CONTROL_PLANE_ONLY`, or explicit `BLOCKED_*` code.
- Next logical steps: patch blockers, rerun targeted tests/legal scan, then adversarial review before merge/close.
