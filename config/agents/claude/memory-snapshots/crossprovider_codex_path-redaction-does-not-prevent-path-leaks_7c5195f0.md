---
name: crossprovider codex path-redaction-does-not-prevent-path-leaks
description: Path redaction does not prevent path leaks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-safety, output-handling, security]
---

Substring redaction on file paths doesn't prevent sensitive filenames from leaking; redacting matching content still exposes the unredacted path structure. Use NUL-delimited git output to treat paths as structured data, and redact entire paths from output or replace them with neutral IDs, not substrings of path text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
