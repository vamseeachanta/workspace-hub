---
name: development-workflow-orchestrator-integration-with-other-skills
description: 'Sub-skill of development-workflow-orchestrator: Integration with Other
  Skills.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Integration with Other Skills

## Integration with Other Skills


**With knowledge-base-system:**
```python
# Load patterns and examples
kb = KnowledgeBase()
patterns = kb.search(query="YAML configuration", category="workflow")
examples = kb.examples.find(task="CSV analysis")

# Use KB templates
yaml_template = kb.templates.get("input_config.yaml")
pseudocode_template = kb.templates.get("pseudocode.md")
```

**With ai-questioning-pattern:**
```python
# Use questioning skill before YAML generation
questions = AIQuestioningPattern().generate_questions(user_prompt)
answers = await ask_user(questions)
yaml_config = generate_yaml(user_prompt, answers)
```

**With sparc-workflow:**
```python
# Integrate with SPARC phases
sparc = SPARCWorkflow()
sparc.specification(user_prompt)    # Phase 1-2
sparc.pseudocode(yaml_config)       # Phase 3
sparc.architecture(pseudocode)      # Design
sparc.refinement(tests, code)       # Phase 4-5
sparc.completion(execution)         # Phase 6
```
