---
name: repo-ecosystem-hygiene
description: Interpret the daily read-only repo ecosystem hygiene audit and route remediation through approved workflows.
type: reference
version: 1.0.0
category: workspace-hub
last_updated: 2026-06-12
source: internal
tags: [repo-health, cron, audit, read-only]
related_skills: [repo-sync, worktree-branch-sync-hygiene]
freedom: low
---

# Repo Ecosystem Hygiene

Use this skill when reviewing `.claude/state/repo-ecosystem-hygiene/latest.md` or the matching JSON state.

## Safety Boundary

The audit is read-only. It reports drift; it does not clean files, update branches, sync remotes, remove worktrees, or post GitHub comments. Treat every remediation action as a separate approved workflow.

## Read The Latest Report

```bash
UV_CACHE_DIR=.claude/state/uv-cache bash scripts/cron/repo-ecosystem-hygiene-audit.sh
sed -n '1,220p' .claude/state/repo-ecosystem-hygiene/latest.md
```

## Triage Findings

- `ERROR` on a required repo: verify the checkout/upstream state directly, then route through `repo-sync` or a GitHub issue if the fix needs approval.
- `WARN` on optional or machine-access repos: preserve the evidence, then decide whether to sync, archive, or update `config/workstations/registry.yaml`.
- `dirty_worktree`, `ahead_of_upstream`, or `behind_upstream`: run a direct `git status --short --branch` in that repo, preserve the output, then route through `repo-sync` or issue-scoped manual integration.
- `missing_upstream`: do not invent tracking. Record the current branch and remotes, then decide whether the repo should track a remote branch or be marked differently in the registry.
- `stash_inventory` or `stale_stash`: inspect `git stash list --date=iso-strict`, preserve any needed patch with an approved workflow, and only drop a stash after explicit disposition.
- `worktree_drift`, `stale_worktree`, or `stale_branch`: use the worktree/branch hygiene workflow; never prune/delete from this audit.
- `registry_disposition_required`: do not delete. Add a registry disposition or open an issue with the path, repo state, and recommended owner.
- `unknown_sibling_residue`: identify owner/source first. If it is expected runtime state, add an explicit registry or runtime allowlist; otherwise open a cleanup issue.
- `registry_policy_gap`: reconcile `config/workstations/registry.yaml` so raw machine access and governed buckets agree.
- `historical_state_changed_since_prior_comment`: preserve the historical source issue/comment context and reconcile registry history before taking cleanup action.
- `schedule_metadata_mismatch`, `known_path_model_mismatch`, or `cron_health_state_missing_or_stale`: treat as scheduler/control-plane metadata debt, not repo drift.

## Closeout Evidence

When acting on findings, cite:

- the report path and timestamp,
- the affected repo/path,
- the exact finding code,
- the issue or approved workflow used for remediation.
