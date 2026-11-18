# Merge authorization — the team merges at reviewed heads

**When to apply:** any time an agent considers merging a PR, in any repo of the ecosystem.

**Policy** (maintainer rulings of 2026-10-12, 2026-11-06 and 2026-11-12; replaces the #3390 default of handing the human the merge command):

1. The team merges its own PRs once the current head has an independent review that passes and CI is green (`mergeStateStatus == CLEAN`). No per-PR word from the maintainer is needed.
2. Merge with the CLEAN-only helper, `scripts/operations/merge-when-clean.sh --merge <PR>`, or the fleet merge worker. Never `--admin`, and never from `BEHIND`, `BLOCKED`, `DIRTY`, `UNKNOWN` or `UNSTABLE`.
3. A merge never stands in for `status:plan-approved`, the maintainer's review of client-facing or outward work, or completeness stamps.
4. After a merge, verify MERGED on the remote and that the content landed (`git cat-file -e origin/main:<path>`), then rerun the changed-domain generated-artifact checks on the landed `origin/main` before closing the issue.
5. Never push to `main` directly, except the exemptions below.

## Direct-main exemptions

The default path remains branch -> PR -> merge. These registered automation
exceptions may push to `main` only within the bounded write surfaces named here:

- `.claude/cron/ecosystem-sync.sh`: may write `.claude/state/ecosystem-sync/last-sync.yaml` and `docs/sync-reports/` after a successful ecosystem sync run. The exemption exists so the scheduled sync can publish its digest and state without a human PR for each run. The script enforces the bound: it exits 6 without committing or pushing when anything else is staged, when any pre-existing outgoing commit touches another path, or when any outgoing merge commit exists ([#3985](https://github.com/vamseeachanta/workspace-hub/issues/3985); test `scripts/cron/tests/test_ecosystem_sync_push_guard.sh`).
- `scripts/fleet/account-usage-cron.sh`: may write `config/ai-tools/account-usage-latest.json` and `docs/reports/ai-account-usage.md` after a successful fleet account-usage collection. The exemption exists so hourly generated account-usage evidence can stay current without burning CI minutes or requiring an operator to merge routine telemetry.
- `scripts/fleet/fleet-snapshot-daily.sh`: may write `docs/reports/fleet-snapshots/latest.json` after a successful fleet snapshot collection and labelling run. The exemption exists so the daily public fleet snapshot can stay current without committing dated files or requiring a human PR for routine telemetry.
- `scripts/client_llm_wiki/bootstrap_git.py`: may push exactly the first root commit to a newly registered client-wiki repository's `refs/heads/main` through the descriptor-bound bootstrap transport. The exemption exists because an empty client-wiki repository has no prior branch to PR against; it does not authorize later commits or arbitrary workspace-hub main writes.

**Related:** [`merge-cleanup.md`](merge-cleanup.md) (what follows a merge), [`model-routing.md`](model-routing.md), [`completeness-before-close.md`](completeness-before-close.md). Memory: `reference_squash_merge_reachability_false_orphan`, `feedback_dependabot_merge_no_rebase_trust_clean`. History: workspace-hub#3390 item 4.
