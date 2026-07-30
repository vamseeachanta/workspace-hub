---
name: crossprovider codex absolute-paths-from-non-repo-sources-should-be-r
description: Absolute paths from non-repo sources should be redacted in durable reports
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [paths, provenance, redaction, non-repo-sources]
---

When sourcing input files from outside the repo (user-supplied data, client paths), embedding absolute filesystem paths in provenance reports or display functions leaks local topology. Report non-repo sources by redacted identifier (basename + digest) or require explicit `source_id` labels in configuration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
