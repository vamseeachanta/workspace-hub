---
name: crossprovider hermes shell-script-append-anti-pattern-creates-unreach
description: Shell script append anti-pattern: creates unreachable code after terminal exits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-scripting, git-hooks, anti-pattern]
---

Blind append to scripts that already have `exit $X` leaves appended code unreachable. install-hooks.sh appended stage-prompt-drift after pre-push's final exit; code never runs. Fix: structural insertion (before exit blocks) rather than append. Make idempotent by checking for existing blocks before inserting.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
