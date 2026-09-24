---
name: crossprovider codex frontmatter-parsing-must-gracefully-skip-malform
description: Frontmatter parsing must gracefully skip malformed entries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parsing, robustness, error-handling]
---

Parse YAML frontmatter defensively: skip files with malformed YAML, missing fields, or invalid dates without crashing. Track skip counts separately (files_skipped_no_orchestrator, files_skipped_malformed) for later debugging. Do not fail the entire collection on one bad file.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
