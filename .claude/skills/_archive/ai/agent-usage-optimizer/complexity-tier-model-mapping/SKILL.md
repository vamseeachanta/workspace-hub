---
name: agent-usage-optimizer-complexity-tier-model-mapping
description: "Sub-skill of agent-usage-optimizer: Complexity Tier \u2192 Model Mapping."
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Complexity Tier → Model Mapping

## Complexity Tier → Model Mapping


Use this alongside Route mapping when task nature is clear:

| Complexity tier | Keywords | Recommended model |
|----------------|----------|------------------|
| `routine` | format, rename, config, scaffold, update-doc, copy | Claude Haiku |
| `standard` | implement, review, test, fix, migrate, document | Claude Sonnet |
| `complex` | architecture, design, cross-repo, security, compound | Claude Opus |

**Key insight**: the gap between theoretical and observed exposure is an implementation gap —
not a capability gap. Routing routine tasks to cheaper models closes this gap for our workflow.
See WRK-5002 to automate tier detection in `task_classifier.sh`.

---

*Use this skill before any multi-item work session or when quota is a concern.*
*Related: `ai/optimization/model-selection`, `ai/optimization/usage-optimization`*
