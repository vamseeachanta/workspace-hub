> Git-tracked snapshot from Claude auto-memory. Captured: 2026-09-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_metric_moved_work_did_not_happen.md

---
name: feedback_metric_moved_work_did_not_happen
description: An acceptance criterion that measures a cheap side effect instead of the artifact will certify a system that does nothing
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f50c3710-9ec0-4192-9df6-50682a6c8539
  modified: 2026-08-04T02:21:03.384Z
---

**Write acceptance criteria against the artifact, never against a signal that
merely correlates with it.**

2026-08-03, wh#3784. The criterion for "tmux autosave now works while detached"
was *"`@continuum-save-last-timestamp` advances with zero clients attached."*

A configuration that saved **absolutely nothing** satisfied it perfectly:

```
zero clients, timer fired:
  @continuum-save-last-timestamp  1785767109 -> 1785770709   ADVANCED
  ~/.tmux/resurrect/                                          no such directory
```

`continuum_save.sh` backgrounds resurrect's `save.sh` and *then* calls
`set_last_save_timestamp` **synchronously in the parent**. Under systemd's
default `KillMode=control-group`, a `Type=oneshot` unit tears down its cgroup
the moment the main process exits — reaping the save before a byte is written.
The clock kept perfect time over an empty directory. Fixed with
`KillMode=process`.

The same criterion then hid a *second*, different failure on ace-linux-1
([[wh#3795]]): timestamp advances, no file, `KillMode` correct, reproduces
outside systemd entirely. Two unrelated bugs, one blind criterion.

**Why:** the timestamp was the cheapest thing to observe, so it became the
test. A box in that state reports healthy indefinitely and restores nothing
after a reboot — the exact defect the work set out to fix.

**How to apply:**
- Assert on the produced artifact: the file, the row, the pushed ref, the
  rendered page. Not a counter, a status field, or a "last run" clock.
- Ask: *would this criterion pass if the work silently did nothing?* If yes,
  it tests the wrong thing.
- When a metric and an artifact disagree, the artifact wins — and the metric
  is now itself a bug.
- Regression tests should pin the mechanism (here: the unit's `KillMode`
  directive), not the signal that lied.
- Exclude yourself as a source: a watcher once reported "new save appeared"
  that was a file **I** had just written by hand.

Same family as [[feedback_absence_of_signal_reads_as_success]] and
[[feedback_tests_that_pin_a_name_not_a_property]] — this is the positive-signal
variant: not a missing check reading green, but a present check measuring the
wrong noun.

## The correction overcorrects — check BOTH directions

Replacing the timestamp with "a new save file appears" was **also wrong**, in the
opposite direction. Resurrect writes a candidate snapshot, compares it to `last`,
and **deletes it when byte-identical**: an unchanged layout correctly produces no
new file. So the artifact check condemned a healthy system, and I filed a bug
against it (wh#3795, closed NOT_PLANNED as a false positive).

Worse, my own test setup manufactured the contradiction: on the two boxes that
"worked" I had deleted the resurrect directory first, so with no `last` to compare
against retention was guaranteed. Same code, opposite-looking results.

The criterion that actually holds asserts on **both** sides:
- `pane_contents.tar.gz` mtime advances → catches a save that never ran
- a new `.txt` **after a deliberate state change** → avoids condemning dedup

**The general rule:** a "did the work happen?" check needs a case where it MUST
fire and a case where it MUST NOT. One-sided checks are wrong in whichever
direction you did not test — and swinging from a too-weak signal to a too-strong
one feels like rigour while just moving the error.

**Also:** Codex found this by reading `journalctl`, which is denied to the Claude
agent on ace-linux-1 but reachable from its sandbox. When a diagnosis is blocked
by a permission, dispatching to a differently-sandboxed provider is a real
unblock, not a formality — see [[feedback_delegate_token_heavy_to_codex]].
