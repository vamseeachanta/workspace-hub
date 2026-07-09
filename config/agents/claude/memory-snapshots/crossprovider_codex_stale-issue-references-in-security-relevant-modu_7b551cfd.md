---
name: crossprovider codex stale-issue-references-in-security-relevant-modu
description: Stale issue references in security-relevant modules mislead scope
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [documentation, refactoring, security]
---

When a module generalizes from one issue's initial code, leaving stale issue-N docstrings/comments (e.g., 'for ACE issue 68' after generalization to issue 72 contracts) creates false claims about authority and can confuse scope boundaries for future maintainers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
