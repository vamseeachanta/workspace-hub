---
name: metocean-data-fetcher-best-practices
description: 'Sub-skill of metocean-data-fetcher: Best Practices.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Use caching** - Built-in cache with 24-hour TTL reduces API load
2. **Respect rate limits** - Clients implement automatic rate limiting
3. **Use `fetch_realtime` for recent data** - Last 45 days for NDBC
4. **Use `fetch_historical` for archived data** - NDBC archives go back years
5. **Coordinate-based sources have no stations** - Open-Meteo and MET Norway
6. **Check quality flags** - Harmonized observations include quality assessment
7. **Batch operations** - Use `harmonize_batch` for efficiency
8. **Context managers** - Always use `with` statement for clients
