---
name: crossprovider codex trust-live-github-issue-state-not-stale-issue-bo
description: Trust live GitHub issue state, not stale issue bodies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-integration, scope-discovery, data-freshness]
---

Issue body text can become outdated as work progresses. Use `gh issue view` to fetch current labels, status, and parent state for scope discovery. Stale body claims about open/closed parents must be verified against live GitHub, not hardcoded into implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
