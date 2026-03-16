---
name: semantic-search-setup-model-selection
description: 'Sub-skill of semantic-search-setup: Model Selection.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Model Selection

## Model Selection


| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| `all-MiniLM-L6-v2` | 384 | Fast | Good | General purpose |
| `all-mpnet-base-v2` | 768 | Medium | Better | Higher accuracy |
| `bge-small-en-v1.5` | 384 | Fast | Good | Multilingual |
| `text-embedding-3-small` | 1536 | API | Excellent | Production (OpenAI) |

**Recommended:** `all-MiniLM-L6-v2` for local CPU processing.
