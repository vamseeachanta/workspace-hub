# Solver consolidation checkpoint

Initiative: https://github.com/vamseeachanta/workspace-hub/issues/3601

Report: `docs/reports/2026-09-12-solver-automation-consolidation.html`

## Verified state

- OrcaFlex integrity PR https://github.com/vamseeachanta/digitalmodel/pull/2099 is merged at `f7faaa969b678846a277e51cb755d6567fc26982`.
- Diffraction PR https://github.com/vamseeachanta/digitalmodel/pull/2106 was advanced from `b6d5ac02` to `f5f1bb20f6a5c9bba47b0b15e216a54b2e33c5bc`. RED `10dcd813`: 15 failed / 2 passed. GREEN `cf9ddc66`: 81 focused tests passed. Independent Codex review reran 17 new tests and approved only the bounded corrections. Legal scan passed. The remote head was read back successfully.
- Full PR clearance remains withheld: axisymmetric zero-diagonal physics, fresh CI and cross-provider review remain outstanding. No merge was performed.
- Nested policy nonfinite-input acceptance was reproduced without a solver and filed as https://github.com/vamseeachanta/digitalmodel/issues/2111, status needs-plan.
- ANSYS worktree branch `feat/issue-2094-example-deck-validation` remains clean at `0484af00`, five commits beyond current main. Remaining acceptance work and the extra AQWA-to-structural document need reconciliation.
- GHS PR https://github.com/vamseeachanta/digitalmodel/pull/2102 remains draft with native recovery and acceptance outstanding.

## Fleet and cleanup

Four of seven registered machines were inspected directly: ace-win-1 locally and ace-linux-1, ace-linux-2, gpu-claw through SSH. The secondary Windows host responded but rejected authentication. The registered MacBook and shoerack names did not resolve. Historical secondary-host findings cannot substitute for live inventory.

Two worktrees, `digitalmodel-1565` and `digitalmodel-1594-base`, were moved using Git worktree management from the active worktree directory into a dated quarantine under the workspace parent. Their original HEADs, clean state and absence from the original paths were read back. Branches were preserved. See `docs/reports/2026-09-12-solver-quarantine-manifest.json` for exact local paths.

Independent review approved reversible quarantine only. Process working directories/open handles remain unestablished; permanent deletion is not authorized by the verification manifest. The first worktree contains an empty UV environment in addition to caches. No candidate dependency reference was found in the reviewed editable-install metadata.

Expected preserved residue: active FOUNDATION modifications and lock; original comparison worktree's 26 generated tracked modifications; baseline and closeout test logs; ANSYS branch; editable dependency chain for the campaign worktrees; active remote CFD work; the new correction worktree; quarantined worktrees. No unrelated dirty content was staged into the correction commits.

## Next checkpoint

1. Resolve or explicitly scope the axisymmetric zero-diagonal finding, complete required cross-provider review and inspect fresh PR CI before requesting the exact merge authorization.
2. Recover authenticated secondary-host access and read back its local branches, worktrees and handoffs. Do not revive its licensed-run agent merely to obtain access.
3. Complete per-target remote cleanup evidence and process/open-handle checks before any further quarantine or deletion.
4. Reconcile ANSYS acceptance evidence and licensed-routing issue https://github.com/vamseeachanta/deckhand/issues/579. Keep exact native-run approvals separate from software preparation.

No native solve, queue submission, credential change, task cutover, merge or permanent deletion occurred. First-seen SSH host keys were recorded using accept-new with existing login identities. The issue received the implementation checkpoint comment. The parent consolidation lock will be released at handoff.

## Known evidence limitations

The named agent-data-handling contract file is absent locally and on queried main. Existing data-layer contracts and the source/domain indexes were consulted; no engineering dataset was transformed or promoted. The repository-specific legal-scanner resolver returned an empty scan directory; that invocation was rejected as evidence. Root scanning and exact isolated-root scanning were used successfully instead.

Report review returned MINOR for incomplete nested-policy context and an inactivity overstatement; both report findings were corrected inline. This remains Codex-provider review evidence, not cross-provider consensus.
