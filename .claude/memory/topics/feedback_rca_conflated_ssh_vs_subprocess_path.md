> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_rca_conflated_ssh_vs_subprocess_path.md

---
name: rca-conflated-ssh-vs-subprocess-path
description: "When diagnosing subprocess \"executable not found on PATH\" failures, never substitute the SSH-session $PATH for the subprocess PATH. They are different envs. Read /proc/<pid>/environ for ground truth."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c33ac478-fe2b-456e-b884-3c68d71720c2
---

**Rule:** For any "executable not found on PATH" symptom in a long-running daemon's spawned subprocess, the diagnostic ground truth is `/proc/<daemon-pid>/environ`, NOT `echo $PATH` from an SSH session. Confirm what the subprocess actually inherits before recommending a fix.

**Why:** [#2712](https://github.com/vamseeachanta/workspace-hub/issues/2712) issue body claimed "subprocess PATH lacks `~/.local/bin` (verified: SSH session `echo $PATH` returns …)" and recommended a sudo symlink to `/usr/local/bin`. Closing verification on 2026-05-15 found the gateway (systemd user unit, `hermes-gateway.service`) actually had `/home/vamsee/.local/bin` AND `/home/vamsee/.hermes/hermes-agent/venv/bin` in its `/proc/<pid>/environ` PATH — the worker subprocess inherits this via `env = dict(os.environ)` (`hermes_cli/kanban_db.py:3779`). The original failure could not be reproduced; sudo fix would have been belt-and-braces but not load-bearing. Cost of conflation: ~30 min of agent time across two sessions, plus an obsolete sudo recommendation that needed manual revocation.

Three distinct PATH contexts that can all be different on the same machine:
1. **SSH non-login session** — sourced from `/etc/environment` + `~/.ssh/environment` only; misses interactive-shell additions like `~/.local/bin`. `ssh host 'echo $PATH'` shows this.
2. **Login / interactive shell** — sourced `.profile`, `.bashrc`, etc.; includes `~/.local/bin`, `~/.npm-global/bin`, venv paths. `ssh -t host 'bash -l -c "echo \$PATH"'` shows this.
3. **Daemon / systemd-user-unit subprocess** — frozen at daemon-launch time, persists across SSH sessions. `cat /proc/<pid>/environ | tr '\0' '\n' | grep PATH` shows this. THIS is what `subprocess.Popen(cmd, env=dict(os.environ))` from the daemon would see.

**How to apply:** When triaging a subprocess "not found" failure, before recommending any PATH-related fix:

1. Find the spawning process: `pgrep -af '<daemon name>'`. Note the PID.
2. Read its frozen env: `cat /proc/<pid>/environ | tr '\0' '\n' | grep -E '^(PATH|HOME|USER)='`.
3. Find the spawn site in source: `grep -rn 'subprocess.Popen\|env=' <source dir>`. Check whether the spawn passes `env=` explicitly or inherits. If explicit, find where `env` is constructed.
4. Replicate the spawn: write a small Python that reads `/proc/<pid>/environ` and calls `subprocess.Popen([target_executable, "--help"], env=that_env)`. If it succeeds, the original RCA is wrong.
5. ONLY after that, propose a fix. The right fix depends on whether the subprocess truly has a broken PATH (then: fix the daemon launch context) or the failure has moved (then: capture fresh repro before sudo).

Cross-reference: [[project_ace_linux_2_dispatch_capability]] — the live example. [[feedback_mock_vs_live_invocation_divergence]] — sister rule for external CLIs (verify against live state, not assumed state).

**Do NOT apply when:** the symptom is a fresh failure with a fresh `/proc/<pid>/environ` snapshot already attached. Then the diagnostic loop is done; trust the snapshot. This rule fires for stale issues, second-hand RCAs, or any case where the only PATH evidence is from an SSH session rather than `/proc`.
