---
name: crossprovider codex untracked-retained-review-artifacts-block-legal-
description: Untracked retained review artifacts block legal scans and close-out
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-curation, legal-compliance, close-out-gate]
---

Public-surface review artifacts that remain untracked cause `legal-sanity-scan.sh --diff-only` to fail even when content is clean. Retained artifacts must either be committed or selector-selectable; temporary review outputs should be cleaned before close-out or explicitly stashed. This is a gate-enforcement issue, not content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
