---
name: crossprovider codex yaml-placeholder-based-path-fixes-require-explic
description: YAML placeholder-based path fixes require explicit runtime resolvers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [paths, yaml, test-fixtures]
---

Replacing absolute paths with ${REPO_ROOT} placeholders in YAML test fixtures requires runtime substitution code. Test loaders typically do not auto-substitute; the fix is incomplete without explicit resolver logic (e.g., yaml.safe_load() followed by string templating). Verify the loader pattern before assuming placeholders will work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
