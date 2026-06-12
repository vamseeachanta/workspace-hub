---
name: crossprovider codex approval-scope-assumptions-convert-adversarial-b
description: Approval-scope assumptions convert adversarial blockers into presentable plans
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, adversarial-review, engineering-governance]
---

When adversarial review finds unresolved engineering/source/governance blockers blocking plan approval, convert them to explicit approval-scope assumptions with fail-closed implementation gates. List the assumption, explain why it's unresolved, state the fail-close behavior (implementation stops if assumption cannot be fulfilled), and request user approval. This pattern allows plan→plan-review without upfront resolution; user approval of assumptions unblocks work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
