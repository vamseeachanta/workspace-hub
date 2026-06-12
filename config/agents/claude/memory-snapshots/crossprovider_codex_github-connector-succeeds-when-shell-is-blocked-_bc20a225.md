---
name: crossprovider codex github-connector-succeeds-when-shell-is-blocked-
description: GitHub connector succeeds when shell is blocked; use as fallback for inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [github-connector, fallback, inspection]
---

When local shell execution fails in Codex sandbox, GitHub connector can still read branch diffs, file contents, issue metadata, and perform limited write operations (though writes may be cancelled by harness). Use connector to inspect implementation branches, read plan artifacts, and verify review findings when local inspection is unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
