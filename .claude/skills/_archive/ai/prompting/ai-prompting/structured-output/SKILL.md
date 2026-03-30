---
name: ai-prompting-structured-output
description: 'Sub-skill of ai-prompting: Structured Output (+2).'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Structured Output (+2)

## Structured Output


```python
from pydantic import BaseModel

class OutputSchema(BaseModel):
    summary: str
    key_points: list[str]
    confidence: float

# Force structured output
response = llm.complete(
    prompt,
    response_format={"type": "json_object"},
    schema=OutputSchema.schema()
)
```

## Error Handling and Fallbacks


```python
def robust_llm_call(prompt, fallback_response=None):
    try:
        response = llm.complete(prompt, timeout=30)
        if not validate_response(response):
            raise ValueError("Invalid response format")
        return response
    except RateLimitError:
        time.sleep(60)
        return robust_llm_call(prompt, fallback_response)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return fallback_response
```

## Caching and Cost Optimization


```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embedding(text: str) -> list[float]:
    return embedding_model.embed(text)

def cache_key(prompt, model, temperature):
    content = f"{prompt}|{model}|{temperature}"
    return hashlib.sha256(content.encode()).hexdigest()
```
