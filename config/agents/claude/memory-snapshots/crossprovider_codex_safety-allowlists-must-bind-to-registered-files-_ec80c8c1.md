---
name: crossprovider codex safety-allowlists-must-bind-to-registered-files-
description: Safety allowlists must bind to registered files, not filesystem shape
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety, security, allowlisting, untracked-content]
---

Glob patterns accepting 'any *.md under wikis/' can expose untracked local drafts. Allowlist must reference committed/registered file identifiers (git ls-files, committed symlinks) to exclude local-only content. Test explicitly with untracked files matching the shape to ensure they fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
