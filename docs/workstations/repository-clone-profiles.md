# Explicit repository clone profiles

`scripts/repository_sync clone` can opt into a new-destination profile. The
existing profile-less command retains its existing behavior. Profile execution
does not convert, update or replace existing checkouts.

The profile path uses `config/repos.conf` for URLs and
`config/workstations/registry.yaml` for
`machines.<machine>.tier1_baseline.required` membership. Its default machine is
`dev-primary`, whose required set is workspace-hub, digitalmodel, assetutilities,
worldenergydata, llm-wiki and assethold. It accepts one named member per invocation;
`all`, `work`, `personal`, unknown members and missing URL entries fail explicitly.
The current URL config contains four of these six: workspace-hub and llm-wiki
have no entry. For an absent URL, `--url-source-checkout` can explicitly resolve the
origin from an existing local checkout. It reads only bounded direct Git metadata,
rejects redirects and credential-bearing URLs, and requires the repository name
to match. It never follows config includes or overrides an existing `repos.conf`
mapping. The receipt records the origin configuration path. This URL observation
does not establish new core membership, a deployment profile, access or runtime readiness.
Use an existing Python environment with PyYAML. Set `REPOSITORY_SYNC_PYTHON` to its
interpreter when the default `python3` is unsuitable. No dependency installation
or environment hydration is attempted. For example, with a task-owned Windows root:

```powershell
$env:REPOSITORY_SYNC_PYTHON='C:/existing-core/workspace-hub/.venv/Scripts/python.exe'
& 'C:/Program Files/Git/bin/bash.exe' scripts/repository_sync clone digitalmodel --profile lean --destination C:/new-core/digitalmodel --include-dir src --include-dir tests/unit --dry-run
& 'C:/Program Files/Git/bin/bash.exe' scripts/repository_sync clone workspace-hub --profile lean --destination C:/new-core/workspace-hub --include-dir scripts --url-source-checkout C:/existing-core/workspace-hub --dry-run
& 'C:/Program Files/Git/bin/bash.exe' scripts/repository_sync clone llm-wiki --profile lean --destination C:/new-core/llm-wiki --include-dir scripts --url-source-checkout C:/existing-core/llm-wiki --dry-run
```

`C:/new-core` must already exist without symlink/reparse components. The destination
must not exist, including an empty directory, file or dangling link, and its
basename must equal the selected repository. Dry-run reads local configuration
and emits a JSON command plan; it does not call Git, create directories or import
bytecode. Remove `--dry-run` only for an authorized clone. `--branch` defaults to
`main`; `--machine` chooses an existing machine baseline with a nonempty required set.

Lean requires explicit `--include-dir` entries (at most twenty relative directory
paths). Hidden workflow directories such as `.agents`, `.codex` and `.claude`
are accepted explicitly; `.git` is rejected case-insensitively at every path
component. Hidden-directory support does not relax branch validation. It checks
remote filter capability, requests a depth-one, single-branch,
blob-filtered clone without checkout, verifies the promisor configuration/store,
and checks that each selected path is a tree without lazy fetching. It then applies
cone sparse checkout and materializes the selected source. Cone mode also includes
root files and ancestor files. `blob:none` is a request, not a network byte cap:
if capability changes between preflight and clone, ignored filtering can transfer
objects before the tool rejects the result. Later pilots need an approved,
known-capable source and measured receipts.

Heavy accepts no sparse entries. It explicitly downloads the full single-branch
object history and leaves the checkout unmaterialized. It is for a separately
authorized heavy working store; it is not a lean-budget success. Both profiles
disable LFS smudge and submodule recursion. Neither downloads task datasets,
installs dependencies or runs solvers.

Git child environments isolate inherited Git bindings, global/system configuration,
hooks and templates. Existing SSH identity configuration remains available through
the SSH transport; global Git HTTPS credential helpers are not loaded. Authentication
failure is reported without changing credentials, permissions or configuration.

Failed, rejected or timed-out new destinations are retained; no unfiltered retry,
replacement or automatic cleanup occurs. Parent/target identity is checked between
steps. These are cooperative checks, not a hostile concurrent-filesystem guarantee.

After an authorized pilot, use the existing checker to observe the complete required
set, including absent members, Git stores and dependency bytes:

```bash
python3 scripts/workstations/check-tier1-repo-baseline.py --footprint-only --machine dev-primary --repo-root /new-core --budget-bytes 3000000000
```

Missing members, redirects, read errors or unsupported allocation reporting make
the budget indeterminate. A footprint receipt does not establish runtime readiness.
Verify task source, sibling dependencies, pinned revision and only named fixtures
separately. Keep heavy data/results in their existing owners and stores.

Windows footprint allocation uses metadata-only handles and
`FileStandardInfo.AllocationSize`, including NTFS cluster rounding, sparse and
compressed allocation. Handle identity and repeated metadata queries reject
observed replacements/changes; paths and directories are checked for redirects
and observed mutations. This remains a sequential observation of quiescent
files, not an atomic or hostile-filesystem snapshot. The checker never flushes
or modifies user files. Unknown allocation or detected changes keep the budget
indeterminate; observed lower bounds remain visible. POSIX retains `st_blocks`.

Environments under selected checkout roots are included. External environments
are excluded unless explicitly supplied with repeatable absolute
`--footprint-environment /path/to/environment`. Explicit environments share the
same inode deduplication as checkout/Git scans; missing or redirected paths make
the receipt incomplete. The receipt records this inclusion/exclusion policy.
For a complete runtime budget, explicitly account for each shared environment;
no environment is installed, inspected by execution, or automatically discovered.
Filesystem directory metadata and other volume overhead are outside file-allocation
totals. Git common stores, worktree administration, LFS/recovery sidecars and
external private Git directories are included once; alternate stores remain an
explicit incomplete-coverage condition.
Allocation can lag unflushed writes even when repeated metadata queries agree.
The read-only checker deliberately does not flush existing files. A fresh pilot
must establish settled writes in its task-owned targets before a physical-budget
claim, and retain/review uncertain measurements rather than extrapolate logical
size. This is separate from runtime readiness and filesystem-wide overhead.
