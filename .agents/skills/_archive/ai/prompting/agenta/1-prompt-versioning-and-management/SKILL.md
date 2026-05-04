---
name: agenta-1-prompt-versioning-and-management
description: 'Sub-skill of agenta: 1. Prompt Versioning and Management.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# 1. Prompt Versioning and Management

## 1. Prompt Versioning and Management


**Creating Versioned Prompts:**
```python
"""
Create and manage versioned prompts with Agenta.
"""
import agenta as ag
from agenta import Agenta
from typing import Optional, Dict, Any

# Initialize Agenta
ag.init()

@ag.entrypoint
def generate_summary(
    text: str,
    max_length: int = 100,
    style: str = "professional"
) -> str:
    """
    Generate a summary with versioned prompt.

    Args:
        text: Text to summarize
        max_length: Maximum summary length
        style: Writing style (professional, casual, technical)

    Returns:
        Generated summary
    """
    # Define prompt template (this becomes versioned)
    prompt = f"""Summarize the following text in a {style} tone.
Keep the summary under {max_length} words.

Text: {text}

Summary:"""

    # Call LLM (Agenta tracks this)
    response = ag.llm.complete(
        prompt=prompt,
        model="gpt-4",
        temperature=0.3,
        max_tokens=max_length * 2
    )

    return response.text


# Example usage
text = """
The company reported strong Q3 results with revenue up 25% year-over-year.
Operating margins improved to 18% from 15% in the prior year.
The CEO highlighted expansion into new markets and product launches.
"""

summary = generate_summary(text, max_length=50, style="professional")
print(summary)
```

**Managing Prompt Versions:**
```python
"""
Manage multiple prompt versions programmatically.
"""
import agenta as ag
from agenta import Agenta
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class PromptVersion:
    """Represents a prompt version."""
    version_id: str
    name: str
    template: str
    parameters: Dict[str, Any]
    created_at: datetime
    is_active: bool = False


class PromptManager:
    """
    Manage prompt versions with Agenta.
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.client = Agenta()

    def create_version(
        self,
        name: str,
        template: str,
        parameters: Dict[str, Any] = None
    ) -> PromptVersion:
        """
        Create a new prompt version.

        Args:
            name: Version name
            template: Prompt template
            parameters: Default parameters

        Returns:
            Created PromptVersion
        """
        # Create variant in Agenta
        variant = self.client.create_variant(
            app_name=self.app_name,
            variant_name=name,
            config={
                "template": template,
                "parameters": parameters or {}
            }
        )

        return PromptVersion(
            version_id=variant.id,
            name=name,
            template=template,
            parameters=parameters or {},
            created_at=datetime.now(),
            is_active=False
        )

    def list_versions(self) -> List[PromptVersion]:
        """List all prompt versions."""
        variants = self.client.list_variants(app_name=self.app_name)

        versions = []
        for v in variants:
            versions.append(PromptVersion(
                version_id=v.id,
                name=v.name,
                template=v.config.get("template", ""),
                parameters=v.config.get("parameters", {}),
                created_at=v.created_at,
                is_active=v.is_default
            ))

        return versions

    def set_active_version(self, version_id: str) -> None:
        """Set a version as the active/default version."""
        self.client.set_default_variant(
            app_name=self.app_name,
            variant_id=version_id
        )

    def get_version(self, version_id: str) -> PromptVersion:
        """Get a specific version."""
        variant = self.client.get_variant(variant_id=version_id)

        return PromptVersion(
            version_id=variant.id,
            name=variant.name,
            template=variant.config.get("template", ""),
            parameters=variant.config.get("parameters", {}),
            created_at=variant.created_at,
            is_active=variant.is_default
        )

    def compare_versions(
        self,
        version_ids: List[str],
        test_input: str
    ) -> Dict[str, str]:
        """
        Compare outputs from multiple versions.

        Args:
            version_ids: List of version IDs to compare
            test_input: Input to test with

        Returns:
            Dictionary mapping version_id to output
        """
        results = {}

        for vid in version_ids:
            version = self.get_version(vid)

            # Format prompt with test input

*Content truncated — see parent skill for full reference.*
