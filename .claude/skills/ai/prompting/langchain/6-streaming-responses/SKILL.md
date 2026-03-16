---
name: langchain-6-streaming-responses
description: 'Sub-skill of langchain: 6. Streaming Responses.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 6. Streaming Responses

## 6. Streaming Responses


**Streaming Chain:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio

def create_streaming_chain():
    """Create chain that supports streaming output."""

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        streaming=True
    )

    prompt = ChatPromptTemplate.from_template(
        "You are an expert engineer. Explain in detail: {topic}"
    )

    chain = prompt | llm | StrOutputParser()

    return chain

# Synchronous streaming
def stream_response(chain, topic: str):
    """Stream response token by token."""
    print("Response: ", end="", flush=True)

    for chunk in chain.stream({"topic": topic}):
        print(chunk, end="", flush=True)

    print("\n")

# Async streaming
async def astream_response(chain, topic: str):
    """Async stream response."""
    print("Response: ", end="", flush=True)

    async for chunk in chain.astream({"topic": topic}):
        print(chunk, end="", flush=True)

    print("\n")

# Usage
chain = create_streaming_chain()

# Sync streaming
stream_response(chain, "mooring line catenary equations")

# Async streaming
asyncio.run(astream_response(chain, "wave-structure interaction"))
```

**Streaming with Callbacks:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List
import json

class CustomStreamHandler(BaseCallbackHandler):
    """Custom callback handler for streaming."""

    def __init__(self):
        self.tokens = []
        self.final_response = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated."""
        self.tokens.append(token)
        self.final_response += token
        # Could send to WebSocket, write to file, etc.
        print(token, end="", flush=True)

    def on_llm_end(self, response: Any, **kwargs) -> None:
        """Called when LLM finishes."""
        print(f"\n\n[Generation complete: {len(self.tokens)} tokens]")

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called on error."""
        print(f"\n[Error: {error}]")

def stream_with_callbacks(prompt: str):
    """Stream with custom callbacks."""

    handler = CustomStreamHandler()

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        streaming=True,
        callbacks=[handler]
    )

    response = llm.invoke(prompt)

    return handler.final_response, handler.tokens

# Usage
response, tokens = stream_with_callbacks(
    "Explain the design considerations for a turret mooring system"
)

print(f"\nTotal tokens: {len(tokens)}")
```
