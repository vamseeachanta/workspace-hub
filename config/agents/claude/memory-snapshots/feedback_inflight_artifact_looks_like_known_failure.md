---
name: feedback_inflight_artifact_looks_like_known_failure
description: "A slow tool's part-written output read mid-flight is indistinguishable from its documented failure mode — confirm the process exited before diagnosing"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f50c3710-9ec0-4192-9df6-50682a6c8539
  modified: 2026-08-03T03:51:57.167Z
---

An in-flight artifact looks exactly like a failed one. Before diagnosing a failure from an
artifact's contents, **confirm the producing process has exited.**

2026-08-02: dispatched `plan-review-fanout.sh --providers=codex` for [[project_external_ssh_tailscale_fleet]]
plan #3784. Read the result 60 s later: **0-byte** `.md` plus a `.err` containing
`Reading additional input from stdin...`. That is a byte-for-byte match for the documented
failure signature in wh#3578 (codex exec hangs on stdin). I declared it INVALID_OUTPUT, built a
workaround, and **posted a wrong diagnosis to #3578** — including a confident cwd/NTFS-FUSE root-cause
hypothesis for a failure that never happened.

The run completed normally at **~10 minutes** and wrote a valid 4.2 KB review plus a disagreement file.
The `.err` line was progress chatter on stderr, not a fatal condition. Retracted on #3578.

**Why:** a known failure mode makes for a fast, satisfying pattern-match, and that is exactly when the
in-flight state gets misread — the more familiar the failure signature, the less the evidence gets
checked. Cost here was a wrong public diagnosis plus a redundant duplicate run.

**How to apply:**
- Check liveness first: `pgrep -af '<the command>'`, or wait on the task's completion notification.
  An empty/short artifact from a **live** process is not evidence of anything.
- Prefer waiting on the exit signal over polling file contents. For a background Bash task, the
  completion notification is the signal — polling the output file is what invites this error.
- Budget the real wall-clock. A 400+ line adversarial review prompt takes ~10 min, not ~1.
- Tooling fix that removes the ambiguity: write to `<name>.partial` and rename on success, so
  "in progress" and "failed" are distinguishable states.
- Same discipline as [[feedback_absence_of_signal_reads_as_success]] — absent output is not a verdict.
  Related: [[feedback_verify_subagent_line_citations_not_just_claims]].
