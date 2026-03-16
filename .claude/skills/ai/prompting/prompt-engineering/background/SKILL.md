---
name: prompt-engineering-background
description: 'Sub-skill of prompt-engineering: Background.'
version: 1.0.0
category: ai-prompting
type: reference
scripts_exempt: true
---

# Background

## Background


You specialize in:
{chr(10).join(f"- {s}" for s in specializations)}
"""

    if notable_work:
        persona += f"""
