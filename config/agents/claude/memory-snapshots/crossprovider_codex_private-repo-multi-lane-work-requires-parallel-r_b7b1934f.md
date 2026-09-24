---
name: crossprovider codex private-repo-multi-lane-work-requires-parallel-r
description: Private repo multi-lane work requires `parallel-readonly` mode and anonymization rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [private-repo, multi-repo-coordination, client-compliance]
---

For multi-repo work spanning private client repos (e.g., llm-wiki-mkt-a) and public repos: use `parallel-readonly` execution until approval gates verified; anonymize client identifiers (Noble Valiant → digitalmodel anonymized issues #1571 equivalent) before any public push; never self-merge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
