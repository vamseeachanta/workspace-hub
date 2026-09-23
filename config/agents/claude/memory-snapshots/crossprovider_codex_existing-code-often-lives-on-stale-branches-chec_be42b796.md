---
name: crossprovider codex existing-code-often-lives-on-stale-branches-chec
description: Existing code often lives on stale branches; checkout state matters for preflight
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [codebase-discovery, preflight-checks, branch-state]
---

machine-ecosystem/ collector already existed in repo but preflight checks reported it missing because the working checkout was on branch contacts/email-draft-pipeline. The actual gap was never 'build a collector'—it was 'turn on the existing one'. Branch/checkout state is invisible to task estimation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
