---
name: crossprovider codex build-order-sync-erasure-in-cross-repo-deploymen
description: Build-order sync erasure in cross-repo deployment
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [build-ci, cross-repo, deployment]
---

When a build pipeline deletes output directories (e.g., `dist/`), verify that cross-repo sync steps run AFTER the build, not before, or synced content will be erased. Currently aceengineer-website's `daily-update.sh` runs sync before build, losing WED outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
