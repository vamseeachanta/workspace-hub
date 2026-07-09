---
name: crossprovider codex test-fixtures-for-secret-auth-systems-use-reques
description: Test fixtures for secret/auth systems use request-markers or runtime generation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [testing, security, fixtures, secrets]
---

Never commit concrete token/password values in fixtures, even placeholders. Use entropy-only generators (no source-derivation) or structurally-unambiguous request markers (e.g., `{"public_source_token_request": {"fixture_id": "safe_row_001"}}`). Duplicate handling must be testable via stub, not 'practically impossible' reasoning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
