# Tier-1 Indexing Checklist

This checklist derives from `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` and tracks the current routing/indexing state for the four tier-1 repositories named in `docs/BUSINESS_BRAIN.md`.

MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority. Scorecards may be cited as local attestation only; this checklist must remain anchored to the standards contract, repo entry points, and issue-approved remediation work.

Allowed status values for the fields below are: `present`, `partial`, `missing`, `not-applicable`.

## Checklist Records

### workspace-hub

- repo_name: workspace-hub
- operator_map_status: partial
- registry_status: partial
- data_placement_status: present
- evidence_source: `AGENTS.md`, `docs/README.md`, `docs/standards/DATA_PLACEMENT.md`, #2464
- follow_through_issue: #2464
- notes: workspace-hub has strong control-plane standards and docs discovery, but #2464 owns the curated tier-1 routing index split from raw inventory noise.

### digitalmodel

- repo_name: digitalmodel
- operator_map_status: partial
- registry_status: partial
- data_placement_status: partial
- evidence_source: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` as local attestation only, #2462
- follow_through_issue: #2462
- notes: digitalmodel has strong OrcaWave/OrcaFlex routing depth, but #2462 owns repo-wide operator-map and canonical-registry completion beyond that slice.

### assetutilities

- repo_name: assetutilities
- operator_map_status: missing
- registry_status: partial
- data_placement_status: partial
- evidence_source: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` as local attestation only, #2461
- follow_through_issue: #2461
- notes: assetutilities needs canonical routing surfaces and source-hygiene cleanup under #2461.

### aceengineer-website

- repo_name: aceengineer-website
- operator_map_status: missing
- registry_status: missing
- data_placement_status: partial
- evidence_source: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` as local attestation only, #2463
- follow_through_issue: #2463
- notes: aceengineer-website needs canonical routing surfaces and legacy product-doc reference cleanup under #2463.

## Use Rules

- Use this checklist as a planning and verification surface, not as a substitute for the contract.
- Confirm issue work against each repository's `AGENTS.md`, `README.md`, `docs/README.md`, operator map, and canonical registry before implementation.
- Treat `present` as usable but still subject to freshness review.
- Treat `partial` or `missing` as a routing risk that must be resolved by the relevant child issue before broad repo-specific execution.
- Keep #2465 responsible for the daily freshness review automation and `docs/reports/tier-1-indexing-freshness-latest.md` refresh path.
