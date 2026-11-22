# Local kanban mirrors

Generated issue boards can contain private titles, labels and retained body
excerpts. They are local inputs to the optional kanban loader. They are not
publication artifacts. The publishing workflow has already been removed, and
the generated board tree is ignored by Git.

## Destination checks

Before fetching issues, reconciliation checks every manifest entry backed by
a repository, including domain boards. Each destination must stay inside the
kanban `boards` directory without following a symlink. Inside a Git checkout,
the destination must be ignored and absent from the index. Failure aborts
before any issue fetch or board write. These checks also apply to dry runs.

Standalone directories outside Git remain usable for local mirrors. Git
inspection errors fail closed. Inherited Git directory, worktree and index
bindings cannot select another checkout. The default root is anchored to the
script's checkout; use `--kanban-root` to select another local mirror explicitly.

The CLI reports counts by default. A local operator can request
the content diff with `--show-diff`. Such output may contain private content and
must stay in an appropriately restricted destination. Library callers that use
`ReconcileResult.diff` retain responsibility for that content. Existing size,
count-drift and unavailable-repository diagnostics still include board or
repository metadata, so command output still needs an appropriate audience.

## Worked example

Inputs: a synthetic repository `sample/repo`, a manifest entry targeting
`boards/repo-sample.yaml`, and one open issue with title `Synthetic task`.
The checkout's `.gitignore` contains `boards/` and the index contains no board.

Method: resolve the board destination, check containment and symlinks, check
index membership, then check Git ignore status. Only after those checks succeed
is the issue fetched and routed to its repository board.

Answer: the local board contains one issue card. The default command output is
`kanban reconcile: 1 board file(s) changed`, without the issue title. This count
is an independent enumeration of the single fixture input, not a calibrated
constant. `--dry-run` performs the same validation and reports the proposed
change without writing it. `--show-diff` explicitly requests the card text.
Removing the ignore rule or making the board tracked causes refusal before the
fetch; existing bytes remain intact. Tests exercise both outcomes.

## Scope and limits

This change prevents reconciliation from writing generated content to a
trackable destination. It does not prevent a later forced Git addition, another
publisher, concurrent filesystem changes, or disclosure by a library caller.
It does not inspect repository visibility or authorize publishing private data.
Authored boards without a repository remain preserved; their contents require
separate review. An existing authored path cannot become a generated destination
while it remains tracked.

Historical exposure is not removed by ignore rules or generator checks.
Restricted archival, review of retained authored material and any coordinated
history remediation require separate maintainer action. No files are deleted
and no history is rewritten here.

## Basis and checks

- Issue #3770 describes private issue mirroring and retained excerpts; issue
  #3768 describes publication through derived issue text.
- [Data handling contract](../architecture/agent-data-handling-contract.md),
  “Original retention, rights and publication”: local storage does not establish
  publication authority, and restricted payloads do not belong in public receipts.
- [Git ignore rules](../../.gitignore) define the existing local output boundary.
- Git's [check-ignore manual](https://git-scm.com/docs/git-check-ignore),
  “Exit status”, defines the ignored-path result. Its
  [ls-files manual](https://git-scm.com/docs/git-ls-files), “Description” and
  “Options”, defines index inspection. Both were accessed on 2026-10-22.
- `tests/test_kanban_publication.py` covers ignored, tracked, trackable,
  malformed and redirected destinations, dry runs and explicit diff output.

No engineering equations, empirical coefficients or acceptance limits apply.
