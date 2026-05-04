---
name: rag-system-builder-system-prompt-template
description: 'Sub-skill of rag-system-builder: System Prompt Template (+1).'
version: 1.2.0
category: data
type: reference
scripts_exempt: true
---

# System Prompt Template (+1)

## System Prompt Template


```python
SYSTEM_PROMPT = """You are a technical expert assistant. Your role is to:
1. Answer questions based ONLY on the provided documents
2. Cite specific sources when possible
3. Acknowledge when information is not available
4. Be precise with technical terminology
5. Provide practical, actionable answers

If asked about topics not covered in the documents, say:
"I don't have information about that in the available documents."
"""
```

## Multi-Turn Conversations


```python
def query_with_history(self, question, history=[]):
    """Support follow-up questions."""
    context = self.get_relevant_context(question)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for h in history[-4:]:  # Last 4 turns
        messages.append({"role": "user", "content": h['question']})

*See sub-skills for full details.*
