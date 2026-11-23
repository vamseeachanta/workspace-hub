# Short Runbook — 2026-04-09 Batch

1. Back up current issue bodies for #2055 and #2062 using the backup commands in `docs/plans/claude-ops-2026-04-09/results/refinement-application-pack.md` Section 1, and verify both backup files are non-empty before continuing.

2. Apply the refined issue body and refinement comment for #2055 (Sections 2a-2c) and #2062 (Sections 3a-3d) from `docs/plans/claude-ops-2026-04-09/results/refinement-application-pack.md`.

3. Apply post-refinement labels (`scope:v1`, `status:plan-review`, and `status:needs-data` for #2055) using the combined commands in Section 4 of `docs/plans/claude-ops-2026-04-09/results/refinement-application-pack.md`.

4. Label #2059, #2063, and #2056 as `status:plan-review` and post the review comments using Section 1 of `docs/plans/claude-ops-2026-04-09/results/plan-review-command-pack.md`.

5. Review the three execution packs at `docs/plans/claude-followup-2026-04-09/results/issue-{2059,2063,2056}-execution-pack.md` to confirm scope, TDD sequence, and file boundaries.

6. **STOP/GO CHECKPOINT: Do not proceed until you have reviewed every execution pack and decided which issues to approve — all subsequent steps mutate GitHub issue state.**

7. For each approved issue, swap labels from `status:plan-review` to `status:plan-approved` and post the approval comment using Section 2 of `docs/plans/claude-ops-2026-04-09/results/plan-review-command-pack.md`.

8. Launch up to 3 parallel implementation agents using the self-contained prompts (A, B, C) in `docs/plans/claude-ops-2026-04-09/results/implementation-launch-pack.md` Section 4 — all three have zero file overlap and are safe to run concurrently.

9. After each agent finishes, run the per-issue verification checks from Section 5 of `docs/plans/claude-ops-2026-04-09/results/implementation-launch-pack.md`.

10. Run the cross-issue checks (no file overlap, submodule pointer, atomic commits, summary comments) from the same Section 5.

11. Route each completed issue for cross-review per the 2-provider table in Section 6 of `docs/plans/claude-ops-2026-04-09/results/implementation-launch-pack.md`, merging in order: #2059, then #2063, then #2056.

12. Confirm all three GitHub issues have summary comments posted and labels reflect final status.

RECOMMENDATION: USE THIS AS THE FASTEST OPERATOR PATH
