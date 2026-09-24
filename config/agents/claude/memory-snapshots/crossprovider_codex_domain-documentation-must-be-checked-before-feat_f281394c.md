---
name: crossprovider codex domain-documentation-must-be-checked-before-feat
description: Domain documentation must be checked before feature deferral
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning-process, repository-awareness, deferral-decisions]
---

Feature deferral decisions should scan existing domain documentation, examples, and parameter references before marking work as out-of-scope. Deferring features that already have working examples in the repo wastes review cycles and misdirects implementation scope. Example: auto control-surface YAML generation was deferred despite existing source documentation with concrete mappings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
