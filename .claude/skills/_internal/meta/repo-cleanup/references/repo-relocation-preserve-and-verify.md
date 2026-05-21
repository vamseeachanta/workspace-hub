# Repository Relocation: Preserve Existing Destinations and Verify Before Source Removal

Use this pattern when moving whole git repositories between workspace roots, especially to storage mounts such as `/mnt/ace` where partial/preexisting directories may already exist and large trees may exceed foreground tool timeouts.

## Pattern

1. Preflight every requested repo:
   - source exists and is a git repo: `/source-root/<repo>/.git`
   - destination state: absent, git repo, or non-git/preexisting directory
   - destination root exists and is writable
2. If `/dest-root/<repo>` already exists, do not overwrite or merge blindly. Rename it first:
   - `/dest-root/<repo>.preexisting-before-repo-move-<timestamp>`
3. For normal-sized repos, `mv /source-root/<repo> /dest-root/<repo>` is acceptable after preflight.
4. For large repos or timeout-prone moves, use a copy-then-delete pattern:
   - `rsync -a --delete /source-root/<repo>/ /dest-root/<repo>/`
   - verify git identity, at minimum `git -C source rev-parse HEAD` equals `git -C dest rev-parse HEAD`
   - only then remove source with `rm -rf --one-file-system /source-root/<repo>`
5. For long `rsync` runs, launch as a tracked background process with completion notification rather than repeating foreground calls that time out.
6. Keep a move log under the destination root recording source, destination, preserved preexisting paths, verification output, and final status.

## Verification checklist

For each repo, report:

```text
<repo> src=gone|exists dst=git|non-git|absent head=<short-sha|no-git>
```

A move is not complete until:

- source is gone, or explicitly preserved because verification failed
- destination is a git repo
- destination HEAD matches the source HEAD captured before deletion
- any preexisting destination was renamed, not deleted

## Pitfalls

- A preexisting destination can be a partial old copy, a non-git data directory, or a different checkout. Preserve it first; do not assume it is disposable.
- `mv` or `rsync` can exceed foreground tool limits on large repos. The durable lesson is to resume with tracked `rsync` and verify before source removal, not to declare failure.
- Avoid expensive recursive status/du checks on huge repos during preflight; use shallow indicators first (`stat`, `.git`, `rev-parse HEAD`).
