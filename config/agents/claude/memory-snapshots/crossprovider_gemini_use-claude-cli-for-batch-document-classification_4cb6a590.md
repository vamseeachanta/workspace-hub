---
name: crossprovider gemini use-claude-cli-for-batch-document-classification
description: Use Claude CLI for batch document classification at scale
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [batch-processing, claude-cli, document-classification, automation]
---

When building batch document classification pipelines, invoke Claude via subprocess with `claude -p` prompt interface rather than ANTHROPIC_API_KEY + Anthropic SDK calls. The CLI handles batching, session management, and error handling more robustly for classification workflows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
