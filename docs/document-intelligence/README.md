# Document Intelligence — Navigation Index

> Entry point for the workspace-hub intelligence ecosystem architecture,
> inventories, and knowledge assets.
>
> Last Updated: 2026-04-11

## Reading Order for Newcomers

1. **Start here:** [Parent Operating Model](llm-wiki-resource-doc-intelligence-operating-model.md) — six-layer pyramid, ownership, flows
2. **Identity rules:** [Provenance Contract](standards-codes-provenance-reuse-contract.md) — doc_key, reuse rules
3. **Durability rules:** [Boundary Policy](durable-vs-transient-knowledge-boundary.md) — durable vs transient classification
4. **Current state:** [Accessibility Map](intelligence-accessibility-map.md) — what exists, what's broken

## Architecture (Normative)

| Document | Issue | Purpose |
|---|---|---|
| [Operating Model](llm-wiki-resource-doc-intelligence-operating-model.md) | #2205 | Six-layer pyramid, ownership, information flows |
| [Provenance Contract](standards-codes-provenance-reuse-contract.md) | #2207 | doc_key identity, reuse rules |
| [Boundary Policy](durable-vs-transient-knowledge-boundary.md) | #2209 | Durable vs transient classification |
| [Conformance Checks](pyramid-conformance-checks.md) | #2206 | Validation design |

## Knowledge Assets

| Domain | Index | Scale |
|---|---|---|
| Engineering | [wiki/index.md](../../knowledge/wikis/engineering/wiki/index.md) | ~78 pages |
| Marine Engineering | [wiki/index.md](../../knowledge/wikis/marine-engineering/wiki/index.md) | ~19,168 pages |
| Maritime Law | [wiki/index.md](../../knowledge/wikis/maritime-law/wiki/index.md) | ~22 pages |
| Naval Architecture | [wiki/index.md](../../knowledge/wikis/naval-architecture/wiki/index.md) | ~45 pages |
| Personal | [wiki/index.md](../../knowledge/wikis/personal/wiki/index.md) | ~5 pages |
| Cross-wiki references | [cross-links.md](../../knowledge/wikis/cross-links.md) | 25 links |
| Knowledge seeds | [knowledge/seeds/](../../knowledge/seeds/) | 6 seed files |

## Registries & Provenance (Operational)

See [Data Intelligence Map](data-intelligence-map.md) for comprehensive registry reference.

Key surfaces:
- Corpus index: `data/document-index/index.jsonl` (1M+ records)
- Standards ledger: `data/document-index/standards-transfer-ledger.yaml` (425 standards)
- Design codes: [data/design-codes/code-registry.yaml](../../data/design-codes/code-registry.yaml) (~30 codes)
- Maturity tracking: [resource-intelligence-maturity.yaml](../../data/document-index/resource-intelligence-maturity.yaml)

## Maps & Inventories (Operational)

| Document | Purpose |
|---|---|
| [Accessibility Map](intelligence-accessibility-map.md) | Asset discoverability inventory (#2096) |
| [Engineering Documentation Map](engineering-documentation-map.md) | Domain-by-domain document inventory |
| [Domain Coverage](domain-coverage.md) | Standards coverage by engineering domain |
| [Mount Drive Knowledge Map](mount-drive-knowledge-map.md) | Mount point and file catalog |

## Back

[docs/README.md](../README.md)
