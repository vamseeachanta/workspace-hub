# Tier-1 Indexing Freshness Report

Generated: 2026-04-22
Scope: workspace-hub, digitalmodel, assetutilities, aceengineer-website
Source baseline: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`

## Overall Status

Portfolio status: yellow

Reason:
- no material improvement has occurred yet since the baseline scorecard
- the same structural/indexing weaknesses remain open and now have tracked remediation issues
- daily freshness monitoring has been scheduled to keep this report current

## Repo Status

### workspace-hub — yellow
Current concerns
- `docs/CONTENT_INDEX.md` remains too noisy for trusted issue-routing
- top-level tracked routing-noise artifacts remain present
- discoverability gaps still exist for some intelligence surfaces linked by the accessibility registry

Next actions
- execute #2464
- keep curated routing surfaces separate from raw inventory

### digitalmodel — yellow
Current concerns
- no `digitalmodel/docs/README.md`
- stale/missing canonical registry references remain in live docs
- repo-wide operator map still missing outside the OrcaWave/OrcaFlex slice

Next actions
- execute #2462
- align README, roadmap, and docs to one canonical registry + repo-wide operator map

### assetutilities — red
Current concerns
- stale README remains in place
- no `docs/README.md`
- structure guidance remains misaligned with observed package layout
- tracked backup artifacts remain inside source paths

Next actions
- execute #2461 first among repo-specific remediations
- remove source-path backup artifacts and establish canonical routing docs

### aceengineer-website — yellow
Current concerns
- trusted docs still contain legacy missing product-doc references
- no `docs/README.md`
- no repo-wide operator map for content/scripts/tests routing

Next actions
- execute #2463
- replace legacy missing-product-doc references with current canonical routing surfaces

## Assumption Check Against 2026-04-22 Scorecard

Status: unchanged

The assumptions in `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` still hold:
- digitalmodel remains the strongest repo structurally but lacks repo-wide routing surfaces
- workspace-hub remains the richest control plane but needs curation hygiene
- assetutilities remains the highest misplacement risk
- aceengineer-website remains serviceable for direct edits but weak for durable issue-routing

## Tracking

Created issues
- #2460 tier-1 indexing and code-placement contract
- #2461 assetutilities routing surfaces and source-hygiene cleanup
- #2462 digitalmodel repo-wide routing surfaces
- #2463 aceengineer-website routing surfaces cleanup
- #2464 workspace-hub curated routing index cleanup
- #2465 daily tier-1 indexing freshness audit and scorecard refresh

Scheduled job
- `tier1-indexing-daily` (`aefef5167f2f`) at `30 3 * * *`

## Notes

This report intentionally avoids legacy product-doc reference patterns and uses current canonical routing surfaces only.
