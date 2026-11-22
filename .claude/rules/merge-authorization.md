# Merge authorization — the team merges on green required checks

**When to apply:** any time an agent considers running `gh pr merge` itself, in any repo of the ecosystem, client wikis (every `llm-wiki*`) included.

**Why:** owner decision, 22 Nov 2026 (fleet-ops #577): the team decides and merges its own PRs once the required checks are green. No word from the owner is needed, and no review verdict is a merge gate.

**Policy:**

1. **Merge on green required checks.** When every required check on the PR head is green, the team merges it. This holds in every repo, client wikis included. Second-provider (Codex/Claude) review is advisory: a real bug it finds is fixed before the merge, but a missing or pending verdict never holds a PR.
2. **Pinned squash merge, no branch delete.** Run `gh pr merge <N> --squash --match-head-commit <full head SHA> --repo owner/name`. Never add `--delete-branch` or `--admin`. Do not use `scripts/operations/merge-when-clean.sh --merge`: it still passes `--delete-branch`.
3. **Holds still apply.** An unexpired `hold` label, a hold_check basis hold, or an engineering-basis question waiting on the owner keeps the PR open.
4. **Freshness.** Immediately before the merge, require `mergeStateStatus == CLEAN`; never land from `BEHIND`, `BLOCKED`, `DIRTY`, `UNKNOWN`, or `UNSTABLE`. Explicit user authorization never waives these checks: green required checks, a clean merge state, holds and the landed-tree validation below apply to every merge, whoever asks for it.
5. **Owner records stay the owner's.** Merging never self-applies `status:plan-approved` or completeness stamps.
6. **After any merge, verify MERGED on the remote** and confirm the content landed (`git cat-file -e origin/main:<path>` — squash-merge makes merge-commit reachability meaningless, see `reference_squash_merge_reachability_false_orphan`).
7. **Validate the actual landed tree before closeout.** After remote MERGED verification, run `git fetch origin main`, resolve the actual landed `origin/main` commit, and rerun the changed-domain generated-artifact checks against that tree before commenting complete or closing the issue. Synthetic merge commits and the pre-merge working tree are not landed-tree evidence.

## Direct-main exemptions

The default path remains branch -> PR -> merge. These registered automation
exceptions may push to `main` only within the bounded write surfaces named here:

- `.claude/cron/ecosystem-sync.sh`: may write `.claude/state/ecosystem-sync/last-sync.yaml` and `docs/sync-reports/` after a successful ecosystem sync run. The exemption exists so the scheduled sync can publish its digest and state without a human PR for each run. The script enforces the bound: it exits 6 without committing or pushing when anything else is staged, when any pre-existing outgoing commit touches another path, or when any outgoing merge commit exists ([#3985](https://github.com/vamseeachanta/workspace-hub/issues/3985); test `scripts/cron/tests/test_ecosystem_sync_push_guard.sh`).
- `scripts/fleet/account-usage-cron.sh`: may write `config/ai-tools/account-usage-latest.json` and `docs/reports/ai-account-usage.md` after a successful fleet account-usage collection. The exemption exists so hourly generated account-usage evidence can stay current without burning CI minutes or requiring an operator to merge routine telemetry.
- `scripts/fleet/fleet-snapshot-daily.sh`: may write `docs/reports/fleet-snapshots/latest.json` after a successful fleet snapshot collection and labelling run. The exemption exists so the daily public fleet snapshot can stay current without committing dated files or requiring a human PR for routine telemetry.
- `scripts/client_llm_wiki/bootstrap_git.py`: may push exactly the first root commit to a newly registered client-wiki repository's `refs/heads/main` through the descriptor-bound bootstrap transport. The exemption exists because an empty client-wiki repository has no prior branch to PR against; it does not authorize later commits or arbitrary workspace-hub main writes.

**Related:** [`model-routing.md`](model-routing.md) (corollary 4), [`merge-cleanup.md`](merge-cleanup.md), [`completeness-before-close.md`](completeness-before-close.md). Memory: `feedback_dependabot_merge_no_rebase_trust_clean`. Issue: workspace-hub#3390; owner decision of 22 Nov 2026 on fleet-ops #577.
