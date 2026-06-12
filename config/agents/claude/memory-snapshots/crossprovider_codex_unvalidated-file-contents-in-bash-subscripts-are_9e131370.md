---
name: crossprovider codex unvalidated-file-contents-in-bash-subscripts-are
description: Unvalidated file contents in bash subscripts are a shell-injection risk
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, security, input-validation]
---

Never use file contents directly as associative-array subscripts or in variable expansions without validation. Bash evaluates subscripts, so malformed or crafted content can trigger command substitution. Validate with regex (e.g., `[[ $sentinel_id =~ ^WRK-[0-9]+$ ]]`) before any array lookup. WRK-1042 had this.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
