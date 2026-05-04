---
name: langchain-1-error-handling
description: 'Sub-skill of langchain: 1. Error Handling (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Error Handling (+2)

## 1. Error Handling


```python
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import CallbackManager
import logging

logger = logging.getLogger(__name__)

def safe_invoke(chain, input_data, max_retries=3):
    """Invoke chain with retry logic."""
    for attempt in range(max_retries):
        try:
            return chain.invoke(input_data)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```


## 2. Prompt Versioning


```python
from pathlib import Path
import yaml

def load_prompt_template(version: str = "v1"):
    """Load versioned prompt template."""
    prompt_path = Path(f"prompts/{version}.yaml")
    with open(prompt_path) as f:
        config = yaml.safe_load(f)

    return ChatPromptTemplate.from_template(config["template"])
```


## 3. Cost Monitoring


```python
from langchain_community.callbacks import get_openai_callback

def track_costs(chain, input_data):
    """Track API costs for chain invocation."""
    with get_openai_callback() as cb:
        result = chain.invoke(input_data)

    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost: ${cb.total_cost:.4f}")

    return result, cb
```
