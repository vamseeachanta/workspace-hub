---
name: agenta-langchain-integration
description: 'Sub-skill of agenta: Langchain Integration.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Langchain Integration

## Langchain Integration


```python
"""
Use Agenta for prompt management in Langchain applications.
"""
import agenta as ag
from agenta import Agenta
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any

class AgentaPromptLoader:
    """
    Load prompts from Agenta into Langchain.
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.client = Agenta()
        self._cache: Dict[str, PromptTemplate] = {}

    def get_prompt(
        self,
        variant_name: str = None,
        use_cache: bool = True
    ) -> PromptTemplate:
        """
        Get a Langchain PromptTemplate from Agenta.

        Args:
            variant_name: Variant to load (None for default)
            use_cache: Whether to use cached prompts

        Returns:
            Langchain PromptTemplate
        """
        cache_key = variant_name or "default"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Get variant from Agenta
        if variant_name:
            variant = self.client.get_variant_by_name(
                app_name=self.app_name,
                variant_name=variant_name
            )
        else:
            variant = self.client.get_default_variant(app_name=self.app_name)

        # Create Langchain prompt
        template = variant.config.get("template", "{input}")
        prompt = PromptTemplate.from_template(template)

        # Cache
        self._cache[cache_key] = prompt

        return prompt

    def create_chain(
        self,
        variant_name: str = None,
        model: str = "gpt-4",
        temperature: float = 0.3
    ):
        """
        Create a Langchain chain from Agenta prompt.

        Args:
            variant_name: Variant to use
            model: Model name
            temperature: Temperature setting

        Returns:
            Langchain chain
        """
        prompt = self.get_prompt(variant_name)
        llm = ChatOpenAI(model=model, temperature=temperature)

        return prompt | llm | StrOutputParser()


# Usage
ag.init()

loader = AgentaPromptLoader("qa-app")

# Get prompt template
prompt = loader.get_prompt("concise-v1")
print(f"Template: {prompt.template}")

# Create and use chain
chain = loader.create_chain(variant_name="detailed-v2")
result = chain.invoke({"input": "What is machine learning?"})
print(f"Result: {result}")
```
