---
name: crossprovider codex ssh-without-n-in-a-stdin-loop-consumes-remaining
description: ssh without -n in a stdin loop consumes remaining targets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, probe-generators, stdin-hazard]
---

When probing a list of targets in a `while read` loop, `ssh` without the `-n` flag will consume the caller's stdin and break the loop iteration. This is a common footgun in reachability generators. The fix: always use `ssh -n` inside stdin loops, confirmed by test `test_reachability_ssh_probe_does_not_consume_stdin`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
