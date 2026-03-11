# ADR: Knowledge Routing Table — WRK-1105

## Status: Accepted (2026-03-10)

## Context

Knowledge generated during WRK execution has been accumulating in MEMORY.md, which is
line-limited (200 lines, auto-eviction via compact-memory.py). Engineering domain expertise
exists nowhere in the system. Resource-intelligence Stage 2 mines docs/skills but not a
real knowledge base. Each session rediscovers patterns already learned.

## Decision: Knowledge Routing Table

| Knowledge Type | Current Destination | Correct Destination | Rationale |
|----------------|--------------------|--------------------|-----------|
| WRK completion summary | MEMORY.md (manual, temporary) | `knowledge-base/wrk-completions.jsonl` | Queryable, persistent, indexed — MEMORY.md is a working-memory scratchpad, not an archive |
| Reusable patterns from WRK | MEMORY.md (partial, evictable) | `knowledge-base/wrk-completions.jsonl` (patterns field) | Captured at archive time by capture-wrk-summary.sh |
| Script/tool inventory | MEMORY.md (partial) | resource-intelligence skills + symbol-index | Already partially solved by WRK-1085 (symbol index) |
| Career learnings / domain expertise | Nowhere | `knowledge/seeds/career-learnings.yaml` (committed) → `knowledge-base/index.jsonl` (runtime) | Committed seed survives machine re-provisioning; runtime index makes it queryable |
| Cross-repo architectural decisions | MEMORY.md (partial) | `knowledge-base/wrk-completions.jsonl` (patterns field) or ADR docs in `specs/` | WRK ADRs in specs/ are permanent; summary captured in knowledge-base |
| Engineering domain knowledge (FEA, CFD, OrcaFlex, etc.) | Nowhere | `knowledge/seeds/career-learnings.yaml` | Manually seeded once; queried by session-start and resource-intelligence |

## Persistence Layers

### Committed Seed (tracked in git)
- `knowledge/seeds/career-learnings.yaml` — source of truth for career domain knowledge
- Must pass legal scan before commit (no client identifiers)
- Manually curated; updated by humans/orchestrators via WRK

### Machine-Local Runtime (gitignored)
- `knowledge-base/wrk-completions.jsonl` — WRK completion entries, appended at archive time
- `knowledge-base/index.jsonl` — merged and deduplicated index of all stores
- `knowledge-base/*.lock` — flock files for concurrent-write safety
- Rationale: knowledge-base is local to ace-linux-1; rebuilt from archive/ if lost via
  `bash scripts/knowledge/rebuild-from-archive.sh` (future WRK follow-on)
- **Not committed** — machine-specific runtime state

### MEMORY.md Role (Redefined)
- `/home/vamsee/.claude/projects/.../memory/MEMORY.md` (Claude auto-memory, outside repo)
- After WRK-1105: ≤80 lines of active state + pointers only
- No WRK ARCHIVED summaries — those go to knowledge-base/
- Distinct from `.claude/memory/KNOWLEDGE.md` (in-repo institutional memory)

## JSONL Schema

```json
{
  "id": "WRK-NNN",
  "type": "wrk",
  "category": "harness",
  "subcategory": "knowledge",
  "title": "Human-readable title from WRK frontmatter",
  "archived_at": "2026-03-10T00:00:00Z",
  "source": "archive-item-hook",
  "mission": "First 500 chars of ## Mission section",
  "patterns": ["pattern 1 from resource-intelligence.yaml", "..."],
  "follow_ons": ["WRK-NNNN", "..."]
}
```

Career entry schema:
```json
{
  "id": "CAREER-engineering-orcaflex-viv",
  "type": "career",
  "category": "engineering",
  "subcategory": "offshore",
  "title": "OrcaFlex VIV analysis patterns",
  "learned_at": "2026-03-10T00:00:00Z",
  "source": "career-learnings.yaml",
  "context": "Domain expertise summary",
  "patterns": ["key pattern 1", "key pattern 2"],
  "follow_ons": []
}
```

The `type` field (`wrk` vs `career`) enables display and dedup separation in query output.
Career entries render as `## CAREER-slug: title` (not `## WRK-ID`).

## Consequences

**Positive:**
- MEMORY.md stays ≤80 lines; no WRK knowledge lost to eviction
- Career domain expertise persists across machines (committed)
- query-knowledge.sh surfaces relevant past work in < 1s
- resource-intelligence Stage 2 and session-start can enrich planning from real data

**Negative:**
- knowledge-base/ is machine-local; cross-machine sync not supported (accepted)
- Manual career-learnings seed required initially

## Rebuild Path

If `knowledge-base/` is lost:
```bash
bash scripts/knowledge/rebuild-from-archive.sh
```
(Future-work follow-on WRK — see future-work.yaml for this item.)
Interim: re-run `build-knowledge-index.sh` from any surviving JSONL or re-capture
from archive/WRK-*.md manually using `capture-wrk-summary.sh WRK-NNN`.
