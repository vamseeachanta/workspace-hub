---
name: ai-prompting-integration-with-workspace-hub
description: 'Sub-skill of ai-prompting: Integration with Workspace-Hub.'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills power AI features across the workspace-hub ecosystem:

```
workspace-hub/
├── ai/
│   ├── chains/              # Uses: langchain
│   │   ├── qa_chain.py
│   │   └── summarize_chain.py
│   ├── prompts/             # Uses: prompt-engineering
│   │   ├── templates/
│   │   └── optimized/
│   ├── pipelines/           # Uses: dspy
│   │   └── optimized_qa.py
│   └── data/                # Uses: pandasai
│       └── smart_analysis.py
├── evaluation/              # Uses: agenta
│   ├── test_cases/
│   └── metrics/
└── config/
    └── llm_config.yaml
```
