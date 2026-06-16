---
name: crossprovider codex index-drift-in-batch-prs-requires-explicit-scope
description: Index drift in batch PRs requires explicit scope check
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [batch-verification, document-index, scope-creep]
---

When verification batch PRs change queue rows (e.g., asset-management rows), document-index regeneration must match exactly that scope. PR #686 changed only 12 asset-management queue rows but also regenerated 3 unrelated pipeline-engineering index rows, masking the scope creep. Verify: manifest rows → queue rows → index rows are 1:1; split out-of-scope regeneration into a separate index-rebuild PR before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
