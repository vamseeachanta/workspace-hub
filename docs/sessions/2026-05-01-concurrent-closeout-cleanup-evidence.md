# Concurrent closeout cleanup evidence — 2026-05-01
Generated: 2026-05-01T15:09:49-05:00

## Summary
This records the cleanup performed after the stale branch/worktree root-cause review. Scope was intentionally limited to broken/unregistered Claude worktree directories and local branches already merged into `origin/main`. Unmerged branches were preserved.

## Verification snapshot
| Check | Result |
|---|---:|
| `HEAD` | `992455fd0` |
| `ORIGIN` | `992455fd0` |
| `AHEAD_BEHIND` | `0	0` |
| `LOCAL_BRANCHES` | `36` |
| `MERGED_REMAINING` | `0` |
| `UNMERGED_REMAINING` | `35` |
| `REGISTERED_WORKTREES` | `1` |
| `CLAUDE_WORKTREE_ENTRIES` | `0` |
| `STATUS_ENTRIES` | `17` |

## Broken/unregistered Claude worktrees removed
- `351M	.claude/worktrees/agent-a0343527`
- `353M	.claude/worktrees/agent-a0b1b064`
- `350M	.claude/worktrees/agent-addee4fc`

The remaining empty `agent-a2e2ea6a` directory tree was also removed after verifying it contained no files.

## Local merged branches deleted
Deleted `54` local branches already ancestral to `origin/main`:

- `chore/save-agent-execution-scripts-20260427`
- `claude/capacity-20260430-1841-issue-2070-state-size-guard`
- `claude/capacity-20260430-1841-issue-2227-wiki-promotion`
- `claude/capacity-20260430-1841-plan-review-2550-2552-security`
- `codex/10thread-20260427-2036-issue-2459`
- `codex/10thread-20260428-issue-2126`
- `codex/10thread-20260428-issue-2324`
- `codex/10thread-20260428-issue-2327`
- `codex/10thread-20260428-issue-2364`
- `codex/10thread-20260428-issue-2368`
- `codex/10thread-20260428-issue-2373`
- `codex/10thread-20260428-issue-2402`
- `codex/burn-20260427-issue-2152`
- `codex/burn-20260427-issue-2227`
- `codex/burn-20260427-issue-2357`
- `codex/burn-20260427-issue-2459`
- `codex/burn-20260427-issue-2461`
- `codex/burn-20260427-issue-2463`
- `codex/burn-20260427-issue-2464`
- `codex/burn-20260427-issue-2471`
- `codex/burn-20260427-issue-2493`
- `codex/nextwave-20260427-issue-2408`
- `codex/nextwave-20260427-issue-2417`
- `codex/nextwave-20260427-issue-2424`
- `codex/nextwave-20260427-issue-2433`
- `cron/wiki-health-20260427`
- `docs/final-exit-20260428`
- `docs/final-exit-20260429`
- `final/merge-workspace-hub-20260428`
- `fix/codex-stdin-hang`
- `integration/merge-all-worktrees-20260429-night`
- `issue-2311-exec`
- `issue-2476-semantic-equivalence-contract`
- `issue-2488-implementation`
- `issue-2510-planreview`
- `issue-2514-governance`
- `issue-2555-vessel-chart-assets`
- `lane10-provider-queue-autofeed-20260430-0431`
- `lane6-2560-evidence-fill`
- `lane7-closeout-audit-20260430T0431`
- `lane8-artifact-inline-20260430044205`
- `merge/issue-2464-20260427-163214`
- `nightly-batch-2-20260430T034746Z`
- `nightly-batch-3-2070`
- `nightly-batch-5-integration-20260430T053418Z`
- `nightly-batch-5-integration-20260501T054654Z`
- `nightly-immediate-batch4-20260430T034353Z`
- `nightly/immediate-batch2-20260430T034203Z`
- `nightly/immediate-batch5-20260430T034333Z`
- `nightly/immediate-batch5-20260430T034808Z-audit`
- `overnight-codex-2-review-20260501-033341`
- `overnight-codex-3-audit-20260501-033904`
- `overnight-issue-2112-20260501-033341`
- `reconcile/post-reboot-main-20260427`

## Unmerged/unique local branches preserved
Preserved `35` branches because they still have commits not in `origin/main` or require explicit disposition:

| Branch | Unique commits vs origin/main | Upstream | Tip |
|---|---:|---|---|
| `codex/10thread-20260428-issue-1583` | 1 | `NO_UPSTREAM` | `b5f2be130` |
| `codex/10thread-20260428-issue-2017` | 1 | `origin/codex/10thread-20260428-issue-2017` | `891adc8c0` |
| `codex/10thread-20260428-issue-2105` | 1 | `origin/main` | `5d1620fe0` |
| `codex/10thread-20260428-issue-2125` | 1 | `NO_UPSTREAM` | `e4b619323` |
| `codex/10thread-20260428-issue-2129` | 1 | `NO_UPSTREAM` | `6510614a1` |
| `codex/10thread-20260428-issue-2269` | 1 | `NO_UPSTREAM` | `464efb8cc` |
| `codex/10thread-20260428-issue-2270` | 1 | `NO_UPSTREAM` | `15ae2f994` |
| `codex/10thread-20260428-issue-2271` | 1 | `origin/codex/10thread-20260428-issue-2271` | `7546045f3` |
| `codex/10thread-20260428-issue-2289` | 1 | `origin/codex/10thread-20260428-issue-2289` | `681da0334` |
| `codex/10thread-20260428-issue-2346` | 1 | `origin/main` | `44735e979` |
| `codex/10thread-20260428-issue-2369` | 1 | `origin/codex/10thread-20260428-issue-2369` | `49c2dc80d` |
| `codex/10thread-20260428-issue-2403` | 2 | `origin/main` | `4297c493f` |
| `codex/burn-20260427-issue-2458` | 1 | `origin/main` | `09993cbc7` |
| `codex/burn-20260427-issue-2462` | 1 | `origin/codex/burn-20260427-issue-2462` | `7810834e5` |
| `execute/issue-2380-batch-pack-3-tier-a-tier-a` | 3 | `origin/execute/issue-2380-batch-pack-3-tier-a-tier-a` | `41f7a40ed` |
| `flywheel/aces-5-v2-patch` | 3 | `origin/flywheel/aces-5-v2-patch` | `b3b079ef2` |
| `flywheel/aces-issue-tree-and-p0-plans` | 1 | `NO_UPSTREAM` | `0449f4147` |
| `nightly-batch-2-plan-review-20260501T043948Z` | 1 | `origin/nightly-batch-2-plan-review-20260501T043948Z` | `0cdf3297d` |
| `nightly-batch-4-gtm-artifacts-20260430` | 1 | `origin/nightly-batch-4-gtm-artifacts-20260430` | `317740268` |
| `nightly-immediate-batch4-20260430T034753Z` | 1 | `origin/nightly-immediate-batch4-20260430T034753Z` | `18f91e929` |
| `plan/issue-2103-aqwa-bemrosetta-ingestion` | 6 | `origin/plan/issue-2103-aqwa-bemrosetta-ingestion` | `12acaf355` |
| `plan/issue-2124-orcina-resources-examples-training` | 5 | `origin/plan/issue-2124-orcina-resources-examples-training` | `cb1c4a972` |
| `plan/issue-2125-orcina-auto-refresh` | 3 | `origin/plan/issue-2125-orcina-auto-refresh` | `dc4715767` |
| `plan/issue-2126-markdown-conversion-qa` | 6 | `origin/plan/issue-2126-markdown-conversion-qa` | `c5d82b265` |
| `plan/issue-2227-ocimf-tandem-csa-z276-wiki-promotion` | 3 | `origin/plan/issue-2227-ocimf-tandem-csa-z276-wiki-promotion` | `b77bdd038` |
| `plan/issue-2363-wiki-refs-reverse-lookup` | 2 | `origin/plan/issue-2363-wiki-refs-reverse-lookup` | `73f366d46` |
| `plan/issue-2364-batch-pack-1` | 9 | `origin/plan/issue-2364-batch-pack-1` | `0ff8cb033` |
| `plan/issue-2368-faceted-portal-pages` | 2 | `origin/plan/issue-2368-faceted-portal-pages` | `1c01062d8` |
| `plan/issue-2369-batch-pack-2` | 5 | `origin/plan/issue-2369-batch-pack-2` | `b24b3f2dc` |
| `plan/issue-2373-batch-pack-4` | 3 | `origin/plan/issue-2373-batch-pack-4` | `c516ec853` |
| `plan/issue-2380-batch-pack-3-tier-a` | 1 | `origin/plan/issue-2380-batch-pack-3-tier-a` | `84570eb12` |
| `plan/issue-2392-wiki-coverage-gap-detector` | 2 | `origin/plan/issue-2392-wiki-coverage-gap-detector` | `9dd83e708` |
| `plan/issue-2471-standards-wiki-path-sanction` | 2 | `origin/plan/issue-2471-standards-wiki-path-sanction` | `ef0a984b9` |
| `salvage/post-reboot-20260427-063127` | 4 | `NO_UPSTREAM` | `8daf482be` |
| `salvage/primary-before-realign-20260427-102750` | 4 | `NO_UPSTREAM` | `8daf482be` |

## Next required policy follow-up
- Do not close GitHub issues before commit/push/branch disposition/worktree removal evidence is posted.
- Preserve or merge each listed unmerged branch through a separate review; do not bulk-delete these.
- Keep implementation work out of the main checkout; use isolated worktrees and a repo-level closeout lock for writer operations.
