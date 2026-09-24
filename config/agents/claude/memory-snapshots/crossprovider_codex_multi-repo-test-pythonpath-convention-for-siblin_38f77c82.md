---
name: crossprovider codex multi-repo-test-pythonpath-convention-for-siblin
description: Multi-repo test PYTHONPATH convention for sibling dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, python, path-resolution]
---

Specify PYTHONPATH as "src:../sibling-repo/src" when running tests in one repo that depend on an adjacent repo. Ensures consistent path resolution across both the local and neighboring source trees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
