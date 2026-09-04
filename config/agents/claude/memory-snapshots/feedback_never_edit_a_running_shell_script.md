---
name: never-edit-a-running-shell-script
description: "bash reads scripts incrementally by byte offset — editing a script while an invocation is blocked (e.g. inside an ssh) makes the old process execute the NEW file's bytes on resume; cost a completed 75-min mesh on gpu-claw"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d40540de-bdf2-4f0d-a52f-ec7d12a1f029
  modified: 2026-09-04T02:42:38.598Z
---

On 2026-09-04 02:40Z a subagent's `stage4_build.sh` was blocked inside its launch ssh (a
`cd && … &` wrapper-subshell bug kept the ssh open until the remote chain finished). While
blocked, the agent edited the script on disk. When the ssh returned, bash resumed reading the
*rewritten* file at its stale byte offset, landed on the new launch line, and re-launched the
mesh chain — whose start-up `rm -rf constant/polyMesh log.*` destroyed the just-completed
run-1 mesh and its `checkMesh` verdict. ~1.3 h of gpu-claw lost, the launch slipped to 04:00Z.

**Why:** bash does not load a script into memory; it reads it as it executes. Any edit to a
script that has a live invocation is executed by that invocation.

**How to apply:**
- Never edit a shell script that may have a running invocation; copy it to a new name and
  run the copy, or wrap the entire body in `main() { … }; main "$@"` so bash parses the whole
  file before executing any of it (applied to `stage4_build.sh`).
- Remote chain launchers must return immediately: `ssh host 'setsid nohup … >/dev/null 2>&1 </dev/null & disown'`
  with the chain writing its own PID file — never `cd && cmd &` inside the ssh string.
- Chains that `rm` prior outputs at start-up must refuse to start if a `*_DONE` marker exists.
- Related: [[subagent-relaunch-reads-as-crash]] — a subagent killing/relaunching remote runs
  without reporting makes the main session's marker watcher read it as a crash; briefs must
  say "report before any kill/relaunch".
