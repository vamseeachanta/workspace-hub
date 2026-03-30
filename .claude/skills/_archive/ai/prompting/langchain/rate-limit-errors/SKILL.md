---
name: langchain-rate-limit-errors
description: 'Sub-skill of langchain: Rate Limit Errors (+2).'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Rate Limit Errors (+2)

## Rate Limit Errors


```python
from langchain_openai import ChatOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt

llm = ChatOpenAI(
    model="gpt-4",
    max_retries=3,
    request_timeout=60
)

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def invoke_with_retry(chain, input_data):
    return chain.invoke(input_data)
```


## Memory Issues with Large Documents


```python
# Process documents in batches
def batch_process_documents(documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        yield process_batch(batch)
```


## Vector Store Performance


```python
# Use FAISS for larger collections
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(
    documents,
    embeddings,
    distance_strategy="COSINE"
)

# Add index for faster retrieval
vectorstore.save_local("faiss_index")
```
