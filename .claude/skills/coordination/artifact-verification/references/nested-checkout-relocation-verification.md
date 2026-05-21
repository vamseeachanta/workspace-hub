# Nested Checkout Relocation / Duplicate Removal Verification

Use this reference when a worker claims to have moved, removed, or preserved a nested Git checkout under a parent repo (for example, converting `/parent/repo-name` into canonical sibling `/mnt/local-analysis/repo-name`).

## Durable verification pattern

Before accepting the worker result, independently verify both the source/nested and destination/sibling roles.

### Preflight before move/delete

For each involved checkout:

```bash
git -C "$path" remote get-url origin
git -C "$path" rev-parse HEAD
git -C "$path" rev-list --left-right --count HEAD...@{u}
git -C "$path" status --porcelain=v1
```

Required checks:

- Remotes point to the same canonical GitHub repo; tolerate `.git` suffix differences only after explicit comparison.
- HEAD SHAs match when deleting a duplicate checkout.
- Ahead/behind is `0 0` unless the plan explicitly includes preserving/pushing local commits.
- Dirty status is empty unless every dirty/untracked artifact has an explicit preservation path.
- Parent repo status for the nested path is empty/ignored-only if the nested directory is being removed from inside a parent checkout.

### Preserve artifacts before deletion

When the nested checkout contains untracked or dirty artifacts that are not in the primary checkout:

1. Copy only the intended relative paths into the primary checkout.
2. Verify byte identity before deleting the nested checkout:

```bash
cmp -s "$nested/$relpath" "$primary/$relpath"
```

3. Stage only those copied paths.
4. Commit/push in the destination repo if the artifacts need durable preservation.
5. Re-verify destination clean and `0 0` against upstream before deleting the source.

### Process/cwd guard

Before removing or moving a checkout, scan for processes with cwd under the source path:

```bash
found=0
for d in /proc/[0-9]*/cwd; do
  target=$(readlink "$d" 2>/dev/null || true)
  case "$target" in "$src"|"$src"/*)
    echo "${d%/cwd} $target"
    found=1
    ;;
  esac
done
[ "$found" -eq 0 ]
```

If stale language-server or type-checker processes hold cwd under an obsolete nested checkout, identify them with `ps` first and terminate only when they are clearly stale/non-user-interactive. Then repeat the cwd scan before `rm -rf` or `mv`.

### Post-action verification

After `rm -rf` or `mv`:

```bash
[ ! -e "$src" ]
[ -d "$dst/.git" ]
git -C "$dst" remote get-url origin
git -C "$dst" rev-parse HEAD
git -C "$dst" rev-list --left-right --count HEAD...@{u}
git -C "$dst" status --porcelain=v1
git -C "$parent" status --porcelain=v1 -- "$nested_name"
```

Report exact command output in the issue comment. Do not accept a worker's self-report without the orchestrator re-running the post-action checks.

## Delegated default-branch push pitfall

Some delegated agent harnesses may refuse `git push origin main` even when the dispatch prompt says to push, because default-branch pushes require explicit authorization/allowlisting inside that harness. Treat this as a governance guard, not a failure to bypass. The orchestrator can either:

- perform the push directly after verifying the exact commit and files, or
- redispatch with a scoped permission/allowlist if available.

Never claim preservation is complete until `git rev-list --left-right --count HEAD...@{u}` is `0 0` after the push.
