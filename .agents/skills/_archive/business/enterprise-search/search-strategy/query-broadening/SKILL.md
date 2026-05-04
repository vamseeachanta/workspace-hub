---
name: search-strategy-query-broadening
description: 'Sub-skill of search-strategy: Query Broadening.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Query Broadening

## Query Broadening


If initial queries return too few results:
```
Original: "PostgreSQL migration Q2 timeline decision"
Broader:  "PostgreSQL migration"
Broader:  "database migration"
Broadest: "migration"
```

Remove constraints in this order:
1. Date filters (search all time)
2. Source/location filters
3. Less important keywords
4. Keep only core entity/topic terms
