---
name: development-workflow-orchestrator-troubleshooting
description: 'Sub-skill of development-workflow-orchestrator: Troubleshooting.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Troubleshooting

## Troubleshooting


**Problem: User requirements unclear**
```
Solution: Use AI Questioning Pattern skill
- Ask specific questions about ambiguities
- Provide options with trade-offs
- Wait for explicit approval
```

**Problem: YAML generation failing**
```
Solution: Use templates from knowledge base
- Load yaml_config.yaml template
- Fill in from user_prompt systematically
- Validate against schema
```

**Problem: Pseudocode not approved**
```
Solution: Iterate based on feedback
- Address specific concerns
- Provide alternatives
- Re-generate and re-submit
```

**Problem: Tests not passing**
```
Solution: Follow TDD cycle properly
- Verify tests are correct first
- Implement minimal code to pass
- Don't proceed until all tests pass
```
