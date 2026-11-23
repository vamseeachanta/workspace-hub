# Intelligence Summary Drift Report

Date: 2026-04-14
Issue: #2250

## Scope

This report reconciles current intelligence summary artifacts against their
canonical ledgers and records which mismatches required correction versus
which artifacts needed explicit metric-family ownership notes.

## Canonical ledgers checked

- `data/document-index/resource-intelligence-maturity.yaml`
- `data/document-index/registry.yaml`
- `data/document-index/standards-transfer-ledger.yaml`

## Drift findings

| Status | Artifact | Evidence of drift | Canonical source | Resolution |
|---|---|---|---|---|
| Fixed | `data/document-index/resource-intelligence-maturity.md` | Reported `5` docs in scope / `0` read / `0%`, while the YAML ledger reports `425` / `29` / `6.8%` | `data/document-index/resource-intelligence-maturity.yaml` | Regenerated the markdown summary to match the YAML ledger fields exactly |
| Fixed | `docs/document-intelligence/data-intelligence-map.md` | Claimed `registry.yaml` had `12` domains and that `standards-transfer-ledger.yaml` was `425` total with `29` done / `235` gap | `data/document-index/registry.yaml`, `data/document-index/standards-transfer-ledger.yaml`, `data/document-index/resource-intelligence-maturity.yaml` | Updated the map to distinguish live corpus totals, live standards-ledger totals, and bounded active-maturity-scope metrics |
| Fixed | `data/document-index/data-audit-report.md` | Section titled `Standards Transfer Ledger Status` presented the bounded `425 / 29 / 138 / 235` active-scope snapshot as if it were the live standards ledger | `data/document-index/resource-intelligence-maturity.yaml`, `data/document-index/standards-transfer-ledger.yaml` | Renamed and clarified the section as an active-maturity snapshot and added the live-ledger counts separately |
| Verified, no edit | `docs/reports/llm-wiki-external-source-priority-queue.md` | Uses `425 standards in active maturity scope`, which matches the maturity ledger’s bounded scope | `data/document-index/resource-intelligence-maturity.yaml` | Left unchanged; wording is already consistent with the bounded metric family |
| Historical snapshot, no edit | `data/document-index/summary-extraction-plan.yaml` | Contains older `current_state` numbers for issue `#1542`; it is a dated planning artifact rather than a live summary surface | Planning artifact dated `2026-03-31` | Left unchanged; treat as historical plan input, not a live control-plane summary |

## File-level evidence

### 1. Stale maturity markdown

- Canonical ledger: `resource-intelligence-maturity.yaml`
  - `documents_in_scope: 425`
  - `documents_marked_read: 29`
  - `documents_marked_read_percent: 6.8`
- Stale markdown previously reported:
  - `Documents in scope: 5`
  - `Documents marked read: 0`
  - `Documents marked read percent: 0`

### 2. Registry/domain-count drift

- Canonical `registry.yaml`
  - source count: `6`
  - domain count: `14`
  - repo count: `11`
- `data-intelligence-map.md` previously reported `domain (12)`.

### 3. Standards-ledger vs active-scope conflation

- Canonical live standards ledger: `standards-transfer-ledger.yaml`
  - total entries: `436`
  - domains: `13`
  - status split: `done: 435`, `implemented: 1`
- Canonical bounded active-maturity scope: `resource-intelligence-maturity.yaml`
  - documents in scope: `425`
  - documents marked read: `29`
  - gap standards: `235`
  - reference standards: `138`
- The corrected reporting surfaces now treat these as distinct metric families.

## Outcome

- Current known drift is documented with file-level evidence.
- Stale summary artifacts were updated or re-labeled so their numbers align with the authoritative ledgers.
- Historical planning artifacts were left untouched but classified explicitly as non-canonical.
