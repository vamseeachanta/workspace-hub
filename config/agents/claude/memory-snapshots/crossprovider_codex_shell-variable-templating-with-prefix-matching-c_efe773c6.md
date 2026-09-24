---
name: crossprovider codex shell-variable-templating-with-prefix-matching-c
description: Shell variable templating with prefix matching corrupts related variables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, templating, bug-class]
---

Using raw string replacement like `.replace("$LOG", value)` in templating will corrupt any variables that start with that prefix (e.g., `$LOGDIR` becomes `/tmp/workspace-hubDIR`). Use boundary-aware matching: exact `${VAR}` / `$VAR` forms only, surrounded by non-alphanumeric characters, or use shell parameter expansion syntax.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
