# Freshness Governance Contract

Issue: #2105
Updated: 2026-04-28

## Scope

#2105 is the governance lock for intelligence freshness vocabulary and source-of-truth precedence. It does not populate the per-asset matrix and it does not extend scanners to new intelligence asset classes.

Out-of-scope child work:

- #2483 populates `docs/document-intelligence/freshness-cadence-matrix.md` with per-asset rows after this vocabulary lands.
- #2484 extends scanner coverage beyond the current document staleness scanner after this vocabulary lands.

## Canonical Vocabulary

Staleness status vocabulary is `FRESH / MODERATE / STALE`. This adopts the live document scanner and dashboard vocabulary instead of the abandoned `current / warn / stale` draft terms.

Cadence vocabulary is `nightly / weekly / monthly / quarterly / on-demand`.

Legacy `daily` cadence values are normalized to `nightly` when the source runs once per day through cron or another scheduled automation. The word `daily` may still appear in prose that describes human timing, but machine-readable cadence fields use `nightly`.

## Canonical Artifacts

`data/document-index/freshness-cadences.yaml` is the machine-readable canonical artifact for expected cadence, staleness thresholds, evidence sources, and governance metadata.

`docs/document-intelligence/freshness-cadence-matrix.md` is a derived human review matrix. It may summarize or render the YAML contract for operators, but it is not the source of truth when values disagree.

`data/document-index/intelligence-accessibility-registry.yaml` remains the inventory source for asset metadata such as asset key, canonical path, reachability, owner issue, `freshness_source`, and `freshness_cadence`.

## Source-Of-Truth Precedence

Use this source-of-truth precedence when scanner output, registry metadata, and matrix values disagree:

1. scanner output for measured age and observed `FRESH / MODERATE / STALE` status
2. `data/document-index/freshness-cadences.yaml` for expected cadence, thresholds, check method, and alias handling
3. `data/document-index/intelligence-accessibility-registry.yaml` for asset metadata, owner, canonical path, and declared `freshness_source`
4. `docs/document-intelligence/freshness-cadence-matrix.md` for human review presentation

If a scanner reports an observed age that contradicts the cadence file, weekly review should treat the scanner output as current evidence and open a follow-up to repair the cadence metadata or the scanner logic.

## Registry Field Diff

The registry field diff for #2105 is intentionally additive/normalizing:

| Field | Action | Contract |
|---|---|---|
| `freshness_cadence` | Keep and normalize | Allowed values are `nightly`, `weekly`, `monthly`, `quarterly`, `on-demand`. Legacy `daily` becomes `nightly`. |
| `freshness_source` | Keep | Continue to describe the command, timestamp, or review evidence used to assess freshness. |
| `staleness_status` | Do not persist | Status is computed by scanners or review runs and uses `FRESH / MODERATE / STALE`. Static registry entries should not store this field. |

## Ownership

Cadence vocabulary changes require review through #2105 follow-up planning or a child issue that explicitly names the affected fields.

Per-asset cadence changes belong to the owner issue recorded in `intelligence-accessibility-registry.yaml` when present. If no owner issue exists, weekly review may propose a cadence change but should capture it as a new issue before changing the canonical YAML.

The weekly ecosystem review consumes this contract and should report freshness failures with:

- asset key or path
- observed scanner output when available
- expected cadence and staleness threshold from `freshness-cadences.yaml`
- owner issue or missing-owner gap
- whether the remediation belongs to #2483, #2484, or a new follow-up
