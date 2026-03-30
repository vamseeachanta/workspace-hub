---
name: rag-system-builder-streaming-responses
description: 'Sub-skill of rag-system-builder: Streaming Responses.'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# Streaming Responses

## Streaming Responses


For better UX with long answers:

```python
def query_streaming(self, question, top_k=5):
    """Stream RAG response for real-time display."""
    context = self.get_context(question, top_k)
    prompt = self.build_prompt(context, question)

    # Anthropic streaming
    with anthropic.Anthropic().messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield text
```
