# Cross-Review: WRK-1064 Plan (Stage 6 — Claude; codex gate deferred for Route A)
Verdict: MAJOR

## Findings

- [MAJOR] New-remote-branch push (remote_oid = all zeros) not handled.
  When pushing a branch that does not yet exist on the remote, `remote_oid` is all zeros.
  `git diff --name-only <remote_oid>..<local_oid>` cannot resolve an all-zeros SHA and
  exits non-zero. With `set -euo pipefail` in the hook, this blocks every first push to
  any new remote branch.
  Recommendation: Guard before the diff — if remote_oid is all zeros (new branch),
  fall back to `--all` mode:
  `[[ "$remote_oid" == "0000000000000000000000000000000000000000" ]] && run_all=true`

- [MINOR] Submodule `.git` entry is a file, not a directory.
  In a workspace-hub checkout, each submodule's `.git` is typically a file
  (`gitdir: ../.git/modules/<name>`) rather than a directory; `<sub>/.git/hooks/`
  does not exist as a path. install-hooks.sh will silently fail.
  Recommendation: Resolve hooks dir via:
  `git -C "$sub_path" rev-parse --git-dir` → append `/hooks`

- [MINOR] `logs/hooks/` directory does not exist.
  Bare append to `logs/hooks/pre-push-bypass.jsonl` will fail if the directory is absent
  under `set -euo pipefail`.
  Recommendation: Add `mkdir -p "$(dirname "$BYPASS_LOG")"` before the append;
  create `logs/hooks/.gitkeep` in the implementation.

- [MINOR] Bypass JSONL schema not specified.
  The plan says to log bypass but does not define the record fields.
  Recommendation: Schema: `{"timestamp":"<ISO8601>","local_ref":"...","local_oid":"...",
  "remote_ref":"...","remote_oid":"...","operator":"GIT_PRE_PUSH_SKIP","exit_code":0}`

## Summary

One blocking correctness bug: the all-zeros `remote_oid` case (new remote branch) causes
`git diff` to fail under `set -euo pipefail`, blocking every first push to a new branch.
Three minor issues (submodule hooks path resolution, missing log dir, undefined JSONL schema)
should also be addressed in the implementation.
