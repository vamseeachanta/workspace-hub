---
name: crossprovider codex owner-evidence-parsing-must-handle-actual-github
description: Owner evidence parsing must handle actual GitHub API shape and reject malformed inputs fail-closed
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [owner-evidence, api-parsing, fail-closed]
---

Approved plan requires owner-authored comment with `author.authorAssociation==OWNER` post-approval timestamp. Implementation must parse real `gh api` payloads (author={login, ...}, created_at timestamp) and reject: extra fields, multiple blocks, non-owner authors, free-form notes, and malformed timestamps without exception suppression. Simple dict injection in tests hides these requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
