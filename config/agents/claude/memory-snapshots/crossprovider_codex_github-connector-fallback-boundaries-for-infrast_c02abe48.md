---
name: crossprovider codex github-connector-fallback-boundaries-for-infrast
description: GitHub connector fallback boundaries for infrastructure failures
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [infrastructure, fallback-patterns, cli-tools]
---

When local shell fails (bwrap setup, sandbox errors), GitHub connector is viable for metadata/status audits (labels, comments, default-branch metadata) but cannot replace filesystem reads. Plan accordingly: status audits work remotely; file-location checks require local access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
