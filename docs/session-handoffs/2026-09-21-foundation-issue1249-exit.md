# FOUNDATION exit handoff — 2026-09-21

Owner: FOUNDATION. Scope: [issue 1249](https://github.com/vamseeachanta/workspace-hub/issues/1249), approved hub repair and current Windows pilot. Session paused at the user's request. No new merge, rollout, runtime/settings change, source transfer or credential change is performed by this documentation checkpoint; only this handoff is published.

## Verified result

[PR3879](https://github.com/vamseeachanta/workspace-hub/pull/3879) is merged at `5bda0efacd4dc4ae34d70a3011a9bc02a7b875fb`. All 32 changed paths match the approved head. Actual landed-tree validation passed 213 tests and all six generated-runtime checks. Its old branch/worktree was removed after source archival; `evidence/issue1249-reviewed-02319be1a` retains the reviewed commit locally.

[PR3881](https://github.com/vamseeachanta/workspace-hub/pull/3881) remains OPEN at `aa3b56c7b32aa9d020947f9266c78d8e6cc9bb23`. It repairs shared-authority and coordination-owner references in AGENTS.md, with regression tests, plan and plan-index entry. Exit observation at 2026-09-22T02:42:47.1918247Z: CLEAN, 16 successful checks and two skipped; retained private receipt: issue1249-merge-20260921/exit-handoff/ci.json. Hosted Claude review completed, but its findings have not been inspected; that review gate remains pending. Refresh this observation before action. No merge authorization exists for this follow-up.

Independent Claude artifact review approved manifest `0438902e66173574bae2d9122e931ce0f77a3e0d8c318d5fbe06f3ded4ec99f5`; index-only review approved `49e8a680c6961b29db0c52373321daab8c08c523ca8e62524f555ce18237fe58`. Automatic Codex missing-index finding was corrected. The final three named routing tests passed with revision-bound provenance; 41 routing/bootstrap tests passed before the contamination fixture was strengthened. All four published file blobs match. Agy was unavailable; three-provider consensus is not claimed.

## Preserved state and limits

Canonical local main remains `26341417ab61146d214010194f4ccd1f93c9f75a`: four local-only commits and twenty remote-only commits at the retained comparison. Its 43 dirty/untracked paths are preserved in private hash-verified snapshots. Local preservation ref: `archive/1249-canonical-pre-reconcile-20260921`. Shared stash `cc2005edd9a095a0aa74dd4daa2316ecf63dfb05` is retained. Do not reset, rebase, sweep-commit or replay local governance changes as part of a merge.

The existing Windows native baseline was re-observed NATIVE_VERIFIED in the preceding checkpoint. This does not qualify the newer main baseline. Combined historical evidence comprises 39 base non-lazy cases, two supplemental lazy cases and two guard controls; original provisional and failed evidence remains retained. No fleet-wide or interactive-session qualification is established. Private evidence remains local; off-machine backup is not established.

The active follow-up worktree, original runtime receipts/journals, test fixtures, private snapshots and unrelated owner worktrees are expected retained state. The exit audit and exact private locators are in the existing FOUNDATION coordination checkpoint. At exit, seven generated machine-status reports had changed since the earlier snapshot (timestamps/session counts); the other 36 paths were unchanged. All were preserved. Other owners' controls remain untouched.

## Resume sequence

1. Read the latest FOUNDATION issue1249 PM checkpoint and private exit audit; check parallel owners and reacquire the shared issue claim before mutations.
2. Inspect PR3881 for intervening commits, fresh CI and review findings. Present the exact current head for its separate per-PR merge decision; approval for PR3879 is not reusable.
3. After inspecting the completed hosted review and resolving any findings, and after explicit approval, use the CLEAN-only merge helper with `--expected-head`, verify remote MERGED and actual landed blobs, then run changed-domain landed-tree validation.
4. Prepare a concrete reviewed canonical reconciliation transaction preserving local-only history and all runtime evidence. Any destructive disposition needs explicit approval. Requalify the actual installed baseline before claiming deployment.
5. Keep sibling/private/fleet rollout deferred to its authorized scope; issue1249 remains open. No Spark delivery or CFD/SOLVERS action follows from this handoff.

Existing published evidence: [native result report](../reports/2026-09-20-issue-1249-windows-native-agents.html), [routing plan](../plans/2026-09-21-issue-1249-published-routing.html), [issue handoff](https://github.com/vamseeachanta/workspace-hub/issues/1249#issuecomment-5759739169). Generalizable review-provenance findings were recorded on [issue 3615](https://github.com/vamseeachanta/workspace-hub/issues/3615#issuecomment-5759820328).