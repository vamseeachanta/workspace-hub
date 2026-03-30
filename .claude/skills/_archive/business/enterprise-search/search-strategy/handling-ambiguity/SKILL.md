---
name: search-strategy-handling-ambiguity
description: 'Sub-skill of search-strategy: Handling Ambiguity.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Handling Ambiguity

## Handling Ambiguity


When a query is ambiguous, prefer asking one focused clarifying question over guessing:

```
Ambiguous: "search for the migration"
→ "I found references to a few migrations. Are you looking for:
   1. The database migration (Project Phoenix)
   2. The cloud migration (AWS → GCP)
   3. The email migration (Exchange → O365)"
```

Only ask for clarification when:
- There are genuinely distinct interpretations that would produce very different results
- The ambiguity would significantly affect which sources to search

Do NOT ask for clarification when:
- The query is clear enough to produce useful results
- Minor ambiguity can be resolved by returning results from multiple interpretations
