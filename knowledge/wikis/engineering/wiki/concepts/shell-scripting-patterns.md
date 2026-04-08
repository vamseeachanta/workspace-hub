---
title: "Shell Scripting Patterns"
tags: [shell, bash, scripting, flock, atomic-writes, idempotency]
sources: [career-learnings-seed]
added: 2026-04-08
last_updated: 2026-04-08
---

# Shell Scripting Patterns

Robust shell scripting patterns for production scripts, cron jobs, and git hooks.

## Script Preamble

Every script should start with strict mode:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

| Flag | Effect |
|------|--------|
| `-e` | Exit on first error |
| `-u` | Treat unset variables as errors |
| `-o pipefail` | Pipe fails if any stage fails (not just last) |

## Atomic File Writes

Write to a temporary file, then `mv` into place. On the same filesystem, `mv` is atomic -- readers never see a half-written file.

```bash
tmp="$(mktemp "${target}.tmp.XXXXXX")"
# ... write to "$tmp" ...
mv -- "$tmp" "$target"
```

If the script exits before `mv`, the `.tmp` file is harmless and can be cleaned up by a separate sweep. Never write directly to the target file in a concurrent environment.

## Flock for Concurrent-Write Protection

Use `flock` when multiple processes may write the same file (cron overlap, parallel agents):

```bash
exec 9>"${lockfile}"
flock -w 30 9        # wait up to 30s for exclusive lock
# ... critical section ...
flock -u 9           # release (also released on FD close / script exit)
```

**Key rule:** the check-then-append pattern must happen entirely inside the same flock. If you check outside the lock and append inside, another process can insert between the check and the append, causing duplicates or corruption.

```bash
# WRONG -- check outside lock
if ! grep -q "$entry" "$file"; then
  flock -w 10 9
  echo "$entry" >> "$file"    # race: another process may have added it
  flock -u 9
fi

# RIGHT -- check + append inside lock
flock -w 10 9
if ! grep -q "$entry" "$file"; then
  echo "$entry" >> "$file"
fi
flock -u 9
```

## Best-Effort Hooks

Git hooks and cron-triggered helpers should never block the parent operation. End with `|| true`:

```bash
# In a pre-commit hook or cron wrapper
/usr/local/bin/optional-linter "$@" || true
```

This ensures a flaky linter or network timeout does not prevent commits or break cron chains.

## Quoting and Substitution

- Always use `$()` over backticks -- nesting is cleaner and less error-prone.
- Double-quote all variable expansions: `"$var"`, `"${arr[@]}"`, `"$(cmd)"`.
- Unquoted expansions cause word splitting and glob expansion bugs that are difficult to reproduce.

```bash
# WRONG
files=`ls $dir`

# RIGHT
files=$(ls "$dir")
```

## ShellCheck

[ShellCheck](https://www.shellcheck.net/) enforces most of the patterns above automatically. Run it in CI or as a pre-commit hook:

```bash
shellcheck -x scripts/*.sh
```

Use `# shellcheck disable=SC2059` inline only when you understand why the warning is inapplicable.

## awk: mawk vs gawk

| Feature | mawk | gawk |
|---------|------|------|
| `match($0, /regex/, arr)` with capture groups | Not supported | Supported |
| Speed on large files | Faster | Slower |
| Availability | Default on Debian/Ubuntu | Must install separately |

For portable scripts, avoid `match()` with the third argument. Instead, use `index()` + `substr()` + `sub()` to extract fields from matched strings.

### Portable JSON Field Extraction (No Capture Groups)

```awk
# Extract value for key "name" from a JSON line (no jq dependency)
{
  pos = index($0, "\"name\":")
  if (pos > 0) {
    rest = substr($0, pos + 7)
    sub(/^[[:space:]]*"/, "", rest)
    sub(/".*/, "", rest)
    print rest
  }
}
```

## sed and Symlinks

`sed -i` follows symlinks and replaces the symlink with a regular file. If a config file is a symlink (common in dotfile managers), `sed -i` silently breaks the link.

Workaround:

```bash
# Preserve symlink by writing to the resolved target
sed -i "s/old/new/" "$(readlink -f "$symlink")"
```

Or use the atomic tmp+mv pattern and recreate the symlink.

## Related Pages

- [JSONL Knowledge Stores](jsonl-knowledge-stores.md) -- uses flock and atomic writes for append-only stores
- [Python Type Safety](python-type-safety.md) -- subprocess.run patterns called from shell
- [Test-Driven Development](test-driven-development.md) -- testing shell scripts with bats or shunit2
