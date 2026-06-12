---
name: crossprovider hermes issue-2657-structured-metadata-scope-spans-tool-
description: Issue #2657 structured-metadata scope spans tool-call limits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scope, context-compression, hermes-sessions, test-driven-development]
---

Adding `forbidden_actions`, `exception_path_prefixes`, `current_authority_scan_paths` to `llm_wiki_spinout_path_drift` + RED tests for three focal paths + registry updates + markdown rendering updates is substantial enough to trigger context compression across multiple Hermes sessions. Work requires pre-chunking (tests → implementation → validation) or explicit state preservation across boundaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
