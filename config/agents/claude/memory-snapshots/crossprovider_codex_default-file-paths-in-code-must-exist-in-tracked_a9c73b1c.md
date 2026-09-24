---
name: crossprovider codex default-file-paths-in-code-must-exist-in-tracked
description: Default file paths in code must exist in tracked artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deployment, defaults, tracked-state]
---

Code that references a default file path (e.g. CONTENT_VALUE_POLICY_PATH = 'data/document-index/policy.json') will fail closed when cloned unless that file is tracked or the code provides a fallback. Always verify default paths exist in git ls-files or document the initialization step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
