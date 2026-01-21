---
name: memory-systems
description: Design agent memory architectures for cross-session persistence. Use for building learning systems, maintaining entity consistency, and temporal knowledge tracking. Based on muratcankoylan/Agent-Skills-for-Context-Engineering.
version: 1.0.0
category: agents
last_updated: 2026-01-19
source: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
related_skills:
  - multi-agent-patterns
  - context-management
  - session-memory
---

# Memory Systems Skill

## Overview

This skill addresses agent persistence across sessions through layered architectures balancing immediate context with long-term knowledge retention. Effective memory systems enable agents to learn, maintain consistency, and reason over accumulated knowledge.

## Quick Start

1. **Identify needs** - What must persist? (entities, decisions, patterns)
2. **Choose architecture** - File-based, vector, graph, or hybrid
3. **Design retrieval** - How will memory be accessed?
4. **Implement storage** - With temporal validity
5. **Monitor growth** - Prune and consolidate regularly

## When to Use

- Building cross-session agents
- Maintaining entity consistency
- Implementing reasoning over accumulated knowledge
- Designing learning systems
- Creating growing knowledge bases
- Building temporal-aware state tracking

## Memory Spectrum

Memory ranges from volatile to permanent:

| Layer | Persistence | Latency | Capacity |
|-------|-------------|---------|----------|
| Working Memory | Context window | Zero | Limited |
| Short-term | Session-scoped | Low | Moderate |
| Long-term | Cross-session | Medium | Large |
| Archival | Permanent | High | Unlimited |

Effective systems layer multiple types:
- **Working memory** - Current context window
- **Short-term** - Session facts, active tasks
- **Long-term** - Learned patterns, entity knowledge
- **Entity-specific** - Per-entity history
- **Temporal graphs** - Time-aware relationships

## Architecture Options

### 1. File-System-as-Memory

**Structure:**
```
memory/
├── entities/
│   └── {entity_id}.json
├── sessions/
│   └── {session_id}/
├── knowledge/
│   └── {topic}.md
└── index.json
```

**Pros:** Simple, debuggable, version-controlled
**Cons:** No semantic search, manual organization

**Implementation:**
```python
class FileMemory:
    def __init__(self, base_path: str):
        self.base = Path(base_path)

    def store(self, key: str, value: dict, category: str = "general"):
        path = self.base / category / f"{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        value["_stored_at"] = datetime.utcnow().isoformat()
        path.write_text(json.dumps(value, indent=2))

    def retrieve(self, key: str, category: str = "general") -> Optional[dict]:
        path = self.base / category / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None
```

### 2. Vector RAG with Metadata

**Structure:**
```python
class MemoryEntry:
    id: str
    content: str
    embedding: List[float]
    metadata: dict  # entity_tags, temporal_validity, confidence
    created_at: datetime
    valid_until: Optional[datetime]
```

**Pros:** Semantic search, scalable
**Cons:** Loses relationship information, no temporal queries

**Enhancement with metadata:**
```python
def search_with_temporal_filter(
    query: str,
    as_of: datetime = None,
    entity_filter: List[str] = None
) -> List[MemoryEntry]:
    results = vector_search(query)
    return [r for r in results
            if r.is_valid_at(as_of or datetime.utcnow())
            and (not entity_filter or r.has_entity(entity_filter))]
```

### 3. Knowledge Graph

**Structure:**
```
Entities: [Person, Project, Decision, Event]
Relations: [owns, participates_in, decided_by, happened_at]
```

**Pros:** Preserves relationships, relational queries
**Cons:** Complex setup, query language learning curve

**Key capability:**
```cypher
MATCH (p:Person)-[:PARTICIPATES_IN]->(proj:Project)
      -[:HAS_DECISION]->(d:Decision)
WHERE d.date > $since
RETURN p.name, d.description, d.date
```

### 4. Temporal Knowledge Graph

**Structure:**
```python
class TemporalFact:
    subject: str
    predicate: str
    object: str
    valid_from: datetime
    valid_until: Optional[datetime]
    source: str
    confidence: float
```

**Pros:** Time-travel queries, fact evolution tracking
**Cons:** Most complex, highest overhead

**Capability example:**
```python
# What was the project status on date X?
facts = temporal_graph.query_as_of(
    subject="project-alpha",
    predicate="has_status",
    as_of=datetime(2025, 6, 15)
)
```

## Performance Benchmarks

| Architecture | Accuracy | Retrieval Time | Best For |
|--------------|----------|----------------|----------|
| Temporal KG | 94.8% | 2.58s | Complex relationships |
| GraphRAG | 75-85% | Variable | Balanced |
| Vector RAG | 60-70% | Fast | Simple semantic |
| File-based | N/A | Fast | Simple persistence |

## Vector Store Limitations

**Problems:**
- "Vector stores lose relationship information"
- Cannot answer queries traversing relationships
- Lack temporal mechanisms for current vs. outdated facts

**Example failure:**
```
Query: "Who approved the decision that affected Project X?"
Vector RAG: Returns documents mentioning approvals and Project X
            but cannot connect the relationship chain
```

**Solution:** Combine vector search with graph traversal:
```python
def hybrid_query(query: str):
    # Semantic search for relevant entities
    entities = vector_search(query)

    # Graph traversal for relationships
    for entity in entities:
        related = graph.traverse(entity.id, max_depth=2)
        entity.relationships = related

    return entities
```

## Memory Lifecycle

### Writing

```python
def store_memory(
    content: str,
    category: str,
    entities: List[str],
    valid_from: datetime = None,
    valid_until: datetime = None,
    confidence: float = 1.0
):
    entry = MemoryEntry(
        id=generate_id(),
        content=content,
        embedding=embed(content),
        metadata={
            "category": category,
            "entities": entities,
            "confidence": confidence
        },
        valid_from=valid_from or datetime.utcnow(),
        valid_until=valid_until
    )
    storage.save(entry)
```

### Reading

```python
def recall_memory(
    query: str,
    context: dict,
    as_of: datetime = None,
    limit: int = 10
) -> List[MemoryEntry]:
    # 1. Semantic search
    candidates = vector_search(query, limit=limit * 3)

    # 2. Temporal filtering
    valid = [c for c in candidates if c.is_valid_at(as_of)]

    # 3. Context relevance scoring
    scored = [(c, relevance_score(c, context)) for c in valid]

    # 4. Return top results
    return sorted(scored, key=lambda x: x[1], reverse=True)[:limit]
```

### Consolidation

```python
def consolidate_memories(category: str, older_than_days: int = 30):
    """Combine related old memories into summaries."""
    old_memories = get_memories(
        category=category,
        before=datetime.utcnow() - timedelta(days=older_than_days)
    )

    # Group by entity
    grouped = group_by_entity(old_memories)

    for entity, memories in grouped.items():
        if len(memories) > threshold:
            summary = generate_summary(memories)
            store_memory(summary, category="consolidated", entities=[entity])
            archive_memories(memories)
```

## Best Practices

### Do

1. Match architecture to query requirements
2. Implement progressive disclosure for memory access
3. Use temporal validity to prevent outdated info conflicts
4. Consolidate periodically to manage growth
5. Design graceful retrieval failures
6. Monitor storage size and query performance

### Don't

1. Store everything (be selective)
2. Ignore temporal validity
3. Mix fact types without categorization
4. Skip consolidation indefinitely
5. Trust old memories without verification
6. Ignore retrieval latency in design

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Stale data returned | Missing temporal filter | Add validity checks |
| Contradictory facts | Multiple sources | Use confidence scoring |
| Memory bloat | No consolidation | Implement periodic cleanup |
| Slow retrieval | Index issues | Optimize embeddings/indexes |
| Lost relationships | Vector-only storage | Add graph layer |

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Retrieval accuracy | >85% | Relevant results returned |
| Temporal accuracy | >95% | Correct time-based filtering |
| Storage efficiency | <100MB/month | Reasonable growth |
| Query latency | <500ms | P95 retrieval time |
| Consolidation rate | Monthly | Old memories summarized |

## Related Skills

- [multi-agent-patterns](../multi-agent-patterns/SKILL.md) - Agent coordination
- [context-management](../../context-management/SKILL.md) - Context optimization
- [session-memory](../../automation/session-memory/SKILL.md) - Session persistence

---

## Version History

- **1.0.0** (2026-01-19): Initial release adapted from Agent-Skills-for-Context-Engineering
