---
name: crossprovider codex nested-repo-path-handling-differs-systematically
description: Nested-repo path handling differs systematically by provider
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-repo, provider-drift, path-handling]
---

Codex sessions often assume workspace-root absolute paths (`/mnt/...`) while nested-repo implementation work requires repo-relative navigation. This is a systematic drift pattern, not a one-off mistake—provider guidance should reinforce nested-repo context independence when dispatch spans multiple repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
