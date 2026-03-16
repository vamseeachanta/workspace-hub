---
name: data-exploration-key-columns
description: 'Sub-skill of data-exploration: Key Columns (+5).'
version: 1.0.0
category: data-analytics
type: reference
scripts_exempt: true
---

# Key Columns (+5)

## Key Columns


| Column | Type | Description | Example Values | Notes |
|--------|------|-------------|----------------|-------|
| user_id | STRING | Unique user identifier | "usr_abc123" | FK to users.id |
| event_type | STRING | Type of event | "click", "view", "purchase" | 15 distinct values |
| revenue | DECIMAL | Transaction revenue in USD | 29.99, 149.00 | Null for non-purchase events |
| created_at | TIMESTAMP | When the event occurred | 2024-01-15 14:23:01 | Partitioned on this column |


## Relationships

- Joins to `users` on `user_id`
- Joins to `products` on `product_id`
- Parent of `event_details` (1:many on event_id)


## Known Issues

- [List any known data quality issues]
- [Note any gotchas for analysts]


## Common Query Patterns

- [Typical use cases for this table]
```


## Schema Exploration Queries


When connected to a data warehouse, use these patterns to discover schema:

```sql
-- List all tables in a schema (PostgreSQL)
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Column details (PostgreSQL)
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'my_table'
ORDER BY ordinal_position;

-- Table sizes (PostgreSQL)
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Row counts for all tables (general pattern)
-- Run per-table: SELECT COUNT(*) FROM table_name
```


## Lineage and Dependencies


When exploring an unfamiliar data environment:

1. Start with the "output" tables (what reports or dashboards consume)
2. Trace upstream: What tables feed into them?
3. Identify raw/staging/mart layers
4. Map the transformation chain from raw data to analytical tables
5. Note where data is enriched, filtered, or aggregated
