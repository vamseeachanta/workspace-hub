---
name: agenta-fastapi-integration
description: 'Sub-skill of agenta: FastAPI Integration.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# FastAPI Integration

## FastAPI Integration


```python
"""
Integrate Agenta with FastAPI for production deployments.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import agenta as ag
from agenta import Agenta

app = FastAPI(title="Agenta-Powered API")

# Initialize Agenta
ag.init()
client = Agenta()


class QueryRequest(BaseModel):
    """Request model for queries."""
    input: str
    variant: Optional[str] = None
    parameters: Optional[dict] = None


class QueryResponse(BaseModel):
    """Response model."""
    output: str
    variant_used: str
    latency: float


@app.post("/generate", response_model=QueryResponse)
async def generate(request: QueryRequest):
    """Generate response using Agenta-managed prompts."""
    import time

    try:
        # Get variant (default or specified)
        if request.variant:
            variant = client.get_variant_by_name(
                app_name="production-app",
                variant_name=request.variant
            )
        else:
            variant = client.get_default_variant(app_name="production-app")

        # Get prompt template
        template = variant.config.get("template", "{input}")
        prompt = template.format(input=request.input)

        # Get parameters
        params = variant.config.get("parameters", {})
        if request.parameters:
            params.update(request.parameters)

        # Generate
        start_time = time.time()
        response = ag.llm.complete(prompt=prompt, **params)
        latency = time.time() - start_time

        return QueryResponse(
            output=response.text,
            variant_used=variant.name,
            latency=latency
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/variants")
async def list_variants():
    """List available variants."""
    variants = client.list_variants(app_name="production-app")
    return [{"name": v.name, "id": v.id, "is_default": v.is_default} for v in variants]


# Run with: uvicorn api:app --reload
```
