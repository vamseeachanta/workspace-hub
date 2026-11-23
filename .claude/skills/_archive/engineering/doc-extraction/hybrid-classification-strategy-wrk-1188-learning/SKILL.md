---
name: doc-extraction-hybrid-classification-strategy-wrk-1188-learning
description: 'Sub-skill of doc-extraction: Hybrid Classification Strategy (WRK-1188
  Learning).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Hybrid Classification Strategy (WRK-1188 Learning)

## Hybrid Classification Strategy (WRK-1188 Learning)


For large homogeneous collections, prefer deterministic classifiers over LLM:

| Collection | Strategy | Cost | Accuracy |
|-----------|----------|------|----------|
| ASTM (25,537 docs) | Designation prefix → discipline | $0 | 86% vs LLM |
| API/DNV/ISO (1,062) | LLM (Claude Haiku CLI) | ~$2 | Baseline |
| Unknown org (484) | LLM (Claude Haiku CLI) | ~$1 | Baseline |

**Rule**: If org has predictable title/designation patterns, write a deterministic
classifier first. Validate with 100-doc LLM sample. Accept if >85%.

See `data/document-index-pipeline` skill for full pipeline orchestration.
