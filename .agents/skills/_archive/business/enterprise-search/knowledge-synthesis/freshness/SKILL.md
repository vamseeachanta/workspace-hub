---
name: knowledge-synthesis-freshness
description: 'Sub-skill of knowledge-synthesis: Freshness (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Freshness (+3)

## Freshness


| Recency | Confidence impact |
|---------|------------------|
| Today / yesterday | High confidence for current state |
| This week | Good confidence |
| This month | Moderate — things may have changed |
| Older than a month | Lower confidence — flag as potentially outdated |

For status queries, heavily weight freshness. For policy/factual queries, freshness matters less.


## Authority


| Source type | Authority level |
|-------------|----------------|
| Official wiki / knowledge base | Highest — curated, maintained |
| Shared documents (final versions) | High — intentionally published |
| Email announcements | High — formal communication |
| Meeting notes | Moderate-high — may be incomplete |
| Chat messages (thread conclusions) | Moderate — informal but real-time |
| Chat messages (mid-thread) | Lower — may not reflect final position |
| Draft documents | Low — not finalized |
| Task comments | Contextual — depends on commenter |


## Expressing Confidence


When confidence is high (multiple fresh, authoritative sources agree):
```
The team decided to use REST for the API redesign. [direct statement]
```

When confidence is moderate (single source or somewhat dated):
```
Based on the discussion in #engineering last month, the team was leaning
toward REST for the API redesign. This may have evolved since then.
```

When confidence is low (old data, informal source, or conflicting signals):
```
I found a reference to an API migration discussion from three months ago
in ~~chat, but I couldn't find a formal decision document. The information
may be outdated. You might want to check with the team for current status.
```


## Conflicting Information


When sources disagree:
```
I found conflicting information about the API approach:
- The ~~chat discussion on Jan 10 suggested GraphQL
- But Sarah's email on Jan 15 confirmed REST
- The design doc (updated Jan 15) reflects REST

The most recent sources indicate REST was the final decision,
but the earlier ~~chat discussion explored GraphQL first.
```

Always surface conflicts rather than silently picking one version.
