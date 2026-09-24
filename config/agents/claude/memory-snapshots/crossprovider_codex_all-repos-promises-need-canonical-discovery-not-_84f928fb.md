---
name: crossprovider codex all-repos-promises-need-canonical-discovery-not-
description: "All repos" promises need canonical discovery, not hardcoding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope, repo-discovery, multi-repo, maintainability]
---

When a system claims to cover "all repos" or "across N repos," hardcoding a list creates silent misses when new repos are added. Use a canonical registry or config for repo discovery so coverage stays consistent as the workspace grows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
