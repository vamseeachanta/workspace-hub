# Line-ending-only dirty working trees during repo sync

Use this when a repository is otherwise synced with upstream (`ahead=0`, `behind=0`) but `git status` shows many tracked modified files.

## Diagnosis

Run both shortstats from the repository root:

```bash
git diff --shortstat
git diff --ignore-space-at-eol --shortstat
```

Interpretation:

- Normal shortstat is large, but `--ignore-space-at-eol` prints nothing: likely CRLF/LF line-ending churn only.
- Both shortstats show changes: there are substantive local edits; treat as a normal dirty tree.

Optional context probes:

```bash
git config --get core.autocrlf || true
git config --get core.eol || true
git diff --name-status | head -50
```

## Safe sync behavior

If the repo has no upstream divergence (`ahead=0`, `behind=0`), line-ending-only churn is not a remote sync blocker. Report it separately from synced/unsynced state.

Do **not** automatically run any of the following without explicit user approval:

- `git checkout -- .`
- `git restore .`
- mass normalization commits
- stash/pop cycles intended only to hide the churn
- `.gitattributes` changes that normalize the repo globally

Line-ending changes can touch many files and obscure real work, so they should be an explicit cleanup task.

## Reporting pattern

Use wording like:

> Repo is remote-synced (`ahead=0`, `behind=0`) but has tracked local modifications. The diff disappears with `git diff --ignore-space-at-eol --shortstat`, so this appears to be line-ending-only churn. I did not discard or normalize it without approval.

## When to escalate

Ask for explicit approval before normalizing if the user wants the repo clean. A good follow-up plan is:

1. Add or verify `.gitattributes` line-ending policy.
2. Run normalization in a dedicated commit.
3. Re-run `git diff --check` and project tests/linters if available.
4. Push the normalization commit only after review.
