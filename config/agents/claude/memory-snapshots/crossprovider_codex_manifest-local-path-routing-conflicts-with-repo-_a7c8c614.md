---
name: crossprovider codex manifest-local-path-routing-conflicts-with-repo-
description: Manifest local-path routing conflicts with repo governance
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [manifest-governance, path-routing, precedent-drift]
---

Plans proposing to store `/mnt/ace` paths in repo-visible manifests and reports (e.g., `docs/research/abs-source-manifest.md`) conflict with existing governance rules forbidding path-rich artifacts in public surfaces. Existing wiki pages and verification queues already expose local paths, creating divergence between stated policy and actual precedent. Future plans must explicitly choose: off-repo private manifests or redacted repo-facing schemas with separate local storage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
