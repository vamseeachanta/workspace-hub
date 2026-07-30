# #3511 code review — Windows scheduler lane

**Reviewer stance:** adversarial, read-only  
**Initial verdict:** MAJOR — do not approve  
**Disposition:** execution and rollback blockers were patched inline; pre-existing file-size/test-isolation debt was promoted to #3539.

## Findings and disposition

1. **MAJOR:** registrar and wrapper used different Git Bash discovery sets. Fixed by passing the registrar's verified `GitBashPath` and `WorkspaceRoot` into the scheduled wrapper action.
2. **MAJOR:** wrapper accepted `WorkspaceRoot` but did not enter it, allowing manual runs to fingerprint the caller's repository. Fixed with `Set-Location -LiteralPath $WorkspaceRoot`; wrapper-path test pins the behavior.
3. **MAJOR:** uv-only resolution unset the legacy scalar `$PYTHON`. Fixed with a scalar shell wrapper backed by the resolved uv command; uv-only legacy-call regression test added.
4. **MAJOR:** removal could mutate earlier tasks and fail on late identity/YAML/action validation. Fixed with an early identity/YAML-independent removal transaction; WhatIf removal proves all four equivalence tasks are addressed without scheduler queries.
5. **MAJOR:** pre-existing oversized equality files and non-hermetic Windows collector tests remain outside the bounded sentinel fix. Promoted to [#3539](https://github.com/vamseeachanta/workspace-hub/issues/3539) with exact line counts and baseline reproductions.
6. **Cleanup:** a one-byte mangled test residue was removed from the worktree root.

## Verification

- Windows scheduler suite: included in the 78-test focused pass.
- PowerShell parser: all changed/new scheduler files parse.
- WhatIf renders daily 05:15 reconcile and six-hour minute-17 sentinel for both Windows identities.
- Live audit remains mutation-free: daily reconcile, sentinel, and curation tasks are currently absent; EqualityReport exists but last result is 1.

