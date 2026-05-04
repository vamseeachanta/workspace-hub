---
name: search-strategy-the-goal
description: 'Sub-skill of search-strategy: The Goal.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# The Goal

## The Goal


Turn this:
```
"What did we decide about the API migration timeline?"
```

Into targeted searches across every connected source:
```
~~chat:  "API migration timeline decision" (semantic) + "API migration" in:#engineering after:2025-01-01
~~knowledge base: semantic search "API migration timeline decision"
~~project tracker:  text search "API migration" in relevant workspace
```

Then synthesize the results into a single coherent answer.
