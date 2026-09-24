---
name: crossprovider codex parser-tests-using-simplified-fixtures-bypass-re
description: Parser tests using simplified fixtures bypass real API shapes, causing silent production failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, parsing, api-integration]
---

Session 7 found tests for GitHub comment parsing used `{"author": "string"}` while real `gh issue view --json comments` returns `{"author": {"login": "string"}}`. Tests passed locally but the parser would fail closed on real GitHub payloads. Always test parsers against actual API output format or capture examples as fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
