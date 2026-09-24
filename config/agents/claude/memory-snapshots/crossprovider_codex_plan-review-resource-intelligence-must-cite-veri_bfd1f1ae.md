---
name: crossprovider codex plan-review-resource-intelligence-must-cite-veri
description: Plan review: Resource Intelligence must cite verifiable evidence, not prose assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, adversarial-review, resource-intelligence, verification]
---

Resource Intelligence Summary sections routinely assert facts (file lengths, issue states, document existence) as plain prose without providing independently checkable artifacts, paths, or command transcripts. Codex reviews treat self-assertion as blocking defect and require: concrete file paths that can be verified via `ls`, issue status backed by `gh issue view` output, and committed evidence or immutable refs. Prose-only Resource Intelligence = unverified dependency state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
