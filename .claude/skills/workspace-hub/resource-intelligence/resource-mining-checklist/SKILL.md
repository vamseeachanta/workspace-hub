---
name: resource-intelligence-resource-mining-checklist
description: 'Sub-skill of resource-intelligence: Resource Mining Checklist.'
version: 1.1.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Resource Mining Checklist

## Resource Mining Checklist


Mine in this order (cheapest lookup first). Stop a category when no relevant results found after a reasonable scan.

| # | Category | Where to look | When relevant |
|---|----------|--------------|---------------|
| 1 | **Skills** | `.claude/skills/**` — scan for domain keywords | Always — load domain skills before planning |
| 2 | **Prior WRKs** | `work-queue/archive/`, `related:` + `blocked_by:` fields | Always — avoid re-deriving solved problems |
| 3 | **Memory** | `MEMORY.md`, `memory/*.md` | Always — institutional knowledge |
| 4 | **Existing code / scripts** | `src/`, `scripts/` in each `target_repo` | Implementation WRKs |
| 5 | **Specs / plans** | `specs/wrk/`, `specs/modules/` | Route B/C — prior design decisions |
| 6 | **Workspace docs** | `.claude/docs/` | Architecture, orchestration, legal decisions |
| 7 | **Document index** | `data/document-index/registry.yaml`, `index.jsonl`, `standards-transfer-ledger.yaml` | Engineering / standards WRKs |
| 8 | **Mounted sources** | `/mnt/ace/`, `/mnt/remote/dev-secondary/dde` | Engineering domain WRKs |
| 9 | **Online / additive** | External URLs | Only when repo sources are insufficient |
| 10 | **Knowledge base** | `bash scripts/knowledge/query-knowledge.sh --query <keyword> --category <cat>` | Always for harness/knowledge WRKs; check for any WRK when prior work patterns are relevant |

---
