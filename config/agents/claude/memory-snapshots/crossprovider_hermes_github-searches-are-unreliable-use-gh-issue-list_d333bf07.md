---
name: crossprovider hermes github-searches-are-unreliable-use-gh-issue-list
description: GitHub searches are unreliable; use gh issue list or individual view
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-cli, tool-quirk]
---

Broad `gh search issues` queries are noisy/truncated; quoted `repo:` syntax fails. For reliable issue discovery, use focused `gh issue list --search <term>` or individual `gh issue view <N>` instead of search-based discovery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
