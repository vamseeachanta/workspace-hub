---
name: web-scraper-energy-best-practices
description: 'Sub-skill of web-scraper-energy: Best Practices.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Respect rate limits** - Use 1-2 second delays between requests
2. **Cache responses** - Avoid re-fetching unchanged data
3. **Validate data** - Check for missing/invalid values post-scrape
4. **Handle errors** - Implement retries with exponential backoff
5. **User agent** - Identify your scraper appropriately
6. **Check robots.txt** - Respect site crawling policies
