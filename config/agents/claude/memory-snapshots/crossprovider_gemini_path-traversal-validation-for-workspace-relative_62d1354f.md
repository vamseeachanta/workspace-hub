---
name: crossprovider gemini path-traversal-validation-for-workspace-relative
description: Path traversal validation for workspace-relative file references
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, path-handling, file-loading, workspace-hub]
---

When loading user-provided file paths from frontmatter (e.g., `plan_html_review_draft_ref`), validate they remain within the workspace root using `candidate.relative_to(workspace_root)`, catching ValueError on escape attempts. Applies to any tool that resolves external references to disk.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
