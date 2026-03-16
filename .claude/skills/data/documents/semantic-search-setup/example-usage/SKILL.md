---
name: semantic-search-setup-example-usage
description: 'Sub-skill of semantic-search-setup: Example Usage.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Example Usage

## Example Usage


```bash
# Generate embeddings
python embed.py --db knowledge.db --batch 100

# Run as background service
./embed-service.sh start

# Check progress
./embed-service.sh status

# Search
python search.py "fatigue analysis requirements"
```
