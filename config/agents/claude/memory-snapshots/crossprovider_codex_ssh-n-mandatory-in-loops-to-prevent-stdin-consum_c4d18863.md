---
name: crossprovider codex ssh-n-mandatory-in-loops-to-prevent-stdin-consum
description: ssh -n mandatory in loops to prevent stdin consumption
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [ssh, loops, stdin, automation, probe-safety]
---

ssh without -n consumes stdin and eats remaining lines in a while-read loop. ssh -n is required inside pipe/loop contexts. Covered by test_reachability_ssh_probe_does_not_consume_stdin.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
