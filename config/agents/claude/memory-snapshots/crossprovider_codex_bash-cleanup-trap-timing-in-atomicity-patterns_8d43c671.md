---
name: crossprovider codex bash-cleanup-trap-timing-in-atomicity-patterns
description: Bash cleanup trap timing in atomicity patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, atomicity, error-handling]
---

When implementing pre-validate-then-write patterns with cleanup traps, the trap must remain armed through ALL mutation phases, not disarmed early. Disarming before final writes (e.g., parent frontmatter update, YAML rewrite) leaves orphan files and partial state on failure. WRK-1130 showed multiple rounds of fixing this.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
