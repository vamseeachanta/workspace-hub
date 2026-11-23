# Intelligence Metric Source-of-Truth Map

Date: 2026-04-14
Issue: #2250

## Canonical ownership by metric family

| Metric family | Canonical file | Canonical fields | Allowed derivative surfaces | Rule |
|---|---|---|---|---|
| Active maturity scope | `data/document-index/resource-intelligence-maturity.yaml` | `documents_in_scope`, `documents_marked_read`, `documents_marked_read_percent`, `gap_standards`, `reference_standards`, `wrk_captured_standards` | `data/document-index/resource-intelligence-maturity.md`, bounded prioritization summaries such as `docs/reports/llm-wiki-external-source-priority-queue.md` | Derivatives must say they represent the bounded active-maturity scope, not the live standards ledger |
| Live corpus totals | `data/document-index/registry.yaml` | `total_docs`, `total_summaries`, `by_source`, `by_domain`, `repos` | `data/document-index/data-audit-report.md`, `docs/document-intelligence/data-intelligence-map.md`, bounded reports that quote corpus size | Derivatives may copy counts, but the registry remains authoritative |
| Live standards-ledger totals | `data/document-index/standards-transfer-ledger.yaml` | top-level `total`, `summary.done`, `summary.implemented`, per-entry `status`, per-entry `domain` | `docs/document-intelligence/data-intelligence-map.md`, any report discussing live standards-ledger coverage | Derivatives must not substitute bounded active-scope numbers for live ledger totals |
| Historical planning snapshots | Dated plan artifacts such as `data/document-index/summary-extraction-plan.yaml` | Point-in-time planning assumptions | None beyond the plan itself | Treat as historical context only; do not reuse as live control-plane truth |

## Human-convenience summaries

These files are convenience surfaces and are not primary ledgers:

- `data/document-index/resource-intelligence-maturity.md`
- `data/document-index/data-audit-report.md`
- `docs/document-intelligence/data-intelligence-map.md`
- `docs/reports/llm-wiki-external-source-priority-queue.md`

## Lightweight drift-check rule

Run this review whenever a convenience summary is updated or during weekly intelligence hygiene checks:

1. Compare `resource-intelligence-maturity.md` against `resource-intelligence-maturity.yaml` for the bounded active-scope fields.
2. Compare any copied corpus totals or domain counts against `registry.yaml`.
3. Compare any copied live standards-ledger totals against `standards-transfer-ledger.yaml`.
4. If a file mixes metric families, rewrite it so each number is explicitly labeled with its canonical source.

## Copy-review checklist

- Does the artifact say whether it is reporting the bounded active-maturity scope or the live standards ledger?
- If it quotes corpus totals or domain counts, do they match `registry.yaml`?
- If it quotes live standards-ledger totals, do they match `standards-transfer-ledger.yaml`?
- If it is a dated plan or audit snapshot, is that snapshot status explicit?

## Validator note

No new script was added for this bounded issue. The repeatable validator for now is the source-of-truth review above:

- use `resource-intelligence-maturity.yaml` for bounded active-scope metrics
- use `registry.yaml` for live corpus totals
- use `standards-transfer-ledger.yaml` for live standards-ledger totals
- reject any convenience summary that merges those families without labeling them
