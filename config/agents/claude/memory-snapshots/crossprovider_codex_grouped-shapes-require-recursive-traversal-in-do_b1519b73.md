---
name: crossprovider codex grouped-shapes-require-recursive-traversal-in-do
description: Grouped shapes require recursive traversal in document extraction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [document-parsing, faithfulness, structured-data]
---

PowerPoint/Office document content extraction that iterates only top-level shapes misses pictures/objects inside grouped shapes (p:grpSp). Faithful extraction requires recursive descent. Grepping top-level counts masks true missing content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
