---
name: crossprovider codex build-deployment-order-can-silently-erase-output
description: Build/deployment order can silently erase outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deployment, build-pipeline, cross-repo-integration]
---

In multi-stage deploys, if sync→build→build-deletes-output ordering runs in the wrong sequence, outputs from the sync step get erased silently. Verify that stateful intermediate artifacts are not overwritten by subsequent build steps; consider gating build cleanup until after publish steps complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
