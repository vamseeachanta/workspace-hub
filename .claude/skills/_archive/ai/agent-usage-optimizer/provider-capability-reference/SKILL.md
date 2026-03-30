---
name: agent-usage-optimizer-provider-capability-reference
description: 'Sub-skill of agent-usage-optimizer: Provider Capability Reference.'
version: 1.0.0
category: ai
type: reference
scripts_exempt: true
---

# Provider Capability Reference

## Provider Capability Reference


| Provider       | Strengths                                          | Avoid When                          |
|----------------|----------------------------------------------------|-------------------------------------|
| Claude Opus    | Architecture, deep reasoning, compound tasks       | Quota < 20%; simple tasks           |
| Claude Sonnet  | Standard code, reviews, balanced quality/speed     | Quota < 20% and Route C needed      |
| Claude Haiku   | Bulk data, summarisation, cost-effective volume    | Architecture or security decisions  |
| Codex          | Focused code gen, unit tests, debugging functions  | Long-context docs; planning work    |
| Gemini         | Long-context analysis, large files, cross-repo     | Fine-grained code edits             |
