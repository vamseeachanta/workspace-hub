---
title: "Shell Scripting Patterns"
tags: [software, scripting, bash, flock, atomic-writes, idempotency]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# Shell Scripting Patterns

Robust shell scripting patterns for production scripts: atomic file writes, concurrent-write
protection with flock, idempotency, and defensive coding practices.

## Core Patterns

### Atomic File Writes

Write to a temporary file then `mv` — `mv` is atomic on the same filesystem, preventing
partial reads by concurrent processes.

### Flock for Concurrent-Write Protection

```
exec FD>lockfile
flock -w N FD
# ... critical section ...
flock -u FD
```

Used for shared JSONL files and any append-only data store.

### Idempotency

- Idempotency checks must be inside the lock section to avoid race conditions
- Check-then-append must be within same flock to prevent duplicate writes

## Defensive Coding Rules

| Rule | Rationale |
|------|-----------|
| `set -euo pipefail` at top | Fail on errors, unset vars, pipe failures |
| `$()` over backticks | Nesting support, readability |
| Double-quote all variables | Prevent word splitting and globbing |
| `shellcheck` enforcement | Catches most of the above automatically |

## Best-Effort Hooks

- Always end with `|| true` so parent process never fails
- Exit 0 on all error paths for hooks that must not block callers

## Design Patterns

- Atomic write: write to .tmp then mv — mv is atomic on same filesystem
- Flock pattern: exec FD>lockfile; flock -w N FD; ... ; flock -u FD
- Idempotency inside lock: check-then-append must be within same flock
- Best-effort hooks: always end with || true so parent process never fails
