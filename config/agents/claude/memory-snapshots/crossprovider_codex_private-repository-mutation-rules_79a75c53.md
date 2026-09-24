---
name: crossprovider codex private-repository-mutation-rules
description: Private repository mutation rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [private-repos, client-confidentiality, multi-repo]
---

For private repos (llm-wiki-mkt-a, deckhand-licensed-runs-queue): never self-merge, owner approves any `state:approved` queue push, verify before push, never mix client identifiers into public repos. Use anonymized parallel lanes (e.g., digitalmodel #) for public-facing work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
