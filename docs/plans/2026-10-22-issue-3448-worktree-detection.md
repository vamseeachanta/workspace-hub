# Plan for #3448: linked worktree repository detection

Status: draft. Complexity: medium. Implementation scope follows the maintainer's
current task direction; the issue's original planning-only scope will not be
treated as implementation authority.

## Resource intelligence summary

- Issue #3448 describes directory-only detection rejecting linked worktrees.
- Related digitalmodel issue #662 is closed and describes the geometry bridge;
  it supplies provenance, rather than a repository-detection specification.
- `config/tier1-python-repos.txt` supplies the Python-tooling repository set.
  `config/workstations/registry.yaml` also identifies the required wiki and hub.
- `scripts/lib/tier1_repos.py` and `scripts/lib/tier1-repos.sh` currently accept
  a `.git` directory or `pyproject.toml`; the latter is an intentional source
  export fallback that will remain available.
- `scripts/search/build_content_index.py:is_repo_root` accepts only directories.
- Git's [repository layout](https://git-scm.com/docs/gitrepository-layout)
  describes a `.git` text file pointing to repository metadata. Its
  [rev-parse reference](https://git-scm.com/docs/git-rev-parse), options
  `--is-inside-work-tree`, `--show-prefix`, and `--local-env-vars`, defines the
  proposed detection and environment-isolation pattern. Both public references
  were retrieved successfully on 2026-10-22. No engineering constants or
  equations will be introduced.

### Evidence and gaps

The initial worktree is clean and its revision equals the base reference.
The live required set contains working trees for workspace-hub, digitalmodel,
assetutilities, worldenergydata and assethold. The expected llm-wiki checkout
is unavailable. The hub is a linked worktree; the other observed repositories
are primary checkouts. Only tracked script files will be inventoried; absent
repositories and other languages will remain explicit coverage gaps.

## Deliverable and artifact map

| Slice | Files | Intended result |
| --- | --- | --- |
| 1 | `docs/reports/2026-10-22-worktree-detection-audit.md` | Enumerate observed repositories and classify candidate predicates with follow-up dispositions. |
| 2 | `scripts/lib/git_worktree.py`, `scripts/lib/tier1_repos.py`, `scripts/lib/tier1-repos.sh` | Share a Git-backed working-tree root predicate and use equivalent shell semantics in tier-1 resolution. |
| 3 | `scripts/search/build_content_index.py`, focused quality tests and existing resolver fixtures | Apply the predicate to content indexing, demonstrate real linked worktrees, and preserve existing consumer contracts. |

This document will carry the proportionate plan, test design and review notes.
The audit will carry the worked example and migration guidance. Sibling
repository files will remain read-only.

## Pseudocode

```text
is_git_worktree_root(candidate):
    require candidate directory with a .git marker
    ask Git for repository-local environment variable names
    remove those bindings in the probe child only
    ask Git whether candidate is inside a working tree and for its prefix
    accept successful true response with empty prefix

resolve_tier1_repo_path(slug):
    preserve explicit-base, nested, sibling precedence and duplicate warning
    validate candidates with .git metadata using the root predicate
    otherwise retain the pyproject.toml source-export fallback
```

## TDD test list and acceptance criteria

Expected booleans will follow Git's documented semantics and fixtures made by
Git itself. Expected resolver paths will follow the existing probe order.

| Case | Expected result and independent basis |
| --- | --- |
| Primary checkout, linked worktree, separate Git directory | Accept root; Git creates these supported layouts. |
| Bare repository, missing path, ordinary directory, nested directory | Reject; none is a working-tree root with valid metadata. |
| Malformed gitfile, empty metadata directory, dangling marker | Reject; presence alone cannot establish a valid repository. |
| Inherited repository-local Git variables | Probe the requested candidate and preserve the caller's environment. |
| Source export with pyproject only | Preserve the existing resolver fallback. |
| Git metadata present but invalid, even with pyproject | Reject rather than mask invalid metadata with the fallback. |
| Explicit base and duplicate layouts | Preserve precedence and diagnostics in both implementations. |
| Direct content-index invocation outside the hub | Index the linked worktree and preserve the raw-inventory banner. |

Tests will be written and run before implementation, then repeated after the
correction. Existing tests for every changed module and relevant shell consumers
will run. Ruff will check touched Python files; shell syntax, diff whitespace,
file-size, ignore, LFS and public-text checks will cover the final change.

## Adversarial plan review

Self-review identified ancestor discovery, inherited Git bindings, malformed
markers, and source-export compatibility as failure cases. The predicate will
therefore require a marker and an empty root prefix, isolate all Git-reported
local bindings, and distinguish absent metadata from invalid metadata.

Directory-only predicates in destructive cleanup and isolated-clone dispatch
will not be mechanically replaced: changing their root-selection semantics
could change the safety boundary. Independent provider review remains a required
follow-up before merge and will not be represented as completed here.

## Risks and later slices

- The audit will classify literal predicates in tracked shell, Python and
  PowerShell scripts. Dynamic predicates and code outside that search boundary
  will not be claimed as covered.
- Remaining discovery predicates will be listed with their locations for
  consumer-specific regression tests and migration.
- Primary-clone and private bootstrap restrictions will require their own
  security review before any behavioral change.
- Git ownership/configuration errors will fail closed. The helpers will not
  override trust configuration or authenticate a repository's remote identity.
