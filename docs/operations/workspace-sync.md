# Portable repository synchronization

The helper in `scripts/operations/ws.py` provides status, guarded synchronization,
and read-only workspace and tooling inspection for
issue 3880.
It uses the Python standard library and Git. Python 3.9 or newer is required
because the implementation uses `str.removeprefix`.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add explicit repository synchronization and inspection to support consistent checkout layouts. |

Table 1. Guide revisions.

## Commands

Run from a repository root, or select a repository with `--repo`. A directory
inside a working tree is also supported, including linked Git worktrees.

```console
python3 scripts/operations/ws.py status
python3 scripts/operations/ws.py pull
python3 scripts/operations/ws.py push
python3 scripts/operations/ws.py doctor
python3 scripts/operations/ws.py inventory --root WORKSPACE --expect alpha beta
```

To expose the short `ws` command, set `WS_HELPER` locally to the absolute
location of this script. In a POSIX shell, define:

```sh
ws() { python3 "$WS_HELPER" "$@"; }
```

In PowerShell, set the environment variable `WS_HELPER` to that script location
and define:

```powershell
function ws { py -3 $env:WS_HELPER @args }
```

These optional wrappers select the same implementation from any working
directory. They are local shell settings; no profile is modified by the helper.

On Windows, use the installed Python launcher, for example `py -3`, in place of
`python3`. The same Python file is used on each platform. Executable discovery
reports the literal baseline tool names, including `python3`: another Python
launcher does not silently satisfy that name.

| Command | Result and criterion |
| --- | --- |
| `status` | JSON branch, dirty flag, upstream presence and local ahead/behind counts; no network request. |
| `pull` | Pull the existing upstream with fast-forward-only integration and no rebase; refusal leaves local commits unchanged. A fetch can update tracking refs even when integration is refused. |
| `push` | Push only HEAD to its configured upstream branch, without force or automatic tag following. Both the source and destination are checked against `main` and `master`. |
| `doctor` | Report executable presence for git, gh, node, python3, claude and codex without starting them. Tool versions and authentication remain unevaluated. |
| `inventory` | Inspect immediate nonhidden directories, including linked worktrees, against explicitly supplied repository folder names. No root or repository set is inferred. |

Table 2. Operations and their evidence boundaries.

`status` reports success when inspection succeeds, including dirty or detached
repositories. Missing tracking information is JSON `null`, rather than a zero
count. An unborn branch can therefore be inspected. Ahead/behind counts refer
to local tracking refs and do not establish current remote state.

Synchronization refuses uncommitted tracked, staged or untracked changes,
detached HEAD, absent upstreams, local-branch upstreams and unfinished merge,
rebase, cherry-pick or revert operations. Ignored files are left in place; Git
still enforces its overwrite checks. A push uses an explicit refspec so a
configured push default cannot select additional branches. Submodule recursion
is disabled. No commit, stash, reset, clone, installation or automatic recovery
is performed. Repository hooks retain their normal behavior. Review the
upstream and remote configuration before authorizing a synchronization command.

Errors omit raw Git output because it can expose private paths, remote addresses
or credentials. Inspect detailed failures locally in the selected repository.
Git failures return a nonzero exit status. `doctor` returns nonzero when a tool
is missing; presence is not a version or operational readiness check.

`inventory` lists repositories, unmanaged directories, invalid Git markers and
excluded symbolic links separately. Hidden entries and ordinary files are not
inventoried. A supplied expected set qualifies folder-name equality only;
`ready` is true when no expected repository is missing, no extra repository is
found, and no candidate is unverified. Unmanaged directories and excluded links
are reported but do not belong to the repository-set comparison. Without an
expected set, `ready` is `null` and the criterion is `not-supplied`. Symlinked
repositories are excluded to avoid traversing another workspace. Inspection
neither moves nor deletes entries, and does not establish remote identity,
authentication, matching versions or matching content across machines.

## Worked example: independently constructed commit graphs

Input: two repositories track the same branch at commit A. A local child B is
created in the first repository. The graph is:

```text
local:     A -- B
tracking:  A
```

Method: count commits reachable only from local HEAD for `ahead`, and commits
reachable only from the tracking ref for `behind`, using Git's symmetric
commit difference. The sets are `{B}` and the empty set. The answer is
`ahead = 1`, `behind = 0`. These counts are derived from the drawn graph.
After a successful push and tracking update, both tips are B and both counts
are zero. The helper does not manufacture a commit from dirty files.

For a divergent case, the second repository publishes another child C of A:

```text
local:     A -- B
tracking:  A -- C
```

The local-only and tracking-only sets are `{B}` and `{C}`. Each count is one.
`pull` fetches the upstream but refuses integration because neither child is an
ancestor of the other. Local HEAD stays B. The maintainers can then review the
histories and select a separate integration procedure.

The tests construct these graphs using independent Git fixture operations and
assert literal expected counts and commit identity preservation. Additional
cases cover dirty and staged changes, upstream selection, protected branches,
non-fast-forward pushes, configured tag following, linked worktrees, repository
environment isolation, missing tools, and layout qualification.

For a layout example, take immediate checkout folders `alpha` and `beta`, plus
an ordinary `artifacts` directory. With `--expect alpha beta`, the repository set
matches, `ready` is true, and `artifacts` is reported as unmanaged. Adding
`gamma` to the expected set produces `missing = ["gamma"]` and `ready = false`.
This example does not prescribe a new storage root.

## Sources and limits

The following upstream Git manuals were opened successfully on 2026-10-22:

- [git-rev-list](https://git-scm.com/docs/git-rev-list), symmetric difference,
  `--left-right` and `--count`: basis for the worked counts.
- [git-pull](https://git-scm.com/docs/git-pull), `--ff-only` and `--no-rebase`:
  basis for refusing divergent integration.
- [git-push](https://git-scm.com/docs/git-push), refspecs, fast-forward checks and
  `--no-follow-tags`: basis for the explicit destination and tag behavior.

No engineering equations, empirical coefficients or physical acceptance limits
apply to this utility. Protected branch names are a local workflow policy,
not a universal list of protected branches; server-side protections still apply.
Tests use local disposable repositories and do not authenticate to a service.
Linux execution is tested; Windows and macOS execution remain unverified.

## Remaining rollout

The helper, inspection and worked example are three implementation slices of
issue 3880.
The following issue outcomes remain unestablished and require separate access
or maintainer decisions:

- Determine the in-scope machines, authoritative checkout roots and expected
  repository set before asserting coverage or moving any checkout.
- Survey each authorized machine and record repository names, remote identity,
  dirty state, tool versions and available authentication locally.
- Review uncommitted work before publication, establish backups before moves,
  and select a declutter layout for checkouts, worktrees and generated artifacts.
- Install missing tools and clone missing repositories only with matching access.
- Run the same inventory criterion on every in-scope machine and compare actual
  version observations; tool presence alone cannot satisfy version equality.

No machine migration, bulk clone, tool installation or remote repository change
is part of this implementation. The existing Bash synchronization scripts are
unchanged; adoption of this helper is explicit.
