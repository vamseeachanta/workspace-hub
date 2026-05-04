---
name: knowledge-synthesis-cross-source-deduplication
description: 'Sub-skill of knowledge-synthesis: Cross-Source Deduplication (+2).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Cross-Source Deduplication (+2)

## Cross-Source Deduplication


The same information often appears in multiple places. Identify and merge duplicates:

**Signals that results are about the same thing:**
- Same or very similar text content
- Same author/sender
- Timestamps within a short window (same day or adjacent days)
- References to the same entity (project name, document, decision)
- One source references another ("as discussed in ~~chat", "per the email", "see the doc")

**How to merge:**
- Combine into a single narrative item
- Cite all sources where it appeared
- Use the most complete version as the primary text
- Add unique details from each source


## Deduplication Priority


When the same information exists in multiple sources, prefer:
```
1. The most complete version (fullest context)
2. The most authoritative source (official doc > chat)
3. The most recent version (latest update wins for evolving info)
```


## What NOT to Deduplicate


Keep as separate items when:
- The same topic is discussed but with different conclusions
- Different people express different viewpoints
- The information evolved meaningfully between sources (v1 vs v2 of a decision)
- Different time periods are represented
