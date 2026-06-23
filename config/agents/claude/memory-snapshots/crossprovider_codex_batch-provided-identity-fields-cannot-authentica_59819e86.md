---
name: crossprovider codex batch-provided-identity-fields-cannot-authentica
description: Batch-provided identity fields cannot authenticate target pages alone
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [batch-processing, authentication, security-defect]
---

Accepting dispatch-provided `matched_code_id` as proof of target identity is bypassable: corrupted batch can keep `code_id` sequence correct but forge `matched_code_id` to point at wrong page. Must validate incoming batch against expected identity map (code_id + matched_code_id + page_path + source_label tuple), and independently verify page frontmatter before writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
